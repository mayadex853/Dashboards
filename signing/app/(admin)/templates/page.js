"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, fmtDate } from "@/lib/api";
import { CATEGORIES } from "@/lib/fields";

export default function Templates() {
  const [list, setList] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [category, setCategory] = useState("");
  const router = useRouter();

  useEffect(() => {
    api("/api/templates").then(setList).catch((e) => setErr(e.message));
  }, []);

  const upload = async (file) => {
    if (!file) return;
    setBusy(true);
    setErr("");
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("category", category);
      const t = await api("/api/templates", { method: "POST", form });
      router.push(`/templates/${t.id}`);
    } catch (e) {
      setErr(e.message);
      setBusy(false);
    }
  };

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Contract templates</h1>
          <div className="muted">Upload a PDF once, place fields, reuse for every signing.</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <h2>Add a template</h2>
        <div className="row">
          <select style={{ width: 200 }} value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">Any signing type</option>
            {CATEGORIES.map((c) => <option key={c.key} value={c.key}>{c.label}</option>)}
          </select>
          <label className="btn" style={{ margin: 0 }}>
            {busy ? "Uploading…" : "Upload PDF"}
            <input type="file" accept="application/pdf" hidden disabled={busy} onChange={(e) => upload(e.target.files[0])} />
          </label>
        </div>
        {err && <div className="error">{err}</div>}
      </div>

      <div className="card">
        {!list ? (
          <div className="muted">Loading…</div>
        ) : !list.length ? (
          <div className="muted">No templates yet.</div>
        ) : (
          <table>
            <thead><tr><th>Name</th><th>Type</th><th>Fields</th><th>Updated</th><th /></tr></thead>
            <tbody>
              {list.map((t) => (
                <tr key={t.id}>
                  <td><Link href={`/templates/${t.id}`}>{t.name}</Link></td>
                  <td className="muted">{CATEGORIES.find((c) => c.key === t.category)?.label || "Any"}</td>
                  <td className="muted">{t.fields.length}</td>
                  <td className="muted small">{fmtDate(t.updated_at || t.created_at)}</td>
                  <td style={{ textAlign: "right" }}><Link className="btn sm ghost" href={`/send?template=${t.id}`}>Use</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
