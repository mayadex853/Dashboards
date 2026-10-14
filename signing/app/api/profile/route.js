import * as db from "@/lib/db";
import { route } from "@/lib/http";
import { getProfile } from "@/lib/envelopes";

export const GET = route(async () => getProfile());

export const PUT = route(async (req) => {
  const body = await req.json();
  const cur = await getProfile();
  return db.upsert("profile", {
    id: "me",
    data: body.data ?? cur.data ?? {},
    signature: body.signature !== undefined ? body.signature : cur.signature ?? null,
    initials: body.initials !== undefined ? body.initials : cur.initials ?? null,
    updated_at: new Date().toISOString(),
  });
});
