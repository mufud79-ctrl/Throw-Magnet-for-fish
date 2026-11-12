"""2D UI art (system python3, PIL + numpy), drawn 4x supersampled.

    python3 tools/ui/make_frames.py ui

ui/frames/button_{blue,green,orange}.png  128x128, 9-slice SliceCenter Rect(40, 40, 88, 82)
ui/frames/slot_<Rarity>.png, slot_Locked.png  96x96, 9-slice SliceCenter Rect(28, 28, 68, 68)
ui/icons/close.png, ui/icons/lock.png          512x512
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fishdata  # noqa: E402
from postprocess import dilate, layer, over  # noqa: E402

SS = 4
OUT = np.array(fishdata.hex2rgb(fishdata.OUTLINE), float) / 255

BUTTONS = {  # top, bottom, lip
    "blue": ("#6FD3FF", "#2386F0", "#1457B5"),
    "green": ("#8BF06E", "#2DB83A", "#1C7A27"),
    "orange": ("#FFD94D", "#FF8A1A", "#B9520A"),
    "red": ("#FF7A6A", "#E0282E", "#9C111B"),
}


def rgb(h):
    return np.array(fishdata.hex2rgb(h), float) / 255


def canvas(n):
    return np.zeros((n * SS, n * SS, 4))


def mask_rr(n, box, r):
    im = Image.new("L", (n * SS, n * SS), 0)
    ImageDraw.Draw(im).rounded_rectangle([v * SS for v in box], r * SS, fill=255)
    return np.asarray(im, float) / 255


def grad(n, top, bot, y0=0, y1=None, diag=False):
    N = n * SS
    y1 = N if y1 is None else y1 * SS
    yy, xx = np.mgrid[0:N, 0:N].astype(float)
    t = (xx + yy) / (2 * N) if diag else np.clip((yy - y0 * SS) / max(1, y1 - y0 * SS), 0, 1)
    return rgb(top) * (1 - t[..., None]) + rgb(bot) * t[..., None]


def down(a, n):
    im = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA").convert("RGBa")
    return im.resize((n, n), Image.LANCZOS).convert("RGBA")


def button_shape(n, top, bot, lip, o, r, lip_h, gloss=True):
    """Chunky 3D button: dark outline, darker lip at the bottom, gradient face, gloss band."""
    c = canvas(n)
    c = over(layer(OUT, mask_rr(n, (0, 0, n, n), r)), c)
    c = over(layer(rgb(lip), mask_rr(n, (o, o, n - o, n - o), r - o)), c)
    c = over(layer(grad(n, top, bot, o, n - o - lip_h), mask_rr(n, (o, o, n - o, n - o - lip_h), r - o)), c)
    if gloss:
        g = mask_rr(n, (o + n * 0.07, o + n * 0.05, n - o - n * 0.07, o + n * 0.25), n * 0.1)
        fade = np.linspace(0.5, 0.08, n * SS)[:, None]
        c = over(layer(np.ones(3), g * fade), c)
    return c


def button(name, n=128):
    top, bot, lip = BUTTONS[name]
    return down(button_shape(n, top, bot, lip, o=6, r=30, lip_h=10), n)


def star(c, n, x, y, s, col=(1, 1, 1), a=0.9):
    im = Image.new("L", (n * SS, n * SS), 0)
    d = ImageDraw.Draw(im)
    X, Y, S = x * SS, y * SS, s * SS
    d.polygon([(X, Y - S), (X + S * 0.28, Y - S * 0.28), (X + S, Y), (X + S * 0.28, Y + S * 0.28),
               (X, Y + S), (X - S * 0.28, Y + S * 0.28), (X - S, Y), (X - S * 0.28, Y - S * 0.28)], fill=255)
    return over(layer(np.array(col, float), np.asarray(im, float) / 255 * a), c)


def slot(rarity, n=96, o=6, r=20):
    if rarity == "Locked":
        main, top, bot, acc = "#4A5368", "#5E6880", "#30374A", "#8C96AE"
    else:
        main, top, bot, acc = fishdata.PALETTE[rarity]
    c = canvas(n)
    c = over(layer(OUT, mask_rr(n, (0, 0, n, n), r)), c)
    inner = mask_rr(n, (o, o, n - o, n - o), r - o)
    c = over(layer(grad(n, top, bot, o, n - o, diag=(rarity == "Celestial")), inner), c)
    # soft light in the middle so thumbnails pop
    yy, xx = np.mgrid[0:n * SS, 0:n * SS] / (n * SS) - 0.5
    glow = np.clip(1 - np.hypot(xx, yy * 1.1) / 0.45, 0, 1) ** 1.5 * 0.22
    c = over(layer(np.ones(3), inner * glow), c)
    # inner accent ring
    bw = 3.5 if rarity in ("Secret", "Divine", "Celestial") else 2.0
    ring = np.clip(mask_rr(n, (o + 2, o + 2, n - o - 2, n - o - 2), r - o - 2)
                   - mask_rr(n, (o + 2 + bw, o + 2 + bw, n - o - 2 - bw, n - o - 2 - bw), r - o - 2 - bw), 0, 1)
    c = over(layer(rgb(acc), ring * (0.95 if bw > 2 else 0.55)), c)
    if rarity == "Celestial":
        for x, y, s in ((17, 17, 5), (79, 78, 4.5), (24, 76, 3), (74, 20, 3)):
            c = star(c, n, x, y, s)
    if rarity == "Secret":
        for x, y in ((16, 16), (80, 16), (16, 80), (80, 80)):
            c = star(c, n, x, y, 3.5, rgb("#FF2A2A"), 1.0)
    if rarity == "Divine":
        for x, y in ((16, 16), (80, 16)):
            c = star(c, n, x, y, 4.5, rgb("#FFC22E"), 1.0)
    return down(c, n)


def thick_line(d, p, q, w, fill):
    d.line([p, q], fill=fill, width=int(w))
    for x, y in (p, q):
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=fill)


def close_icon(n=512):
    c = button_shape(n, *BUTTONS["red"], o=22, r=110, lip_h=34)
    N = n * SS
    im = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(im)
    a, b, cy = 0.31 * N, 0.69 * N, -0.035 * N
    for w, val in ((0.2 * N, 255),):
        thick_line(d, (a, a + cy), (b, b + cy), w, val)
        thick_line(d, (b, a + cy), (a, b + cy), w, val)
    xm = np.asarray(im, float) / 255
    xo = np.asarray(im.resize((n, n), Image.LANCZOS), float) / 255
    ring = np.asarray(Image.fromarray((dilate(xo, 9.0) * 255).astype(np.uint8)).resize((N, N), Image.BILINEAR), float) / 255
    c = over(layer(OUT, ring), c)
    c = over(layer(grad(n, "#FFFFFF", "#FFE3DE"), xm), c)
    return down(c, n)


def lock_icon(n=512):
    N = n * SS
    c = canvas(n)
    # shackle
    sh = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(sh)
    box = [0.27 * N, 0.08 * N, 0.73 * N, 0.62 * N]
    d.arc(box, 180, 360, fill=255, width=int(0.085 * N))
    d.rectangle([0.27 * N, 0.33 * N, 0.27 * N + 0.085 * N, 0.5 * N], fill=255)
    d.rectangle([0.73 * N - 0.085 * N, 0.33 * N, 0.73 * N, 0.5 * N], fill=255)
    shm = np.asarray(sh, float) / 255
    body = mask_rr(n, (0.16 * n, 0.42 * n, 0.84 * n, 0.9 * n), 0.08 * n)
    full = np.maximum(shm, body)
    small = np.asarray(Image.fromarray((full * 255).astype(np.uint8)).resize((n, n), Image.LANCZOS), float) / 255
    ring = np.asarray(Image.fromarray((dilate(small, 14.0) * 255).astype(np.uint8)).resize((N, N), Image.BILINEAR), float) / 255
    c = over(layer(OUT, ring), c)
    c = over(layer(grad(n, "#E9EEF5", "#8D97A8", 0.05 * n, 0.5 * n), shm), c)
    # body: dark rim then gold face
    c = over(layer(OUT, body), c)
    face = mask_rr(n, (0.16 * n + 10, 0.42 * n + 10, 0.84 * n - 10, 0.9 * n - 26), 0.06 * n)
    lip = mask_rr(n, (0.16 * n + 10, 0.42 * n + 10, 0.84 * n - 10, 0.9 * n - 10), 0.06 * n)
    c = over(layer(rgb("#C27A0A"), lip), c)
    c = over(layer(grad(n, "#FFE45A", "#FFA21A", 0.42 * n, 0.88 * n), face), c)
    g = mask_rr(n, (0.16 * n + 30, 0.42 * n + 22, 0.84 * n - 30, 0.42 * n + 70), 24)
    c = over(layer(np.ones(3), g * 0.4), c)
    kh = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(kh)
    cx, cy, r = 0.5 * N, 0.6 * N, 0.065 * N
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    d.polygon([(cx - r * 0.55, cy), (cx + r * 0.55, cy), (cx + r * 0.85, cy + 2.4 * r), (cx - r * 0.85, cy + 2.4 * r)], fill=255)
    c = over(layer(OUT, np.asarray(kh, float) / 255), c)
    return down(c, n)


def main(ui):
    fr, ic = os.path.join(ui, "frames"), os.path.join(ui, "icons")
    os.makedirs(fr, exist_ok=True)
    os.makedirs(ic, exist_ok=True)
    for b in ("blue", "green", "orange"):
        button(b).save(os.path.join(fr, f"button_{b}.png"), optimize=True)
    for r in fishdata.RARITIES:
        slot(r).save(os.path.join(fr, f"slot_{r}.png"), optimize=True)
    close_icon().save(os.path.join(ic, "close.png"), optimize=True)
    lock_icon().save(os.path.join(ic, "lock.png"), optimize=True)
    print("frames + close/lock ->", ui)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ui")
