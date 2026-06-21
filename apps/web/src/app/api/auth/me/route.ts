import { NextResponse } from "next/server";
import { fetchCurrentUser, getAuthToken } from "@/lib/auth";

export const dynamic = "force-dynamic";

export async function GET() {
  const user = await fetchCurrentUser(await getAuthToken());
  if (!user) {
    return NextResponse.json({ message: "Not authenticated" }, { status: 401 });
  }

  return NextResponse.json({ user });
}
