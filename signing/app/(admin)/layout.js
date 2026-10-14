import Nav from "@/components/Nav";
import { health } from "@/lib/db";
import { emailConfigured } from "@/lib/email";

export const dynamic = "force-dynamic";

export default async function AdminLayout({ children }) {
  const h = await health().catch((e) => ({ ok: false, problem: e.message }));
  return (
    <div className="shell">
      <Nav problem={h.ok ? null : h.problem} emailOn={emailConfigured()} />
      <main className="main">
        {!h.ok && (
          <div className="error" style={{ marginBottom: 18 }}>
            <b>TakaSign can't save data yet.</b> {h.problem}
            <div className="small" style={{ marginTop: 4 }}>
              Fix it in Vercel → takasign → Settings → Environment Variables, then redeploy.
            </div>
          </div>
        )}
        {children}
      </main>
    </div>
  );
}
