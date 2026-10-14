"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  ["/", "Home"],
  ["/quick-sign", "Sign a document"],
  ["/send", "Send"],
  ["/intake", "Intake"],
  ["/templates", "Templates"],
  ["/profile", "My signature & info"],
];

export default function Nav({ problem, emailOn }) {
  const path = usePathname();
  return (
    <nav className="nav">
      <Link href="/" className="brand" style={{ textDecoration: "none" }}>
        <span className="logo">T</span>TakaSign
      </Link>
      {LINKS.map(([href, label]) => (
        <Link key={href} href={href} className={`tab ${(href === "/" ? path === "/" : path.startsWith(href)) ? "active" : ""}`}>
          {label}
        </Link>
      ))}
      <div className="spacer" />
      {problem && <span className="status" title={problem}>Setup issue: data can't save</span>}
      {!emailOn && <span className="status" title="Microsoft 365 isn't connected yet. Signing links are shown for you to copy.">Email off</span>}
      <Link href="/send" className="btn yellow sm">Start</Link>
      <button
        className="signout"
        onClick={async () => {
          await fetch("/api/logout", { method: "POST" });
          location.href = "/login";
        }}
      >
        Sign out
      </button>
    </nav>
  );
}
