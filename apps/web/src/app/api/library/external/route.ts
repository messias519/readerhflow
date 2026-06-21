import { NextResponse } from "next/server";
import { getAuthToken } from "@/lib/auth";
import { apiBaseUrl } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const token = await getAuthToken();
  if (!token) {
    return NextResponse.json({ message: "Not authenticated" }, { status: 401 });
  }

  const payload = await request.json();
  const response = await fetch(`${apiBaseUrl()}/api/library/external`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    cache: "no-store",
  });
  const body = await response.json().catch(() => ({ message: "Unable to add library item." }));
  return NextResponse.json(body, { status: response.status });
}
