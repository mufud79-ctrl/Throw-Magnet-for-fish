"""TFFA Sabertooth (Ice Age, Cannon Tame) - hero build: Smilodon on the attack.

Reference analysis (a Smilodon roaring over its kill, the classic paleo-art pose, most important first):
1. Silhouette: a heavy, bear-like big cat - massive front quarters and shoulders as the highest point, back sloping down to
   lower hips, thick powerful forelegs set wide, a SHORT bobbed tail (no long cat tail), head low and forward.
2. Head: mouth gaping enormously wide (the Smilodon gape) so the two huge SABRE FANGS hang free, longer than the head is
   tall, white and flat-bladed; snarl wrinkles, angry squinted amber eyes under heavy brows, short round ears.
3. Signature: the sabres, the bob tail, a shaggy ice-age ruff on the neck/shoulders with frost tips, faint darker
   stripes on the flanks, big paws with dark claws.
4. Colours: tawny gold + darker back/stripes, cream muzzle/belly, white fangs, frost-blue accents, amber eyes.
Bones: Body, Neck, Head, Jaw, Ear_L/R, Leg_FL/FR/BL/BR, Tail1. Studded, snarl + muscular."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

FUR, FUR_D, CREAM, STRIPE = rgb(214, 160, 88), rgb(164, 112, 58), rgb(244, 222, 180), rgb(126, 80, 40)
FROST, CLAW, AMBER = rgb(186, 226, 255), rgb(44, 34, 30), rgb(255, 170, 40)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Sabertooth", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.5, chamfer=0.17, jitter=0.06)
m.gait = {"amp": 0.85}

body = m.bone("Body", (0, 0, 3.6)); body.__enter__()
m.box("Chest", (1.3, 0, 3.75), (2.9, 3.0, 3.1), FUR, top=(0.8, 0.86), bot=(0.78, 0.86))
m.box("Waist", (-0.75, 0, 3.55), (2.2, 2.5, 2.2), FUR, top=(0.92, 0.92), bot=(0.86, 0.9))
m.box("Hips", (-2.2, 0, 3.3), (1.9, 2.6, 2.3), FUR, top=(0.82, 0.86), bot=(0.86, 0.9))
m.box("Back", (-0.8, 0, 4.6), (3.6, 1.5, 0.45), FUR_D, top=(0.7, 0.8))
m.box("Belly", (-0.4, 0, 2.45), (3.4, 1.8, 0.4), CREAM, **NS)
for s in (1, -1):
    m.box(f"Haunch{s}", (-2.2, s * 1.22, 3.2), (1.6, 0.4, 1.7), FUR, top=(0.8, 0.8), bot=(0.7, 0.8))
    m.box(f"ShoulderBulge{s}", (1.5, s * 1.55, 4.0), (1.9, 0.35, 1.8), FUR, top=(0.8, 0.8), bot=(0.75, 0.8))
    for j, x in enumerate((0.2, -0.45, -1.1, -1.75)):                # faint flank stripes
        m.box(f"Stripe{s}{j}", (x, s * (1.27 if x > -1.6 else 1.32), 3.75), (0.22, 0.08, 1.2 - 0.1 * j), STRIPE, rot=Ry(0.25), **NS)
# shaggy ice-age ruff on neck + shoulders, swept back, frost tips
m.box("Ruff", (2.1, 0, 4.9), (1.8, 3.1, 1.3), FUR_D, top=(0.7, 0.8))
for k in range(9):
    x = 2.9 - k * 0.42; y = (k % 3 - 1) * 0.85; z = 5.35 - k * 0.1
    b = V(x, y, z); t = b + V(-1.15, y * 0.35, 0.45)
    m.spike(f"Shag{k}", b, t, 0.42, FUR_D if k % 2 else FUR, flat=0.55)
    m.spike(f"Frost{k}", b.lerp(t, 0.62), t + V(-0.12, 0, 0.06), 0.18, FROST, flat=0.55)
for s in (1, -1):
    for k in range(3):
        b = V(2.4 - k * 0.5, s * 1.6, 4.3 - k * 0.2)
        m.spike(f"SideShag{s}{k}", b, b + V(-0.6, s * 0.35, -0.75), 0.36, FUR_D, flat=0.55)

for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (1.7, s * 1.3, 3.6)):
        m.box(f"Shoulder{s}", (1.8, s * 1.4, 3.35), (1.7, 0.75, 2.1), FUR, top=(0.8, 0.8), bot=(0.75, 0.85))
        m.seg(f"Forearm{s}", V(1.95, s * 1.42, 2.7), V(2.3, s * 1.55, 0.7), 1.3, 1.1, FUR)
        m.box(f"Paw{s}", (2.55, s * 1.58, 0.33), (1.6, 1.3, 0.66), FUR, top=(0.85, 0.9))
        for t in (-1.5, -0.5, 0.5, 1.5):
            b = V(3.3, s * 1.58 + t * 0.3, 0.32)
            m.spike(f"Claw{s}{t}", b, b + V(0.5, t * 0.05, -0.28), 0.1, CLAW, flat=0.4)
    with m.bone(f"Leg_B{LR(s)}", (-2.2, s * 1.15, 3.3)):
        m.box(f"Thigh{s}", (-2.25, s * 1.22, 2.5), (1.8, 0.95, 2.1), FUR, rot=Ry(-0.3), top=(0.85, 0.9), bot=(0.7, 0.8))
        m.seg(f"Hock{s}", V(-2.75, s * 1.25, 1.8), V(-2.45, s * 1.3, 0.6), 0.9, 0.8, FUR_D)
        m.box(f"HindPaw{s}", (-2.2, s * 1.3, 0.3), (1.35, 1.1, 0.6), FUR_D, top=(0.85, 0.9))
with m.bone("Tail1", (-3.05, 0, 3.9)):
    m.seg("Tail", V(-3.0, 0, 3.9), V(-3.75, 0, 4.35), 0.62, 0.5, FUR)
    m.box("TailTip", (-3.85, 0, 4.4), (0.5, 0.55, 0.5), STRIPE, top=(0.7, 0.7))

with m.bone("Neck", (2.6, 0, 4.4)):
    m.seg("Neck", V(2.3, 0, 4.5), V(3.4, 0, 3.9), 2.0, 1.8, FUR, d0=2.2, d1=1.9)
with m.bone("Head", (3.3, 0, 4.0), "Neck"):
    hc = V(4.1, 0, 3.8)
    m.box("Head", hc, (1.9, 2.15, 1.75), FUR, top=(0.84, 0.86), bot=(0.88, 0.9))
    m.box("Brow", hc + V(0.72, 0, 0.6), (0.55, 1.95, 0.42), FUR_D, top=(0.7, 0.92))
    m.box("Muzzle", hc + V(1.3, 0, -0.25), (1.1, 1.45, 0.85), CREAM, top=(0.86, 0.9))
    m.box("Nose", hc + V(1.88, 0, 0.08), (0.18, 0.6, 0.36), rgb(60, 36, 30), bot=(0.9, 0.5), **NS)
    for k in range(3): m.box(f"Wrinkle{k}", hc + V(0.95 + k * 0.22, 0, 0.3), (0.1, 1.0, 0.1), FUR_D, **NS)
    m.box("Maw", hc + V(1.2, 0, -0.85), (1.2, 1.25, 0.45), MOUTH, **NS)
    for t in (1, -1):                                        # the sabres: long flat blades hanging past the chin
        m.spike(f"Sabre{t}", hc + V(1.55, t * 0.55, -0.6), hc + V(1.78, t * 0.58, -2.35), 0.24, TOOTH, flat=0.38)
        m.spike(f"Tooth{t}", hc + V(1.75, t * 0.25, -0.62), hc + V(1.77, t * 0.25, -0.9), 0.08, TOOTH, flat=0.3)
    m.eyes(tuple(hc + V(0.98, 0.58, 0.22)), facing=(0.85, 0.5, 0), size=(0.58, 0.34), pupil=0.8, look=(0.5, 0), angry=0.55,
           white=AMBER, brow_col=CLAW, brow_h=0.6, brow_up=0.75, depth=0.14)
    for s in (1, -1):
        with m.bone(f"Ear_{LR(s)}", hc + V(-0.4, s * 0.8, 0.8)):
            m.box(f"Ear{s}", hc + V(-0.4, s * 0.85, 0.95), (0.4, 0.5, 0.5), FUR, top=(0.6, 0.7))
    with m.bone("Jaw", hc + V(0.2, 0, -0.65)), m.frame(pivot=hc + V(0.2, 0, -0.65), rot=Ry(0.75)):   # the Smilodon gape
        m.box("Jaw", hc + V(1.0, 0, -1.05), (1.45, 1.15, 0.4), CREAM)
        m.box("Tongue", hc + V(0.95, 0, -0.84), (1.0, 0.75, 0.12), TONGUE, **NS)
        m.teeth("ToothB", hc + V(1.6, -0.4, -0.85), hc + V(1.6, 0.4, -0.85), 4, 0.18, 0.07, down=False)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
