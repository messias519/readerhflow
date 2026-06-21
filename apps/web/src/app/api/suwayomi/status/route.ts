import { NextResponse } from "next/server";
import { apiBaseUrl } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await fetch(`${apiBaseUrl()}/api/suwayomi/status`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });
    const payload = await response.json();
    return NextResponse.json(payload, { status: response.ok ? 200 : 502 });
  } catch (error) {
    return NextResponse.json(
      {
        checked_at: new Date().toISOString(),
        suwayomi: {
          name: "suwayomi",
          status: "error",
          message: error instanceof Error ? error.message : "Unknown Suwayomi error.",
        },
      },
      { status: 502 },
    );
  }
}
