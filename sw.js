/* Cache the app shell and form clips so the home-screen PWA works offline. */
const CACHE = "mike-gym-v3";
const PRECACHE = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon-192.png",
  "./icon-512.png",
  "./apple-touch-icon.png",
  "./media/a1.gif",
  "./media/a2.gif",
  "./media/a3.gif",
  "./media/a4.gif",
  "./media/a5.gif",
  "./media/a6.gif",
  "./media/b1.gif",
  "./media/b2.gif",
  "./media/b3.gif",
  "./media/b4.gif",
  "./media/b5.gif",
  "./media/b6.gif",
  "./media/c1.gif",
  "./media/c2.gif",
  "./media/c3.gif",
  "./media/c4.gif",
  "./media/c5.gif",
  "./media/c6.gif",
  "./media/d1.gif",
  "./media/d2.gif",
  "./media/d3.gif",
  "./media/d4.gif",
  "./media/d5.gif",
  "./media/d6.gif"
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE).then(function (cache) {
      return cache.addAll(PRECACHE);
    }).then(function () {
      return self.skipWaiting();
    })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (key) {
        return key !== CACHE;
      }).map(function (key) {
        return caches.delete(key);
      }));
    }).then(function () {
      return self.clients.claim();
    })
  );
});

self.addEventListener("fetch", function (event) {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (url.pathname.indexOf("/media/") !== -1 || url.pathname.endsWith(".gif")) {
    event.respondWith(
      caches.match(request).then(function (cached) {
        return cached || fetch(request).then(function (response) {
          if (response && response.ok) {
            const copy = response.clone();
            caches.open(CACHE).then(function (cache) { cache.put(request, copy); });
          }
          return response;
        });
      })
    );
    return;
  }

  event.respondWith(
    fetch(request).then(function (response) {
      if (response && response.ok) {
        const copy = response.clone();
        caches.open(CACHE).then(function (cache) { cache.put(request, copy); });
      }
      return response;
    }).catch(function () {
      return caches.match(request).then(function (cached) {
        return cached || caches.match("./index.html");
      });
    })
  );
});
