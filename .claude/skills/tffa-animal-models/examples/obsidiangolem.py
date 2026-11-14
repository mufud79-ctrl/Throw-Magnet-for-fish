"""TFFA ObsidianGolem (Volcano) - hero build.

Reference analysis (iconic rock / crystal golem art, most important first):
1. Silhouette: a hulking knuckle-walker - enormous boulder shoulders as the highest point, a small head sunk low
   between them, a massive chest tapering to short thick legs, gigantic arms ending in huge fists planted on the ground.
2. Head: a small faceted helm of rock with a heavy brow and glowing slit eyes, a crown of crystal shards.
3. Signature (the twist): a caged CRYSTAL HEART glowing purple through obsidian ribs in the chest; crystal clusters
   erupting from the shoulders and back with glowing tips; rings of floating rocks orbiting the forearms; glowing
   rune-cracks across the body.
4. Colours: glossy black-violet obsidian with lighter facet highlights, violet crystal, purple glow (one glow colour).
Bones: Body, Head, Leg_FL/FR (arms, knuckle-walk like the gorilla), Leg_BL/BR. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

OBS, OBS_L, OBS_D, CRY, GL = rgb(44, 36, 58), rgb(80, 68, 108), rgb(26, 20, 34), rgb(120, 70, 190), rgb(206, 100, 255)
V = lambda *a: Vector(a); LR = lambda s: "L" if s > 0 else "R"

def crystal(m, name, base, d, L, r):
    d = d.normalized(); tip = base + d * L
    m.spike(f"{name}", base, tip, r, CRY, sides=5)
    m.spike(f"{name}G", base.lerp(tip, 0.55), tip + d * 0.04, r * 0.45, GL, sides=5, glow=True)

m = Model("ObsidianGolem", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.55, chamfer=0.14, jitter=0.07)
m.gait = {"amp": 0.7}
body = m.bone("Body", (0, 0, 4.0)); body.__enter__()
m.box("Chest", (0.55, 0, 5.3), (2.9, 4.4, 3.1), OBS, rot=Ry(-0.28), top=(0.82, 0.8), bot=(0.8, 0.82))
m.box("Abdomen", (-0.55, 0, 3.75), (2.1, 3.1, 1.9), OBS, top=(0.95, 0.95), bot=(0.85, 0.9))
m.box("Hips", (-0.9, 0, 2.95), (1.9, 3.1, 1.2), OBS_D, top=(1.0, 1.0))
m.box("Facet", (1.5, 0, 6.3), (1.2, 3.2, 0.9), OBS_L, rot=Ry(-0.6), top=(0.7, 0.8))
# caged crystal heart in the chest
m.box("HeartCavity", (1.92, 0, 5.05), (0.3, 1.5, 1.5), OBS_D, studs=False)
m.box("Heart", (2.0, 0, 5.05), (0.55, 1.0, 1.1), GL, rot=Rx(0.785), glow=True, studs=False)
for k, y in enumerate((-0.45, 0.0, 0.45)):
    m.box(f"CageBar{k}", (2.22, y, 5.05), (0.18, 0.16, 1.7), OBS, studs=False)
m.box("CageTop", (2.18, 0, 5.85), (0.25, 1.6, 0.2), OBS, studs=False)
m.box("CageBot", (2.18, 0, 4.25), (0.25, 1.6, 0.2), OBS, studs=False)
for s in (1, -1):    # rune cracks
    for j, (x, z, l, a) in enumerate(((0.3, 5.9, 1.2, 0.5), (0.6, 4.6, 1.0, -0.6), (-0.6, 3.7, 0.9, 0.3))):
        m.box(f"Rune{s}{j}", (x, s * (2.15 if z > 4.2 else 1.58), z), (l, 0.08, 0.14), GL, rot=Ry(a), glow=True, studs=False)
# boulder shoulders with crystal clusters, back crystals
for s in (1, -1):
    m.box(f"Shoulder{s}", (0.8, s * 2.45, 6.35), (2.3, 1.8, 1.9), OBS, top=(0.75, 0.75), rot=Rx(s * 0.15))
    m.box(f"ShoulderFacet{s}", (1.4, s * 2.6, 6.9), (1.0, 1.2, 0.8), OBS_L, rot=Ry(-0.5), top=(0.6, 0.7))
    for j, (d, L, r) in enumerate(((V(-0.2, s * 0.4, 1.0), 1.7, 0.36), (V(-0.6, s * 0.8, 0.7), 1.3, 0.28), (V(0.3, s * 0.6, 0.8), 1.1, 0.24))):
        crystal(m, f"ShoulderCrystal{s}{j}", V(0.6 + 0.3 * j * 0, s * (2.5 + 0.2 * j), 7.15), d, L, r)
for j, (x, y, d, L) in enumerate(((-0.4, 0.5, V(-0.6, 0.3, 1), 1.4), (-0.6, -0.6, V(-0.7, -0.4, 0.9), 1.2), (-0.9, 0.0, V(-0.9, 0, 0.7), 1.0))):
    crystal(m, f"BackCrystal{j}", V(x, y, 6.2), d, L, 0.3)

# arms: huge, planted fists (knuckle-walk), floating rock rings round the forearms
for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (0.9, s * 2.6, 6.0)):
        sh, el, wr = V(0.9, s * 2.75, 6.0), V(1.6, s * 3.05, 3.7), V(2.2, s * 3.0, 1.55)
        m.seg(f"UpperArm{s}", sh, el, 1.45, 1.25, OBS)
        m.seg(f"Forearm{s}", el, wr, 1.55, 1.9, OBS, d0=1.5, d1=1.85)
        m.box(f"Fist{s}", (2.4, s * 3.0, 0.82), (1.9, 1.8, 1.64), OBS, top=(0.9, 0.9))
        m.box(f"Knuckles{s}", (3.32, s * 3.0, 0.95), (0.3, 1.6, 0.9), OBS_L, studs=False)
        for t in (-1, 0, 1): crystal(m, f"Knuckle{s}{t}", V(3.0, s * 3.0 + t * 0.5, 1.65), V(0.3, 0, 1), 0.55, 0.14)
        m.box(f"ArmRune{s}", (1.9, s * 3.82, 2.7), (1.2, 0.08, 0.14), GL, rot=Ry(1.2), glow=True, studs=False)
        mid = el.lerp(wr, 0.5); ax = (wr - el).normalized(); u = ax.cross(V(0, 1, 0)).normalized(); w = ax.cross(u)
        for k in range(7):
            a = 2 * math.pi * k / 7; p = mid + (u * math.cos(a) + w * math.sin(a)) * 1.55
            m.box(f"Orbit{s}{k}", p, (0.34, 0.3, 0.3), OBS_L if k % 2 else OBS, rot=Rz(a) @ Rx(a * 0.7), studs=False)
        for k in range(14):
            a = 2 * math.pi * k / 14; p = mid + (u * math.cos(a) + w * math.sin(a)) * 1.55
            m.box(f"OrbitGlow{s}{k}", p, (0.08, 0.08, 0.08), GL, glow=True, studs=False) if k % 2 else None
    with m.bone(f"Leg_B{LR(s)}", (-0.9, s * 1.25, 2.8)):
        m.seg(f"Thigh{s}", V(-0.9, s * 1.3, 2.9), V(-0.7, s * 1.4, 0.95), 1.45, 1.3, OBS)
        m.box(f"Foot{s}", (-0.4, s * 1.4, 0.38), (1.9, 1.45, 0.76), OBS, top=(0.88, 0.9))
        m.box(f"FootFacet{s}", (0.35, s * 1.4, 0.55), (0.4, 1.3, 0.5), OBS_L, studs=False)

# small head sunk low between the shoulders, crystal crown
with m.bone("Head", (1.4, 0, 6.3)):
    hc = V(2.05, 0, 6.35)
    m.box("Head", hc, (1.35, 1.5, 1.2), OBS, top=(0.8, 0.85))
    m.box("Brow", hc + V(0.5, 0, 0.32), (0.45, 1.55, 0.35), OBS_L, top=(0.7, 0.9))
    m.box("Jaw", hc + V(0.3, 0, -0.5), (1.0, 1.3, 0.35), OBS_D)
    for s in (1, -1):
        m.box(f"EyeSlit{s}", hc + V(0.69, s * 0.33, 0.05), (0.06, 0.42, 0.14), GL, rot=Rx(s * 0.3), glow=True, studs=False)
    for j, (y, L) in enumerate(((0.0, 0.9), (0.42, 0.65), (-0.42, 0.65))):
        crystal(m, f"Crown{j}", hc + V(-0.1, y, 0.55), V(-0.2, y * 0.6, 1), L, 0.16)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 25, 10, 45)], glow_color=GL)
