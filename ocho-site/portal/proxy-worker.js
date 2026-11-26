// Pass-through for portal.ochomusicgroup.com (deployed in the Cloudflare account that holds ochomusicgroup.com).
// Every request is forwarded unchanged to the portal app at portal.ochoaudio.com; the browser only ever sees
// portal.ochomusicgroup.com (logins, share links and downloads all stay on this address).
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const target = 'https://portal.ochoaudio.com' + url.pathname + url.search;
    const headers = new Headers(request.headers);
    headers.set('x-ocho-host', url.hostname);
    headers.set('x-ocho-country', request.headers.get('cf-ipcountry') || '');
    return fetch(target, {
      method: request.method,
      headers,
      body: ['GET', 'HEAD'].includes(request.method) ? undefined : request.body,
      redirect: 'manual',
    });
  },
};
