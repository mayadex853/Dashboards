import * as db from "@/lib/db";
import { route, pdfResponse, httpError } from "@/lib/http";

export const GET = route(async (_req, { id }) => {
  const q = await db.get("quick_signs", id);
  if (!q) throw httpError("Not found", 404);
  return pdfResponse(await db.getFile(q.pdf_path), `${q.title}.pdf`, true);
});
