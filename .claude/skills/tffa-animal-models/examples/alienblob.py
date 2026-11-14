"""TFFA AlienBlob (Space) - hero build.

Reference analysis (iconic slime / ooze alien, most important first):
1. Silhouette: a tall tiered goo mound (puddle base -> wide body -> narrower top -> dome) leaning forward, three eyeballs
   on wobbly stalks rising above it, two goo arms reaching out low.
2. Face: a huge wide grin across the front with jagged teeth top and bottom and goo strands between them; the eyeballs
   have heavy lids (angry), so it reads menacing, not cute.
3. Signature: drips hanging off every ledge, glowing nucleus spots inside the goo, a bubbling top.
4. Colours: lime body, darker green ledges/puddle, glowing yellow-green spots; white eyes + teeth.
Bones: Body, Tent0..2_<j> (eye stalks), Tent3/4_<j> (arms). Crawl gait. Studded."""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

GOO, GOO_D, GOO_L, GLOW = rgb(112, 222, 84), rgb(52, 150, 56), rgb(170, 246, 130), rgb(210, 255, 110)
V = lambda *a: Vector(a)

m = Model("AlienBlob", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.45, chamfer=0.18, jitter=0.06)
m.gait = {"crawl": True}
body = m.bone("Body", (0, 0, 1.2)); body.__enter__()
m.box("Puddle", (0.1, 0, 0.16), (4.5, 3.6, 0.32), GOO_D, top=(0.92, 0.92))
m.box("Puddle2", (0.0, 0, 0.14), (3.5, 3.5, 0.28), GOO_D, rot=Rz(0.785), top=(0.92, 0.92))
for k, (x, y, r) in enumerate(((2.3, 1.3, 0.6), (-2.2, -1.4, 0.7), (-1.0, 2.0, 0.5), (1.4, -1.9, 0.55))):
    m.box(f"Splat{k}", (x, y, 0.1), (r, r, 0.2), GOO_D, studs=False)
m.box("Lower", (0.1, 0, 0.95), (3.6, 3.2, 1.4), GOO, top=(0.92, 0.92), bot=(1.0, 1.0))
m.box("Mid", (-0.05, 0, 2.15), (3.0, 2.75, 1.15), GOO, top=(0.82, 0.84), shift=(-0.15, 0))
m.box("Upper", (-0.3, 0, 3.05), (2.3, 2.15, 0.85), GOO, top=(0.7, 0.72), shift=(-0.15, 0))
m.box("Dome", (-0.5, 0, 3.65), (1.5, 1.45, 0.5), GOO_L, top=(0.55, 0.6))
for k, (x, y, r) in enumerate(((-0.2, 0.4, 0.32), (-0.7, -0.35, 0.26), (-0.4, -0.05, 0.2))):   # bubbles on the top
    m.box(f"Bubble{k}", (x, y, 3.98), (r, r, r * 0.8), GOO_L, studs=False)
rnd = random.Random(4)
for k in range(12):      # drips hanging off the ledges
    a = rnd.uniform(-2.8, 2.8); ledge = rnd.choice(((1.65, 1.55, 1.7), (1.45, 1.35, 2.7)))
    x, y = math.cos(a) * ledge[0], math.sin(a) * ledge[1]; L = rnd.uniform(0.35, 0.7)
    m.box(f"Drip{k}", (x, y, ledge[2] - L / 2), (0.28, 0.28, L), GOO_L, bot=(0.6, 0.6), studs=False)
for k, (x, y, z, r) in enumerate(((0.9, 1.62, 1.2, 0.34), (-0.8, -1.62, 1.0, 0.4), (-1.2, 1.4, 2.1, 0.28), (0.4, -1.4, 2.25, 0.26),
                                 (-0.9, 0.0, 3.25, 0.22), (1.5, -0.9, 0.7, 0.26), (-1.6, -0.6, 0.6, 0.3))):
    m.box(f"Nucleus{k}", (x, y, z), (r, 0.12 if abs(y) > 1 else r, r), GLOW, studs=False, glow=True)
# grin: crimson mouth across the front, jagged teeth top + bottom, goo strands, dark lips
m.box("Mouth", (1.82, 0, 1.15), (0.2, 2.3, 0.75), MOUTH, studs=False)
m.box("LipTop", (1.86, 0, 1.6), (0.26, 2.5, 0.18), GOO_D, studs=False)
m.box("LipBot", (1.86, 0, 0.72), (0.26, 2.4, 0.16), GOO_D, studs=False)
m.teeth("ToothT", (1.92, -1.0, 1.52), (1.92, 1.0, 1.52), 7, 0.3, 0.1, fangs=(1, 5))
m.teeth("ToothB", (1.92, -0.85, 0.8), (1.92, 0.85, 0.8), 6, 0.24, 0.09, down=False)
m.box("Tongue", (1.75, 0.3, 0.9), (0.3, 0.8, 0.14), TONGUE, studs=False)
for y in (-0.55, 0.6): m.box(f"Strand{y}", (1.9, y, 1.15), (0.05, 0.06, 0.62), GOO_L, studs=False)

UP = V(0, 0, 1)
for k, (base, d) in enumerate(((V(0.2, 0, 3.75), V(0.35, 0, 1)), (V(-0.2, 0.75, 3.4), V(0.25, 0.55, 0.9)), (V(-0.2, -0.75, 3.4), V(0.25, -0.55, 0.9)))):
    d = d.normalized(); L = 1.7 if k == 0 else 1.35
    pts = [base, base + d * L * 0.5 + V(0.15, 0, 0), base + d * L + V(0.3, 0, 0)]
    m.chain(f"Stalk{k}", pts, [0.42, 0.34, 0.3], GOO, bones=[f"Tent{k}_0", f"Tent{k}_1"])
    with m.bone(f"Tent{k}_1"):
        e = pts[-1] + V(0.1, 0, 0.3)
        m.box(f"Eyeball{k}", e, (0.62, 0.62, 0.62), WHITE, studs=False)
        m.box(f"Pupil{k}", e + V(0.31, 0, -0.04), (0.06, 0.3, 0.34), PUPIL, studs=False)
        m.box(f"Lid{k}", e + V(0.04, 0, 0.26), (0.7, 0.7, 0.24), GOO_D, rot=Ry(0.35), studs=False)
for k, s in ((3, 1), (4, -1)):    # goo arms reaching forward-out, three nub fingers
    pts = [V(0.5, s * 1.45, 1.4), V(1.3, s * 2.3, 1.15), V(2.0, s * 2.55, 0.55)]
    m.chain(f"Arm{k}", pts, [0.75, 0.6, 0.46], GOO, bones=[f"Tent{k}_0", f"Tent{k}_1"])
    with m.bone(f"Tent{k}_1"):
        for t in (-1, 0, 1):
            m.box(f"Finger{k}{t}", pts[-1] + V(0.4, t * 0.2, -0.2), (0.45, 0.16, 0.18), GOO_L, rot=Rz(t * 0.4), studs=False)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 25, 15, 45)], glow_color=GLOW)
