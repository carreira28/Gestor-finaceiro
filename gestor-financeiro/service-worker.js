self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('gestor-financeiro-cache').then((cache) => {
      return cache.addAll([
        '/',
        '/static/style.css',
        '/static/app.js',
        '/static/manifest.json',
        '/static/icons/icon-192x192.png',
        '/static/icons/icon-512x512.png',
        '/static/images/load-36_256.gif',
        '/static/images/despesa.png',
        '/static/images/fundo.jpg',
        '/static/images/logo.png',
        '/static/images/poupanca.png',
        '/static/images/renda.png'
      ]);
    })
  );
  self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      return cachedResponse || fetch(event.request);
    })
  );
});
