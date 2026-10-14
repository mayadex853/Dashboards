"use client";
// Renders every page of a PDF to canvas and lets callers overlay fields on each page.
import { useEffect, useRef, useState } from "react";

let pdfjsPromise;
function loadPdfjs() {
  if (!pdfjsPromise) {
    pdfjsPromise = import("pdfjs-dist").then((pdfjs) => {
      pdfjs.GlobalWorkerOptions.workerSrc = "/pdf.worker.min.mjs";
      return pdfjs;
    });
  }
  return pdfjsPromise;
}

/**
 * @param {{src: string|Uint8Array, overlay?: (pageIndex:number, size:{width:number,height:number}) => React.ReactNode, onPageClick?: (pageIndex:number, fx:number, fy:number) => void, onLoaded?: (numPages:number) => void}} props
 */
export default function PdfPages({ src, overlay, onPageClick, onLoaded }) {
  const wrapRef = useRef(null);
  const [pages, setPages] = useState([]); // [{width, height}] in CSS px
  const [error, setError] = useState(null);
  const canvases = useRef([]);
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setWidth(Math.min(el.clientWidth, 1000)));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    if (!src || !width) return;
    let cancelled = false;
    let doc;
    (async () => {
      try {
        const pdfjs = await loadPdfjs();
        const data = typeof src === "string" ? { url: src, withCredentials: true } : { data: src.slice() };
        doc = await pdfjs.getDocument(data).promise;
        if (cancelled) return;
        const sizes = [];
        const pdfPages = [];
        for (let i = 1; i <= doc.numPages; i++) {
          const p = await doc.getPage(i);
          const vp = p.getViewport({ scale: 1 });
          const scale = width / vp.width;
          sizes.push({ width, height: vp.height * scale, scale });
          pdfPages.push(p);
        }
        if (cancelled) return;
        setPages(sizes);
        onLoaded?.(doc.numPages);
        // wait for canvases to mount
        await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        for (let i = 0; i < pdfPages.length; i++) {
          if (cancelled) return;
          const canvas = canvases.current[i];
          if (!canvas) continue;
          const vp = pdfPages[i].getViewport({ scale: sizes[i].scale * dpr });
          canvas.width = vp.width;
          canvas.height = vp.height;
          await pdfPages[i].render({ canvasContext: canvas.getContext("2d"), viewport: vp, annotationMode: 1 }).promise;
        }
      } catch (e) {
        if (!cancelled) setError(e.message || String(e));
      }
    })();
    return () => {
      cancelled = true;
      doc?.destroy?.();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [src, width]);

  return (
    <div ref={wrapRef} className="pdf-wrap">
      {error && <div className="error">Couldn't open PDF: {error}</div>}
      {!error && !pages.length && <div className="muted pad">Loading document…</div>}
      {pages.map((size, i) => (
        <div
          key={i}
          className="pdf-page"
          style={{ width: size.width, height: size.height }}
          onClick={(e) => {
            if (!onPageClick || e.target !== e.currentTarget.querySelector(".pdf-hit")) return;
            const rect = e.currentTarget.getBoundingClientRect();
            onPageClick(i, (e.clientX - rect.left) / rect.width, (e.clientY - rect.top) / rect.height);
          }}
        >
          <canvas ref={(el) => (canvases.current[i] = el)} style={{ width: size.width, height: size.height }} />
          <div className="pdf-hit" />
          {overlay?.(i, size)}
          <div className="page-num">
            {i + 1} / {pages.length}
          </div>
        </div>
      ))}
    </div>
  );
}
