"""Grade hooded-skull iterations (raw/H*.png + raw/H*_eye.png) into the live midnight palette + red optic; contact sheet."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from blue_variants import tritone, PALETTES, circle  # noqa: E402

LABELS = {
    "H0": "front · fangs · engraved hatching (= live E4)",
    "H1": "front · worn closed bite · stipple shading",
    "H2": "3/4 turn + tilt · fangs · hatching",
    "H3": "3/4 turn + tilt · worn bite · half in shadow",
    "H4": "3/4 other way · broken teeth · stipple",
    "H5": "3/4 slight · clenched teeth · stipple",
    "H6": "front · clenched teeth · half in shadow",
}


def build(k):
    base = Image.open(f"{D}/raw/{k}.png").convert("RGB")
    eye = Image.open(f"{D}/raw/{k}_eye.png").convert("RGBA")
    out = Image.alpha_composite(tritone(base, *PALETTES["midnight"]).convert("RGBA"), eye).convert("RGB").resize((400, 400), Image.LANCZOS)
    out.save(f"{D}/variants/hood_{k}.png")
    return out


if __name__ == "__main__":
    keys = sys.argv[1:] or list(json.load(open(f"{D}/raw/hood_set_params.json")).keys())
    tiles = [(k, build(k)) for k in keys]
    T, cols, padx = 300, 4 if len(tiles) > 6 else 3, 26
    rows = (len(tiles) + cols - 1) // cols
    Hc = T + 110
    sheet = Image.new("RGB", (cols * (T + padx) + padx, rows * Hc + padx), (245, 247, 250))
    dr = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 20)
        fs = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
    except Exception:
        f = fs = ImageFont.load_default()
    for i, (k, img) in enumerate(tiles):
        c, r = i % cols, i // cols
        x, y = padx + c * (T + padx), padx + r * Hc
        sheet.paste(circle(img, T), (x, y))
        sheet.paste(circle(img, 48), (x, y + T + 12))
        sheet.paste(circle(img, 32), (x + 56, y + T + 20))
        dr.text((x + 100, y + T + 12), k, fill=(20, 24, 33), font=f)
        dr.text((x + 100, y + T + 38), LABELS.get(k, ""), fill=(90, 98, 112), font=fs)
    sheet.save(f"{D}/variants/hood_sheet.png")
    print(f"{D}/variants/hood_sheet.png")
