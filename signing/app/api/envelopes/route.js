import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";
import { createEnvelope, sendEnvelope } from "@/lib/envelopes";

export const GET = route(async () => db.list("envelopes"));

/** multipart: file? + payload (JSON: {title, templateId?, fields?, recipients, message?, values?, send?}) */
export const POST = route(async (req) => {
  const form = await req.formData();
  const payload = JSON.parse(form.get("payload") || "{}");
  const file = form.get("file");
  if (!payload.recipients?.length) throw httpError("Add at least one signer");
  for (const r of payload.recipients) if (!r.name || !/^\S+@\S+\.\S+$/.test(r.email || "")) throw httpError(`Signer needs a name and valid email`);
  const env = await createEnvelope({
    ...payload,
    pdfBytes: file && typeof file !== "string" ? new Uint8Array(await file.arrayBuffer()) : undefined,
  });
  const links = payload.send ? await sendEnvelope(env.id) : [];
  return { envelope: env, links };
});
