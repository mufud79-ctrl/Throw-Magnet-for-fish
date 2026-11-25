"""Dragon fire matter review sheets: every frame of each fire flipbook tinted with the kit's layer conventions and
blended the way Roblox blends LightEmission (lerp between alpha-over and additive), over a dark backdrop and over
sand, with the hot colours and the cooled colours (ember red / char) side by side.

    /tmp/bpyenv/bin/python fire_preview.py [name ...] [--out DIR] [--sheet contact.jpg]
"""
import os, sys, argparse
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import photocraft as pc
from vfx_textures import LIB, OUT

# (colour, LightEmission, transparency) per layer: hot and cooled stages of lab/dragon/kit.py
HOT = {"glow": ("#ff7a1a", 0.75, 0.7), "rim": ("#d4202a", 0.2, 0), "mid": ("#ffc23a", 0.4, 0), "core": ("#fff4c8", 1, 0)}
COOL = {"glow": ("#d4202a", 0.75, 0.82), "rim": ("#3a1c1e", 0.0, 0), "mid": ("#d4202a", 0.4, 0.2), "core": ("#ff7a1a", 1, 0.4)}
FIRE = ["flame_billow", "flame_tongue", "claw_rake", "fire_crescent", "fire_ring", "fire_impact", "molten_crack",
        "claw_gouge", "fire_slice", "heat_ring"]
STRIPS = [f"flame_strip_{i}" for i in range(1, 5)]


def load(name, L):
    return np.asarray(Image.open(os.path.join(OUT, f"{name}_{L}.png")).convert("RGBA"), np.float32)[..., 3] / 255


def blend(bg, lay, conv):
    out = bg.copy()
    for L in ("glow", "rim", "mid", "core"):
        col, le, tr = conv[L]
        a = (lay[L] * (1 - tr))[..., None]
        c = pc.hexc(col) * (1.15 if L == "core" else 1.0)
        out = out * (1 - a * (1 - le)) + c * a
    return np.clip(out, 0, 1)


def sand(w, h):
    y = np.linspace(0, 1, h)[:, None, None]
    return (pc.hexc("#d9c49a") * (0.9 + 0.1 * y) * np.ones((h, w, 3))).astype(np.float32)


def dark(w, h):
    return np.ones((h, w, 3), np.float32) * pc.hexc("#14161d")


def cells(a, grid=4):
    n = a.shape[0] // grid
    return [a[r * n:(r + 1) * n, c * n:(c + 1) * n] for r in range(grid) for c in range(grid)]


def row(name, size=160):
    per = {L: cells(load(name, L)) for L in ("glow", "rim", "mid", "core")}
    strips = []
    for bgf, conv in ((dark, HOT), (sand, HOT)):
        R = Image.new("RGB", (size * 16, size))
        for i in range(16):
            lay = {L: np.asarray(Image.fromarray((per[L][i] * 255).astype(np.uint8)).resize((size, size), Image.LANCZOS), np.float32) / 255 for L in per}
            R.paste(pc.to_img(blend(bgf(size, size), lay, conv)), (i * size, 0))
        strips.append(R)
    return strips


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--out", default=os.path.join(OUT, "..", "previews", "dragon"))
    a = ap.parse_args()
    pc.ensure(a.out)
    names = a.names or FIRE
    size, lab = 150, 22
    blocks = []
    for nm in names:
        if nm.startswith("flame_strip"):
            continue
        d, s = row(nm, size)
        blocks.append((nm, d, s))
        im = Image.new("RGB", (d.width, d.height * 2)); im.paste(d, (0, 0)); im.paste(s, (0, d.height))
        im.save(os.path.join(a.out, f"{nm}.jpg"), quality=90)
    if blocks:
        W = blocks[0][1].width
        C = Image.new("RGB", (W, len(blocks) * (2 * size + lab)), (12, 13, 18))
        dr = ImageDraw.Draw(C)
        for k, (nm, d, s) in enumerate(blocks):
            y = k * (2 * size + lab)
            dr.text((6, y + 5), f"{nm}   (16 frames: top over dark, bottom over sand; hot colours)", fill=(235, 235, 240))
            C.paste(d, (0, y + lab)); C.paste(s, (0, y + lab + size))
        C.save(os.path.join(a.out, "fire_contact.jpg"), quality=88)
    # strips: each tinted hot and cooled, over sand, tiled twice to show the seam
    st = [n for n in (a.names or STRIPS) if n.startswith("flame_strip")]
    if st:
        rows = []
        for nm in st:
            lay = {L: load(nm, L) for L in ("glow", "rim", "mid", "core")}
            h, w = lay["rim"].shape
            lay2 = {L: np.concatenate([v, v], 1) for L, v in lay.items()}
            for conv, bgf in ((HOT, dark), (HOT, sand), (COOL, sand)):
                rows.append(pc.to_img(blend(bgf(2 * w, h), lay2, conv)))
        S2 = Image.new("RGB", (rows[0].width, sum(r.height for r in rows)))
        y = 0
        for r in rows:
            S2.paste(r, (0, y)); y += r.height
        S2.thumbnail((2048, 99999))
        S2.save(os.path.join(a.out, "flame_strips.jpg"), quality=88)
    print("previews in", os.path.abspath(a.out))


if __name__ == "__main__":
    main()
