import * as db from "@/lib/db";
import { route, pdfResponse, httpError } from "@/lib/http";

export const GET = route(async (_req, { id }) => {
  const t = await db.get("templates", id);
  if (!t) throw httpError("Not found", 404);
  return pdfResponse(await db.getFile(t.pdf_path), `${t.name}.pdf`);
});
