"""TFFA Chimera (Mythic Isles) - custom build from the user's reference painting (stalking chimera):
low stalking crouch with the shoulders as the highest point, head hung below the shoulder line, swept-back blond mane
cape, snarling lion face with glowing orange eyes, pale goat head stacked above-left of the lion head with HUGE ringed
C-curved horns (near-black base -> blood-red tips), thick olive snake tail curling round the right flank to the front with
its fanged mouth open, big paws with long dark claws, reddish lower forelegs, shoulder scars. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

FUR, FUR_D, MANE, MANE_D = rgb(176, 124, 72), rgb(142, 96, 56), rgb(218, 174, 112), rgb(180, 132, 78)
FACE, MUZ, LOWLEG, DCLAW = rgb(186, 118, 74), rgb(226, 190, 140), rgb(150, 78, 50), rgb(44, 34, 32)
GOAT, HORN, HORN_R, SCAR = rgb(234, 224, 204), rgb(50, 40, 36), rgb(180, 56, 38), rgb(120, 70, 50)
SNAKE, SNAKE_B, SNAKE_D, EYE = rgb(80, 100, 50), rgb(176, 180, 112), rgb(48, 62, 32), rgb(255, 140, 30)
V = lambda *a: Vector(a)
LR = lambda s: "L" if s > 0 else "R"

m = Model("Chimera", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.5, chamfer=0.16, jitter=0.06)
m.gait = {"amp": 0.8}
body = m.bone("Body", (0, 0, 3.6)); body.__enter__()

# ---------------------------------------------------------------- body: shoulders highest, back slopes down to the hips
m.box("Chest", (1.4, 0, 3.75), (2.9, 3.3, 3.1), FUR, top=(0.8, 0.86), bot=(0.78, 0.86))
m.box("Waist", (-0.7, 0, 3.55), (2.3, 2.7, 2.2), FUR, top=(0.92, 0.92), bot=(0.86, 0.9))
m.box("Hips", (-2.3, 0, 3.3), (1.9, 2.75, 2.2), FUR, top=(0.82, 0.86), bot=(0.85, 0.88))
m.box("Back", (-0.9, 0, 4.6), (3.6, 1.6, 0.5), FUR_D, top=(0.7, 0.8))
for s in (1, -1):
    m.box(f"Haunch{s}", (-2.3, s * 1.3, 3.15), (1.6, 0.4, 1.7), FUR, top=(0.8, 0.8), bot=(0.7, 0.8))
    for j, (x, z, w, a) in enumerate(((0.9, 3.7, 0.9, 0.5), (0.5, 3.2, 0.7, -0.4), (-0.6, 3.9, 0.6, 0.3))):
        m.box(f"Scar{s}{j}", (x, s * 1.42, z), (w, 0.08, 0.1), SCAR, rot=Ry(a), studs=False)
# mane cape: thick fur over the shoulders, swept back, shaggy fringes hanging off the sides
m.box("Mantle", (1.5, 0, 5.15), (2.8, 3.5, 1.3), MANE, top=(0.68, 0.78))
m.box("MantleBack", (0.0, 0, 4.85), (1.8, 2.6, 0.9), MANE_D, top=(0.6, 0.75))
for k in range(9):
    x = 2.3 - k * 0.42; y = (k % 3 - 1) * 0.75; z = 5.55 - k * 0.12
    m.spike(f"Shag{k}", (x, y, z), (x - 1.25, y * 1.15, z + 0.55 - k * 0.05), 0.42, MANE if k % 2 else MANE_D, flat=0.55)
for s in (1, -1):
    m.box(f"Fringe{s}", (1.55, s * 1.75, 4.15), (2.4, 0.5, 2.0), MANE, top=(0.9, 0.9), bot=(0.75, 0.8))
    for j in range(4):
        x = 2.4 - j * 0.6
        m.spike(f"FringeTuft{s}{j}", (x, s * 1.8, 3.4), (x - 0.5, s * 2.0, 2.55), 0.3, MANE_D if j % 2 else MANE, flat=0.5)

# ---------------------------------------------------------------- legs: front reaching forward + wide, hind coiled
for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (2.0, s * 1.3, 3.6)):
        m.box(f"Shoulder{s}", (2.1, s * 1.45, 3.5), (1.6, 0.7, 1.9), FUR, top=(0.8, 0.8), bot=(0.75, 0.85))
        m.seg(f"Forearm{s}", V(2.2, s * 1.4, 3.0), V(3.0, s * 1.75, 1.2), 1.15, 0.95, FUR)
        m.seg(f"Lower{s}", V(2.95, s * 1.75, 1.45), V(3.2, s * 1.85, 0.45), 0.95, 0.85, LOWLEG)
        m.box(f"Paw{s}", (3.4, s * 1.85, 0.32), (1.45, 1.2, 0.64), LOWLEG, top=(0.85, 0.9))
        for t in (-1.5, -0.5, 0.5, 1.5):
            b = V(4.0, s * 1.85 + t * 0.28, 0.32)
            m.spike(f"Claw{s}{t}", b, b + V(0.55, t * 0.05, -0.3), 0.11, DCLAW, flat=0.4)
    with m.bone(f"Leg_B{LR(s)}", (-2.2, s * 1.2, 3.4)):
        m.box(f"Thigh{s}", (-2.25, s * 1.25, 2.55), (1.8, 0.95, 2.1), FUR, rot=Ry(0.4), top=(0.85, 0.9), bot=(0.7, 0.8))
        m.seg(f"Shin{s}", V(-2.85, s * 1.25, 1.85), V(-2.15, s * 1.3, 0.45), 0.8, 0.72, FUR_D)
        m.box(f"HindPaw{s}", (-1.95, s * 1.3, 0.28), (1.25, 1.0, 0.56), FUR_D, top=(0.85, 0.9))
        for t in (-1, 0, 1):
            b = V(-1.38, s * 1.3 + t * 0.3, 0.28)
            m.spike(f"HClaw{s}{t}", b, b + V(0.4, 0, -0.22), 0.09, DCLAW, flat=0.4)

# ---------------------------------------------------------------- neck + lion head hung low and forward, snarling
with m.bone("Neck", (2.6, 0, 4.3)):
    m.seg("Neck", V(2.2, 0, 4.4), V(3.2, 0, 3.7), 2.0, 1.8, FUR, d0=2.2, d1=1.9)
    # goat: neck out of the mane above-left of the lion head, pale head, slit-pupil eyes, huge ringed C-curved horns
    m.seg("GoatNeck", V(2.2, 0, 4.85), V(3.35, 0, 5.45), 1.3, 1.1, GOAT, d0=1.35, d1=1.15)
    g = V(3.45, 0, 5.95)
    gf = m.frame(pivot=g, scale=1.5, move=(0.45, 0, -0.25)); gf.__enter__()   # goat head ~60% of the lion head, centred above it (user)
    m.box("GoatHead", g, (1.15, 0.9, 0.9), GOAT, top=(0.85, 0.9))
    m.box("GoatSnout", g + V(0.72, 0, -0.18), (0.6, 0.62, 0.55), GOAT, top=(0.8, 0.85), bot=(0.9, 0.9))
    m.box("GoatNose", g + V(1.03, 0, -0.08), (0.06, 0.36, 0.14), dk(GOAT, 0.45), studs=False)
    m.box("GoatBeard", g + V(0.55, 0, -0.68), (0.28, 0.3, 0.5), dk(GOAT, 0.8), top=(0.4, 0.5), rot=Ry(0.2), studs=False)
    for s in (1, -1):
        m.box(f"GoatEar{s}", g + V(-0.2, s * 0.62, 0.12), (0.26, 0.55, 0.14), GOAT, rot=Rx(s * 0.35), studs=False)
        m.box(f"GoatEye{s}", g + V(0.3, s * 0.46, 0.12), (0.32, 0.06, 0.2), rgb(255, 200, 40), studs=False, glow=True)
        m.box(f"GoatPupil{s}", g + V(0.3, s * 0.49, 0.12), (0.2, 0.04, 0.07), PUPIL, studs=False)
        m.box(f"GoatBrow{s}", g + V(0.3, s * 0.46, 0.28), (0.4, 0.08, 0.09), dk(GOAT, 0.5), rot=Ry(0.3), studs=False)
        a0 = g + V(0.05, s * 0.24, 0.42)
        o = 0.85                                         # C-curve: both horns sweep out symmetrically
        pts = [a0, a0 + V(-0.3, s * 0.45 * o, 0.7), a0 + V(-0.5, s * 1.0 * o, 1.5), a0 + V(-0.4, s * 1.35 * o, 2.3), a0 + V(-0.05, s * 1.45 * o, 2.95)]
        ws = [0.44, 0.38, 0.31, 0.24, 0.16]
        cols = [HORN, HORN, HORN, HORN_R]
        for i in range(4):
            m.seg(f"Horn{s}{i}", pts[i], pts[i + 1] + (pts[i + 1] - pts[i]).normalized() * 0.08, ws[i], ws[i + 1], cols[i], studs=False)
            r = pts[i].lerp(pts[i + 1], 0.5); d = (pts[i + 1] - pts[i]).normalized()
            m.seg(f"HornRing{s}{i}", r - d * 0.06, r + d * 0.06, (ws[i] + ws[i + 1]) / 2 + 0.08, (ws[i] + ws[i + 1]) / 2 + 0.08,
                  dk(cols[i], 0.7), studs=False)
        m.seg(f"HornRed{s}", pts[2].lerp(pts[3], 0.55), pts[3], ws[2] * 0.85 + 0.02, ws[3] + 0.02, HORN_R, studs=False)
        m.spike(f"HornTip{s}", pts[4], pts[4] + V(0.4, -s * 0.12 * o, 0.6), ws[4] / 2, HORN_R, sides=5)
    gf.__exit__(None, None, None)

with m.bone("Head", (3.1, 0, 3.8), "Neck"):
    hc = V(3.9, 0, 3.25)
    m.box("Ruff", hc + V(-0.75, 0, 0.25), (1.3, 3.5, 3.2), MANE, top=(0.75, 0.8), bot=(0.8, 0.8))
    for k in range(12):                         # wild ruff: spikes radiating round the face and swept back
        a = 2 * math.pi * (k + 0.5) / 12; y, z = math.cos(a), math.sin(a); L = 1.9 if k % 2 else 1.55
        b = hc + V(-0.7, y * 1.35, 0.25 + z * 1.35)
        m.spike(f"RuffSpike{k}", b, b + V(-1.0, y * L, z * L), 0.5, MANE if k % 2 else MANE_D, flat=0.6)
    m.box("Head", hc, (2.0, 2.35, 1.9), FACE, top=(0.86, 0.88), bot=(0.88, 0.9))
    m.box("Brow", hc + V(0.85, 0, 0.62), (0.5, 2.1, 0.42), dk(FACE, 0.85), top=(0.7, 0.92))
    for s in (1, -1):
        m.box(f"Ear{s}", hc + V(-0.35, s * 1.05, 1.15), (0.5, 0.55, 0.55), FACE, top=(0.65, 0.75))
        m.box(f"Pad{s}", hc + V(1.4, s * 0.4, -0.38), (0.8, 0.82, 0.68), MUZ, top=(0.85, 0.9))
    m.box("Nose", hc + V(1.83, 0, -0.02), (0.2, 0.8, 0.45), rgb(52, 30, 26), bot=(0.9, 0.45), studs=False)
    for k in range(3):
        m.box(f"Wrinkle{k}", hc + V(1.05 + k * 0.22, 0, 0.3 - k * 0.05), (0.12, 0.9, 0.12), dk(FACE, 0.7), studs=False)
    m.box("Mouth", hc + V(1.2, 0, -0.85), (0.85, 1.25, 0.55), MOUTH, studs=False)
    m.teeth("ToothT", hc + V(1.7, -0.45, -0.72), hc + V(1.7, 0.45, -0.72), 4, 0.22, 0.09)
    for s in (1, -1):
        m.spike(f"Fang{s}", hc + V(1.72, s * 0.42, -0.66), hc + V(1.78, s * 0.42, -1.4), 0.12, TOOTH, flat=0.35)
    m.eyes(tuple(hc + V(1.02, 0.55, 0.22)), size=(0.62, 0.4), pupil=0.85, look=(0.4, 0), angry=0.5, white=EYE, glow_white=True,
           brow_col=rgb(70, 40, 28), brow_h=0.55, brow_up=0.72, depth=0.15)
    with m.bone("Jaw", hc + V(0.4, 0, -0.75)), m.frame(pivot=hc + V(0.4, 0, -0.75), rot=Ry(0.45)):
        m.box("Jaw", hc + V(1.1, 0, -1.1), (1.25, 1.25, 0.42), MUZ)
        m.box("Tongue", hc + V(1.05, 0, -0.88), (0.95, 0.85, 0.12), TONGUE, studs=False)
        m.teeth("ToothB", hc + V(1.6, -0.38, -0.92), hc + V(1.6, 0.38, -0.92), 3, 0.2, 0.08, down=False)
        for s in (1, -1):
            m.spike(f"FangB{s}", hc + V(1.62, s * 0.45, -0.95), hc + V(1.66, s * 0.45, -0.42), 0.11, TOOTH, flat=0.35)

# ---------------------------------------------------------------- snake tail: up off the rump, round the right flank to the front
pts = [V(-3.0, 0, 3.9), V(-3.9, 0, 4.6), V(-4.5, -0.7, 3.6), V(-3.9, -2.0, 1.7), V(-2.3, -2.65, 0.75), V(-0.5, -2.85, 0.7),
       V(0.9, -2.95, 1.35), V(1.55, -2.95, 2.5)]
ws = [0.85, 0.82, 0.78, 0.72, 0.66, 0.6, 0.54, 0.5]
m.chain("Snake", pts, ws, SNAKE, bones="Tail")
for i in range(1, len(pts) - 1):
    with m.bone(f"Tail{i}"):
        for t in (0.3, 0.75):
            q = pts[i].lerp(pts[i + 1], t); w = ws[i] + (ws[i + 1] - ws[i]) * t
            d = (pts[i + 1] - pts[i]).normalized(); out = V(0, -1, 0) if i >= 3 else V(0, 0, 1)
            inn = (V(0, 0, -1) if i >= 3 else V(0, 0, -1))
            m.box(f"Belly{i}{t}", q + inn * w * 0.46, (w * 0.55, w * 0.55, w * 0.14), SNAKE_B, studs=False)
            m.box(f"Diamond{i}{t}", q + V(0, 0, w * 0.47), (w * 0.38, w * 0.38, w * 0.1), SNAKE_D, rot=Rz(0.785), studs=False)
e = pts[-1]; n = len(pts) - 1
with m.bone(f"Tail{n}"):
    hd = e + V(0.45, 0, 0.35)
    m.box("SnakeHead", hd, (1.15, 0.85, 0.52), SNAKE, top=(0.85, 0.9))
    m.box("SnakeMouth", hd + V(0.05, 0, -0.32), (0.95, 0.68, 0.14), MOUTH, studs=False)
    for s in (1, -1):
        m.box(f"SnakeEye{s}", hd + V(0.18, s * 0.44, 0.1), (0.3, 0.06, 0.2), rgb(255, 214, 60), studs=False, glow=True)
        m.box(f"SnakePupil{s}", hd + V(0.18, s * 0.47, 0.1), (0.06, 0.04, 0.19), PUPIL, studs=False)
        m.box(f"SnakeBrow{s}", hd + V(0.15, s * 0.43, 0.28), (0.4, 0.09, 0.1), SNAKE_D, rot=Ry(0.25), studs=False)
        m.spike(f"SnakeFang{s}", hd + V(0.46, s * 0.24, -0.22), hd + V(0.52, s * 0.24, -0.68), 0.08, TOOTH, flat=0.3)
    with m.frame(pivot=hd + V(-0.45, 0, -0.28), rot=Ry(0.55)):
        m.box("SnakeJaw", hd + V(0.05, 0, -0.42), (1.0, 0.75, 0.2), SNAKE_B)
        for s in (1, -1):
            m.spike(f"SnakeFangB{s}", hd + V(0.46, s * 0.2, -0.34), hd + V(0.5, s * 0.2, -0.02), 0.07, TOOTH, flat=0.3)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 22, 24, 45)], glow_color=EYE)
