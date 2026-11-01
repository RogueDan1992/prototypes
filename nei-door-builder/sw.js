// NEI Door Builder service worker: lets phones install the app. It does not cache, so everyone always gets the latest version.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", () => {});
