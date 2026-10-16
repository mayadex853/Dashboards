"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api, fmtDate } from "@/lib/api";
import { CATEGORIES } from "@/lib/fields";

const blank = { category: "artist", signee_name: "", signee_email: "", template_id: "", message: "", auto_send: false, deal: {} };

export default function Intake() {
  const [list, setList] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [f, setF] = useState(blank);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [result, setResult] = useState(null);

  const load = () => api("/api/intakes").then(setList);
  useEffect(() => {
    load();
    api("/api/templates").then(setTemplates);
  }, []);

  const template = templates.find((t) => t.id === f.template_id);
  const dealKeys = [...new Set((template?.fields || []).map((x) => x.key).filter((k) => k?.startsWith("deal.")))];
  const suggested = templates.filter((t) => !t.category || t.category === f.category);

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    setBusy(true);
    try {
      const res = await api("/api/intakes", { method: "POST", body: f });
      setResult(res);
      setF({ ...blank, category: f.category });
      load();
    } catch (ex) {
      setErr(ex.message);
    }
    setBusy(false);
  };

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Signing intake</h1>
          <div className="muted">Send a new signee a short form. Their answers fill the contract automatically.</div>
        </div>
      </div>

      <form className="card" style={{ marginBottom: 20 }} onSubmit={submit}>
        <h2>New intake</h2>
        <div className="field">
          <label>Signing type</label>
          <div className="chips">
            {CATEGORIES.map((c) => (
              <button type="button" key={c.key} className={`chip ${f.category === c.key ? "on" : ""}`} onClick={() => setF({ ...f, category: c.key })}>{c.label}</button>
            ))}
          </div>
        </div>
        <div className="form-grid">
          <div><label>Signee name</label><input value={f.signee_name} onChange={(e) => setF({ ...f, signee_name: e.target.value })} /></div>
          <div><label>Signee email</label><input type="email" required value={f.signee_email} onChange={(e) => setF({ ...f, signee_email: e.target.value })} /></div>
          <div>
            <label>Contract template</label>
            <select value={f.template_id} onChange={(e) => setF({ ...f, template_id: e.target.value })}>
              <option value="">Decide later</option>
              {suggested.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          </div>
        </div>
        {dealKeys.length > 0 && (
          <>
            <h3 style={{ marginTop: 16 }}>Deal terms</h3>
            <div className="form-grid">
              {dealKeys.map((k) => (
                <div key={k}>
                  <label>{k.replace("deal.", "").replace(/_/g, " ")}</label>
                  <input value={f.deal[k.slice(5)] || ""} onChange={(e) => setF({ ...f, deal: { ...f.deal, [k.slice(5)]: e.target.value } })} />
                </div>
              ))}
            </div>
          </>
        )}
        <div className="field" style={{ marginTop: 14 }}>
          <label>Personal note (optional)</label>
          <textarea value={f.message} onChange={(e) => setF({ ...f, message: e.target.value })} placeholder="Welcome aboard! Fill this out and I'll send the agreement right over." />
        </div>
        {f.template_id && (
          <label className="row" style={{ gap: 8 }}>
            <input type="checkbox" checked={f.auto_send} onChange={(e) => setF({ ...f, auto_send: e.target.checked })} />
            Send the contract for signature automatically when they submit (skip my review)
          </label>
        )}
        {err && <div className="error">{err}</div>}
        <div className="row end"><button className="btn" disabled={busy}>{busy ? "Sending…" : "Send intake form"}</button></div>
        {result && (
          <div className={result.emailed ? "success" : "hint"} style={{ marginTop: 12 }}>
            {result.emailed ? "Intake emailed. " : "Email isn't configured, so share this link yourself: "}
            <div className="copy" style={{ marginTop: 6 }}>
              <input readOnly value={result.link} onFocus={(e) => e.target.select()} />
              <button type="button" className="btn sm ghost" onClick={() => navigator.clipboard.writeText(result.link)}>Copy</button>
            </div>
          </div>
        )}
      </form>

      <div className="card">
        <h2>All intakes</h2>
        {!list ? <div className="muted">Loading…</div> : !list.length ? <div className="muted">None yet.</div> : (
          <table>
            <thead><tr><th>Signee</th><th>Type</th><th>Status</th><th>Sent</th></tr></thead>
            <tbody>
              {list.map((i) => (
                <tr key={i.id}>
                  <td><Link href={`/intake/${i.id}`}>{i.answers?.professional_name || i.answers?.legal_name || i.signee_name || i.signee_email}</Link><div className="muted small">{i.signee_email}</div></td>
                  <td className="muted">{CATEGORIES.find((c) => c.key === i.category)?.label}</td>
                  <td><span className={`badge ${i.status}`}>{i.status === "sent" ? "awaiting form" : i.status}</span></td>
                  <td className="muted small">{fmtDate(i.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
