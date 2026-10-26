"use client";
// DocuSign-style send wizard:
//   Step 1 — Add documents, recipients (with signing order / CC) and the email message
//   Step 2 — Full-screen "Add Fields" editor, then Send
import { Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { stashLinks, api } from "@/lib/api";
import FieldEditor from "@/components/FieldEditor";
import SignerList from "@/components/SignerList";
import FullScreen from "@/components/FullScreen";
import { takeUpload } from "@/components/HomeDrop";
import { toast } from "@/components/Toast";

export default function SendPage() {
  return (
    <Suspense fallback={<div className="muted">Loading…</div>}>
      <Send />
    </Suspense>
  );
}

const blankSigner = () => ({ name: "", email: "", routing_order: 1, kind: "signer" });

function Send() {
  const params = useSearchParams();
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [templates, setTemplates] = useState([]);
  const [profile, setProfile] = useState(null);
  const [templateId, setTemplateId] = useState(params.get("template") || "");
  const [file, setFile] = useState(null);
  const [fileBytes, setFileBytes] = useState(null);
  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("");
  const [subjectTouched, setSubjectTouched] = useState(false);
  const [message, setMessage] = useState("");
  const [signers, setSigners] = useState([blankSigner()]);
  const [fields, setFields] = useState([]);
  const [values, setValues] = useState({});
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const template = templates.find((t) => t.id === templateId);

  useEffect(() => {
    api("/api/templates").then(setTemplates).catch(() => {});
    api("/api/profile").then(setProfile).catch(() => setProfile({ data: {} }));
    if (params.get("from") === "drop") {
      const f = takeUpload();
      if (f) pickFile(f);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Picking a template sets the document, its recipient roles and its fields
  useEffect(() => {
    if (!template || !profile) return;
    setTitle(template.name);
    setFields(template.fields.map((f) => ({ ...f })));
    setSigners(
      template.roles.map((r, i) =>
        r.kind === "me"
          ? { name: profile.data?.full_name || "", email: profile.data?.email || "", routing_order: i + 1, is_me: true, roleName: r.name, role_index: i, kind: "signer" }
          : { name: "", email: "", routing_order: i + 1, roleName: r.name, role_index: i, kind: "signer" }
      )
    );
  }, [template, profile]);

  useEffect(() => {
    if (!subjectTouched) setSubject(title ? `Complete with TakaSign: ${title}` : "");
  }, [title, subjectTouched]);

  // Template text fields that need values from you when sending (deal terms etc.)
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

  async function pickFile(f) {
    if (!f) return;
    setTemplateId("");
    setFile(f);
    setFileBytes(new Uint8Array(await f.arrayBuffer()));
    setTitle(f.name.replace(/\.pdf$/i, ""));
    setFields([]);
    setSigners((s) => (s.some((x) => x.role_index !== undefined) ? [blankSigner()] : s));
  }
  const clearDoc = () => {
    setFile(null);
    setFileBytes(null);
    setTemplateId("");
    setTitle("");
    setFields([]);
    setSigners([blankSigner()]);
  };

  const signerOnly = signers.filter((s) => s.kind !== "cc");
  // Roles shown in the field editor, labelled with the real person's name
  const roles = template
    ? template.roles.map((r, i) => {
        const s = signers.find((x) => x.role_index === i);
        return { ...r, name: s?.name ? `${s.name} (${r.name})` : r.name };
      })
    : signerOnly.map((s, i) => ({ name: s.is_me ? "Me" : s.name || `Signer ${i + 1}`, kind: s.is_me ? "me" : "other" }));

  const next = () => {
    setErr("");
    if (!template && !file) return setErr("Add a document or choose a template");
    if (!signerOnly.length) return setErr("Add at least one person who needs to sign");
    const bad = signers.find((s) => !s.name.trim() || !/^\S+@\S+\.\S+$/.test(s.email));
    if (bad) return setErr("Every recipient needs a name and a valid email");
    // Fields point at signers by position: drop any that now point past the last signer
    const stale = fields.filter((f) => f.role >= signerOnly.length);
    if (!template && stale.length) {
      setFields(fields.filter((f) => f.role < signerOnly.length));
      toast(`${stale.length} field(s) belonged to a removed signer and were deleted.`, true);
    }
    setStep(2);
  };

  const submit = async (send) => {
    setErr("");
    const roleCount = template ? template.roles.length : signerOnly.length;
    const empty = [...Array(roleCount).keys()].filter((i) => !fields.some((f) => f.role === i));
    if (send && empty.length) {
      const names = empty.map((i) => roles[i]?.name || `Signer ${i + 1}`).join(", ");
      toast(`Add at least one field for: ${names}`, true);
      return;
    }
    setBusy(true);
    try {
      const form = new FormData();
      if (file && !template) form.append("file", file);
      form.append(
        "payload",
        JSON.stringify({
          title,
          subject,
          message,
          templateId: template?.id,
          fields,
          values,
          recipients: signers.map((orig) => {
            const { roleName, ...s } = orig;
            const cc = s.kind === "cc";
            return { ...s, kind: cc ? "cc" : "signer", role_index: cc ? -1 : template ? s.role_index : signerOnly.indexOf(orig) };
          }),
          send,
        })
      );
      const res = await api("/api/envelopes", { method: "POST", form });
      stashLinks(res);
      router.push(`/envelopes/${res.envelope.id}`);
    } catch (e) {
      toast(e.message, true);
      setBusy(false);
    }
  };

  if (step === 2)
    return (
      <FullScreen
        title={title}
        subtitle="Add fields for each recipient. Drag a field onto the document, or click a field then click the page."
        onBack={() => setStep(1)}
        actions={
          <>
            <button className="btn ghost" disabled={busy} onClick={() => submit(false)}>Save and close</button>
            <button className="btn yellow" disabled={busy} onClick={() => submit(true)}>{busy ? "Sending…" : "Send"}</button>
          </>
        }
      >
        <FieldEditor src={template ? `/api/templates/${template.id}/pdf` : fileBytes} fields={fields} setFields={setFields} roles={roles} showKeys />
      </FullScreen>
    );

  return (
    <>
      <div className="wiz-steps">
        <div className="s on"><span className="num">1</span>Add documents and recipients</div>
        <div className="s"><span className="num">2</span>Add fields</div>
      </div>

      <div className="wiz-section">
        <div className="h">Add documents</div>
        <div className="b">
          <div className="row" style={{ alignItems: "flex-start", gap: 14 }}>
            {(file || template) && (
              <div className="doc-tile">
                <div className="thumb">📄</div>
                <div className="nm" title={title}>{template ? `${template.name} (template)` : file.name}</div>
                <button className="link small" style={{ padding: "0 10px 8px", color: "var(--bad)" }} onClick={clearDoc}>Remove</button>
              </div>
            )}
            {!file && !template && (
              <label
                className="upload-tile"
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => { e.preventDefault(); pickFile(e.dataTransfer.files[0]); }}
              >
                <span style={{ fontSize: 28 }}>⬆</span>
                <b>Upload</b>
                <span className="small muted">or drop a PDF here</span>
                <input type="file" accept="application/pdf" hidden onChange={(e) => pickFile(e.target.files[0])} />
              </label>
            )}
            {!file && !template && (
              <div className="upload-tile" style={{ cursor: "default" }}>
                <span style={{ fontSize: 28 }}>▤</span>
                <b>Use a template</b>
                <select value={templateId} onChange={(e) => setTemplateId(e.target.value)} style={{ fontSize: 12.5 }}>
                  <option value="">Choose…</option>
                  {templates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="wiz-section">
        <div className="h">Add recipients</div>
        <div className="b">
          <SignerList signers={signers} setSigners={setSigners} profile={profile} fixedRoles={!!template} />
        </div>
      </div>

      {askKeys.length > 0 && (
        <div className="wiz-section">
          <div className="h">Fill in contract details</div>
          <div className="b">
            <div className="form-grid">
              {askKeys.map((k) => (
                <div key={k.key}>
                  <label>{k.label} <span className="muted small">({k.key})</span></label>
                  <input value={values[k.key] || ""} onChange={(e) => setValues({ ...values, [k.key]: e.target.value })} />
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="wiz-section">
        <div className="h">Add message</div>
        <div className="b">
          <div className="field">
            <label>Email subject *</label>
            <input value={subject} maxLength={100} onChange={(e) => { setSubject(e.target.value); setSubjectTouched(true); }} placeholder="Complete with TakaSign: Agreement" />
          </div>
          <div className="field" style={{ marginBottom: 0 }}>
            <label>Email message</label>
            <textarea value={message} maxLength={2000} onChange={(e) => setMessage(e.target.value)} placeholder="Enter a message for your recipients" />
          </div>
        </div>
      </div>

      {err && <div className="error">{err}</div>}
      <div className="wiz-foot">
        <button className="btn ghost" onClick={() => router.push("/")}>Cancel</button>
        <button className="btn" onClick={next}>Next</button>
      </div>
    </>
  );
}
