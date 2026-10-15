const V='v11',F=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png','icon-512-maskable.png'],O=['en','de','nl'].map(l=>'tr-'+l+'.js').concat(['links.js','gloss.js','quiz.js','Amiri-Regular.ttf','Amiri-Bold.ttf']);
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(F).then(()=>Promise.all(O.map(u=>c.add(u).catch(()=>{}))))).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;
e.respondWith(fetch(e.request).then(r=>{const c=r.clone();caches.open(V).then(ch=>ch.put(e.request,c));return r}).catch(()=>caches.match(e.request).then(m=>m||caches.match('index.html'))))});
