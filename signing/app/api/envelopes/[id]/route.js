import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";
import { recipientsFor } from "@/lib/envelopes";

export const GET = route(async (_req, { id }) => {
  const envelope = await db.get("envelopes", id);
  if (!envelope) throw httpError("Not found", 404);
  const recipients = (await recipientsFor(id)).map(({ token_hash, ...r }) => r);
  const events = await db.list("events", { envelope_id: id }, { order: "created_at", asc: true });
  return { envelope, recipients, events };
});

export const DELETE = route(async (_req, { id }) => {
  const env = await db.get("envelopes", id);
  if (env?.status === "completed") throw httpError("Completed envelopes can't be deleted");
  for (const r of await recipientsFor(id)) await db.remove("recipients", r.id);
  await db.remove("envelopes", id);
});
