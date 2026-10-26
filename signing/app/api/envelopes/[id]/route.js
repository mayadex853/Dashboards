import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";
import { recipientsFor, releaseIntake } from "@/lib/envelopes";

export const GET = route(async (_req, { id }) => {
  const envelope = await db.get("envelopes", id);
  if (!envelope) throw httpError("Not found", 404);
  const recipients = (await recipientsFor(id)).map(({ token_hash, ...r }) => r);
  const events = await db.list("events", { envelope_id: id }, { order: "created_at", asc: true });
  return { envelope, recipients, events };
});

export const DELETE = route(async (_req, { id }) => {
  const env = await db.get("envelopes", id);
  if (!env) return;
  // Only drafts can be deleted: sent/completed envelopes are the legal record
  if (env.status !== "draft") throw httpError("Only drafts can be deleted. Void a sent envelope instead.");
  await releaseIntake(env);
  for (const r of await recipientsFor(id)) await db.remove("recipients", r.id);
  for (const ev of await db.list("events", { envelope_id: id })) await db.remove("events", ev.id);
  await db.remove("envelopes", id);
  await db.removeFiles(`envelopes/${id}/`).catch(() => {});
});
