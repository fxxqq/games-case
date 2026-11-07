# -*- coding: utf-8 -*-
"""封面取景微调：按指定裁剪框重新出图，并做轻度色调/对比优化"""
import io
import os
from PIL import Image, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/ 的上一级 = wx-material
RAW = os.path.join(ROOT, "raw")
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

W, H = 650, 250
LIMIT = 80 * 1024


def encode(img, q):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=q, optimize=True, progressive=True, subsampling=1)
    return buf.getvalue()


def save_under(img, path):
    lo, hi, best = 30, 95, None
    while lo <= hi:
        mid = (lo + hi) // 2
        d = encode(img, mid)
        if len(d) <= LIMIT:
            best, lo = d, mid + 1
        else:
            hi = mid - 1
    best = best or encode(img, 30)
    open(path, "wb").write(best)
    print(f"{os.path.basename(path)}: {len(best)/1024:.1f} KB")


def build(src, rect, out, contrast=1.0, color=1.0, bright=1.0, sharpen=True):
    img = Image.open(os.path.join(RAW, src)).convert("RGB").crop(rect)
    mid = img.resize((W * 2, H * 2), Image.LANCZOS)
    if sharpen:
        mid = mid.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))
    if bright != 1.0:
        mid = ImageEnhance.Brightness(mid).enhance(bright)
    if contrast != 1.0:
        mid = ImageEnhance.Contrast(mid).enhance(contrast)
    if color != 1.0:
        mid = ImageEnhance.Color(mid).enhance(color)
    save_under(mid.resize((W, H), Image.LANCZOS), os.path.join(OUT, out))


if __name__ == "__main__":
    A = "Ultra_wide_banner_illustration_2026-11-07T08-45-59.png"
    B = "Ultra_wide_banner_illustration_2026-11-07T08-46-16.png"
    # A2：向台球桌推近，裁掉多余顶部与底部，提亮 + 提饱和
    build(A, (150, 330, 1450, 830), "cover_A2_realistic_zoom.jpg",
          contrast=1.08, color=1.12, bright=1.10)
    # B2：构图略上移，露出暖色背景光，减少底部空地面
    build(B, (0, 140, 1536, 731), "cover_B2_pixel_shift.jpg",
          contrast=1.06, color=1.10, bright=1.08)
