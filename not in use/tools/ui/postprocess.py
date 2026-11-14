"""Step 2: cartoon outline + soft drop shadow on raw renders (system python3, PIL + numpy).

    python3 tools/ui/postprocess.py thumbs RAW_DIR ui/thumbnails     # 50 fish + <Name>_locked.png
    python3 tools/ui/postprocess.py icons  RAW_DIR ui/icons          # fish/shop/index icons
    python3 tools/ui/postprocess.py sheet  ui/thumbnails OUT.png     # review contact sheet
"""
import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fishdata  # noqa: E402

OUT_RGB = np.array(fishdata.hex2rgb(fishdata.OUTLINE), float) / 255
LOCK_RGB = np.array((40, 44, 62), float) / 255


def load(p):
    return np.asarray(Image.open(p).convert("RGBA"), float) / 255


def save(a, p):
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA").save(p, optimize=True)


def shift(a, dx, dy):
    out = np.zeros_like(a)
    h, w = a.shape
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    out[yd, xd] = a[ys, xs]
    return out


def dilate(a, r):
    """Round, anti-aliased dilation of an alpha mask."""
    d = a.copy()
    R = int(np.ceil(r)) + 1
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            w = np.clip(r + 0.5 - np.hypot(dx, dy), 0, 1)
            if w > 0 and (dx or dy):
                d = np.maximum(d, shift(a, dx, dy) * w)
    return d


def over(top, bot):
    ta, ba = top[..., 3:], bot[..., 3:]
    oa = ta + ba * (1 - ta)
    rgb = (top[..., :3] * ta + bot[..., :3] * ba * (1 - ta)) / np.maximum(oa, 1e-6)
    return np.concatenate([rgb, oa], -1)


def layer(rgb, alpha):
    return np.concatenate([np.broadcast_to(rgb, alpha.shape + (3,)), alpha[..., None]], -1)


def cartoon(img, r, shadow_dy, locked=False):
    a = img[..., 3]
    ring = dilate(a, r)
    sh = shift(ring, 0, shadow_dy) * 0.35
    out = layer(np.zeros(3), sh)
    out = over(layer(OUT_RGB, ring), out)
    if locked:
        # flat silhouette with a slightly lighter top so the shape still reads
        h = img.shape[0]
        grad = np.linspace(1.25, 0.85, h)[:, None, None]
        body = layer(np.clip(LOCK_RGB * grad, 0, 1), a)
    else:
        body = img
    return over(body, out)


def thumbs(raw, dst):
    os.makedirs(dst, exist_ok=True)
    for name, _ in fishdata.all_fish():
        p = os.path.join(raw, f"{name}.png")
        if not os.path.exists(p):
            print("missing", name)
            continue
        img = load(p)
        save(cartoon(img, 5.0, 4), os.path.join(dst, f"{name}.png"))
        save(cartoon(img, 5.0, 4, locked=True), os.path.join(dst, f"{name}_locked.png"))
    print("thumbs ->", dst)


def icons(raw, dst):
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(raw)):
        if f.startswith("icon_") and f.endswith(".png"):
            save(cartoon(load(os.path.join(raw, f)), 12.0, 9), os.path.join(dst, f[5:]))
            print("icon", f[5:])


def sheet(src, out, cols=10, tile=128):
    names = [n for n, _ in fishdata.all_fish()]
    files = [f"{n}.png" for n in names] + [f"{n}_locked.png" for n in names[:10]]
    rows = (len(files) + cols - 1) // cols
    im = Image.new("RGBA", (cols * tile, rows * tile), (70, 150, 220, 255))
    for i, f in enumerate(files):
        t = Image.open(os.path.join(src, f)).convert("RGBA").resize((tile, tile), Image.LANCZOS)
        im.alpha_composite(t, ((i % cols) * tile, (i // cols) * tile))
    im.save(out)
    print("sheet ->", out)


if __name__ == "__main__":
    {"thumbs": thumbs, "icons": icons, "sheet": sheet}[sys.argv[1]](*sys.argv[2:])
