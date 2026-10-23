/* Japanese Grammar Garden v0.2.4-dev: safer offline response handling */
const CACHE="jgg-v0.2.4-dev";
const ASSETS=["./","./index.html","./manifest.webmanifest","./icon.svg","./kanji-app.js","./kanji-app.css",
"./data/kanji/kanji-stage-1-100.draft.json","./data/kanji/kanji-stage-2-100.draft.json",
"./data/kanji/kanji-stage-3-100.draft.json","./data/kanji/kanji-stage-4-100.draft.json",
"./data/kanji/kanji-stage-5-100.draft.json"];
self.addEventListener("install",event=>{
  event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)));
});
self.addEventListener("activate",event=>{
  event.waitUntil((async()=>{
    const keys=await caches.keys();
    await Promise.all(keys.filter(key=>key.startsWith("jgg-")&&key!==CACHE).map(key=>caches.delete(key)));
    await self.clients.claim();
  })());
});
self.addEventListener("message",event=>{
  if(event.data&&event.data.type==="SKIP_WAITING")self.skipWaiting();
});
self.addEventListener("fetch",event=>{
  const req=event.request;
  const url=new URL(req.url);
  if(req.method!=="GET"||url.origin!==self.location.origin||!url.href.startsWith(self.registration.scope))return;
  event.respondWith((async()=>{
    const cache=await caches.open(CACHE);
    try{
      const response=await fetch(req);
      if(response.ok){try{await cache.put(req,response.clone())}catch(e){}}
      return response;
    }catch(e){
      const cached=await caches.match(req);
      if(cached)return cached;
      if(req.mode==="navigate"){
        const shell=await caches.match("./index.html");
        if(shell)return shell;
      }
      return Response.error();
    }
  })());
});
