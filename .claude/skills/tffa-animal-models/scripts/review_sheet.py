import sys, os
from PIL import Image
"""Review sheet: one image with hero / front / side of several builds, so a whole batch is reviewed in one look.
usage: python3 scripts/review_sheet.py out.png <out_dir1> [<out_dir2> ...]
       each out_dir is a build folder (<Name>/ with previews/<Name>_{hero,front,side}.png); rows = animals."""
out, dirs = sys.argv[1], sys.argv[2:]
views = ["hero", "front", "side"]; T = 450
im = Image.new("RGB", (T * 3, T * len(dirs)), "white")
for r, d in enumerate(dirs):
    n = os.path.basename(d.rstrip("/"))
    for c, v in enumerate(views):
        p = os.path.join(d, "previews", f"{n}_{v}.png")
        if os.path.exists(p):
            a = Image.open(p).convert("RGB"); w, h = a.size; k = 0.12
            a = a.crop((int(w * k), int(h * k), int(w * (1 - k)), int(h * (1 - k)))).resize((T, T))
            im.paste(a, (c * T, r * T))
im.save(out); print(out)
