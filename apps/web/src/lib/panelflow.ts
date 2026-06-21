import { apiBaseUrl } from "@/lib/api";

export type SourceSummary = {
  id: string;
  name: string;
  display_name?: string | null;
  language?: string | null;
  is_nsfw?: boolean | null;
  supports_latest?: boolean | null;
  status: string;
  extension_name?: string | null;
  extension_package?: string | null;
  icon_url?: string | null;
};

export type SearchResult = {
  title: string;
  subtitle?: string | null;
  item_type: string;
  source_type: "external_suwayomi";
  source_id: string;
  source_name?: string | null;
  external_id: string;
  external_url?: string | null;
  cover_url?: string | null;
  description?: string | null;
  status?: string | null;
};

export type SearchResponse = {
  source_id: string;
  query: string;
  has_next_page: boolean;
  results: SearchResult[];
};

export type LibraryItem = {
  id: number;
  user_id: number;
  title: string;
  subtitle?: string | null;
  item_type: string;
  source_type: string;
  source_id: string;
  external_id: string;
  external_url?: string | null;
  cover_url?: string | null;
  description?: string | null;
  status?: string | null;
  created_at: string;
  updated_at: string;
};

export type ApiProblem = {
  code: string;
  message: string;
};

export type FetchResult<T> = {
  data: T | null;
  error: string | null;
  status: number;
};

function problemMessage(payload: unknown, fallback: string) {
  if (payload && typeof payload === "object" && "detail" in payload) {
    const detail = (payload as { detail: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (detail && typeof detail === "object" && "message" in detail) {
      const message = (detail as ApiProblem).message;
      if (typeof message === "string") {
        return message;
      }
    }
  }
  return fallback;
}

export async function fetchPanelFlow<T>(path: string, token?: string, init?: RequestInit): Promise<FetchResult<T>> {
  if (!token) {
    return { data: null, error: "Authentication is required.", status: 401 };
  }

  try {
    const response = await fetch(`${apiBaseUrl()}${path}`, {
      ...init,
      headers: {
        ...(init?.headers ?? {}),
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
      next: { revalidate: 0 },
    });
    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      return {
        data: null,
        error: problemMessage(payload, `PanelFlow API returned HTTP ${response.status}.`),
        status: response.status,
      };
    }
    return { data: payload as T, error: null, status: response.status };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : "PanelFlow API is not reachable.",
      status: 0,
    };
  }
}

export function coverSrc(coverUrl?: string | null) {
  if (!coverUrl) {
    return "";
  }
  if (coverUrl.startsWith("/")) {
    return `/api/suwayomi/image?url=${encodeURIComponent(coverUrl)}`;
  }
  return coverUrl;
}
