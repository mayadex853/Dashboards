"use client";
// Sign a document someone sent you: drag your saved info and signature onto it,
// auto-fill fillable forms, then download or email it back.
import { useEffect, useState } from "react";
import { api, fmtDate } from "@/lib/api";
import { PROFILE_FIELDS, FIELD_TYPES, today } from "@/lib/fields";
import { stampPdf, listFormFields } from "@/lib/stamp";
import { autoMatch } from "@/lib/automatch";
import PdfPages from "@/components/PdfPages";
import FieldBox from "@/components/FieldBox";
import SignaturePad from "@/components/SignaturePad";
import { startPaletteDrag } from "@/components/dragPlace";
import { toast } from "@/components/Toast";

const uid = () => Math.random().toString(36).slice(2, 10);
const size = (type) => FIELD_TYPES.find((x) => x.type === type) || FIELD_TYPES.find((x) => x.type === "text");

export default function QuickSign() {
  const [profile, setProfile] = useState(null);
  const [file, setFile] = useState(null);
  const [bytes, setBytes] = useState(null);
  const [formFields, setFormFields] = useState([]);
  const [formValues, setFormValues] = useState({});
  const [fields, setFields] = useState([]);
  const [tool, setTool] = useState(null); // palette item armed for click-to-place
  const [sel, setSel] = useState(null);
  const [pad, setPad] = useState(null); // {item, page, fx, fy} waiting for a signature
  const [emailTo, setEmailTo] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState(null);
  const [history, setHistory] = useState([]);

  const loadHistory = () => api("/api/quick-sign").then(setHistory).catch(() => {});
  useEffect(() => {
    api("/api/profile").then(setProfile).catch((e) => { setProfile({ data: {} }); toast(e.message, true); });
    loadHistory();
  }, []);

  useEffect(() => {
    const onKey = (e) => {
      if (["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement?.tagName)) return;
      if (sel && (e.key === "Delete" || e.key === "Backspace")) { setFields((fs) => fs.filter((f) => f.id !== sel)); setSel(null); }
      if (e.key === "Escape") { setTool(null); setSel(null); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [sel]);

  const data = profile?.data || {};

  // Fill fillable-form fields from your info (also when the profile loads after the PDF)
  useEffect(() => {
    if (!profile || !formFields.length) return;
    setFormValues((cur) => {
      const vals = { ...cur };
      for (const x of formFields) if (x.kind === "text" && !vals[x.name]) { const v = autoMatch(x.name, profile.data || {}); if (v) vals[x.name] = v; }
      return vals;
    });
  }, [profile, formFields]);

  const cityLine = [data.city, [data.state, data.postal_code].filter(Boolean).join(" ")].filter(Boolean).join(", ");
  const valueItems = [
    ...PROFILE_FIELDS.filter((f) => data[f.key]).map((f) => ({ type: "text", value: data[f.key], label: f.label })),
    ...(cityLine && cityLine !== data.city ? [{ type: "text", value: cityLine, label: "City, State ZIP" }] : []),
    ...Object.entries(data).filter(([k, v]) => v && !PROFILE_FIELDS.some((f) => f.key === k)).map(([k, v]) => ({ type: "text", value: v, label: k.replace(/_/g, " ") })),
  ].filter((c, i, all) => all.findIndex((x) => x.value === c.value) === i);
  const baseItems = [
    { type: "signature", label: "Signature", icon: "✍" },
    { type: "initials", label: "Initials", icon: "AB" },
    { type: "date", label: "Date", icon: "📅", value: today() },
    { type: "checkbox", label: "Check mark", icon: "✕" },
    { type: "text", label: "Custom text", icon: "Aa", value: "", custom: true },
  ];

  const open = async (f) => {
    if (!f) return;
    if (f.type && f.type !== "application/pdf") return toast("Please choose a PDF file", true);
    const b = new Uint8Array(await f.arrayBuffer());
    setFile(f);
    setBytes(b);
    setFields([]);
    setSel(null);
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

  const place = (item, page, fx, fy, img) => {
    if ((item.type === "signature" || item.type === "initials") && !img && !profile?.[item.type]) {
      setPad({ item, page, fx, fy });
      return;
    }
    const def = size(item.type === "date" ? "date" : item.type);
    let w = def.w;
    if (item.type === "text") w = Math.min(0.6, Math.max(0.1, String(item.value || "Text").length * 0.011));
    const value =
      item.type === "signature" || item.type === "initials" ? img || profile[item.type] :
      item.type === "checkbox" ? true :
      item.custom ? "" : item.value;
    const f = { id: uid(), type: item.type === "date" ? "text" : item.type, page, x: clamp(fx - 0.005, 0, 1 - w), y: clamp(fy - def.h / 2, 0, 1 - def.h), w, h: def.h, value, role: 0 };
    setFields((fs) => [...fs, f]);
    setSel(f.id);
    if (item.custom) setTimeout(() => document.getElementById("qs-text")?.focus(), 50);
  };
  const patch = (id, p) => setFields((fs) => fs.map((f) => (f.id === id ? { ...f, ...p } : f)));
  const selected = fields.find((f) => f.id === sel);

  const paletteProps = (item) => ({
    className: `pitem ${tool === item ? "on" : ""}`,
    onPointerDown: (e) =>
      startPaletteDrag(e, {
        label: item.value && item.type === "text" ? item.value : item.label,
        onDrop: (page, fx, fy) => place(item, page, fx, fy),
        onClick: () => setTool(tool === item ? null : item),
      }),
  });

  const finish = async () => {
    setBusy(true);
    setMsg(null);
    try {
      const out = await stampPdf(bytes, fields, { fillForm: formValues, flattenForm: true });
      const title = file.name.replace(/\.pdf$/i, "") + " - signed";
      const url = URL.createObjectURL(new Blob([out], { type: "application/pdf" }));
      const a = document.createElement("a");
      a.href = url;
      a.download = `${title}.pdf`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 5000);
      // Keep a copy and optionally email it. The download above works even if this fails.
      try {
        const form = new FormData();
        form.append("file", new Blob([out], { type: "application/pdf" }), `${title}.pdf`);
        form.append("title", title);
        form.append("email_to", emailTo);
        const res = await api("/api/quick-sign", { method: "POST", form });
        setMsg({ ok: true, text: `Downloaded and saved to your history${emailTo ? (res.emailed ? `, and emailed to ${emailTo}` : ". Email wasn't sent because Microsoft 365 isn't connected yet") : ""}.` });
        loadHistory();
      } catch (e) {
        setMsg({ ok: false, text: `Downloaded, but couldn't save a copy: ${e.message}` });
      }
    } catch (e) {
      setMsg({ ok: false, text: e.message });
    }
    setBusy(false);
  };

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Sign a document</h1>
          <div className="muted">Upload a form someone sent you, drag your info and signature onto it, and send it back.</div>
        </div>
        {bytes && (
          <div className="actions">
            <label className="btn ghost" style={{ margin: 0 }}>
              Open another PDF
              <input type="file" accept="application/pdf" hidden onChange={(e) => open(e.target.files[0])} />
            </label>
          </div>
        )}
      </div>

      {!bytes ? (
        <>
          <label
            className="card center-box"
            style={{ minHeight: 240, cursor: "pointer", borderStyle: "dashed", borderWidth: 2, flexDirection: "column", gap: 8 }}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); open(e.dataTransfer.files[0]); }}
          >
            <span className="btn yellow">Upload PDF</span>
            <span className="muted">or drop it here. Fillable forms fill in automatically from your saved info.</span>
            <input type="file" accept="application/pdf" hidden onChange={(e) => open(e.target.files[0])} />
          </label>
          {profile && !profile.signature && <div className="hint" style={{ marginTop: 12 }}>Tip: set up your signature under <a href="/profile">My signature & info</a> and it drops in with one move.</div>}
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
        <div className="editor two">
          <div className="side stack">
            <div className="card" style={{ padding: 14 }}>
              <div className="panel-title">Drag onto the document</div>
              <div className="palette">
                {baseItems.map((item) => (
                  <button key={item.label} {...paletteProps(item)}>
                    <span className="ico">{item.type === "signature" && profile?.signature ? <img src={profile.signature} alt="" style={{ maxWidth: 24, maxHeight: 20 }} /> : item.icon}</span>
                    {item.label}
                  </button>
                ))}
              </div>
              <div className="panel-title" style={{ marginTop: 14 }}>My info</div>
              {valueItems.length ? (
                <div className="palette">
                  {valueItems.map((item) => (
                    <button key={item.label} {...paletteProps(item)} title={item.label}>
                      <span style={{ minWidth: 0 }}>
                        <span style={{ display: "block", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{item.value}</span>
                        <span className="val">{item.label}</span>
                      </span>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="help">Add your details under <a href="/profile">My signature & info</a> to drag them here.</div>
              )}
              <div className="hint" style={{ marginTop: 12 }}>
                {tool ? `Click the document to place "${tool.label}". Esc to stop.` : "Drag an item onto the page, or click it and then click the page."}
              </div>
            </div>

            {selected && (
              <div className="card" style={{ padding: 14 }}>
                <div className="panel-title">Selected</div>
                {selected.type === "text" && <input id="qs-text" placeholder="Type text…" value={selected.value} onChange={(e) => patch(selected.id, { value: e.target.value })} />}
                <div className="row" style={{ justifyContent: "space-between", marginTop: 10 }}>
                  <span className="muted small">Drag to move · corner to resize</span>
                  <button className="btn sm danger" onClick={() => { setFields(fields.filter((f) => f.id !== sel)); setSel(null); }}>Remove</button>
                </div>
              </div>
            )}

            {formFields.length > 0 && (
              <div className="card" style={{ padding: 14 }}>
                <div className="row" style={{ justifyContent: "space-between" }}>
                  <div className="panel-title" style={{ margin: 0 }}>Form fields ({formFields.length})</div>
                  <span className="muted small">{Object.values(formValues).filter(Boolean).length} filled</span>
                </div>
                <div style={{ maxHeight: 320, overflow: "auto", marginTop: 8 }}>
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
                <div className="help">Written into the form when you finish. For signature boxes, drag your signature onto the page.</div>
              </div>
            )}

            <div className="card" style={{ padding: 14 }}>
              <div className="panel-title">Finish</div>
              <label>Email signed copy to (optional)</label>
              <input placeholder="them@company.com" value={emailTo} onChange={(e) => setEmailTo(e.target.value)} />
              <button className="btn yellow" style={{ width: "100%", justifyContent: "center", marginTop: 12 }} disabled={busy} onClick={finish}>
                {busy ? "Working…" : "Finish & download"}
              </button>
              {msg && <div className={msg.ok ? "success" : "error"}>{msg.text}</div>}
            </div>
          </div>

          <PdfPages
            src={bytes}
            onPageClick={(page, fx, fy) => (tool ? place(tool, page, fx, fy) : setSel(null))}
            overlay={(page, sz) =>
              fields.filter((f) => f.page === page).map((f) => (
                <FieldBox key={f.id} field={f} size={sz} editable color="#3d3bd4" className="filled" selected={sel === f.id} onSelect={() => setSel(f.id)} onChange={(p) => patch(f.id, p)}>
                  {f.type === "signature" || f.type === "initials" ? <img src={f.value} alt="" /> :
                    f.type === "checkbox" ? <b style={{ margin: "auto", color: "#111a40" }}>✕</b> :
                    <span className="val" style={{ fontSize: Math.min(f.h * sz.height * 0.72, 12 * sz.scale), color: f.value ? undefined : "#999" }}>{f.value || "Type text…"}</span>}
                </FieldBox>
              ))
            }
          />
        </div>
      )}

      {pad && (
        <SignaturePad
          defaultName={data.full_name || ""}
          actionLabel="Adopt and Sign"
          onCancel={() => setPad(null)}
          onDone={async ({ signature, initials, name }) => {
            const { item, page, fx, fy } = pad;
            setProfile((p) => ({ ...p, signature, initials }));
            setPad(null);
            place(item, page, fx, fy, item.type === "signature" ? signature : initials);
            try {
              await api("/api/profile", { method: "PUT", body: { signature, initials, data: { ...data, full_name: data.full_name || name } } });
            } catch (e) {
              toast(`Signature placed, but couldn't save it to your profile: ${e.message}`, true);
            }
          }}
        />
      )}
    </>
  );
}

const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
