"""data/*.csv を読み、app/template.html に埋め込んで app/index.html を作る。

使い方:
  python app/build.py [出力先パス]   Artifact 用（head の無い断片。1ファイル）
  python app/build.py --site DIR     公開用（PWA）。DIR に index.html・manifest・sw.js・アイコンを出す
"""
import csv, json, sys, datetime, hashlib, re, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows の画面でも知らせの文字で止まらないように
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


def built_date():
    """「データ作成」の日付＝画面かデータを最後に直したコミットの日。ビルドした日にすると、
    README を直しただけの push でも毎日中身が変わり「新しいデータがあります」が出てしまう。
    （Actions では checkout に fetch-depth: 0 が要る）"""
    try:
        d = subprocess.run(["git", "log", "-1", "--format=%cs", "--", "data", "app"], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            return d
    except (OSError, subprocess.CalledProcessError):
        pass
    return datetime.date.today().isoformat()


data = {
    "coils": load("coils.csv"),
    "catheters": load("catheters.csv"),
    "limits": load("platform_limits.csv"),
}
# データの版（共有リンクに入れ、受け取った側のデータと同じかを確かめる）
data["ver"] = hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:8]
data["built"] = built_date()
# 画面上部の「添付文書と照合」の日付：照合した日のうち、いちばん古いもの（どの製品もこの日以降に確かめてある）
rows = data["coils"] + data["catheters"]
bad = [r.get("coil_id") or r.get("cat_id") for r in rows if r.get("checked_date") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["checked_date"])]
if bad:
    sys.exit(f"checked_date の形が YYYY-MM-DD でない行: {', '.join(bad)}")
data["checked"] = min((r["checked_date"] for r in rows if r.get("checked_date")), default="")
data["unchecked"] = sum(1 for r in rows if not r.get("checked_date"))  # 照合日のない行（画面に「未照合あり」と出す）
if data["unchecked"]:
    print(f"注意：照合日（checked_date）のない行が {data['unchecked']} 行あります")
html = (ROOT / "app" / "template.html").read_text(encoding="utf-8")
# データに </script> などが入っても壊れないよう < をエスケープして埋め込む
html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False).replace("<", "\\u003c"))


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
    shown = re.sub(r"/\*.*?\*/|<!--.*?-->", "", page, flags=re.S)  # コメントの文字は画面に出ないので数えない
    miss = sorted({c for c in shown if ord(c) > 0x7F and c not in have and not c.isspace()})
    if miss:
        print("注意：同梱フォントにない文字 → python tools/make_fonts.py で作り直す：", "".join(miss))

if sys.argv[1:2] == ["--site"]:
    out = build_site(Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "_site")
else:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "app" / "index.html"
    out.write_text(html, encoding="utf-8")
print(f"{out}  coils={len(data['coils'])} catheters={len(data['catheters'])}")
