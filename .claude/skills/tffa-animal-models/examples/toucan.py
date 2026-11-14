"""TFFA Toucan (Jungle, Cannon Tame) - hero build: a toco toucan.

Reference analysis (the iconic toco toucan on a branch, most important first):
1. Silhouette: upright black egg body with a long square tail angled down-back, and a GIANT bill as long as the body
   sticking straight forward from a smallish head - the bill is what reads at thumbnail size.
2. Head: black crown, bare orange skin round the eye, bright blue eye ring with a big black pupil, a narrow brow.
3. Signature: the bill - tall at the base (as tall as the head), yellow-orange at the base turning deep orange, a red
   ridge along the top, a black base band and a black tip with a small hook; the white throat bib; red under the tail.
4. Colours: black (slightly blue sheen on wing feathers), white bib, bill orange/yellow + red + black, blue eye ring,
   blue-grey legs.
Bones: Body, Head, Wing_L/R, Leg_L/R, Tail1 (walk + fly). Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

BLK, BLK_B, BIB, BIB_Y = rgb(30, 30, 38), rgb(40, 46, 70), rgb(250, 246, 232), rgb(255, 226, 120)
BILL_Y, BILL_O, BILL_R, RIDGE = rgb(255, 196, 40), rgb(255, 138, 28), rgb(240, 92, 24), rgb(214, 34, 30)
SKIN, RING, LEG, RED = rgb(255, 168, 40), rgb(56, 140, 236), rgb(86, 112, 186), rgb(220, 30, 40)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Toucan", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.4, chamfer=0.16, jitter=0.04)

body = m.bone("Body", (0, 0, 2.2)); body.__enter__()
m.seg("Body", V(-0.55, 0, 1.25), V(0.12, 0, 3.25), 1.85, 1.7, BLK, d0=1.7, d1=1.55)
m.box("Bib", (0.6, 0, 3.05), (0.35, 1.45, 1.1), BIB, rot=Ry(-0.3), top=(0.9, 0.9), bot=(0.8, 0.8))
m.box("BibEdge", (0.48, 0, 2.48), (0.3, 1.2, 0.25), BIB_Y, rot=Ry(-0.3), **NS)
m.box("UnderTail", (-0.85, 0, 1.12), (0.65, 0.95, 0.45), RED, rot=Ry(0.5), top=(0.8, 0.8))

with m.bone("Head", (0.2, 0, 3.3)), m.frame(pivot=(0.2, 0, 3.3), scale=1.15):
    hc = V(0.35, 0, 3.85)
    m.box("Head", hc, (1.35, 1.32, 1.25), BLK, top=(0.82, 0.85), bot=(0.95, 0.95))
    m.box("Throat", hc + V(0.3, 0, -0.5), (0.7, 1.15, 0.45), BIB, **NS)
    for s in (1, -1):
        m.box(f"EyeSkin{s}", hc + V(0.28, s * 0.63, 0.08), (0.68, 0.1, 0.6), SKIN, **NS)
    m.eyes(tuple(hc + V(0.3, 0.68, 0.1)), facing=(0.25, 1, 0), size=(0.42, 0.42), pupil=0.68, look=(0.15, 0), angry=0.22,
           white=RING, brow_col=BLK, brow_h=0.42, brow_up=0.78, depth=0.12)
    # the giant bill
    m.box("BillBand", hc + V(0.67, 0, 0.0), (0.14, 0.98, 1.12), BLK, **NS)
    m.seg("BillUpper0", hc + V(0.62, 0, 0.12), hc + V(1.85, 0, 0.08), 0.86, 0.66, BILL_Y, d0=0.98, d1=0.76)
    m.seg("BillUpper1", hc + V(1.8, 0, 0.08), hc + V(3.0, 0, -0.28), 0.66, 0.3, BILL_O, d0=0.76, d1=0.36)
    m.seg("BillLower", hc + V(0.62, 0, -0.45), hc + V(2.75, 0, -0.5), 0.76, 0.3, BILL_R, d0=0.42, d1=0.22)
    m.seg("BillLine", hc + V(0.7, 0, -0.27), hc + V(2.8, 0, -0.42), 0.8, 0.3, rgb(120, 50, 20), d0=0.06, d1=0.05, **NS)
    m.seg("Ridge0", hc + V(0.72, 0, 0.66), hc + V(1.85, 0, 0.5), 0.24, 0.2, RIDGE, d0=0.14, d1=0.13, **NS)
    m.seg("Ridge1", hc + V(1.8, 0, 0.5), hc + V(2.95, 0, -0.06), 0.2, 0.1, RIDGE, d0=0.13, d1=0.1, **NS)
    m.seg("BillTip", hc + V(2.9, 0, -0.25), hc + V(3.35, 0, -0.42), 0.32, 0.14, BLK, d0=0.38, d1=0.16, **NS)
    m.spike("BillHook", hc + V(3.3, 0, -0.38), hc + V(3.42, 0, -0.62), 0.09, BLK, flat=0.6)
    m.seg("LowerTip", hc + V(2.6, 0, -0.5), hc + V(2.95, 0, -0.55), 0.3, 0.16, BLK, d0=0.22, d1=0.12, **NS)

for s in (1, -1):
    with m.bone(f"Wing_{LR(s)}", (0.1, s * 0.85, 3.05)):
        m.seg(f"Wing{s}", V(0.15, s * 0.98, 3.0), V(-0.75, s * 1.05, 1.75), 0.34, 0.28, BLK, d0=1.3, d1=0.95)
        for k in range(3):                                 # primaries fanning down past the tail base
            o = V(-0.55 - k * 0.15, s * (1.04 - k * 0.04), 1.95 + k * 0.05)
            d = V(-0.75 - 0.1 * k, 0, -0.55 + 0.12 * k).normalized()
            m.slab(f"Primary{s}{k}", [(-0.22, 0), (0.22, 0), (0.18, 0.9), (0, 1.05), (-0.18, 0.9)], 0.1, BLK_B,
                   origin=o, xaxis=(d.z, 0, -d.x), yaxis=d)

with m.bone("Tail1", (-0.75, 0, 1.45)):
    for k, y in enumerate((-0.32, 0.0, 0.32)):
        m.seg(f"Tail{k}", V(-0.75, y * 0.6, 1.5), V(-2.05, y, 0.7 + 0.06 * (k == 1)), 0.6, 0.62, BLK, d0=0.22, d1=0.18)

for s in (1, -1):
    with m.bone(f"Leg_{LR(s)}", (-0.1, s * 0.45, 1.4)):
        m.seg(f"Thigh{s}", V(-0.1, s * 0.45, 1.45), V(0.05, s * 0.5, 0.75), 0.55, 0.42, BLK)
        m.seg(f"Shank{s}", V(0.05, s * 0.5, 0.82), V(0.12, s * 0.5, 0.18), 0.24, 0.2, LEG, **NS)
        for k in (-1, 1):
            m.spike(f"ToeF{s}{k}", V(0.12, s * 0.5 + k * 0.1, 0.12), V(0.62, s * 0.5 + k * 0.18, 0.04), 0.09, LEG)
            m.spike(f"ToeB{s}{k}", V(0.08, s * 0.5 + k * 0.1, 0.12), V(-0.42, s * 0.5 + k * 0.16, 0.04), 0.08, LEG)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
