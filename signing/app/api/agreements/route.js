import * as db from "@/lib/db";
import { route } from "@/lib/http";
import { envelopeView } from "@/lib/fields";

// Everything the Agreements page lists: envelopes (with recipients) and documents you signed yourself.
export const GET = route(async () => {
  const [envelopes, recipients, quick] = await Promise.all([db.list("envelopes"), db.list("recipients"), db.list("quick_signs")]);
  const byEnv = {};
  for (const { token_hash, ...r } of recipients) (byEnv[r.envelope_id] ||= []).push(r);
  return {
    envelopes: envelopes.map(({ fields, ...e }) => envelopeView(e, byEnv[e.id] || [])),
    quick,
  };
});
