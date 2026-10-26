// Data layer. Uses Supabase when configured, otherwise a local JSON store in ./.data
// (local mode is for trying the app on your own machine only).
import "server-only";
import { createClient } from "@supabase/supabase-js";
import { promises as fs } from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const BUCKET = "documents";
export const isLocalMode = !process.env.SUPABASE_URL;

/** Explains a misconfigured Supabase key in plain words (or returns null if it looks right). */
export function keyProblem() {
  const key = (process.env.SUPABASE_SERVICE_ROLE_KEY || "").trim();
  if (!key) return "SUPABASE_SERVICE_ROLE_KEY is not set in Vercel.";
  if (key.startsWith("sb_publishable_")) return "SUPABASE_SERVICE_ROLE_KEY is the publishable key. Use the secret key (sb_secret_…) from Supabase > Project Settings > API Keys.";
  if (key.startsWith("sb_secret_")) return null;
  try {
    const role = JSON.parse(Buffer.from(key.split(".")[1], "base64url").toString()).role;
    if (role === "service_role") return null;
    return `SUPABASE_SERVICE_ROLE_KEY is the "${role}" key. Use the service_role key from Supabase > Project Settings > API.`;
  } catch {
    return "SUPABASE_SERVICE_ROLE_KEY doesn't look like a Supabase key. Copy the service_role / secret key again.";
  }
}

let _sb;
function sb() {
  if (!_sb) {
    const problem = keyProblem();
    if (problem) throw new Error(problem);
    _sb = createClient(process.env.SUPABASE_URL.trim(), process.env.SUPABASE_SERVICE_ROLE_KEY.trim(), {
      auth: { persistSession: false },
    });
  }
  return _sb;
}

/** Read-only check that the database and storage are reachable with full access. */
export async function health() {
  if (isLocalMode) return { ok: true, mode: "local" };
  const problem = keyProblem();
  if (problem) return { ok: false, problem };
  const { error } = await sb().from("profile").select("id").limit(1);
  if (error) return { ok: false, problem: `Database: ${error.message}` };
  const { data: buckets, error: bErr } = await sb().storage.listBuckets();
  if (bErr) return { ok: false, problem: `Storage: ${bErr.message}` };
  if (!buckets.some((b) => b.id === BUCKET)) return { ok: false, problem: `Storage bucket "${BUCKET}" not found` };
  return { ok: true, mode: "supabase" };
}

// ---------- local JSON store ----------
const DATA_DIR = path.join(process.cwd(), ".data");
// Local mode runs every operation one at a time (like a database would), so concurrent
// requests can't overwrite each other. LOCAL_DB_LATENCY_MS simulates network latency for tests.
let _chain = Promise.resolve();
function serialized(fn) {
  const run = async () => {
    const ms = Number(process.env.LOCAL_DB_LATENCY_MS || 0);
    if (ms) await new Promise((r) => setTimeout(r, ms));
    return fn();
  };
  const p = _chain.then(run, run);
  _chain = p.catch(() => {});
  return p;
}
async function readTable(table) {
  try {
    return JSON.parse(await fs.readFile(path.join(DATA_DIR, `${table}.json`), "utf8"));
  } catch {
    return [];
  }
}
async function writeTable(table, rows) {
  await fs.mkdir(DATA_DIR, { recursive: true });
  await fs.writeFile(path.join(DATA_DIR, `${table}.json`), JSON.stringify(rows, null, 2));
}
const matches = (row, filter) => Object.entries(filter).every(([k, v]) => (row[k] ?? null) === v);

// ---------- generic table API ----------
export async function insert(table, row) {
  const rec = { id: row.id ?? crypto.randomUUID(), created_at: new Date().toISOString(), ...row };
  if (isLocalMode)
    return serialized(async () => {
      const rows = await readTable(table);
      rows.push(rec);
      await writeTable(table, rows);
      return rec;
    });
  const { data, error } = await sb().from(table).insert(rec).select().single();
  if (error) throw new Error(`${table} insert: ${error.message}`);
  return data;
}

export async function update(table, id, patch) {
  if (isLocalMode)
    return serialized(async () => {
      const rows = await readTable(table);
      const i = rows.findIndex((r) => r.id === id);
      if (i < 0) return null;
      rows[i] = { ...rows[i], ...patch };
      await writeTable(table, rows);
      return rows[i];
    });
  const { data, error } = await sb().from(table).update(patch).eq("id", id).select().maybeSingle();
  if (error) throw new Error(`${table} update: ${error.message}`);
  return data;
}

/**
 * Compare-and-set: apply `patch` only if the row still matches `where` (use null for "is empty").
 * Returns the updated row, or null if someone else changed it first. This is what stops two
 * simultaneous requests from both "winning" (double sign, double complete, lost updates).
 */
