import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";
import { defaultRecipients } from "@/lib/intake";

export const GET = route(async (_req, { id }) => {
  const intake = await db.get("intakes", id);
  if (!intake) throw httpError("Not found", 404);
  delete intake.token_hash;
  const template = intake.template_id ? await db.get("templates", intake.template_id) : null;
  return { intake, template, recipients: template ? await defaultRecipients(template, intake) : [] };
});

export const PUT = route(async (req, { id }) => {
  const { deal, template_id, answers } = await req.json();
  const patch = {};
  if (deal !== undefined) patch.deal = deal;
  if (template_id !== undefined) patch.template_id = template_id || null;
  if (answers !== undefined) patch.answers = answers;
  return db.update("intakes", id, patch);
});

export const DELETE = route(async (_req, { id }) => {
  await db.remove("intakes", id);
});
