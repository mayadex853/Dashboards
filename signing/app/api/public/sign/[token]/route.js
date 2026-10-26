import { cookies } from "next/headers";
import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";
import { recipientByToken, isTurn, logEvent, submitSignature, clientInfo, getProfile, notifyStopped, releaseIntake } from "@/lib/envelopes";
import { sendEmail, emailLayout } from "@/lib/email";
import { SESSION_COOKIE, verifySessionValue } from "@/lib/session";

async function load(token) {
  const found = await recipientByToken(token);
  if (!found) throw httpError("This signing link is invalid or has already been used.", 404);
  if (found.env.status === "voided") throw httpError("This document was voided by the sender.", 410);
  if (found.env.status === "declined") throw httpError("This document was declined and is no longer active.", 410);
  return found;
}

export const maxDuration = 60;

export const GET = route(async (req, { token }) => {
  const { r, env } = await load(token);
  const turn = await isTurn(env, r);
  if (!r.viewed_at && turn) {
    const info = clientInfo(req);
    // compare-and-set so a view can never overwrite a status that changed in the meantime
    const marked = await db.updateWhere("recipients", r.id, { status: r.status, viewed_at: null }, { viewed_at: new Date().toISOString(), status: r.status === "sent" ? "viewed" : r.status });
    if (marked) await logEvent(env.id, "viewed", { recipient_id: r.id, ...info });
  }
  // Your saved signature is only offered when you're logged in and this is your signer slot
  const isAdmin = r.is_me && (await verifySessionValue((await cookies()).get(SESSION_COOKIE)?.value));
  const profile = isAdmin ? await getProfile() : null;
  return {
    title: env.title,
    message: env.message,
    signer: { name: r.name, email: r.email, status: r.status },
    turn,
    fields: env.fields.filter((f) => Number(f.role) === r.role_index && !f.stamped),
    saved: profile ? { signature: profile.signature, initials: profile.initials } : null,
    sender: process.env.MAIL_FROM_NAME || "TakaSign",
  };
}, { expose: false });

export const POST = route(async (req, { token }) => {
  const { r, env } = await load(token);
  const body = await req.json().catch(() => ({}));
  const info = clientInfo(req);
  if (env.status !== "sent") throw httpError("This document isn't open for signing.");
  if (r.status === "signed") throw httpError("You've already signed.");
  if (!(await isTurn(env, r))) throw httpError("It's not your turn to sign yet. You'll get an email when it is.");

  if (body.action === "decline") {
    const won = await db.updateWhere("envelopes", env.id, { status: "sent" }, { status: "declined" });
    if (!won) throw httpError("This document isn't open for signing.");
    await releaseIntake(env);
    await logEvent(env.id, "declined", { recipient_id: r.id, detail: { reason: body.reason || "" }, ...info });
    await notifyStopped(env, { reason: "declined", by: r });
    if (process.env.MAIL_FROM)
      await sendEmail({
        to: process.env.MAIL_FROM,
        subject: `Declined: ${env.title}`,
        html: emailLayout({ heading: `${r.name} declined to sign`, intro: `Reason: ${body.reason || "(none given)"}` }),
      });
    return { ok: true };
  }

  if (!body.consent) throw httpError("Please agree to sign electronically.");
  await submitSignature(env.id, r.id, body.values || {}, { ...info, tz: body.tz });
  return { ok: true };
}, { expose: false });
