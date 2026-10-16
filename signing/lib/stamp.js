// Draws field values (signatures, text, dates, checkmarks) onto a PDF with pdf-lib.
// Field boxes are stored as fractions (0–1) of the page as displayed, so they
// survive any zoom level; this handles rotated pages too. Works in browser and server.
import { PDFDocument, StandardFonts, rgb, degrees, PDFTextField, PDFCheckBox, PDFDropdown, PDFOptionList, PDFRadioGroup, PDFRef, PDFName } from "pdf-lib";

const INK = rgb(0.07, 0.1, 0.25);

/** Convert a point given as fractions of the displayed (rotated) page to PDF user space. */
export function viewToPdf(page, fx, fy) {
  const { x: x0, y: y0, width: W, height: H } = page.getMediaBox();
  const r = ((page.getRotation().angle % 360) + 360) % 360;
  const viewW = r % 180 === 0 ? W : H;
  const viewH = r % 180 === 0 ? H : W;
  const vx = fx * viewW;
  const vy = fy * viewH;
  let x, y;
  if (r === 90) [x, y] = [vy, vx];
  else if (r === 180) [x, y] = [W - vx, vy];
  else if (r === 270) [x, y] = [W - vy, H - vx];
  else [x, y] = [vx, H - vy];
  return { x: x + x0, y: y + y0, rotate: degrees(r), viewW, viewH };
}

// pdf-lib's flatten() deletes widget objects but can leave references to them in
// each page's /Annots, which some readers report as a damaged file. Remove those.
function dropDeadAnnots(doc) {
  for (const page of doc.getPages()) {
    const annots = page.node.Annots();
    if (!annots) continue;
    const live = annots.asArray().filter((ref) => !(ref instanceof PDFRef) || doc.context.lookup(ref));
    if (!live.length) page.node.delete(PDFName.of("Annots"));
    else if (live.length !== annots.size()) page.node.set(PDFName.of("Annots"), doc.context.obj(live));
  }
}

function safeText(font, text) {
  const s = String(text ?? "");
  try {
    font.encodeText(s);
    return s;
  } catch {
    return Array.from(s)
      .map((ch) => {
        try {
          font.encodeText(ch);
          return ch;
        } catch {
          return "?";
        }
      })
      .join("");
  }
}

function dataUrlBytes(dataUrl) {
  const b64 = dataUrl.split(",")[1] || "";
  if (typeof Buffer !== "undefined") return new Uint8Array(Buffer.from(b64, "base64"));
  const bin = atob(b64);
  return Uint8Array.from(bin, (c) => c.charCodeAt(0));
}

/**
 * @param {Uint8Array} pdfBytes
 * @param {Array} fields  each {page, x, y, w, h, type, value}
 * @param {{flattenForm?: boolean, fillForm?: Record<string,string|boolean>}} opts
 */
export async function stampPdf(pdfBytes, fields, opts = {}) {
  const doc = await PDFDocument.load(pdfBytes, { ignoreEncryption: true });
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const pages = doc.getPages();

  if (opts.fillForm) {
    const form = doc.getForm();
    for (const [name, val] of Object.entries(opts.fillForm)) {
      try {
        const f = form.getField(name);
        if (f instanceof PDFTextField) f.setText(safeText(font, val));
        else if (f instanceof PDFCheckBox) val ? f.check() : f.uncheck();
        else if (f instanceof PDFDropdown || f instanceof PDFOptionList || f instanceof PDFRadioGroup) f.select(String(val));
      } catch (e) {
        console.warn("form fill skipped", name, e.message);
      }
    }
  }
  if (opts.flattenForm) {
    try {
      doc.getForm().flatten();
      dropDeadAnnots(doc);
    } catch (e) {
      console.warn("form flatten failed", e.message);
    }
  }

  for (const f of fields) {
    const page = pages[f.page];
    if (!page || f.value === undefined || f.value === null || f.value === "" || f.value === false) continue;
    const { viewW, viewH } = viewToPdf(page, 0, 0);
    const boxW = f.w * viewW;
    const boxH = f.h * viewH;

    if (f.type === "signature" || f.type === "initials") {
      if (typeof f.value !== "string" || !f.value.startsWith("data:image")) continue;
      const bytes = dataUrlBytes(f.value);
      const img = f.value.startsWith("data:image/png") ? await doc.embedPng(bytes) : await doc.embedJpg(bytes);
      const scale = Math.min(boxW / img.width, boxH / img.height);
      const w = img.width * scale;
      const h = img.height * scale;
      // bottom-left of the image as displayed, left-aligned & vertically centered in the box
      const offY = (boxH - h) / 2;
      const p = viewToPdf(page, f.x, f.y + (boxH - offY) / viewH);
      page.drawImage(img, { x: p.x, y: p.y, width: w, height: h, rotate: p.rotate });
    } else if (f.type === "checkbox") {
      const size = Math.min(boxW, boxH) * 0.95;
      const p = viewToPdf(page, f.x + (boxW - size * 0.62) / 2 / viewW, f.y + (boxH + size * 0.7) / 2 / viewH);
      page.drawText("X", { x: p.x, y: p.y, size, font, color: INK, rotate: p.rotate });
    } else {
      const text = safeText(font, f.value);
      let size = Math.min(boxH * 0.72, 12);
      const pad = 2;
      while (size > 5 && font.widthOfTextAtSize(text, size) > boxW - pad * 2) size -= 0.5;
      const baseline = (boxH + size * 0.68) / 2; // vertically center cap height
      const p = viewToPdf(page, f.x + pad / viewW, f.y + baseline / viewH);
      page.drawText(text, { x: p.x, y: p.y, size, font, color: INK, rotate: p.rotate });
    }
  }
  return new Uint8Array(await doc.save());
}

/** Detect AcroForm fields in a PDF (for quick-sign auto-fill). */
export async function listFormFields(pdfBytes) {
  const doc = await PDFDocument.load(pdfBytes, { ignoreEncryption: true });
  return doc
    .getForm()
    .getFields()
    .map((f) => ({ name: f.getName(), kind: fieldKind(f) }))
    .filter((f) => f.kind);
}

function fieldKind(f) {
  if (f instanceof PDFTextField) return "text";
  if (f instanceof PDFCheckBox) return "checkbox";
  if (f instanceof PDFDropdown || f instanceof PDFOptionList || f instanceof PDFRadioGroup) return "choice";
  return null;
}
