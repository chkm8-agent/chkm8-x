"""Grade the occult skull set into the live PFP palette (midnight tritone + red optic) and build a contact sheet."""
import os, sys
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from blue_variants import tritone, PALETTES, circle  # noqa: E402

SET = [("ouroboros", "Ouroboros: serpent eating its tail, crowned skull"),
       ("moth", "Death's-head moth: skull as the moth's body"),
       ("candle", "Memento mori: candle burning on the skull"),
       ("eye", "All-seeing eye: skull in the triangle, crown"),
       ("hourglass", "Tempus fugit: winged hourglass, crossbones"),
       ("sigil", "Alchemical seal: planetary glyph ring")]


def build(v):
    base = Image.open(f"{D}/raw/set_{v}.png").convert("RGB")
    eye = Image.open(f"{D}/raw/set_{v}_eye.png").convert("RGBA")
    out = Image.alpha_composite(tritone(base, *PALETTES["midnight"]).convert("RGBA"), eye).convert("RGB")
    out = out.resize((400, 400), Image.LANCZOS)
    out.save(f"{D}/variants/set_{v}.png")
    return out


if __name__ == "__main__":
    tiles = [(v, label, build(v)) for v, label in SET]
    T, cols, padx = 300, 3, 30
    rows = (len(tiles) + cols - 1) // cols
    W, Hc = cols * (T + padx) + padx, T + 120
    sheet = Image.new("RGB", (W, rows * Hc + padx), (245, 247, 250))
    dr = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 20)
        fs = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
    except Exception:
        f = fs = ImageFont.load_default()
    for i, (v, label, img) in enumerate(tiles):
        c, r = i % cols, i // cols
        x, y = padx + c * (T + padx), padx + r * Hc
        sheet.paste(circle(img, T), (x, y))
        sheet.paste(circle(img, 48), (x, y + T + 12))
        sheet.paste(circle(img, 32), (x + 56, y + T + 20))
        dr.text((x + 100, y + T + 14), f"{i + 1}. {v}", fill=(20, 24, 33), font=f)
        dr.text((x + 100, y + T + 40), label, fill=(90, 98, 112), font=fs)
        print(f"{D}/variants/set_{v}.png")
    sheet.save(f"{D}/variants/set_sheet.png")
    print(f"{D}/variants/set_sheet.png")
