import { route, httpError } from "@/lib/http";
import { sendEmail, emailLayout } from "@/lib/email";

// Sends a test message from MAIL_FROM to itself (admin only — protected by middleware).
export const POST = route(async () => {
  const to = process.env.MAIL_FROM;
  if (!to) throw httpError("MAIL_FROM is not set");
  const r = await sendEmail({
    to,
    subject: "TakaSign test email",
    html: emailLayout({ heading: "Email is working", intro: "TakaSign can send signing requests and completed documents from this mailbox." }),
  });
  if (!r.sent) throw httpError(r.reason || "Email was not sent");
  return { ok: true, to };
});
