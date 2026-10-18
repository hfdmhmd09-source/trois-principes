const V='v18',F=['./','book.js','index.html','manifest.webmanifest','icon-192.png','icon-512.png','icon-512-maskable.png'],O=['en','de','nl'].map(l=>'tr-'+l+'.js').concat(['links.js','gloss.js','quiz.js','audio.js','Amiri-Regular.ttf','Amiri-Bold.ttf']);
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(F).then(()=>Promise.all(O.map(u=>c.add(u).catch(()=>{}))))).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V&&x!=='audio').map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;if(/\.mp3$/.test(new URL(e.request.url).pathname)){e.respondWith(audioResp(e.request));return}
e.respondWith(fetch(e.request).then(r=>{const c=r.clone();caches.open(V).then(ch=>ch.put(e.request,c));return r}).catch(()=>caches.match(e.request).then(m=>m||caches.match('index.html'))))});

async function audioResp(req){const c=await caches.open('audio'),r=await c.match(req.url);if(!r)return fetch(req);
const rg=req.headers.get('range');if(!rg)return r;const b=await r.blob(),m=/bytes=(\d+)-(\d*)/.exec(rg);if(!m)return r;const st=+m[1],en=m[2]?Math.min(+m[2],b.size-1):b.size-1;
return new Response(b.slice(st,en+1),{status:206,headers:{'Content-Type':'audio/mpeg','Content-Range':'bytes '+st+'-'+en+'/'+b.size,'Content-Length':String(en-st+1)}})}
