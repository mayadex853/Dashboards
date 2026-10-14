// Envelope workflow: create → send in routing order → each signer signs → complete with audit certificate.
import "server-only";
import crypto from "node:crypto";
import { PDFDocument, StandardFonts, rgb } from "pdf-lib";
import * as db from "@/lib/db";
import { stampPdf } from "@/lib/stamp";
import { sendEmail, emailLayout } from "@/lib/email";
import { resolveKey, today } from "@/lib/fields";

export const sha256 = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
export const newToken = () => crypto.randomBytes(24).toString("base64url");
export const hashToken = (t) => crypto.createHash("sha256").update(String(t)).digest("hex");
export const appUrl = () => (process.env.APP_URL || "http://localhost:3000").replace(/\/$/, "");

export async function logEvent(envelope_id, type, { recipient_id = null, detail = null, ip = null, user_agent = null } = {}) {
  return db.insert("events", { envelope_id, recipient_id, type, detail, ip, user_agent });
}

export async function getProfile() {
  return (await db.get("profile", "me")) || { id: "me", data: {}, signature: null, initials: null };
}

/**
 * Create a draft envelope.
 * @param {{title, pdfBytes?, templateId?, fields, recipients: {name,email,routing_order,role_index,is_me}[], message?, source?, intakeId?, values?: Record<string,string>}} input
 *   values: extra key values (e.g. deal.advance) used to prefill keyed fields
 */
export async function createEnvelope(input) {
  const id = crypto.randomUUID();
  let pdfBytes = input.pdfBytes;
  let fields = input.fields || [];
  let templateId = input.templateId || null;
  if (templateId) {
    const t = await db.get("templates", templateId);
    if (!t) throw new Error("Template not found");
    pdfBytes = await db.getFile(t.pdf_path);
    if (!input.fields) fields = t.fields;
  }
  if (!pdfBytes) throw new Error("No document");

  // Prefill keyed fields from profile / intake / deal values
  const profile = await getProfile();
  const intake = input.intakeId ? await db.get("intakes", input.intakeId) : null;
  const ctx = { profile: profile.data || {}, intake: intake?.answers || {}, deal: { ...(intake?.deal || {}) } };
  for (const [k, v] of Object.entries(input.values || {})) {
    const [ns, ...rest] = k.split(".");
    ctx[ns] = { ...(ctx[ns] || {}), [rest.join(".")]: v };
  }
  fields = fields.map((f) => {
    const v = f.key ? resolveKey(f.key, ctx) : undefined;
    return { ...f, value: f.value ?? v ?? (f.type === "text" ? f.defaultValue : undefined) };
  });

  const original_pdf_path = `envelopes/${id}/original.pdf`;
  await db.putFile(original_pdf_path, pdfBytes);
  const env = await db.insert("envelopes", {
    id,
    title: input.title || "Untitled",
    status: "draft",
    source: input.source || (templateId ? "template" : "upload"),
    template_id: templateId,
    intake_id: input.intakeId || null,
    original_pdf_path,
    current_pdf_path: original_pdf_path,
    original_sha256: sha256(pdfBytes),
    fields,
    message: input.message || null,
  });
  for (const r of input.recipients) {
    await db.insert("recipients", {
      envelope_id: id,
      role_index: Number(r.role_index ?? 0),
      name: r.name,
      email: r.email,
      routing_order: Number(r.routing_order || 1),
      is_me: !!r.is_me,
      status: "pending",
    });
  }
  await logEvent(id, "created", { detail: { title: env.title } });
  return env;
}

export async function recipientsFor(envelopeId) {
  return db.list("recipients", { envelope_id: envelopeId }, { order: "routing_order", asc: true });
}

/** Email (and generate links for) every recipient in the lowest unsigned routing order. */
export async function advance(envelopeId) {
  const env = await db.get("envelopes", envelopeId);
  const recs = await recipientsFor(envelopeId);
  const unsigned = recs.filter((r) => r.status !== "signed");
  if (!unsigned.length) return completeEnvelope(envelopeId);
  const order = Math.min(...unsigned.map((r) => r.routing_order));
  const results = [];
  for (const r of unsigned.filter((r) => r.routing_order === order && r.status === "pending")) {
    results.push(await notifyRecipient(env, r));
  }
  return results;
}

