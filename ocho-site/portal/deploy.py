"""Deploy the client portal to Cloudflare (needs CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID).

  python3 deploy.py schema                 create/upgrade D1 tables (schema.sql, idempotent)
  python3 deploy.py files MANIFEST.jsonl   load {key,size,crc} lines into the files table (for ZIP downloads)
  python3 deploy.py worker                 build dist/worker.js and upload it with its bindings
  python3 deploy.py domain                 attach portal.ochoaudio.com to the worker
  python3 deploy.py invite EMAIL "NAME" [admin|client] [none|mp3|wav]   create/refresh a user and print a set-password link
"""
import hashlib
import json
import os
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
ACC, TOK = os.environ["CLOUDFLARE_ACCOUNT_ID"], os.environ["CLOUDFLARE_API_TOKEN"]
API = f"https://api.cloudflare.com/client/v4/accounts/{ACC}"
DB_NAME, SCRIPT, HOST, ZONE = "ocho-portal", "ocho-portal", "portal.ochoaudio.com", "ochoaudio.com"


def call(method, url, body=None, ctype="application/json"):
    data = body if isinstance(body, (bytes, type(None))) else json.dumps(body).encode()
    req = urllib.request.Request(url if url.startswith("http") else API + url, data=data, method=method,
                                 headers={"Authorization": "Bearer " + TOK, "User-Agent": "ocho-portal", **({"Content-Type": ctype} if data else {})})
    try:
        return json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {url}: {e.code} {e.read()[:500].decode(errors='replace')}")


def db_id():
    return next(d["uuid"] for d in call("GET", "/d1/database")["result"] if d["name"] == DB_NAME)


def sql(statement, params=None):
    r = call("POST", f"/d1/database/{db_id()}/query", {"sql": statement, "params": params or []})
    return r["result"][0]["results"] if r["result"] else []


def schema():
    for st in (s.strip() for s in (HERE / "schema.sql").read_text().split(";")):
        lines = [l for l in st.splitlines() if not l.strip().startswith("--")]
        if "\n".join(lines).strip():
            sql("\n".join(lines))
    print("schema ok")


def files(path):
    rows = [json.loads(l) for l in open(path) if l.strip()]
    dbid = db_id()
    for i in range(0, len(rows), 30):
        part = rows[i:i + 30]
        call("POST", f"/d1/database/{dbid}/query", {"sql": "INSERT OR REPLACE INTO files (key, size, crc) VALUES " + ",".join(["(?,?,?)"] * len(part)),
                                                   "params": [v for r in part for v in (r["key"], r["size"], r["crc"])]})
    print(f"files: {len(rows)} rows")


def worker():
    subprocess.run([sys.executable, str(HERE / "build.py")], check=True)
    meta = {"main_module": "worker.js", "compatibility_date": "2026-11-01",
            "bindings": [{"type": "d1", "name": "DB", "id": db_id()},
                         {"type": "r2_bucket", "name": "AUDIO", "bucket_name": "ocho-audio"},
                         {"type": "r2_bucket", "name": "MASTERS", "bucket_name": "ocho-masters"}]}
    b = "----ocho" + secrets.token_hex(8)
    code = (HERE / "dist" / "worker.js").read_bytes()
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"metadata\"\r\nContent-Type: application/json\r\n\r\n{json.dumps(meta)}\r\n"
            f"--{b}\r\nContent-Disposition: form-data; name=\"worker.js\"; filename=\"worker.js\"\r\nContent-Type: application/javascript+module\r\n\r\n").encode() + code + f"\r\n--{b}--\r\n".encode()
    r = call("PUT", f"/workers/scripts/{SCRIPT}", body, "multipart/form-data; boundary=" + b)
    print("worker uploaded:", r["success"])


def domain():
    zone = call("GET", f"https://api.cloudflare.com/client/v4/zones?name={ZONE}")["result"][0]["id"]
    r = call("PUT", "/workers/domains", {"environment": "production", "hostname": HOST, "service": SCRIPT, "zone_id": zone})
    print("domain:", r["success"], HOST)


def invite(email, name="", role="client", download="mp3"):
    email = email.strip().lower()
    now = int(time.time())
    sql("INSERT INTO users (email, name, role, download, created_at) VALUES (?,?,?,?,?) ON CONFLICT(email) DO UPDATE SET role = excluded.role, download = excluded.download, disabled = 0, name = CASE WHEN excluded.name != '' THEN excluded.name ELSE users.name END",
        [email, name, role, download, now])
    has_pw = sql("SELECT pw_hash IS NOT NULL p FROM users WHERE email = ?", [email])[0]["p"]
    token = secrets.token_urlsafe(24)
    kind = "reset" if has_pw else "invite"
    sql("INSERT INTO invites (token_hash, email, kind, created_at, expires_at) VALUES (?,?,?,?,?)",
        [hashlib.sha256(token.encode()).hexdigest(), email, kind, now, now + 14 * 86400])
    print(f"https://{HOST}/{kind}/{token}")


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    {"schema": schema, "files": files, "worker": worker, "domain": domain, "invite": invite}[cmd](*args)
