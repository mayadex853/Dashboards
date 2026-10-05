// Sends email from your Microsoft 365 mailbox via Microsoft Graph (client credentials).
import "server-only";

const configured = () => !!(process.env.MS_TENANT_ID && process.env.MS_CLIENT_ID && process.env.MS_CLIENT_SECRET && process.env.MAIL_FROM);
export const emailConfigured = configured;

let cached = { token: null, exp: 0 };
async function graphToken() {
  if (cached.token && cached.exp > Date.now() + 60_000) return cached.token;
  const res = await fetch(`https://login.microsoftonline.com/${process.env.MS_TENANT_ID}/oauth2/v2.0/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: process.env.MS_CLIENT_ID,
      client_secret: process.env.MS_CLIENT_SECRET,
      scope: "https://graph.microsoft.com/.default",
      grant_type: "client_credentials",
    }),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(`Microsoft auth failed: ${json.error_description || json.error}`);
  cached = { token: json.access_token, exp: Date.now() + json.expires_in * 1000 };
  return cached.token;
}

const MAX_ATTACH_BYTES = 2.8 * 1024 * 1024; // Graph sendMail limit is ~3MB per request

/**
 * @param {{to: string|string[], subject: string, html: string, attachments?: {name: string, bytes: Uint8Array}[]}} msg
 * @returns {Promise<{sent: boolean, reason?: string}>}
 */
export async function sendEmail({ to, subject, html, attachments = [] }) {
  const recipients = (Array.isArray(to) ? to : [to]).filter(Boolean);
  if (!configured()) {
    console.log(`[email skipped: Microsoft 365 not configured] to=${recipients.join(",")} subject="${subject}"`);
    return { sent: false, reason: "Email not configured" };
  }
  const fit = attachments.filter((a) => a.bytes.length <= MAX_ATTACH_BYTES);
  const body = {
    message: {
      subject,
      body: { contentType: "HTML", content: html },
      from: { emailAddress: { address: process.env.MAIL_FROM, name: process.env.MAIL_FROM_NAME || undefined } },
      toRecipients: recipients.map((address) => ({ emailAddress: { address } })),
      attachments: fit.map((a) => ({
        "@odata.type": "#microsoft.graph.fileAttachment",
        name: a.name,
        contentType: "application/pdf",
        contentBytes: Buffer.from(a.bytes).toString("base64"),
      })),
    },
    saveToSentItems: true,
  };
  const res = await fetch(`https://graph.microsoft.com/v1.0/users/${encodeURIComponent(process.env.MAIL_FROM)}/sendMail`, {
    method: "POST",
    headers: { Authorization: `Bearer ${await graphToken()}`, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    console.error("Graph sendMail failed", res.status, text);
    return { sent: false, reason: `Microsoft Graph error ${res.status}` };
  }
  return { sent: true };
}

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

/** Simple branded email layout with a button. */
export function emailLayout({ heading, intro, buttonText, buttonUrl, note }) {
  const from = esc(process.env.MAIL_FROM_NAME || "HD Music");
  return `<!doctype html><html><body style="margin:0;background:#f4f4f2;font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#1a1a19">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:32px 12px"><tr><td align="center">
  <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;background:#fff;border-radius:12px;padding:32px">
    <tr><td style="font-size:12px;letter-spacing:.6px;text-transform:uppercase;color:#898781">${from}</td></tr>
    <tr><td style="font-size:20px;font-weight:600;padding:12px 0 8px">${esc(heading)}</td></tr>
    <tr><td style="font-size:15px;line-height:1.55;color:#383835;white-space:pre-line">${esc(intro)}</td></tr>
    ${buttonUrl ? `<tr><td style="padding:24px 0"><a href="${esc(buttonUrl)}" style="background:#3987e5;color:#fff;text-decoration:none;padding:12px 22px;border-radius:8px;font-weight:600;display:inline-block">${esc(buttonText)}</a></td></tr>` : ""}
    ${note ? `<tr><td style="font-size:12px;color:#898781;line-height:1.5">${esc(note)}</td></tr>` : ""}
  </table></td></tr></table></body></html>`;
}
