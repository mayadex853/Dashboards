import "server-only";
import * as db from "@/lib/db";
import { createEnvelope, sendEnvelope, getProfile } from "@/lib/envelopes";

/** Default signer list for a template: signee signs first, you countersign. */
export async function defaultRecipients(template, intake) {
  const profile = await getProfile();
  const me = profile.data || {};
  return (template.roles || []).map((role, i) => {
    if (role.kind === "me")
      return { role_index: i, name: me.full_name || process.env.MAIL_FROM_NAME || "Me", email: me.email || process.env.MAIL_FROM || "", routing_order: i + 1, is_me: true };
    if (role.kind === "signee" && intake)
      return { role_index: i, name: intake.answers?.legal_name || intake.signee_name, email: intake.answers?.email || intake.signee_email, routing_order: i + 1 };
    return { role_index: i, name: "", email: "", routing_order: i + 1 };
  });
}

export async function contractFromIntake(intake, { recipients, values, send = true, message } = {}) {
  if (!intake.template_id) throw new Error("This intake has no contract template attached");
  const template = await db.get("templates", intake.template_id);
  if (!template) throw new Error("Template not found");
  const recs = recipients || (await defaultRecipients(template, intake));
  const missing = recs.find((r) => !r.name || !r.email);
  if (missing) throw new Error("Every signer needs a name and email");
  const env = await createEnvelope({
    title: `${template.name} - ${intake.answers?.professional_name || intake.answers?.legal_name || intake.signee_name}`,
    templateId: template.id,
    intakeId: intake.id,
    source: "intake",
    recipients: recs,
    values,
    message: message || intake.message,
  });
  await db.update("intakes", intake.id, { envelope_id: env.id });
  const links = send ? await sendEnvelope(env.id) : [];
  return { envelope: env, links };
}
