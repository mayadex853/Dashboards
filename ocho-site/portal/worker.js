// Ocho client portal: Cloudflare Worker + D1 (DB) + R2 (AUDIO = public MP3 bucket, MASTERS = private WAV bucket).
// build.py inlines the app page and the catalog into dist/worker.js; deploy.py uploads it.
const HTML = __HTML__;
const CATALOG = __CATALOG__;

const DAY = 86400, LEVEL = { none: 0, mp3: 1, wav: 2 }, COOKIE = 'ocho_s';
const FILES = {}; // file key (no extension) -> { album, track, version }
CATALOG.albums.forEach(a => a.tracks.forEach(t => t.v.forEach(v => { FILES[v.f.replace(/\.mp3$/, '')] = { a, t, v }; })));

const now = () => Math.floor(Date.now() / 1000);
const json = (d, s = 200, h = {}) => new Response(JSON.stringify(d), { status: s, headers: { 'content-type': 'application/json', 'cache-control': 'no-store', ...h } });
const err = (s, m) => json({ error: m }, s);
const hex = b => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('');
const sha = async s => hex(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)));
const rand = (n = 24) => btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(n)))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const eqStr = (a, b) => { if (!a || !b || a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; };
const cleanEmail = e => String(e || '').trim().toLowerCase();
const safeName = s => String(s).replace(/[\\/:*?"<>|]+/g, '').replace(/\s+/g, ' ').trim();

function fileName(key, fmt, idx) {
  const x = FILES[key]; if (!x) return key.split('/').pop() + '.' + fmt;
  return safeName((idx != null ? String(idx + 1).padStart(2, '0') + ' ' : '') + x.a.a + ' - ' + x.t.t + (x.v.l ? ' (' + x.v.l + ')' : '')) + '.' + fmt;
}

async function body(req) { try { return await req.json(); } catch { return {}; } }

async function currentUser(req, env) {
  const m = (req.headers.get('cookie') || '').match(new RegExp('(?:^|; )' + COOKIE + '=([^;]+)'));
  if (!m) return null;
  const s = await env.DB.prepare('SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token_hash = ? AND s.expires_at > ? AND u.disabled = 0')
    .bind(await sha(m[1]), now()).first();
  return s || null;
}
const isAdmin = u => u && u.role === 'admin';
const userLevel = u => !u ? 0 : isAdmin(u) ? 2 : LEVEL[u.download] || 0;

async function logEvent(env, req, e) {
  await env.DB.prepare('INSERT INTO events (ts, kind, user_id, share, file, fmt, n, country) VALUES (?,?,?,?,?,?,?,?)')
    .bind(now(), e.kind, e.user_id || null, e.share || null, e.file || null, e.fmt || null, e.n || null, (req.cf && req.cf.country) || null).run();
}

async function getShare(env, token) {
  if (!token) return null;
  const s = await env.DB.prepare('SELECT * FROM shares WHERE token = ?').bind(token).first();
  if (!s || s.revoked || (s.expires_at && s.expires_at < now())) return null;
  return s;
}
async function shareFiles(env, s) {
  if (s.kind === 'album') { const a = CATALOG.albums.find(x => x.id === s.ref); return a ? a.tracks.flatMap(t => t.v.map(v => v.f.replace(/\.mp3$/, ''))) : []; }
  return (await env.DB.prepare('SELECT file FROM playlist_items WHERE playlist_id = ? ORDER BY position').bind(+s.ref).all()).results.map(r => r.file);
}
async function playlistFor(env, u, id) {
  const p = await env.DB.prepare('SELECT * FROM playlists WHERE id = ?').bind(+id).first();
  if (!p || (!isAdmin(u) && p.owner_id !== u.id)) return null;
  return p;
}

// ---------- ZIP (store, no compression; CRC32 + sizes precomputed in the files table) ----------
function dosTime(d = new Date()) {
  return { time: (d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1), date: ((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate() };
}
function zipPlan(entries) { // entries: [{name, size, crc, key, bucket}]
  const enc = new TextEncoder(), t = dosTime(); let off = 0; const locals = [], centrals = [];
  for (const e of entries) {
    const nb = enc.encode(e.name), l = new DataView(new ArrayBuffer(30));
    l.setUint32(0, 0x04034b50, true); l.setUint16(4, 20, true); l.setUint16(6, 0x0800, true); l.setUint16(8, 0, true);
    l.setUint16(10, t.time, true); l.setUint16(12, t.date, true); l.setUint32(14, e.crc >>> 0, true);
    l.setUint32(18, e.size, true); l.setUint32(22, e.size, true); l.setUint16(26, nb.length, true); l.setUint16(28, 0, true);
    const head = new Uint8Array(30 + nb.length); head.set(new Uint8Array(l.buffer)); head.set(nb, 30);
    const c = new DataView(new ArrayBuffer(46));
    c.setUint32(0, 0x02014b50, true); c.setUint16(4, 20, true); c.setUint16(6, 20, true); c.setUint16(8, 0x0800, true); c.setUint16(10, 0, true);
    c.setUint16(12, t.time, true); c.setUint16(14, t.date, true); c.setUint32(16, e.crc >>> 0, true); c.setUint32(20, e.size, true); c.setUint32(24, e.size, true);
    c.setUint16(28, nb.length, true); c.setUint32(42, off, true);
    const cen = new Uint8Array(46 + nb.length); cen.set(new Uint8Array(c.buffer)); cen.set(nb, 46);
    locals.push(head); centrals.push(cen); off += head.length + e.size;
  }
  const cdSize = centrals.reduce((a, c) => a + c.length, 0), end = new DataView(new ArrayBuffer(22));
  end.setUint32(0, 0x06054b50, true); end.setUint16(8, entries.length, true); end.setUint16(10, entries.length, true);
  end.setUint32(12, cdSize, true); end.setUint32(16, off, true);
  return { locals, centrals, end: new Uint8Array(end.buffer), total: off + cdSize + 22 };
}
async function zipResponse(env, ctx, entries, name) {
  const plan = zipPlan(entries);
  if (plan.total > 0xfff00000) return err(413, 'Too large for one download. Download WAVs in smaller groups.');
  const { readable, writable } = new FixedLengthStream(plan.total);
  ctx.waitUntil((async () => {
    let w = writable.getWriter();
    try {
      for (let i = 0; i < entries.length; i++) {
        await w.write(plan.locals[i]);
        const obj = await entries[i].bucket.get(entries[i].key);
        if (!obj) throw new Error('missing ' + entries[i].key);
        w.releaseLock(); await obj.body.pipeTo(writable, { preventClose: true }); w = writable.getWriter();
      }
      for (const c of plan.centrals) await w.write(c);
      await w.write(plan.end); await w.close();
    } catch (e) { try { await w.abort(e); } catch {} }
  })());
  return new Response(readable, { headers: { 'content-type': 'application/zip', 'content-disposition': `attachment; filename*=UTF-8''${encodeURIComponent(name)}` } });
}

// ---------- download permission ----------
async function canDownload(env, req, u, url, fmt) { // returns { ok, share, files? }
  const need = LEVEL[fmt]; if (!need) return { ok: false };
  const st = url.searchParams.get('s');
  if (st) {
    const s = await getShare(env, st); if (!s || (LEVEL[s.download] || 0) < need) return { ok: false };
    return { ok: true, share: s, files: await shareFiles(env, s) };
  }
  return { ok: userLevel(u) >= need };
}

async function api(req, env, ctx, url, u) {
  const p = url.pathname, m = req.method;
  if (m === 'POST' && !(req.headers.get('content-type') || '').includes('application/json')) return err(415, 'JSON only');

  // ---- auth ----
  if (p === '/api/login' && m === 'POST') {
    const b = await body(req), email = cleanEmail(b.email);
    const fails = await env.DB.prepare('SELECT COUNT(*) n FROM login_fails WHERE email = ? AND ts > ?').bind(email, now() - 900).first();
    if (fails.n >= 6) return err(429, 'Too many attempts. Try again in 15 minutes.');
    const user = await env.DB.prepare('SELECT * FROM users WHERE email = ? AND disabled = 0').bind(email).first();
    if (!user || !user.pw_hash || !eqStr(await sha(user.pw_salt + String(b.key || '')), user.pw_hash)) {
      await env.DB.prepare('INSERT INTO login_fails (email, ts) VALUES (?, ?)').bind(email, now()).run();
      return err(401, 'Wrong email or password.');
    }
    return startSession(env, req, user);
  }
  if (p === '/api/logout' && m === 'POST') {
    const c = (req.headers.get('cookie') || '').match(new RegExp('(?:^|; )' + COOKIE + '=([^;]+)'));
    if (c) await env.DB.prepare('DELETE FROM sessions WHERE token_hash = ?').bind(await sha(c[1])).run();
    return json({ ok: true }, 200, { 'set-cookie': `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax` });
  }
  if (p.startsWith('/api/invite/') && m === 'GET') {
    const inv = await env.DB.prepare('SELECT * FROM invites WHERE token_hash = ? AND used_at IS NULL AND expires_at > ?').bind(await sha(p.slice(12)), now()).first();
    if (!inv) return err(404, 'This link has expired or was already used. Ask Ocho for a new one.');
    const user = await env.DB.prepare('SELECT name, company FROM users WHERE email = ?').bind(inv.email).first();
    return json({ email: inv.email, kind: inv.kind, name: user ? user.name : '' });
  }
  if (p === '/api/invite/accept' && m === 'POST') {
    const b = await body(req), th = await sha(String(b.token || ''));
    const inv = await env.DB.prepare('SELECT * FROM invites WHERE token_hash = ? AND used_at IS NULL AND expires_at > ?').bind(th, now()).first();
    if (!inv) return err(404, 'This link has expired or was already used.');
    if (!/^[0-9a-f]{64}$/.test(String(b.key || ''))) return err(400, 'Bad password data.');
    const salt = rand(16), h = await sha(salt + b.key);
    await env.DB.batch([
      env.DB.prepare('UPDATE users SET pw_salt = ?, pw_hash = ?, name = CASE WHEN ? != \'\' THEN ? ELSE name END WHERE email = ?').bind(salt, h, String(b.name || '').slice(0, 80), String(b.name || '').slice(0, 80), inv.email),
      env.DB.prepare('UPDATE invites SET used_at = ? WHERE token_hash = ?').bind(now(), th),
      env.DB.prepare('DELETE FROM sessions WHERE user_id = (SELECT id FROM users WHERE email = ?)').bind(inv.email),
    ]);
    const user = await env.DB.prepare('SELECT * FROM users WHERE email = ?').bind(inv.email).first();
    return startSession(env, req, user);
  }
  if (p.startsWith('/api/share/') && m === 'GET') { // public share page data
    const s = await getShare(env, p.slice(11)); if (!s) return err(404, 'This link is no longer active. Contact Ocho for a fresh one.');
    const files = await shareFiles(env, s);
    if (url.searchParams.get('view')) ctx.waitUntil(logEvent(env, req, { kind: 'view', share: s.token }));
    return json({ title: s.title, recipient: s.recipient, kind: s.kind, ref: s.ref, download: s.download, files });
  }
  if (p === '/api/event' && m === 'POST') {
    const b = await body(req);
    if (b.kind !== 'play' || !FILES[b.file]) return err(400, 'bad event');
    const s = b.share ? await getShare(env, b.share) : null;
    if (!u && !s) return err(401, 'login');
    await logEvent(env, req, { kind: 'play', user_id: u && u.id, share: s && s.token, file: b.file });
    return json({ ok: true });
  }

  // ---- everything below needs a login ----
  if (!u) return err(401, 'Please log in.');
  if (p === '/api/me') return json({ id: u.id, email: u.email, name: u.name, company: u.company, role: u.role, download: isAdmin(u) ? 'wav' : u.download });

  if (p === '/api/playlists' && m === 'GET') {
    const r = await env.DB.prepare(`SELECT p.*, u.name owner_name, u.email owner_email, (SELECT COUNT(*) FROM playlist_items i WHERE i.playlist_id = p.id) n
      FROM playlists p JOIN users u ON u.id = p.owner_id ${isAdmin(u) ? '' : 'WHERE p.owner_id = ?'} ORDER BY p.updated_at DESC`);
    return json((isAdmin(u) ? await r.all() : await r.bind(u.id).all()).results);
  }
  if (p === '/api/playlists' && m === 'POST') {
    const b = await body(req), name = String(b.name || '').trim().slice(0, 120) || 'Untitled playlist';
    const r = await env.DB.prepare('INSERT INTO playlists (owner_id, name, created_at, updated_at) VALUES (?,?,?,?) RETURNING id').bind(u.id, name, now(), now()).first();
    return json({ id: r.id });
  }
  let mm = p.match(/^\/api\/playlists\/(\d+)(\/add)?$/);
  if (mm) {
    const pl = await playlistFor(env, u, mm[1]); if (!pl) return err(404, 'Playlist not found.');
    if (m === 'GET') {
      const items = (await env.DB.prepare('SELECT file FROM playlist_items WHERE playlist_id = ? ORDER BY position').bind(pl.id).all()).results.map(r => r.file);
      return json({ ...pl, items });
    }
    if (m === 'DELETE') {
      await env.DB.batch([env.DB.prepare('DELETE FROM playlist_items WHERE playlist_id = ?').bind(pl.id), env.DB.prepare('DELETE FROM playlists WHERE id = ?').bind(pl.id),
        env.DB.prepare("UPDATE shares SET revoked = 1 WHERE kind = 'playlist' AND ref = ?").bind(String(pl.id))]);
      return json({ ok: true });
    }
    const b = await body(req), st = [];
    if (mm[2]) { // add files
      const files = (Array.isArray(b.files) ? b.files : [b.file]).filter(f => FILES[f]);
      const mx = await env.DB.prepare('SELECT COALESCE(MAX(position), -1) m FROM playlist_items WHERE playlist_id = ?').bind(pl.id).first();
      files.forEach((f, i) => st.push(env.DB.prepare('INSERT OR IGNORE INTO playlist_items (playlist_id, file, position, added_at) VALUES (?,?,?,?)').bind(pl.id, f, mx.m + 1 + i, now())));
    } else {
      if (b.name != null) st.push(env.DB.prepare('UPDATE playlists SET name = ? WHERE id = ?').bind(String(b.name).trim().slice(0, 120) || pl.name, pl.id));
      if (b.notes != null) st.push(env.DB.prepare('UPDATE playlists SET notes = ? WHERE id = ?').bind(String(b.notes).slice(0, 2000), pl.id));
      if (Array.isArray(b.items)) {
        st.push(env.DB.prepare('DELETE FROM playlist_items WHERE playlist_id = ?').bind(pl.id));
        [...new Set(b.items.filter(f => FILES[f]))].forEach((f, i) => st.push(env.DB.prepare('INSERT INTO playlist_items (playlist_id, file, position, added_at) VALUES (?,?,?,?)').bind(pl.id, f, i, now())));
      }
    }
    st.push(env.DB.prepare('UPDATE playlists SET updated_at = ? WHERE id = ?').bind(now(), pl.id));
    await env.DB.batch(st);
    return json({ ok: true });
  }

  // ---- admin ----
  if (!isAdmin(u)) return err(403, 'Admins only.');
  if (p === '/api/users' && m === 'GET') {
    return json((await env.DB.prepare(`SELECT u.id, u.email, u.name, u.company, u.role, u.download, u.disabled, u.created_at, u.last_login, (u.pw_hash IS NOT NULL) active,
      (SELECT COUNT(*) FROM events e WHERE e.user_id = u.id AND e.kind = 'play') plays,
      (SELECT COUNT(*) FROM events e WHERE e.user_id = u.id AND e.kind IN ('download','zip')) downloads
      FROM users u ORDER BY u.role, u.created_at DESC`).all()).results);
  }
  if (p === '/api/users' && m === 'POST') {
    const b = await body(req), email = cleanEmail(b.email);
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return err(400, 'Enter a valid email.');
    const role = b.role === 'admin' ? 'admin' : 'client', dl = LEVEL[b.download] != null ? b.download : 'mp3';
    await env.DB.prepare('INSERT INTO users (email, name, company, role, download, created_at) VALUES (?,?,?,?,?,?) ON CONFLICT(email) DO UPDATE SET name = excluded.name, company = excluded.company, role = excluded.role, download = excluded.download, disabled = 0')
      .bind(email, String(b.name || '').slice(0, 80), String(b.company || '').slice(0, 80), role, dl, now()).run();
    return json({ url: await makeInvite(env, url, email, 'invite', u.id) });
  }
  mm = p.match(/^\/api\/users\/(\d+)(\/reset)?$/);
  if (mm && m === 'POST') {
    const t = await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(+mm[1]).first(); if (!t) return err(404, 'No such user.');
    if (mm[2]) return json({ url: await makeInvite(env, url, t.email, t.pw_hash ? 'reset' : 'invite', u.id) });
    const b = await body(req);
    if (t.id === u.id && (b.role === 'client' || b.disabled)) return err(400, "You can't remove your own admin access.");
    await env.DB.prepare('UPDATE users SET download = COALESCE(?, download), role = COALESCE(?, role), disabled = COALESCE(?, disabled), name = COALESCE(?, name), company = COALESCE(?, company) WHERE id = ?')
      .bind(LEVEL[b.download] != null ? b.download : null, ['admin', 'client'].includes(b.role) ? b.role : null, b.disabled == null ? null : (b.disabled ? 1 : 0),
        b.name == null ? null : String(b.name).slice(0, 80), b.company == null ? null : String(b.company).slice(0, 80), t.id).run();
    if (b.disabled) await env.DB.prepare('DELETE FROM sessions WHERE user_id = ?').bind(t.id).run();
    return json({ ok: true });
  }
  if (p === '/api/shares' && m === 'GET') {
    return json((await env.DB.prepare(`SELECT s.*, u.name creator,
      (SELECT COUNT(*) FROM events e WHERE e.share = s.token AND e.kind = 'view') views,
      (SELECT COUNT(*) FROM events e WHERE e.share = s.token AND e.kind = 'play') plays,
      (SELECT COUNT(*) FROM events e WHERE e.share = s.token AND e.kind IN ('download','zip')) downloads,
      (SELECT MAX(ts) FROM events e WHERE e.share = s.token) last_seen
      FROM shares s JOIN users u ON u.id = s.created_by ORDER BY s.created_at DESC`).all()).results);
  }
  if (p === '/api/shares' && m === 'POST') {
    const b = await body(req), kind = b.kind === 'album' ? 'album' : 'playlist';
    if (kind === 'album' && !CATALOG.albums.some(a => a.id === b.ref)) return err(400, 'Unknown album.');
    if (kind === 'playlist' && !(await playlistFor(env, u, b.ref))) return err(400, 'Unknown playlist.');
    const token = rand(12), days = +b.days || 0;
    await env.DB.prepare('INSERT INTO shares (token, kind, ref, title, recipient, download, created_by, created_at, expires_at) VALUES (?,?,?,?,?,?,?,?,?)')
      .bind(token, kind, String(b.ref), String(b.title || '').slice(0, 120) || 'Ocho Music Group', String(b.recipient || '').slice(0, 120),
        LEVEL[b.download] != null ? b.download : 'none', u.id, now(), days ? now() + days * DAY : null).run();
    return json({ token, url: url.origin + '/s/' + token });
  }
  mm = p.match(/^\/api\/shares\/([\w-]+)$/);
  if (mm && m === 'POST') {
    const b = await body(req);
    await env.DB.prepare('UPDATE shares SET revoked = COALESCE(?, revoked), download = COALESCE(?, download) WHERE token = ?')
      .bind(b.revoked == null ? null : (b.revoked ? 1 : 0), LEVEL[b.download] != null ? b.download : null, mm[1]).run();
    return json({ ok: true });
  }
  if (p === '/api/stats' && m === 'GET') return json(await stats(env, Math.min(365, Math.max(1, +url.searchParams.get('days') || 30))));
  return err(404, 'Not found.');
}

async function makeInvite(env, url, email, kind, by) {
  const token = rand(24);
  await env.DB.prepare('INSERT INTO invites (token_hash, email, kind, created_by, created_at, expires_at) VALUES (?,?,?,?,?,?)')
    .bind(await sha(token), email, kind, by, now(), now() + (kind === 'reset' ? 3 : 14) * DAY).run();
  return url.origin + '/' + (kind === 'reset' ? 'reset' : 'invite') + '/' + token;
}

async function startSession(env, req, user) {
  const token = rand(32);
  await env.DB.batch([
    env.DB.prepare('INSERT INTO sessions (token_hash, user_id, created_at, expires_at) VALUES (?,?,?,?)').bind(await sha(token), user.id, now(), now() + 30 * DAY),
    env.DB.prepare('UPDATE users SET last_login = ? WHERE id = ?').bind(now(), user.id),
    env.DB.prepare('DELETE FROM sessions WHERE expires_at < ?').bind(now()),
    env.DB.prepare('DELETE FROM login_fails WHERE ts < ?').bind(now() - 3600),
    env.DB.prepare("INSERT INTO events (ts, kind, user_id, country) VALUES (?, 'login', ?, ?)").bind(now(), user.id, (req.cf && req.cf.country) || null),
  ]);
  return json({ ok: true }, 200, { 'set-cookie': `${COOKIE}=${token}; Path=/; Max-Age=${30 * DAY}; HttpOnly; Secure; SameSite=Lax` });
}

async function stats(env, days) {
  const since = now() - days * DAY, q = (s, ...a) => env.DB.prepare(s).bind(...a);
  const [tot, daily, topPlay, topDl, shares, feed, users] = await env.DB.batch([
    q(`SELECT kind, COUNT(*) n, COUNT(DISTINCT COALESCE(user_id, share)) who FROM events WHERE ts > ? GROUP BY kind`, since),
    q(`SELECT date(ts, 'unixepoch') d, kind, COUNT(*) n FROM events WHERE ts > ? AND kind IN ('play','download','zip','view') GROUP BY d, kind ORDER BY d`, since),
    q(`SELECT file, COUNT(*) n FROM events WHERE ts > ? AND kind = 'play' GROUP BY file ORDER BY n DESC LIMIT 10`, since),
    q(`SELECT file, COUNT(*) n FROM events WHERE ts > ? AND kind = 'download' GROUP BY file ORDER BY n DESC LIMIT 10`, since),
    q(`SELECT s.token, s.title, s.recipient, s.download,
        SUM(e.kind = 'view') views, SUM(e.kind = 'play') plays, SUM(e.kind IN ('download','zip')) downloads, MAX(e.ts) last_seen
       FROM shares s JOIN events e ON e.share = s.token WHERE e.ts > ? GROUP BY s.token ORDER BY last_seen DESC LIMIT 25`, since),
    q(`SELECT e.ts, e.kind, e.file, e.fmt, e.n, e.country, u.name uname, u.email uemail, u.company ucompany, s.title stitle, s.recipient srecipient
       FROM events e LEFT JOIN users u ON u.id = e.user_id LEFT JOIN shares s ON s.token = e.share
       WHERE e.ts > ? ORDER BY e.ts DESC LIMIT 80`, since),
    q(`SELECT u.id, u.name, u.email, u.company, u.last_login, SUM(e.kind = 'play') plays, SUM(e.kind IN ('download','zip')) downloads, MAX(e.ts) last_seen
       FROM users u JOIN events e ON e.user_id = u.id WHERE e.ts > ? AND u.role = 'client' GROUP BY u.id ORDER BY last_seen DESC LIMIT 25`, since),
  ]);
  return { days, totals: tot.results, daily: daily.results, topPlays: topPlay.results, topDownloads: topDl.results, shares: shares.results, feed: feed.results, users: users.results };
}

async function download(req, env, ctx, url, u) {
  const fmt = url.searchParams.get('fmt') === 'wav' ? 'wav' : 'mp3';
  const perm = await canDownload(env, req, u, url, fmt);
  if (!perm.ok) return err(403, 'Downloads are not enabled for this link.');
  const bucket = fmt === 'wav' ? env.MASTERS : env.AUDIO;

  if (url.pathname === '/dl') {
    const key = url.searchParams.get('f') || '';
    if (!FILES[key] || (perm.files && !perm.files.includes(key))) return err(404, 'File not found.');
    const obj = await bucket.get(key + '.' + fmt);
    if (!obj) return err(404, fmt === 'wav' ? 'The WAV for this track is not available yet. Contact Ocho.' : 'File not found.');
    ctx.waitUntil(logEvent(env, req, { kind: 'download', user_id: u && u.id, share: perm.share && perm.share.token, file: key, fmt }));
    return new Response(obj.body, { headers: { 'content-type': fmt === 'wav' ? 'audio/wav' : 'audio/mpeg', 'content-length': obj.size,
      'content-disposition': `attachment; filename*=UTF-8''${encodeURIComponent(fileName(key, fmt))}` } });
  }

  // /zip: a share, one of the user's playlists, or an album
  let files, title;
  if (perm.share) { files = perm.files; title = perm.share.title; }
  else if (url.searchParams.get('playlist')) {
    const pl = u && await playlistFor(env, u, url.searchParams.get('playlist')); if (!pl) return err(404, 'Playlist not found.');
    files = (await env.DB.prepare('SELECT file FROM playlist_items WHERE playlist_id = ? ORDER BY position').bind(pl.id).all()).results.map(r => r.file); title = pl.name;
  } else {
    const a = CATALOG.albums.find(x => x.id === url.searchParams.get('album')); if (!a) return err(404, 'Album not found.');
    files = a.tracks.flatMap(t => t.v.map(v => v.f.replace(/\.mp3$/, ''))); title = a.id + ' ' + a.t;
  }
  const only = url.searchParams.get('only'); if (only) files = files.filter(f => only.split(',').includes(f));
  files = files.filter(f => FILES[f]); if (!files.length) return err(404, 'Nothing to download.');
  const keys = files.map(f => f + '.' + fmt), meta = {};
  for (let i = 0; i < keys.length; i += 90) {
    const part = keys.slice(i, i + 90);
    (await env.DB.prepare(`SELECT key, size, crc FROM files WHERE key IN (${part.map(() => '?').join(',')})`).bind(...part).all()).results.forEach(r => { meta[r.key] = r; });
  }
  const missing = keys.filter(k => !meta[k]);
  if (missing.length) return err(409, missing.length + ' of these files are not ready for ZIP download yet. Download them one at a time, or try again later.');
  ctx.waitUntil(logEvent(env, req, { kind: 'zip', user_id: u && u.id, share: perm.share && perm.share.token, fmt, n: files.length,
    file: url.searchParams.get('album') || (url.searchParams.get('playlist') ? 'playlist:' + url.searchParams.get('playlist') : null) }));
  return zipResponse(env, ctx, files.map((f, i) => ({ name: fileName(f, fmt, i), size: meta[f + '.' + fmt].size, crc: meta[f + '.' + fmt].crc, key: f + '.' + fmt, bucket })),
    safeName('Ocho Music Group - ' + title) + ' (' + fmt.toUpperCase() + ').zip');
}

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    try {
      if (url.pathname === '/catalog.json') return new Response(JSON.stringify(CATALOG), { headers: { 'content-type': 'application/json', 'cache-control': 'public, max-age=300' } });
      const u = await currentUser(req, env);
      if (url.pathname.startsWith('/api/')) return await api(req, env, ctx, url, u);
      if (url.pathname === '/dl' || url.pathname === '/zip') return await download(req, env, ctx, url, u);
      if (req.method !== 'GET') return err(405, 'Method not allowed');
      let title = 'Ocho Music Group | Client Portal', desc = 'Authentic Latin music for film, TV & ads. Stream, build playlists and download.';
      const sm = url.pathname.match(/^\/s\/([\w-]+)/);
      if (sm) { const s = await getShare(env, sm[1]); if (s) { title = s.title + ' | Ocho Music Group'; desc = (s.recipient ? 'Selected for ' + s.recipient + '. ' : '') + 'Stream it now. Authentic Latin music for film, TV & ads.'; } }
      const at = x => x.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
      return new Response(HTML.split('__OG_TITLE__').join(at(title)).split('__OG_DESC__').join(at(desc)), { headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-frame-options': 'DENY',
        'referrer-policy': 'same-origin', 'x-robots-tag': 'noindex' } });
    } catch (e) {
      console.log(e && e.stack || e);
      return err(500, 'Something went wrong. Please try again.');
    }
  },
};
