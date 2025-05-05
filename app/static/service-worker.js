/* ------------------------------------------------------------------
   Leaky Meatbag PWA – Service Worker (Auto Versioning + Auto Reload)
   ------------------------------------------------------------------ */

/* 🔄  Auto-bump the cache version on every SW install */
const CACHE_VERSION = Date.now();                 // 👈 timestamp cache version
const CACHE_NAME    = `leaky-cache-${CACHE_VERSION}`;

/* Assets you want available offline */
const APP_SHELL = [
  '/',                           // dashboard / homepage
  '/static/css/main.css',
  '/static/js/dashboard.js',
  '/static/img/PWA/icon-192x192.png',
  '/static/img/PWA/icon-512x512.png',
];

/* ---------------------------------------------------------- */
/* INSTALL – pre-cache the app shell                          */
/* ---------------------------------------------------------- */
self.addEventListener('install', (event) => {
  self.skipWaiting();   // activate immediately
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL))
  );
});

/* ---------------------------------------------------------- */
/* ACTIVATE – clear old caches, take control, and reload pages */
/* ---------------------------------------------------------- */
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key.startsWith('leaky-cache-') && key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
    .then(() => {
      // 👇 Force all open tabs to reload after new SW activation
      return self.clients.matchAll({ type: 'window' }).then(clients => {
        clients.forEach(client => client.navigate(client.url));
      });
    })
  );
});

/* ---------------------------------------------------------- */
/* FETCH – cache-first, then fallback to network              */
/* ---------------------------------------------------------- */
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then(
      (cached) => cached || fetch(event.request)
    )
  );
});
