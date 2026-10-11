"""PWA 用のアイコンを app/static/ に作る（Pillow が必要。作り直すときだけ実行）。

使い方: python tools/make_icons.py
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "app" / "static"
BG = (13, 108, 140)      # --accent（ライト）
FG = (255, 255, 255)
S = 1024                 # 描いてから縮小する


def coil(d, cx, cy, w, h, turns, lw):
    """横から見たコイル（らせん）を、小さな円を並べて描く。"""
    n = 4000
    r = lw / 2
    for i in range(n + 1):
        t = i / n
        a = t * turns * 2 * math.pi
        x = cx - w / 2 + w * t + (h * 0.22) * math.sin(a)
        y = cy - (h / 2) * math.cos(a)
        d.ellipse((x - r, y - r, x + r, y + r), fill=FG)


def make(scale, rounded):
    """scale: 図柄の大きさ（maskable は中央 80% に収める）。"""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if rounded:
        d.rounded_rectangle((0, 0, S - 1, S - 1), radius=int(S * 0.22), fill=BG)
    else:
        d.rectangle((0, 0, S, S), fill=BG)
    coil(d, S / 2, S / 2, S * 0.56 * scale, S * 0.46 * scale, 3.5, int(S * 0.06 * scale))
    return im


def save(im, name, px):
    im.resize((px, px), Image.LANCZOS).save(OUT / name)
    print(OUT / name)


OUT.mkdir(parents=True, exist_ok=True)
std = make(1.0, rounded=True)
full = make(1.0, rounded=False)      # iOS は自分で角を丸める
mask = make(0.78, rounded=False)     # Android の maskable（安全域 80%）
save(std, "icon-192.png", 192)
save(std, "icon-512.png", 512)
save(mask, "icon-maskable-512.png", 512)
save(full, "apple-touch-icon.png", 180)
save(std, "favicon-32.png", 32)
