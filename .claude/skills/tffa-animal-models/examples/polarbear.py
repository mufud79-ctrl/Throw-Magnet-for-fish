"""TFFA PolarBear (Arctic, Cannon Tame) - hero build.

Reference analysis (a charging, roaring polar bear on the ice, most important first):
1. Silhouette: a huge heavy quadruped, shoulder hump the highest point, long neck reaching FORWARD and LOW so the head
   sits below the shoulders (attack posture), massive pillar legs with dinner-plate paws, small rump.
2. Head: long wedge head, black nose, ROARING open jaw (crimson mouth, blade teeth, long fangs, tongue), small round ears,
   ice-blue eyes squinted under heavy dark brows, nose-bridge wrinkles.
3. Signature: shaggy scruff on the neck/shoulders swept back with frosted ice-blue tips, shaggy fringe hanging along the
   belly and behind the legs, long black claws, frost on the back (a few ice crystals).
4. Colours: warm white + cream shadows, black nose/claws/lips, ice-blue eyes + frost accents.
Bones: Body, Neck, Head, Jaw, Ear_L/R, Leg_FL/FR/BL/BR, Tail1. Studded, snarl + muscular."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

FUR, FUR_D, CREAM, MUZ = rgb(240, 236, 222), rgb(206, 200, 182), rgb(224, 218, 198), rgb(232, 226, 210)
BLK, ICE, ICE_D, SCAR = rgb(30, 30, 38), rgb(150, 214, 255), rgb(96, 168, 230), rgb(196, 170, 170)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("PolarBear", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.55, chamfer=0.17, jitter=0.04)
m.gait = {"amp": 0.75}

body = m.bone("Body", (0, 0, 4.0)); body.__enter__()
m.box("Chest", (1.4, 0, 4.0), (3.2, 3.5, 3.4), FUR, top=(0.82, 0.86), bot=(0.78, 0.86))
m.box("Waist", (-0.8, 0, 3.95), (2.4, 3.1, 2.7), FUR, top=(0.92, 0.92), bot=(0.86, 0.9))
m.box("Hips", (-2.5, 0, 3.85), (2.3, 3.2, 2.9), FUR, top=(0.8, 0.86), bot=(0.86, 0.9))
m.box("Hump", (1.0, 0, 5.85), (2.8, 2.7, 1.1), FUR, top=(0.6, 0.72))
m.box("Back", (-1.0, 0, 5.25), (3.6, 1.8, 0.5), FUR_D, top=(0.7, 0.8))
for s in (1, -1):
    m.box(f"Haunch{s}", (-2.5, s * 1.5, 3.8), (1.8, 0.4, 2.0), FUR, top=(0.8, 0.8), bot=(0.7, 0.8))
    m.box(f"ShoulderBulge{s}", (1.6, s * 1.72, 4.3), (2.0, 0.4, 2.0), FUR, top=(0.8, 0.8), bot=(0.75, 0.8))
    for k in range(6):                                  # shaggy fringe hanging along the belly
        x = 2.0 - k * 0.85
        m.spike(f"Fringe{s}{k}", (x, s * 1.35, 2.75), (x - 0.35, s * 1.45, 1.85), 0.42, FUR_D if k % 2 else CREAM, flat=0.55)
for j, (x, z, w, a) in enumerate(((1.0, 4.6, 1.0, 0.5), (0.4, 4.1, 0.8, -0.4))):     # claw scars on the left flank
    m.box(f"Scar{j}", (x, 1.95, z), (w, 0.08, 0.12), SCAR, rot=Ry(a), **NS)
# scruff: thick fur swept back off the neck and hump, frosted ice-blue tips
m.box("Scruff", (2.2, 0, 5.4), (2.0, 3.0, 1.2), FUR, top=(0.7, 0.8))
for k in range(8):
    x = 3.0 - k * 0.45; y = (k % 3 - 1) * 0.8; z = 5.95 - k * 0.1
    b = V(x, y, z); t = b + V(-1.2, y * 0.3, 0.55)
    m.spike(f"Shag{k}", b, t, 0.45, FUR if k % 2 else CREAM, flat=0.55)
    m.spike(f"Frost{k}", b.lerp(t, 0.6), t + V(-0.15, 0, 0.08), 0.2, ICE, flat=0.55)
for j, (x, y) in enumerate(((-0.4, 0.5), (-1.5, -0.4), (-2.6, 0.3))):    # ice crystals frozen on the back
    m.spike(f"IceCrystal{j}", (x, y, 5.35 - j * 0.1), (x - 0.2, y * 1.2, 6.05 - j * 0.1), 0.26, ICE, sides=4)

for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (1.8, s * 1.5, 4.0)):
        m.box(f"Shoulder{s}", (1.9, s * 1.6, 3.6), (1.9, 0.9, 2.5), FUR, top=(0.8, 0.8), bot=(0.8, 0.85))
        m.seg(f"Forearm{s}", V(2.1, s * 1.62, 2.9), V(2.45, s * 1.72, 0.75), 1.5, 1.35, FUR)
        m.spike(f"LegShag{s}", V(1.6, s * 1.75, 2.6), V(1.0, s * 1.85, 1.5), 0.4, CREAM, flat=0.55)
        m.box(f"Paw{s}", (2.7, s * 1.75, 0.36), (2.0, 1.6, 0.72), FUR, top=(0.86, 0.9))
        for t in (-1.5, -0.5, 0.5, 1.5):
            b = V(3.65, s * 1.75 + t * 0.36, 0.34)
            m.spike(f"Claw{s}{t}", b, b + V(0.55, t * 0.05, -0.3), 0.12, BLK, flat=0.4)
    with m.bone(f"Leg_B{LR(s)}", (-2.5, s * 1.4, 3.9)):
        m.box(f"Thigh{s}", (-2.55, s * 1.5, 2.9), (2.2, 1.2, 2.6), FUR, rot=Ry(-0.25), top=(0.85, 0.9), bot=(0.7, 0.8))
        m.seg(f"Shin{s}", V(-2.95, s * 1.55, 2.1), V(-2.6, s * 1.6, 0.7), 1.3, 1.2, FUR)
        m.box(f"HindPaw{s}", (-2.3, s * 1.6, 0.36), (1.9, 1.5, 0.72), FUR, top=(0.86, 0.9))
        for t in (-1, 0, 1):
            b = V(-1.38, s * 1.6 + t * 0.4, 0.34)
            m.spike(f"HClaw{s}{t}", b, b + V(0.45, 0, -0.26), 0.11, BLK, flat=0.4)
with m.bone("Tail1", (-3.6, 0, 4.4)):
    m.box("Tail", (-3.8, 0, 4.4), (0.6, 0.8, 0.7), FUR, top=(0.7, 0.7))

# long neck reaching forward and down; head below the shoulder line, roaring
with m.bone("Neck", (2.6, 0, 4.9)):
    m.seg("Neck", V(2.4, 0, 4.9), V(4.1, 0, 4.15), 2.4, 2.0, FUR, d0=2.5, d1=2.0)
with m.bone("Head", (4.0, 0, 4.2), "Neck"):
    hc = V(4.9, 0, 3.95)
    m.box("Head", hc, (1.9, 2.15, 1.75), FUR, top=(0.84, 0.86), bot=(0.88, 0.9))
    m.box("Brow", hc + V(0.7, 0, 0.6), (0.6, 1.95, 0.45), CREAM, top=(0.7, 0.92))
    m.box("Snout", hc + V(1.5, 0, -0.25), (1.6, 1.3, 0.85), MUZ, top=(0.86, 0.9), bot=(0.95, 0.95))
    m.box("Nose", hc + V(2.32, 0, 0.02), (0.22, 0.75, 0.42), BLK, bot=(0.9, 0.55), **NS)
    for k in range(3): m.box(f"Wrinkle{k}", hc + V(0.95 + k * 0.25, 0, 0.22), (0.1, 0.95, 0.1), FUR_D, **NS)
    m.box("Maw", hc + V(1.35, 0, -0.78), (1.5, 1.1, 0.4), MOUTH, **NS)
    m.box("Lip", hc + V(1.45, 0, -0.66), (1.55, 1.32, 0.1), BLK, **NS)
    for t in (1, -1):
        for k, x in enumerate((1.25, 1.6, 1.95)):
            m.spike(f"ToothU{t}{k}", hc + V(x, t * 0.55, -0.72), hc + V(x + 0.02, t * 0.54, -1.02), 0.09, TOOTH, flat=0.3)
        m.spike(f"Fang{t}", hc + V(2.15, t * 0.45, -0.7), hc + V(2.2, t * 0.45, -1.3), 0.13, TOOTH, flat=0.35)
    for s in (1, -1):
        m.box(f"EyePatch{s}", hc + V(0.86, s * 0.62, 0.22), (0.2, 0.62, 0.42), rgb(70, 76, 96), **NS)
    m.eyes(tuple(hc + V(0.98, 0.62, 0.22)), facing=(0.85, 0.5, 0), size=(0.55, 0.34), pupil=0.8, look=(0.5, 0), angry=0.55,
           white=ICE, brow_col=BLK, brow_h=0.6, brow_up=0.75, depth=0.14)
    for s in (1, -1):
        with m.bone(f"Ear_{LR(s)}", hc + V(-0.4, s * 0.8, 0.8)):
            m.box(f"Ear{s}", hc + V(-0.4, s * 0.85, 0.95), (0.4, 0.55, 0.5), FUR, top=(0.65, 0.75))
            m.box(f"EarIn{s}", hc + V(-0.22, s * 0.85, 0.95), (0.08, 0.32, 0.3), FUR_D, **NS)
    with m.bone("Jaw", hc + V(0.3, 0, -0.65)), m.frame(pivot=hc + V(0.3, 0, -0.65), rot=Ry(0.42)):
        m.box("Jaw", hc + V(1.3, 0, -1.08), (1.65, 1.2, 0.42), MUZ)
        m.box("Tongue", hc + V(1.2, 0, -0.84), (1.1, 0.8, 0.12), TONGUE, **NS)
        for t in (1, -1):
            for k, x in enumerate((1.4, 1.8)):
                m.spike(f"ToothL{t}{k}", hc + V(x, t * 0.48, -0.88), hc + V(x - 0.02, t * 0.47, -0.62), 0.08, TOOTH, flat=0.3)
            m.spike(f"FangB{t}", hc + V(2.02, t * 0.42, -0.9), hc + V(2.05, t * 0.42, -0.4), 0.11, TOOTH, flat=0.35)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
