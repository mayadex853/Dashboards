// Small client-side fetch helper.
export async function api(path, { method = "GET", body, form } = {}) {
  const res = await fetch(path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: form || (body ? JSON.stringify(body) : undefined),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(json.error || `Request failed (${res.status})`);
  return json;
}

export const fmtDate = (t) => (t ? new Date(t).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }) : "—");

// Hand freshly generated signing links to the envelope page (they're only shown once).
export function stashLinks(res) {
  try {
    if (res.links?.length) sessionStorage.setItem(`links:${res.envelope.id}`, JSON.stringify(res.links));
  } catch {}
}
export function takeLinks(id) {
  try {
    const v = sessionStorage.getItem(`links:${id}`);
    sessionStorage.removeItem(`links:${id}`);
    return v ? JSON.parse(v) : [];
  } catch {
    return [];
  }
}
