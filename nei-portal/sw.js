/* Offline service worker. Cache-first; one cache per version. */
var CACHE = 'nei-portal-1.0.0';
var FILES = ["./", "./index.html", "./manifest.webmanifest", "./d3.min.js", "./fonts/fonts.css", "./icons/icon-180.png", "./icons/icon-192.png", "./icons/icon-512.png", "./fonts/barlow-latin-400-normal.woff2", "./fonts/barlow-latin-500-normal.woff2", "./fonts/barlow-latin-600-normal.woff2", "./fonts/barlow-latin-700-normal.woff2", "./fonts/barlow-semi-condensed-latin-500-normal.woff2", "./fonts/barlow-semi-condensed-latin-600-normal.woff2", "./fonts/barlow-semi-condensed-latin-700-normal.woff2", "./fonts/barlow-semi-condensed-latin-800-normal.woff2", "./fonts/ibm-plex-mono-latin-400-normal.woff2", "./fonts/ibm-plex-mono-latin-500-normal.woff2", "./fonts/ibm-plex-mono-latin-600-normal.woff2"];
self.addEventListener('install', function (e) { e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(FILES); })); });
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf('nei-portal-') === 0 && k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  e.respondWith(caches.open(CACHE).then(function (c) {
    return c.match(req, { ignoreSearch: true }).then(function (hit) {
      return hit || fetch(req).catch(function () { return req.mode === 'navigate' ? c.match('./index.html') : Response.error(); });
    });
  }));
});
self.addEventListener('message', function (e) { if (e.data === 'skipWaiting') self.skipWaiting(); });
