"""TFFA SphinxCat (Desert, Cannon Tame) - hero build: a pharaoh's temple cat.

Reference analysis (an Egyptian temple-cat statue come to life, most important first):
1. Silhouette: a lean, long-legged regal cat standing tall with its chest out and head high, a striped royal headdress
   (nemes) framing the head and falling in two lappets onto the chest, big pointed ears rising through it, a long tail
   curling up at the tip.
2. Head: wedge cat face, glowing emerald eyes with slit pupils and black kohl eyeliner flicking back (Eye of Horus),
   a cool, slightly disdainful stare; a turquoise scarab gem on the forehead.
3. Signature: the nemes headdress (gold + lapis-blue stripes), a wide gold usekh collar with lapis/turquoise bands, gold
   hoop earrings, gold bands on the forelegs and on the tail.
4. Colours: sandy gold coat + darker back, gold + lapis blue + turquoise jewellery, emerald glow.
Bones: Body, Neck, Head, Ear_L/R, Leg_FL/FR/BL/BR, Tail1..4. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

COAT, COAT_D, MUZ = rgb(224, 180, 116), rgb(178, 132, 78), rgb(240, 214, 170)
GOLD, LAPIS, TURQ, KOHL, EMER = rgb(255, 198, 44), rgb(36, 72, 180), rgb(40, 196, 190), rgb(24, 22, 30), rgb(90, 255, 120)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("SphinxCat", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.4, chamfer=0.16, jitter=0.05)

body = m.bone("Body", (0, 0, 2.6)); body.__enter__()
m.box("Chest", (1.0, 0, 2.65), (1.9, 1.45, 1.8), COAT, top=(0.82, 0.86), bot=(0.74, 0.84))
m.box("Waist", (-0.35, 0, 2.7), (1.3, 1.15, 1.2), COAT, top=(0.92, 0.92), bot=(0.86, 0.9))
m.box("Hips", (-1.45, 0, 2.65), (1.4, 1.35, 1.5), COAT, top=(0.82, 0.86), bot=(0.86, 0.9))
m.box("Back", (-0.3, 0, 3.4), (2.8, 0.75, 0.25), COAT_D, top=(0.7, 0.8))
# usekh collar: stacked bands of gold / lapis / turquoise round the chest
for k, (col, r) in enumerate(((GOLD, 1.0), (LAPIS, 0.92), (TURQ, 0.84), (GOLD, 0.76))):
    m.box(f"Collar{k}", (1.75 - k * 0.04, 0, 3.0 - k * 0.22), (0.5, 1.6 * r, 0.24), col, rot=Ry(-0.35), **NS)
m.box("CollarGem", (2.02, 0, 2.55), (0.12, 0.3, 0.3), TURQ, rot=Ry(-0.35), **NS)

for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (1.2, s * 0.55, 2.6)):
        m.box(f"Shoulder{s}", (1.2, s * 0.65, 2.55), (1.05, 0.45, 1.2), COAT, top=(0.8, 0.8))
        m.seg(f"Foreleg{s}", V(1.25, s * 0.66, 2.3), V(1.45, s * 0.68, 0.3), 0.6, 0.5, COAT)
        m.box(f"Anklet{s}", (1.42, s * 0.68, 0.75), (0.62, 0.62, 0.22), GOLD, **NS)
        m.box(f"AnkletGem{s}", (1.74, s * 0.68, 0.75), (0.06, 0.18, 0.14), LAPIS, **NS)
        m.box(f"Paw{s}", (1.6, s * 0.68, 0.18), (0.72, 0.56, 0.36), COAT, top=(0.85, 0.9))
    with m.bone(f"Leg_B{LR(s)}", (-1.5, s * 0.55, 2.6)):
        m.box(f"Thigh{s}", (-1.5, s * 0.66, 2.0), (1.25, 0.5, 1.6), COAT, rot=Ry(-0.3), top=(0.85, 0.9), bot=(0.65, 0.75))
        m.seg(f"Hock{s}", V(-1.85, s * 0.68, 1.45), V(-1.55, s * 0.68, 0.3), 0.5, 0.45, COAT)
        m.box(f"HindPaw{s}", (-1.35, s * 0.68, 0.18), (0.7, 0.54, 0.36), COAT, top=(0.85, 0.9))
pts = [V(-2.1, 0, 3.0), V(-2.75, 0, 2.6), V(-3.2, 0, 2.95), V(-3.3, 0, 3.75), V(-2.95, 0, 4.3)]
m.chain("Tail", pts, [0.42, 0.38, 0.35, 0.32, 0.26], COAT, bones="Tail")
for i, t in ((1, 0.5), (3, 0.4)):
    with m.bone(f"Tail{i + 1}"):
        q = pts[i].lerp(pts[i + 1], t); d = (pts[i + 1] - pts[i]).normalized()
        m.seg(f"TailRing{i}", q - d * 0.1, q + d * 0.1, 0.46, 0.46, GOLD, **NS)

with m.bone("Neck", (1.6, 0, 3.0)):
    m.seg("Neck", V(1.4, 0, 3.0), V(2.0, 0, 3.75), 1.0, 0.9, COAT, d0=1.0, d1=0.9)
with m.bone("Head", (2.0, 0, 3.7), "Neck"), m.frame(pivot=(2.0, 0, 3.7), scale=1.18):
    hc = V(2.3, 0, 4.0)
    m.box("Head", hc, (1.15, 1.25, 1.0), COAT, top=(0.8, 0.86), bot=(0.86, 0.88))
    m.box("Snout", hc + V(0.62, 0, -0.25), (0.5, 0.72, 0.45), MUZ, top=(0.8, 0.85))
    m.box("Nose", hc + V(0.88, 0, -0.08), (0.08, 0.26, 0.16), rgb(150, 80, 70), bot=(0.9, 0.5), **NS)
    m.box("Mouth", hc + V(0.87, 0, -0.33), (0.06, 0.32, 0.05), KOHL, **NS)
    # nemes headdress: gold-and-lapis striped cap with lappets falling onto the chest
    m.box("NemesCap", hc + V(-0.12, 0, 0.55), (1.3, 1.45, 0.32), GOLD, top=(0.85, 0.9), **NS)
    m.box("NemesBand", hc + V(0.52, 0, 0.42), (0.12, 1.45, 0.16), LAPIS, **NS)
    m.box("NemesBack", hc + V(-0.6, 0, -0.1), (0.35, 1.5, 1.25), GOLD, top=(0.9, 0.9), **NS)
    for s in (1, -1):
        for k in range(5):
            m.box(f"Lappet{s}{k}", hc + V(-0.05, s * 0.72, 0.25 - k * 0.32), (0.55 - k * 0.03, 0.14, 0.3),
                  GOLD if k % 2 == 0 else LAPIS, **NS)
        with m.bone(f"Ear_{LR(s)}", hc + V(-0.2, s * 0.45, 0.6)):
            m.spike(f"Ear{s}", hc + V(-0.2, s * 0.48, 0.6), hc + V(-0.32, s * 0.68, 1.55), 0.32, COAT, flat=0.6)
            m.spike(f"EarIn{s}", hc + V(-0.1, s * 0.48, 0.68), hc + V(-0.22, s * 0.66, 1.3), 0.17, rgb(240, 170, 150), flat=0.5)
            m.box(f"Earring{s}", hc + V(-0.1, s * 0.62, 0.42), (0.06, 0.2, 0.2), GOLD, **NS)
        m.box(f"Kohl{s}", hc + V(0.42, s * 0.6, 0.1), (0.5, 0.05, 0.07), KOHL, rot=Rz(s * 0.3) @ Ry(0.25), **NS)   # eyeliner flick
    m.box("Scarab", hc + V(0.58, 0, 0.5), (0.12, 0.26, 0.22), TURQ, glow=True, **NS)
    m.eyes(tuple(hc + V(0.58, 0.32, 0.12)), facing=(0.9, 0.35, 0), size=(0.4, 0.26), pupil=0.9, look=(0.2, 0), angry=0.3,
           white=EMER, glow_white=True, brow_col=KOHL, brow_h=0.42, brow_up=0.72, depth=0.1)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)], glow_color=EMER)
