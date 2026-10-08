"use client";
import { Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { stashLinks, api } from "@/lib/api";
import FieldEditor from "@/components/FieldEditor";
import SignerList from "@/components/SignerList";

export default function SendPage() {
  return (
    <Suspense fallback={<div className="muted">Loading…</div>}>
      <Send />
    </Suspense>
  );
}

function Send() {
  const params = useSearchParams();
  const router = useRouter();
  const [templates, setTemplates] = useState([]);
  const [profile, setProfile] = useState(null);
  const [templateId, setTemplateId] = useState(params.get("template") || "");
  const [file, setFile] = useState(null);
  const [fileBytes, setFileBytes] = useState(null);
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [signers, setSigners] = useState([{ name: "", email: "", routing_order: 1 }]);
  const [fields, setFields] = useState([]);
  const [values, setValues] = useState({});
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const template = templates.find((t) => t.id === templateId);

  useEffect(() => {
    api("/api/templates").then(setTemplates);
    api("/api/profile").then(setProfile);
  }, []);

  // When a template is picked, build the signer list from its roles
  useEffect(() => {
    if (!template || !profile) return;
    setTitle((t) => t || template.name);
    setSigners(
      template.roles.map((r, i) =>
        r.kind === "me"
          ? { name: profile.data?.full_name || "", email: profile.data?.email || "", routing_order: i + 1, is_me: true, roleName: r.name }
          : { name: "", email: "", routing_order: i + 1, roleName: r.name }
      )
    );
  }, [template, profile]);

  // Keyed fields we can't resolve automatically → ask for values
  const askKeys = useMemo(() => {
    if (!template) return [];
    const seen = new Map();
    for (const f of template.fields) {
      if (!f.key || f.key === "today") continue;
      const [ns, name] = f.key.split(".");
      if (ns === "profile" && profile?.data?.[name]) continue;
      if (!seen.has(f.key)) seen.set(f.key, f.label);
    }
    return [...seen].map(([key, label]) => ({ key, label }));
  }, [template, profile]);

  const pickFile = async (f) => {
    if (!f) return;
    setTemplateId("");
    setFile(f);
    setFileBytes(new Uint8Array(await f.arrayBuffer()));
    setTitle(f.name.replace(/\.pdf$/i, ""));
    setFields([]);
  };

  const roles = template ? template.roles : signers.map((s, i) => ({ name: s.is_me ? "Me" : s.name || `Signer ${i + 1}` }));

  const submit = async (send) => {
    setErr("");
    setBusy(true);
    try {
      if (!template && !file) throw new Error("Choose a template or upload a PDF");
      if (!template && !fields.length) throw new Error("Place at least one field on the document");
      const form = new FormData();
      if (file && !template) form.append("file", file);
      form.append(
        "payload",
        JSON.stringify({
          title,
          message,
          templateId: template?.id,
          fields: template ? undefined : fields,
          values,
          recipients: signers.map((s, i) => ({ ...s, role_index: i })),
          send,
        })
      );
      const res = await api("/api/envelopes", { method: "POST", form });
      stashLinks(res);
      router.push(`/envelopes/${res.envelope.id}`);
    } catch (e) {
      setErr(e.message);
      setBusy(false);
    }
  };

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Send for signature</h1>
          <div className="muted">Signers get emailed one after another in signing order.</div>
        </div>
      </div>

      <div className="stack">
        <div className="card">
          <h2>Document</h2>
          <div className="row">
            <select style={{ maxWidth: 360 }} value={templateId} onChange={(e) => { setTemplateId(e.target.value); setFile(null); setFileBytes(null); setTitle(""); }}>
              <option value="">Choose a template…</option>
              {templates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
            <span className="muted">or</span>
            <label className="btn ghost" style={{ margin: 0 }}>
              {file ? file.name : "Upload a PDF"}
              <input type="file" accept="application/pdf" hidden onChange={(e) => pickFile(e.target.files[0])} />
            </label>
          </div>
          {(template || file) && (
            <div className="form-grid" style={{ marginTop: 14 }}>
              <div>
                <label>Title</label>
                <input value={title} onChange={(e) => setTitle(e.target.value)} />
              </div>
              <div style={{ gridColumn: "span 2" }}>
                <label>Message to signers (optional)</label>
                <input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Hi! Here's the agreement we discussed." />
              </div>
            </div>
          )}
        </div>

        {(template || file) && (
          <div className="card">
            <h2>Signers & order</h2>
            <SignerList signers={signers} setSigners={setSigners} profile={profile} fixedRoles={!!template} />
          </div>
        )}

        {askKeys.length > 0 && (
          <div className="card">
            <h2>Fill in contract details</h2>
            <div className="form-grid">
              {askKeys.map((k) => (
                <div key={k.key}>
                  <label>{k.label} <span className="muted small">({k.key})</span></label>
                  <input value={values[k.key] || ""} onChange={(e) => setValues({ ...values, [k.key]: e.target.value })} />
                </div>
              ))}
            </div>
            <div className="help">Blank values stay blank; fields assigned to a signer can be completed by them.</div>
          </div>
        )}

        {fileBytes && !template && (
          <div>
            <h2>Place fields</h2>
            <FieldEditor src={fileBytes} fields={fields} setFields={setFields} roles={roles} showKeys />
          </div>
        )}

        {err && <div className="error">{err}</div>}
        {(template || file) && (
          <div className="row end">
            <button className="btn ghost" disabled={busy} onClick={() => submit(false)}>Save draft</button>
            <button className="btn" disabled={busy} onClick={() => submit(true)}>{busy ? "Sending…" : "Send"}</button>
          </div>
        )}
      </div>
    </>
  );
}
