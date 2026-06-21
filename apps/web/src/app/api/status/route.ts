import { NextResponse } from "next/server";
import { fetchApiStatus } from "@/lib/status";

export const dynamic = "force-dynamic";

export async function GET() {
  const status = await fetchApiStatus();
  return NextResponse.json(status);
}
