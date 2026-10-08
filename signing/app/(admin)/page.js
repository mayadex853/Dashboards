import Link from "next/link";
import * as db from "@/lib/db";
import { CATEGORIES } from "@/lib/fields";

const fmt = (t) => (t ? new Date(t).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : "—");

export default async function Dashboard() {
  const [envelopes, recipients, intakes] = await Promise.all([db.list("envelopes"), db.list("recipients"), db.list("intakes")]);
  const byEnv = {};
  for (const r of recipients) (byEnv[r.envelope_id] ||= []).push(r);

  const rows = envelopes.map((e) => {
    const recs = (byEnv[e.id] || []).sort((a, b) => a.routing_order - b.routing_order);
    const pending = recs.filter((r) => r.status !== "signed");
    const order = pending.length ? Math.min(...pending.map((r) => r.routing_order)) : null;
    const waitingOn = e.status === "sent" ? pending.filter((r) => r.routing_order === order) : [];
    return { ...e, recs, waitingOn, myTurn: waitingOn.some((r) => r.is_me) };
  });
  const myTurn = rows.filter((r) => r.myTurn);
  const awaiting = rows.filter((r) => r.status === "sent" && !r.myTurn);
  const monthStart = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString();
  const completedMonth = rows.filter((r) => r.status === "completed" && r.completed_at >= monthStart);
  const intakeReady = intakes.filter((i) => i.status === "submitted");

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Dashboard</h1>
          <div className="muted">Contracts, intake and signatures in one place</div>
        </div>
      </div>

      <div className="quick">
        <Link href="/quick-sign"><b>Quick Sign</b><span>Someone sent you a form? Upload, auto-fill your info, sign.</span></Link>
        <Link href="/intake"><b>New signing intake</b><span>Send an artist, writer or catalog owner an intake form → contract.</span></Link>
        <Link href="/send"><b>Send for signature</b><span>Pick a template or upload a PDF and route it in signing order.</span></Link>
      </div>

      <div className="stats">
        <div className="card stat"><div className="n" style={{ color: myTurn.length ? "#f0a640" : undefined }}>{myTurn.length}</div><div className="l">Waiting on you</div></div>
        <div className="card stat"><div className="n">{awaiting.length}</div><div className="l">Waiting on others</div></div>
        <div className="card stat"><div className="n">{intakeReady.length}</div><div className="l">Intakes ready for contract</div></div>
        <div className="card stat"><div className="n">{completedMonth.length}</div><div className="l">Completed this month</div></div>
      </div>

      {intakeReady.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h2>Intakes ready for a contract</h2>
          <table>
            <tbody>
              {intakeReady.map((i) => (
                <tr key={i.id}>
                  <td><Link href={`/intake/${i.id}`}>{i.answers?.professional_name || i.answers?.legal_name || i.signee_name}</Link></td>
                  <td className="muted">{CATEGORIES.find((c) => c.key === i.category)?.label}</td>
                  <td className="muted">Submitted {fmt(i.submitted_at)}</td>
                  <td style={{ textAlign: "right" }}><Link className="btn sm" href={`/intake/${i.id}`}>Review & send</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="card">
        <h2>Documents</h2>
        {!rows.length ? (
          <p className="muted">Nothing yet. Start with Quick Sign, an intake, or Send for signature.</p>
        ) : (
          <table>
            <thead>
              <tr><th>Document</th><th>Status</th><th>Signers</th><th>Updated</th></tr>
            </thead>
            <tbody>
              {rows.map((e) => (
                <tr key={e.id}>
                  <td><Link href={`/envelopes/${e.id}`}>{e.title}</Link></td>
                  <td>
                    {e.myTurn ? <span className="badge turn">Your turn</span> : <span className={`badge ${e.status}`}>{e.status === "sent" ? "In progress" : e.status}</span>}
                  </td>
                  <td className="small">
                    {e.recs.map((r) => (
                      <span key={r.id} style={{ marginRight: 10, color: r.status === "signed" ? "#43c443" : e.waitingOn.includes(r) ? "#f0a640" : "var(--muted)" }}>
                        {r.routing_order}. {r.is_me ? "You" : r.name} {r.status === "signed" ? "✓" : ""}
                      </span>
                    ))}
                  </td>
                  <td className="muted small">{fmt(e.completed_at || e.sent_at || e.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
