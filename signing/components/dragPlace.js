"use client";
// Drag an item from a palette and drop it on a PDF page (works with mouse and touch).
// A plain click (no movement) is reported as onClick so "click item, then click page" also works.

/**
 * @param {PointerEvent} e  pointerdown event from the palette item
 * @param {{label: string, onDrop: (page:number, fx:number, fy:number) => void, onClick?: () => void}} opts
 */
export function startPaletteDrag(e, { label, onDrop, onClick }) {
  if (e.button !== undefined && e.button !== 0) return;
  e.preventDefault();
  const sx = e.clientX;
  const sy = e.clientY;
  let ghost = null;
  let hoverPage = null;

  const pageAt = (x, y) => document.elementsFromPoint(x, y).find((el) => el.classList?.contains("pdf-page"));
  const setHover = (el) => {
    if (hoverPage === el) return;
    hoverPage?.classList.remove("drop-hover");
    hoverPage = el;
    hoverPage?.classList.add("drop-hover");
  };

  const move = (ev) => {
    if (!ghost && Math.hypot(ev.clientX - sx, ev.clientY - sy) < 5) return;
    if (!ghost) {
      ghost = document.createElement("div");
      ghost.className = "drag-ghost";
      ghost.textContent = label;
      document.body.appendChild(ghost);
    }
    ghost.style.left = `${ev.clientX}px`;
    ghost.style.top = `${ev.clientY}px`;
    setHover(pageAt(ev.clientX, ev.clientY) || null);
  };
  const up = (ev) => {
    window.removeEventListener("pointermove", move);
    window.removeEventListener("pointerup", up);
    window.removeEventListener("pointercancel", up);
    setHover(null);
    if (!ghost) return onClick?.();
    ghost.remove();
    const page = pageAt(ev.clientX, ev.clientY);
    if (!page) return;
    const r = page.getBoundingClientRect();
    onDrop(Number(page.dataset.page), (ev.clientX - r.left) / r.width, (ev.clientY - r.top) / r.height);
  };
  window.addEventListener("pointermove", move);
  window.addEventListener("pointerup", up);
  window.addEventListener("pointercancel", up);
}
