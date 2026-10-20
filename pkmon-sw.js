/* PKmon service worker: app shell offline, network-first for the page, never caches API calls */
const SHELL = "pkmon-shell-v5";
const FILES = ["./", "index.html", "pkmon.webmanifest", "pkmon-icon.svg", "pkmon-192.png", "pkmon-512.png", "pkmon-maskable-512.png", "apple-touch-icon.png"];
self.addEventListener("install", e => e.waitUntil(caches.open(SHELL).then(c => c.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== SHELL && k !== "pkmon-index").map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;
  if (/pkmon-(cards\.json|fp\.bin)$/.test(u.pathname)) return;   // the app keeps the card list and fingerprints in its own cache
  e.respondWith(fetch(e.request).then(r => { const copy = r.clone(); caches.open(SHELL).then(c => c.put(e.request, copy)); return r; }).catch(() => caches.match(e.request, { ignoreSearch: true })));
});
