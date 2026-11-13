"""Side-by-side reference vs render sheet for harsh visual review (system python + Pillow).
usage: python3 compare.py out.png REF[:x0,y0,x1,y1] RENDER [RENDER2 ...]"""
import sys
from PIL import Image, ImageDraw

def load(spec):
    if ":" in spec and spec.rsplit(":", 1)[1].count(",") == 3:
        p, box = spec.rsplit(":", 1); im = Image.open(p).convert("RGB"); return im.crop(tuple(int(v) for v in box.split(",")))
    return Image.open(spec).convert("RGB")

def main():
    out, specs = sys.argv[1], sys.argv[2:]
    ims = [load(s) for s in specs]; H = 640
    ims = [im.resize((int(im.width * H / im.height), H), Image.LANCZOS) for im in ims]
    W = sum(im.width for im in ims) + 10 * (len(ims) - 1)
    sheet = Image.new("RGB", (W, H + 28), (255, 255, 255)); x = 0; d = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        sheet.paste(im, (x, 28)); d.text((x + 6, 6), "REFERENCE" if i == 0 else f"OURS {i}", fill=(0, 0, 0)); x += im.width + 10
    sheet.save(out); print(out)

if __name__ == "__main__":
    main()
