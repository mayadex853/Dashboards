import { cookies } from "next/headers";
import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";
import { recipientByToken, isTurn, logEvent, submitSignature, clientInfo, getProfile } from "@/lib/envelopes";
import { sendEmail, emailLayout } from "@/lib/email";
import { SESSION_COOKIE, verifySessionValue } from "@/lib/session";

async function load(token) {
  const found = await recipientByToken(token);
  if (!found) throw httpError("This signing link is invalid or has already been used.", 404);
  if (found.env.status === "voided") throw httpError("This document was voided by the sender.", 410);
  if (found.env.status === "declined") throw httpError("This document was declined and is no longer active.", 410);
  return found;
}

export const GET = route(async (req, { token }) => {
  const { r, env } = await load(token);
  const turn = await isTurn(env, r);
  if (!r.viewed_at && turn) {
    const info = clientInfo(req);
    await db.update("recipients", r.id, { viewed_at: new Date().toISOString(), status: r.status === "signed" ? "signed" : "viewed" });
    await logEvent(env.id, "viewed", { recipient_id: r.id, ...info });
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
    sender: process.env.MAIL_FROM_NAME || "HD Music",
  };
});

export const POST = route(async (req, { token }) => {
  const { r, env } = await load(token);
  const body = await req.json();
  const info = clientInfo(req);
  if (env.status !== "sent") throw httpError("This document isn't open for signing.");
  if (r.status === "signed") throw httpError("You've already signed.");
  if (!(await isTurn(env, r))) throw httpError("It's not your turn to sign yet. You'll get an email when it is.");

  if (body.action === "decline") {
    await db.update("envelopes", env.id, { status: "declined" });
    await logEvent(env.id, "declined", { recipient_id: r.id, detail: { reason: body.reason || "" }, ...info });
    if (process.env.MAIL_FROM)
      await sendEmail({
        to: process.env.MAIL_FROM,
        subject: `Declined: ${env.title}`,
        html: emailLayout({ heading: `${r.name} declined to sign`, intro: `Reason: ${body.reason || "(none given)"}` }),
      });
    return { ok: true };
  }

  if (!body.consent) throw httpError("Please agree to sign electronically.");
  await db.update("recipients", r.id, { consent_at: new Date().toISOString() });
  await logEvent(env.id, "consented", { recipient_id: r.id, ...info });
  await submitSignature(env, r, body.values || {}, { ...info, localDate: body.localDate });
  return { ok: true };
});
