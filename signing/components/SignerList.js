"use client";
// DocuSign-style recipients: optional signing order, reorder with arrows, and
// "Needs to sign" vs "Receives a copy" (CC gets the completed PDF).
import { useState } from "react";
import { ROLE_COLORS } from "@/components/FieldBox";

export const isCc = (s) => s.kind === "cc";

/**
 * @param {{signers: any[], setSigners: Function, profile: any, fixedRoles?: boolean}} props
 *   fixedRoles: signer rows come from a template (can't remove or turn into copies; copies can still be added)
 */
export default function SignerList({ signers, setSigners, profile, fixedRoles }) {
  const signerRows = signers.map((s, i) => ({ s, i })).filter(({ s }) => !isCc(s));
  const ccRows = signers.map((s, i) => ({ s, i })).filter(({ s }) => isCc(s));
  const [ordered, setOrdered] = useState(true);

  const sorted = [...signerRows].sort((a, b) => a.s.routing_order - b.s.routing_order || a.i - b.i);
  const set = (i, p) => setSigners(signers.map((s, j) => (j === i ? { ...s, ...p } : s)));
  const fillMe = (i) => set(i, { name: profile?.data?.full_name || "", email: profile?.data?.email || "", is_me: true });
  const signerIndex = (i) => signerRows.findIndex((r) => r.i === i); // stable color per signer

  // Renumber signers 1..n following the given display order
  const renumber = (rows) => {
    const next = signers.slice();
    rows.forEach(({ i }, n) => (next[i] = { ...next[i], routing_order: n + 1 }));
    setSigners(next);
  };
  const move = (pos, dir) => {
    const rows = sorted.slice();
    const to = pos + dir;
    if (to < 0 || to >= rows.length) return;
    [rows[pos], rows[to]] = [rows[to], rows[pos]];
    renumber(rows);
  };
  const toggleOrder = (on) => {
    setOrdered(on);
    if (on) renumber(sorted);
    else setSigners(signers.map((s) => (isCc(s) ? s : { ...s, routing_order: 1 })));
  };
  const add = (kind) => {
    const maxOrder = Math.max(0, ...signerRows.map(({ s }) => s.routing_order));
    setSigners([...signers, { name: "", email: "", kind, routing_order: kind === "cc" ? 99 : ordered ? maxOrder + 1 : 1 }]);
  };

  // Plain render function (not a component) so inputs keep focus while typing
  const renderRow = ({ s, i }, pos) => {
    const cc = isCc(s);
    const color = cc ? "#9a9aa6" : ROLE_COLORS[signerIndex(i) % ROLE_COLORS.length];
    const locked = fixedRoles && s.role_index !== undefined && !cc; // template signer
    return (
      <div key={i} className="card" style={{ padding: 12, marginBottom: 8, borderLeft: `4px solid ${color}`, boxShadow: "none" }}>
        <div className="row" style={{ alignItems: "flex-end" }}>
          {!cc && ordered && (
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <input
                aria-label="Signing order"
                type="number"
                min={1}
                value={s.routing_order}
                onChange={(e) => set(i, { routing_order: Math.max(1, Number(e.target.value) || 1) })}
                style={{ width: 54, textAlign: "center", fontWeight: 600 }}
              />
              <div style={{ display: "flex", flexDirection: "column" }}>
                <button className="link small" title="Move up" disabled={pos === 0} onClick={() => move(pos, -1)}>▲</button>
                <button className="link small" title="Move down" disabled={pos === sorted.length - 1} onClick={() => move(pos, 1)}>▼</button>
              </div>
            </div>
          )}
          <div style={{ flex: 1, minWidth: 150 }}>
            <label>Name</label>
            <input placeholder={s.roleName || "Full name"} value={s.name} onChange={(e) => set(i, { name: e.target.value, is_me: false })} />
          </div>
          <div style={{ flex: 1, minWidth: 180 }}>
            <label>Email</label>
            <input type="email" placeholder="email@example.com" value={s.email} onChange={(e) => set(i, { email: e.target.value, is_me: false })} />
          </div>
          <div style={{ width: 170 }}>
            <label>Action</label>
            <select
              value={cc ? "cc" : "signer"}
              disabled={locked}
              onChange={(e) => set(i, { kind: e.target.value, routing_order: e.target.value === "cc" ? 99 : Math.max(0, ...signerRows.map((r) => r.s.routing_order)) + 1 })}
            >
              <option value="signer">Needs to sign</option>
              <option value="cc">Receives a copy</option>
            </select>
          </div>
          {!s.is_me ? <button className="btn sm ghost" onClick={() => fillMe(i)} title="Fill with your details">Me</button> : <span className="badge signed">You</span>}
          {!locked && signers.length > 1 && (
            <button className="btn sm ghost" title="Remove" onClick={() => setSigners(signers.filter((_, j) => j !== i))}>✕</button>
          )}
        </div>
        {(s.roleName || cc) && (
          <div className="small muted" style={{ marginTop: 6 }}>
            {s.roleName && <span className="badge" style={{ marginRight: 6 }}>{s.roleName}</span>}
            {cc && "Gets a copy of the completed, signed document. No signature needed."}
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      <label className="row" style={{ gap: 8, marginBottom: 12, fontSize: 14, color: "var(--ink)" }}>
        <input type="checkbox" checked={ordered} onChange={(e) => toggleOrder(e.target.checked)} />
        Set signing order
        <span className="muted small" style={{ fontWeight: 400 }}>
          {ordered ? "Recipients sign one after another (1 first). Same number = sign at the same time." : "Everyone receives it at once and can sign in any order."}
        </span>
      </label>
      {sorted.map((r, pos) => renderRow(r, pos))}
      {ccRows.map((r) => renderRow(r))}
      <div className="row" style={{ marginTop: 4 }}>
        {!fixedRoles && <button className="btn sm ghost" onClick={() => add("signer")}>+ Add signer</button>}
        <button className="btn sm ghost" onClick={() => add("cc")}>+ Add copy recipient (CC)</button>
      </div>
    </div>
  );
}
