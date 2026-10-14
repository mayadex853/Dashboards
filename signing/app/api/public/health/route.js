import { NextResponse } from "next/server";
import { health } from "@/lib/db";
import { emailConfigured } from "@/lib/email";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    return NextResponse.json({ ...(await health()), email: emailConfigured() });
  } catch (e) {
    return NextResponse.json({ ok: false, problem: e.message }, { status: 500 });
  }
}
