"use client";
// Place and configure signing fields on a PDF (used for templates and one-off sends).
import { useEffect, useState } from "react";
import PdfPages from "@/components/PdfPages";
import FieldBox, { ROLE_COLORS } from "@/components/FieldBox";
import { FIELD_TYPES, PROFILE_FIELDS, ALL_INTAKE_KEYS } from "@/lib/fields";

const KEY_SUGGESTIONS = [
  { key: "today", label: "Today's date" },
  ...ALL_INTAKE_KEYS.map((k) => ({ key: `intake.${k.key}`, label: `Signee: ${k.label}` })),
  { key: "intake.full_address", label: "Signee: full address (one line)" },
  ...PROFILE_FIELDS.map((f) => ({ key: `profile.${f.key}`, label: `Me: ${f.label}` })),
  { key: "profile.full_address", label: "Me: full address (one line)" },
  { key: "deal.advance", label: "Deal: advance" },
  { key: "deal.royalty", label: "Deal: royalty %" },
  { key: "deal.term", label: "Deal: term" },
  { key: "deal.territory", label: "Deal: territory" },
  { key: "deal.effective_date", label: "Deal: effective date" },
];

export default function FieldEditor({ src, fields, setFields, roles, showKeys = true }) {
  const [tool, setTool] = useState(null);
  const [role, setRole] = useState(0);
  const [sel, setSel] = useState(null);
  const selected = fields.find((f) => f.id === sel);

  useEffect(() => {
    const onKey = (e) => {
      if (!sel || ["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement?.tagName)) return;
      if (e.key === "Delete" || e.key === "Backspace") {
        setFields((fs) => fs.filter((f) => f.id !== sel));
        setSel(null);
      }
      if (e.key === "Escape") setSel(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [sel, setFields]);

  const place = (page, fx, fy) => {
    if (!tool) return setSel(null);
    const t = FIELD_TYPES.find((x) => x.type === tool);
    const f = {
      id: Math.random().toString(36).slice(2, 10),
      type: tool,
      page,
      x: Math.min(fx, 1 - t.w),
      y: Math.min(Math.max(fy - t.h / 2, 0), 1 - t.h),
      w: t.w,
      h: t.h,
      role,
      label: t.label,
      required: tool !== "checkbox",
    };
    setFields((fs) => [...fs, f]);
    setSel(f.id);
  };
  const patch = (id, p) => setFields((fs) => fs.map((f) => (f.id === id ? { ...f, ...p } : f)));

  return (
    <div className="editor">
      <div className="side stack">
        <div className="card">
          <h3>1. Who fills it in?</h3>
          <div className="chips">
            {roles.map((r, i) => (
              <button key={i} className={`chip ${role === i ? "on" : ""}`} style={role === i ? { background: ROLE_COLORS[i], borderColor: ROLE_COLORS[i] } : { color: ROLE_COLORS[i] }} onClick={() => setRole(i)}>
                {r.name || `Signer ${i + 1}`}
              </button>
            ))}
          </div>
          <h3 style={{ marginTop: 16 }}>2. Pick a field, click the page</h3>
          <div className="palette">
            {FIELD_TYPES.map((t) => (
              <button key={t.type} className={`chip ${tool === t.type ? "on" : ""}`} onClick={() => setTool(tool === t.type ? null : t.type)}>
                {t.label}
              </button>
            ))}
          </div>
          {tool && <div className="hint" style={{ marginTop: 10 }}>Click on the document to drop a {tool} field. Click again to add more.</div>}
        </div>

        {selected && (
          <div className="card">
            <h3>Selected field</h3>
            <div className="field">
              <label>Assigned to</label>
              <select value={selected.role} onChange={(e) => patch(selected.id, { role: Number(e.target.value) })}>
                {roles.map((r, i) => <option key={i} value={i}>{r.name || `Signer ${i + 1}`}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Label</label>
              <input value={selected.label || ""} onChange={(e) => patch(selected.id, { label: e.target.value })} />
            </div>
            {selected.type === "text" && showKeys && (
              <div className="field">
                <label>Auto-fill from</label>
                <input list="key-suggestions" placeholder="e.g. intake.legal_name" value={selected.key || ""} onChange={(e) => patch(selected.id, { key: e.target.value.trim() || undefined })} />
                <datalist id="key-suggestions">
                  {KEY_SUGGESTIONS.map((k) => <option key={k.key} value={k.key}>{k.label}</option>)}
                </datalist>
                <div className="help">Signee answers (intake.*), your info (profile.*), or deal terms you enter when sending (deal.anything).</div>
              </div>
            )}
            {selected.type === "text" && (
              <div className="field">
                <label>Default text</label>
                <input value={selected.defaultValue || ""} onChange={(e) => patch(selected.id, { defaultValue: e.target.value || undefined })} />
              </div>
            )}
            <label className="row" style={{ gap: 6 }}>
              <input type="checkbox" checked={selected.required !== false} onChange={(e) => patch(selected.id, { required: e.target.checked })} /> Required
            </label>
            <div className="row end">
              <button className="btn sm danger" onClick={() => { setFields((fs) => fs.filter((f) => f.id !== selected.id)); setSel(null); }}>Delete field</button>
            </div>
          </div>
        )}
        <div className="muted small">{fields.length} field(s). Drag to move, corner to resize, Delete key removes.</div>
      </div>

      <PdfPages
        src={src}
        onPageClick={place}
        overlay={(page, size) =>
          fields
            .filter((f) => f.page === page)
            .map((f) => (
              <FieldBox key={f.id} field={f} size={size} editable selected={sel === f.id} onSelect={() => setSel(f.id)} onChange={(p) => patch(f.id, p)}>
                <span className="lbl">{f.key ? `{${f.key}}` : f.label}</span>
              </FieldBox>
            ))
        }
      />
    </div>
  );
}