export async function updateWhere(table, id, where, patch) {
  if (isLocalMode)
    return serialized(async () => {
      const rows = await readTable(table);
      const i = rows.findIndex((r) => r.id === id && matches(r, where));
      if (i < 0) return null;
      rows[i] = { ...rows[i], ...patch };
      await writeTable(table, rows);
      return rows[i];
    });
  let q = sb().from(table).update(patch).eq("id", id);
  for (const [k, v] of Object.entries(where)) q = v === null ? q.is(k, null) : q.eq(k, v);
  const { data, error } = await q.select();
  if (error) throw new Error(`${table} updateWhere: ${error.message}`);
  return data?.[0] ?? null;
}

export async function upsert(table, row) {
  if (isLocalMode)
    return serialized(async () => {
      const rows = await readTable(table);
      const i = rows.findIndex((r) => r.id === row.id);
      if (i < 0) rows.push(row);
      else rows[i] = { ...rows[i], ...row };
      await writeTable(table, rows);
      return row;
    });
  const { data, error } = await sb().from(table).upsert(row).select().single();
  if (error) throw new Error(`${table} upsert: ${error.message}`);
  return data;
}

export async function remove(table, id) {
  if (isLocalMode)
    return serialized(async () => {
      const rows = await readTable(table);
      await writeTable(table, rows.filter((r) => r.id !== id));
    });
  const { error } = await sb().from(table).delete().eq("id", id);
  if (error) throw new Error(`${table} delete: ${error.message}`);
}

export async function list(table, filter = {}, { order = "created_at", asc = false } = {}) {
  if (isLocalMode)
    return serialized(async () => {
      const rows = (await readTable(table)).filter((r) => matches(r, filter));
      rows.sort((a, b) => (a[order] > b[order] ? 1 : a[order] < b[order] ? -1 : 0) * (asc ? 1 : -1));
      return rows;
    });
  // Supabase returns at most 1000 rows per request, so page through everything.
  const PAGE = 1000;
  const all = [];
  for (let from = 0; ; from += PAGE) {
    let q = sb().from(table).select("*");
    for (const [k, v] of Object.entries(filter)) q = q.eq(k, v);
    const { data, error } = await q.order(order, { ascending: asc }).order("id").range(from, from + PAGE - 1);
    if (error) throw new Error(`${table} list: ${error.message}`);
    all.push(...data);
    if (data.length < PAGE) return all;
  }
}

/** How many rows match `filter` and were created since `sinceISO`. */
export async function countSince(table, filter, sinceISO) {
  if (isLocalMode)
    return serialized(async () => (await readTable(table)).filter((r) => matches(r, filter) && r.created_at >= sinceISO).length);
  let q = sb().from(table).select("id", { count: "exact", head: true }).gte("created_at", sinceISO);
  for (const [k, v] of Object.entries(filter)) q = q.eq(k, v);
  const { count, error } = await q;
  if (error) throw new Error(`${table} count: ${error.message}`);
  return count ?? 0;
}

export async function findOne(table, filter) {
  if (isLocalMode) return serialized(async () => (await readTable(table)).find((r) => matches(r, filter)) ?? null);
  let q = sb().from(table).select("*");
  for (const [k, v] of Object.entries(filter)) q = q.eq(k, v);
  const { data, error } = await q.limit(1).maybeSingle();
  if (error) throw new Error(`${table} find: ${error.message}`);
  return data;
}

export const get = (table, id) => findOne(table, { id });

// ---------- file storage ----------
export async function putFile(key, bytes, contentType = "application/pdf") {
  if (isLocalMode) {
    const p = path.join(DATA_DIR, "files", key);
    await fs.mkdir(path.dirname(p), { recursive: true });
    await fs.writeFile(p, Buffer.from(bytes));
    return key;
  }
  const { error } = await sb().storage.from(BUCKET).upload(key, bytes, { contentType, upsert: true });
  if (error) throw new Error(`upload: ${error.message}`);
  return key;
}

export async function getFile(key) {
  if (isLocalMode) return new Uint8Array(await fs.readFile(path.join(DATA_DIR, "files", key)));
  const { data, error } = await sb().storage.from(BUCKET).download(key);
  if (error) throw new Error(`download: ${error.message}`);
  return new Uint8Array(await data.arrayBuffer());
}

/** Delete every stored file under a folder prefix (e.g. "envelopes/<id>"). */
export async function removeFiles(prefix) {
  if (isLocalMode) {
    await fs.rm(path.join(DATA_DIR, "files", prefix), { recursive: true, force: true });
    return;
  }
  const { data, error } = await sb().storage.from(BUCKET).list(prefix.replace(/\/$/, ""), { limit: 1000 });
  if (error) throw new Error(`list files: ${error.message}`);
  if (data?.length) {
    const { error: rmErr } = await sb().storage.from(BUCKET).remove(data.map((f) => `${prefix.replace(/\/$/, "")}/${f.name}`));
    if (rmErr) throw new Error(`remove files: ${rmErr.message}`);
  }
}
