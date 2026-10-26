import { NextResponse } from "next/server";
import { health } from "@/lib/db";
import { emailAuthProblem } from "@/lib/email";
import { SESSION_COOKIE, verifySessionValue } from "@/lib/session";

export const dynamic = "force-dynamic";

// Public: only says whether things work. The reasons (which can name internal accounts) go to the signed-in admin only.
export async function GET(req) {
  const admin = await verifySessionValue(req.cookies.get(SESSION_COOKIE)?.value);
  try {
    const [h, emailProblem] = await Promise.all([health(), emailAuthProblem()]);
    return NextResponse.json({ ok: h.ok, email: !emailProblem, ...(admin ? { mode: h.mode, problem: h.problem, emailProblem } : {}) });
  } catch (e) {
    return NextResponse.json({ ok: false, email: false, ...(admin ? { problem: e.message } : {}) }, { status: 500 });
  }
}
