"use client";
import { use, useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { api, fmtDate, takeLinks } from "@/lib/api";
import PdfPages from "@/components/PdfPages";

export default function EnvelopePage({ params }) {
  const { id } = use(params);
  const [d, setD] = useState(null);
  const [err, setErr] = useState("");
  const [links, setLinks] = useState({});
  const [v, setV] = useState(0);
  const router = useRouter();

  const load = useCallback(() => api(`/api/envelopes/${id}`).then(setD).catch((e) => setErr(e.message)), [id]);
  useEffect(() => {
    load();
    const fresh = takeLinks(id);
    if (fresh.length) setLinks(Object.fromEntries(fresh.map((x) => [x.recipient_id, x])));
  }, [load, id]);
  if (err && !d) return <div className="error">{err}</div>;
  if (!d) return <div className="muted">Loading…</div>;
  const { envelope: e, recipients, events } = d;

  const act = async (action, recipient_id) => {
    setErr("");
    try {
      const res = await api(`/api/envelopes/${id}/action`, { method: "POST", body: { action, recipient_id } });
      const l = { ...links };
      for (const x of res.links || []) l[x.recipient_id] = x;
      if (res.link) l[recipient_id] = { link: res.link };
      setLinks(l);
      await load();
      setV(v + 1);
      return res;
    } catch (ex) {
      setErr(ex.message);
    }
  };

  const pending = recipients.filter((r) => r.status !== "signed");
  const order = pending.length ? Math.min(...pending.map((r) => r.routing_order)) : null;
  const isTurn = (r) => e.status === "sent" && r.status !== "signed" && r.routing_order === order;

  return (
    <>
      <div className="page-head">
        <div>
          <h1>{e.title}</h1>
          <div className="row">
            <span className={`badge ${e.status}`}>{e.status === "sent" ? "In progress" : e.status}</span>
            <span className="muted small">Created {fmtDate(e.created_at)}</span>
          </div>
        </div>
        <div className="actions">
          {e.status === "draft" && <button className="btn danger" onClick={async () => { if (confirm("Delete draft?")) { await api(`/api/envelopes/${id}`, { method: "DELETE" }); router.push("/"); } }}>Delete</button>}
          {e.status === "sent" && <button className="btn danger" onClick={() => confirm("Void this envelope? Signing links will stop working.") && act("void")}>Void</button>}
          <a className="btn ghost" href={`/api/envelopes/${id}/pdf?download`}>Download{e.status === "completed" ? " signed PDF" : ""}</a>
          {e.status === "draft" && <button className="btn" onClick={() => act("send")}>Send now</button>}
        </div>
      </div>
      {err && <div className="error">{err}</div>}

      <div className="card" style={{ marginBottom: 18 }}>
        <h2>Signers</h2>
        <table>
          <thead><tr><th>#</th><th>Signer</th><th>Status</th><th>Sent</th><th>Viewed</th><th>Signed</th><th /></tr></thead>
          <tbody>
            {recipients.map((r) => (
              <tr key={r.id}>
                <td>{r.routing_order}</td>
                <td>{r.name}{r.is_me && <span className="badge" style={{ marginLeft: 6 }}>You</span>}<div className="muted small">{r.email}</div></td>
                <td>{isTurn(r) ? <span className="badge turn">Waiting</span> : <span className={`badge ${r.status}`}>{r.status}</span>}</td>
                <td className="small muted">{fmtDate(r.sent_at)}</td>
                <td className="small muted">{fmtDate(r.viewed_at)}</td>
                <td className="small muted">{fmtDate(r.signed_at)}</td>
                <td style={{ textAlign: "right" }}>
                  {isTurn(r) && (
                    <div className="row" style={{ justifyContent: "flex-end" }}>
                      {r.is_me ? (
                        <button className="btn sm" onClick={async () => { const res = await act("link", r.id); if (res?.link) location.href = res.link; }}>Sign now</button>
                      ) : (
                        <>
                          <button className="btn sm ghost" onClick={() => act("remind", r.id)}>Resend email</button>
                          <button className="btn sm ghost" onClick={() => act("link", r.id)}>Get link</button>
                        </>
                      )}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {Object.entries(links).map(([rid, l]) => {
          const r = recipients.find((x) => x.id === rid);
          if (!r || r.status === "signed") return null;
          return (
            <div key={rid} style={{ marginTop: 10 }}>
              <label>
                Signing link for {r.name} {l.emailed === false && <span className="muted">(email not sent — copy and share this link)</span>}
              </label>
              <div className="copy">
                <input readOnly value={l.link} onFocus={(ev) => ev.target.select()} />
                <button className="btn sm ghost" onClick={() => navigator.clipboard.writeText(l.link)}>Copy</button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="editor">
        <div className="side">
          <div className="card">
            <h3>History</h3>
            {events.map((ev) => {
              const r = recipients.find((x) => x.id === ev.recipient_id);
              return (
                <div key={ev.id} style={{ marginBottom: 8 }}>
                  <div style={{ textTransform: "capitalize" }}>{ev.type.replace(/_/g, " ")}{r ? ` · ${r.name}` : ""}</div>
                  <div className="muted small">{fmtDate(ev.created_at)}{ev.ip ? ` · ${ev.ip}` : ""}</div>
                </div>
              );
            })}
            {e.final_sha256 && <div className="muted small" style={{ wordBreak: "break-all", marginTop: 10 }}>SHA-256: {e.final_sha256}</div>}
          </div>
        </div>
        <PdfPages key={v} src={`/api/envelopes/${id}/pdf?v=${v}`} />
      </div>
    </>
  );
}
