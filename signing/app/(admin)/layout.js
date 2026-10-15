import Nav from "@/components/Nav";
import { health } from "@/lib/db";
import { emailConfigured } from "@/lib/email";
import { getProfile } from "@/lib/envelopes";
import { initialsOf } from "@/lib/fields";

export const dynamic = "force-dynamic";

export default async function AdminLayout({ children }) {
  const h = await health().catch((e) => ({ ok: false, problem: e.message }));
  const profile = h.ok ? await getProfile().catch(() => null) : null;
  return (
    <div className="shell">
      <Nav problem={h.ok ? null : h.problem} emailOn={emailConfigured()} initials={initialsOf(profile?.data?.full_name) || "Me"} />
      <main className="main">
        {!h.ok && (
          <div className="error" style={{ marginBottom: 18 }}>
            <b>TakaSign can't save data yet.</b> {h.problem}
            <div className="small" style={{ marginTop: 4 }}>Fix it in Vercel → takasign → Settings → Environment Variables, then redeploy.</div>
          </div>
        )}
        {children}
      </main>
    </div>
  );
}
