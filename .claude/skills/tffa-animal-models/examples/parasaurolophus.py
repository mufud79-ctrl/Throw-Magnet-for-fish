"""TFFA Parasaurolophus (DinoLand) - hero build.

Reference analysis (iconic Parasaurolophus art, most important first):
1. Silhouette: a big duck-billed hadrosaur in a tripod stance - strong hind legs, body tilted forward, front hands
   touching down, a long thick tail as counterweight; the LONG TUBULAR CREST sweeping back from the head is the
   highest point and the signature.
2. Head: long flat duck bill (lighter) with a widened tip, calm proud side eyes.
3. Signature: the crest is bright orange with a yellow stripe, joined to the neck by a skin frill; dark vertical
   stripes over a teal back, pale belly.
4. Colours: teal green, dark teal stripes, cream belly, orange crest + frill, yellow stripe, tan bill.
Bones: Body, Neck, Head, Tail1..4, Leg_L/R, Arm_L/R. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

TEAL, TEAL_D, BELLY, CREST, CREST_D, STRIPE, BILL = rgb(62, 156, 134), rgb(32, 92, 80), rgb(242, 228, 192), rgb(246, 122, 40), rgb(206, 84, 30), rgb(252, 214, 70), rgb(232, 198, 140)
V = lambda *a: Vector(a); LR = lambda s: "L" if s > 0 else "R"

m = Model("Parasaurolophus", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.6, chamfer=0.15, jitter=0.06)
m.gait = {"amp": 0.85}
body = m.bone("Body", (0, 0, 4.3)); body.__enter__()
m.box("Body", (0, 0, 4.3), (4.3, 2.7, 2.7), TEAL, rot=Ry(-0.25), top=(0.85, 0.85), bot=(0.85, 0.88))
m.box("Belly", (0.5, 0, 3.4), (3.4, 2.3, 1.2), BELLY, rot=Ry(-0.3), studs=False)
for s in (1, -1):
    for k, x in enumerate((1.2, 0.3, -0.6, -1.5)):
        m.box(f"Stripe{s}{k}", (x, s * 1.37, 4.55 + x * 0.22), (0.3, 0.06, 1.4), TEAL_D, rot=Ry(-0.25), studs=False)
    with m.bone(f"Leg_{LR(s)}", (-0.5, s * 1.3, 4.0)):
        m.box(f"Thigh{s}", (-0.55, s * 1.35, 3.5), (2.2, 1.1, 2.6), TEAL, rot=Ry(0.25), top=(0.85, 0.9), bot=(0.75, 0.85))
        m.seg(f"Shin{s}", V(-0.85, s * 1.4, 2.4), V(-0.35, s * 1.4, 0.65), 1.0, 0.85, TEAL)
        m.box(f"Foot{s}", (0.25, s * 1.4, 0.3), (1.8, 1.15, 0.6), TEAL_D, top=(0.85, 0.9))
        for t in (-1, 0, 1): m.box(f"Hoof{s}{t}", (1.18, s * 1.4 + t * 0.36, 0.22), (0.3, 0.3, 0.4), BELLY, studs=False)
    with m.bone(f"Arm_{LR(s)}", (1.8, s * 1.05, 4.0)):
        m.seg(f"Arm{s}", V(1.8, s * 1.05, 4.0), V(2.3, s * 1.2, 2.2), 0.75, 0.6, TEAL)
        m.seg(f"Forearm{s}", V(2.3, s * 1.2, 2.3), V(2.55, s * 1.25, 0.45), 0.6, 0.5, TEAL)
        m.box(f"Hand{s}", (2.7, s * 1.25, 0.22), (0.75, 0.7, 0.44), TEAL_D, studs=False)

pts = [V(-2.0, 0, 4.7), V(-3.8, 0, 4.3), V(-5.5, 0, 4.0), V(-7.0, 0, 3.9), V(-8.2, 0, 4.0)]
m.chain("Tail", pts, [2.0, 1.5, 1.05, 0.65, 0.3], TEAL, bones="Tail")
for i in range(3):
    with m.bone(f"Tail{i + 1}"):
        q = pts[i].lerp(pts[i + 1], 0.5); w = [1.75, 1.27, 0.85][i]
        for s in (1, -1): m.box(f"TailStripe{i}{s}", q + V(0, s * w * 0.5, 0.1), (0.3, 0.06, w * 0.8), TEAL_D, studs=False)

with m.bone("Neck", (1.8, 0, 5.0)):
    m.seg("Neck", V(1.6, 0, 4.9), V(2.85, 0, 6.6), 1.55, 1.2, TEAL, d0=1.7, d1=1.3)
    m.box("Throat", (2.55, 0, 5.6), (0.9, 1.1, 1.4), BELLY, rot=Ry(-0.6), studs=False)
with m.bone("Head", (2.8, 0, 6.6), "Neck"):
    hc = V(3.35, 0, 6.9)
    m.box("Head", hc, (1.65, 1.35, 1.25), TEAL, top=(0.85, 0.88), bot=(0.9, 0.9))
    m.box("Bill", hc + V(1.2, 0, -0.35), (1.3, 1.15, 0.62), BILL, top=(0.95, 0.95))
    m.box("BillTip", hc + V(1.95, 0, -0.35), (0.35, 1.4, 0.58), BILL, top=(0.9, 0.95))
    m.box("BillLine", hc + V(1.4, 0, -0.42), (1.6, 1.42, 0.06), rgb(150, 110, 70), studs=False)
    for s in (1, -1): m.box(f"Nostril{s}", hc + V(1.75, s * 0.4, -0.08), (0.3, 0.12, 0.1), rgb(110, 80, 50), studs=False)
    m.eyes(tuple(hc + V(0.15, 0.68, 0.18)), facing=(0.35, 1, 0), size=(0.58, 0.52), pupil=0.66, look=(0.3, 0), angry=0.1,
           brow_col=TEAL_D, brow_h=0.32, brow_up=0.66, depth=0.13)
    cp = [hc + V(0.0, 0, 0.45), hc + V(-0.9, 0, 1.2), hc + V(-2.1, 0, 1.55), hc + V(-3.3, 0, 1.45), hc + V(-4.1, 0, 1.15)]   # long tube crest
    m.chain("Crest", cp, [0.72, 0.66, 0.6, 0.54, 0.46], CREST, studs=False)
    m.box("CrestTip", cp[-1] + V(-0.15, 0, -0.08), (0.5, 0.5, 0.5), CREST_D, top=(0.8, 0.8), studs=False)
    for i in range(4):
        a, b = cp[i], cp[i + 1]; d = (b - a).normalized(); up = V(-d.z, 0, d.x)
        m.seg(f"CrestStripe{i}", a + up * 0.34, b + up * 0.3, 0.44, 0.38, STRIPE, d0=0.1, d1=0.1, studs=False)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 6, 45), ("side", 90, 4, 50), ("ref", 50, 8, 45)])
