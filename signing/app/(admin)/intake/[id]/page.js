"use client";
import { use, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { stashLinks, api, fmtDate } from "@/lib/api";
import { CATEGORIES, intakeQuestions } from "@/lib/fields";
import SignerList from "@/components/SignerList";

export default function IntakeDetail({ params }) {
  const { id } = use(params);
  const [d, setD] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [profile, setProfile] = useState(null);
  const [deal, setDeal] = useState({});
  const [signers, setSigners] = useState([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const router = useRouter();

  const load = () =>
    api(`/api/intakes/${id}`).then((x) => {
      setD(x);
      setDeal(x.intake.deal || {});
      setSigners(x.recipients.map((r, i) => ({ ...r, roleName: x.template?.roles[i]?.name })));
    });
  useEffect(() => {
    load().catch((e) => setErr(e.message));
    api("/api/templates").then(setTemplates);
    api("/api/profile").then(setProfile);
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps
  if (err && !d) return <div className="error">{err}</div>;
  if (!d) return <div className="muted">Loading…</div>;
  const { intake, template } = d;
  const qs = intakeQuestions(intake.category);
  const dealKeys = [...new Set((template?.fields || []).map((x) => x.key).filter((k) => k?.startsWith("deal.")).map((k) => k.slice(5)))];

  const setTemplate = async (template_id) => {
    await api(`/api/intakes/${id}`, { method: "PUT", body: { template_id } });
    load();
  };
  const generate = async (send) => {
    setErr("");
    setBusy(true);
    try {
      await api(`/api/intakes/${id}`, { method: "PUT", body: { deal } });
      const res = await api(`/api/intakes/${id}/contract`, {
        method: "POST",
        body: { send, recipients: signers.map(({ roleName, ...s }) => s), values: Object.fromEntries(Object.entries(deal).map(([k, v]) => [`deal.${k}`, v])) },
      });
      stashLinks(res);
      router.push(`/envelopes/${res.envelope.id}`);
    } catch (e) {
      setErr(e.message);
      setBusy(false);
    }
  };

  return (
    <>
      <div className="page-head">
        <div>
          <h1>{intake.answers?.professional_name || intake.answers?.legal_name || intake.signee_name || intake.signee_email}</h1>
          <div className="row">
            <span className="badge">{CATEGORIES.find((c) => c.key === intake.category)?.label}</span>
            <span className={`badge ${intake.status}`}>{intake.status === "sent" ? "awaiting form" : intake.status}</span>
            <span className="muted small">Sent {fmtDate(intake.created_at)}{intake.submitted_at ? ` · Submitted ${fmtDate(intake.submitted_at)}` : ""}</span>
          </div>
        </div>
        <div className="actions">
          <button className="btn danger" onClick={async () => { if (confirm("Delete this intake?")) { await api(`/api/intakes/${id}`, { method: "DELETE" }); router.push("/intake"); } }}>Delete</button>
          {intake.envelope_id && <Link className="btn ghost" href={`/envelopes/${intake.envelope_id}`}>View contract</Link>}
        </div>
      </div>
      {err && <div className="error">{err}</div>}

      <div className="stack">
        <div className="card">
          <h2>Their answers</h2>
          {!intake.answers ? (
            <p className="muted">They haven't submitted the form yet.</p>
          ) : (
            <table>
              <tbody>
                {qs.filter((q) => q.key && intake.answers[q.key]).map((q) => (
                  <tr key={q.key}><td className="muted" style={{ width: "40%" }}>{q.label}</td><td>{intake.answers[q.key]}</td></tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {intake.status !== "contracted" && (
          <div className="card">
            <h2>Contract</h2>
            <div className="field">
              <label>Template</label>
              <select style={{ maxWidth: 400 }} value={intake.template_id || ""} onChange={(e) => setTemplate(e.target.value)}>
                <option value="">Choose…</option>
                {templates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
            {template && (
              <>
                {dealKeys.length > 0 && (
                  <>
                    <h3>Deal terms</h3>
                    <div className="form-grid" style={{ marginBottom: 16 }}>
                      {dealKeys.map((k) => (
                        <div key={k}>
                          <label>{k.replace(/_/g, " ")}</label>
                          <input value={deal[k] || ""} onChange={(e) => setDeal({ ...deal, [k]: e.target.value })} />
                        </div>
                      ))}
                    </div>
                  </>
                )}
                <h3>Signers & order</h3>
                <SignerList signers={signers} setSigners={setSigners} profile={profile} fixedRoles />
                <div className="row end">
                  <button className="btn ghost" disabled={busy || !intake.answers} onClick={() => generate(false)}>Create draft</button>
                  <button className="btn" disabled={busy || !intake.answers} onClick={() => generate(true)}>{busy ? "Working…" : "Generate & send for signature"}</button>
                </div>
                {!intake.answers && <div className="help" style={{ textAlign: "right" }}>Available once they submit the form.</div>}
              </>
            )}
          </div>
        )}
      </div>
    </>
  );
}
