"""TFFA FireSalamander (Volcano) - hero build.

Reference analysis (iconic fire salamander - real Salamandra salamandra + mythic fire salamander art):
1. Silhouette: a low, sprawling amphibian with its body bent in an S-curve, head raised and turned slightly, legs
   splayed out to the sides, a long tapering tail curling away.
2. Head: wide, flat, rounded head with a long smiling mouth line, big bulging gold eyes on the top-sides.
3. Signature (the twist): axolotl-style EXTERNAL GILLS made of fire - three flame plumes on each side of the head;
   the classic yellow salamander blotches are glowing lava; a crest of little flames runs down the spine; the tail tip
   burns.
4. Colours: glossy black body, orange-red belly, glowing yellow-orange spots + flame cores (one glow colour),
   red/orange flame layers, gold eyes.
Bones: Body, Head, Leg_FL/FR/BL/BR, Tail1..4. Crawl gait. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector, Matrix

BLK, BLK_L, BELLY, GL = rgb(34, 30, 38), rgb(62, 56, 70), rgb(232, 96, 40), rgb(255, 184, 46)
FL_R, FL_O, EYEC = rgb(214, 52, 22), rgb(250, 138, 30), rgb(255, 210, 70)
V = lambda *a: Vector(a); LR = lambda s: "L" if s > 0 else "R"

def flame(m, name, base, d, L, w, flat=0.55, front=(1, 0, 0)):
    """Three-layer flame tongue, layers FANNED toward `front` so every colour shows: deep red at the back (longest),
    orange in front of it, glowing yellow core in front (shortest)."""
    d = d.normalized(); f = Vector(front); f = (f - d * f.dot(d)); f = f.normalized() if f.length > 1e-3 else Vector((0, 0, 1))
    m.spike(f"{name}R", base, base + d * L, w, FL_R, flat=flat)
    m.spike(f"{name}O", base + f * w * 0.45, base + f * w * 0.3 + d * L * 0.8, w * 0.8, FL_O, flat=flat)
    m.spike(f"{name}Y", base + f * w * 0.85, base + f * w * 0.6 + d * L * 0.55, w * 0.55, GL, flat=flat, glow=True)

def spot(m, name, p, n, r):
    """Glowing lava blotch on a surface with outward normal n (axis-aligned-ish)."""
    sz = (r, r, 0.1) if abs(n.z) > 0.7 else ((r, 0.08, r * 0.8) if abs(n.y) > 0.7 else (0.08, r, r * 0.8))
    m.box(name, p + n * 0.02, sz, GL, glow=True, studs=False)

m = Model("FireSalamander", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.4, chamfer=0.18, jitter=0.05)
m.gait = {"crawl": True}
body = m.bone("Body", (0, 0, 1.0)); body.__enter__()
# S-curved torso: chest -> mid -> hips, each yawed a little
SEGS = [(V(1.55, 0.35, 1.1), 1.9, 1.8, 1.3, 0.4), (V(0.0, 0.75, 1.05), 1.9, 1.9, 1.3, -0.08), (V(-1.5, 0.3, 1.02), 1.8, 1.75, 1.25, -0.45)]
for i, (c, l, w, h, yaw) in enumerate(SEGS):
    m.box(f"Torso{i}", c, (l, w, h), BLK, rot=Rz(yaw), top=(0.86, 0.86), bot=(0.9, 0.9))
    m.box(f"Belly{i}", c + V(0, 0, -h * 0.42), (l * 0.92, w * 0.9, h * 0.22), BELLY, rot=Rz(yaw), studs=False)
    n_up = V(0, 0, 1)
    for j, (dx, dy, r) in enumerate(((0.35, 0.4, 0.42), (-0.4, -0.35, 0.36), (0.0, -0.05, 0.28))):
        q = c + Matrix.Rotation(yaw, 3, "Z") @ V(dx, dy, h / 2)
        spot(m, f"SpotT{i}{j}", q, n_up, r)
    for s in (1, -1):
        q = c + Matrix.Rotation(yaw, 3, "Z") @ V(0.1 * s, s * w / 2, 0.05)
        spot(m, f"SpotS{i}{s}", q, Matrix.Rotation(yaw, 3, "Z") @ V(0, s, 0), 0.4)
for k in range(6):             # dorsal flame crest down the spine
    t = k / 5; c = SEGS[0][0].lerp(SEGS[2][0], t) + V(0, 0, 0.6)
    flame(m, f"Crest{k}", c, V(-0.5, 0, 1.0), 1.5 - 0.12 * abs(k - 2), 0.4)

# sprawled legs: out to the side then down, splayed four-toed hands
LEGS = [("F", 1.5, 0.25, 1.0), ("B", -1.55, 0.2, -1.0)]
for fb, x, yc, fwd in LEGS:
    for s in (1, -1):
        hip = V(x, yc + s * 0.8, 0.95)
        with m.bone(f"Leg_{fb}{LR(s)}", hip):
            knee = hip + V(0.2 * fwd, s * 1.0, 0.25); foot = knee + V(0.25 * fwd, s * 0.25, -0.95)
            m.seg(f"Upper{fb}{s}", hip, knee, 0.62, 0.52, BLK)
            m.seg(f"Lower{fb}{s}", knee, foot, 0.5, 0.42, BLK)
            m.box(f"Hand{fb}{s}", foot + V(0.1 * fwd, 0, 0.1), (0.7, 0.7, 0.24), BLK_L, studs=False)
            for t in (-1.5, -0.5, 0.5, 1.5):
                a = t * 0.38 + (0 if fwd > 0 else math.pi)
                d = V(math.cos(a) * fwd, math.sin(a) * s if fwd > 0 else -math.sin(a) * s * -1, 0)
                m.box(f"Toe{fb}{s}{t}", foot + V(0.1 * fwd, 0, 0.08) + d * 0.48, (0.42, 0.14, 0.12), BLK_L, rot=Rz(math.atan2(d.y, d.x)), studs=False)
            spot(m, f"SpotL{fb}{s}", knee + V(0, 0, 0.27), V(0, 0, 1), 0.26)

# long curling tail
pts = [V(-2.3, 0.05, 0.95), V(-3.4, -0.45, 0.8), V(-4.4, -1.1, 0.62), V(-5.2, -1.15, 0.5), V(-5.8, -0.6, 0.45)]
ws = [1.05, 0.82, 0.6, 0.42, 0.26]
m.chain("Tail", pts, ws, BLK, depths=[0.9, 0.7, 0.52, 0.38, 0.24], bones="Tail")
for i in range(1, 4):
    with m.bone(f"Tail{i}"):
        q = pts[i].lerp(pts[i + 1], 0.45); spot(m, f"SpotTail{i}", q + V(0, 0, ws[i] * 0.4), V(0, 0, 1), ws[i] * 0.5)
        flame(m, f"TailCrest{i}", q + V(0, 0, ws[i] * 0.35), V(-0.4, 0, 1), 1.1 - 0.15 * i, 0.3)
with m.bone("Tail4"):
    flame(m, "TailFire", pts[-1], V(0.3, 0.6, 0.6), 1.7, 0.42, front=(0, 0, 1))

# head: wide flat smiling head, bulging gold eyes, FIRE GILLS
with m.bone("Head", (2.4, 0.25, 1.15)):
    hc = V(3.25, 0.15, 1.35)
    with m.frame(pivot=hc, rot=Rz(-0.15) @ Ry(-0.12)):
        m.box("Head", hc, (2.0, 2.5, 1.15), BLK, top=(0.82, 0.84), bot=(0.92, 0.92))
        m.box("Snout", hc + V(1.1, 0, -0.1), (0.55, 2.05, 0.85), BLK, top=(0.8, 0.84))
        m.box("Chin", hc + V(0.35, 0, -0.5), (1.6, 1.9, 0.2), BELLY, studs=False)
        m.box("Smile", hc + V(1.18, 0, -0.25), (0.06, 1.5, 0.07), rgb(120, 30, 20), studs=False)
        for s in (1, -1):
            m.box(f"SmileSide{s}", hc + V(0.55, s * 1.06, -0.2), (1.2, 0.06, 0.07), rgb(120, 30, 20), rot=Ry(-0.15), studs=False)
            m.box(f"EyeBump{s}", hc + V(0.5, s * 0.85, 0.6), (0.95, 0.85, 0.6), BLK, top=(0.8, 0.8))
            spot(m, f"SpotH{s}", hc + V(-0.25, s * 0.45, 0.47), V(0, 0, 1), 0.34)
            for g, (dz, dy, L) in enumerate(((0.35, 0.25, 1.15), (0.0, 0.45, 1.3), (-0.3, 0.3, 1.0))):   # fire gills
                root = hc + V(-0.7, s * 1.2, dz)
                m.seg(f"GillStalk{s}{g}", root - V(0.0, s * 0.2, 0), root + V(-0.15, s * 0.25, 0.05), 0.24, 0.2, BLK_L, studs=False)
                flame(m, f"Gill{s}{g}", root + V(-0.15, s * 0.22, 0.05), V(-0.55, s * (0.55 + dy), 0.35 + dz * 0.8), L * 1.8, 0.48, front=(0.6, 0, 1))
        m.eyes(tuple(hc + V(0.86, 0.93, 0.7)), facing=(0.55, 0.75, 0.35), size=(0.74, 0.74), pupil=0.62, look=(0.3, 0.05), angry=0.15,
               white=EYEC, brow_col=BLK_L, brow_h=0.25, brow_up=0.65, depth=0.16)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 16, 45), ("front", 0, 10, 45), ("side", 90, 8, 45), ("ref", 30, 25, 45)], glow_color=GL)
