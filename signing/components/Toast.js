"use client";
// Tiny global toast: call toast("Saved") or toast("Something broke", true) from anywhere.
import { useEffect, useState } from "react";

let push;
export function toast(text, isError = false) {
  push?.({ text, isError, id: Date.now() });
}

export default function Toaster() {
  const [t, setT] = useState(null);
  useEffect(() => {
    push = setT;
    return () => (push = null);
  }, []);
  useEffect(() => {
    if (!t) return;
    const h = setTimeout(() => setT(null), t.isError ? 7000 : 2500);
    return () => clearTimeout(h);
  }, [t]);
  if (!t) return null;
  return (
    <div className={`toast ${t.isError ? "err" : ""}`} role="status" onClick={() => setT(null)}>
      {t.text}
    </div>
  );
}
