"""TFFA Compy (Compsognathus, DinoLand) - hero build.

Reference analysis (iconic Compsognathus - the cheeky pack scavenger, most important first):
1. Silhouette: a small, lean biped leaning forward in a pounce: long S-curved neck, long whip tail held straight back
   as a counterweight, long bird-like legs with three-toed feet, tiny clawed arms.
2. Head: a big (TFFA) narrow head with a pointed snout, a toothy grin, big mischievous eyes.
3. Signature (the twist): it's a little thief - a STOLEN DRUMSTICK clamped in its jaws; a spiky orange proto-feather
   crest down the neck; dark stripes across the back and tail.
4. Colours: lime green, dark green stripes, yellow belly, orange crest, cream claws/teeth.
Bones: Body, Neck, Head, Tail1..3, Leg_L/R, Arm_L/R. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

GRN, GRN_D, BELLY, CREST, MEAT, BONEC = rgb(124, 194, 72), rgb(50, 112, 40), rgb(244, 222, 120), rgb(244, 130, 40), rgb(196, 110, 60), rgb(246, 240, 224)
V = lambda *a: Vector(a); LR = lambda s: "L" if s > 0 else "R"

m = Model("Compy", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.3, chamfer=0.17, jitter=0.05)
body = m.bone("Body", (0, 0, 2.0)); body.__enter__()
m.box("Body", (0, 0, 2.05), (1.75, 1.15, 1.1), GRN, rot=Ry(-0.2), top=(0.85, 0.85), bot=(0.85, 0.9))
m.box("Belly", (0.15, 0, 1.6), (1.3, 0.95, 0.3), BELLY, rot=Ry(-0.2), studs=False)
for k, x in enumerate((0.45, 0.0, -0.45)):
    m.box(f"Stripe{k}", (x, 0, 2.62 - x * 0.18), (0.16, 1.0, 0.08), GRN_D, rot=Ry(-0.2), studs=False)
for s in (1, -1):
    with m.bone(f"Leg_{LR(s)}", (-0.2, s * 0.42, 1.8)):
        m.box(f"Thigh{s}", (-0.2, s * 0.5, 1.6), (0.85, 0.45, 0.95), GRN, rot=Ry(0.45), top=(0.85, 0.9))
        m.seg(f"Shin{s}", V(-0.42, s * 0.5, 1.25), V(-0.15, s * 0.5, 0.42), 0.32, 0.26, GRN)
        m.seg(f"Ankle{s}", V(-0.15, s * 0.5, 0.45), V(0.05, s * 0.5, 0.15), 0.26, 0.22, GRN)
        m.box(f"Foot{s}", (0.3, s * 0.5, 0.1), (0.7, 0.32, 0.2), GRN_D, studs=False)
        for t in (-1, 0, 1): m.spike(f"Toe{s}{t}", V(0.62, s * 0.5 + t * 0.12, 0.1), V(0.85, s * 0.5 + t * 0.16, 0.03), 0.06, BONEC, flat=0.5)
    with m.bone(f"Arm_{LR(s)}", (0.7, s * 0.42, 2.0)):
        m.seg(f"Arm{s}", V(0.7, s * 0.45, 2.0), V(1.0, s * 0.5, 1.7), 0.2, 0.16, GRN)
        for t in (-1, 1): m.spike(f"Claw{s}{t}", V(1.02, s * 0.5 + t * 0.05, 1.68), V(1.15, s * 0.5 + t * 0.06, 1.52), 0.04, BONEC, flat=0.5)
pts = [V(-0.8, 0, 2.15), V(-1.8, 0, 2.25), V(-2.8, 0, 2.4), V(-3.7, 0, 2.55)]
m.chain("Tail", pts, [0.72, 0.5, 0.32, 0.14], GRN, bones="Tail")
for i in range(3):
    with m.bone(f"Tail{i + 1}"):
        q = pts[i].lerp(pts[i + 1], 0.5); w = [0.6, 0.41, 0.23][i]
        m.box(f"TailStripe{i}", q + V(0, 0, w * 0.45), (0.14, w * 0.9, 0.06), GRN_D, studs=False)

with m.bone("Neck", (0.7, 0, 2.35)):
    m.seg("Neck1", V(0.55, 0, 2.3), V(1.0, 0, 2.95), 0.58, 0.5, GRN)
    m.seg("Neck2", V(0.95, 0, 2.9), V(1.25, 0, 3.35), 0.5, 0.45, GRN)
    for k, (x, z) in enumerate(((0.55, 2.75), (0.8, 3.15), (1.0, 3.5), (1.2, 3.85))):     # spiky proto-feather crest
        m.spike(f"Crest{k}", V(x, 0, z - 0.1), V(x - 0.35, 0, z + 0.3), 0.14, CREST, flat=0.5)
with m.bone("Head", (1.25, 0, 3.4), "Neck"):
    hc = V(1.7, 0, 3.55)
    m.box("Head", hc, (1.0, 0.8, 0.72), GRN, top=(0.85, 0.85), bot=(0.9, 0.9))
    m.box("Snout", hc + V(0.72, 0, -0.08), (0.7, 0.6, 0.45), GRN, top=(0.85, 0.85))
    m.box("Jaw", hc + V(0.6, 0, -0.42), (0.85, 0.52, 0.16), BELLY, rot=Ry(0.15), studs=False)
    m.box("Mouth", hc + V(0.62, 0, -0.3), (0.75, 0.5, 0.1), MOUTH, studs=False)
    for t in (1, -1):
        for k, x in enumerate((0.45, 0.65, 0.85)): m.spike(f"Tooth{t}{k}", hc + V(x, t * 0.26, -0.28), hc + V(x + 0.02, t * 0.26, -0.42), 0.04, TOOTH, flat=0.3)
    for k in range(2): m.spike(f"HeadCrest{k}", hc + V(-0.2 - k * 0.25, 0, 0.36), hc + V(-0.55 - k * 0.25, 0, 0.7), 0.12, CREST, flat=0.5)
    m.eyes(tuple(hc + V(0.18, 0.41, 0.12)), facing=(0.45, 0.9, 0.1), size=(0.42, 0.42), pupil=0.62, look=(0.4, 0.05), angry=0.2,
           brow_col=GRN_D, brow_h=0.35, brow_up=0.68, depth=0.1)
    d0, d1 = hc + V(0.85, -0.6, -0.32), hc + V(0.85, 0.55, -0.32)           # stolen drumstick clamped in the jaws
    m.seg("BoneShaft", d0, d1, 0.12, 0.12, BONEC, studs=False)
    m.box("BoneKnob1", d0 + V(0, -0.06, 0.05), (0.16, 0.14, 0.24), BONEC, studs=False)
    m.box("BoneKnob2", d0 + V(0, -0.06, -0.08), (0.16, 0.14, 0.2), BONEC, studs=False)
    m.box("Meat", d1 + V(0, 0.18, 0), (0.42, 0.42, 0.42), MEAT, top=(0.8, 0.8), bot=(0.8, 0.8), studs=False)
    m.box("MeatBite", d1 + V(0.18, 0.22, 0.12), (0.1, 0.16, 0.14), rgb(240, 200, 170), studs=False)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 30, 10, 45)])
