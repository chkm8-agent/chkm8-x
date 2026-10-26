"""Reaper PFP (from the user's reference): midnight grade + iced-out pave diamond teeth + red laser eye.

Usage: .venv/bin/python x/pfp/ref/make_reaper.py
Writes x/pfp/ref/reaper_diamond.png (400x400) and reaper_sheet.png
"""
import os, sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(D))
from blue_variants import tritone, PALETTES, circle  # noqa: E402

N = 800
src = Image.open(f"{D}/reaper_ref.png").convert("RGB")
BOX = (58, 30, 374, 346)
s = N / (BOX[2] - BOX[0])


def P(x, y):  # original-image coords -> 800px square coords
    return ((x - BOX[0]) * s, (y - BOX[1]) * s)


def Pc(cx, cy):  # teeth-crop coords (crop (160,215) scaled 4x) -> 800px coords
    return P(160 + cx / 4, 215 + cy / 4)


sq = src.crop(BOX).resize((N, N), Image.LANCZOS)
base = tritone(sq, *PALETTES["midnight"], grain=False, soften=0)

# ---------------- tooth mask ----------------
poly = [Pc(x, y) for x, y in [(95, 98), (130, 82), (260, 92), (380, 100), (450, 115), (492, 150), (497, 205),
                              (472, 242), (420, 252), (330, 248), (250, 238), (150, 210), (98, 182)]]
region = Image.new("L", (N, N), 0)
ImageDraw.Draw(region).polygon(poly, fill=255)
L = np.asarray(sq.convert("L"), float)
reg = np.asarray(region) > 0
# teeth = bright enamel inside the region; local threshold keeps the dark gaps between teeth
Lb = np.asarray(Image.fromarray(L.astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)), float)
tooth = reg & (L > np.maximum(48, Lb * 0.72))
m = Image.fromarray((tooth * 255).astype(np.uint8))
m = m.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.MinFilter(3))  # clean + keep gaps
mask = np.asarray(m.filter(ImageFilter.GaussianBlur(1.2)), float) / 255.0
shade = np.clip(L / 255.0, 0, 1)

# ---------------- pave diamonds ----------------
rng = np.random.default_rng(5)
ice = Image.new("RGB", (N, N), (0, 0, 0))
dr = ImageDraw.Draw(ice)
r = 3.8                       # stone radius in px (800 canvas)
dx, dy = r * 2.05, r * 1.78   # hex grid
ys, xs = np.nonzero(tooth)
x0, x1, y0, y1 = xs.min() - 10, xs.max() + 10, ys.min() - 10, ys.max() + 10
sparkle_pts = []
row = 0
y = y0
while y < y1:
    x = x0 + (dx / 2 if row % 2 else 0)
    while x < x1:
        xi, yi = int(x), int(y)
        if 0 <= xi < N and 0 <= yi < N and reg[yi, xi]:
            lum = 0.6 + 0.4 * min(1.0, shade[yi, xi] * 1.6)
            # setting (dark prong ring), stone body, table, facet star
            dr.ellipse((x - r - 0.8, y - r - 0.8, x + r + 0.8, y + r + 0.8), fill=(28, 34, 48))
            body = int(150 * lum + rng.integers(-25, 25))
            dr.ellipse((x - r, y - r, x + r, y + r), fill=(body - 10, body + 6, body + 22))
            for k in range(8):  # facets: alternating light/dark wedges
                a0 = k * 45 + rng.integers(-8, 8)
                v = int((235 if k % 2 else 120) * lum)
                dr.pieslice((x - r, y - r, x + r, y + r), a0, a0 + 45, fill=(v - 8, v + 4, min(255, v + 20)))
            t = r * 0.42
            v = int(255 * lum)
            dr.polygon([(x, y - t), (x + t, y), (x, y + t), (x - t, y)], fill=(v, v, 255 if v > 200 else v + 30))
            if L[yi, xi] > 120 and rng.random() < 0.06:
                sparkle_pts.append((x + rng.uniform(-1.5, 1.5), y + rng.uniform(-1.5, 1.5), lum))
        x += dx
    y += dy
    row += 1
