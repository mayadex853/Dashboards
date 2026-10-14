"use client";
import { useState } from "react";

export default function Login() {
  const [pw, setPw] = useState("");
  const [err, setErr] = useState("");
  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    const res = await fetch("/api/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ password: pw }) });
    if (res.ok) location.href = "/";
    else setErr((await res.json()).error || "Login failed");
  };
  return (
    <div className="center-box">
      <form className="card" style={{ width: 340, textAlign: "left" }} onSubmit={submit}>
        <h1>HD Sign</h1>
        <p className="muted" style={{ marginTop: 0 }}>Sign in to continue</p>
        <div className="field">
          <label>Password</label>
          <input type="password" autoFocus value={pw} onChange={(e) => setPw(e.target.value)} />
        </div>
        {err && <div className="error">{err}</div>}
        <button className="btn" style={{ width: "100%", justifyContent: "center" }}>Sign in</button>
      </form>
    </div>
  );
}
