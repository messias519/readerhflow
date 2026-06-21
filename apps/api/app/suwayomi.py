from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from fastapi import Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.config import Settings, get_settings


class ApiError(BaseModel):
    code: str
    message: str


class SourceSummary(BaseModel):
    id: str
    name: str
    display_name: str | None = None
    language: str | None = None
    is_nsfw: bool | None = None
    supports_latest: bool | None = None
    status: str = "installed"
    extension_name: str | None = None
    extension_package: str | None = None
    icon_url: str | None = None


class SourceDetail(SourceSummary):
    is_configurable: bool | None = None
    has_preferences: bool | None = None


class SearchResult(BaseModel):
    title: str
    subtitle: str | None = None
    item_type: str = "manga"
    source_type: str = "external_suwayomi"
    source_id: str
    source_name: str | None = None
    external_id: str
    external_url: str | None = None
    cover_url: str | None = None
    description: str | None = None
    status: str | None = None


class SearchResponse(BaseModel):
    source_id: str
    query: str
    has_next_page: bool = False
    results: list[SearchResult]


class SuwayomiClientError(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class SuwayomiClient:
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.suwayomi_url.rstrip("/")
        self.graphql_url = f"{self.base_url}/api/graphql"
        self.timeout = httpx.Timeout(10.0, connect=5.0)

    async def _graphql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.post(
                    self.graphql_url,
                    json={"query": query, "variables": variables or {}},
                )
        except httpx.RequestError as exc:
            raise SuwayomiClientError(
                "suwayomi_unavailable",
                "Suwayomi is not reachable from the PanelFlow API.",
            ) from exc

        if response.status_code >= 500:
            raise SuwayomiClientError(
                "suwayomi_error",
                "Suwayomi returned an internal error. Check the Suwayomi container logs.",
                status.HTTP_502_BAD_GATEWAY,
            )
        if response.status_code >= 400:
            raise SuwayomiClientError(
                "suwayomi_request_failed",
                "Suwayomi rejected the request. Check that the internal API is available.",
                status.HTTP_502_BAD_GATEWAY,
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise SuwayomiClientError(
                "suwayomi_invalid_response",
                "Suwayomi returned an invalid response.",
                status.HTTP_502_BAD_GATEWAY,
            ) from exc

        errors = payload.get("errors")
        if errors:
            raise SuwayomiClientError(
                "suwayomi_graphql_error",
                "Suwayomi could not complete the request. Check installed extensions and source availability.",
                status.HTTP_502_BAD_GATEWAY,
            )

        data = payload.get("data")
        if not isinstance(data, dict):
            raise SuwayomiClientError(
                "suwayomi_invalid_response",
                "Suwayomi returned an unexpected response.",
                status.HTTP_502_BAD_GATEWAY,
            )
        return data

    async def list_sources(self) -> list[SourceSummary]:
        data = await self._graphql(
            """
            query PanelFlowSources {
              sources(orderBy: NAME) {
                nodes {
                  id
                  name
                  displayName
                  lang
                  isNsfw
                  supportsLatest
                  iconUrl
                  extension {
                    name
                    pkgName
                    isInstalled
                    hasUpdate
                    isObsolete
                  }
                }
              }
            }
            """
        )
        nodes = data.get("sources", {}).get("nodes", [])
        return [self._source_summary(node) for node in nodes if isinstance(node, dict)]

    async def get_source(self, source_id: str) -> SourceDetail:
        data = await self._graphql(
            """
            query PanelFlowSource($id: LongString!) {
              source(id: $id) {
                id
                name
                displayName
                lang
                isNsfw
                supportsLatest
                isConfigurable
                iconUrl
                preferences { __typename }
                extension {
                  name
                  pkgName
                  isInstalled
                  hasUpdate
                  isObsolete
                }
              }
            }
            """,
            {"id": source_id},
        )
        source = data.get("source")
        if not isinstance(source, dict):
            raise SuwayomiClientError("source_not_found", "Source not found.", status.HTTP_404_NOT_FOUND)
        summary = self._source_summary(source)
        return SourceDetail(
            **summary.model_dump(),
            is_configurable=source.get("isConfigurable"),
            has_preferences=bool(source.get("preferences")),
        )

    async def search(self, source_id: str, query: str, page: int = 1) -> SearchResponse:
        data = await self._graphql(
            """
            mutation PanelFlowSearch($source: LongString!, $query: String!, $page: Int!) {
              fetchSourceManga(input: { source: $source, query: $query, page: $page, type: SEARCH }) {
                hasNextPage
                mangas {
                  id
                  title
                  url
                  realUrl
                  thumbnailUrl
                  description
                  status
                  sourceId
                  source {
                    id
                    name
                    displayName
                    lang
                  }
                }
              }
            }
            """,
            {"source": source_id, "query": query, "page": page},
        )
        payload = data.get("fetchSourceManga", {})
        mangas = payload.get("mangas", [])
        return SearchResponse(
            source_id=source_id,
            query=query,
            has_next_page=bool(payload.get("hasNextPage")),
            results=[self._search_result(manga, source_id) for manga in mangas if isinstance(manga, dict)],
        )

    async def fetch_internal_image(self, image_url: str) -> tuple[bytes, str]:
        if not image_url.startswith("/"):
            raise SuwayomiClientError("invalid_image_url", "Only internal Suwayomi image paths can be proxied.", 400)

        target = urljoin(f"{self.base_url}/", image_url.lstrip("/"))
        parsed_base = urlparse(self.base_url)
        parsed_target = urlparse(target)
        if parsed_target.netloc != parsed_base.netloc:
            raise SuwayomiClientError("invalid_image_url", "Invalid Suwayomi image path.", 400)

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(target)
                response.raise_for_status()
        except httpx.RequestError as exc:
            raise SuwayomiClientError("suwayomi_unavailable", "Suwayomi image service is not reachable.") from exc
        except httpx.HTTPStatusError as exc:
            raise SuwayomiClientError(
                "suwayomi_image_error",
                "Suwayomi could not return the requested image.",
                status.HTTP_502_BAD_GATEWAY,
            ) from exc

        content_type = response.headers.get("content-type", "application/octet-stream")
        return response.content, content_type

    async def proxy_webui(self, request: Request, path: str = "") -> Response:
        target_url = self._proxy_target(path, str(request.url.query))
        headers = self._proxy_request_headers(request)
        content = await request.body()

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False) as client:
                upstream = await client.request(
                    request.method,
                    target_url,
                    content=content if content else None,
                    headers=headers,
                )
        except httpx.RequestError as exc:
            raise SuwayomiClientError(
                "suwayomi_unavailable",
                "Suwayomi WebUI is not reachable from the PanelFlow API.",
            ) from exc

        response_headers = self._proxy_response_headers(upstream)
        body = upstream.content
        content_type = upstream.headers.get("content-type", "")

        if "text/html" in content_type.lower():
            body = self._rewrite_html(body, upstream.encoding or "utf-8")
            response_headers["content-length"] = str(len(body))
        elif "text/css" in content_type.lower():
            body = self._rewrite_css(body, upstream.encoding or "utf-8")
            response_headers["content-length"] = str(len(body))

        return Response(content=body, status_code=upstream.status_code, headers=response_headers)

    def _source_summary(self, node: dict[str, Any]) -> SourceSummary:
        extension = node.get("extension") if isinstance(node.get("extension"), dict) else {}
        status_text = "installed"
        if extension.get("isObsolete"):
            status_text = "obsolete"
        elif extension.get("hasUpdate"):
            status_text = "update_available"

        return SourceSummary(
            id=str(node.get("id") or ""),
            name=str(node.get("name") or node.get("displayName") or "Unknown source"),
            display_name=node.get("displayName"),
            language=node.get("lang"),
            is_nsfw=node.get("isNsfw"),
            supports_latest=node.get("supportsLatest"),
            status=status_text,
            extension_name=extension.get("name"),
            extension_package=extension.get("pkgName"),
            icon_url=node.get("iconUrl"),
        )

    def _search_result(self, manga: dict[str, Any], fallback_source_id: str) -> SearchResult:
        source = manga.get("source") if isinstance(manga.get("source"), dict) else {}
        external_id = str(manga.get("id") or manga.get("realUrl") or manga.get("url") or "")
        source_id = str(manga.get("sourceId") or source.get("id") or fallback_source_id)

        return SearchResult(
            title=str(manga.get("title") or "Untitled"),
            source_id=source_id,
            source_name=source.get("displayName") or source.get("name"),
            external_id=external_id,
            external_url=manga.get("realUrl") or manga.get("url"),
            cover_url=manga.get("thumbnailUrl"),
            description=manga.get("description"),
            status=manga.get("status"),
        )

    def _proxy_target(self, path: str, query: str) -> str:
        clean_path = path.lstrip("/")
        target = urljoin(f"{self.base_url}/", clean_path)
        parsed_base = urlparse(self.base_url)
        parsed_target = urlparse(target)
        if parsed_target.scheme != parsed_base.scheme or parsed_target.netloc != parsed_base.netloc:
            raise SuwayomiClientError("invalid_proxy_path", "Invalid Suwayomi proxy path.", 400)
        if query:
            return f"{target}?{query}"
        return target

    def _proxy_request_headers(self, request: Request) -> dict[str, str]:
        blocked = {
            "host",
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailer",
            "transfer-encoding",
            "upgrade",
            "authorization",
            "content-length",
        }
        headers: dict[str, str] = {}
        for name, value in request.headers.items():
            lower_name = name.lower()
            if lower_name in blocked:
                continue
            if lower_name.startswith("x-forwarded-"):
                continue
            headers[name] = value
        headers["x-forwarded-prefix"] = "/api/admin/suwayomi"
        return headers

    def _proxy_response_headers(self, upstream: httpx.Response) -> dict[str, str]:
        blocked = {
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailer",
            "transfer-encoding",
            "upgrade",
            "content-encoding",
            "content-length",
            "x-frame-options",
            "content-security-policy",
        }
        headers: dict[str, str] = {}
        for name, value in upstream.headers.items():
            lower_name = name.lower()
            if lower_name in blocked:
                continue
            if lower_name == "location":
                headers[name] = self._rewrite_location(value)
                continue
            headers[name] = value
        headers.setdefault("cache-control", "no-store")
        return headers

    def _rewrite_location(self, location: str) -> str:
        parsed_location = urlparse(location)
        parsed_base = urlparse(self.base_url)
        if not parsed_location.netloc and location.startswith("/"):
            return f"/api/admin/suwayomi{location}"
        if parsed_location.scheme == parsed_base.scheme and parsed_location.netloc == parsed_base.netloc:
            path = parsed_location.path or "/"
            query = f"?{parsed_location.query}" if parsed_location.query else ""
            fragment = f"#{parsed_location.fragment}" if parsed_location.fragment else ""
            return f"/api/admin/suwayomi{path}{query}{fragment}"
        return location

    def _rewrite_html(self, body: bytes, encoding: str) -> bytes:
        text = body.decode(encoding, errors="replace")
        text = re.sub(r'((?:href|src|action)=["\'])/(?!/|api/admin/suwayomi/)', r"\1/api/admin/suwayomi/", text)
        text = text.replace('url("/', 'url("/api/admin/suwayomi/')
        text = text.replace("url('/", "url('/api/admin/suwayomi/")
        text = re.sub(r"url\(/(?!/|api/admin/suwayomi/)", "url(/api/admin/suwayomi/", text)

        shim = """
<base href="/api/admin/suwayomi/">
<script>
(() => {
  const prefix = "/api/admin/suwayomi";
  const rewrite = (url) => {
    if (typeof url !== "string") return url;
    if (url === prefix || url.startsWith(prefix + "/")) return url;
    if (url.startsWith("/")) return prefix + url;
    try {
      const parsed = new URL(url, window.location.origin);
      if (parsed.origin === window.location.origin && parsed.pathname !== prefix && !parsed.pathname.startsWith(prefix + "/")) {
        return prefix + parsed.pathname + parsed.search + parsed.hash;
      }
    } catch {}
    return url;
  };
  const originalFetch = window.fetch;
  window.fetch = (input, init) => {
    if (typeof input === "string") return originalFetch(rewrite(input), init);
    if (input instanceof Request) return originalFetch(new Request(rewrite(input.url), input), init);
    return originalFetch(input, init);
  };
  const originalOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    return originalOpen.call(this, method, rewrite(url), ...rest);
  };
})();
</script>
"""
        if "</head>" in text:
            text = text.replace("</head>", f"{shim}</head>", 1)
        else:
            text = f"{shim}{text}"
        return text.encode(encoding)

    def _rewrite_css(self, body: bytes, encoding: str) -> bytes:
        text = body.decode(encoding, errors="replace")
        text = text.replace('url("/', 'url("/api/admin/suwayomi/')
        text = text.replace("url('/", "url('/api/admin/suwayomi/")
        text = re.sub(r"url\(/(?!/|api/admin/suwayomi/)", "url(/api/admin/suwayomi/", text)
        return text.encode(encoding)


def get_suwayomi_client(settings: Settings = Depends(get_settings)) -> SuwayomiClient:
    return SuwayomiClient(settings)


def suwayomi_http_error(error: SuwayomiClientError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail=ApiError(code=error.code, message=error.message).model_dump(),
    )

