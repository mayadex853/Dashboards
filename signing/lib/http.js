import "server-only";
import { NextResponse } from "next/server";

/**
 * Wrap a route handler so thrown errors become JSON responses.
 * Pass { expose: false } on public (signer-facing) routes: unexpected errors then show a generic
 * message instead of internal details. Errors created with httpError() are always shown.
 */
export function route(fn, { expose = true } = {}) {
  return async (req, ctx) => {
    try {
      const params = ctx?.params ? await ctx.params : {};
      const res = await fn(req, params);
      return res instanceof Response ? res : NextResponse.json(res ?? { ok: true });
    } catch (e) {
      console.error(e);
      const deliberate = !!e.status;
      return NextResponse.json(
        { error: deliberate || expose ? e.message || "Something went wrong" : "Something went wrong. Please try again." },
        { status: e.status || 500 }
      );
    }
  };
}

/** Content-Disposition that survives any file name (accents, en dashes, curly quotes, emoji). */
export function contentDisposition(name, download) {
  const clean = String(name || "document.pdf").replace(/[\r\n"\\]/g, "").trim() || "document.pdf";
  const ascii = clean.replace(/[^\x20-\x7e]/g, "_");
  const encoded = encodeURIComponent(clean).replace(/['()*]/g, (c) => "%" + c.charCodeAt(0).toString(16).toUpperCase());
  return `${download ? "attachment" : "inline"}; filename="${ascii}"; filename*=UTF-8''${encoded}`;
}

export const pdfResponse = (bytes, filename = "document.pdf", download = false) =>
  new Response(Buffer.from(bytes), {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": contentDisposition(filename, download),
      "Cache-Control": "private, no-store",
    },
  });

export function httpError(message, status = 400) {
  const e = new Error(message);
  e.status = status;
  return e;
}

/** Reject uploads that aren't PDFs (checks the file's first bytes, not just its name). */
export function assertPdf(bytes) {
  const head = Buffer.from(bytes.slice(0, 1024)).toString("latin1");
  if (!head.includes("%PDF-")) throw httpError("That file doesn't look like a PDF. Please upload a .pdf file.");
}
