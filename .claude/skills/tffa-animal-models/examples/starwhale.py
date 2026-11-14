"""TFFA StarWhale (Space) - hero build.

Reference analysis (iconic "cosmic whale" art, most important first):
1. Silhouette: a huge humpback-style whale gliding through space - big blunt head, deep chest, long tapering body
   rising slightly to the tail, giant flukes, and very long wing-like pectoral fins swept out and down. It floats.
2. Head: knobbly tubercles on top, a long curving mouth line, small calm wise eyes, pale grooved throat.
3. Signature: the back is a night sky - glowing stars joined into constellation lines; glowing fin edges; fluke tips
   glow like a nebula trail.
4. Colours: deep indigo-blue back, lavender belly with darker grooves, pale gold starlight (one glow colour).
Bones: Body, Head, Fin_L/R, Tail1..3. Crawl gait (swim wiggle). Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

BACK, BACK_D, BELLY, GROOVE, STAR = rgb(46, 52, 128), rgb(30, 34, 90), rgb(160, 148, 226), rgb(118, 104, 190), rgb(255, 238, 170)
V = lambda *a: Vector(a); LR = lambda s: "L" if s > 0 else "R"
Z = 3.4        # float height of the body axis

m = Model("StarWhale", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.6, chamfer=0.16, jitter=0.05)
m.gait = {"crawl": True}
body = m.bone("Body", (0, 0, Z)); body.__enter__()
# body: tapered blocks along the axis (narrowing smoothly toward the tail) + a lighter belly keel underneath
m.seg("Chest", V(3.2, 0, Z), V(-0.2, 0, Z + 0.1), 3.9, 3.6, BACK, d0=3.5, d1=3.3)
m.seg("Mid", V(0.2, 0, Z + 0.1), V(-2.9, 0, Z + 0.25), 3.6, 2.9, BACK, d0=3.3, d1=2.7)
m.seg("BellyF", V(3.4, 0, Z - 1.2), V(-0.2, 0, Z - 1.05), 3.3, 3.0, BELLY, d0=1.3, d1=1.2)
m.seg("BellyM", V(0.0, 0, Z - 1.05), V(-2.8, 0, Z - 0.75), 3.0, 2.2, BELLY, d0=1.2, d1=1.0)
for k in range(5):
    m.box(f"Groove{k}", (1.4, (k - 2) * 0.5, Z - 1.86), (3.6, 0.12, 0.08), GROOVE, studs=False)
m.box("Dorsal", (-2.0, 0, Z + 1.55), (1.2, 0.35, 0.8), BACK_D, top=(0.4, 1.0), shift=(-0.4, 0))

with m.bone("Head", (2.8, 0, Z)):
    # humpback head: a wedge sloping from the high crown down to a low, wide, blunt snout; big pale lower jaw + throat
    m.hexa("Head", [V(2.6, -1.95, Z - 1.3), V(6.1, -1.35, Z - 1.0), V(6.1, 1.35, Z - 1.0), V(2.6, 1.95, Z - 1.3),
                    V(2.6, -1.7, Z + 1.7), V(6.3, -1.05, Z + 0.15), V(6.3, 1.05, Z + 0.15), V(2.6, 1.7, Z + 1.7)], BACK)
    m.hexa("Jaw", [V(2.4, -1.85, Z - 2.0), V(5.9, -1.25, Z - 1.6), V(5.9, 1.25, Z - 1.6), V(2.4, 1.85, Z - 2.0),
                   V(2.4, -1.95, Z - 0.95), V(6.25, -1.4, Z - 0.75), V(6.25, 1.4, Z - 0.75), V(2.4, 1.95, Z - 0.95)], BELLY)
    for k in range(5):
        m.box(f"ThroatGroove{k}", (4.2, (k - 2) * 0.5, Z - 1.92), (3.2, 0.12, 0.08), GROOVE, studs=False, rot=Ry(-0.11))
    for s in (1, -1):    # long curving mouth line along the jaw seam, curling up at the back
        m.box(f"MouthLine{s}", (4.4, s * 1.74, Z - 0.9), (3.6, 0.1, 0.12), BACK_D, rot=Rz(s * -0.17), studs=False)
        m.box(f"MouthEnd{s}", (2.55, s * 1.98, Z - 0.6), (0.5, 0.1, 0.12), BACK_D, rot=Ry(-0.7), studs=False)
    for k, (x, y) in enumerate(((5.6, 0.45), (5.6, -0.45), (5.0, 0.8), (5.0, -0.8), (5.3, 0.0), (4.4, 0.45), (4.4, -0.45), (3.8, 0.0))):
        zt = Z + 1.7 - (x - 2.6) / 3.7 * 1.55     # sit on the sloping crown
        m.box(f"Knob{k}", (x, y, zt + 0.06), (0.34, 0.34, 0.24), BACK_D, studs=False)
    m.eyes((3.5, 1.79, Z - 0.35), facing=(0.2, 1, 0), size=(0.58, 0.5), pupil=0.72, look=(0.3, 0), angry=-0.05,
           brow_col=BACK_D, brow_h=0.25, brow_up=0.62, depth=0.12)

for s in (1, -1):      # long wing-like pectoral fins, swept back and down, glowing leading edge + star dots
    with m.bone(f"Fin_{LR(s)}", (2.0, s * 1.8, Z - 0.8)):
        o = V(2.0, s * 1.85, Z - 0.9); xa = V(-0.4, s * 0.85, -0.35).normalized(); ya = V(1, 0, 0)
        pts = [(0, -0.9), (1.6, -1.05), (3.4, -0.85), (4.6, -0.4), (5.0, 0.15), (3.8, 0.75), (1.9, 1.05), (0, 1.1)]
        m.slab(f"Fin{s}", pts, 0.42, BACK, origin=o, xaxis=xa, yaxis=ya)
        for j, (x0, y0, x1, y1) in enumerate(((0.3, 1.12, 1.9, 1.08), (1.9, 1.08, 3.8, 0.78), (3.8, 0.78, 4.95, 0.2))):   # glowing leading edge: short bars
            q0 = o + xa * x0 + ya * y0; q1 = o + xa * x1 + ya * y1
            m.seg(f"FinEdge{s}{j}", q0, q1, 0.16, 0.14, STAR, glow=True, studs=False)
        for j, t in enumerate((1.4, 2.6, 3.7)):
            q = o + xa * t + V(0, 0, 0.18) + ya * 0.0
            m.box(f"FinStar{s}{j}", q, (0.16, 0.16, 0.1), STAR, studs=False, glow=True)

pts = [V(-2.7, 0, Z + 0.15), V(-4.3, 0, Z + 0.7), V(-5.7, 0, Z + 1.5), V(-6.8, 0, Z + 2.3)]       # body arcs up into the tail
m.chain("Tail", pts, [2.8, 2.1, 1.45, 0.9], BACK, depths=[2.6, 2.0, 1.35, 0.85], bones="Tail")
with m.bone("Tail3"):
    for s in (1, -1):
        o = V(-6.6, 0, Z + 2.3)
        fl = [(0, 0), (0.8, 1.3 * s), (0.4, 3.2 * s), (-0.8, 3.9 * s), (-1.2, 3.4 * s), (-0.8, 2.1 * s), (-1.3, 0.3 * s)]
        m.slab(f"Fluke{s}", [(p[0], p[1]) for p in fl] if s > 0 else [(p[0], p[1]) for p in reversed(fl)], 0.3, BACK,
               origin=o, xaxis=(1, 0, 0.05), yaxis=(0, 1, 0))
        m.box(f"FlukeGlow{s}", (-7.6, s * 3.55, Z + 2.4), (0.6, 0.8, 0.34), STAR, rot=Rz(s * 0.4), studs=False, glow=True)

# constellations: stars on the back joined by thin glowing lines
STARS = [(3.3, 0.6), (2.2, -0.4), (1.0, 0.7), (0.0, -0.2), (-1.0, 0.6), (-2.2, -0.5), (-3.3, 0.3), (-4.5, -0.2), (1.8, 1.2), (-0.6, -1.0)]
SZ = lambda x: (Z + 1.7 - (x - 2.6) / 3.7 * 1.55 if x > 2.6 else Z + 1.78 - (2.6 - x) * 0.03) if x > -2.7 else Z + 1.45 + (-2.7 - x) * 0.25
def bone_for(x): return "Head" if x > 2.8 else ("Body" if x > -2.7 else ("Tail1" if x > -4.4 else "Tail2"))
for k, (x, y) in enumerate(STARS):
    with m.bone(bone_for(x)):
        m.box(f"Star{k}", (x, y, SZ(x) + 0.05), (0.3, 0.3, 0.14), STAR, studs=False, glow=True)
for k, (i, j) in enumerate(((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (2, 8), (3, 9))):
    (x0, y0), (x1, y1) = STARS[i], STARS[j]; mx, my = (x0 + x1) / 2, (y0 + y1) / 2; L = math.hypot(x1 - x0, y1 - y0)
    with m.bone(bone_for(mx)):
        m.box(f"Line{k}", (mx, my, SZ(mx) + 0.02), (L, 0.07, 0.06), STAR, rot=Rz(math.atan2(y1 - y0, x1 - x0)), studs=False, glow=True)
for s in (1, -1):
    for j, (x, z) in enumerate(((0.6, Z + 0.6), (-1.0, Z + 0.9), (2.0, Z + 0.3), (-2.0, Z - 0.2))):
        m.box(f"SideStar{s}{j}", (x, s * (1.73 if x > -0.2 else 1.48), z), (0.2, 0.08, 0.2), STAR, studs=False, glow=True)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 55, 20, 45)], glow_color=STAR)
