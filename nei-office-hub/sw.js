// NEI Hub service worker: shows phone/desktop alerts and opens the right item when tapped.
// It does not cache the app, so everyone always gets the latest version.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));

self.addEventListener("push", (e) => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch { d = { title: e.data ? e.data.text() : "" }; }
  const title = d.title || "NEI Hub";
  const jobs = [
    self.registration.showNotification(title, {
      body: d.body || "",
      icon: "icon-192.png",
      badge: "badge-96.png",
      tag: d.tag || undefined,
      data: { anchor: d.anchor || "" },
    }),
  ];
  if (typeof d.badge === "number" && self.navigator && "setAppBadge" in self.navigator) {
    jobs.push(d.badge > 0 ? self.navigator.setAppBadge(d.badge) : self.navigator.clearAppBadge());
  }
  jobs.push(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((cs) => cs.forEach((c) => c.postMessage({ type: "push" }))));
  e.waitUntil(Promise.all(jobs).catch(() => {}));
});

self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  const anchor = (e.notification.data && e.notification.data.anchor) || "";
  const url = new URL("./", self.registration.scope).href + (anchor ? "#" + anchor : "");
  e.waitUntil((async () => {
    const cs = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    const c = cs.find((x) => x.url.startsWith(self.registration.scope));
    if (c) {
      await c.focus();
      c.postMessage({ type: "open", anchor });
      return;
    }
    await self.clients.openWindow(url);
  })());
});
