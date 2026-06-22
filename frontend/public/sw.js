// Service worker mínimo: habilita la instalación de la PWA sin caché offline.
// Para activar caché offline en el futuro, añadir lógica en el handler fetch.

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));

// Chrome requiere un handler fetch registrado para mostrar el prompt de instalación.
// Este pasa todas las peticiones directamente a la red (sin caché).
self.addEventListener("fetch", (e) => {
  e.respondWith(fetch(e.request));
});
