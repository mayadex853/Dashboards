import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";
import { hashToken, appUrl } from "@/lib/envelopes";
import { intakeQuestions, CATEGORIES } from "@/lib/fields";
import { contractFromIntake } from "@/lib/intake";
import { sendEmail, emailLayout } from "@/lib/email";

async function load(token) {
  const intake = await db.findOne("intakes", { token_hash: hashToken(token) });
  if (!intake) throw httpError("This link is invalid.", 404);
  return intake;
}

export const GET = route(async (_req, { token }) => {
  const i = await load(token);
  return {
    submitted: i.status !== "sent",
    category: CATEGORIES.find((c) => c.key === i.category)?.label,
    questions: intakeQuestions(i.category),
    prefill: { legal_name: i.signee_name, email: i.signee_email, ...(i.answers || {}) },
    sender: process.env.MAIL_FROM_NAME || "HD Music",
  };
});

export const POST = route(async (req, { token }) => {
  const intake = await load(token);
  if (intake.status !== "sent") throw httpError("This form was already submitted. Contact us to make changes.");
  const { answers = {} } = await req.json();
  const qs = intakeQuestions(intake.category).filter((q) => q.key);
  const clean = {};
  for (const q of qs) if (answers[q.key] !== undefined) clean[q.key] = String(answers[q.key]).slice(0, 2000).trim();
  const missing = qs.filter((q) => q.required && !clean[q.key]);
  if (missing.length) throw httpError(`Please fill in: ${missing.map((q) => q.label).join(", ")}`);

  const updated = await db.update("intakes", intake.id, { answers: clean, status: "submitted", submitted_at: new Date().toISOString() });
  let autoSent = false;
  if (intake.auto_send && intake.template_id) {
    try {
      await contractFromIntake(updated);
      autoSent = true;
    } catch (e) {
      console.error("auto-send failed", e);
    }
  }
  if (process.env.MAIL_FROM)
    await sendEmail({
      to: process.env.MAIL_FROM,
      subject: `Intake received: ${clean.professional_name || clean.legal_name}`,
      html: emailLayout({
        heading: `${clean.legal_name} submitted their intake form`,
        intro: autoSent ? "Their contract was generated and sent for signature automatically." : "Review their details and send the contract.",
        buttonText: "Open intake",
        buttonUrl: `${appUrl()}/intake/${intake.id}`,
      }),
    });
  return { ok: true, autoSent };
});
