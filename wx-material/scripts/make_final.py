# -*- coding: utf-8 -*-
"""定稿：在 A2 取景基础上加暗角，输出微信小游戏通用素材封面（650×250, JPG, <=80KB）"""
import io
import os
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/ 的上一级 = wx-material
RAW = os.path.join(ROOT, "raw")
OUT = os.path.join(ROOT, "out")
W, H = 650, 250
LIMIT = 78500  # 微信后台按 80KB 卡口，留 3KB 余量更稳
SRC = "Ultra_wide_banner_illustration_2026-11-07T08-45-59.png"
RECT = (150, 330, 1450, 830)


def build() -> Image.Image:
    img = Image.open(os.path.join(RAW, SRC)).convert("RGB").crop(RECT)
    mid = img.resize((W * 2, H * 2), Image.LANCZOS)
    mid = mid.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))
    mid = ImageEnhance.Brightness(mid).enhance(1.10)
    mid = ImageEnhance.Contrast(mid).enhance(1.08)
    mid = ImageEnhance.Color(mid).enhance(1.12)
    mid = mid.resize((W, H), Image.LANCZOS)

    # 椭圆暗角：中心透明，四周压暗 -> 视线更集中在球桌
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse((-W * 0.18, -H * 0.35, W * 1.18, H * 1.35), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(60))
    dark = Image.new("RGB", (W, H), (8, 6, 10))
    return Image.composite(mid, Image.blend(mid, dark, 0.45), mask)


def encode(img, q):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=q, optimize=True, progressive=True, subsampling=1)
    return buf.getvalue()


if __name__ == "__main__":
    final = build()
    lo, hi, best = 40, 95, None
    while lo <= hi:
        mid = (lo + hi) // 2
        d = encode(final, mid)
        if len(d) <= LIMIT:
            best, lo = d, mid + 1
        else:
            hi = mid - 1
    path = os.path.join(OUT, "怀旧游戏收纳盒-台球-素材封面-650x250.jpg")
    with open(path, "wb") as f:
        f.write(best)
    print(path)
    print(f"size={final.size}, {len(best)/1024:.1f} KB")
