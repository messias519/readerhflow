import { NextResponse } from "next/server";
import { apiBaseUrl } from "@/lib/api";
import { getAuthToken } from "@/lib/auth";

export const dynamic = "force-dynamic";

const blockedRequestHeaders = new Set([
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
]);

const blockedResponseHeaders = new Set([
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
]);

type RouteContext = {
  params: Promise<{ path?: string[] }>;
};

function buildUpstreamUrl(pathParts: string[] | undefined, requestUrl: string) {
  const path = (pathParts ?? []).map(encodeURIComponent).join("/");
  const suffix = path ? `/${path}` : "";
  const upstream = new URL(`${apiBaseUrl()}/api/admin/suwayomi${suffix}`);
  upstream.search = new URL(requestUrl).search;
  return upstream;
}

function requestHeaders(request: Request, token: string) {
  const headers = new Headers();
  request.headers.forEach((value, key) => {
    const lowerKey = key.toLowerCase();
    if (blockedRequestHeaders.has(lowerKey) || lowerKey.startsWith("x-forwarded-")) {
      return;
    }
    headers.set(key, value);
  });
  headers.set("Authorization", `Bearer ${token}`);
  return headers;
}

function responseHeaders(response: Response) {
  const headers = new Headers();
  response.headers.forEach((value, key) => {
    if (!blockedResponseHeaders.has(key.toLowerCase())) {
      headers.set(key, value);
    }
  });
  return headers;
}

async function proxy(request: Request, context: RouteContext) {
  const token = await getAuthToken();
  if (!token) {
    return NextResponse.json({ message: "Not authenticated" }, { status: 401 });
  }

  const { path } = await context.params;
  const upstream = buildUpstreamUrl(path, request.url);
  const body = ["GET", "HEAD"].includes(request.method) ? undefined : await request.arrayBuffer();

  const response = await fetch(upstream, {
    method: request.method,
    headers: requestHeaders(request, token),
    body,
    cache: "no-store",
  });

  const responseBody = await response.arrayBuffer();
  return new NextResponse(responseBody, {
    status: response.status,
    headers: responseHeaders(response),
  });
}

export async function GET(request: Request, context: RouteContext) {
  return proxy(request, context);
}

export async function POST(request: Request, context: RouteContext) {
  return proxy(request, context);
}

export async function PUT(request: Request, context: RouteContext) {
  return proxy(request, context);
}

export async function PATCH(request: Request, context: RouteContext) {
  return proxy(request, context);
}

export async function DELETE(request: Request, context: RouteContext) {
  return proxy(request, context);
}
