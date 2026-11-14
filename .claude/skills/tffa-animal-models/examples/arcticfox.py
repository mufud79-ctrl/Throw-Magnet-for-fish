"""TFFA ArcticFox (Arctic, Cannon Tame) - hero build.

Reference analysis (a white arctic fox stalking over the snow, most important first):
1. Silhouette: compact fluffy body low to the ground, a HUGE bushy tail sweeping up and curling forward over the back
   (as big as the body), head held low and forward in a stalking pose, alert big ears.
2. Head: narrow pointed snout with a black nose, sly half-grin with one small fang showing, narrowed ice-blue eyes under
   slanted brows (a cunning hunter), fluffy cheek ruff flaring out sideways.
3. Signature: the winter coat - a thick neck ruff and cheek tufts, fluffy fur tufts along the tail, frost-blue tail tip,
   socks and inner ears.
4. Colours: snow white + cool-grey shadows, frost blue accents, black nose, ice-blue eyes.
Bones: Body, Neck, Head, Ear_L/R, Leg_FL/FR/BL/BR, Tail1..4. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

FUR, FUR_D, FROST, FROST_D = rgb(248, 248, 252), rgb(208, 214, 228), rgb(176, 210, 246), rgb(120, 160, 214)
BLK, ICE, BROW = rgb(30, 30, 38), rgb(130, 210, 255), rgb(92, 112, 150)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("ArcticFox", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.4, chamfer=0.16, jitter=0.04)

body = m.bone("Body", (0, 0, 2.3)); body.__enter__()
m.box("Chest", (0.85, 0, 2.35), (1.8, 1.65, 1.75), FUR, top=(0.82, 0.86), bot=(0.8, 0.86))
m.box("Waist", (-0.45, 0, 2.4), (1.4, 1.4, 1.3), FUR, top=(0.92, 0.92), bot=(0.86, 0.9))
m.box("Hips", (-1.45, 0, 2.4), (1.4, 1.55, 1.55), FUR, top=(0.82, 0.86), bot=(0.86, 0.9))
m.box("Back", (-0.3, 0, 3.12), (2.6, 0.9, 0.26), FUR_D, top=(0.7, 0.8))
m.box("Belly", (-0.2, 0, 1.65), (2.4, 1.1, 0.3), FUR_D, **NS)
for k in range(10):                                         # thick winter neck ruff
    a = math.pi * (k + 0.5) / 10; y, z = math.cos(a), math.sin(a) * 0.9 - 0.15
    b = V(1.55, y * 0.85, 2.55 + z * 0.8)
    m.spike(f"Ruff{k}", b, b + V(-0.75, y * 0.55, z * 0.45), 0.36, FUR if k % 2 else FUR_D, flat=0.55)

def leg(nm, hip, foot, w0, w1):
    m.seg(nm, hip, foot, w0, w1, FUR)
    m.box(nm + "Sock", foot + V(0, 0, 0.25), (w1 * 1.05, w1 * 1.05, 0.55), FROST, top=(0.95, 0.95))
for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (1.0, s * 0.6, 2.2)):
        m.box(f"Shoulder{s}", (1.05, s * 0.7, 2.15), (1.0, 0.45, 1.1), FUR, top=(0.8, 0.8))
        leg(f"Foreleg{s}", V(1.05, s * 0.66, 2.0), V(1.3, s * 0.7, 0.3), 0.7, 0.6)
        m.box(f"Paw{s}", (1.45, s * 0.7, 0.2), (0.78, 0.62, 0.4), FROST, top=(0.85, 0.9))
    with m.bone(f"Leg_B{LR(s)}", (-1.5, s * 0.6, 2.3)):
        m.box(f"Thigh{s}", (-1.5, s * 0.7, 1.85), (1.2, 0.55, 1.4), FUR, rot=Ry(-0.3), top=(0.85, 0.9), bot=(0.65, 0.75))
        leg(f"Hock{s}", V(-1.8, s * 0.72, 1.4), V(-1.55, s * 0.72, 0.3), 0.6, 0.54)
        m.box(f"HindPaw{s}", (-1.35, s * 0.72, 0.2), (0.75, 0.58, 0.4), FROST, top=(0.85, 0.9))

# huge bushy tail sweeping up and curling forward over the back
pts = [V(-2.05, 0, 2.75), V(-2.9, 0, 3.0), V(-3.4, 0, 3.85), V(-3.25, 0, 4.75), V(-2.6, 0, 5.15)]
ws = [0.6, 1.05, 1.2, 1.05, 0.7]
m.chain("Tail", pts, ws, FUR, bones="Tail")
for i in range(1, 4):
    with m.bone(f"Tail{i + 1 if i < 4 else 4}"):
        q = pts[i]; d = (pts[i + 1] - pts[i]).normalized()
        for s in (1, -1):
            m.spike(f"TailTuft{i}{s}", q + V(0, s * ws[i] * 0.4, 0), q + V(0, s * ws[i] * 0.85, 0) - d * 0.55, 0.36, FUR_D, flat=0.55)
with m.bone("Tail4"):
    m.spike("TailTip", pts[-1] - (pts[-1] - pts[-2]) * 0.15, pts[-1] + V(0.75, 0, -0.1), 0.42, FROST, flat=0.8)
    m.box("TailTipBand", pts[-1], (0.55, 0.75, 0.6), FROST, top=(0.8, 0.8))

with m.bone("Neck", (1.4, 0, 2.7)):
    m.seg("Neck", V(1.2, 0, 2.75), V(2.1, 0, 2.95), 1.25, 1.1, FUR, d0=1.3, d1=1.1)
with m.bone("Head", (2.0, 0, 2.95), "Neck"), m.frame(pivot=(2.0, 0, 2.95), scale=1.12):
    hc = V(2.5, 0, 3.05)
    m.box("Head", hc, (1.3, 1.45, 1.15), FUR, top=(0.82, 0.86), bot=(0.88, 0.9))
    for s in (1, -1):                                       # cheek ruff flaring out sideways
        for k, z in enumerate((-0.15, -0.45)):
            b = hc + V(-0.1, s * 0.6, z)
            m.spike(f"Cheek{s}{k}", b, b + V(-0.45, s * 0.65, -0.12 - 0.12 * k), 0.3, FUR if k else FUR_D, flat=0.55)
    m.box("Snout", hc + V(0.95, 0, -0.25), (1.0, 0.72, 0.52), FUR, top=(0.75, 0.85), bot=(0.9, 0.9))
    m.box("Nose", hc + V(1.47, 0, -0.1), (0.14, 0.34, 0.24), BLK, **NS)
    m.box("Mouth", hc + V(1.46, 0, -0.38), (0.06, 0.44, 0.06), BLK, **NS)
    for s in (1, -1):
        m.box(f"MouthSide{s}", hc + V(1.0, s * 0.37, -0.4), (0.9, 0.06, 0.06), BLK, **NS)
    m.box("Grin", hc + V(0.5, 0.37, -0.3), (0.36, 0.06, 0.06), BLK, rot=Ry(-0.5), **NS)       # sly half-grin on the left
    m.spike("Fang", hc + V(1.3, 0.3, -0.4), hc + V(1.32, 0.3, -0.72), 0.07, TOOTH, flat=0.35)
    m.eyes(tuple(hc + V(0.58, 0.42, 0.18)), facing=(0.9, 0.45, 0), size=(0.44, 0.26), pupil=0.85, look=(0.55, 0), angry=0.5,
           white=ICE, brow_col=BROW, brow_h=0.6, brow_up=0.75, depth=0.12)
    for s in (1, -1):
        with m.bone(f"Ear_{LR(s)}", hc + V(-0.2, s * 0.45, 0.55)):
            m.spike(f"Ear{s}", hc + V(-0.2, s * 0.48, 0.48), hc + V(-0.45, s * 0.66, 1.45), 0.38, FUR, flat=0.6)
            m.spike(f"EarIn{s}", hc + V(-0.1, s * 0.49, 0.55), hc + V(-0.35, s * 0.65, 1.2), 0.2, FROST, flat=0.5)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
