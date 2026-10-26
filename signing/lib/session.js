// Admin session cookie: "<expiry>.<hmac>" signed with SESSION_SECRET.
// Uses Web Crypto so it runs in both middleware (edge) and route handlers.
export const SESSION_COOKIE = "hd_session";
const MAX_AGE = 60 * 60 * 24 * 30; // 30 days

const enc = new TextEncoder();

// There is deliberately no built-in default secret: without one, nobody can log in
// (a known default would let anyone forge a session cookie).
function secret() {
  return process.env.SESSION_SECRET || process.env.ADMIN_PASSWORD || null;
}

async function hmac(value) {
  const s = secret();
  if (!s) throw new Error("SESSION_SECRET is not set on the server.");
  const key = await crypto.subtle.importKey("raw", enc.encode(s), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(value));
  return Array.from(new Uint8Array(sig), (b) => b.toString(16).padStart(2, "0")).join("");
}

export async function createSessionValue() {
  const exp = Math.floor(Date.now() / 1000) + MAX_AGE;
  return { value: `${exp}.${await hmac(String(exp))}`, maxAge: MAX_AGE };
}

export async function verifySessionValue(value) {
  try {
    if (!value || !secret()) return false;
    const [exp, sig] = value.split(".");
    if (!exp || !sig || !Number.isFinite(Number(exp)) || Number(exp) < Date.now() / 1000) return false;
    const expected = await hmac(exp);
    if (expected.length !== sig.length) return false;
    let diff = 0;
    for (let i = 0; i < sig.length; i++) diff |= expected.charCodeAt(i) ^ sig.charCodeAt(i);
    return diff === 0;
  } catch {
    return false;
  }
}
