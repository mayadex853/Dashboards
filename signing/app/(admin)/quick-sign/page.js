"use client";
// Sign a document someone sent you: auto-fill your info, drop your signature, download / email it back.
import { useEffect, useState } from "react";
import { api, fmtDate } from "@/lib/api";
import { PROFILE_FIELDS, FIELD_TYPES, today } from "@/lib/fields";
import { stampPdf, listFormFields } from "@/lib/stamp";
import { autoMatch } from "@/lib/automatch";
import PdfPages from "@/components/PdfPages";
import FieldBox from "@/components/FieldBox";
import SignaturePad from "@/components/SignaturePad";

export default function QuickSign() {
  const [profile, setProfile] = useState(null);
  const [file, setFile] = useState(null);
  const [bytes, setBytes] = useState(null);
  const [formFields, setFormFields] = useState([]);
  const [formValues, setFormValues] = useState({});
  const [fields, setFields] = useState([]);
  const [tool, setTool] = useState(null); // {type, value, label}
  const [sel, setSel] = useState(null);
  const [pad, setPad] = useState(null);
  const [emailTo, setEmailTo] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState(null);
  const [history, setHistory] = useState([]);

  const loadHistory = () => api("/api/quick-sign").then(setHistory);
  useEffect(() => {
    api("/api/profile").then(setProfile);
    loadHistory();
  }, []);

  useEffect(() => {
    const onKey = (e) => {
      if (!sel || ["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement?.tagName)) return;
      if (e.key === "Delete" || e.key === "Backspace") { setFields((fs) => fs.filter((f) => f.id !== sel)); setSel(null); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [sel]);

  const data = profile?.data || {};

  // If the profile arrives after the PDF was opened, fill any still-empty form fields
  useEffect(() => {
    if (!profile || !formFields.length) return;
    setFormValues((cur) => {
      const vals = { ...cur };
      for (const x of formFields) if (x.kind === "text" && !vals[x.name]) { const v = autoMatch(x.name, profile.data || {}); if (v) vals[x.name] = v; }
      return vals;
    });
  }, [profile, formFields]);

  const allChips = [
    ...PROFILE_FIELDS.filter((f) => data[f.key]).map((f) => ({ type: "text", value: data[f.key], label: f.label })),
    ...(data.city ? [{ type: "text", value: [data.city, [data.state, data.postal_code].filter(Boolean).join(" ")].filter(Boolean).join(", "), label: "City, State ZIP" }] : []),
    ...Object.entries(data).filter(([k]) => !PROFILE_FIELDS.some((f) => f.key === k)).map(([k, v]) => ({ type: "text", value: v, label: k.replace(/_/g, " ") })),
  ];
  const chips = allChips.filter((c, i) => c.value && allChips.findIndex((x) => x.value === c.value) === i);

  const open = async (f) => {
    if (!f) return;
    const b = new Uint8Array(await f.arrayBuffer());
    setFile(f);
    setBytes(b);
    setFields([]);
    setMsg(null);
    try {
      const ff = await listFormFields(b);
      setFormFields(ff);
      const vals = {};
      for (const x of ff) if (x.kind === "text") { const v = autoMatch(x.name, data); if (v) vals[x.name] = v; }
      setFormValues(vals);
    } catch {
      setFormFields([]);
    }
  };

  const place = (page, fx, fy) => {
    if (!tool) return setSel(null);
    if ((tool.type === "signature" || tool.type === "initials") && !profile?.[tool.type]) {
      setPad({ type: tool.type, then: { page, fx, fy } });
      return;
    }
    addField(tool, page, fx, fy);
  };
  const addField = (t, page, fx, fy, img) => {
    const def = FIELD_TYPES.find((x) => x.type === t.type) || FIELD_TYPES[3];
    let w = def.w;
    if (t.type === "text") w = Math.min(0.6, Math.max(0.08, String(t.value).length * 0.0105));
    const value = t.type === "signature" || t.type === "initials" ? img || profile[t.type] : t.type === "date" ? today() : t.type === "checkbox" ? true : t.value;
    const f = { id: Math.random().toString(36).slice(2, 10), type: t.type === "date" ? "text" : t.type, page, x: Math.min(fx, 1 - w), y: Math.max(0, Math.min(fy - def.h / 2, 1 - def.h)), w, h: def.h, value, role: 0 };
    setFields((fs) => [...fs, f]);
    setSel(f.id);
  };
  const patch = (id, p) => setFields((fs) => fs.map((f) => (f.id === id ? { ...f, ...p } : f)));
  const selected = fields.find((f) => f.id === sel);

  const finish = async () => {
    setBusy(true);
    setMsg(null);
    try {
      const out = await stampPdf(bytes, fields, { fillForm: formValues, flattenForm: true });
      const title = file.name.replace(/\.pdf$/i, "") + " - signed";
      // download locally
      const url = URL.createObjectURL(new Blob([out], { type: "application/pdf" }));
      const a = document.createElement("a");
      a.href = url;
      a.download = `${title}.pdf`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 5000);
      // keep a copy + optionally email
      const form = new FormData();
      form.append("file", new Blob([out], { type: "application/pdf" }), `${title}.pdf`);
      form.append("title", title);
      form.append("email_to", emailTo);
      const res = await api("/api/quick-sign", { method: "POST", form });
      setMsg({ ok: true, text: `Downloaded and saved${emailTo ? (res.emailed ? `, emailed to ${emailTo}` : " (email not sent: Microsoft 365 isn't configured)") : ""}.` });
      loadHistory();
    } catch (e) {
      setMsg({ ok: false, text: e.message });
    }
    setBusy(false);
  };

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Quick Sign</h1>
          <div className="muted">Upload a form someone sent you, fill in your info with a click, sign, send it back.</div>
        </div>
        <div className="actions">
          <label className="btn ghost" style={{ margin: 0 }}>
            {file ? "Open another PDF" : "Upload PDF"}
            <input type="file" accept="application/pdf" hidden onChange={(e) => open(e.target.files[0])} />
          </label>
        </div>
      </div>

      {!bytes ? (
        <>
          <label className="card center-box" style={{ minHeight: 220, cursor: "pointer", borderStyle: "dashed", flexDirection: "column" }}
            onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); open(e.dataTransfer.files[0]); }}>
            <b>Drop a PDF here or click to upload</b>
            <span className="muted small">Fillable forms are auto-filled from your saved info.</span>
            <input type="file" accept="application/pdf" hidden onChange={(e) => open(e.target.files[0])} />
          </label>
          {profile && !profile.signature && <div className="hint" style={{ marginTop: 12 }}>Tip: save your signature under <a href="/profile">My info & signature</a> so it drops in with one click.</div>}
          {history.length > 0 && (
            <div className="card" style={{ marginTop: 20 }}>
              <h2>Recently signed</h2>
              <table>
                <tbody>
                  {history.map((h) => (
                    <tr key={h.id}>
                      <td>{h.title}</td>
                      <td className="muted small">{h.emailed_to ? `Emailed to ${h.emailed_to}` : ""}</td>
                      <td className="muted small">{fmtDate(h.created_at)}</td>
                      <td style={{ textAlign: "right" }}><a className="btn sm ghost" href={`/api/quick-sign/${h.id}/pdf`}>Download</a></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      ) : (
        <div className="editor">
          <div className="side stack">
            <div className="card">
              <h3>Click a value, then click the page</h3>
              <div className="palette" style={{ marginBottom: 10 }}>
                {[{ type: "signature", label: "Signature" }, { type: "initials", label: "Initials" }, { type: "date", label: "Today's date" }, { type: "checkbox", label: "✕ Check" }].map((t) => (
                  <button key={t.type} className={`chip ${tool?.type === t.type ? "on" : ""}`} onClick={() => setTool(tool?.type === t.type ? null : t)}>{t.label}</button>
                ))}
              </div>
              <div className="chips">
                {chips.map((c, i) => (
                  <button key={i} title={c.label} className={`chip ${tool?.label === c.label ? "on" : ""}`} onClick={() => setTool(tool?.label === c.label ? null : c)}>{c.value}</button>
                ))}
                <button className={`chip ${tool?.label === "Custom" ? "on" : ""}`} onClick={() => setTool({ type: "text", value: "Text", label: "Custom" })}>+ Custom text</button>
              </div>
              {!chips.length && <div className="help">Add your details under My info to get one-click values here.</div>}
              {tool && <div className="hint" style={{ marginTop: 10 }}>Click where it goes. Keep clicking to place it again.</div>}
            </div>

            {selected && selected.type === "text" && (
              <div className="card">
                <h3>Selected text</h3>
                <input value={selected.value} onChange={(e) => patch(selected.id, { value: e.target.value })} />
                <div className="row end"><button className="btn sm danger" onClick={() => { setFields(fields.filter((f) => f.id !== sel)); setSel(null); }}>Remove</button></div>
              </div>
            )}
            {selected && selected.type !== "text" && (
              <div className="card row" style={{ justifyContent: "space-between" }}>
                <span className="muted">Drag to move, corner to resize</span>
                <button className="btn sm danger" onClick={() => { setFields(fields.filter((f) => f.id !== sel)); setSel(null); }}>Remove</button>
              </div>
            )}

            {formFields.length > 0 && (
              <div className="card">
                <h3>Form fields ({formFields.length})</h3>
                <div className="row" style={{ marginBottom: 10 }}>
                  <button className="btn sm" onClick={() => {
                    const vals = { ...formValues };
                    for (const x of formFields) if (x.kind === "text") { const v = autoMatch(x.name, data); if (v) vals[x.name] = v; }
                    setFormValues(vals);
                  }}>Fill from my info</button>
                  <span className="muted small">{Object.keys(formValues).length} filled</span>
                </div>
                <div style={{ maxHeight: 340, overflow: "auto" }}>
                  {formFields.map((x) => (
                    <div className="field" key={x.name} style={{ marginBottom: 8 }}>
                      <label className="small" title={x.name}>{x.name}</label>
                      {x.kind === "checkbox" ? (
                        <input type="checkbox" checked={!!formValues[x.name]} onChange={(e) => setFormValues({ ...formValues, [x.name]: e.target.checked })} />
                      ) : (
                        <input value={formValues[x.name] || ""} onChange={(e) => setFormValues({ ...formValues, [x.name]: e.target.value })} />
                      )}
                    </div>
                  ))}
                </div>
                <div className="help">Values are written into the form when you finish. Signature boxes: place your signature on the page.</div>
              </div>
            )}

            <div className="card">
              <h3>Finish</h3>
              <label>Email signed copy to (optional)</label>
              <input placeholder="them@company.com" value={emailTo} onChange={(e) => setEmailTo(e.target.value)} />
              <div className="row end"><button className="btn" disabled={busy} onClick={finish}>{busy ? "Working…" : "Download signed PDF"}</button></div>
              {msg && <div className={msg.ok ? "success" : "error"}>{msg.text}</div>}
            </div>
          </div>

          <PdfPages
            src={bytes}
            onPageClick={place}
            overlay={(page, size) =>
              fields.filter((f) => f.page === page).map((f) => (
                <FieldBox key={f.id} field={f} size={size} editable color="#3987e5" className="filled" selected={sel === f.id} onSelect={() => setSel(f.id)} onChange={(p) => patch(f.id, p)}>
                  {f.type === "signature" || f.type === "initials" ? <img src={f.value} alt="" /> :
                    f.type === "checkbox" ? <b style={{ margin: "auto", color: "#111a40" }}>X</b> :
                    <span className="val" style={{ fontSize: Math.min(f.h * size.height * 0.72, 12 * size.scale) }}>{f.value}</span>}
                </FieldBox>
              ))
            }
          />
        </div>
      )}

      {pad && (
        <SignaturePad
          kind={pad.type}
          defaultName={data.full_name || ""}
          onCancel={() => setPad(null)}
          onDone={async (png) => {
            const saved = await api("/api/profile", { method: "PUT", body: { [pad.type]: png } });
            setProfile(saved);
            const { page, fx, fy } = pad.then;
            setPad(null);
            addField({ type: pad.type }, page, fx, fy, png);
          }}
        />
      )}
    </>
  );
}
