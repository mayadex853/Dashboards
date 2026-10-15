import Link from "next/link";
import * as db from "@/lib/db";
import { CATEGORIES, envelopeView } from "@/lib/fields";
import { getProfile } from "@/lib/envelopes";
import HomeDrop from "@/components/HomeDrop";

const fmt = (t) => (t ? new Date(t).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : "—");

export default async function Home() {
  const [envelopes, recipients, intakes, profile] = await Promise.all([
    db.list("envelopes").catch(() => []),
    db.list("recipients").catch(() => []),
    db.list("intakes").catch(() => []),
    getProfile().catch(() => ({ data: {} })),
  ]);
  const byEnv = {};
  for (const r of recipients) (byEnv[r.envelope_id] ||= []).push(r);
  const rows = envelopes.map((e) => envelopeView(e, byEnv[e.id] || []));
  const since = new Date(Date.now() - 182 * 864e5).toISOString();
  const count = (k) => rows.filter((r) => r.view.key === k).length;
  const completed = rows.filter((r) => r.view.key === "completed" && r.completed_at >= since).length;
  const intakeReady = intakes.filter((i) => i.status === "submitted");
  const first = (profile.data?.full_name || "").split(" ")[0];

  return (
    <>
      <div className="home-hero">
        <div>
          <h1>Welcome back{first ? `, ${first}` : ""}</h1>
          <div style={{ opacity: 0.85 }}>Send, sign and track your agreements.</div>
          <div className="sigcard">
            {profile.signature ? <img src={profile.signature} alt="Your signature" /> : <span style={{ opacity: 0.8 }}>No signature yet</span>}
            <Link href="/profile">{profile.signature ? "Edit" : "Create your signature"}</Link>
          </div>
        </div>
        <HomeDrop />
      </div>

      <div className="tiles">
        <Link className="tile" href="/agreements?f=action"><div className="n" style={{ color: count("action") ? "var(--warn)" : undefined }}>{count("action")}</div><div className="l">Action Required</div></Link>
        <Link className="tile" href="/agreements?f=waiting"><div className="n">{count("waiting")}</div><div className="l">Waiting for Others</div></Link>
        <Link className="tile" href="/intake"><div className="n">{intakeReady.length}</div><div className="l">Intakes ready for contract</div></Link>
        <Link className="tile" href="/agreements?f=completed"><div className="n">{completed}</div><div className="l">Completed (last 6 months)</div></Link>
      </div>

      {intakeReady.length > 0 && (
        <div className="card" style={{ marginBottom: 18 }}>
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
        <div className="row" style={{ justifyContent: "space-between", marginBottom: 6 }}>
          <h2 style={{ margin: 0 }}>Recent activity</h2>
          <Link href="/agreements">View all agreements</Link>
        </div>
        {!rows.length ? (
          <p className="muted">No agreements yet. Drop a document above, or use Start → Send an envelope.</p>
        ) : (
          <table>
            <tbody>
              {rows.slice(0, 8).map((e) => (
                <tr key={e.id}>
                  <td>
                    <Link href={`/envelopes/${e.id}`} style={{ fontWeight: 600 }}>{e.title}</Link>
                    <div className="muted small">To: {e.recs.map((r) => (r.is_me ? "You" : r.name)).join(", ")}</div>
                  </td>
                  <td><span className={`st ${e.view.cls}`}><span className="dot">{e.view.icon}</span>{e.view.label}</span></td>
                  <td className="muted small">{fmt(e.completed_at || e.sent_at || e.created_at)}</td>
                  <td style={{ textAlign: "right" }}>
                    {e.myTurn ? <Link className="btn yellow sm" href={`/envelopes/${e.id}?sign=1`}>Sign</Link> : <Link className="btn ghost sm" href={`/envelopes/${e.id}`}>View</Link>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
