"""TFFA Triceratops (DinoLand) - hero build in the user-approved Ankylosaurus proportions (the archetype version - small
head, flat frill - was rejected; chunky, wide, short thick legs and a BIG head are what was approved).

Reference analysis (iconic Triceratops, most important first):
1. Silhouette: a chunky, wide, low quadruped; the HEAD is the hero - a huge shield frill rising behind it (the tallest
   thing) and two long brow horns pointing forward-up, plus a short nose horn.
2. Head: big boxy head with a dark hooked beak, angry side eyes under heavy brow ridges, cheek horns.
3. Signature: the frill has a darker rim lined with cream epoccipital spikes and two big eye-spot patches; heavy
   pillar legs with hoofed toes; a short thick tail.
4. Colours: warm orange-brown body, golden frill with a red-brown rim, cream horns/spikes, cream belly.
Bones: Body, Head, Leg_FL/FR/BL/BR, Tail1..3. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

BODY, BODY_D, BELLY, FRILL, RIM, SPOT, HORNC = rgb(208, 124, 60), rgb(148, 80, 38), rgb(240, 224, 186), rgb(248, 186, 70), rgb(176, 64, 40), rgb(120, 52, 34), rgb(244, 236, 214)
V = lambda *a: Vector(a); LR = lambda s: "L" if s > 0 else "R"

m = Model("Triceratops", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.5, chamfer=0.16, jitter=0.06)
m.gait = {"amp": 0.8}
body = m.bone("Body", (0, 0, 2.6)); body.__enter__()
m.box("Body", (-0.2, 0, 2.6), (4.6, 3.7, 2.8), BODY, top=(0.84, 0.86), bot=(0.88, 0.9))
m.box("Shoulders", (1.4, 0, 3.0), (1.8, 3.9, 2.4), BODY, top=(0.8, 0.84))
m.box("Belly", (0.0, 0, 1.25), (4.0, 3.0, 0.45), BELLY, studs=False)
m.box("BackRidge", (-0.4, 0, 4.05), (3.4, 1.4, 0.3), BODY_D, top=(0.7, 0.8))
for sx in (1, -1):
    for s in (1, -1):
        x = sx * 1.55 - 0.1; y = s * 1.45
        with m.bone(f"Leg_{'F' if sx > 0 else 'B'}{LR(s)}", (x, y, 1.6)):
            m.box(f"Leg{sx}{s}", (x, y, 0.85), (1.3, 1.2, 1.7), BODY, top=(1.0, 1.0), bot=(0.9, 0.9))
            m.box(f"Foot{sx}{s}", (x + 0.12, y, 0.2), (1.5, 1.35, 0.4), BODY_D, studs=False)
            for t in (-1, 0, 1): m.box(f"Hoof{sx}{s}{t}", (x + 0.82, y + t * 0.4, 0.17), (0.28, 0.3, 0.34), HORNC, studs=False)
pts = [V(-2.4, 0, 2.9), V(-3.7, 0, 2.55), V(-4.8, 0, 2.2), V(-5.6, 0, 2.0)]
m.chain("Tail", pts, [1.9, 1.35, 0.9, 0.5], BODY, bones="Tail")
for i in (1, 2):
    with m.bone(f"Tail{i}"):
        q = pts[i].lerp(pts[i + 1], 0.5); m.box(f"TailRidge{i}", q + V(0, 0, [1.35, 0.9][i - 1] * 0.5), (0.7, 0.5, 0.22), BODY_D, studs=False)

with m.bone("Head", (2.4, 0, 2.9)), m.frame(pivot=(2.4, 0, 2.9), scale=1.25):
    hc = V(3.35, 0, 2.75)
    # frill: big shield tilted back behind the head, rim + epoccipital spikes, eye-spots
    fo = hc + V(-0.75, 0, 0.55); xa = (0, 1, 0); ya = V(-0.42, 0, 1).normalized()
    R = 2.0
    outline = [(R * math.cos(a), R * 0.95 * math.sin(a) + 0.15) for a in [math.radians(d) for d in range(-25, 206, 23)]]
    outline = outline + [(-R * 0.7, -0.55), (R * 0.7, -0.55)][::-1]
    m.slab("FrillRim", [(x * 1.08, y * 1.08) for x, y in outline], 0.32, RIM, origin=fo - V(0.06, 0, 0), xaxis=xa, yaxis=ya)
    m.slab("Frill", outline, 0.42, FRILL, origin=fo + V(0.04, 0, 0), xaxis=xa, yaxis=ya)
    for k, a in enumerate([math.radians(d) for d in range(-10, 191, 25)]):
        p = fo + V(0, R * 1.12 * math.cos(a), 0) + ya * (R * 1.12 * 0.95 * math.sin(a) + 0.15)
        m.spike(f"Epoccipital{k}", p, p + (V(0, math.cos(a), 0) + ya * math.sin(a)).normalized() * 0.55, 0.16, HORNC, flat=0.5)
    for s in (1, -1):
        sp = fo + V(0.24, s * 0.95, 0) + ya * 1.1
        m.box(f"FrillSpot{s}", sp, (0.08, 0.7, 0.7), SPOT, rot=Ry(-0.4), studs=False)
    m.box("Head", hc, (1.9, 2.1, 1.7), BODY, top=(0.86, 0.88), bot=(0.9, 0.9))
    m.box("Snout", hc + V(1.15, 0, -0.25), (0.9, 1.45, 1.15), BODY, top=(0.85, 0.85))
    m.box("Beak", hc + V(1.72, 0, -0.42), (0.42, 1.05, 0.9), rgb(64, 48, 40), top=(0.8, 0.85), bot=(0.6, 0.7), studs=False)
    m.box("Cheek", hc + V(0.2, 0, -0.7), (1.6, 2.15, 0.35), BELLY, studs=False)
    m.spike("NoseHorn", hc + V(1.3, 0, 0.3), hc + V(1.65, 0, 1.05), 0.2, HORNC, sides=5)
    for s in (1, -1):
        m.box(f"BrowRidge{s}", hc + V(0.45, s * 0.62, 0.78), (0.9, 0.5, 0.36), BODY_D, top=(0.8, 0.9))
        m.spike(f"BrowHorn{s}", hc + V(0.35, s * 0.6, 0.85), hc + V(2.2, s * 0.85, 2.3), 0.26, HORNC, sides=5)
        m.spike(f"CheekHorn{s}", hc + V(0.0, s * 1.05, -0.45), hc + V(-0.35, s * 1.55, -0.7), 0.17, HORNC, flat=0.6)
    m.eyes(tuple(hc + V(0.4, 1.06, 0.3)), facing=(0.35, 1, 0), size=(0.55, 0.5), pupil=0.68, look=(0.35, 0), angry=0.4,
           brow_col=BODY_D, brow_h=0.42, brow_up=0.7, depth=0.13)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 35, 16, 45)])
