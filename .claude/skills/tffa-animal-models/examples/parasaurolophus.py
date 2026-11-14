"""TFFA Parasaurolophus (DinoLand) - hero build v2 on the user-approved T-Rex body proportions (v1, a lanky custom build,
was rejected; T-Rex + Ankylosaurus approved -> chunky TFFA proportions: big head, thick legs, heavy body).

Reference analysis (iconic Parasaurolophus):
1. Silhouette: the chunky T-Rex stance (heavy leaning body, thick legs, long tail), herbivore version with sturdier arms;
   the LONG TUBULAR CREST sweeping back from the head is the highest point.
2. Head: a big boxy head with a wide, flat, closed duck bill (lighter colour, flared tip), calm proud side eye.
3. Signature: orange crest with a gold stripe and a darker tip cap; dark vertical stripes over teal; cream belly/throat.
4. Colours: teal, dark teal stripes, cream, orange crest, gold stripe, tan bill.
Bones: Body, Neck, Head, Tail1-4, Leg_L/R, Arm_L/R (same as the theropod family, so clips are shared). Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector
import numpy as np

TEAL, TEAL_D, BELLY, CREST, CREST_D, STRIPE, BILL, BILL_D = rgb(60, 156, 136), rgb(30, 92, 80), rgb(244, 230, 194), rgb(248, 122, 40), rgb(196, 76, 28), rgb(254, 214, 70), rgb(236, 202, 142), rgb(150, 112, 72)
LR = lambda t: "L" if t > 0 else "R"
s = 0.95
S = lambda x, y, z: Vector((x * s, y * s, z * s)); Z = lambda *a: tuple(v * s for v in a)

m = Model("Parasaurolophus", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.6, chamfer=0.14, jitter=0.07)
body = m.bone("Body", S(0, 0, 5.0)); body.__enter__()
m.box("Body", S(0, 0, 5.0), Z(5.4, 3.9, 3.9), TEAL, rot=Ry(-0.35), top=(0.85, 0.85))
m.box("Belly", S(0.8, 0, 4.2), Z(3.6, 3.1, 2.6), BELLY, rot=Ry(-0.45), studs=False)
for t in (1, -1):
    for j, x in enumerate((1.5, 0.5, -0.5, -1.5)):
        m.box(f"Stripe{t}{j}", S(x, t * 1.98, 5.3 + x * 0.3), Z(0.4, 0.1, 2.0), TEAL_D, rot=Ry(-0.35), studs=False)
tp = [S(-2.3, 0, 5.3), S(-4.4, 0, 5.4), S(-6.3, 0, 5.6), S(-8.0, 0, 6.0), S(-9.3, 0, 6.5)]
m.chain("Tail", tp, [v * s for v in (3.0, 2.4, 1.8, 1.2, 0.6)], TEAL, bones="Tail")
for i in range(3):
    with m.bone(f"Tail{i + 1}"):
        q = tp[i].lerp(tp[i + 1], 0.5); w = [2.7, 2.1, 1.5][i] * s
        for t in (1, -1): m.box(f"TailStripe{i}{t}", q + Vector((0, t * w * 0.5, 0)), (0.4 * s, 0.1, w * 0.8), TEAL_D, studs=False)
for t in (1, -1):
    with m.bone(f"Leg_{LR(t)}", S(-0.6, t * 1.9, 4.8)):
        m.box(f"Thigh{t}", S(-0.6, t * 1.9, 4.0), Z(2.8, 1.5, 3.4), TEAL, rot=Ry(0.25), top=(0.85, 0.9))
        m.seg(f"Shin{t}", S(-0.9, t * 2.0, 2.6), S(-0.3, t * 2.0, 0.7), 1.3 * s, 1.1 * s, TEAL)
        m.box(f"Foot{t}", S(0.3, t * 2.0, 0.4), Z(2.4, 1.6, 0.8), TEAL_D)
        for k in (-1, 0, 1): m.box(f"Hoof{t}{k}", S(1.55, t * 2.0 + k * 0.5, 0.3), Z(0.45, 0.42, 0.55), BELLY, studs=False)
    with m.bone(f"Arm_{LR(t)}", S(2.3, t * 1.55, 5.2)):
        m.seg(f"Arm{t}", S(2.3, t * 1.55, 5.2), S(3.0, t * 1.75, 3.9), 0.85 * s, 0.7 * s, TEAL)
        m.seg(f"Forearm{t}", S(3.0, t * 1.75, 4.0), S(3.45, t * 1.8, 3.0), 0.7 * s, 0.6 * s, TEAL)
        m.box(f"Hand{t}", S(3.55, t * 1.8, 2.75), Z(0.75, 0.7, 0.55), TEAL_D, studs=False)
H_ = S(3.2, 0, 7.6)
with m.bone("Neck", S(1.8, 0, 6.0)):
    m.seg("Neck", S(1.8, 0, 6.0), S(3.0, 0, 7.7), 3.0 * s, 2.6 * s, TEAL, d0=3.2 * s, d1=2.8 * s)
    m.box("Throat", S(3.4, 0, 6.6), Z(2.0, 2.6, 2.0), BELLY, rot=Ry(0.2), studs=False)
with m.bone("Head", H_, "Neck"):
    hc = S(4.15, 0, 8.55)
    m.box("Head", hc, Z(2.8, 2.9, 2.3), TEAL, top=(0.88, 0.9), bot=(0.92, 0.92))
    m.box("Cheek", hc + Vector((0.2, 0, -0.85)) * s, Z(2.3, 2.95, 0.7), BELLY, studs=False)
    m.box("Bill", hc + Vector((2.2, 0, -0.55)) * s, Z(2.0, 2.4, 1.15), BILL, top=(0.95, 0.95))
    m.box("BillTip", hc + Vector((3.25, 0, -0.55)) * s, Z(0.55, 2.9, 1.08), BILL, top=(0.92, 0.95))
    m.box("BillLine", hc + Vector((2.55, 0, -0.68)) * s, Z(2.8, 2.98, 0.1), BILL_D, studs=False)
    for t in (1, -1): m.box(f"Nostril{t}", hc + Vector((2.95, t * 0.75, -0.02)) * s, Z(0.5, 0.25, 0.18), BILL_D, studs=False)
    m.eyes(tuple(hc + Vector((0.25, 1.47, 0.35)) * s), facing=(0.3, 1, 0), size=Z(1.15, 1.05), pupil=0.68, look=(0.3, 0), angry=0.1,
           brow_col=TEAL_D, brow_h=0.38, brow_up=0.66, brow_w=1.2, depth=0.3 * s)
    cp = [hc + Vector(v) * s for v in ((-0.1, 0, 1.0), (-1.3, 0, 2.2), (-2.9, 0, 2.8), (-4.5, 0, 2.6), (-5.6, 0, 2.0))]
    m.chain("Crest", cp, [w * s for w in (1.15, 1.05, 0.95, 0.85, 0.7)], CREST, studs=False)
    for i in range(4):
        a, b = cp[i], cp[i + 1]; d = (b - a).normalized(); up = Vector((-d.z, 0, d.x))
        m.seg(f"CrestStripe{i}", a + up * 0.5 * s, b + up * 0.45 * s, 0.6 * s, 0.5 * s, STRIPE, d0=0.14 * s, d1=0.14 * s, studs=False)
    m.box("CrestTip", cp[-1] + Vector((-0.25, 0, -0.1)) * s, Z(0.8, 0.82, 0.8), CREST_D, top=(0.8, 0.8), studs=False)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 50), ("ref", 50, 8, 50)])
