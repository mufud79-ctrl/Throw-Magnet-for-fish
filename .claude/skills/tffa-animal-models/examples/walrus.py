"""TFFA Walrus (Arctic, Cannon Tame) - hero build: an old bull walrus, king of the ice floe.

Reference analysis (a bull walrus rearing up on its front flippers, most important first):
1. Silhouette: a MASSIVE blubbery mound, chest raised high on splayed front flippers, the bulk pouring back into a thick
   tapering rear with hind flippers; the head is small relative to the body but the TUSKS are huge - long, white,
   reaching down past the chin almost to the ice, spreading slightly apart.
2. Head: a broad bristly moustache pad (two big lobes covered in bristles), small angry eyes set high under heavy brows,
   a wrinkled forehead.
3. Signature: the tusks, the moustache, blubber folds ringing the neck and chest, battle scars on the hide.
4. Colours: rosy cinnamon-brown hide + darker folds, pale moustache, white tusks, dark flippers, pink scars.
Bones: Body, Neck, Head, Fin_L/R, Tail1..2 (flop/crawl clip). Studded, fierce."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

HIDE, HIDE_D, MUST, BRIST = rgb(184, 116, 88), rgb(140, 84, 64), rgb(226, 182, 146), rgb(120, 82, 60)
FLIP, SCAR, BLK = rgb(108, 66, 52), rgb(236, 150, 150), rgb(28, 24, 26)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Walrus", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.55, chamfer=0.18, jitter=0.06)
m.gait = {"amp": 0.7}

body = m.bone("Body", (0.5, 0, 2.2)); body.__enter__()
m.seg("Chest", V(-1.0, 0, 2.0), V(1.6, 0, 2.8), 3.6, 3.0, HIDE, d0=3.2, d1=2.9)
m.box("Belly", (0.2, 0, 0.6), (3.6, 2.8, 0.8), HIDE_D, top=(0.95, 0.95), bot=(0.85, 0.85))
for k, (x, w, h) in enumerate(((1.9, 2.9, 2.6), (1.15, 3.4, 3.0))):          # blubber folds ringing neck + chest
    m.box(f"Fold{k}", (x, 0, 2.8 - k * 0.2), (0.32, w, h), HIDE_D, rot=Ry(-0.35), top=(0.8, 0.85), bot=(0.85, 0.9))
for j, (x, z, w, a) in enumerate(((0.6, 3.1, 1.2, 0.4), (-0.2, 2.6, 0.9, -0.3), (0.9, 2.3, 0.7, 0.8))):   # battle scars
    m.box(f"Scar{j}", (x, 1.62, z), (w, 0.08, 0.13), SCAR, rot=Ry(a), **NS)
    m.box(f"ScarR{j}", (x - 0.5, -1.62, z + 0.2), (w * 0.8, 0.08, 0.13), SCAR, rot=Ry(-a), **NS)
rear = [V(-1.0, 0, 2.0), V(-2.8, 0, 1.3), V(-4.2, 0, 0.65)]
m.chain("Rear", rear, [3.4, 2.4, 1.4], HIDE, depths=[3.0, 2.0, 1.1], bones="Tail")
with m.bone("Tail1"):
    m.box("RearFold", (-2.2, 0, 1.5), (0.3, 2.9, 2.3), HIDE_D, rot=Ry(0.45), top=(0.85, 0.85))
with m.bone("Tail2"):
    for s in (1, -1):
        o = rear[-1] + V(-0.3, s * 0.2, -0.1)
        m.slab(f"HindFlip{s}", [(-0.35, 0), (0.35, 0), (0.75, 1.5), (0.15, 1.25), (-0.15, 1.55), (-0.55, 1.25), (-0.85, 1.5)], 0.22, FLIP,
               origin=o, xaxis=(0, 0, 1), yaxis=(-0.85, s * 0.53, 0.1))

with m.bone("Neck", (1.9, 0, 3.3)):
    m.seg("Neck", V(1.6, 0, 3.0), V(2.6, 0, 3.7), 2.7, 2.2, HIDE, d0=2.6, d1=2.1)
with m.bone("Head", (2.6, 0, 3.7), "Neck"):
    hc = V(3.0, 0, 4.0)
    m.box("Head", hc, (1.7, 2.05, 1.6), HIDE, top=(0.8, 0.85), bot=(0.92, 0.92))
    for k in range(3): m.box(f"Wrinkle{k}", hc + V(0.55 - k * 0.3, 0, 0.82), (0.12, 1.3 - k * 0.2, 0.1), HIDE_D, **NS)
    for s in (1, -1):                                          # bristly moustache lobes
        m.box(f"Moustache{s}", hc + V(1.0, s * 0.52, -0.5), (1.0, 1.05, 1.05), MUST, top=(0.8, 0.85), bot=(0.85, 0.85))
        for k in range(6):
            r, c = divmod(k, 3)
            m.box(f"Bristle{s}{k}", hc + V(1.52, s * (0.25 + c * 0.28), -0.25 - r * 0.38), (0.06, 0.1, 0.1), BRIST, **NS)
        # the tusks: long white blades reaching down past the chin, spreading apart
        a, b = hc + V(1.25, s * 0.45, -0.9), hc + V(1.55, s * 0.68, -3.2)
        m.seg(f"Tusk{s}", a, b, 0.36, 0.2, TOOTH, d0=0.42, d1=0.24, **NS)
        m.spike(f"TuskTip{s}", b - (b - a).normalized() * 0.05, b + (b - a).normalized() * 0.5, 0.11, TOOTH, flat=0.8)
        m.box(f"Nostril{s}", hc + V(0.95, s * 0.3, 0.12), (0.2, 0.16, 0.08), BLK, **NS)
    m.box("Chin", hc + V(0.65, 0, -0.95), (0.8, 1.0, 0.45), HIDE_D)
    m.eyes(tuple(hc + V(0.6, 0.62, 0.42)), facing=(0.8, 0.6, 0), size=(0.42, 0.3), pupil=0.75, look=(0.4, 0), angry=0.55,
           brow_col=HIDE_D, brow_h=0.7, brow_up=0.72, depth=0.14)

for s in (1, -1):
    with m.bone(f"Fin_{LR(s)}", (1.3, s * 1.5, 2.2)):
        m.seg(f"FrontArm{s}", V(1.3, s * 1.45, 2.3), V(2.1, s * 2.15, 0.45), 0.6, 0.5, HIDE, d0=1.4, d1=1.2)
        o = V(2.1, s * 2.15, 0.15)
        m.slab(f"FrontFlip{s}", [(-0.6, 0), (0.6, 0), (0.7, 1.1), (0.25, 1.3), (-0.25, 1.3), (-0.7, 1.1)], 0.22, FLIP,
               origin=o, xaxis=(0, 1, 0), yaxis=(1, s * 0.35, 0))
        for k in (-1, 0, 1):
            m.spike(f"Claw{s}{k}", o + V(1.2, s * 0.4 + k * 0.35, 0.05), o + V(1.5, s * 0.5 + k * 0.4, 0.0), 0.08, BLK, flat=0.5)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
