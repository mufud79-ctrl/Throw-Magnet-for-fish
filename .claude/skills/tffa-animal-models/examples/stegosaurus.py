"""TFFA Stegosaurus (DinoLand) - hero build v2 in the user-approved Ankylosaurus proportions (v1, tall pillar legs and
a tiny head, was rejected: chunky, wide, short thick legs and a big head are what was approved).

Reference analysis (iconic Stegosaurus):
1. Silhouette: a chunky, wide body with the hips higher than the shoulders (arched back), short thick legs, a big head
   held low; two rows of huge, THICK alternating plates (biggest over the hips) are the tallest thing; the tail rises to
   four big spikes.
2. Head: big (TFFA) with a dark beak and angry side eyes under heavy brows.
3. Signature: plates two-tone (red-orange face, gold rim); throat studs; a darker back stripe; spikes cream.
4. Colours: olive green, darker underside, cream belly, red-orange + gold plates, cream spikes.
Bones: Body, Neck, Head, Leg_FL/FR/BL/BR, Tail1..3. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

BODY, BODY_D, BELLY, PLATE, RIM, BONE = rgb(118, 156, 66), rgb(76, 104, 42), rgb(224, 214, 156), rgb(230, 88, 46), rgb(252, 196, 72), rgb(242, 234, 212)
V = lambda *a: Vector(a); LR = lambda s: "L" if s > 0 else "R"

def plate(m, name, base, h, w, lean=0.0):
    """Thick diamond plate in the XZ plane: gold rim slab behind, thicker red-orange face slab (rim shows on both sides)."""
    pts = [(0, -w * 0.32), (h * 0.55, -w * 0.5), (h, 0.0), (h * 0.55, w * 0.5), (0, w * 0.32)]
    ax = V(math.sin(lean), 0, math.cos(lean)); ay = V(-math.cos(lean), 0, math.sin(lean))
    m.slab(f"{name}Rim", pts, 0.34, RIM, origin=base, xaxis=ax, yaxis=ay)
    m.slab(f"{name}", [(p[0] * 0.8 + h * 0.06, p[1] * 0.72) for p in pts], 0.5, PLATE, origin=base, xaxis=ax, yaxis=ay)

m = Model("Stegosaurus", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.5, chamfer=0.16, jitter=0.06)
m.gait = {"amp": 0.8}
body = m.bone("Body", (0, 0, 2.9)); body.__enter__()
m.box("Hips", (-0.8, 0, 3.2), (3.0, 3.7, 2.9), BODY, top=(0.8, 0.84), bot=(0.88, 0.9))
m.box("Chest", (1.3, 0, 2.7), (2.6, 3.4, 2.4), BODY, top=(0.84, 0.86), bot=(0.88, 0.9), rot=Ry(0.15))
m.box("Belly", (0.3, 0, 1.6), (3.8, 3.0, 0.5), BELLY, studs=False)
m.box("BackStripe", (-0.4, 0, 4.66), (2.8, 0.9, 0.12), BODY_D, rot=Ry(0.15), studs=False)
for sx, x, top_z, lw in ((1, 1.6, 2.3, 1.25), (-1, -1.0, 2.7, 1.45)):
    for s in (1, -1):
        y = s * 1.45
        with m.bone(f"Leg_{'F' if sx > 0 else 'B'}{LR(s)}", (x, y, top_z)):
            m.box(f"Leg{sx}{s}", (x, y, top_z / 2 + 0.1), (lw, lw * 0.95, top_z + 0.2), BODY, top=(1.0, 1.0), bot=(0.9, 0.9))
            m.box(f"Foot{sx}{s}", (x + 0.12, y, 0.2), (lw * 1.2, lw * 1.1, 0.4), BODY_D, studs=False)
            for t in (-1, 0, 1): m.box(f"Toe{sx}{s}{t}", (x + 0.12 + lw * 0.6, y + t * lw * 0.32, 0.16), (0.26, 0.26, 0.3), BONE, studs=False)
ROW = [(2.2, 3.85, 1.25), (1.45, 4.25, 1.75), (0.65, 4.6, 2.3), (-0.2, 4.75, 2.7), (-1.05, 4.7, 2.65), (-1.9, 4.45, 2.15), (-2.6, 4.1, 1.6)]
for k, (x, z, h) in enumerate(ROW):
    for r, s in enumerate((1, -1)):
        plate(m, f"Plate{k}{r}", V(x + (0.4 if (k + r) % 2 else 0.0), s * 0.42, z - 0.4), h, h * 0.95, lean=-0.12)
pts = [V(-2.3, 0, 3.6), V(-3.8, 0, 3.75), V(-5.1, 0, 4.1), V(-6.1, 0, 4.6)]
m.chain("Tail", pts, [2.2, 1.6, 1.1, 0.7], BODY, bones="Tail")
for i, (x, z, h) in enumerate(((-3.7, 4.4, 1.25), (-4.95, 4.6, 0.9))):
    with m.bone(f"Tail{i + 1}"):
        for r, s in enumerate((1, -1)): plate(m, f"TailPlate{i}{r}", V(x + 0.3 * r, s * 0.25, z), h, h * 0.95, lean=-0.3)
with m.bone("Tail3"):
    e = pts[-1]
    for k, (dy, dz, dx) in enumerate(((1.0, 0.6, -0.4), (0.85, 0.85, 0.35), (-1.0, 0.6, -0.4), (-0.85, 0.85, 0.35))):
        b = e + V(-0.1 + (0.4 if k % 2 else -0.2), 0.22 * (1 if dy > 0 else -1), 0.1)
        m.spike(f"Thagomizer{k}", b, b + V(dx - 0.45, dy * 1.8, dz * 1.6), 0.26, BONE, sides=5)
with m.bone("Neck", (2.4, 0, 2.8)):
    m.seg("Neck", V(2.2, 0, 2.95), V(3.3, 0, 2.35), 1.8, 1.55, BODY, d0=1.8, d1=1.55)
    for k in range(4): m.box(f"ThroatStud{k}", (2.55 + k * 0.3, 0, 1.95 - k * 0.1), (0.24, 1.0, 0.18), BONE, studs=False)
with m.bone("Head", (3.3, 0, 2.4), "Neck"), m.frame(pivot=(3.3, 0, 2.4), scale=1.35):
    hc = V(3.95, 0, 2.4)
    m.box("Head", hc, (1.6, 1.45, 1.2), BODY, top=(0.84, 0.86), bot=(0.9, 0.9))
    m.box("Snout", hc + V(0.95, 0, -0.12), (0.62, 1.1, 0.82), BODY, top=(0.85, 0.85))
    m.box("Beak", hc + V(1.34, 0, -0.26), (0.26, 0.85, 0.5), rgb(60, 50, 42), bot=(0.8, 0.8), studs=False)
    m.box("Cheek", hc + V(0.4, 0, -0.5), (1.1, 1.32, 0.3), BELLY, studs=False)
    for s in (1, -1): m.box(f"BrowPlate{s}", hc + V(0.3, s * 0.6, 0.62), (0.7, 0.42, 0.26), RIM, studs=False)
    m.eyes(tuple(hc + V(0.25, 0.73, 0.2)), facing=(0.35, 1, 0), size=(0.56, 0.5), pupil=0.68, look=(0.35, 0), angry=0.4,
           brow_col=BODY_D, brow_h=0.42, brow_up=0.7, depth=0.13)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 14, 45), ("front", 0, 10, 45), ("side", 90, 6, 45), ("ref", 35, 22, 45)])
