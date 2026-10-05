import { NextResponse } from "next/server";
import crypto from "node:crypto";
import { SESSION_COOKIE, createSessionValue } from "@/lib/session";

const attempts = new Map(); // simple in-memory throttle per IP

export async function POST(req) {
  const ip = (req.headers.get("x-forwarded-for") || "local").split(",")[0];
  const a = attempts.get(ip) || { n: 0, t: Date.now() };
  if (Date.now() - a.t > 15 * 60_000) Object.assign(a, { n: 0, t: Date.now() });
  if (a.n >= 10) return NextResponse.json({ error: "Too many attempts. Try again in 15 minutes." }, { status: 429 });

  const { password } = await req.json().catch(() => ({}));
  const expected = process.env.ADMIN_PASSWORD;
  if (!expected) return NextResponse.json({ error: "ADMIN_PASSWORD is not set on the server." }, { status: 500 });
  const ok =
    typeof password === "string" &&
    password.length === expected.length &&
    crypto.timingSafeEqual(Buffer.from(password), Buffer.from(expected));
  if (!ok) {
    a.n++;
    attempts.set(ip, a);
    return NextResponse.json({ error: "Wrong password" }, { status: 401 });
  }
  attempts.delete(ip);
  const { value, maxAge } = await createSessionValue();
  const res = NextResponse.json({ ok: true });
  res.cookies.set(SESSION_COOKIE, value, { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", maxAge, path: "/" });
  return res;
}
