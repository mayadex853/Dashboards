import * as db from "@/lib/db";
import { route, pdfResponse, httpError } from "@/lib/http";
import { recipientByToken } from "@/lib/envelopes";

export const GET = route(async (_req, { token }) => {
  const found = await recipientByToken(token);
  if (!found || ["voided", "declined"].includes(found.env.status)) throw httpError("Invalid link", 404);
  return pdfResponse(await db.getFile(found.env.current_pdf_path), `${found.env.title}.pdf`);
});
