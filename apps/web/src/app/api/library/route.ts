import { NextResponse } from "next/server";
import { getAuthToken } from "@/lib/auth";
import { apiBaseUrl } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function GET() {
  const token = await getAuthToken();
  if (!token) {
    return NextResponse.json({ message: "Not authenticated" }, { status: 401 });
  }

  const response = await fetch(`${apiBaseUrl()}/api/library`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  const body = await response.json().catch(() => ({ message: "Unable to load library." }));
  return NextResponse.json(body, { status: response.status });
}
