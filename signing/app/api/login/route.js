import { NextResponse } from "next/server";
import crypto from "node:crypto";
import * as db from "@/lib/db";
import { SESSION_COOKIE, createSessionValue } from "@/lib/session";

const WINDOW_MS = 15 * 60_000;
const MAX_FAILS_PER_IP = 8;
const MAX_FAILS_ALL = 120; // blunts distributed guessing without letting a stranger lock you out easily
const memory = new Map(); // fallback if the database is unreachable

const sha = (v) => crypto.createHash("sha256").update(String(v)).digest();

export async function POST(req) {
  const ip = (req.headers.get("x-forwarded-for") || req.headers.get("x-real-ip") || "local").split(",")[0].trim();
  const since = new Date(Date.now() - WINDOW_MS).toISOString();

  // Failed attempts are stored in the database so the limit holds across serverless instances.
  let useDb = true;
  let failsIp = 0;
  let failsAll = 0;
  try {
    [failsIp, failsAll] = await Promise.all([db.countSince("events", { type: "login_failed", ip }, since), db.countSince("events", { type: "login_failed" }, since)]);
  } catch {
    useDb = false;
    const m = memory.get(ip) || { n: 0, t: Date.now() };
    if (Date.now() - m.t > WINDOW_MS) Object.assign(m, { n: 0, t: Date.now() });
    failsIp = m.n;
  }
  if (failsIp >= MAX_FAILS_PER_IP || failsAll >= MAX_FAILS_ALL)
    return NextResponse.json({ error: "Too many attempts. Try again in 15 minutes." }, { status: 429 });

  const { password } = await req.json().catch(() => ({}));
  const expected = process.env.ADMIN_PASSWORD;
  if (!expected) return NextResponse.json({ error: "ADMIN_PASSWORD is not set on the server." }, { status: 500 });
  const ok = typeof password === "string" && crypto.timingSafeEqual(sha(password), sha(expected));
  if (!ok) {
    if (useDb) await db.insert("events", { type: "login_failed", ip, user_agent: req.headers.get("user-agent") }).catch(() => {});
    else {
      const m = memory.get(ip) || { n: 0, t: Date.now() };
      m.n++;
      memory.set(ip, m);
    }
    return NextResponse.json({ error: "Wrong password" }, { status: 401 });
  }
  memory.delete(ip);
  let session;
  try {
    session = await createSessionValue();
  } catch (e) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
  const res = NextResponse.json({ ok: true });
  res.cookies.set(SESSION_COOKIE, session.value, { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", maxAge: session.maxAge, path: "/" });
  return res;
}
