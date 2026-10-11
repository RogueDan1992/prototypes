// The game moved to ../penny-to-plenty/. Remove the old offline copy and reload into the new address.
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf('from-nothing-') === 0; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.registration.unregister(); }).then(function () { return self.clients.matchAll(); })
    .then(function (cs) { cs.forEach(function (c) { c.navigate('../penny-to-plenty/'); }); }));
});
