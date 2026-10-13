/* オフライン用の Service Worker。キャッシュ名と ASSETS の中身は build.py が埋める。
   キャッシュ優先：画面・フォント・アイコンは手元の写しをすぐ出す（電波が弱くても待たない）。
   データや画面を直すと sw.js の中身（キャッシュ名）が変わり、ブラウザが新しい版を裏で受け取る。
   受け取ったら画面の下に「新しいデータがあります」を出し、押されたら切り替えて読み直す（tail.html）。 */
const CACHE = "cc-__VERSION__";
const ASSETS = __ASSETS__;
const TOP = new URL("./", self.location).pathname;  /* 公開版のトップ（…/coil_compat/） */

self.addEventListener("install", e => {
  /* HTTP のキャッシュ（GitHub Pages は10分）に古い版が残っていても、必ず新しく取る */
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS.map(u => new Request(u, {cache:"reload"})))));
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
      e.respondWith(caches.match("./").then(hit => hit || fetch(req)));
    return;
  }
  e.respondWith(caches.match(req, {ignoreSearch:true}).then(hit => hit || fetch(req)));
});
