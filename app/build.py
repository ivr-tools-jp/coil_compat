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
# 画面上部の「添付文書と照合」の日付：照合した日のうち、いちばん古いもの（どの製品もこの日以降に確かめてある）
data["checked"] = min((r["checked_date"] for r in data["coils"] + data["catheters"] if r.get("checked_date")), default="")
html = (ROOT / "app" / "template.html").read_text(encoding="utf-8")
html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))


def build_site(out):
    """GitHub Pages などに置く一式。sw.js のキャッシュ名は中身のハッシュで、データや画面を直すと自動で切り替わる。"""
    pwa, static = ROOT / "app" / "pwa", ROOT / "app" / "static"
    out.mkdir(parents=True, exist_ok=True)
    page = (pwa / "head.html").read_text(encoding="utf-8") + html + (pwa / "tail.html").read_text(encoding="utf-8")
    (out / "index.html").write_text(page, encoding="utf-8")
    # 試作の beta.html は公開版に入れ替えたので、来た人をトップへ送る（共有リンクの # も引き継ぐ）
    (out / "beta.html").write_text((pwa / "beta_redirect.html").read_text(encoding="utf-8"), encoding="utf-8")
    shutil.copy(pwa / "manifest.webmanifest", out)
    icons = sorted(static.glob("*.png"))
    for f in icons:
        shutil.copy(f, out)
    fonts = sorted((static / "fonts").glob("*.woff2"))
    (out / "fonts").mkdir(exist_ok=True)
    for f in fonts + sorted((static / "fonts").glob("OFL*.txt")):
        shutil.copy(f, out / "fonts")
    check_font(page)
    h = hashlib.sha256(page.encode("utf-8"))
    for f in [pwa / "manifest.webmanifest", *icons, *fonts]:
        h.update(f.read_bytes())
    assets = ["./", "manifest.webmanifest"] + [f.name for f in icons] + [f"fonts/{f.name}" for f in fonts]
    sw = (pwa / "sw.js").read_text(encoding="utf-8")
    sw = sw.replace("__VERSION__", h.hexdigest()[:12]).replace("__ASSETS__", json.dumps(assets))
    (out / "sw.js").write_text(sw, encoding="utf-8")
    return out / "index.html"


def check_font(page):
    """同梱フォント（使う文字だけに絞ってある）にない文字が画面・データにあれば知らせる。端末のフォントで出るだけで動作は変わらない"""
    f = ROOT / "app" / "static" / "fonts" / "bizudpgothic-chars.txt"
    if not f.exists():
        print("注意：フォントがありません。python tools/make_fonts.py を実行してください")
        return
    have = set(f.read_text(encoding="utf-8"))
    miss = sorted({c for c in page if ord(c) > 0x7F and c not in have and not c.isspace()})
    if miss:
        print("注意：同梱フォントにない文字 → python tools/make_fonts.py で作り直す：", "".join(miss))

if sys.argv[1:2] == ["--site"]:
    out = build_site(Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "_site")
else:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "app" / "index.html"
    out.write_text(html, encoding="utf-8")
print(f"{out}  coils={len(data['coils'])} catheters={len(data['catheters'])}")
