"use client";
import { ROLE_COLORS } from "@/components/FieldBox";

/** Editable list of signers with routing order. Same order number = sign at the same time. */
export default function SignerList({ signers, setSigners, profile, fixedRoles }) {
  const set = (i, p) => setSigners(signers.map((s, j) => (j === i ? { ...s, ...p } : s)));
  const fillMe = (i) => set(i, { name: profile?.data?.full_name || "", email: profile?.data?.email || "", is_me: true });

  return (
    <div>
      {signers.map((s, i) => (
        <div className="row" key={i} style={{ marginBottom: 8, alignItems: "flex-end" }}>
          <div style={{ width: 70 }}>
            {i === 0 && <label>Order</label>}
            <input type="number" min={1} value={s.routing_order} onChange={(e) => set(i, { routing_order: Number(e.target.value) || 1 })} />
          </div>
          <div style={{ width: 8, alignSelf: "stretch", background: ROLE_COLORS[i % ROLE_COLORS.length], borderRadius: 4 }} />
          <div style={{ flex: 1, minWidth: 160 }}>
            {i === 0 && <label>Name</label>}
            <input placeholder={s.roleName || "Full name"} value={s.name} onChange={(e) => set(i, { name: e.target.value, is_me: false })} />
          </div>
          <div style={{ flex: 1, minWidth: 180 }}>
            {i === 0 && <label>Email</label>}
            <input type="email" placeholder="email@example.com" value={s.email} onChange={(e) => set(i, { email: e.target.value, is_me: false })} />
          </div>
          {s.roleName && <span className="badge">{s.roleName}</span>}
          {!s.is_me && <button className="btn sm ghost" onClick={() => fillMe(i)}>Me</button>}
          {s.is_me && <span className="badge signed">You</span>}
          {!fixedRoles && signers.length > 1 && <button className="btn sm ghost" onClick={() => setSigners(signers.filter((_, j) => j !== i))}>✕</button>}
        </div>
      ))}
      {!fixedRoles && (
        <button className="btn sm ghost" onClick={() => setSigners([...signers, { name: "", email: "", routing_order: signers.length + 1 }])}>+ Add signer</button>
      )}
      <div className="help">Lower numbers sign first. Give two people the same number to have them sign at the same time.</div>
    </div>
  );
}
