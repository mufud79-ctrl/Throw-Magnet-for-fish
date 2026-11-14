"""TFFA Sloth (Jungle, Cannon Tame) - hero build: a three-toed sloth.

Reference analysis (the iconic smiling three-toed sloth, most important first):
1. Silhouette: a hunched pear - narrow round head low on a big shaggy body, very long arms reaching forward and down
   ending in HUGE hooked claws (the claws are as long as the hands), short stubby legs.
2. Head: round, pale face mask with the famous dark eye stripes running from the eyes back toward the ears, heavy
   sleepy lids (half-closed eyes), small dark nose and a permanent content smile; a shaggy fringe on the forehead.
3. Signature: the three long cream claws on each hand, shaggy fur hanging in strands from the shoulders/back/arms,
   green algae-moss patches with tiny sprouting leaves on the back, a pink jungle flower stuck on the head.
4. Colours: grey-tan fur + darker strands, cream face, dark brown stripes, moss green, pink flower accent.
Bones: Body, Head, Arm_L/R, Leg_L/R, Tail1 (slow biped). Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

FUR, FUR_D, FUR_L, FACE = rgb(170, 146, 108), rgb(122, 100, 72), rgb(206, 186, 146), rgb(242, 230, 198)
STRIPE, MOSS, MOSS_D, CLAWC = rgb(66, 46, 34), rgb(108, 168, 66), rgb(66, 120, 44), rgb(236, 220, 184)
PETAL, PETAL_D, YELLOW = rgb(255, 100, 150), rgb(214, 52, 104), rgb(255, 214, 50)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Sloth", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.42, chamfer=0.16, jitter=0.05)
m.gait = {"amp": 0.6}

body = m.bone("Body", (0, 0, 1.8)); body.__enter__()
m.box("Pelvis", (-0.15, 0, 1.45), (1.6, 2.0, 1.1), FUR, top=(0.95, 0.95), bot=(0.8, 0.85))
m.seg("Torso", V(-0.1, 0, 1.4), V(0.3, 0, 3.45), 2.3, 2.0, FUR, d0=1.75, d1=1.5)
m.box("Belly", (0.72, 0, 2.2), (0.3, 1.45, 1.5), FUR_L, rot=Ry(-0.18), top=(0.85, 0.9))
for k in range(10):                                        # shaggy strands hanging off the back and flanks
    a = math.pi * (0.15 + 0.7 * (k % 5) / 4); y = math.cos(a) * 1.05; z = 3.2 - (k // 5) * 0.85
    b = V(-0.62 - 0.12 * (k // 5), y * 0.95, z)
    m.spike(f"Shag{k}", b, b + V(-0.22, y * 0.15, -0.85), 0.3, FUR_D if k % 2 else FUR, flat=0.5)
# algae moss on the back, with sprouting leaves
for k, (y, z, w, h) in enumerate(((0.35, 2.75, 0.75, 0.6), (-0.4, 2.3, 0.6, 0.55), (0.05, 1.85, 0.55, 0.45))):
    m.box(f"Moss{k}", (-0.88 + (z - 1.85) * 0.12, y, z), (0.2, w, h), MOSS if k % 2 == 0 else MOSS_D, rot=Ry(-0.2), **NS)
for k, (x, y, w) in enumerate(((-0.35, 0.55, 0.75), (-0.2, -0.6, 0.6), (-0.6, -0.05, 0.6))):   # moss over the shoulders
    m.box(f"MossTop{k}", (x, y, 3.42 - 0.1 * k), (w, w * 0.9, 0.18), MOSS if k % 2 == 0 else MOSS_D, rot=Ry(0.15), **NS)
for k, (y, z, a) in enumerate(((0.45, 3.05, 0.5), (0.2, 3.1, -0.3), (-0.45, 2.55, 0.2))):
    o = V(-0.95 + (z - 1.85) * 0.12, y, z)
    m.slab(f"Leaf{k}", [(0, 0), (0.18, 0.3), (0, 0.62), (-0.18, 0.3)], 0.07, MOSS, origin=o,
           xaxis=(0, math.cos(a), math.sin(a) * 0.3), yaxis=(-0.6, math.sin(a) * 0.5, 0.8))

with m.bone("Head", (0.4, 0, 3.55)), m.frame(pivot=(0.5, 0, 3.7), scale=1.15):
    hc = V(0.7, 0, 4.15)
    m.box("Head", hc, (1.55, 1.85, 1.45), FUR, top=(0.8, 0.85), bot=(0.85, 0.85))
    m.box("Face", hc + V(0.72, 0, -0.08), (0.25, 1.55, 1.15), FACE, top=(0.85, 0.9), bot=(0.8, 0.85))
    m.box("Snout", hc + V(0.88, 0, -0.36), (0.3, 0.8, 0.5), FACE, top=(0.85, 0.85))
    for k in range(4):                                     # shaggy fringe over the forehead
        y = (k - 1.5) * 0.4; b = hc + V(0.55, y, 0.62)
        m.spike(f"Fringe{k}", b, b + V(0.35, y * 0.25, -0.35), 0.24, FUR_D if k % 2 else FUR, flat=0.55)
    for s in (1, -1):                                      # dark eye stripes sweeping back toward the ears
        m.box(f"Stripe{s}", hc + V(0.86, s * 0.42, 0.04), (0.08, 0.66, 0.38), STRIPE, rot=Rx(s * 0.28), **NS)
        m.box(f"StripeSide{s}", hc + V(0.35, s * 0.86, -0.05), (0.85, 0.1, 0.32), STRIPE, rot=Ry(0.15), **NS)
    m.eyes(tuple(hc + V(0.92, 0.42, 0.06)), size=(0.5, 0.42), pupil=0.8, look=(0.15, -0.2), angry=-0.12,
           brow_col=STRIPE, brow_up=0.3, brow_h=0.55, brow_w=1.2, depth=0.12)
    m.box("Nose", hc + V(1.05, 0, -0.22), (0.12, 0.42, 0.26), NOSE, top=(0.8, 0.7), **NS)
    m.box("Smile", hc + V(1.04, 0, -0.5), (0.08, 0.42, 0.08), STRIPE, **NS)
    for s in (1, -1):
        m.box(f"SmileUp{s}", hc + V(1.02, s * 0.3, -0.44), (0.08, 0.24, 0.08), STRIPE, rot=Rx(s * 0.55), **NS)
    f = hc + V(0.15, 0.98, 0.5)                            # pink jungle flower tucked behind the left eye stripe
    for k in range(5):
        a = 2 * math.pi * k / 5
        m.slab(f"Petal{k}", [(-0.16, 0), (0.16, 0), (0.26, 0.34), (0, 0.5), (-0.26, 0.34)], 0.07, PETAL if k % 2 else PETAL_D,
               origin=f, xaxis=(-math.sin(a), 0, math.cos(a)), yaxis=(math.cos(a), 0.3, math.sin(a)), grad=(PETAL_D, PETAL))
    m.box("FlowerHeart", f + V(0, 0.1, 0), (0.22, 0.16, 0.22), YELLOW, **NS)

for s in (1, -1):
    with m.bone(f"Arm_{LR(s)}", (0.3, s * 1.1, 3.2)):
        m.box(f"Shoulder{s}", (0.3, s * 1.12, 3.15), (0.9, 0.75, 0.85), FUR)
        m.seg(f"UpperArm{s}", V(0.3, s * 1.15, 3.1), V(0.8, s * 1.62, 2.05), 0.72, 0.62, FUR)
        m.seg(f"Forearm{s}", V(0.8, s * 1.62, 2.1), V(1.4, s * 1.48, 1.2), 0.62, 0.56, FUR)
        for j in range(2):                                 # fur strands hanging under the arm
            b = V(0.55 + j * 0.55, s * (1.45 + j * 0.1), 2.5 - j * 0.65)
            m.spike(f"ArmShag{s}{j}", b, b + V(-0.35, s * 0.2, -0.6), 0.25, FUR_D, flat=0.55)
        m.box(f"Hand{s}", (1.5, s * 1.45, 1.05), (0.55, 0.6, 0.5), FUR_D, top=(0.9, 0.9))
        for k in (-1, 0, 1):                               # three huge hooked claws
            y = s * 1.45 + k * 0.19
            a, b, c = V(1.7, y, 1.05), V(2.15, y, 0.78), V(2.12, y, 0.3)
            m.seg(f"Claw{s}{k}", a, b, 0.15, 0.13, CLAWC, **NS)
            m.spike(f"ClawTip{s}{k}", b + V(0.02, 0, 0.05), c, 0.08, CLAWC, flat=0.6)
    with m.bone(f"Leg_{LR(s)}", (-0.05, s * 0.7, 1.3)):
        m.seg(f"Thigh{s}", V(-0.1, s * 0.72, 1.4), V(0.3, s * 0.88, 0.75), 0.85, 0.7, FUR)
        m.seg(f"Shin{s}", V(0.3, s * 0.88, 0.8), V(0.2, s * 0.92, 0.3), 0.7, 0.6, FUR_D)
        m.box(f"Foot{s}", (0.4, s * 0.92, 0.2), (0.85, 0.65, 0.4), FUR_D, top=(0.85, 0.9))
        for k in (-1, 0, 1):
            b = V(0.8, s * 0.92 + k * 0.18, 0.18)
            m.spike(f"Toe{s}{k}", b, b + V(0.42, 0, -0.14), 0.08, CLAWC, flat=0.6)
with m.bone("Tail1", (-0.8, 0, 1.2)):
    m.box("Tail", (-0.95, 0, 1.15), (0.45, 0.5, 0.45), FUR_D, top=(0.7, 0.7))
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
