"""Grade a rendered image into the exact palette of occult.webp.

Builds a luminance -> RGB lookup from the source cards (mean colour of every source
pixel at each brightness), then maps every pixel of the target through it, adds the
source's paper grain and a touch of softness so drawn cards sit next to the
original ones without looking newer.

Usage: .venv/bin/python x/tarot_grade.py in.png out.png [--keep x0,x1]  (keep = untouched column range, px)
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

SRC = "/Users/checkmate_agent/chkm8/x/banner/occult_src.png"


def build_lut():
    s = np.asarray(Image.open(SRC).convert("RGB"), dtype=np.float64)
    L = (0.299 * s[..., 0] + 0.587 * s[..., 1] + 0.114 * s[..., 2]).round().astype(int)
    lut = np.zeros((256, 3))
    have = np.zeros(256, bool)
    for v in range(256):
        m = L == v
        if m.sum() >= 15:
            lut[v] = s[m].mean(0)
            have[v] = True
    idx = np.arange(256)
    for c in range(3):  # fill gaps / ends by interpolation
        lut[:, c] = np.interp(idx, idx[have], lut[have, c])
    # Map target white onto the source's *ink* colour (the tan #dec9a5 line work),
    # not its brightest gutter cream; target black onto the source's darkest field.
    lo = np.percentile(L, 1)
    hi = 0.299 * 0xde + 0.587 * 0xc9 + 0.114 * 0xa5
    return lut, lo, hi


def grade(img, keep=None, grain=True, soften=0.55):
    lut, lo, hi = build_lut()
    a = np.asarray(img.convert("RGB"), dtype=np.float64)
    L = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    L = lo + (L / 255.0) * (hi - lo)
    if grain:
        rng = np.random.default_rng(7)
        h, w = L.shape
        fine = rng.normal(0, 4, (h, w))
        blot = np.asarray(Image.fromarray((rng.random((h // 6 + 1, w // 6 + 1)) * 255).astype(np.uint8))
                          .resize((w, h), Image.BICUBIC), dtype=np.float64)
        L = L + fine + (blot - 128) * 0.05
    L = np.clip(L, 0, 255).round().astype(int)
    out = lut[L]
    o = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    if soften:
        o = o.filter(ImageFilter.GaussianBlur(soften))
    if keep:
        x0, x1 = keep
        o.paste(img.convert("RGB").crop((x0, 0, x1, img.height)), (x0, 0))
    return o


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    keep = None
    if "--keep" in sys.argv:
        keep = tuple(int(v) for v in sys.argv[sys.argv.index("--keep") + 1].split(","))
    grade(Image.open(src), keep).save(dst, quality=93)
    print("wrote", dst)
