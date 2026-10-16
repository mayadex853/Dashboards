import { NextResponse } from "next/server";
import { health } from "@/lib/db";
import { emailAuthProblem } from "@/lib/email";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const emailProblem = await emailAuthProblem();
    return NextResponse.json({ ...(await health()), email: !emailProblem, emailProblem });
  } catch (e) {
    return NextResponse.json({ ok: false, problem: e.message }, { status: 500 });
  }
}
