"""TFFA Seal (Arctic, Cannon Tame) - hero build: a harbour seal with a fresh catch.

Reference analysis (a seal hauled out on an ice floe, fish in its mouth, most important first):
1. Silhouette: a plump torpedo lying belly-down, the chest + head raised high (a proud "up" pose), the rear tapering to
   a pair of hind flippers spread in a V on the ice, short front flippers planted forward.
2. Head: round head with a short dog-like muzzle, big round eyes (the seal's charm), whisker pads with long whiskers,
   small nostrils; a silver fish clamped crosswise in its mouth, tail flopping.
3. Signature: the fish, the dappled spot pattern, the whiskers, the V of hind flippers.
4. Colours: blue-grey back with darker spots, pale silver-grey belly, dark flippers, white eyes with big black pupils,
   fish in silver-blue with a darker back.
Bones: Body, Neck, Head, Fin_L/R, Tail1..2 (flop/crawl clip). Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

GREY, GREY_D, BELLY, SPOT = rgb(136, 150, 168), rgb(98, 110, 130), rgb(214, 222, 230), rgb(76, 86, 104)
FLIP, FISH, FISH_D, BLK = rgb(80, 88, 104), rgb(136, 176, 214), rgb(48, 86, 150), rgb(26, 26, 32)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Seal", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.42, chamfer=0.17, jitter=0.04)

body = m.bone("Body", (0.3, 0, 1.3)); body.__enter__()
m.seg("Chest", V(-0.8, 0, 1.15), V(1.3, 0, 1.75), 2.3, 1.95, GREY, d0=2.0, d1=1.85)
m.box("Belly", (0.3, 0, 0.4), (2.6, 1.8, 0.5), BELLY, top=(0.95, 0.95), bot=(0.85, 0.85))
m.box("ChestFront", (1.55, 0, 1.4), (0.6, 1.6, 1.4), BELLY, rot=Ry(-0.4), top=(0.85, 0.85))
for k, (x, y, w) in enumerate(((0.8, 0.5, 0.36), (0.1, -0.3, 0.42), (-0.5, 0.45, 0.32), (0.5, -0.65, 0.3), (-0.2, 0.05, 0.28))):
    m.box(f"Spot{k}", (x, y, 2.18 + x * 0.25), (w, w * 0.8, 0.1), SPOT, rot=Ry(-0.28) @ Rz(0.7 * k), **NS)
rear = [V(-0.75, 0, 1.15), V(-2.0, 0, 0.8), V(-3.0, 0, 0.5)]
m.chain("Rear", rear, [2.2, 1.6, 1.0], GREY, depths=[1.9, 1.35, 0.8], bones="Tail")
with m.bone("Tail1"):
    m.box("RearBelly", (-1.4, 0, 0.32), (1.6, 1.4, 0.3), BELLY, **NS)
    m.box("RearSpot", (-1.5, 0.3, 1.5), (0.4, 0.32, 0.1), SPOT, rot=Ry(0.25), **NS)
with m.bone("Tail2"):
    for s in (1, -1):                                         # hind flippers in a V
        o = rear[-1] + V(-0.2, s * 0.15, 0.0)
        m.slab(f"HindFlip{s}", [(-0.25, 0), (0.25, 0), (0.55, 1.15), (0.1, 0.95), (-0.1, 1.2), (-0.4, 0.95), (-0.6, 1.15)], 0.16, FLIP,
               origin=o, xaxis=(0, 0, 1), yaxis=(-0.85, s * 0.53, 0.1))

with m.bone("Neck", (1.2, 0, 1.9)):
    m.seg("Neck", V(1.1, 0, 1.8), V(1.75, 0, 2.6), 1.7, 1.45, GREY, d0=1.7, d1=1.4)
with m.bone("Head", (1.7, 0, 2.6), "Neck"), m.frame(pivot=(1.7, 0, 2.6), scale=1.12):
    hc = V(1.95, 0, 2.95)
    m.box("Head", hc, (1.4, 1.5, 1.3), GREY, top=(0.82, 0.86), bot=(0.9, 0.9))
    m.box("Muzzle", hc + V(0.85, 0, -0.3), (0.65, 1.0, 0.62), BELLY, top=(0.85, 0.85), bot=(0.9, 0.9))
    for s in (1, -1):
        m.box(f"WhiskerPad{s}", hc + V(0.95, s * 0.28, -0.32), (0.5, 0.42, 0.42), BELLY, top=(0.85, 0.85))
        for k in range(3):
            b = hc + V(1.0, s * 0.42, -0.25 - k * 0.1)
            m.seg(f"Whisker{s}{k}", b, b + V(0.15, s * 0.65, 0.1 - k * 0.12), 0.05, 0.03, rgb(250, 250, 250), **NS)
        m.box(f"Nostril{s}", hc + V(1.17, s * 0.13, -0.08), (0.06, 0.12, 0.08), BLK, **NS)
    for k, (x, y) in enumerate(((-0.2, 0.4), (0.1, -0.35))):
        m.box(f"HeadSpot{k}", hc + V(x, y, 0.66), (0.28, 0.22, 0.06), SPOT, **NS)
    m.eyes(tuple(hc + V(0.66, 0.4, 0.08)), facing=(0.85, 0.5, 0), size=(0.44, 0.42), pupil=0.82, look=(0.3, 0.1), angry=0.12,
           brow_col=GREY_D, brow_h=0.35, brow_up=0.78, depth=0.12)
    # the catch: a silver fish clamped crosswise in the mouth
    f0 = hc + V(1.1, 0, -0.62)
    m.seg("Fish", f0 + V(0, -0.95, 0.05), f0 + V(0, 0.75, -0.05), 0.42, 0.24, FISH, d0=0.5, d1=0.28, **NS)
    m.box("FishBack", f0 + V(0, -0.1, 0.22), (0.12, 1.5, 0.08), FISH_D, **NS)
    m.slab("FishTail", [(0, 0), (0.35, 0.5), (0, 0.32), (-0.35, 0.5)], 0.08, FISH_D, origin=f0 + V(0, 0.72, -0.08),
           xaxis=(0, 0, 1), yaxis=(0, 1, -0.4))
    m.box("FishEye", f0 + V(0.2, -0.75, 0.1), (0.06, 0.12, 0.12), BLK, **NS)

for s in (1, -1):
    with m.bone(f"Fin_{LR(s)}", (1.0, s * 1.0, 1.0)):
        m.seg(f"FrontFlip{s}", V(1.0, s * 1.0, 1.05), V(1.6, s * 1.45, 0.15), 0.28, 0.24, FLIP, d0=0.85, d1=0.7)
        for k in (-1, 0, 1):
            m.spike(f"Claw{s}{k}", V(1.85, s * 1.45 + k * 0.08, 0.15 + k * 0.12), V(2.05, s * 1.5 + k * 0.08, 0.08 + k * 0.12), 0.05, BLK, flat=0.5)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
