"""data/*.csv を読み、app/template.html に埋め込んで app/index.html を作る。

使い方:
  python app/build.py [出力先パス]   Artifact 用（head の無い断片。1ファイル）
  python app/build.py --site DIR     公開用（PWA）。DIR に index.html・manifest・sw.js・アイコンを出す
"""
import csv, json, sys, datetime, hashlib, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NUM = {"id_min_in", "id_max_in", "reposition_limit_min", "id_distal_in", "id_proximal_in",
       "od_distal_fr", "od_proximal_fr", "max_gw_in", "min_guide_id_in", "upper_id_in"}


def load(name):
    with open(ROOT / "data" / name, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            if k in NUM:
                r[k] = float(v) if v.strip() else None
            elif k in ("verified", "detachable"):
                r[k] = v.strip() == "1"
    return rows


data = {
    "coils": load("coils.csv"),
    "catheters": load("catheters.csv"),
    "limits": load("platform_limits.csv"),
    "built": datetime.date.today().isoformat(),
}
html = (ROOT / "app" / "template.html").read_text(encoding="utf-8")
html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))


def build_site(out):
    """GitHub Pages などに置く一式。sw.js のキャッシュ名は中身のハッシュで、データを直すと自動で切り替わる。"""
    pwa, static = ROOT / "app" / "pwa", ROOT / "app" / "static"
    out.mkdir(parents=True, exist_ok=True)
    page = (pwa / "head.html").read_text(encoding="utf-8") + html + (pwa / "tail.html").read_text(encoding="utf-8")
    (out / "index.html").write_text(page, encoding="utf-8")
    beta = ROOT / "design" / "v3_proto_template.html"  # 新デザインの試作。公開版とは別ページ（beta.html）で試す
    if beta.exists():
        t = beta.read_text(encoding="utf-8").replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
        (out / "beta.html").write_text((pwa / "beta_head.html").read_text(encoding="utf-8") + t, encoding="utf-8")
    shutil.copy(pwa / "manifest.webmanifest", out)
    icons = sorted(static.glob("*.png"))
    for f in icons:
        shutil.copy(f, out)
    h = hashlib.sha256(page.encode("utf-8"))
    for f in [pwa / "manifest.webmanifest", *icons]:
        h.update(f.read_bytes())
    assets = ["./", "manifest.webmanifest"] + [f.name for f in icons]
    sw = (pwa / "sw.js").read_text(encoding="utf-8")
    sw = sw.replace("__VERSION__", h.hexdigest()[:12]).replace("__ASSETS__", json.dumps(assets))
    (out / "sw.js").write_text(sw, encoding="utf-8")
    return out / "index.html"


if sys.argv[1:2] == ["--site"]:
    out = build_site(Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "_site")
else:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "app" / "index.html"
    out.write_text(html, encoding="utf-8")
print(f"{out}  coils={len(data['coils'])} catheters={len(data['catheters'])}")
