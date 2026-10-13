"""画面で使うフォントを app/static/fonts/ に置く（オフラインでも同じ見た目にするため。Google Fonts には頼らない）。

  python tools/make_fonts.py 元フォントのフォルダ

元フォントのフォルダに置くもの（リポジトリには入れない）：
  BIZUDPGothic-Regular.ttf / BIZUDPGothic-Bold.ttf … https://github.com/google/fonts/tree/main/ofl/bizudpgothic
  IBMPlexMono-Medium.woff2 / IBMPlexMono-SemiBold.woff2 … npm @ibm/plex-mono の fonts/complete/woff2/

BIZ UDPゴシックは画面とデータに出てくる文字＋かな・英数字だけに絞る（4.6MB → 数百KB）。
データに新しい漢字が増えたら、build.py が「フォントにない文字」と知らせるので、このスクリプトを流し直す。
IBM Plex Mono は「Plex」が予約フォント名なので手を加えず（絞らず）そのまま写す。
必要なもの：pip install fonttools brotli
"""
import shutil, sys
from pathlib import Path
from fontTools import subset

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "app" / "static" / "fonts"


def used_chars():
    text = "".join((ROOT / "app" / p).read_text(encoding="utf-8") for p in ["template.html", "pwa/head.html", "pwa/tail.html"])
    for f in sorted((ROOT / "data").glob("*.csv")):
        text += f.read_text(encoding="utf-8-sig")
    chars = {c for c in text if ord(c) >= 0x20}
    chars |= {chr(i) for i in range(0x20, 0x7F)}       # 英数字・記号
    chars |= {chr(i) for i in range(0x3041, 0x3097)}   # ひらがな（検索欄に打つ文字）
    chars |= {chr(i) for i in range(0x30A1, 0x30FB)}   # カタカナ
    chars |= {chr(i) for i in range(0xFF01, 0xFF5F)}   # 全角英数字・記号
    chars |= set("ー・、。「」『』（）〜～※○△×★☆″′℃％　")
    return "".join(sorted(chars))


def main(src):
    OUT.mkdir(parents=True, exist_ok=True)
    chars = used_chars()
    for w, name in [("400", "Regular"), ("700", "Bold")]:
        opt = subset.Options()
        opt.flavor = "woff2"
        opt.layout_features = ["*"]
        opt.name_IDs = ["*"]
        opt.notdef_outline = True
        font = subset.load_font(str(src / f"BIZUDPGothic-{name}.ttf"), opt)
        s = subset.Subsetter(opt)
        s.populate(text=chars)
        s.subset(font)
        out = OUT / f"bizudpgothic-{w}.woff2"
        subset.save_font(font, str(out), opt)
        print(f"{out.name}  {out.stat().st_size // 1024} KB")
    for w in ["Medium", "SemiBold"]:
        shutil.copy(src / f"IBMPlexMono-{w}.woff2", OUT)
    # build.py が「フォントにない文字」を調べるための一覧
    (OUT / "bizudpgothic-chars.txt").write_text(chars, encoding="utf-8")
    print(f"{len(chars)} 文字")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
