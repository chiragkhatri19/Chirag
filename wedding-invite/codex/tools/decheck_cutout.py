"""Turn an image whose 'transparent' background is a baked-in grey/white checkerboard into a real RGBA cut-out.

    python3 decheck_cutout.py in.webp out.png

Background = neutral (grey/white) pixels connected to the image border, plus enclosed neutral regions that carry the
checker texture (gaps between arms and body). The edge band is then alpha-matted (pymatting closed-form) and the
foreground colours are decontaminated so no grey fringe is left.
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from pymatting import estimate_alpha_cf, estimate_foreground_ml

src, dst = sys.argv[1], sys.argv[2]
rgb = np.asarray(Image.open(src).convert('RGB')).astype(np.float64)
R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
mx, mn = rgb.max(-1), rgb.min(-1)
lum = rgb.mean(-1)

# the checker is two near-neutral, slightly cool greys (~172 and ~240) with soft transitions between squares
neutral = (mx - mn <= 16) & (B - R >= -5) & (lum >= 150) & (lum <= 252)

lab, n = ndi.label(neutral)
border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
bg = np.isin(lab, border[border > 0])

# enclosed checker gaps: neutral components with strong 8 px checker texture
tex = ndi.uniform_filter(lum, 9)
loc_sd = np.sqrt(np.maximum(ndi.uniform_filter(lum ** 2, 9) - tex ** 2, 0))
for k in range(1, n + 1):
    if k in border:
        continue
    m = lab == k
    if m.sum() > 300 and loc_sd[m].mean() > 18:
        bg |= m

bg = ndi.binary_opening(bg, iterations=1)
fg = ndi.binary_fill_holes(~bg)                       # nothing inside the figure is background unless detected above
fg &= ~bg

# trimap: certain fg / certain bg / a thin unknown band along the silhouette
sure_fg = ndi.binary_erosion(fg, iterations=3)
sure_bg = ndi.binary_erosion(~fg, iterations=3)
trimap = np.full(fg.shape, .5)
trimap[sure_fg] = 1
trimap[sure_bg] = 0

img = rgb / 255.0
alpha = estimate_alpha_cf(img, trimap)
alpha = np.clip(alpha, 0, 1)
alpha[sure_bg] = 0
alpha[sure_fg] = 1
fgc = estimate_foreground_ml(img, alpha)
out = np.dstack([np.clip(fgc, 0, 1) * 255, alpha * 255]).round().astype(np.uint8)
Image.fromarray(out, 'RGBA').save(dst)
print('saved', dst, 'fg px', int(fg.sum()), 'components', n)
