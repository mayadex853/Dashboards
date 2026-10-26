"use client";
// Your saved info and signature. Everything autosaves.
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { PROFILE_FIELDS } from "@/lib/fields";
import SignaturePad from "@/components/SignaturePad";
import { toast } from "@/components/Toast";

export default function Profile() {
  const [p, setP] = useState(null);
  const [extra, setExtra] = useState([]);
  const [pad, setPad] = useState(false);
  const [status, setStatus] = useState({ state: "idle" });
  const timer = useRef(null);
  const latest = useRef(null);
  const dirty = useRef(false);

  useEffect(() => {
    api("/api/profile")
      .then((prof) => {
        setP(prof);
        const known = new Set(PROFILE_FIELDS.map((f) => f.key));
        setExtra(Object.entries(prof.data || {}).filter(([k]) => !known.has(k)).map(([k, v]) => ({ k, v })));
      })
      .catch((e) => toast(e.message, true));
  }, []);

  const buildData = (prof, rows) => {
    const data = {};
    for (const f of PROFILE_FIELDS) if (prof.data?.[f.key]) data[f.key] = prof.data[f.key];
    for (const { k, v } of rows) if (k.trim() && v) data[k.trim().toLowerCase().replace(/\s+/g, "_")] = v;
    return data;
  };

  const save = async (body) => {
    setStatus({ state: "saving" });
    try {
      await api("/api/profile", { method: "PUT", body });
      setStatus({ state: "saved" });
    } catch (e) {
      setStatus({ state: "error", msg: e.message });
      toast(`Couldn't save: ${e.message}`, true);
      throw e;
    }
  };

  // Debounced autosave for typed details
  const queue = (prof, rows) => {
    latest.current = { prof, rows };
    dirty.current = true;
    setStatus({ state: "pending" });
    clearTimeout(timer.current);
    timer.current = setTimeout(() => {
      const { prof: pp, rows: rr } = latest.current;
      dirty.current = false;
      save({ data: buildData(pp, rr) }).catch(() => {});
    }, 700);
  };
  // Leaving the page within the debounce window must not lose the last edit
  useEffect(() => () => {
    clearTimeout(timer.current);
    if (dirty.current && latest.current) {
      const { prof: pp, rows: rr } = latest.current;
      fetch("/api/profile", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ data: buildData(pp, rr) }), keepalive: true }).catch(() => {});
    }
  }, []);

  if (!p) return <div className="muted">Loading…</div>;

  const setField = (k, v) => {
    const next = { ...p, data: { ...p.data, [k]: v } };
    setP(next);
    queue(next, extra);
  };
  const setRows = (rows) => {
    setExtra(rows);
    queue(p, rows);
  };

  return (
    <>
      <div className="page-head">
        <div>
          <h1>My signature & info</h1>
          <div className="muted">Used to fill forms and contracts with one click. Changes save automatically.</div>
        </div>
        <div className="actions">
          <SaveStatus status={status} />
        </div>
      </div>

      <div className="stack">
        <div className="card">
          <div className="row" style={{ justifyContent: "space-between", marginBottom: 12 }}>
            <h2 style={{ margin: 0 }}>Signature & initials</h2>
            <button className="btn yellow sm" onClick={() => setPad(true)}>{p.signature ? "Change" : "Create signature"}</button>
          </div>
          <div className="form-grid">
            <div>
              <label>Signature</label>
              <div className="sig-preview">{p.signature ? <img src={p.signature} alt="signature" /> : <span className="muted">Not set</span>}</div>
            </div>
            <div>
              <label>Initials</label>
              <div className="sig-preview">{p.initials ? <img src={p.initials} alt="initials" /> : <span className="muted">Not set</span>}</div>
            </div>
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
          <div className="row" style={{ justifyContent: "space-between" }}>
            <div>
              <h2 style={{ margin: 0 }}>Email</h2>
              <div className="muted small">Signing requests and completed documents are sent from your Microsoft 365 mailbox.</div>
            </div>
            <button
              className="btn ghost sm"
              onClick={async () => {
                try {
                  const r = await api("/api/test-email", { method: "POST" });
                  toast(`Test email sent to ${r.to}. Check your inbox.`);
                } catch (e) {
                  toast(`Email not sent: ${e.message}`, true);
                }
              }}
            >
              Send me a test email
            </button>
          </div>
        </div>

        <div className="card">
          <h2>Other saved values</h2>
          <p className="muted small" style={{ marginTop: -6 }}>Anything else you type often: SoundExchange ID, business license #, bank name…</p>
          {extra.map((row, i) => (
            <div className="row" key={i} style={{ marginBottom: 8 }}>
              <input style={{ flex: 1 }} placeholder="Label" value={row.k} onChange={(e) => setRows(extra.map((r, j) => (j === i ? { ...r, k: e.target.value } : r)))} />
              <input style={{ flex: 2 }} placeholder="Value" value={row.v} onChange={(e) => setRows(extra.map((r, j) => (j === i ? { ...r, v: e.target.value } : r)))} />
              <button className="btn sm ghost" onClick={() => setRows(extra.filter((_, j) => j !== i))}>Remove</button>
            </div>
          ))}
          <button className="btn sm ghost" onClick={() => setExtra([...extra, { k: "", v: "" }])}>+ Add value</button>
        </div>
      </div>

      {pad && (
        <SignaturePad
          defaultName={p.data?.full_name || ""}
          actionLabel="Adopt"
          onCancel={() => setPad(false)}
          onDone={async ({ signature, initials, name }) => {
            const data = buildData({ ...p, data: { ...p.data, full_name: p.data?.full_name || name } }, extra);
            await save({ signature, initials, data });
            setP({ ...p, signature, initials, data: { ...p.data, full_name: data.full_name } });
            setPad(false);
            toast("Signature adopted");
          }}
        />
      )}
    </>
  );
}

function SaveStatus({ status }) {
  if (status.state === "saving" || status.state === "pending") return <span className="saved-pill">Saving…</span>;
  if (status.state === "saved") return <span className="saved-pill ok">All changes saved</span>;
  if (status.state === "error") return <span className="saved-pill err">Not saved: {status.msg}</span>;
  return null;
}