ice = ice.filter(ImageFilter.GaussianBlur(0.35))
# soft weight from the ORIGINAL enamel brightness: tooth shapes and dark gaps come straight from the art
w = np.clip((L - 55) / 70, 0, 1) * (np.asarray(region.filter(ImageFilter.GaussianBlur(2)), float) / 255.0)
w = w[..., None]
a = np.asarray(ice, float) * (0.55 + 0.75 * np.clip(shade, 0, 1))[..., None]   # keep the tooth's own shading
b = np.asarray(base, float)
out = b * (1 - w) + a.clip(0, 255) * w
img = Image.fromarray(out.clip(0, 255).astype(np.uint8))

def layer(fn, blur):
    Lr = Image.new("RGB", (N, N), (0, 0, 0))
    fn(ImageDraw.Draw(Lr))
    return Lr.filter(ImageFilter.GaussianBlur(blur)) if blur else Lr


# sparkles: 4-point stars with soft glow (screen blend)
def sparkles(d):
    for x, y, lum in sparkle_pts:
        L1 = 5 + 7 * lum
        d.line((x - L1, y, x + L1, y), fill=(230, 240, 255), width=1)
        d.line((x, y - L1, x, y + L1), fill=(230, 240, 255), width=1)
        d.ellipse((x - 1.6, y - 1.6, x + 1.6, y + 1.6), fill=(255, 255, 255))


img = ImageChops.screen(img, layer(lambda d: [d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(110, 150, 230)) for x, y, _ in sparkle_pts], 5))
img = ImageChops.screen(img, layer(sparkles, 0.4))

# ---------------- red laser eye ----------------
ex, ey = P(305, 176)
ang = np.deg2rad(8)
end = (ex + 900 * np.cos(ang), ey + 900 * np.sin(ang))
for fn, bl in [
    (lambda d: d.ellipse((ex - 90, ey - 90, ex + 90, ey + 90), fill=(150, 0, 0)), 45),
    (lambda d: d.line((ex, ey, *end), fill=(170, 0, 0), width=34), 20),
    (lambda d: d.line((ex, ey, *end), fill=(255, 30, 20), width=10), 5),
    (lambda d: d.line((ex, ey, *end), fill=(255, 200, 180), width=3), 0.8),
    (lambda d: d.ellipse((ex - 26, ey - 26, ex + 26, ey + 26), fill=(255, 40, 20)), 8),
    (lambda d: d.ellipse((ex - 9, ey - 9, ex + 9, ey + 9), fill=(255, 235, 220)), 1.5),
]:
    img = ImageChops.screen(img, layer(fn, bl))

img.save(f"{D}/reaper_diamond@2x.png")
small = img.resize((400, 400), Image.LANCZOS)
small.save(f"{D}/reaper_diamond.png")

sheet = Image.new("RGB", (24 + 360 + 24 + 520 + 24, 560), (245, 247, 250))
sheet.paste(circle(small, 360), (24, 24))
sheet.paste(circle(small, 48), (24, 400))
sheet.paste(circle(small, 32), (84, 408))
zoom = img.crop((int(Pc(60, 40)[0]), int(Pc(60, 40)[1]), int(Pc(540, 300)[0]), int(Pc(540, 300)[1])))
zoom = zoom.resize((520, int(520 * zoom.height / zoom.width)), Image.LANCZOS)
sheet.paste(zoom, (24 + 360 + 24, 24))
ImageDraw.Draw(sheet).text((24 + 360 + 24, 34 + zoom.height), "close-up: pave diamond grill", fill=(20, 24, 33))
sheet.save(f"{D}/reaper_sheet.png")
print(f"{D}/reaper_diamond.png", f"{D}/reaper_sheet.png", "stones+sparkles:", len(sparkle_pts))
