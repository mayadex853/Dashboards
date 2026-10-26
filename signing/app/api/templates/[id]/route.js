import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";

export const GET = route(async (_req, { id }) => {
  const t = await db.get("templates", id);
  if (!t) throw httpError("Not found", 404);
  return t;
});

export const PUT = route(async (req, { id }) => {
  const { name, category, description, roles, fields } = await req.json();
  if (!Array.isArray(fields) || !Array.isArray(roles)) throw httpError("Invalid template data");
  if (!String(name || "").trim()) throw httpError("A template needs a name");
  const row = await db.update("templates", id, { name, category, description, roles, fields, updated_at: new Date().toISOString() });
  if (!row) throw httpError("Template not found", 404);
  return row;
});

export const DELETE = route(async (_req, { id }) => {
  await db.remove("templates", id);
});
