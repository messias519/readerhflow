import { NextResponse } from "next/server";
import { AUTH_COOKIE_NAME } from "@/lib/auth";
import { apiBaseUrl } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function POST() {
  try {
    await fetch(`${apiBaseUrl()}/api/auth/logout`, {
      method: "POST",
      cache: "no-store",
    });
  } catch {
    // The local cookie is authoritative for the MVP logout flow.
  }

  const response = NextResponse.json({ status: "ok" });
  response.cookies.set(AUTH_COOKIE_NAME, "", {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: 0,
  });
  return response;
}
