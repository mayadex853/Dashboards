import * as db from "@/lib/db";
import { route, pdfResponse, httpError } from "@/lib/http";

export const GET = route(async (req, { id }) => {
  const env = await db.get("envelopes", id);
  if (!env) throw httpError("Not found", 404);
  const which = new URL(req.url).searchParams.get("which") || "latest";
  const path = which === "original" ? env.original_pdf_path : env.final_pdf_path || env.current_pdf_path;
  const download = new URL(req.url).searchParams.has("download");
  return pdfResponse(await db.getFile(path), `${env.title}${env.final_pdf_path ? " - signed" : ""}.pdf`, download);
});
