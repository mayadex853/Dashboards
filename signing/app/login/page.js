"use client";
import { useState } from "react";

export default function Login() {
  const [pw, setPw] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    setBusy(true);
    const res = await fetch("/api/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ password: pw }) });
    if (res.ok) location.href = "/";
    else {
      setErr((await res.json()).error || "Login failed");
      setBusy(false);
    }
  };
  return (
    <div className="center-box" style={{ minHeight: "100vh" }}>
      <form className="card" style={{ width: 360, textAlign: "left", padding: 28 }} onSubmit={submit}>
        <div className="row" style={{ marginBottom: 18 }}>
          <span style={{ width: 34, height: 34, borderRadius: 8, background: "var(--primary)", color: "#fff", display: "grid", placeItems: "center", fontWeight: 700 }}>T</span>
          <h1 style={{ margin: 0 }}>TakaSign</h1>
        </div>
        <p className="muted" style={{ marginTop: 0 }}>Sign in to continue</p>
        <div className="field">
          <label>Password</label>
          <input type="password" autoFocus value={pw} onChange={(e) => setPw(e.target.value)} />
        </div>
        {err && <div className="error">{err}</div>}
        <button className="btn" disabled={busy} style={{ width: "100%", justifyContent: "center" }}>{busy ? "Signing in…" : "Sign in"}</button>
      </form>
    </div>
  );
}
