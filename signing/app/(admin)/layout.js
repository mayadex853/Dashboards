import Nav from "@/components/Nav";
import { isLocalMode } from "@/lib/db";
import { emailConfigured } from "@/lib/email";

export const dynamic = "force-dynamic";

export default function AdminLayout({ children }) {
  return (
    <div className="shell">
      <Nav localMode={isLocalMode} emailOn={emailConfigured()} />
      <main className="main">{children}</main>
    </div>
  );
}
