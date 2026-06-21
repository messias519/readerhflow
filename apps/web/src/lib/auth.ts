import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { apiBaseUrl } from "@/lib/api";

export const AUTH_COOKIE_NAME = "panelflow_token";

export type AuthUser = {
  id: number;
  email: string;
  role: string;
  is_active: boolean;
};

export type LoginResult = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: AuthUser;
};

export async function getAuthToken() {
  const cookieStore = await cookies();
  return cookieStore.get(AUTH_COOKIE_NAME)?.value;
}

export async function fetchCurrentUser(token?: string): Promise<AuthUser | null> {
  if (!token) {
    return null;
  }

  try {
    const response = await fetch(`${apiBaseUrl()}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as AuthUser;
  } catch {
    return null;
  }
}

export async function getCurrentUser() {
  return fetchCurrentUser(await getAuthToken());
}

export async function requireCurrentUser() {
  const user = await getCurrentUser();
  if (!user) {
    redirect("/login");
  }
  return user;
}

export function shouldUseSecureCookie() {
  return (process.env.NEXT_PUBLIC_SITE_URL ?? "").startsWith("https://");
}
