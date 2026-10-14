// Data layer. Uses Supabase when configured, otherwise a local JSON store in ./.data
// (local mode is for trying the app on your own machine only).
import "server-only";
import { createClient } from "@supabase/supabase-js";
import { promises as fs } from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const BUCKET = "documents";
export const isLocalMode = !process.env.SUPABASE_URL;

let _sb;
function sb() {
  if (!_sb) {
    _sb = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY, {
      auth: { persistSession: false },
    });
  }
  return _sb;
}

// ---------- local JSON store ----------
const DATA_DIR = path.join(process.cwd(), ".data");
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
const matches = (row, filter) => Object.entries(filter).every(([k, v]) => row[k] === v);

// ---------- generic table API ----------
export async function insert(table, row) {
  const rec = { id: row.id ?? crypto.randomUUID(), created_at: new Date().toISOString(), ...row };
  if (isLocalMode) {
    const rows = await readTable(table);
    rows.push(rec);
    await writeTable(table, rows);
    return rec;
  }
  const { data, error } = await sb().from(table).insert(rec).select().single();
  if (error) throw new Error(`${table} insert: ${error.message}`);
  return data;
}

export async function update(table, id, patch) {
  if (isLocalMode) {
    const rows = await readTable(table);
    const i = rows.findIndex((r) => r.id === id);
    if (i < 0) return null;
    rows[i] = { ...rows[i], ...patch };
    await writeTable(table, rows);
    return rows[i];
  }
  const { data, error } = await sb().from(table).update(patch).eq("id", id).select().single();
  if (error) throw new Error(`${table} update: ${error.message}`);
  return data;
}

export async function upsert(table, row) {
  if (isLocalMode) {
    const rows = await readTable(table);
    const i = rows.findIndex((r) => r.id === row.id);
    if (i < 0) rows.push(row);
    else rows[i] = { ...rows[i], ...row };
    await writeTable(table, rows);
    return row;
  }
  const { data, error } = await sb().from(table).upsert(row).select().single();
  if (error) throw new Error(`${table} upsert: ${error.message}`);
  return data;
}

export async function remove(table, id) {
  if (isLocalMode) {
    const rows = await readTable(table);
    await writeTable(table, rows.filter((r) => r.id !== id));
    return;
  }
  const { error } = await sb().from(table).delete().eq("id", id);
  if (error) throw new Error(`${table} delete: ${error.message}`);
}

export async function list(table, filter = {}, { order = "created_at", asc = false } = {}) {
  if (isLocalMode) {
    const rows = (await readTable(table)).filter((r) => matches(r, filter));
    rows.sort((a, b) => (a[order] > b[order] ? 1 : a[order] < b[order] ? -1 : 0) * (asc ? 1 : -1));
    return rows;
  }
  let q = sb().from(table).select("*");
  for (const [k, v] of Object.entries(filter)) q = q.eq(k, v);
  const { data, error } = await q.order(order, { ascending: asc });
  if (error) throw new Error(`${table} list: ${error.message}`);
  return data;
}

export async function findOne(table, filter) {
  if (isLocalMode) return (await readTable(table)).find((r) => matches(r, filter)) ?? null;
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
