import { NextResponse } from "next/server";
import { getAuthToken } from "@/lib/auth";
import { apiBaseUrl } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const token = await getAuthToken();
  if (!token) {
    return NextResponse.json({ message: "Not authenticated" }, { status: 401 });
  }

  const url = new URL(request.url);
  const upstream = new URL(`${apiBaseUrl()}/api/search`);
  for (const key of ["source_id", "query", "page"]) {
    const value = url.searchParams.get(key);
    if (value) {
      upstream.searchParams.set(key, value);
    }
  }

  const response = await fetch(upstream, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  const body = await response.json().catch(() => ({ message: "Unable to search source." }));
  return NextResponse.json(body, { status: response.status });
}
