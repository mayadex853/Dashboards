"use client";
// DocuSign-style "Add fields" editor: pick a recipient, drag standard fields onto the document,
// adjust the selected field on the right.
import { useEffect, useState } from "react";
import PdfPages from "@/components/PdfPages";
import FieldBox, { ROLE_COLORS } from "@/components/FieldBox";
import { FIELD_TYPES, PROFILE_FIELDS, ALL_INTAKE_KEYS } from "@/lib/fields";
import { startPaletteDrag } from "@/components/dragPlace";

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

// When you place a field for yourself, fill it from your saved info.
const ME_KEYS = { name: "profile.full_name", email: "profile.email", company: "profile.company", title: "profile.title" };
const SIGNEE_KEYS = { company: "intake.entity_name" };

export const roleColor = (i) => ROLE_COLORS[i % ROLE_COLORS.length];

export default function FieldEditor({ src, fields, setFields, roles, showKeys = true }) {
  const [tool, setTool] = useState(null);
  const [role, setRole] = useState(0);
  const [sel, setSel] = useState(null);
  const selected = fields.find((f) => f.id === sel);

  useEffect(() => {
    if (role >= roles.length) setRole(0);
  }, [roles.length, role]);

  useEffect(() => {
    const onKey = (e) => {
      if (["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement?.tagName)) return;
      if (sel && (e.key === "Delete" || e.key === "Backspace")) {
        setFields((fs) => fs.filter((f) => f.id !== sel));
        setSel(null);
      }
      if (e.key === "Escape") {
        setSel(null);
        setTool(null);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [sel, setFields]);

  const place = (type, page, fx, fy) => {
    const t = FIELD_TYPES.find((x) => x.type === type);
    const kind = roles[role]?.kind;
    const key = kind === "me" ? ME_KEYS[type] : kind === "signee" ? SIGNEE_KEYS[type] : undefined;
    const f = {
      id: Math.random().toString(36).slice(2, 10),
      type,
      page,
      x: clamp(fx - 0.01, 0, 1 - t.w),
      y: clamp(fy - t.h / 2, 0, 1 - t.h),
      w: t.w,
      h: t.h,
      role,
      label: t.label,
      key,
      required: type !== "checkbox",
    };
    setFields((fs) => [...fs, f]);
    setSel(f.id);
  };
  const patch = (id, p) => setFields((fs) => fs.map((f) => (f.id === id ? { ...f, ...p } : f)));
  const remove = (id) => {
    setFields((fs) => fs.filter((f) => f.id !== id));
    setSel(null);
  };

  return (
    <div className="editor">
      <div className="side stack">
        <div className="card" style={{ padding: 14 }}>
          <div className="panel-title">Recipient</div>
          <div className="recips">
            {roles.map((r, i) => (
              <button key={i} className={`recip ${role === i ? "on" : ""}`} style={{ "--fc": roleColor(i) }} onClick={() => setRole(i)}>
                <span className="dot" />
                <span style={{ flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{r.name || `Signer ${i + 1}`}</span>
                <span className="muted small">{fields.filter((f) => f.role === i).length}</span>
              </button>
            ))}
          </div>
          <div className="panel-title" style={{ marginTop: 16 }}>Standard fields</div>
          <div className="palette">
            {FIELD_TYPES.map((t) => (
              <button
                key={t.type}
                className={`pitem ${tool === t.type ? "on" : ""}`}
                onPointerDown={(e) =>
                  startPaletteDrag(e, {
                    label: t.label,
                    onDrop: (page, fx, fy) => place(t.type, page, fx, fy),
                    onClick: () => setTool(t.type),
                  })
                }
              >
                <span className="ico" style={{ background: `color-mix(in srgb, ${roleColor(role)} 18%, white)` }}>{t.icon}</span>
                {t.label}
              </button>
            ))}
          </div>
          <div className="hint" style={{ marginTop: 12 }}>
            {tool ? (
              <>
                Click the document to place <b>{FIELD_TYPES.find((t) => t.type === tool).label}</b> for <b>{roles[role]?.name || "this recipient"}</b>.{" "}
                <button className="link" onClick={() => setTool(null)}>Stop placing</button>
              </>
            ) : (
              "Drag a field onto the document, or click a field then click the page."
            )}
          </div>
        </div>
      </div>

      <PdfPages
        src={src}
        onPageClick={(page, fx, fy) => (tool ? place(tool, page, fx, fy) : setSel(null))}
        overlay={(page, size) =>
          fields
            .filter((f) => f.page === page)
            .map((f) => (
              <FieldBox key={f.id} field={f} size={size} editable selected={sel === f.id} color={roleColor(f.role)} onSelect={() => setSel(f.id)} onChange={(p) => patch(f.id, p)}>
                <span className="lbl">{f.type === "checkbox" ? "" : f.key ? `${f.label} ⟵ ${f.key}` : f.label}</span>
              </FieldBox>
            ))
        }
      />

      <div className="side props">
        <div className="card" style={{ padding: 14 }}>
          {!selected ? (
            <>
              <div className="panel-title">Field properties</div>
              <p className="muted small" style={{ margin: 0 }}>Select a field on the document to edit it. Drag to move, use the corner to resize, press Delete to remove.</p>
              <p className="muted small">{fields.length} field{fields.length === 1 ? "" : "s"} placed.</p>
            </>
          ) : (
            <>
              <div className="panel-title">{FIELD_TYPES.find((t) => t.type === selected.type)?.label} field</div>
              <div className="field">
                <label>Recipient</label>
                <select value={selected.role} onChange={(e) => patch(selected.id, { role: Number(e.target.value) })}>
                  {roles.map((r, i) => <option key={i} value={i}>{r.name || `Signer ${i + 1}`}</option>)}
                </select>
              </div>
              <label className="row" style={{ gap: 6, marginBottom: 12 }}>
                <input type="checkbox" checked={selected.required !== false} onChange={(e) => patch(selected.id, { required: e.target.checked })} /> Required field
              </label>
              <div className="field">
                <label>Data label</label>
                <input value={selected.label || ""} onChange={(e) => patch(selected.id, { label: e.target.value })} />
              </div>
              {["text", "company", "title", "name", "email"].includes(selected.type) && showKeys && (
                <div className="field">
                  <label>Auto-fill from</label>
                  <input list="key-suggestions" placeholder="(signer types it)" value={selected.key || ""} onChange={(e) => patch(selected.id, { key: e.target.value.trim() || undefined })} />
                  <datalist id="key-suggestions">
                    {KEY_SUGGESTIONS.map((k) => <option key={k.key} value={k.key}>{k.label}</option>)}
                  </datalist>
                  <div className="help">Signee answers (intake.*), your info (profile.*), or deal terms entered when sending (deal.anything).</div>
                </div>
              )}
              {selected.type === "text" && (
                <div className="field">
                  <label>Default text</label>
                  <input value={selected.defaultValue || ""} onChange={(e) => patch(selected.id, { defaultValue: e.target.value || undefined })} />
                </div>
              )}
              <div className="row" style={{ justifyContent: "space-between" }}>
                <button className="btn sm ghost" onClick={() => { const c = { ...selected, id: Math.random().toString(36).slice(2, 10), y: clamp(selected.y + selected.h + 0.01, 0, 1 - selected.h) }; setFields((fs) => [...fs, c]); setSel(c.id); }}>Duplicate</button>
                <button className="btn sm danger" onClick={() => remove(selected.id)}>Delete</button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
