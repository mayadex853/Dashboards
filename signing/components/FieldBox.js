"use client";
// A positioned field box on a PDF page. In edit mode it can be dragged and resized.
import { useRef } from "react";

export const ROLE_COLORS = ["#d99a00", "#2f80ed", "#1e9e5a", "#9b51e0", "#e0504a", "#0e9f9e"];

export default function FieldBox({ field, size, editable, selected, onChange, onSelect, children, color, className = "" }) {
  const drag = useRef(null);

  const start = (e, mode) => {
    if (!editable) return;
    e.stopPropagation();
    e.preventDefault();
    onSelect?.();
    drag.current = { mode, x: e.clientX, y: e.clientY, f: { ...field } };
    const move = (ev) => {
      const d = drag.current;
      if (!d) return;
      const dx = (ev.clientX - d.x) / size.width;
      const dy = (ev.clientY - d.y) / size.height;
      if (d.mode === "move") {
        onChange({ x: clamp(d.f.x + dx, 0, 1 - d.f.w), y: clamp(d.f.y + dy, 0, 1 - d.f.h) });
      } else {
        onChange({ w: clamp(d.f.w + dx, 0.015, 1 - d.f.x), h: clamp(d.f.h + dy, 0.012, 1 - d.f.y) });
      }
    };
    const up = () => {
      drag.current = null;
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  };

  const c = color || ROLE_COLORS[Number(field.role) % ROLE_COLORS.length];
  return (
    <div
      data-fid={field.id}
      className={`field-box ${selected ? "selected" : ""} ${editable ? "editable" : ""} ${className}`}
      style={{
        left: field.x * size.width,
        top: field.y * size.height,
        width: field.w * size.width,
        height: field.h * size.height,
        "--fc": c,
      }}
      onPointerDown={(e) => start(e, "move")}
      onClick={(e) => {
        e.stopPropagation();
        onSelect?.();
      }}
    >
      {children}
      {editable && <span className="resize" onPointerDown={(e) => start(e, "resize")} />}
    </div>
  );
}

const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
