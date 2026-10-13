/* オフライン用の Service Worker。キャッシュ名と ASSETS の中身は build.py が埋める。
   キャッシュ優先：画面・フォント・アイコンは手元の写しをすぐ出す（電波が弱くても待たない）。
   データや画面を直すと sw.js の中身（キャッシュ名）が変わり、ブラウザが新しい版を裏で受け取る。
   受け取ったら画面の下に「新しいデータがあります」を出し、押されたら切り替えて読み直す（tail.html）。 */
const CACHE = "cc-__VERSION__";
const ASSETS = __ASSETS__;
const TOP = new URL("./", self.location).pathname;  /* 公開版のトップ（…/coil_compat/） */

self.addEventListener("install", e => {
  /* ブラウザの HTTP キャッシュも配信側（CDN）のキャッシュも飛ばして、この版のものを取る（?v= を付けて取り、付けない名前で写す） */
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(ASSETS.map(async u => {
    const res = await fetch(new Request(u + (u.includes("?") ? "&" : "?") + "v=__VERSION__", {cache:"reload"}));
    if(!res.ok) throw new Error(u + " " + res.status);
    await c.put(u, res);
  }))));
});

self.addEventListener("message", e => { if(e.data === "skip") self.skipWaiting(); });

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith("cc-") && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if(req.method !== "GET") return;
  const url = new URL(req.url);
  if(url.origin !== location.origin) return;
  /* トップ（…/ と …/index.html）だけを写しから出す。ほかのページ（beta.html など）はネットに任せる */
  if(req.mode === "navigate"){
    if(url.pathname === TOP || url.pathname === TOP + "index.html")
      e.respondWith(caches.match("./").catch(() => null).then(hit => hit || fetch(req)));
    /* 試作だった beta.html はトップへ（電波がなくても。# の共有リンクはブラウザが引き継ぐ） */
    else if(url.pathname === TOP + "beta.html") e.respondWith(Response.redirect(TOP, 302));
    return;
  }
  /* 写しが読めない（CacheStorage の不具合など）ときもネットで開けるように */
  e.respondWith(caches.match(req, {ignoreSearch:true}).catch(() => null).then(hit => hit || fetch(req)));
});
