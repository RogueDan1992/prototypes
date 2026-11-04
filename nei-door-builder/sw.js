// NEI Door Builder service worker — offline support.
// App page: network first (so updates arrive), cached copy when offline.
// Libraries, logos and door/glass pictures: served from the cache once saved.
// Supabase data is not cached here; the app keeps its own saved copy of the catalog.
const SHELL = "nei-door-shell-v4", PICS = "nei-door-pics-v2";
const SHELL_FILES = ["./", "index.html", "manifest.webmanifest", "logo.png", "logo-onblack.png",
  "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js",
  "https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.4.0/exceljs.min.js"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(SHELL).then((c) => Promise.all(SHELL_FILES.map((u) => c.add(new Request(u, { cache: "reload" })).catch(() => {})))));
  self.skipWaiting();
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k.startsWith("nei-door-") && k !== SHELL && k !== PICS).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

const isPic = (u) => u.origin === location.origin && /\/img\//.test(u.pathname) || /supabase\.co\/storage\/v1\/object\/public\//.test(u.href);
const isLib = (u) => /cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com/.test(u.host);

self.addEventListener("fetch", (e) => {
  const r = e.request; if (r.method !== "GET") return;
  const u = new URL(r.url);
  if (r.mode === "navigate" || (u.origin === location.origin && /\/(index\.html)?$/.test(u.pathname))) {
    e.respondWith(fetch(r).then((res) => { const cp = res.clone(); caches.open(SHELL).then((c) => c.put("index.html", cp)); return res; })
      .catch(() => caches.match("index.html", { ignoreSearch: true }).then((m) => m || caches.match("./"))));
    return;
  }
  if (isPic(u) || isLib(u) || (u.origin === location.origin && /\.(png|jpg|jpeg|webp|svg|webmanifest)$/.test(u.pathname))) {
    const store = isLib(u) ? SHELL : PICS;
    e.respondWith(caches.match(r).then((m) => m || fetch(r).then((res) => { if (res.ok || res.type === "opaque") { const cp = res.clone(); caches.open(store).then((c) => c.put(r, cp)); } return res; })));
  }
});

// "Save pictures for offline": the page sends every picture address; we fetch the ones not saved yet.
self.addEventListener("message", (e) => {
  if (!e.data || e.data.type !== "precache") return;
  const urls = [...new Set(e.data.urls)], port = e.ports[0];
  e.waitUntil((async () => {
    const c = await caches.open(PICS); let done = 0, failed = 0;
    const todo = [];
    for (const u of urls) { if (!(await c.match(u))) todo.push(u); else done++; }
    port && port.postMessage({ done, total: urls.length, failed });
    let i = 0;
    const worker = async () => { while (i < todo.length) { const u = todo[i++]; try { const res = await fetch(u); if (res.ok) await c.put(u, res); else failed++; } catch (_) { failed++; } done++; if (done % 10 === 0 || done === urls.length) port && port.postMessage({ done, total: urls.length, failed }); } };
    await Promise.all([worker(), worker(), worker(), worker()]);
    port && port.postMessage({ done, total: urls.length, failed, finished: true });
  })());
});
