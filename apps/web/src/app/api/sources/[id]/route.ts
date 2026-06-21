import { NextResponse } from "next/server";
import { getAuthToken } from "@/lib/auth";
import { apiBaseUrl } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function GET(_request: Request, context: { params: Promise<{ id: string }> }) {
  const token = await getAuthToken();
  if (!token) {
    return NextResponse.json({ message: "Not authenticated" }, { status: 401 });
  }

  const { id } = await context.params;
  const response = await fetch(`${apiBaseUrl()}/api/sources/${encodeURIComponent(id)}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  const body = await response.json().catch(() => ({ message: "Unable to load source." }));
  return NextResponse.json(body, { status: response.status });
}
