import crypto from "node:crypto";
import * as db from "@/lib/db";
import { route, httpError, assertPdf } from "@/lib/http";

export const GET = route(async () => db.list("templates", {}, { order: "name", asc: true }));

export const POST = route(async (req) => {
  const form = await req.formData();
  const file = form.get("file");
  if (!file || typeof file === "string") throw httpError("Choose a PDF");
  const bytes = new Uint8Array(await file.arrayBuffer());
  assertPdf(bytes);
  const id = crypto.randomUUID();
  const pdf_path = `templates/${id}.pdf`;
  await db.putFile(pdf_path, bytes);
  return db.insert("templates", {
    id,
    name: form.get("name") || file.name.replace(/\.pdf$/i, ""),
    category: form.get("category") || null,
    description: form.get("description") || null,
    pdf_path,
    roles: [
      { name: "Signee", kind: "signee" },
      { name: "Me", kind: "me" },
    ],
    fields: [],
  });
});
