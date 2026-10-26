"""Compose the tarot banner + skull PFP in the exact occult.webp palette.
Inputs: x/banner/occult_banner@2x.png and x/pfp/pfp_skull_raw@2x.png (rendered from the .html files at DPR 2).
Outputs: x/banner/banner_tarot.jpg (1500x500) and x/pfp/pfp_skull.png (400x400)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageFilter
from tarot_grade import grade

X = os.path.dirname(os.path.abspath(__file__))
src = Image.open(f'{X}/banner/occult_src.png').convert('RGB')
a = np.asarray(src).astype(float)
gut = np.concatenate([a[20:340, 209:214].reshape(-1, 3), a[20:340, 418:423].reshape(-1, 3)])
gc = np.median(gut[gut.mean(1) > 200], 0)

S = 2; W, H = 1500 * S, 500 * S
pad, gap, cardH, cardW, mw, x0 = 18 * S, 16 * S, 464 * S, 271 * S, 834 * S, 46 * S
graded = grade(Image.open(f'{X}/banner/occult_banner@2x.png').convert('RGB'), soften=0.8)
rng = np.random.default_rng(3)
out = Image.fromarray((np.ones((H, W, 3)) * gc + rng.normal(0, 3, (H, W, 1))).clip(0, 255).astype(np.uint8))
for cx in (x0, x0 + cardW + gap + mw + gap):
    box = (cx, pad, cx + cardW, pad + cardH)
    out.paste(graded.crop(box), box[:2])
mid = src.crop((1, 5, 630, 355)).resize((mw, cardH), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4, 50, 2))
out.paste(mid, (x0 + cardW + gap, pad))
out.resize((1500, 500), Image.LANCZOS).save(f'{X}/banner/banner_tarot.jpg', quality=93)
grade(Image.open(f'{X}/pfp/pfp_skull_raw@2x.png').convert('RGB'), soften=0.7).resize((400, 400), Image.LANCZOS).save(f'{X}/pfp/pfp_skull.png')
print('built banner_tarot.jpg + pfp_skull.png')
