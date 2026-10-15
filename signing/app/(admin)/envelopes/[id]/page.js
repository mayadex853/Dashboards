"use client";
// Envelope details, DocuSign style: status header with actions, recipients with routing status,
// history, and the document.
import { use, useEffect, useState, useCallback, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, fmtDate, takeLinks } from "@/lib/api";
import { envelopeView } from "@/lib/fields";
import PdfPages from "@/components/PdfPages";
import { toast } from "@/components/Toast";

export default function EnvelopePage({ params, searchParams }) {
  const { id } = use(params);
  const sp = use(searchParams);
  const [d, setD] = useState(null);
  const [err, setErr] = useState("");
  const [links, setLinks] = useState({});
  const [v, setV] = useState(0);
  const [showHistory, setShowHistory] = useState(false);
  const autoSigned = useRef(false);
  const router = useRouter();

  const load = useCallback(() => api(`/api/envelopes/${id}`).then(setD).catch((e) => setErr(e.message)), [id]);
  useEffect(() => {
    load();
    const fresh = takeLinks(id);
    if (fresh.length) setLinks(Object.fromEntries(fresh.map((x) => [x.recipient_id, x])));
  }, [load, id]);

  const act = async (action, recipient_id) => {
    try {
      const res = await api(`/api/envelopes/${id}/action`, { method: "POST", body: { action, recipient_id } });
      const l = { ...links };
      for (const x of res.links || []) l[x.recipient_id] = x;
      if (res.link) l[recipient_id] = { link: res.link };
      setLinks(l);
      if (action === "remind") toast("Reminder sent");
      if (action === "void") toast("Envelope voided");
      if (action === "send") toast("Envelope sent");
      await load();
      setV((x) => x + 1);
      return res;
    } catch (ex) {
      toast(ex.message, true);
    }
  };
  const signNow = async (r) => {
    const res = await act("link", r.id);
    if (res?.link) location.href = res.link;
  };

  // Arriving from a "Sign" button → open your signing session straight away
  useEffect(() => {
    if (!d || autoSigned.current || sp?.sign !== "1") return;
    const view = envelopeView(d.envelope, d.recipients);
    const me = view.waitingOn.find((r) => r.is_me);
    if (me) {
      autoSigned.current = true;
      signNow(me);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [d]);

  if (err && !d) return <div className="error">{err}</div>;
  if (!d) return <div className="muted">Loading…</div>;
  const { envelope: e, recipients, events } = d;
  const view = envelopeView(e, recipients);
  const isTurn = (r) => view.waitingOn.includes(r);
  const me = view.waitingOn.find((r) => r.is_me);
  const nextOther = view.waitingOn.find((r) => !r.is_me);
  const ordered = [...recipients].sort((a, b) => (a.kind === "cc") - (b.kind === "cc") || a.routing_order - b.routing_order);

  const recipientStatus = (r) => {
    if (r.kind === "cc") return e.status === "completed" ? "Received a copy" : "Will receive a copy when complete";
    if (r.status === "signed") return `Signed on ${fmtDate(r.signed_at)}`;
    if (e.status === "draft") return "Needs to sign";
    if (e.status === "declined" || e.status === "voided") return r.viewed_at ? `Viewed ${fmtDate(r.viewed_at)}` : "—";
    if (isTurn(r)) return r.viewed_at ? `Viewed on ${fmtDate(r.viewed_at)} · Needs to sign` : `Sent on ${fmtDate(r.sent_at)} · Needs to sign`;
    return "Waiting for others to sign first";
  };

  return (
    <>
      <div style={{ marginBottom: 10 }}><Link href="/agreements">← Agreements</Link></div>
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="row" style={{ alignItems: "flex-start" }}>
          <div style={{ flex: 1, minWidth: 240 }}>
            <h1 style={{ marginBottom: 6 }}>{e.title}</h1>
            <span className={`st ${view.view.cls}`}><span className="dot">{view.view.icon}</span>{view.view.label}</span>
            <div className="muted small" style={{ marginTop: 8 }}>
              Created {fmtDate(e.created_at)}{e.sent_at ? ` · Sent ${fmtDate(e.sent_at)}` : ""}{e.completed_at ? ` · Completed ${fmtDate(e.completed_at)}` : ""}
            </div>
          </div>
          <div className="row">
            {me && <button className="btn yellow" onClick={() => signNow(me)}>Sign</button>}
            {e.status === "draft" && <button className="btn yellow" onClick={() => act("send")}>Send now</button>}
            {nextOther && <button className="btn ghost" onClick={() => act("remind", nextOther.id)}>Resend</button>}
            <a className="btn ghost" href={`/api/envelopes/${id}/pdf?download`}>Download</a>
            {e.status === "sent" && <button className="btn danger" onClick={() => confirm("Void this envelope? Signing links will stop working.") && act("void")}>Void</button>}
            {e.status === "draft" && (
              <button className="btn danger" onClick={async () => { if (confirm("Delete this draft?")) { await api(`/api/envelopes/${id}`, { method: "DELETE" }); router.push("/agreements?f=drafts"); } }}>Delete</button>
            )}
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h2>Recipients</h2>
        {ordered.map((r) => (
          <div key={r.id} className="row" style={{ padding: "12px 0", borderTop: "1px solid var(--border)", alignItems: "center" }}>
            <span style={{ width: 30, height: 30, borderRadius: "50%", display: "grid", placeItems: "center", fontWeight: 700, fontSize: 12, background: r.status === "signed" ? "#e3f4e9" : isTurn(r) ? "#fff4cc" : "#efeff3", color: r.status === "signed" ? "var(--good)" : "var(--ink-2)" }}>
              {r.kind === "cc" ? "CC" : r.status === "signed" ? "✓" : r.routing_order}
            </span>
            <div style={{ flex: 1, minWidth: 200 }}>
              <div style={{ fontWeight: 600 }}>{r.name}{r.is_me && <span className="badge" style={{ marginLeft: 6 }}>You</span>}</div>
              <div className="muted small">{r.email} · {r.kind === "cc" ? "Receives a copy" : "Needs to sign"}</div>
            </div>
            <div className="small" style={{ color: isTurn(r) ? "var(--warn)" : r.status === "signed" ? "var(--good)" : "var(--muted)", minWidth: 220 }}>{recipientStatus(r)}</div>
            <div className="row">
              {isTurn(r) && r.is_me && <button className="btn sm yellow" onClick={() => signNow(r)}>Sign</button>}
              {isTurn(r) && !r.is_me && (
                <>
                  <button className="btn sm ghost" onClick={() => act("remind", r.id)}>Resend</button>
                  <button className="btn sm ghost" onClick={() => act("link", r.id)}>Copy signing link</button>
                </>
              )}
            </div>
            {links[r.id] && r.status !== "signed" && (
              <div style={{ width: "100%" }}>
                <label className="small">
                  Signing link for {r.name} {links[r.id].emailed === false && <span className="muted">(email wasn't sent, so copy and share this link)</span>}
                </label>
                <div className="copy">
                  <input readOnly value={links[r.id].link} onFocus={(ev) => ev.target.select()} />
                  <button className="btn sm ghost" onClick={() => { navigator.clipboard.writeText(links[r.id].link); toast("Link copied"); }}>Copy</button>
                </div>
              </div>
            )}
          </div>
        ))}
        {e.message && (
          <div style={{ borderTop: "1px solid var(--border)", paddingTop: 12 }}>
            <div className="panel-title">Message</div>
            <div style={{ whiteSpace: "pre-wrap" }}>{e.message}</div>
          </div>
        )}
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="row" style={{ justifyContent: "space-between" }}>
          <h2 style={{ margin: 0 }}>History</h2>
          <button className="link" onClick={() => setShowHistory(!showHistory)}>{showHistory ? "Hide" : `Show ${events.length} events`}</button>
        </div>
        {showHistory && (
          <table style={{ marginTop: 10 }}>
            <thead><tr><th>Time</th><th>Activity</th><th>Recipient</th><th>IP address</th></tr></thead>
            <tbody>
              {events.map((ev) => {
                const r = recipients.find((x) => x.id === ev.recipient_id);
                return (
                  <tr key={ev.id}>
                    <td className="small">{fmtDate(ev.created_at)}</td>
                    <td style={{ textTransform: "capitalize" }}>{ev.type.replace(/_/g, " ")}</td>
                    <td className="small">{r ? `${r.name} (${r.email})` : "—"}</td>
                    <td className="small muted">{ev.ip || "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
        {e.final_sha256 && <div className="muted small" style={{ wordBreak: "break-all", marginTop: 10 }}>Document fingerprint (SHA-256): {e.final_sha256}</div>}
      </div>

      <h2>Document</h2>
      <PdfPages key={v} src={`/api/envelopes/${id}/pdf?v=${v}`} />
    </>
  );
}