/** Issue a fresh signing link for a recipient and email it. Returns the link. */
export async function notifyRecipient(env, r, { reminder = false } = {}) {
  const token = newToken();
  await db.update("recipients", r.id, {
    token_hash: hashToken(token),
    status: r.status === "pending" ? "sent" : r.status,
    sent_at: new Date().toISOString(),
  });
  const link = `${appUrl()}/s/${token}`;
  const sender = process.env.MAIL_FROM_NAME || "HD Music";
  const mail = await sendEmail({
    to: r.email,
    subject: `${reminder ? "Reminder: " : ""}Please sign: ${env.title}`,
    html: emailLayout({
      heading: `${sender} sent you a document to sign`,
      intro: `Hi ${r.name},\n\n${env.message || `Please review and sign "${env.title}".`}`,
      buttonText: "Review & sign",
      buttonUrl: link,
      note: "This link is unique to you. Do not forward this email.",
    }),
  });
  await logEvent(env.id, reminder ? "reminder_sent" : "sent", { recipient_id: r.id, detail: { email: r.email, emailed: mail.sent } });
  return { recipient_id: r.id, name: r.name, email: r.email, link, emailed: mail.sent };
}

export async function sendEnvelope(envelopeId) {
  await db.update("envelopes", envelopeId, { status: "sent", sent_at: new Date().toISOString() });
  return advance(envelopeId);
}

export async function recipientByToken(token) {
  if (!token) return null;
  const r = await db.findOne("recipients", { token_hash: hashToken(token) });
  if (!r) return null;
  const env = await db.get("envelopes", r.envelope_id);
  if (!env) return null;
  return { r, env };
}

/** Is it this recipient's turn? (Everyone in a lower routing order has signed.) */
export async function isTurn(env, r) {
  const recs = await recipientsFor(env.id);
  return recs.filter((x) => x.routing_order < r.routing_order).every((x) => x.status === "signed");
}

/**
 * Apply a signer's values to the working PDF and advance the envelope.
 * @param values Record<fieldId, value>
 */
export async function submitSignature(env, r, values, { ip, user_agent, localDate }) {
  const mine = env.fields.filter((f) => Number(f.role) === r.role_index && !f.stamped);
  // Use the signer's local date if it's plausible (avoids UTC rollover in the evening)
  const ld = Date.parse(localDate);
  const signDate = ld && Math.abs(ld - Date.now()) < 36 * 3600 * 1000 ? String(localDate).slice(0, 40) : today();
  const filled = mine.map((f) => ({ ...f, value: f.type === "date" ? signDate : values[f.id] ?? f.value }));
  const missing = filled.filter((f) => f.required !== false && f.type !== "checkbox" && !f.value);
  if (missing.length) throw new Error(`Please complete: ${missing.map((f) => f.label || f.type).join(", ")}`);

  const current = await db.getFile(env.current_pdf_path);
  const stamped = await stampPdf(current, filled);
  const path = `envelopes/${env.id}/after-${r.id}.pdf`;
  await db.putFile(path, stamped);
  // Keep signed values (minus signature images) on the envelope for the record
  const filledById = Object.fromEntries(filled.map((f) => [f.id, f]));
  const fields = env.fields.map((f) =>
    filledById[f.id] ? { ...f, value: f.type === "signature" || f.type === "initials" ? "[signed]" : filledById[f.id].value, stamped: true } : f
  );
  await db.update("envelopes", env.id, { current_pdf_path: path, fields });
  const now = new Date().toISOString();
  await db.update("recipients", r.id, { status: "signed", signed_at: now, ip, user_agent, token_hash: null });
  await logEvent(env.id, "signed", { recipient_id: r.id, ip, user_agent, detail: { name: r.name, email: r.email } });
  return advance(env.id);
}

