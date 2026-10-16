"use client";
// Signer experience, modeled on DocuSign: review banner → Continue → guided "Start/Next" tags → Finish.
import { use, useEffect, useMemo, useState } from "react";
import PdfPages from "@/components/PdfPages";
import FieldBox from "@/components/FieldBox";
import SignaturePad from "@/components/SignaturePad";
import { today } from "@/lib/fields";

const isSig = (f) => f.type === "signature" || f.type === "initials";

export default function SignerPage({ params }) {
  const { token } = use(params);
  const [info, setInfo] = useState(null);
  const [err, setErr] = useState("");
  const [values, setValues] = useState({});
  const [agree, setAgree] = useState(false);
  const [started, setStarted] = useState(false);
  const [adopted, setAdopted] = useState(null); // {signature, initials}
  const [pad, setPad] = useState(null); // field waiting for a signature
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(null);
  const [menu, setMenu] = useState(false);

  useEffect(() => {
    fetch(`/api/public/sign/${token}`)
      .then(async (r) => {
        const j = await r.json();
        if (!r.ok) throw new Error(j.error);
        setInfo(j);
        const init = {};
        for (const f of j.fields) {
          if (f.type === "name") init[f.id] = f.value || j.signer.name;
          else if (f.type === "email") init[f.id] = f.value || j.signer.email;
          else if (f.value && !isSig(f) && f.type !== "checkbox") init[f.id] = f.value;
        }
        setValues(init);
        if (j.saved?.signature) setAdopted({ signature: j.saved.signature, initials: j.saved.initials });
      })
      .catch((e) => setErr(e.message));
  }, [token]);

  const fields = useMemo(() => (info?.fields || []).slice().sort((a, b) => a.page - b.page || a.y - b.y || a.x - b.x), [info]);
  const isFilled = (f) => f.type === "date" || f.type === "checkbox" || !!values[f.id];
  const remaining = fields.filter((f) => f.required !== false && !isFilled(f));
  const next = remaining[0];

  const scrollTo = (f) => document.querySelector(`[data-fid="${f.id}"]`)?.scrollIntoView({ behavior: "smooth", block: "center" });
  const act = (f) => {
    if (!started) return;
    if (isSig(f)) {
      const img = adopted?.[f.type];
      if (img && !values[f.id]) setValues((v) => ({ ...v, [f.id]: img }));
      else setPad(f);
    } else if (f.type === "checkbox") {
      setValues((v) => ({ ...v, [f.id]: !v[f.id] }));
    } else {
      document.querySelector(`[data-fid="${f.id}"] input`)?.focus();
    }
  };
  const goNext = () => {
    if (!next) return;
    scrollTo(next);
    setTimeout(() => act(next), 350);
  };

  const submit = async (action = "sign", reason) => {
    setErr("");
    setBusy(true);
    try {
      const r = await fetch(`/api/public/sign/${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, consent: agree, values, reason, localDate: today() }),
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j.error);
      setDone(action);
    } catch (e) {
      setErr(e.message);
    }
    setBusy(false);
  };

  const Brand = () => (
    <div className="row" style={{ gap: 8, fontWeight: 700, fontSize: 16 }}>
      <span style={{ width: 24, height: 24, borderRadius: 6, background: "var(--primary)", color: "#fff", display: "grid", placeItems: "center", fontSize: 13 }}>T</span>
      TakaSign
    </div>
  );
  const Message = ({ title, children, download }) => (
    <div className="public">
      <div className="topbar"><Brand /></div>
      <div className="center-box">
        <div className="card narrow" style={{ padding: 32 }}>
          <h1>{title}</h1>
          <p className="muted" style={{ marginBottom: download ? 18 : 0 }}>{children}</p>
          {download && <a className="btn yellow" href={`/api/public/sign/${token}/pdf`} target="_blank" rel="noreferrer">Download a copy</a>}
        </div>
      </div>
    </div>
  );

  if (done === "sign") return <Message title="You're done signing" download>Thanks for signing. You'll get the completed document by email once everyone has signed.</Message>;
  if (done === "decline") return <Message title="You declined to sign">We've let {info.sender} know.</Message>;
  if (err && !info) return <Message title="Unable to open document">{err}</Message>;
  if (!info) return <div className="public"><div className="center-box muted">Loading document…</div></div>;
  if (info.signer.status === "signed") return <Message title="Already signed" download>You've already signed this document.</Message>;
  if (!info.turn) return <Message title="Not your turn yet">Someone earlier in the signing order still needs to sign. We'll email you when it's ready for you.</Message>;

  return (
    <div className="public">
      <div className="topbar">
        <Brand />
        <div style={{ minWidth: 0 }}>
          <b style={{ display: "block", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{info.title}</b>
          <div className="who">From {info.sender} · Signing as {info.signer.name}</div>
        </div>
        <div className="grow" />
        {started && (
          <button className="btn yellow" disabled={remaining.length > 0 || busy} onClick={() => submit("sign")} title={remaining.length ? `${remaining.length} required field(s) left` : ""}>
            {busy ? "Finishing…" : "Finish"}
          </button>
        )}
        <div style={{ position: "relative" }}>
          <button className="btn ghost" onClick={() => setMenu(!menu)}>Other actions ▾</button>
          {menu && (
            <div className="card" style={{ position: "absolute", right: 0, top: 44, padding: 6, minWidth: 180, zIndex: 30 }}>
              <button className="link" style={{ display: "block", padding: "8px 10px", color: "var(--ink)" }} onClick={() => { setMenu(false); window.open(`/api/public/sign/${token}/pdf`, "_blank"); }}>Download document</button>
              <button className="link" style={{ display: "block", padding: "8px 10px", color: "var(--bad)" }} onClick={() => { setMenu(false); const reason = prompt("Why are you declining to sign? (optional)"); if (reason !== null) submit("decline", reason); }}>Decline to sign</button>
            </div>
          )}
        </div>
      </div>

      {!started ? (
        <div className="banner">
          <div style={{ flex: 1, minWidth: 260 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Please review and act on these documents.</div>
            <label className="consent">
              <input type="checkbox" checked={agree} onChange={(e) => setAgree(e.target.checked)} />
              <span>I agree to use electronic records and signatures, and that my electronic signature is the legal equivalent of my handwritten signature.</span>
            </label>
          </div>
          <button className="btn yellow" disabled={!agree} onClick={() => { setStarted(true); setTimeout(() => fields[0] && scrollTo(remaining[0] || fields[0]), 100); }}>Continue</button>
        </div>
      ) : (
        <div className="banner" style={{ background: remaining.length ? "#26262f" : "#14532d" }}>
          <div style={{ flex: 1 }}>
            {remaining.length
              ? `${remaining.length} required field${remaining.length === 1 ? "" : "s"} left. Use the yellow tags to go field by field.`
              : "All required fields are complete. Select Finish to sign."}
          </div>
          {remaining.length > 0 && <button className="btn yellow sm" onClick={goNext}>Next field</button>}
        </div>
      )}

      <div className="content">
        {info.message && <div className="card" style={{ marginBottom: 14 }}>{info.message}</div>}
        {err && <div className="error">{err}</div>}
        <PdfPages
          src={`/api/public/sign/${token}/pdf`}
          overlay={(page, size) => (
            <>
              {started && next && next.page === page && (
                <button className="start-arrow" style={{ top: (next.y + next.h / 2) * size.height }} onClick={goNext}>
                  {remaining.length === fields.filter((f) => f.required !== false).length ? "START" : "NEXT"}
                </button>
              )}
              {fields
                .filter((f) => f.page === page)
                .map((f) => {
                  const val = values[f.id];
                  const need = started && f.required !== false && !isFilled(f);
                  const fontSize = Math.min(f.h * size.height * 0.7, 13);
                  return (
                    <FieldBox key={f.id} field={f} size={size} className={`sign-tag ${val || f.type === "date" ? "filled" : ""} ${need ? "need" : ""}`} onSelect={() => act(f)}>
                      {isSig(f) ? (
                        val ? <img src={val} alt="" /> : <span className="lbl">{f.type === "signature" ? "Sign ⬇" : "Initial ⬇"}</span>
                      ) : f.type === "date" ? (
                        <span className="val" style={{ fontSize }}>{today()}</span>
                      ) : f.type === "checkbox" ? (
                        <span style={{ margin: "auto", fontWeight: 700, color: "#111a40" }}>{val ? "✕" : ""}</span>
                      ) : (
                        <input
                          className="inline"
                          disabled={!started}
                          placeholder={f.label}
                          style={{ fontSize }}
                          value={val || ""}
                          onPointerDown={(e) => e.stopPropagation()}
                          onChange={(e) => setValues((v) => ({ ...v, [f.id]: e.target.value }))}
                        />
                      )}
                    </FieldBox>
                  );
                })}
            </>
          )}
        />
      </div>

      {pad && (
        <SignaturePad
          defaultName={info.signer.name}
          onCancel={() => setPad(null)}
          onDone={({ signature, initials }) => {
            setAdopted({ signature, initials });
            setValues((v) => ({ ...v, [pad.id]: pad.type === "signature" ? signature : initials }));
            setPad(null);
          }}
        />
      )}
    </div>
  );
}
