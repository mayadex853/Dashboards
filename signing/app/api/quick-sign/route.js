import crypto from "node:crypto";
import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";
import { sha256 } from "@/lib/envelopes";
import { sendEmail, emailLayout } from "@/lib/email";

export const GET = route(async () => db.list("quick_signs"));

/** multipart: file (already-signed PDF from the browser), title, email_to?, message? */
export const POST = route(async (req) => {
  const form = await req.formData();
  const file = form.get("file");
  if (!file || typeof file === "string") throw httpError("Missing PDF");
  const bytes = new Uint8Array(await file.arrayBuffer());
  const id = crypto.randomUUID();
  const title = String(form.get("title") || "Signed document");
  const pdf_path = `quick/${id}.pdf`;
  await db.putFile(pdf_path, bytes);
  const to = String(form.get("email_to") || "").split(/[,;\s]+/).filter(Boolean);
  let emailed = false;
  if (to.length) {
    const r = await sendEmail({
      to,
      subject: `Signed: ${title}`,
      html: emailLayout({ heading: "Signed document attached", intro: String(form.get("message") || `Please find the signed "${title}" attached.`) }),
      attachments: [{ name: `${title.replace(/[^\w\- ]+/g, "")}.pdf`, bytes }],
    });
    emailed = r.sent;
  }
  const rec = await db.insert("quick_signs", { id, title, pdf_path, sha256: sha256(bytes), emailed_to: emailed ? to.join(", ") : null });
  return { record: rec, emailed };
});
