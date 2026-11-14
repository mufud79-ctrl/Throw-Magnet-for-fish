"""TFFA MoonBunny (Space) - hero build, v2 (v1 was "looks bad": stiff pole ears, washed-out, boxy, no signature).

Reference analysis (iconic moon rabbit / jade rabbit art, most important first):
1. Silhouette: chunky rabbit sitting up on big hind feet, chest out; a BIG round head (TFFA heads are big); broad ears
   - one upright, one flopped forward at the tip; and behind the head a large glowing crescent moon like a halo: the
   signature you read from every angle.
2. Head: big glossy eyes, puffy white cheeks + muzzle, pink nose, buck teeth, little crescent mark on the forehead.
3. Signature: crescent halo; constellation markings (glowing stars + lines) on the flanks; glowing ear linings; a
   glowing full-moon tail.
4. Colours: lavender-blue fur, white muzzle/belly, moon-gold glow (one glow colour), pink nose.
Bones: Body, Head, Ear_L/R, Leg_FL/FR/BL/BR, Tail1. Hop gait. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

FUR, FUR_D, WHT, GLOW = rgb(170, 170, 236), rgb(116, 112, 186), rgb(248, 248, 255), rgb(255, 206, 80)
NOSEP = rgb(255, 140, 175)
V = lambda *a: Vector(a); LR = lambda s: "L" if s > 0 else "R"

m = Model("MoonBunny", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.4, chamfer=0.18, jitter=0.04)
m.gait = {"hop": True}
body = m.bone("Body", (0, 0, 1.5)); body.__enter__()
m.box("Rump", (-0.5, 0, 1.3), (2.4, 2.4, 1.9), FUR, top=(0.78, 0.82), bot=(0.88, 0.9))
m.box("Chest", (0.55, 0, 1.6), (1.6, 2.0, 2.0), FUR, top=(0.82, 0.84), bot=(0.9, 0.9))
m.box("Belly", (1.32, 0, 1.4), (0.24, 1.35, 1.5), WHT, top=(0.8, 0.88))
# constellations on the flanks: stars + joining lines
CON = [(-1.1, 1.75), (-0.6, 1.35), (-0.05, 1.7), (-0.75, 0.85), (0.35, 1.2)]
for s in (1, -1):
    yy = s * 1.21
    for j, (x, z) in enumerate(CON):
        m.box(f"Star{s}{j}", (x, yy + s * 0.02, z), (0.17, 0.06, 0.17), GLOW, rot=Rx(0) @ Ry(0.785), glow=True, studs=False)
    for j, (i, k) in enumerate(((0, 1), (1, 2), (1, 3), (2, 4))):
        (x0, z0), (x1, z1) = CON[i], CON[k]
        m.box(f"ConLine{s}{j}", ((x0 + x1) / 2, yy + s * 0.01, (z0 + z1) / 2), (math.hypot(x1 - x0, z1 - z0), 0.04, 0.05), GLOW,
              rot=Ry(-math.atan2(z1 - z0, x1 - x0)), glow=True, studs=False)
    with m.bone(f"Leg_B{LR(s)}", (-0.55, s * 0.95, 1.1)):
        m.box(f"Thigh{s}", (-0.6, s * 1.12, 0.95), (1.55, 0.6, 1.35), FUR, top=(0.78, 0.84), bot=(0.88, 0.9))
        m.box(f"Foot{s}", (0.0, s * 1.08, 0.17), (1.8, 0.7, 0.34), FUR, top=(0.9, 0.9))
        m.box(f"Toe{s}", (0.86, s * 1.08, 0.14), (0.18, 0.62, 0.24), WHT, studs=False)
    with m.bone(f"Leg_F{LR(s)}", (0.85, s * 0.55, 1.2)):
        m.seg(f"Arm{s}", V(0.9, s * 0.58, 1.35), V(1.15, s * 0.62, 0.2), 0.5, 0.44, FUR)
        m.box(f"Paw{s}", (1.28, s * 0.62, 0.13), (0.56, 0.5, 0.26), WHT, studs=False)
with m.bone("Tail1", (-1.75, 0, 1.3)):
    m.box("Tail", (-1.95, 0, 1.4), (0.85, 0.9, 0.85), GLOW, glow=True, top=(0.8, 0.8), bot=(0.8, 0.8))

piv = V(0.85, 0, 2.55)
with m.bone("Head", piv), m.frame(pivot=piv, scale=1.3):
    hc = V(1.15, 0, 3.05)
    # crescent-moon halo behind the head (vertical, facing forward)
    outer = [(math.cos(a) * 1.25, math.sin(a) * 1.25) for a in [math.radians(d) for d in range(-150, 151, 20)]]
    inner = [(math.cos(a) * 0.95 + 0.42, math.sin(a) * 0.95) for a in [math.radians(d) for d in range(140, -141, -20)]]
    m.slab("Halo", outer + inner, 0.14, GLOW, origin=hc + V(-0.95, 0, 0.55), xaxis=(0, 0, 1), yaxis=(0, 1, 0), glow=True)
    m.box("Head", hc, (1.45, 1.75, 1.4), FUR, top=(0.86, 0.9), bot=(0.88, 0.9))
    for s in (1, -1):
        m.box(f"Cheek{s}", hc + V(0.42, s * 0.52, -0.42), (0.7, 0.66, 0.6), WHT, top=(0.85, 0.9))
    m.box("Snout", hc + V(0.76, 0, -0.32), (0.36, 0.76, 0.46), WHT, top=(0.85, 0.9))
    m.box("Nose", hc + V(0.95, 0, -0.17), (0.08, 0.28, 0.16), NOSEP, bot=(0.9, 0.5), studs=False)
    for s in (1, -1): m.box(f"Tooth{s}", hc + V(0.9, s * 0.075, -0.64), (0.06, 0.13, 0.24), WHT, studs=False)
    m.eyes(tuple(hc + V(0.74, 0.4, 0.14)), size=(0.58, 0.58), pupil=0.62, look=(0.3, 0.05), angry=0.0,
           brow_col=FUR_D, brow_h=0.26, brow_up=0.66, depth=0.13)
    for s in (1, -1):     # catchlight glints make the eyes glossy
        m.box(f"Glint{s}", hc + V(0.82, s * 0.32, 0.27), (0.04, 0.1, 0.1), WHT, studs=False)
    cres = [(math.cos(a) * 0.22, math.sin(a) * 0.22) for a in [0.6 + i * 0.6 for i in range(9)]] + \
           [(math.cos(a) * 0.14 + 0.07, math.sin(a) * 0.14) for a in [5.2 - i * 0.55 for i in range(7)]]
    m.slab("Crescent", cres, 0.06, GLOW, origin=hc + V(0.73, 0, 0.5), xaxis=(0, 1, 0), yaxis=(0, 0, 1), glow=True)
    for s in (1, -1):     # broad ears: left upright, right flopped forward at the tip
        with m.bone(f"Ear_{LR(s)}", hc + V(-0.2, s * 0.45, 0.62)):
            a = hc + V(-0.2, s * 0.45, 0.6); b = hc + V(-0.4, s * 0.72, 1.85)
            tip = b + (V(-0.08, s * 0.12, 0.8) if s > 0 else V(0.6, s * 0.1, 0.25))
            m.seg(f"Ear{s}", a, b, 0.72, 0.68, FUR, d0=0.32, d1=0.3)
            m.seg(f"EarTip{s}", b - (b - a).normalized() * 0.12, tip, 0.68, 0.36, FUR, d0=0.3, d1=0.22)
            fw = V(0.17, 0, 0) if s > 0 else V(0.17, 0, -0.05)
            m.seg(f"EarIn{s}", a + V(0.17, 0, 0.3), b + V(0.16, 0, -0.05), 0.42, 0.4, GLOW, d0=0.05, d1=0.05, glow=True)
            if s > 0: m.seg(f"EarInTip{s}", b + V(0.15, 0, -0.1), tip + V(0.12, 0, -0.25), 0.38, 0.18, GLOW, d0=0.05, d1=0.05, glow=True)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 30, 15, 45)], glow_color=GLOW)
