"""TFFA Stegosaurus (DinoLand) - hero build.

Reference analysis (iconic Stegosaurus art, most important first):
1. Silhouette: a high ARCHED back - the hips are the highest body point and the short front legs bring the small
   head low near the ground; two rows of huge alternating diamond plates run along the back (biggest over the hips)
   and are the tallest thing; the tail rises behind and ends in four big spikes (the thagomizer).
2. Head: small, long and low with a beak and a stern side eye (TFFA: still big enough to read).
3. Signature: plates two-tone - red-orange centre with a yellow rim; bony throat studs; darker back stripe.
4. Colours: olive green, pale belly, red-orange plates with yellow rims, cream spikes.
Bones: Body, Neck, Head, Leg_FL/FR/BL/BR, Tail1..3. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

BODY, BODY_D, BELLY, PLATE, RIM, BONE = rgb(116, 156, 70), rgb(74, 104, 44), rgb(224, 214, 156), rgb(228, 90, 50), rgb(252, 196, 72), rgb(242, 234, 212)
V = lambda *a: Vector(a); LR = lambda s: "L" if s > 0 else "R"

def plate(m, name, base, h, w, lean=-0.25):
    """Diamond back plate in the XZ plane: yellow rim behind, red-orange face (thicker, so both sides show the rim)."""
    pts = [(0, -w * 0.3), (h * 0.55, -w * 0.5), (h, 0.0), (h * 0.55, w * 0.5), (0, w * 0.3)]
    ax = V(math.sin(lean), 0, math.cos(lean))
    m.slab(f"{name}Rim", pts, 0.18, RIM, origin=base, xaxis=ax, yaxis=(1, 0, 0) if False else V(math.cos(lean), 0, -math.sin(lean)) * -1)
    inner = [(p[0] * 0.82 + h * 0.05, p[1] * 0.75) for p in pts]
    m.slab(f"{name}", inner, 0.3, PLATE, origin=base, xaxis=ax, yaxis=V(math.cos(lean), 0, -math.sin(lean)) * -1)

m = Model("Stegosaurus", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.55, chamfer=0.15, jitter=0.06)
m.gait = {"amp": 0.8}
body = m.bone("Body", (0, 0, 3.8)); body.__enter__()
m.box("Hips", (-0.6, 0, 4.15), (2.6, 2.7, 2.7), BODY, top=(0.82, 0.85), bot=(0.85, 0.88))
m.box("Chest", (1.4, 0, 3.4), (2.3, 2.5, 2.3), BODY, top=(0.85, 0.85), bot=(0.85, 0.88), rot=Ry(0.25))
m.box("Belly", (0.4, 0, 2.75), (3.6, 2.2, 0.8), BELLY, rot=Ry(0.12), studs=False)
m.box("BackStripe", (-0.3, 0, 5.5), (3.0, 0.7, 0.12), BODY_D, rot=Ry(0.12), studs=False)
for sx, x, top_z, lw in ((1, 1.75, 3.0, 0.95), (-1, -0.75, 3.6, 1.15)):
    for s in (1, -1):
        y = s * 1.15
        with m.bone(f"Leg_{'F' if sx > 0 else 'B'}{LR(s)}", (x, y, top_z)):
            if sx < 0: m.box(f"Thigh{s}", (x, y + s * 0.1, top_z - 0.5), (1.9, 1.0, 2.2), BODY, top=(0.85, 0.9), bot=(0.75, 0.85))
            m.seg(f"Leg{sx}{s}", V(x, y, top_z - (1.0 if sx < 0 else 0.2)), V(x + 0.1, y, 0.5), lw, lw * 0.9, BODY)
            m.box(f"Foot{sx}{s}", (x + 0.2, y, 0.25), (lw * 1.35, lw * 1.15, 0.5), BODY_D, top=(0.85, 0.9))
            for t in (-1, 0, 1): m.box(f"Toe{sx}{s}{t}", (x + 0.2 + lw * 0.7, y + t * lw * 0.32, 0.18), (0.24, 0.24, 0.32), BONE, studs=False)
# two rows of alternating plates, biggest over the hips, following the arch
ROW = [(2.4, 4.05, 1.0), (1.7, 4.6, 1.45), (0.9, 5.1, 1.95), (0.05, 5.45, 2.4), (-0.8, 5.5, 2.45), (-1.65, 5.25, 2.0), (-2.4, 4.85, 1.5)]
for k, (x, z, h) in enumerate(ROW):
    for r, s in enumerate((1, -1)):
        xo = x + (0.35 if (k + r) % 2 else -0.05)
        if (k + r) % 2 == 0 or k in (3, 4):
            plate(m, f"Plate{k}{r}", V(xo, s * 0.32, z - 0.35), h, h * 0.9, lean=-0.1 + 0.05 * (x - 0))
pts = [V(-1.9, 0, 4.6), V(-3.3, 0, 4.7), V(-4.6, 0, 5.0), V(-5.7, 0, 5.45)]
m.chain("Tail", pts, [1.7, 1.25, 0.85, 0.52], BODY, bones="Tail")
for i, (x, z, h) in enumerate(((-3.2, 5.2, 1.0), (-4.4, 5.45, 0.7))):
    with m.bone(f"Tail{i + 1}"):
        for r, s in enumerate((1, -1)): plate(m, f"TailPlate{i}{r}", V(x + 0.25 * r, s * 0.2, z), h, h * 0.9, lean=-0.3)
with m.bone("Tail3"):
    e = pts[-1]
    for k, (dy, dz, dx) in enumerate(((0.9, 0.55, -0.35), (0.75, 0.75, 0.35), (-0.9, 0.55, -0.35), (-0.75, 0.75, 0.35))):
        b = e + V(-0.1 + (0.35 if k % 2 else -0.15), 0.18 * (1 if dy > 0 else -1), 0.1)
        m.spike(f"Thagomizer{k}", b, b + V(dx - 0.4, dy * 1.45, dz * 1.3), 0.17, BONE, sides=5)

with m.bone("Neck", (2.4, 0, 3.4)):
    m.seg("Neck", V(2.2, 0, 3.5), V(3.45, 0, 2.75), 1.25, 1.0, BODY, d0=1.3, d1=1.05)
    for k in range(4): m.box(f"ThroatStud{k}", (2.6 + k * 0.28, 0, 2.55 - k * 0.15), (0.2, 0.75, 0.16), BONE, studs=False)
with m.bone("Head", (3.4, 0, 2.8), "Neck"):
    hc = V(4.05, 0, 2.75)
    m.box("Head", hc, (1.55, 1.25, 1.05), BODY, top=(0.85, 0.88), bot=(0.9, 0.9))
    m.box("Snout", hc + V(0.95, 0, -0.12), (0.6, 0.95, 0.72), BODY, top=(0.85, 0.85))
    m.box("Beak", hc + V(1.32, 0, -0.25), (0.25, 0.75, 0.45), rgb(64, 52, 44), bot=(0.8, 0.8), studs=False)
    m.box("Cheek", hc + V(0.4, 0, -0.42), (1.0, 1.15, 0.28), BELLY, studs=False)
    m.eyes(tuple(hc + V(0.2, 0.63, 0.18)), facing=(0.35, 1, 0), size=(0.5, 0.46), pupil=0.66, look=(0.3, 0), angry=0.25,
           brow_col=BODY_D, brow_h=0.38, brow_up=0.68, depth=0.12)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 60, 10, 45)])
