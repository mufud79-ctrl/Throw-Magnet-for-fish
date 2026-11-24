"""Preview the texture library the way Roblox will show it: layers tinted and stacked over a backdrop.

    /tmp/bpyenv/bin/python texture_preview.py [name ...] [--out DIR]

Writes previews/<name>.png (whole sheet tinted on dark), previews/<name>.gif (flipbook playing over a
sky/sand backdrop, 15 fps) and previews/_board.png (one representative frame of everything).
"""
import os, sys, argparse, math
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import photocraft as pc
from vfx_textures import LIB, PALETTES, OUT

def load(path):
    a = np.asarray(Image.open(path).convert("RGBA"), np.float32) / 255
    return a[..., 3], a[..., 0]

def layers_for(name, tex):
    fn, kind, grid, _, pal = LIB[name]
    if kind == "layered":
        L = {k: load(os.path.join(tex, f"{name}_{k}.png"))[0] for k in ("glow", "rim", "mid", "core")}
        return L, None, grid, pal, kind
    a, v = load(os.path.join(tex, f"{name}.png"))
    return {"single": a}, (v if kind in ("shaded", "strip") else None), grid, pal, kind

def backdrop(w, h):
    """Bright daylight sky over sand, like the RELL showcase arenas."""
    y = np.linspace(0, 1, h)[:, None, None]
    sky = (1 - y) * pc.hexc("#3d7fe0") + y * pc.hexc("#a9cff5")
    sand = pc.hexc("#d9c49a") * (0.92 + 0.08 * (y - 0.62) / 0.38)
    img = np.where(y < 0.62, sky, sand) * np.ones((h, w, 3))
    return img.astype(np.float32)

def cells(arr, grid):
    if grid <= 1:
        return [arr]
    n = arr.shape[0] // grid
    return [arr[r*n:(r+1)*n, c*n:(c+1)*n] for r in range(grid) for c in range(grid)]

def frames_rgb(name, tex, bg_fn, size):
    L, V, grid, pal, kind = layers_for(name, tex)
    P = PALETTES[pal]
    keys = list(L)
    per = {k: cells(L[k], grid) for k in keys}
    vs = cells(V, grid) if V is not None else None
    out = []
    for i in range(len(per[keys[0]])):
        lay = {k: np.asarray(Image.fromarray((per[k][i]*255).astype(np.uint8)).resize(size, Image.LANCZOS), np.float32)/255 for k in keys}
        val = np.asarray(Image.fromarray((vs[i]*255).astype(np.uint8)).resize(size, Image.LANCZOS), np.float32)/255 if vs is not None else None
        out.append(pc.composite(lay, P, bg_fn(*size), val))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("names", nargs="*"); ap.add_argument("--out", default=os.path.join(OUT, "..", "previews"))
    a = ap.parse_args(); pc.ensure(a.out)
    names = a.names or list(LIB)
    dark = lambda w, h: np.ones((h, w, 3), np.float32) * pc.hexc("#14161d")
    board = []
    for nm in names:
        fn, kind, grid, _, _ = LIB[nm]
        if grid == 0:   # strips / full-screen
            L, V, _, pal, _ = layers_for(nm, OUT)
            k0 = next(iter(L)); h, w = L[k0].shape
            img = pc.composite(L, PALETTES[pal], np.ones((h, w, 3), np.float32) * pc.hexc("#14161d"), V)
            pc.to_img(img).save(os.path.join(a.out, nm + ".png"))
            t = pc.to_img(img); t.thumbnail((256, 256)); bt = Image.new("RGB", (256, 256), (20, 22, 29)); bt.paste(t, ((256-t.width)//2, (256-t.height)//2)); board.append((nm, bt))
            continue
        fr_dark = frames_rgb(nm, OUT, dark, (256, 256))
        cols = min(4, len(fr_dark)) if grid > 1 else 1
        rows = math.ceil(len(fr_dark) / cols)
        sheet = Image.new("RGB", (256*cols, 256*rows))
        for i, f in enumerate(fr_dark):
            sheet.paste(pc.to_img(f), ((i % cols)*256, (i//cols)*256))
        sheet.save(os.path.join(a.out, nm + ".png"))
        if grid == 4:
            fr = frames_rgb(nm, OUT, backdrop, (320, 320))
            ims = [pc.to_img(f) for f in fr]
            ims[0].save(os.path.join(a.out, nm + ".gif"), save_all=True, append_images=ims[1:] + [ims[-1]]*4, duration=66, loop=0)
        board.append((nm, pc.to_img(fr_dark[min(4, len(fr_dark)-1)] if grid == 4 else fr_dark[0])))
    cols = 6; rows = math.ceil(len(board)/cols)
    B = Image.new("RGB", (cols*260, rows*280), (12, 13, 18)); d = ImageDraw.Draw(B)
    for i, (nm, im) in enumerate(board):
        x, y = (i % cols)*260 + 2, (i//cols)*280 + 2
        B.paste(im.resize((256, 256)), (x, y)); d.text((x+4, y+260), nm, fill=(230, 230, 240))
    B.save(os.path.join(a.out, "_board.png"))
    print("previews in", os.path.abspath(a.out))

if __name__ == "__main__":
    main()