export async function completeEnvelope(envelopeId) {
  const env = await db.get("envelopes", envelopeId);
  if (env.status === "completed") return [];
  const recs = await recipientsFor(envelopeId);
  const events = await db.list("events", { envelope_id: envelopeId }, { order: "created_at", asc: true });
  const signed = await stampPdf(await db.getFile(env.current_pdf_path), [], { flattenForm: true });
  const finalBytes = await appendCertificate(signed, env, recs, events);
  const final_sha256 = sha256(finalBytes);
  const final_pdf_path = `envelopes/${env.id}/completed.pdf`;
  await db.putFile(final_pdf_path, finalBytes);
  await db.update("envelopes", env.id, { status: "completed", completed_at: new Date().toISOString(), final_pdf_path, final_sha256 });
  await logEvent(env.id, "completed", { detail: { final_sha256 } });

  const name = `${env.title.replace(/[^\w\- ]+/g, "").trim() || "document"} - signed.pdf`;
  const emails = [...new Set(recs.map((r) => r.email.toLowerCase()))];
  if (process.env.MAIL_FROM && !emails.includes(process.env.MAIL_FROM.toLowerCase())) emails.push(process.env.MAIL_FROM);
  for (const to of emails) {
    await sendEmail({
      to,
      subject: `Completed: ${env.title}`,
      html: emailLayout({
        heading: "All parties have signed",
        intro: `"${env.title}" is fully executed. The signed copy with its certificate of completion is attached.`,
        note: finalBytes.length > 2.8 * 1024 * 1024 ? "The file was too large to attach. Reply to this email to request a copy." : `Document fingerprint (SHA-256): ${final_sha256}`,
      }),
      attachments: [{ name, bytes: finalBytes }],
    });
  }
  // Mark linked intake as contracted
  if (env.intake_id) await db.update("intakes", env.intake_id, { status: "contracted" });
  return [];
}

/** Adds a "Certificate of Completion" page with the full audit trail. */
async function appendCertificate(pdfBytes, env, recs, events) {
  const doc = await PDFDocument.load(pdfBytes, { ignoreEncryption: true });
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const bold = await doc.embedFont(StandardFonts.HelveticaBold);
  let page = doc.addPage([612, 792]);
  let y = 740;
  const grey = rgb(0.4, 0.4, 0.4);
  const line = (text, { f = font, size = 9.5, color = rgb(0.1, 0.1, 0.1), indent = 0 } = {}) => {
    if (y < 60) {
      page = doc.addPage([612, 792]);
      y = 740;
    }
    const safe = String(text).replace(/[^\x20-\x7E]/g, "?");
    page.drawText(safe.slice(0, 120), { x: 50 + indent, y, size, font: f, color });
    y -= size + 6;
  };
  const fmt = (t) => (t ? new Date(t).toUTCString() : "—");

  line("Certificate of Completion", { f: bold, size: 18 });
  y -= 6;
  line(`Document: ${env.title}`);
  line(`Envelope ID: ${env.id}`);
  line(`Sent by: ${process.env.MAIL_FROM_NAME || ""} <${process.env.MAIL_FROM || ""}>`);
  line(`Created: ${fmt(env.created_at)}    Completed: ${fmt(new Date())}`);
  line(`Original document SHA-256: ${env.original_sha256}`, { size: 8, color: grey });
  y -= 10;
  line("Signers", { f: bold, size: 12 });
  for (const r of recs) {
    line(`${r.routing_order}. ${r.name} <${r.email}>`, { f: bold });
    line(`Sent: ${fmt(r.sent_at)}   Viewed: ${fmt(r.viewed_at)}`, { indent: 12 });
    line(`Consented to electronic signature: ${fmt(r.consent_at)}`, { indent: 12 });
    line(`Signed: ${fmt(r.signed_at)}`, { indent: 12 });
    line(`IP address: ${r.ip || "—"}`, { indent: 12 });
    line(`Device: ${(r.user_agent || "—").slice(0, 100)}`, { indent: 12, size: 8, color: grey });
    y -= 4;
  }
  y -= 6;
  line("Event history (UTC)", { f: bold, size: 12 });
  const byId = Object.fromEntries(recs.map((r) => [r.id, r]));
  for (const e of events) {
    const who = e.recipient_id && byId[e.recipient_id] ? ` - ${byId[e.recipient_id].name} <${byId[e.recipient_id].email}>` : "";
    line(`${fmt(e.created_at)}  ${e.type.replace(/_/g, " ")}${who}${e.ip ? `  (IP ${e.ip})` : ""}`, { size: 8.5 });
  }
  y -= 10;
  line("Each signer agreed to conduct this transaction electronically under the U.S. ESIGN Act and UETA.", { size: 8, color: grey });
  return new Uint8Array(await doc.save());
}

export function clientInfo(req) {
  const ip = (req.headers.get("x-forwarded-for") || "").split(",")[0].trim() || req.headers.get("x-real-ip") || null;
  return { ip, user_agent: req.headers.get("user-agent") || null };
}
