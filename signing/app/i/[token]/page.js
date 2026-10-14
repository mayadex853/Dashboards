"use client";
import { use, useEffect, useState } from "react";

export default function IntakeForm({ params }) {
  const { token } = use(params);
  const [info, setInfo] = useState(null);
  const [answers, setAnswers] = useState({});
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    fetch(`/api/public/intake/${token}`)
      .then(async (r) => {
        const j = await r.json();
        if (!r.ok) throw new Error(j.error);
        setInfo(j);
        setAnswers(j.prefill || {});
      })
      .catch((e) => setErr(e.message));
  }, [token]);

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    setBusy(true);
    const r = await fetch(`/api/public/intake/${token}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ answers }) });
    const j = await r.json();
    setBusy(false);
    if (!r.ok) return setErr(j.error);
    setDone(j.autoSent ? "sent" : "review");
  };

  const shell = (children) => (
    <div className="public">
      <div className="content narrow">{children}</div>
    </div>
  );
  if (done)
    return shell(
      <div className="card center-box" style={{ minHeight: 240, flexDirection: "column" }}>
        <h1>Thank you!</h1>
        <p className="muted">{done === "sent" ? "Your agreement is on its way. Check your email for a signing link." : `${info.sender} will review your details and send your agreement shortly.`}</p>
      </div>
    );
  if (err && !info) return shell(<div className="card"><h2>Link problem</h2><p className="muted">{err}</p></div>);
  if (!info) return shell(<div className="muted">Loading…</div>);
  if (info.submitted) return shell(<div className="card"><h2>Already submitted</h2><p className="muted">We have your details. Reach out to {info.sender} if anything needs to change.</p></div>);

  return shell(
    <form onSubmit={submit}>
      <div style={{ marginBottom: 18 }}>
        <div className="muted small" style={{ textTransform: "uppercase", letterSpacing: ".6px" }}>{info.sender}</div>
        <h1>{info.category} intake</h1>
        <p className="muted">This information goes into your agreement, so please use your legal details. Fields marked * are required.</p>
      </div>
      <div className="card">
        {info.questions.map((q, i) =>
          q.section ? (
            <h2 key={i} style={{ marginTop: i ? 22 : 0 }}>{q.section}</h2>
          ) : (
            <div className="field" key={q.key}>
              <label>{q.label}{q.required ? " *" : ""}</label>
              {q.type === "select" ? (
                <select required={q.required} value={answers[q.key] || ""} onChange={(e) => setAnswers({ ...answers, [q.key]: e.target.value })}>
                  <option value="">Select…</option>
                  {q.options.map((o) => <option key={o}>{o}</option>)}
                </select>
              ) : q.type === "textarea" ? (
                <textarea value={answers[q.key] || ""} onChange={(e) => setAnswers({ ...answers, [q.key]: e.target.value })} />
              ) : (
                <input type={q.type || "text"} required={q.required} value={answers[q.key] || ""} onChange={(e) => setAnswers({ ...answers, [q.key]: e.target.value })} />
              )}
              {q.help && <div className="help">{q.help}</div>}
            </div>
          )
        )}
        {err && <div className="error">{err}</div>}
        <div className="row end"><button className="btn" disabled={busy}>{busy ? "Submitting…" : "Submit"}</button></div>
      </div>
      <p className="muted small" style={{ marginTop: 12 }}>Tax forms (W-9 / W-8BEN) are collected separately and securely. Don't enter your SSN here.</p>
    </form>
  );
}
