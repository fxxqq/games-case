# -*- coding: utf-8 -*-
"""
怀旧游戏收纳盒 · 微信小游戏「通用素材封面」生成脚本
规格：650×250 JPEG，体积 <= 80KB
做法：从 1536×1024 原始插画中裁出 2.6:1 横带 -> 分两步 Lanczos 降采样 -> 二分调 quality 控体积
"""
import io
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/ 的上一级 = wx-material
RAW = os.path.join(ROOT, "raw")
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

TARGET_W, TARGET_H = 650, 250
MAX_BYTES = 80 * 1024


def crop_band(img: Image.Image, center_y_ratio: float = 0.5) -> Image.Image:
    """按 650:250 的比例从原图裁一条横向画带，center_y_ratio 控制取景重心。"""
    w, h = img.size
    band_h = int(round(w * TARGET_H / TARGET_W))
    if band_h > h:
        band_w = int(round(h * TARGET_W / TARGET_H))
        left = (w - band_w) // 2
        return img.crop((left, 0, left + band_w, h))
    top = int(round(h * center_y_ratio - band_h / 2))
    top = max(0, min(h - band_h, top))
    return img.crop((0, top, w, top + band_h))


def encode_jpeg(img: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality, optimize=True,
             progressive=True, subsampling=1)
    return buf.getvalue()


def fit_under(data_limit: int, img: Image.Image) -> bytes:
    """二分 quality，拿到体积最接近上限的编码结果。"""
    lo, hi, best = 30, 95, None
    while lo <= hi:
        mid = (lo + hi) // 2
        data = encode_jpeg(img, mid)
        if len(data) <= data_limit:
            best = data
            lo = mid + 1
        else:
            hi = mid - 1
    if best is None:
        best = encode_jpeg(img, 30)
    return best


def build(src_name: str, out_name: str, center_y: float, pre_sharpen: bool = True):
    src = Image.open(os.path.join(RAW, src_name)).convert("RGB")
    band = crop_band(src, center_y)
    # 两步降采样，避免细线（球杆、球桌边框）一次性缩放后发虚
    mid = band.resize((TARGET_W * 2, TARGET_H * 2), Image.LANCZOS)
    if pre_sharpen:
        from PIL import ImageFilter
        mid = mid.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))
    final = mid.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    data = fit_under(MAX_BYTES, final)
    path = os.path.join(OUT, out_name)
    with open(path, "wb") as f:
        f.write(data)
    print(f"{out_name}: {final.size[0]}x{final.size[1]}, {len(data)/1024:.1f} KB (limit 80 KB)")
    return path


if __name__ == "__main__":
    build("Ultra_wide_banner_illustration_2026-11-07T08-45-59.png",
          "cover_A_realistic.jpg", 0.50)
    build("Ultra_wide_banner_illustration_2026-11-07T08-46-16.png",
          "cover_B_pixel.jpg", 0.50)
