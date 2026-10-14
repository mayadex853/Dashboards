"use client";
import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { CATEGORIES } from "@/lib/fields";
import FieldEditor from "@/components/FieldEditor";

export default function TemplateEditor({ params }) {
  const { id } = use(params);
  const [t, setT] = useState(null);
  const [fields, setFields] = useState([]);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const router = useRouter();

  useEffect(() => {
    api(`/api/templates/${id}`).then((t) => {
      setT(t);
      setFields(t.fields || []);
    }).catch((e) => setErr(e.message));
  }, [id]);
  if (err && !t) return <div className="error">{err}</div>;
  if (!t) return <div className="muted">Loading…</div>;

  const save = async () => {
    setErr("");
    try {
      await api(`/api/templates/${id}`, { method: "PUT", body: { ...t, fields } });
      setMsg("Saved");
      setTimeout(() => setMsg(""), 2000);
    } catch (e) {
      setErr(e.message);
    }
  };
  const setRole = (i, p) => setT({ ...t, roles: t.roles.map((r, j) => (j === i ? { ...r, ...p } : r)) });

  return (
    <>
      <div className="page-head">
        <div style={{ flex: 1, minWidth: 260 }}>
          <input style={{ fontSize: 18, fontWeight: 600, maxWidth: 480 }} value={t.name} onChange={(e) => setT({ ...t, name: e.target.value })} />
        </div>
        <div className="actions">
          {msg && <span className="muted" style={{ alignSelf: "center" }}>{msg}</span>}
          <button className="btn danger" onClick={async () => { if (confirm("Delete this template?")) { await api(`/api/templates/${id}`, { method: "DELETE" }); router.push("/templates"); } }}>Delete</button>
          <button className="btn ghost" onClick={async () => { await save(); router.push(`/send?template=${id}`); }}>Save & use</button>
          <button className="btn" onClick={save}>Save</button>
        </div>
      </div>
      {err && <div className="error">{err}</div>}

      <div className="card" style={{ marginBottom: 18 }}>
        <div className="form-grid">
          <div>
            <label>Signing type</label>
            <select value={t.category || ""} onChange={(e) => setT({ ...t, category: e.target.value || null })}>
              <option value="">Any</option>
              {CATEGORIES.map((c) => <option key={c.key} value={c.key}>{c.label}</option>)}
            </select>
          </div>
          <div style={{ gridColumn: "span 2" }}>
            <label>Signer roles (signing order top to bottom)</label>
            {t.roles.map((r, i) => (
              <div className="row" key={i} style={{ marginBottom: 6 }}>
                <span className="muted" style={{ width: 16 }}>{i + 1}.</span>
                <input style={{ flex: 1 }} value={r.name} onChange={(e) => setRole(i, { name: e.target.value })} />
                <select style={{ width: 190 }} value={r.kind} onChange={(e) => setRole(i, { kind: e.target.value })}>
                  <option value="signee">The signee (from intake)</option>
                  <option value="me">Me (countersign)</option>
                  <option value="other">Someone else</option>
                </select>
                {t.roles.length > 1 && (
                  <button className="btn sm ghost" onClick={() => {
                    setT({ ...t, roles: t.roles.filter((_, j) => j !== i) });
                    setFields(fields.filter((f) => f.role !== i).map((f) => (f.role > i ? { ...f, role: f.role - 1 } : f)));
                  }}>✕</button>
                )}
              </div>
            ))}
            <button className="btn sm ghost" onClick={() => setT({ ...t, roles: [...t.roles, { name: `Signer ${t.roles.length + 1}`, kind: "other" }] })}>+ Add role</button>
          </div>
        </div>
      </div>

      <FieldEditor src={`/api/templates/${id}/pdf`} fields={fields} setFields={setFields} roles={t.roles} />
    </>
  );
}
