/* Japanese Grammar Garden v0.3.8-dev: versioned offline shell */
const CACHE="jgg-v0.3.8-dev-layout2";
const ASSETS=["./docs/licenses/UNICODE.txt","./docs/licenses/EDRDG.html","./data/kanji/kanji-enrichment.json","./assets/icons/garden-v1/back.webp","./assets/icons/garden-v1/backup.webp","./assets/icons/garden-v1/book.webp","./assets/icons/garden-v1/calendar.webp","./assets/icons/garden-v1/close.webp","./assets/icons/garden-v1/home.webp","./assets/icons/garden-v1/info.webp","./assets/icons/garden-v1/pencil.webp","./assets/icons/garden-v1/play.webp","./assets/icons/garden-v1/restore.webp","./assets/icons/garden-v1/results.webp","./assets/icons/garden-v1/retry.webp","./assets/icons/garden-v1/settings.webp","./assets/icons/garden-v1/sound.webp","./data/kanji/kanji-extra-125.draft.json","./","./index.html","./manifest.webmanifest","./icon.svg","./app-ui.js","./grammar-lessons.js","./sentence-parts.js","./record-backup.js","./sources.html","./icons/apple-touch-icon.png","./icons/icon-192.png","./icons/icon-512.png","./kanji-app.js","./kanji-app.css",
"./data/kanji/kanji-stage-1-100.draft.json","./data/kanji/kanji-stage-2-100.draft.json","./data/kanji/kanji-stage-3-100.draft.json","./data/kanji/kanji-stage-4-100.draft.json","./data/kanji/kanji-stage-5-100.draft.json"];
const assetURLs=new Set(ASSETS.map(path=>new URL(path,self.registration.scope).href));
self.addEventListener("install",event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS.map(path=>new Request(new URL(path,self.registration.scope),{cache:"reload"}))))));
self.addEventListener("activate",event=>event.waitUntil((async()=>{const keys=await caches.keys();await Promise.all(keys.filter(key=>key.startsWith("jgg-")&&key!==CACHE).map(key=>caches.delete(key)));await self.clients.claim()})()));
self.addEventListener("message",event=>{if(event.data?.type==="SKIP_WAITING")self.skipWaiting()});
self.addEventListener("fetch",event=>{
 const req=event.request,url=new URL(req.url);if(req.method!=="GET"||url.origin!==self.location.origin||!url.href.startsWith(self.registration.scope))return;
 event.respondWith((async()=>{
 const cache=await caches.open(CACHE),canonical=new URL(url);canonical.search="";
 // Core assets always come from the active worker's complete install cache.
 if(assetURLs.has(canonical.href)){const cached=await cache.match(canonical.href);if(cached)return cached}
 try{const response=await fetch(req);if(response.ok)return response;const cached=await cache.match(req);if(cached)return cached;return response}
 catch(e){const cached=await cache.match(req);if(cached)return cached;if(req.mode==="navigate"){const shell=await cache.match(new URL("./index.html",self.registration.scope));if(shell)return shell}return Response.error()}
 })());
});
