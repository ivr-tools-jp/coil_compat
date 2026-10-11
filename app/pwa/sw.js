/* オフライン用の Service Worker。キャッシュ名と ASSETS の中身は build.py が埋める。
   画面（index.html）はネット優先：つながれば最新のデータ、つながらない・遅い（4秒）ときは前回の写しを出す。 */
const CACHE = "cc-__VERSION__";
const FONT_CACHE = "cc-fonts-v1";
const ASSETS = __ASSETS__;
const FONT_HOSTS = ["fonts.googleapis.com", "fonts.gstatic.com"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith("cc-") && k !== CACHE && k !== FONT_CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

async function page(req){
  const cache = await caches.open(CACHE);
  const net = fetch(req).then(res => { if(res.ok) cache.put("./", res.clone()); return res; });
  const cached = await cache.match("./");
  if(!cached) return net;
  const late = new Promise(r => setTimeout(() => r(cached), 4000));
  return Promise.race([net.catch(() => cached), late]);
}

async function font(req){
  const cache = await caches.open(FONT_CACHE);
  const hit = await cache.match(req);
  if(hit) return hit;
  const res = await fetch(req);
  if(res.ok || res.type === "opaque") cache.put(req, res.clone());
  return res;
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if(req.method !== "GET") return;
  const url = new URL(req.url);
  const isIndex = url.origin === location.origin && /\/(index\.html)?$/.test(url.pathname);
  if(req.mode === "navigate" && isIndex) return e.respondWith(page(req));
  if(FONT_HOSTS.includes(url.hostname)) return e.respondWith(font(req));
  if(url.origin === location.origin)
    e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
});
