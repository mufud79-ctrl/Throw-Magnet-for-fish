"""TFFA WoollyRhino (Ice Age, Cannon Tame) - hero build: a charging woolly rhinoceros.

Reference analysis (a woolly rhino lowering its head to charge through a blizzard, most important first):
1. Silhouette: a long, low, massive barrel on short thick legs, a big shoulder hump as the highest point, the head held
   LOW (lower than the back), the huge front horn sweeping forward-up from the nose as long as the head; long shaggy
   coat hanging in strands below the belly line (same treatment as the Mammoth).
2. Head: long heavy head, a second smaller horn behind the first, small furious eyes under heavy brows, flared nostrils,
   short ears, a shaggy fringe.
3. Signature: the two horns (ivory -> dark tip), the hanging hair strands, frost/snow caught on the back, a bristly tail.
4. Colours: rusty red-brown coat + darker strands, ivory horns with dark tips, grey-brown skin on the face, snow white.
Bones: Body, Neck, Head, Ear_L/R, Leg_FL/FR/BL/BR, Tail1. Studded, fierce + muscular."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

FUR, FUR_D, FACE, HORN, HORN_D = rgb(156, 96, 54), rgb(112, 66, 36), rgb(128, 96, 76), rgb(236, 220, 186), rgb(96, 78, 64)
SNOW, BLK = rgb(244, 248, 255), rgb(30, 24, 22)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("WoollyRhino", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.55, chamfer=0.18, jitter=0.07)
m.gait = {"amp": 0.75}

body = m.bone("Body", (0, 0, 3.4)); body.__enter__()
m.box("Chest", (1.3, 0, 3.5), (2.8, 3.2, 3.0), FUR, top=(0.82, 0.86), bot=(0.8, 0.86))
m.box("Barrel", (-0.8, 0, 3.4), (2.6, 3.3, 2.8), FUR, top=(0.88, 0.9), bot=(0.86, 0.88))
m.box("Hips", (-2.6, 0, 3.35), (1.9, 3.0, 2.6), FUR, top=(0.8, 0.86), bot=(0.86, 0.9))
m.box("Hump", (1.2, 0, 5.2), (2.4, 2.6, 1.1), FUR_D, top=(0.6, 0.72))
for k, (x, y, z) in enumerate(((1.4, 0.4, 5.78), (0.2, -0.5, 4.88), (-1.2, 0.3, 4.88), (-2.4, -0.2, 4.72))):   # snow on the back
    m.box(f"Snow{k}", (x, y, z), (0.9, 0.8, 0.22), SNOW, rot=Rz(0.5 * k), **NS)
for s in (1, -1):                                            # hanging coat strands (Mammoth treatment)
    for k in range(9):
        x = 2.2 - k * 0.62; L = 1.5 + 0.35 * (k % 2)
        m.box(f"Strand{s}{k}", (x, s * 1.62, 2.35 - L / 2 + 0.6), (0.5, 0.3, L), FUR_D if k % 2 else FUR, top=(0.9, 0.9), bot=(0.7, 0.7))
for k in range(4):
    m.box(f"ChestStrand{k}", (2.75, (k - 1.5) * 0.7, 2.0), (0.3, 0.5, 1.4), FUR_D, bot=(0.7, 0.7))

for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (1.5, s * 1.25, 3.2)):
        m.box(f"Shoulder{s}", (1.55, s * 1.35, 2.9), (1.7, 0.9, 2.0), FUR, top=(0.8, 0.8), bot=(0.8, 0.85))
        m.seg(f"Foreleg{s}", V(1.6, s * 1.35, 2.2), V(1.75, s * 1.4, 0.4), 1.35, 1.25, FUR_D)
        m.box(f"Foot{s}", (1.85, s * 1.4, 0.3), (1.5, 1.35, 0.6), FACE, top=(0.9, 0.9))
        for t in (-1, 0, 1): m.box(f"Toe{s}{t}", (2.55, s * 1.4 + t * 0.42, 0.25), (0.32, 0.36, 0.42), HORN_D, **NS)
    with m.bone(f"Leg_B{LR(s)}", (-2.6, s * 1.15, 3.2)):
        m.box(f"Thigh{s}", (-2.6, s * 1.25, 2.6), (1.9, 1.0, 2.2), FUR, rot=Ry(-0.2), top=(0.85, 0.9), bot=(0.7, 0.8))
        m.seg(f"Hindleg{s}", V(-2.75, s * 1.3, 1.8), V(-2.55, s * 1.35, 0.4), 1.25, 1.15, FUR_D)
        m.box(f"HFoot{s}", (-2.45, s * 1.35, 0.3), (1.45, 1.3, 0.6), FACE, top=(0.9, 0.9))
with m.bone("Tail1", (-3.5, 0, 4.0)):
    m.seg("Tail", V(-3.5, 0, 4.0), V(-3.95, 0, 3.0), 0.32, 0.26, FUR_D)
    m.box("TailTuft", (-4.0, 0, 2.75), (0.45, 0.45, 0.6), BLK, bot=(0.6, 0.6))

with m.bone("Neck", (2.6, 0, 3.9)):
    m.seg("Neck", V(2.4, 0, 4.0), V(3.4, 0, 3.2), 2.3, 2.0, FUR, d0=2.4, d1=2.0)
    for k in range(5):                                       # shaggy fringe on the neck
        b = V(2.6 + k * 0.2, (k - 2) * 0.4, 4.9 - k * 0.25)
        m.spike(f"Fringe{k}", b, b + V(0.4, 0, -0.75), 0.32, FUR_D, flat=0.55)
with m.bone("Head", (3.3, 0, 3.3), "Neck"), m.frame(pivot=(3.3, 0, 3.3), scale=1.1):
    hc = V(4.3, 0, 2.95)
    m.box("Head", hc, (2.3, 1.75, 1.55), FACE, top=(0.8, 0.85), bot=(0.88, 0.9))
    m.box("Snout", hc + V(1.4, 0, -0.15), (0.9, 1.45, 1.15), FACE, top=(0.85, 0.9))
    m.box("Brow", hc + V(0.0, 0, 0.72), (0.7, 1.8, 0.4), FUR_D, top=(0.75, 0.9))
    for s in (1, -1):
        m.box(f"Nostril{s}", hc + V(1.86, s * 0.38, -0.12), (0.08, 0.22, 0.3), BLK, rot=Rx(s * 0.3), **NS)
        m.box(f"Mouth{s}", hc + V(1.3, s * 0.62, -0.62), (0.9, 0.06, 0.08), BLK, rot=Rz(s * 0.15), **NS)
        with m.bone(f"Ear_{LR(s)}", hc + V(-0.8, s * 0.7, 0.75)):
            m.spike(f"Ear{s}", hc + V(-0.8, s * 0.72, 0.68), hc + V(-1.0, s * 0.95, 1.4), 0.3, FUR, flat=0.6)
    # the horns: a huge front horn sweeping forward-up, a smaller second horn behind it
    hp = [hc + V(1.55, 0, 0.42), hc + V(2.15, 0, 1.25), hc + V(2.55, 0, 2.35), hc + V(2.75, 0, 3.15)]
    ws = [0.95, 0.72, 0.48, 0.28]
    for i in range(3):
        m.seg(f"Horn{i}", hp[i], hp[i + 1] + (hp[i + 1] - hp[i]).normalized() * 0.08, ws[i], ws[i + 1], HORN if i < 2 else HORN_D,
              d0=ws[i] * 1.3, d1=ws[i + 1] * 1.3, **NS)
    m.spike("HornTip", hp[3], hp[3] + V(0.2, 0, 0.55), 0.14, HORN_D, flat=0.8)
    m.seg("Horn2", hc + V(0.55, 0, 0.7), hc + V(0.75, 0, 1.7), 0.55, 0.22, HORN, d0=0.7, d1=0.28, **NS)
    m.spike("Horn2Tip", hc + V(0.75, 0, 1.68), hc + V(0.82, 0, 2.05), 0.11, HORN_D, flat=0.8)
    m.eyes(tuple(hc + V(0.2, 0.84, 0.25)), facing=(0.35, 1, 0), size=(0.46, 0.32), pupil=0.72, look=(0.5, 0), angry=0.55,
           brow_col=BLK, brow_h=0.6, brow_up=0.75, depth=0.14)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
