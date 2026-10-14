"use client";
import { use, useEffect, useMemo, useState } from "react";
import PdfPages from "@/components/PdfPages";
import FieldBox from "@/components/FieldBox";
import SignaturePad from "@/components/SignaturePad";
import { today } from "@/lib/fields";

export default function SignerPage({ params }) {
  const { token } = use(params);
  const [info, setInfo] = useState(null);
  const [err, setErr] = useState("");
  const [values, setValues] = useState({});
  const [consent, setConsent] = useState(false);
  const [adopted, setAdopted] = useState({ signature: null, initials: null });
  const [pad, setPad] = useState(null); // field awaiting signature
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(null);

  useEffect(() => {
    fetch(`/api/public/sign/${token}`)
      .then(async (r) => {
        const j = await r.json();
        if (!r.ok) throw new Error(j.error);
        setInfo(j);
        const init = {};
        for (const f of j.fields) if (f.value && f.type === "text") init[f.id] = f.value;
        setValues(init);
        if (j.saved) setAdopted({ signature: j.saved.signature, initials: j.saved.initials });
      })
      .catch((e) => setErr(e.message));
  }, [token]);

  const fields = info?.fields || [];
  const isFilled = (f) => f.type === "date" || f.type === "checkbox" || !!values[f.id];
  const remaining = useMemo(() => fields.filter((f) => f.required !== false && !isFilled(f)), [fields, values]); // eslint-disable-line react-hooks/exhaustive-deps

  const clickSig = (f) => {
    if (!consent) return;
    if (values[f.id]) return setPad(f);
    if (adopted[f.type]) setValues((v) => ({ ...v, [f.id]: adopted[f.type] }));
    else setPad(f);
  };

  const goNext = () => {
    const f = remaining[0];
    if (!f) return;
    document.querySelector(`[data-fid="${f.id}"]`)?.scrollIntoView({ behavior: "smooth", block: "center" });
  };

  const finish = async (action = "sign", reason) => {
    setErr("");
    setBusy(true);
    try {
      const r = await fetch(`/api/public/sign/${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, consent, values, reason, localDate: today() }),
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j.error);
      setDone(action);
    } catch (e) {
      setErr(e.message);
    }
    setBusy(false);
  };

  if (done)
    return (
      <div className="public">
        <div className="center-box">
          <div className="card narrow">
            <h1>{done === "sign" ? "You're done!" : "Declined"}</h1>
            <p className="muted">
              {done === "sign" ? "Thanks for signing. You'll get a copy by email once everyone has signed." : `We've let ${info.sender} know.`}
            </p>
          </div>
        </div>
      </div>
    );
  if (err && !info)
    return (
      <div className="public">
        <div className="center-box"><div className="card narrow"><h2>Unable to open document</h2><p className="muted">{err}</p></div></div>
      </div>
    );
  if (!info) return <div className="public"><div className="center-box muted">Loading…</div></div>;
  if (info.signer.status === "signed")
    return <div className="public"><div className="center-box"><div className="card narrow"><h2>Already signed</h2><p className="muted">You've already signed this document.</p></div></div></div>;
  if (!info.turn)
    return <div className="public"><div className="center-box"><div className="card narrow"><h2>Not your turn yet</h2><p className="muted">Someone earlier in the signing order still needs to sign. We'll email you when it's ready.</p></div></div></div>;

  return (
    <div className="public">
      <div className="topbar">
        <div>
          <b>{info.title}</b>
          <div className="who">From {info.sender} · Signing as {info.signer.name}</div>
        </div>
        <div className="grow" />
        {consent && remaining.length > 0 && <button className="btn ghost" style={{ color: "#333" }} onClick={goNext}>Next field ({remaining.length})</button>}
        <button className="btn" disabled={!consent || remaining.length > 0 || busy} onClick={() => finish("sign")}>
          {busy ? "Finishing…" : "Finish"}
        </button>
      </div>
      <div className="content">
        {info.message && <div className="card" style={{ marginBottom: 14 }}>{info.message}</div>}
        <div className="card" style={{ marginBottom: 18 }}>
          <label className="consent">
            <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
            <span>
              I agree to use electronic records and signatures, and that my electronic signature is the legal equivalent of my handwritten signature on this document.
            </span>
          </label>
          <div className="row" style={{ marginTop: 10, justifyContent: "space-between" }}>
            <span className="muted small">{consent ? "Click each highlighted field to complete it." : "Check the box to start signing."}</span>
            <button className="link small" onClick={() => { const reason = prompt("Reason for declining (optional):"); if (reason !== null) finish("decline", reason); }}>Decline to sign</button>
          </div>
        </div>
        {err && <div className="error">{err}</div>}

        <PdfPages
          src={`/api/public/sign/${token}/pdf`}
          overlay={(page, size) =>
            fields
              .filter((f) => f.page === page)
              .map((f) => {
                const val = values[f.id];
                const need = consent && f.required !== false && !isFilled(f);
                return (
                  <FieldBox key={f.id} field={f} size={size} color="#d97706" className={`${val || f.type === "date" ? "filled" : ""} ${need ? "need" : ""}`} onSelect={() => (f.type === "signature" || f.type === "initials" ? clickSig(f) : null)}>
                      {f.type === "signature" || f.type === "initials" ? (
                        val ? <img src={val} alt="" /> : <span className="lbl">{f.type === "signature" ? "Sign here" : "Initial"}</span>
                      ) : f.type === "date" ? (
                        <span className="val" style={{ fontSize: Math.min(f.h * size.height * 0.7, 13) }}>{today()}</span>
                      ) : f.type === "checkbox" ? (
                        <span
                          style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, color: "#111a40" }}
                          onClick={() => consent && setValues((v) => ({ ...v, [f.id]: !v[f.id] }))}
                        >
                          {val ? "X" : ""}
                        </span>
                      ) : (
                        <input
                          className="inline"
                          disabled={!consent}
                          placeholder={f.label}
                          style={{ fontSize: Math.min(f.h * size.height * 0.7, 13) }}
                          value={val || ""}
                          onPointerDown={(e) => e.stopPropagation()}
                          onChange={(e) => setValues((v) => ({ ...v, [f.id]: e.target.value }))}
                        />
                      )}
                    </FieldBox>
                );
              })
          }
        />
      </div>
      {pad && (
        <SignaturePad
          kind={pad.type}
          defaultName={info.signer.name}
          onCancel={() => setPad(null)}
          onDone={(png) => {
            setAdopted((a) => ({ ...a, [pad.type]: png }));
            // apply to every empty field of the same kind at once
            setValues((v) => {
              const n = { ...v, [pad.id]: png };
              for (const f of fields) if (f.type === pad.type && !n[f.id]) n[f.id] = png;
              return n;
            });
            setPad(null);
          }}
        />
      )}
    </div>
  );
}
