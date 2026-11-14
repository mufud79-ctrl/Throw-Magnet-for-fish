"""TFFA FennecFox (Desert, Cannon Tame) - hero build.

Reference analysis (a fennec fox on a dune at dusk, most important first):
1. Silhouette: a tiny fox whose ENORMOUS ears (taller than the head, wider than the body) dominate everything, held
   up and out in a wide V; a compact body on slim legs, a bushy tail with a black tip held low and out.
2. Head: small rounded head, short pointed snout with a black nose, big dark-amber eyes with dark tear-lines running
   down toward the muzzle, a mischievous half-smile; white cheeks.
3. Signature: the ears - cream outside, pink inside with white fur tufts at the base - and the black tail tip.
4. Colours: warm sand/cream body, white cheeks + belly, pink inner ears, amber eyes, black nose + tail tip.
Bones: Body, Neck, Head, Ear_L/R, Leg_FL/FR/BL/BR, Tail1..3. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

SAND, SAND_D, WH, EARIN = rgb(238, 196, 132), rgb(200, 150, 92), rgb(252, 244, 228), rgb(250, 160, 160)
AMBER, BLK, LINE = rgb(255, 176, 50), rgb(28, 24, 24), rgb(150, 100, 60)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("FennecFox", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.38, chamfer=0.16, jitter=0.05)

body = m.bone("Body", (0, 0, 1.9)); body.__enter__()
m.box("Chest", (0.7, 0, 1.95), (1.5, 1.35, 1.45), SAND, top=(0.82, 0.86), bot=(0.8, 0.86))
m.box("Waist", (-0.35, 0, 2.0), (1.1, 1.15, 1.1), SAND, top=(0.92, 0.92), bot=(0.86, 0.9))
m.box("Hips", (-1.2, 0, 1.95), (1.2, 1.3, 1.3), SAND, top=(0.82, 0.86), bot=(0.86, 0.9))
m.box("Belly", (-0.15, 0, 1.33), (2.0, 0.9, 0.25), WH, **NS)
m.box("Bib", (1.4, 0, 1.85), (0.3, 1.0, 1.1), WH, rot=Ry(-0.25), top=(0.85, 0.9))
for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (0.8, s * 0.5, 1.8)):
        m.seg(f"Foreleg{s}", V(0.85, s * 0.52, 1.75), V(1.05, s * 0.55, 0.25), 0.5, 0.42, SAND)
        m.box(f"Paw{s}", (1.15, s * 0.55, 0.16), (0.6, 0.5, 0.32), SAND_D, top=(0.85, 0.9))
    with m.bone(f"Leg_B{LR(s)}", (-1.25, s * 0.5, 1.9)):
        m.box(f"Thigh{s}", (-1.25, s * 0.58, 1.5), (1.0, 0.45, 1.15), SAND, rot=Ry(-0.3), top=(0.85, 0.9), bot=(0.65, 0.75))
        m.seg(f"Hock{s}", V(-1.5, s * 0.6, 1.1), V(-1.3, s * 0.6, 0.25), 0.42, 0.38, SAND)
        m.box(f"HindPaw{s}", (-1.12, s * 0.6, 0.16), (0.6, 0.48, 0.32), SAND_D, top=(0.85, 0.9))
pts = [V(-1.7, 0, 2.2), V(-2.4, 0, 2.0), V(-2.95, 0, 1.6), V(-3.3, 0, 1.15)]
m.chain("Tail", pts, [0.55, 0.85, 0.8, 0.55], SAND, bones="Tail")
with m.bone("Tail3"):
    m.spike("TailTip", pts[2].lerp(pts[3], 0.4), pts[3] + V(-0.45, 0, -0.3), 0.42, BLK, flat=0.8)

with m.bone("Neck", (1.1, 0, 2.3)):
    m.seg("Neck", V(1.0, 0, 2.3), V(1.6, 0, 2.6), 1.0, 0.9, SAND, d0=1.05, d1=0.9)
with m.bone("Head", (1.6, 0, 2.6), "Neck"), m.frame(pivot=(1.6, 0, 2.6), scale=1.2):
    hc = V(1.95, 0, 2.75)
    m.box("Head", hc, (1.05, 1.2, 0.95), SAND, top=(0.8, 0.85), bot=(0.88, 0.9))
    for s in (1, -1):
        m.box(f"Cheek{s}", hc + V(0.25, s * 0.5, -0.25), (0.6, 0.35, 0.45), WH, top=(0.85, 0.85))
        m.box(f"TearLine{s}", hc + V(0.55, s * 0.36, -0.12), (0.06, 0.06, 0.32), LINE, rot=Rx(s * -0.3) @ Ry(0.4), **NS)
    m.box("Snout", hc + V(0.7, 0, -0.2), (0.6, 0.52, 0.42), WH, top=(0.75, 0.85), bot=(0.9, 0.9))
    m.box("Nose", hc + V(1.02, 0, -0.08), (0.1, 0.24, 0.18), BLK, **NS)
    m.box("Mouth", hc + V(1.0, 0, -0.32), (0.06, 0.28, 0.05), BLK, **NS)
    m.box("Smile", hc + V(0.85, 0.2, -0.3), (0.3, 0.05, 0.05), BLK, rot=Rz(-0.4) @ Ry(-0.35), **NS)
    m.eyes(tuple(hc + V(0.48, 0.3, 0.12)), facing=(0.9, 0.35, 0), size=(0.36, 0.34), pupil=0.75, look=(0.4, 0.05), angry=0.1,
           white=AMBER, brow_col=SAND_D, brow_h=0.38, brow_up=0.78, depth=0.1)
    for s in (1, -1):                                        # the enormous ears: up and out in a wide V
        with m.bone(f"Ear_{LR(s)}", hc + V(-0.15, s * 0.42, 0.42)):
            o = hc + V(-0.12, s * 0.42, 0.38)
            ax = V(0.12, s * 0.72, 1.0).normalized(); wx = V(0, 1.0, -s * 0.72).normalized()   # plate faces forward
            m.slab(f"Ear{s}", [(-0.5, 0), (0.5, 0), (0.42, 0.9), (0.1, 1.95), (-0.1, 1.95), (-0.42, 0.9)], 0.16, SAND,
                   origin=o, xaxis=wx, yaxis=ax)
            m.slab(f"EarIn{s}", [(-0.33, 0.1), (0.33, 0.1), (0.28, 0.9), (0.06, 1.65), (-0.06, 1.65), (-0.28, 0.9)], 0.06, EARIN,
                   origin=o + V(0.11, 0, 0), xaxis=wx, yaxis=ax)
            for k in range(3):
                b = o + ax * 0.15 + V(0.15, s * (k - 1) * 0.05, (k - 1) * 0.12)
                m.spike(f"EarTuft{s}{k}", b, b + V(0.3, -s * 0.1, 0.2), 0.08, WH, flat=0.6)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
