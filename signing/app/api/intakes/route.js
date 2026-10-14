import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";
import { newToken, hashToken, appUrl } from "@/lib/envelopes";
import { sendEmail, emailLayout } from "@/lib/email";
import { CATEGORIES } from "@/lib/fields";

export const GET = route(async () => (await db.list("intakes")).map(({ token_hash, ...i }) => i));

export const POST = route(async (req) => {
  const b = await req.json();
  if (!/^\S+@\S+\.\S+$/.test(b.signee_email || "")) throw httpError("Enter the signee's email");
  if (!CATEGORIES.some((c) => c.key === b.category)) throw httpError("Pick a signing type");
  const token = newToken();
  const intake = await db.insert("intakes", {
    token_hash: hashToken(token),
    category: b.category,
    template_id: b.template_id || null,
    signee_name: b.signee_name || "",
    signee_email: b.signee_email,
    deal: b.deal || {},
    message: b.message || null,
    auto_send: !!b.auto_send && !!b.template_id,
    status: "sent",
  });
  const link = `${appUrl()}/i/${token}`;
  const sender = process.env.MAIL_FROM_NAME || "HD Music";
  const mail = b.email === false ? { sent: false } : await sendEmail({
    to: b.signee_email,
    subject: `${sender}: a few details before we send your agreement`,
    html: emailLayout({
      heading: `Welcome${b.signee_name ? `, ${b.signee_name.split(" ")[0]}` : ""}!`,
      intro: b.message || "We're excited to work with you. Please fill out this short form so we can prepare your agreement. It takes about 3 minutes.",
      buttonText: "Fill out the form",
      buttonUrl: link,
    }),
  });
  return { intake: { ...intake, token_hash: undefined }, link, emailed: mail.sent };
});
