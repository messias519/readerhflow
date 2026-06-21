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
  const imageUrl = url.searchParams.get("url");
  if (!imageUrl) {
    return NextResponse.json({ message: "Missing image URL" }, { status: 400 });
  }

  const upstream = new URL(`${apiBaseUrl()}/api/suwayomi/image`);
  upstream.searchParams.set("url", imageUrl);
  const response = await fetch(upstream, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!response.ok) {
    return NextResponse.json({ message: "Unable to load image" }, { status: response.status });
  }

  const body = await response.arrayBuffer();
  return new NextResponse(body, {
    headers: {
      "Content-Type": response.headers.get("content-type") ?? "application/octet-stream",
      "Cache-Control": "private, max-age=3600",
    },
  });
}
