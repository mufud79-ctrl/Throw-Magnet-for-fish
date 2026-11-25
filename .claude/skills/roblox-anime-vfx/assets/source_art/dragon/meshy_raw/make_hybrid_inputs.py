import numpy as np
from PIL import Image
from scipy import ndimage
src = np.array(Image.open('/home/user/Throw-Magnet-for-fish/.claude/skills/roblox-anime-vfx/assets/source_art/dragon/hybrid_r15_v4.png').convert('RGB')).astype(float)
BG = np.array([200., 200., 200.])
mx, mn = src.max(-1), src.min(-1)
sat = (mx - mn) / np.maximum(mx, 1)
notbg = np.abs(src - BG).max(-1) > 18
darkneutral = (sat < 0.16) & (mx < 140)                       # shirt, pants, ink lines on the body
skin = (np.abs(src - [230, 208, 185]).max(-1) < 11)
keep = notbg & ~darkneutral
navy = (src[..., 2] > src[..., 0] + 20) & (mx < 150)
cream_hi = (src.mean(-1) > 212) & (sat > 0.08) & (sat < 0.4)
yellow = ((src[..., 0] - src[..., 2]) > 55) & (src.mean(-1) > 110)
yellow = ndimage.binary_dilation(yellow, iterations=1)
for (x0, y0, x1, y1), rule in [((237, 138, 363, 238), 'none'), ((622, 120, 754, 240), "navyyellow"), ((1162, 134, 1308, 198), 'navyyellow'),
                               ((0, 252, 74, 348), 'cream'), ((526, 252, 600, 348), 'cream'), ((938, 252, 1016, 348), 'cream'),
                               ((1464, 252, 1536, 348), 'cream'), ((764, 458, 790, 565), 'none')]:
    sub = keep[y0:y1, x0:x1]
    if rule == 'none': sub[:] = False
    elif rule == 'navyyellow': sub &= (navy | yellow)[y0:y1, x0:x1]
    else: sub &= yellow[y0:y1, x0:x1]
keep = ndimage.binary_opening(keep, iterations=1)
lab, n = ndimage.label(keep)
sizes = ndimage.sum(keep, lab, range(1, n + 1))
keep = np.isin(lab, 1 + np.where(sizes > 60)[0])
keep = ndimage.binary_closing(keep, iterations=2)
soft = ndimage.gaussian_filter(keep.astype(float), 0.7)[..., None]
out = src * soft + BG * (1 - soft)
Image.fromarray(out.astype(np.uint8)).save('v4_noavatar_full.png')
VIEWS = {'front': (0, 600, []), 'side': (600, 1062, [(900, 0, 1062, 360)]), 'back': (934, 1536, [(934, 360, 1080, 864)])}
for name, (x0, x1, blank) in VIEWS.items():
    o2 = out.copy()
    for bx0, by0, bx1, by1 in blank: o2[by0:by1, bx0:bx1] = BG
    c = o2[:, x0:x1]
    h, w = c.shape[:2]
    S = int(max(h, w) * 1.08)
    canvas = np.ones((S, S, 3)) * BG
    canvas[(S - h) // 2:(S - h) // 2 + h, (S - w) // 2:(S - w) // 2 + w] = c
    Image.fromarray(canvas.astype(np.uint8)).resize((1024, 1024), Image.LANCZOS).save(f'v4na_{name}.png')
