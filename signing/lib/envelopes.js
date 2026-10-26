// Envelope workflow: create → send in routing order → each signer signs → complete with audit certificate.
import "server-only";
import crypto from "node:crypto";
import { PDFDocument, StandardFonts, rgb } from "pdf-lib";
import * as db from "@/lib/db";
import { stampPdf } from "@/lib/stamp";
import { sendEmail, emailLayout, MAX_ATTACH_BYTES } from "@/lib/email";
import { httpError } from "@/lib/http";
import { resolveKey } from "@/lib/fields";

export const sha256 = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
export const newToken = () => crypto.randomBytes(24).toString("base64url");
export const hashToken = (t) => crypto.createHash("sha256").update(String(t)).digest("hex");

/**
 * A recipient's signing link is derived from the server secret, so it is always the same link.
 * That way "Resend" or "Copy signing link" never breaks a link that was already emailed.
 * (Only a hash is stored; voiding clears it, which kills the link.)
 */
export function signTokenFor(recipientId) {
  const secret = process.env.SESSION_SECRET || process.env.ADMIN_PASSWORD;
  if (!secret) throw new Error("SESSION_SECRET is not set on the server.");
  return crypto.createHmac("sha256", secret).update(`sign:${recipientId}`).digest("base64url");
}

/** Today's date as the signer sees it, computed on the server so it can't be backdated or spoofed. */
export function dateIn(tz) {
  const opts = { year: "numeric", month: "long", day: "numeric" };
  try {
    return new Date().toLocaleDateString("en-US", { ...opts, timeZone: tz || "UTC" });
  } catch {
    return new Date().toLocaleDateString("en-US", { ...opts, timeZone: "UTC" });
  }
}
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
    subject: input.subject || null,
  });
  for (const r of input.recipients) {
    await db.insert("recipients", {
      envelope_id: id,
      role_index: Number(r.role_index ?? 0),
      name: r.name,
      email: r.email,
      routing_order: Number(r.routing_order || 1),
      is_me: !!r.is_me,
      kind: r.kind === "cc" ? "cc" : "signer",
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
  const unsigned = recs.filter((r) => r.kind !== "cc" && r.status !== "signed");
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
  const token = signTokenFor(r.id);
  await db.update("recipients", r.id, {
    token_hash: hashToken(token),
    status: r.status === "pending" ? "sent" : r.status,
    sent_at: new Date().toISOString(),
  });
  const link = `${appUrl()}/s/${token}`;
  const sender = process.env.MAIL_FROM_NAME || "TakaSign";
  const mail = await sendEmail({
    to: r.email,
    subject: `${reminder ? "Reminder: " : ""}${env.subject || `Complete with TakaSign: ${env.title}`}`,
    html: emailLayout({
      heading: `${sender} sent you a document to sign`,
      intro: `Hi ${r.name},\n\n${env.message || `Please review and sign "${env.title}".`}`,
      buttonText: "Review & sign",
      buttonUrl: link,
      note: "This link is unique to you. Do not forward this email.",
    }),
  });
  await logEvent(env.id, reminder ? "reminder_sent" : "sent", {
    recipient_id: r.id,
    detail: { email: r.email, emailed: mail.sent, ...(mail.sent ? {} : { email_error: mail.reason }) },
  });
  return { recipient_id: r.id, name: r.name, email: r.email, link, emailed: mail.sent, emailError: mail.sent ? null : mail.reason };
}

export async function sendEnvelope(envelopeId) {
  const won = await db.updateWhere("envelopes", envelopeId, { status: "draft" }, { status: "sent", sent_at: new Date().toISOString() });
  if (!won) throw httpError("This envelope was already sent.");
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
  return recs.filter((x) => x.kind !== "cc" && x.routing_order < r.routing_order).every((x) => x.status === "signed");
}

const PNG_DATA_URL = /^data:image\/png;base64,[A-Za-z0-9+/]+=*$/;
const MAX_SIGNATURE_CHARS = 600_000;

/** Keep only values for this signer's fields, with sane types and sizes (the signer's browser is untrusted). */
function sanitizeValues(fieldsForSigner, raw) {
  const out = {};
  for (const f of fieldsForSigner) {
    const v = raw?.[f.id];
    if (v === undefined || v === null) continue;
    if (f.type === "signature" || f.type === "initials") {
      if (typeof v !== "string" || v.length > MAX_SIGNATURE_CHARS || !PNG_DATA_URL.test(v))
        throw httpError("That signature image isn't valid. Please redraw it and try again.");
      out[f.id] = v;
    } else if (f.type === "checkbox") {
      out[f.id] = v === true;
    } else {
      out[f.id] = String(v).replace(/[\u0000-\u001f\u007f]/g, " ").slice(0, 500);
    }
  }
  return out;
}

/**
 * Apply a signer's values to the working PDF, then move the envelope along.
 *
 * Safe against simultaneous requests:
 *  - the recipient is "claimed" first, so a double-click or replay can only sign once;
 *  - the PDF is saved with a compare-and-set on the version it started from. If a parallel
 *    signer saved first, we re-stamp on top of their version, so nobody's signature is lost.
 */
export async function submitSignature(envelopeId, recipientId, rawValues, { ip, user_agent, tz } = {}) {
  const r0 = await db.get("recipients", recipientId);
  if (!r0 || r0.kind === "cc") throw httpError("This signing link is invalid.", 404);
  if (r0.status === "signed" || r0.status === "signing") throw httpError("You've already signed this document.");
  const claimed = await db.updateWhere("recipients", r0.id, { status: r0.status }, { status: "signing" });
  if (!claimed) throw httpError("You've already signed this document.");

  let saved = false;
  try {
    for (let attempt = 0; attempt < 8 && !saved; attempt++) {
      const env = await db.get("envelopes", envelopeId);
      if (!env || env.status !== "sent") throw httpError("This document isn't open for signing.");

      const mine = env.fields.filter((f) => Number(f.role) === r0.role_index && !f.stamped);
      const values = sanitizeValues(mine, rawValues);
      const signDate = dateIn(tz);
      const fallback = (f) => (f.type === "name" ? r0.name : f.type === "email" ? r0.email : undefined);
      const filled = mine.map((f) => ({ ...f, value: f.type === "date" ? signDate : values[f.id] ?? f.value ?? fallback(f) }));
      const missing = filled.filter((f) => f.required !== false && !(f.type === "checkbox" ? f.value === true : f.value));
      if (missing.length) throw httpError(`Please complete: ${missing.map((f) => f.label || f.type).join(", ")}`);

      const current = await db.getFile(env.current_pdf_path);
      let stamped;
      try {
        stamped = await stampPdf(current, filled);
      } catch (e) {
        console.error("stamp failed", e);
        throw httpError("We couldn't apply your signature to this document. Please try again.", 500);
      }
      const path = `envelopes/${env.id}/after-${r0.id}.pdf`;
      await db.putFile(path, stamped);

      // Keep signed values (minus signature images) on the envelope for the record
      const byId = Object.fromEntries(filled.map((f) => [f.id, f]));
      const fields = env.fields.map((f) =>
        byId[f.id] ? { ...f, value: f.type === "signature" || f.type === "initials" ? "[signed]" : byId[f.id].value, stamped: true } : f
      );
      const won = await db.updateWhere("envelopes", env.id, { current_pdf_path: env.current_pdf_path, status: "sent" }, { current_pdf_path: path, fields });
      saved = !!won; // not won = a parallel signer saved first: loop and stamp on top of their version
    }
    if (!saved) throw httpError("Several people are signing at the same moment. Please try again.", 409);
  } catch (e) {
    await db.updateWhere("recipients", r0.id, { status: "signing" }, { status: r0.status }).catch(() => {});
    throw e;
  }

  const now = new Date().toISOString();
  // The link stays valid so the signer can download their copy later (signing again is blocked by status)
  await db.update("recipients", r0.id, { status: "signed", signed_at: now, consent_at: now, ip, user_agent });
  await logEvent(envelopeId, "consented", { recipient_id: r0.id, ip, user_agent });
  await logEvent(envelopeId, "signed", { recipient_id: r0.id, ip, user_agent, detail: { name: r0.name, email: r0.email } });
  await advance(envelopeId);
  await notifyProgress(envelopeId, r0);
}

/**
 * DocuSign-style progress emails after someone signs:
 * the signer gets a confirmation, and the sender hears who signed and who's next.
 * (When the last person signs, the completion email to everyone covers it.)
 */
async function notifyProgress(envelopeId, signer) {
  const env = await db.get("envelopes", envelopeId);
  if (env.status === "completed") return;
  const recs = await recipientsFor(envelopeId);
  const pending = recs.filter((x) => x.kind !== "cc" && x.status !== "signed");
  const order = pending.length ? Math.min(...pending.map((x) => x.routing_order)) : null;
  const next = pending.filter((x) => x.routing_order === order);
  const nextNames = next.map((x) => (x.is_me ? "you" : x.name)).join(" and ");
  const nextForSigner = next.map((x) => (x.is_me ? process.env.MAIL_FROM_NAME || "the sender" : x.name)).join(" and ");
  const link = `${appUrl()}/envelopes/${env.id}`;

  if (!signer.is_me) {
    await sendEmail({
      to: signer.email,
      subject: `You signed: ${env.title}`,
      html: emailLayout({
        heading: "Thanks for signing",
        intro: `Hi ${signer.name},\n\nYou've signed "${env.title}". ${nextForSigner ? `It's now with ${nextForSigner}.` : ""} You'll receive the completed document by email once everyone has signed.`,
      }),
    });
    if (process.env.MAIL_FROM) {
      await sendEmail({
        to: process.env.MAIL_FROM,
        subject: `${signer.name} signed: ${env.title}`,
        html: emailLayout({
          heading: `${signer.name} signed "${env.title}"`,
          intro: nextNames ? `Next up: ${nextNames}.` : "Waiting for the remaining signers.",
          buttonText: next.some((x) => x.is_me) ? "Open and sign" : "View status",
          buttonUrl: next.some((x) => x.is_me) ? `${link}?sign=1` : link,
        }),
      });
    }
  }
}

/** Tell everyone already involved that the envelope was voided or declined. */
export async function notifyStopped(env, { reason, by }) {
  const recs = await recipientsFor(env.id);
  const involved = recs.filter((x) => x.kind !== "cc" && x.status !== "pending" && x.id !== by?.id && !x.is_me);
  for (const x of involved) {
    await sendEmail({
      to: x.email,
      subject: `${reason === "declined" ? "Declined" : "Voided"}: ${env.title}`,
      html: emailLayout({
        heading: reason === "declined" ? `${by?.name || "A recipient"} declined to sign` : "This document was voided",
        intro: `"${env.title}" is no longer active, so no further action is needed from you.`,
      }),
    });
  }
}

export async function completeEnvelope(envelopeId) {
  // Only one request gets to complete an envelope (two parallel last-signers would otherwise both email everyone)
  const env = await db.updateWhere("envelopes", envelopeId, { status: "sent" }, { status: "completing" });
  if (!env) return [];

  let finalBytes, final_sha256, recs;
  try {
    recs = await recipientsFor(envelopeId);
    const events = await db.list("events", { envelope_id: envelopeId }, { order: "created_at", asc: true });
    const flattened = await stampPdf(await db.getFile(env.current_pdf_path), [], { flattenForm: true });
    finalBytes = await appendCertificate(flattened, env, recs, events);
    final_sha256 = sha256(finalBytes);
    const final_pdf_path = `envelopes/${env.id}/completed.pdf`;
    await db.putFile(final_pdf_path, finalBytes);
    await db.update("envelopes", env.id, { status: "completed", completed_at: new Date().toISOString(), final_pdf_path, final_sha256 });
  } catch (e) {
    await db.updateWhere("envelopes", env.id, { status: "completing" }, { status: "sent" }).catch(() => {});
    throw e;
  }
  await logEvent(env.id, "completed", { detail: { final_sha256 } });

  // Everyone gets the signed copy. If the PDF is too big to attach, signers get a link to download it.
  const name = `${env.title.replace(/[^\w\- ]+/g, "").trim() || "document"} - signed.pdf`;
  const attach = finalBytes.length <= MAX_ATTACH_BYTES;
  const byEmail = new Map();
  for (const r of recs) if (!byEmail.has(r.email.toLowerCase())) byEmail.set(r.email.toLowerCase(), r);
  if (process.env.MAIL_FROM && !byEmail.has(process.env.MAIL_FROM.toLowerCase())) byEmail.set(process.env.MAIL_FROM.toLowerCase(), { is_me: true });
  await Promise.allSettled(
    [...byEmail].map(([to, r]) => {
      const downloadUrl = attach ? undefined : r.is_me ? `${appUrl()}/envelopes/${env.id}` : r.kind === "cc" ? undefined : `${appUrl()}/s/${signTokenFor(r.id)}`;
      return sendEmail({
        to,
        subject: `Completed: ${env.title}`,
        html: emailLayout({
          heading: "All parties have signed",
          intro: `"${env.title}" is fully executed. ${attach ? "The signed copy with its certificate of completion is attached." : "The signed copy is too large to attach."}`,
          buttonText: downloadUrl ? "Download signed document" : undefined,
          buttonUrl: downloadUrl,
          note: attach ? `Document fingerprint (SHA-256): ${final_sha256}` : downloadUrl ? undefined : "The file was too large to attach. Reply to this email to request a copy.",
        }),
        attachments: attach ? [{ name, bytes: finalBytes }] : [],
      });
    })
  );
  return [];
}

/** If a contract created from an intake is voided, declined or deleted, let that intake be contracted again. */
export async function releaseIntake(env) {
  if (!env?.intake_id) return;
  const intake = await db.get("intakes", env.intake_id);
  if (intake && intake.envelope_id === env.id) {
    await db.update("intakes", intake.id, { envelope_id: null, status: intake.answers ? "submitted" : "sent" });
  }
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
  for (const r of recs.filter((x) => x.kind !== "cc")) {
    line(`${r.routing_order}. ${r.name} <${r.email}>`, { f: bold });
    line(`Sent: ${fmt(r.sent_at)}   Viewed: ${fmt(r.viewed_at)}`, { indent: 12 });
    line(`Consented to electronic signature: ${fmt(r.consent_at)}`, { indent: 12 });
    line(`Signed: ${fmt(r.signed_at)}`, { indent: 12 });
    line(`IP address: ${r.ip || "—"}`, { indent: 12 });
    line(`Device: ${(r.user_agent || "—").slice(0, 100)}`, { indent: 12, size: 8, color: grey });
    y -= 4;
  }
  const ccs = recs.filter((x) => x.kind === "cc");
  if (ccs.length) {
    y -= 6;
    line("Carbon copies (received the completed document)", { f: bold, size: 12 });
    for (const r of ccs) line(`${r.name} <${r.email}>`);
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
