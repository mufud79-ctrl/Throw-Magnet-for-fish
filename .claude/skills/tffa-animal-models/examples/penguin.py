"""TFFA Penguin (Arctic, Cannon Tame) - hero build: an emperor penguin.

Reference analysis (an emperor penguin standing tall on the ice, most important first):
1. Silhouette: tall upright bowling pin - wide at the belly, narrowing to the shoulders, a smallish head on top,
   flippers held slightly out from the body, short legs and big flat feet, a short stiff tail touching the ice.
2. Head: glossy black head, long slim slightly down-curved beak with an orange stripe on the lower half, stern eyes
   (the emperor is proud and grumpy, not cute) under narrow brows.
3. Signature: the bright yellow-orange ear patches fading into a pale-yellow upper chest, the crisp white belly bordered
   by the black back, flippers with white undersides.
4. Colours: blue-black back, white belly, yellow-orange neck patches, black + orange beak, dark grey feet.
Bones: Body, Head, Wing_L/R (flippers), Leg_L/R, Tail1 (walk, no fly). Studded."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

BLK, BLK_L, WH, YEL, ORG = rgb(34, 38, 56), rgb(58, 64, 88), rgb(248, 248, 250), rgb(255, 236, 160), rgb(255, 166, 40)
FEET, BROW = rgb(52, 54, 64), rgb(90, 98, 124)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Penguin", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.42, chamfer=0.16, jitter=0.04)
m.gait = {"fly": False}

body = m.bone("Body", (0, 0, 2.0)); body.__enter__()
m.seg("Body", V(-0.15, 0, 0.55), V(0.0, 0, 3.75), 2.3, 1.55, BLK, d0=2.1, d1=1.45)
m.box("Belly", (0.62, 0, 1.95), (0.7, 1.9, 2.7), WH, top=(0.78, 0.82), bot=(0.85, 0.85))
m.box("UpperChest", (0.55, 0, 3.3), (0.6, 1.4, 0.75), YEL, top=(0.8, 0.85))
m.box("BellyLow", (0.5, 0, 0.75), (0.6, 1.6, 0.6), WH, **NS)
with m.bone("Tail1", (-0.9, 0, 0.7)):
    m.box("Tail", (-1.25, 0, 0.35), (0.8, 0.8, 0.22), BLK, rot=Ry(-0.4), top=(0.6, 0.8))

with m.bone("Head", (0.0, 0, 3.7)), m.frame(pivot=(0.0, 0, 3.7), scale=1.4):
    hc = V(0.12, 0, 4.3)
    m.box("Head", hc, (1.35, 1.32, 1.15), BLK, top=(0.82, 0.85), bot=(0.95, 0.95))
    for s in (1, -1):                                        # yellow-orange ear patches
        m.box(f"EarPatch{s}", hc + V(-0.12, s * 0.63, -0.3), (0.55, 0.08, 0.5), ORG, rot=Ry(-0.45), **NS)
        m.box(f"NeckPatch{s}", hc + V(0.1, s * 0.6, -0.68), (0.5, 0.08, 0.4), YEL, rot=Ry(-0.45), **NS)
    m.seg("BeakUpper", hc + V(0.6, 0, 0.0), hc + V(1.75, 0, -0.32), 0.36, 0.12, BLK, d0=0.36, d1=0.12)
    m.seg("BeakLower", hc + V(0.6, 0, -0.22), hc + V(1.55, 0, -0.42), 0.32, 0.12, ORG, d0=0.18, d1=0.08, **NS)
    m.eyes(tuple(hc + V(0.44, 0.48, 0.12)), facing=(0.6, 0.8, 0), size=(0.44, 0.36), pupil=0.62, look=(0.5, 0), angry=0.45,
           brow_col=BROW, brow_h=0.5, brow_up=0.75, depth=0.1)

for s in (1, -1):
    with m.bone(f"Wing_{LR(s)}", (0.0, s * 0.9, 3.25)):
        m.seg(f"Flipper{s}", V(0.0, s * 0.92, 3.3), V(-0.1, s * 1.45, 1.35), 0.24, 0.18, BLK, d0=0.85, d1=0.4)
        m.seg(f"FlipperIn{s}", V(0.05, s * 0.8, 3.15), V(-0.05, s * 1.3, 1.45), 0.2, 0.14, WH, d0=0.6, d1=0.3, **NS)
    with m.bone(f"Leg_{LR(s)}", (0.05, s * 0.55, 0.7)):
        m.box(f"Leg{s}", (0.1, s * 0.55, 0.42), (0.5, 0.45, 0.55), BLK)
        m.box(f"Foot{s}", (0.42, s * 0.6, 0.12), (0.95, 0.72, 0.24), FEET, top=(0.9, 0.9))
        for k in (-1, 0, 1):
            m.spike(f"Toe{s}{k}", V(0.85, s * 0.6 + k * 0.22, 0.1), V(1.12, s * 0.6 + k * 0.26, 0.03), 0.07, FEET, flat=0.5)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
