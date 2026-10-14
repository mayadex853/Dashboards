import { NextResponse } from "next/server";
import { SESSION_COOKIE, verifySessionValue } from "@/lib/session";

// Everything is private except the login page and the signee-facing links.
const PUBLIC = [/^\/login/, /^\/api\/login/, /^\/s\//, /^\/i\//, /^\/api\/public\//, /^\/_next\//, /^\/pdf\.worker/, /^\/favicon/];

export async function middleware(req) {
  const { pathname } = req.nextUrl;
  if (PUBLIC.some((re) => re.test(pathname))) return NextResponse.next();
  const ok = await verifySessionValue(req.cookies.get(SESSION_COOKIE)?.value);
  if (ok) return NextResponse.next();
  if (pathname.startsWith("/api/")) return NextResponse.json({ error: "Not signed in" }, { status: 401 });
  const url = req.nextUrl.clone();
  url.pathname = "/login";
  url.search = "";
  return NextResponse.redirect(url);
}

export const config = { matcher: ["/((?!_next/static|_next/image).*)"] };
