import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";
import { sendEnvelope, notifyRecipient, recipientsFor, logEvent, signTokenFor, hashToken, appUrl, notifyStopped, releaseIntake } from "@/lib/envelopes";

// POST { action: "send" | "remind" | "link" | "void", recipient_id? }
export const POST = route(async (req, { id }) => {
  const { action, recipient_id } = await req.json();
  const env = await db.get("envelopes", id);
  if (!env) throw httpError("Not found", 404);
  if (["completed", "voided", "declined"].includes(env.status) && action !== "link") throw httpError(`Envelope is ${env.status}`);

  if (action === "send") {
    if (env.status !== "draft") throw httpError("Already sent");
    return { links: await sendEnvelope(id) };
  }
  const r = recipient_id ? (await recipientsFor(id)).find((x) => x.id === recipient_id) : null;
  if (action === "remind") {
    if (!r || r.status === "signed" || r.status === "pending") throw httpError("Nothing to remind");
    return { links: [await notifyRecipient(env, r, { reminder: true })] };
  }
  if (action === "link") {
    // Fresh signing link without emailing (for signing yourself, or texting a link)
    if (!r || r.status === "signed") throw httpError("No link available");
    if (env.status !== "sent") throw httpError("Send the envelope first");
    const token = signTokenFor(r.id);
    await db.update("recipients", r.id, { token_hash: hashToken(token) });
    await logEvent(id, "link_generated", { recipient_id: r.id });
    return { link: `${appUrl()}/s/${token}` };
  }
  if (action === "void") {
    const won = await db.updateWhere("envelopes", id, { status: env.status }, { status: "voided", voided_at: new Date().toISOString() });
    if (!won) throw httpError("The envelope changed. Refresh and try again.", 409);
    for (const x of await recipientsFor(id)) await db.update("recipients", x.id, { token_hash: null });
    await releaseIntake(env);
    await logEvent(id, "voided");
    await notifyStopped(env, { reason: "voided" });
    return { ok: true };
  }
  throw httpError("Unknown action");
});
