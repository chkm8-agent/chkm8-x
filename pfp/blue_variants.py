"""Blue PFP renditions: duotone/tritone grades of the greyscale skull renders + a contact sheet.

Input renders (DPR 2, 800x800) in x/pfp/raw/<layout>.png. Each palette maps luminance through
dark -> mid -> light stops (same engraved look as the tarot grade, different hue), adds grain.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__))

PALETTES = {
    # name: (dark, mid, light)
    "midnight":   ("#08132a", "#2b4a7c", "#dfe6f0"),  # navy field, cool bone ink
    "prussian":   ("#0a2232", "#3b5a63", "#dec9a5"),  # prussian blue + banner's tan ink (ties to banner)
    "cobalt":     ("#0d1f5c", "#3d5fb8", "#f2ead6"),  # saturated cobalt, cream ink
    "ice":        ("#040a17", "#1d4e86", "#9fd4ff"),  # near-black + glowing ice blue
    "delft":      ("#f3ecdc", "#7c93bd", "#16336e"),  # inverted: cream field, delft-blue ink
}


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def tritone(img, dark, mid, light, grain=True, soften=0.7):
    a = np.asarray(img.convert("L"), float) / 255.0
    if grain:
        rng = np.random.default_rng(11)
        h, w = a.shape
        blot = np.asarray(Image.fromarray((rng.random((h // 6 + 1, w // 6 + 1)) * 255).astype(np.uint8))
                          .resize((w, h), Image.BICUBIC), float) / 255.0
        a = np.clip(a + rng.normal(0, 0.016, a.shape) + (blot - 0.5) * 0.035, 0, 1)
    d, m, l = hex2rgb(dark), hex2rgb(mid), hex2rgb(light)
    t = a[..., None]
    lo = d + (m - d) * np.clip(t / 0.5, 0, 1)
    hi = m + (l - m) * np.clip((t - 0.5) / 0.5, 0, 1)
    out = np.where(t < 0.5, lo, hi)
    o = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    return o.filter(ImageFilter.GaussianBlur(soften)) if soften else o


def circle(img, size):
    img = img.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    bg = Image.new("RGB", (size, size), (255, 255, 255))
    bg.paste(img, (0, 0), mask)
    return bg


if __name__ == "__main__":
    combos = [  # (id, layout, palette)
        ("A", "classic", "midnight"),
        ("B", "classic", "prussian"),
        ("C", "close", "cobalt"),
        ("D", "close", "ice"),
        ("E", "seal", "midnight"),
        ("F", "seal", "delft"),
    ]
    os.makedirs(f"{D}/variants", exist_ok=True)
    tiles = []
    for vid, layout, pal in combos:
        raw = Image.open(f"{D}/raw/{layout}.png").convert("RGB")
        out = tritone(raw, *PALETTES[pal]).resize((400, 400), Image.LANCZOS)
        path = f"{D}/variants/{vid}_{layout}_{pal}.png"
        out.save(path)
        tiles.append((vid, layout, pal, out))
        print(path)

    # contact sheet: each option as X shows it (circle, big) + small 48px circle (timeline size)
    T, small, padx, lab = 300, 56, 30, 46
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    W = cols * (T + padx) + padx
    H = rows * (T + small + lab + 40) + padx
    sheet = Image.new("RGB", (W, H), (245, 247, 250))
    dr = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
        fs = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 15)
    except Exception:
        f = fs = ImageFont.load_default()
    for i, (vid, layout, pal, img) in enumerate(tiles):
        c, r = i % cols, i // cols
        x = padx + c * (T + padx)
        y = padx + r * (T + small + lab + 40)
        sheet.paste(circle(img, T), (x, y))
        sheet.paste(circle(img, small), (x, y + T + 14))
        sheet.paste(circle(img, 32), (x + small + 12, y + T + 14 + (small - 32) // 2))
        dr.text((x + small + 56, y + T + 16), f"{vid}", fill=(20, 24, 33), font=f)
        dr.text((x + small + 56, y + T + 44), f"{layout} · {pal}", fill=(90, 98, 112), font=fs)
    sheet.save(f"{D}/variants/contact_sheet.png")
    print(f"{D}/variants/contact_sheet.png")
