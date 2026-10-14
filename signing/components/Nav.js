"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  ["/", "Dashboard"],
  ["/quick-sign", "Quick Sign"],
  ["/send", "Send for signature"],
  ["/intake", "Intake"],
  ["/templates", "Templates"],
  ["/profile", "My info & signature"],
];

export default function Nav({ localMode, emailOn }) {
  const path = usePathname();
  return (
    <nav className="nav">
      <div className="brand">
        HD Sign<span>Contracts & signatures</span>
      </div>
      {LINKS.map(([href, label]) => (
        <Link key={href} href={href} className={(href === "/" ? path === "/" : path.startsWith(href)) ? "active" : ""}>
          {label}
        </Link>
      ))}
      <div className="spacer" />
      {localMode && <div className="small muted" style={{ padding: "4px 10px" }}>Local mode (no Supabase)</div>}
      {!emailOn && <div className="small muted" style={{ padding: "4px 10px" }}>Email off: copy links manually</div>}
      <a
        href="#"
        onClick={async (e) => {
          e.preventDefault();
          await fetch("/api/logout", { method: "POST" });
          location.href = "/login";
        }}
      >
        Sign out
      </a>
    </nav>
  );
}
