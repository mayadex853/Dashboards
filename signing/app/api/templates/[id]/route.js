import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";

export const GET = route(async (_req, { id }) => {
  const t = await db.get("templates", id);
  if (!t) throw httpError("Not found", 404);
  return t;
});

export const PUT = route(async (req, { id }) => {
  const { name, category, description, roles, fields } = await req.json();
  return db.update("templates", id, { name, category, description, roles, fields, updated_at: new Date().toISOString() });
});

export const DELETE = route(async (_req, { id }) => {
  await db.remove("templates", id);
});
