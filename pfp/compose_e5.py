"""Compose the realistic hooded-skull PFP: midnight-blue grade of the greyscale base + red optic overlay.

Inputs (800x800 renders of pfp_skull.html at DPR 2, zoom 1.2):
  raw/e5_base.png  (greyscale scene)       -> ?z=1.2
  raw/e5_eye.png   (transparent red optic) -> ?z=1.2&layer=eye with transparent page background
Output: variants/E5_<palette>.png (400x400) + variants/E5_sheet.png
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from blue_variants import tritone, PALETTES, circle  # noqa: E402


def compose(palette="midnight", tag="E5"):
    base = Image.open(f"{D}/raw/e5_base.png").convert("RGB")
    eye = Image.open(f"{D}/raw/e5_eye.png").convert("RGBA")
    graded = tritone(base, *PALETTES[palette], soften=0.5).convert("RGBA")
    # subtle vignette for a haunting falloff
    w, h = graded.size
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2))
    vig = np.clip((r - 0.55) / 0.6, 0, 1) ** 1.5 * 0.55
    g = np.asarray(graded, float)
    g[..., :3] *= (1 - vig)[..., None]
    graded = Image.fromarray(g.clip(0, 255).astype(np.uint8), "RGBA")
    out = Image.alpha_composite(graded, eye).convert("RGB")
    out = out.resize((400, 400), Image.LANCZOS)
    path = f"{D}/variants/{tag}_{palette}.png"
    out.save(path)
    return path, out


if __name__ == "__main__":
    items = [("before (E4)", Image.open(f"{D}/variants/E4_hood_midnight.png"))]
    for pal in ("midnight", "ice"):
        p, img = compose(pal)
        items.append((f"E5 {pal}", img))
        print(p)
    T = 340
    sheet = Image.new("RGB", (len(items) * (T + 24) + 24, T + 110), (245, 247, 250))
    d = ImageDraw.Draw(sheet)
    for i, (lab, img) in enumerate(items):
        x = 24 + i * (T + 24)
        sheet.paste(circle(img, T), (x, 20))
        sheet.paste(circle(img, 48), (x, T + 34))
        sheet.paste(circle(img, 32), (x + 58, T + 42))
        d.text((x + 100, T + 48), lab, fill=(20, 24, 33))
    sheet.save(f"{D}/variants/E5_sheet.png")
    print(f"{D}/variants/E5_sheet.png")
