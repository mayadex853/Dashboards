import "server-only";
import { NextResponse } from "next/server";

/** Wrap a route handler so thrown errors become JSON responses. */
export function route(fn) {
  return async (req, ctx) => {
    try {
      const params = ctx?.params ? await ctx.params : {};
      const res = await fn(req, params);
      return res instanceof Response ? res : NextResponse.json(res ?? { ok: true });
    } catch (e) {
      console.error(e);
      return NextResponse.json({ error: e.message || "Something went wrong" }, { status: e.status || 400 });
    }
  };
}

export const pdfResponse = (bytes, filename = "document.pdf", download = false) =>
  new Response(Buffer.from(bytes), {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `${download ? "attachment" : "inline"}; filename="${filename.replace(/"/g, "")}"`,
      "Cache-Control": "private, no-store",
    },
  });

export function httpError(message, status = 400) {
  const e = new Error(message);
  e.status = status;
  return e;
}
