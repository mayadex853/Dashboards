"use client";
// DocuSign-style Agreements: folders on the left, list with status and quick actions on the right.
import { Suspense, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { api, fmtDate } from "@/lib/api";
import { toast } from "@/components/Toast";

const FOLDERS = [
  { section: "Envelopes" },
  { key: "inbox", label: "Inbox", test: (e) => e.status !== "draft" },
  { key: "sent", label: "Sent", test: (e) => ["sent", "completed", "declined", "voided"].includes(e.status) },
  { key: "drafts", label: "Drafts", test: (e) => e.status === "draft" },
  { section: "Quick views" },
  { key: "action", label: "Action Required", test: (e) => e.view.key === "action" },
  { key: "waiting", label: "Waiting for Others", test: (e) => e.view.key === "waiting" },
  { key: "completed", label: "Completed", test: (e) => e.view.key === "completed" },
  { key: "voided", label: "Voided / Declined", test: (e) => ["voided", "declined"].includes(e.view.key) },
  { section: "My documents" },
  { key: "self", label: "Signed by me" },
];

export default function AgreementsPage() {
  return (
    <Suspense fallback={<div className="muted">Loading…</div>}>
      <Agreements />
    </Suspense>
  );
}

function Agreements() {
  const params = useSearchParams();
  const router = useRouter();
  const folder = params.get("f") || "inbox";
  const [data, setData] = useState(null);
  const [q, setQ] = useState("");

  const load = () => api("/api/agreements").then(setData).catch((e) => toast(e.message, true));
  useEffect(() => { load(); }, []);

  const counts = useMemo(() => {
    const c = {};
    for (const f of FOLDERS) if (f.test && data) c[f.key] = data.envelopes.filter(f.test).length;
    if (data) c.self = data.quick.length;
    return c;
  }, [data]);

  const cur = FOLDERS.find((f) => f.key === folder) || FOLDERS[1];
  const needle = q.trim().toLowerCase();
  const rows = !data ? [] : folder === "self" ? [] : data.envelopes.filter(cur.test).filter((e) => !needle || e.title.toLowerCase().includes(needle) || e.recs.some((r) => `${r.name} ${r.email}`.toLowerCase().includes(needle)));
  const quick = !data || folder !== "self" ? [] : data.quick.filter((x) => !needle || x.title.toLowerCase().includes(needle));

  const act = async (e, action, recipient_id) => {
    try {
      await api(`/api/envelopes/${e.id}/action`, { method: "POST", body: { action, recipient_id } });
      toast(action === "remind" ? "Reminder sent" : action === "void" ? "Envelope voided" : "Done");
      load();
    } catch (err) {
      toast(err.message, true);
    }
  };

  return (
    <>
      <div className="page-head">
        <div><h1>Agreements</h1></div>
        <div className="actions">
          <input placeholder="Search agreements" value={q} onChange={(e) => setQ(e.target.value)} style={{ width: 260 }} />
          <Link className="btn yellow" href="/send">Start</Link>
        </div>
      </div>
      <div className="agr">
        <div className="folders">
          {FOLDERS.map((f, i) =>
            f.section ? (
              <div key={i} className="ftitle">{f.section}</div>
            ) : (
              <a key={f.key} href={`/agreements?f=${f.key}`} className={folder === f.key ? "on" : ""} onClick={(ev) => { ev.preventDefault(); router.push(`/agreements?f=${f.key}`); }}>
                <span>{f.label}</span>
                <span className="c">{counts[f.key] ?? ""}</span>
              </a>
            )
          )}
        </div>
        <div className="list">
          <h2>{cur.label}</h2>
          {!data ? (
            <div className="muted">Loading…</div>
          ) : folder === "self" ? (
            !quick.length ? <p className="muted">Nothing here yet. Use Start → Sign a document.</p> : (
              <table>
                <thead><tr><th>Document</th><th>Status</th><th>Signed</th><th /></tr></thead>
                <tbody>
                  {quick.map((x) => (
                    <tr key={x.id}>
                      <td><div className="subj">{x.title}</div>{x.emailed_to && <div className="to">Emailed to {x.emailed_to}</div>}</td>
                      <td><span className="st done"><span className="dot">✓</span>Signed by you</span></td>
                      <td className="muted small">{fmtDate(x.created_at)}</td>
                      <td style={{ textAlign: "right" }}><a className="btn ghost sm" href={`/api/quick-sign/${x.id}/pdf`}>Download</a></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          ) : !rows.length ? (
            <p className="muted">No agreements in this folder.</p>
          ) : (
            <table>
              <thead><tr><th>Subject</th><th>Status</th><th>Last change</th><th /></tr></thead>
              <tbody>
                {rows.map((e) => {
                  const next = e.waitingOn.find((r) => !r.is_me);
                  return (
                    <tr key={e.id}>
                      <td>
                        <Link href={`/envelopes/${e.id}`} className="subj">{e.title}</Link>
                        <div className="to">To: {e.recs.map((r) => `${r.is_me ? "You" : r.name}${r.kind === "cc" ? " (CC)" : ""}`).join(", ")}</div>
                      </td>
                      <td><span className={`st ${e.view.cls}`}><span className="dot">{e.view.icon}</span>{e.view.label}</span></td>
                      <td className="muted small">{fmtDate(e.completed_at || e.voided_at || e.sent_at || e.created_at)}</td>
                      <td style={{ textAlign: "right", whiteSpace: "nowrap" }}>
                        {e.view.key === "action" && <Link className="btn yellow sm" href={`/envelopes/${e.id}?sign=1`}>Sign</Link>}
                        {e.view.key === "waiting" && next && <button className="btn ghost sm" onClick={() => act(e, "remind", next.id)}>Resend</button>}
                        {e.view.key === "draft" && <Link className="btn ghost sm" href={`/envelopes/${e.id}`}>Continue</Link>}
                        {e.view.key === "completed" && <a className="btn ghost sm" href={`/api/envelopes/${e.id}/pdf?download`}>Download</a>}
                        {["voided", "declined"].includes(e.view.key) && <Link className="btn ghost sm" href={`/envelopes/${e.id}`}>View</Link>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
}
