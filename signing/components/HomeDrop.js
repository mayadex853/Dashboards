"use client";
// Home drop zone: drop a PDF, then choose "Send for signature" or "Sign it myself".
import { useState } from "react";
import { useRouter } from "next/navigation";

export function stashUpload(file) {
  window.__takasignUpload = file;
}
export function takeUpload() {
  const f = window.__takasignUpload || null;
  window.__takasignUpload = null;
  return f;
}

export default function HomeDrop() {
  const [over, setOver] = useState(false);
  const [file, setFile] = useState(null);
  const router = useRouter();
  const pick = (f) => f && (f.type === "application/pdf" || f.name?.toLowerCase().endsWith(".pdf")) && setFile(f);
  const go = (path) => {
    stashUpload(file);
    router.push(path);
  };

  return (
    <div
      className={`dropzone ${over ? "over" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setOver(true); }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => { e.preventDefault(); setOver(false); pick(e.dataTransfer.files[0]); }}
    >
      {!file ? (
        <>
          <div style={{ fontSize: 16, fontWeight: 600 }}>Drop documents here to get started</div>
          <label className="btn yellow" style={{ margin: 0 }}>
            Start
            <input type="file" accept="application/pdf" hidden onChange={(e) => pick(e.target.files[0])} />
          </label>
        </>
      ) : (
        <>
          <div style={{ fontWeight: 600 }}>📄 {file.name}</div>
          <div className="row" style={{ justifyContent: "center" }}>
            <button className="btn yellow" onClick={() => go("/send?from=drop")}>Send for signature</button>
            <button className="btn ghost" onClick={() => go("/quick-sign?from=drop")}>Sign it myself</button>
          </div>
          <button className="link small" style={{ color: "#d9d8ff" }} onClick={() => setFile(null)}>Choose a different file</button>
        </>
      )}
    </div>
  );
}
