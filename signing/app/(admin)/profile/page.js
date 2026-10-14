"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PROFILE_FIELDS } from "@/lib/fields";
import SignaturePad from "@/components/SignaturePad";

export default function Profile() {
  const [p, setP] = useState(null);
  const [extra, setExtra] = useState([]);
  const [pad, setPad] = useState(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api("/api/profile").then((prof) => {
      setP(prof);
      const known = new Set(PROFILE_FIELDS.map((f) => f.key));
      setExtra(Object.entries(prof.data || {}).filter(([k]) => !known.has(k)).map(([k, v]) => ({ k, v })));
    });
  }, []);
  if (!p) return <div className="muted">Loading…</div>;

  const setField = (k, v) => setP({ ...p, data: { ...p.data, [k]: v } });
  const save = async (patch = {}) => {
    const data = { ...p.data };
    for (const k of Object.keys(data)) if (!PROFILE_FIELDS.some((f) => f.key === k)) delete data[k];
    for (const { k, v } of extra) if (k.trim()) data[k.trim().toLowerCase().replace(/\s+/g, "_")] = v;
    const saved = await api("/api/profile", { method: "PUT", body: { data, signature: p.signature, initials: p.initials, ...patch } });
    setP(saved);
    setMsg("Saved");
    setTimeout(() => setMsg(""), 2000);
  };

  return (
    <>
      <div className="page-head">
        <div>
          <h1>My info & signature</h1>
          <div className="muted">Used to auto-fill forms and contracts with one click.</div>
        </div>
        <div className="actions">
          {msg && <span className="muted">{msg}</span>}
          <button className="btn" onClick={() => save()}>Save</button>
        </div>
      </div>

      <div className="stack">
        <div className="card">
          <h2>Signature & initials</h2>
          <div className="form-grid">
            {["signature", "initials"].map((kind) => (
              <div key={kind}>
                <label>{kind === "signature" ? "Signature" : "Initials"}</label>
                <div className="sig-preview">{p[kind] ? <img src={p[kind]} alt={kind} /> : <span style={{ color: "#999" }}>Not set</span>}</div>
                <div className="row" style={{ marginTop: 8 }}>
                  <button className="btn sm ghost" onClick={() => setPad(kind)}>{p[kind] ? "Change" : "Create"}</button>
                  {p[kind] && <button className="btn sm danger" onClick={() => save({ [kind]: null })}>Remove</button>}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2>Details</h2>
          <div className="form-grid">
            {PROFILE_FIELDS.map((f) => (
              <div key={f.key}>
                <label>{f.label}</label>
                <input value={p.data?.[f.key] || ""} onChange={(e) => setField(f.key, e.target.value)} />
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2>Other saved values</h2>
          <p className="muted small" style={{ marginTop: -6 }}>Anything else you type often: EIN (last 4), bank name, SoundExchange ID, business license #…</p>
          {extra.map((row, i) => (
            <div className="row" key={i} style={{ marginBottom: 8 }}>
              <input style={{ flex: 1 }} placeholder="Label" value={row.k} onChange={(e) => setExtra(extra.map((r, j) => (j === i ? { ...r, k: e.target.value } : r)))} />
              <input style={{ flex: 2 }} placeholder="Value" value={row.v} onChange={(e) => setExtra(extra.map((r, j) => (j === i ? { ...r, v: e.target.value } : r)))} />
              <button className="btn sm ghost" onClick={() => setExtra(extra.filter((_, j) => j !== i))}>✕</button>
            </div>
          ))}
          <button className="btn sm ghost" onClick={() => setExtra([...extra, { k: "", v: "" }])}>+ Add value</button>
        </div>
      </div>

      {pad && (
        <SignaturePad
          kind={pad}
          defaultName={p.data?.full_name || ""}
          onCancel={() => setPad(null)}
          onDone={(png) => {
            setPad(null);
            setP({ ...p, [pad]: png });
            save({ [pad]: png });
          }}
        />
      )}
    </>
  );
}
