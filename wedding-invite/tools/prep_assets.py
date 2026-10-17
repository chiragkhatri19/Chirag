"""Converts the approved Codex artwork (codex/out) into web-ready assets (assets/v2).

- Street panorama: chroma-green day windows keyed to transparency (with green spill removed).
- Event scenes: JPEG.  Cut-outs: WebP with alpha, trimmed to their content.
"""
import json
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'codex', 'out')
DST = os.path.join(ROOT, 'assets', 'v2')
os.makedirs(DST, exist_ok=True)

# street: key out the green windows
p = np.asarray(Image.open(os.path.join(SRC, 'P_panorama.png')).convert('RGB')).astype(np.float32)
r, g, b = p[..., 0], p[..., 1], p[..., 2]
greenness = g - np.maximum(r, b)
a = 1 - np.clip((greenness - 60) / 80, 0, 1)
spill = (greenness > 0) & (a > 0)
p[..., 1] = np.where(spill, np.minimum(g, np.maximum(r, b) + 4), g)
out = np.dstack([p, a * 255]).clip(0, 255).astype(np.uint8)
Image.fromarray(out, 'RGBA').save(os.path.join(DST, 'street.webp'), quality=90, method=6)

for i, n in enumerate(['E01_ganesh_sthapana', 'E02_mayra_swagat', 'E03_ring_ceremony', 'E04_carnival', 'E05_bandoli',
                       'E06_sangeet', 'E07_ghadi_vinayak', 'E08_haldi_janeu', 'E09_baraat', 'E10_mangal_phera'], 1):
    Image.open(os.path.join(SRC, n + '.png')).convert('RGB').save(os.path.join(DST, 'E%02d.jpg' % i), quality=90)

sizes = {}
for n, name in [('01_anchor_couple', 'couple'), ('02_rickshaw', 'rickshaw'), ('03_puppets', 'puppets'), ('B1_banner', 'banner'),
                ('F1_fg_drape', 'drape'), ('F2_fg_pillar', 'pillar'), ('F3_fg_flowers', 'flowers'), ('F4_fg_petals', 'petals')]:
    im = Image.open(os.path.join(SRC, n + '.png')).convert('RGBA')
    al = np.asarray(im)[..., 3]
    al = np.where(al < 8, 0, al)          # drop near-invisible specks before trimming
    im.putalpha(Image.fromarray(al.astype(np.uint8)))
    if name not in ('petals', 'flowers'):
        im = im.crop(im.getchannel('A').point(lambda v: 255 if v > 20 else 0).getbbox())
    im.save(os.path.join(DST, name + '.webp'), quality=92, method=6)
    sizes[name] = im.size
json.dump(sizes, open(os.path.join(DST, 'sizes.json'), 'w'))
print(sizes)
