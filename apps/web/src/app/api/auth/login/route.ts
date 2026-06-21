import { NextResponse } from "next/server";
import { AUTH_COOKIE_NAME, type LoginResult, shouldUseSecureCookie } from "@/lib/auth";
import { apiBaseUrl } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const payload = await request.json();

  const response = await fetch(`${apiBaseUrl()}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  if (!response.ok) {
    return NextResponse.json({ message: "Invalid email or password" }, { status: 401 });
  }

  const body = (await response.json()) as LoginResult;
  const nextResponse = NextResponse.json({ user: body.user });
  nextResponse.cookies.set(AUTH_COOKIE_NAME, body.access_token, {
    httpOnly: true,
    secure: shouldUseSecureCookie(),
    sameSite: "lax",
    path: "/",
    maxAge: body.expires_in,
  });

  return nextResponse;
}
