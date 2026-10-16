"use client";
// Full-screen workspace with its own top bar, like DocuSign's "Add Fields" view.
import { useEffect } from "react";

export default function FullScreen({ title, subtitle, onBack, backLabel = "Back", actions, children }) {
  useEffect(() => {
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => (document.body.style.overflow = prev);
  }, []);
  return (
    <div className="fs-editor">
      <div className="fs-top">
        {onBack && <button className="btn ghost sm" onClick={onBack}>← {backLabel}</button>}
        <div style={{ minWidth: 0, flex: 1 }}>
          <div className="title">{title}</div>
          {subtitle && <div className="muted small">{subtitle}</div>}
        </div>
        <div className="row">{actions}</div>
      </div>
      <div className="fs-body">{children}</div>
    </div>
  );
}
