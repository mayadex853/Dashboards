"use client";
// DocuSign-style header: tabs, a Start menu and an account menu.
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

const TABS = [
  ["/", "Home"],
  ["/agreements", "Agreements"],
  ["/templates", "Templates"],
  ["/intake", "Intake"],
];

function useMenu() {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  useEffect(() => {
    const close = (e) => ref.current && !ref.current.contains(e.target) && setOpen(false);
    document.addEventListener("pointerdown", close);
    return () => document.removeEventListener("pointerdown", close);
  }, []);
  return { open, setOpen, ref };
}

export default function Nav({ problem, emailOn, initials = "Me" }) {
  const path = usePathname();
  const start = useMenu();
  const acct = useMenu();
  const active = (href) => (href === "/" ? path === "/" : path.startsWith(href) || (href === "/agreements" && path.startsWith("/envelopes")));

  return (
    <nav className="nav">
      <Link href="/" className="brand" style={{ textDecoration: "none" }}>
        <span className="logo">T</span>TakaSign
      </Link>
      {TABS.map(([href, label]) => (
        <Link key={href} href={href} className={`tab ${active(href) ? "active" : ""}`}>
          {label}
        </Link>
      ))}
      <div className="spacer" />
      {problem && <span className="status" title={problem}>Setup issue: data can't save</span>}
      {!emailOn && <span className="status" title="Microsoft 365 isn't connected. Signing links are shown for you to copy.">Email off</span>}

      <div className="menu-wrap" ref={start.ref}>
        <button className="btn yellow" onClick={() => start.setOpen(!start.open)}>Start ▾</button>
        {start.open && (
          <div className="menu" onClick={() => start.setOpen(false)}>
            <Link href="/send"><span className="mi-ico">✉</span>Send an envelope</Link>
            <Link href="/quick-sign"><span className="mi-ico">✍</span>Sign a document</Link>
            <Link href="/templates?use=1"><span className="mi-ico">▤</span>Use a template</Link>
            <div className="sep" />
            <Link href="/intake"><span className="mi-ico">☰</span>New signing intake</Link>
          </div>
        )}
      </div>

      <div className="menu-wrap" ref={acct.ref} style={{ marginLeft: 8 }}>
        <button className="avatar" title="Account" onClick={() => acct.setOpen(!acct.open)}>{initials}</button>
        {acct.open && (
          <div className="menu" onClick={() => acct.setOpen(false)}>
            <Link href="/profile"><span className="mi-ico">✎</span>My signature & info</Link>
            <div className="sep" />
            <button
              onClick={async () => {
                await fetch("/api/logout", { method: "POST" });
                location.href = "/login";
              }}
            >
              <span className="mi-ico">⎋</span>Sign out
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
