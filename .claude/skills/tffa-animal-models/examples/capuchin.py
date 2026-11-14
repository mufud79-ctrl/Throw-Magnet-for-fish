"""TFFA Monkey (Jungle, Cannon Tame) - hero build: a cheeky capuchin with a stolen banana.

Reference analysis (the classic cartoon jungle monkey, most important first):
1. Silhouette: upright on short bent legs, slight forward hunch, one long arm hanging to the knee, the other raised
   holding a banana out to the side; a long tail curling up behind into a question mark (taller than the head).
2. Head: BIG round head with a heart-shaped pale face (two lobes round the eyes, a muzzle below), round cup ears
   sticking straight out, a spiky tuft on top. Expression = mischief: one brow cocked up, the other pulled down,
   a wide toothy grin.
3. Signature: the peeled banana (yellow peel flaps hanging, cream fruit, brown tip), the curled tail, long arms with
   dark leathery hands and feet.
4. Colours: warm brown fur + darker back/limbs, pale peach face/ears/belly, dark skin hands, banana yellow.
Bones: Body, Head, Ear_L/R, Arm_L/R, Leg_L/R, Tail1..6 (biped). Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

FUR, FUR_D, FACE, SKIN = rgb(146, 88, 48), rgb(104, 62, 36), rgb(242, 200, 152), rgb(72, 46, 36)
BAN, FRUIT, BAN_D = rgb(255, 210, 46), rgb(255, 242, 196), rgb(96, 70, 34)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Monkey", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.4, chamfer=0.16, jitter=0.05)

body = m.bone("Body", (0, 0, 1.8)); body.__enter__()
m.box("Pelvis", (-0.05, 0, 1.75), (1.2, 1.55, 0.95), FUR, top=(0.95, 0.95), bot=(0.85, 0.85))
m.seg("Torso", V(0, 0, 1.75), V(0.22, 0, 3.35), 1.75, 2.0, FUR, d0=1.25, d1=1.4)
m.box("Belly", (0.62, 0, 2.35), (0.3, 1.15, 1.3), FACE, rot=Ry(-0.1), top=(0.85, 0.9))
m.box("BackStripe", (-0.5, 0, 2.7), (0.3, 1.0, 1.6), FUR_D, rot=Ry(-0.12))

with m.bone("Head", (0.3, 0, 3.45)), m.frame(pivot=(0.4, 0, 3.6), scale=1.12):
    hc = V(0.45, 0, 4.3)
    m.box("Head", hc, (1.75, 2.05, 1.7), FUR, top=(0.82, 0.86), bot=(0.88, 0.9))
    for k, (y, h, a) in enumerate(((0, 0.75, 0.0), (0.32, 0.6, 0.35), (-0.32, 0.6, -0.35))):    # spiky tuft
        b = hc + V(-0.1, y, 0.75)
        m.spike(f"Tuft{k}", b, b + V(-0.35, math.sin(a) * h, h), 0.3, FUR_D, flat=0.55)
    for s in (1, -1):                                       # heart-shaped face: two lobes round the eyes
        m.box(f"FaceLobe{s}", hc + V(0.86, s * 0.42, 0.12), (0.3, 0.8, 0.95), FACE, top=(0.85, 0.85))
    m.box("FaceMid", hc + V(0.86, 0, -0.2), (0.3, 1.2, 0.7), FACE)
    m.box("Muzzle", hc + V(1.08, 0, -0.55), (0.7, 1.15, 0.72), FACE, top=(0.85, 0.85), bot=(0.9, 0.9))
    for s in (1, -1):
        m.box(f"Nostril{s}", hc + V(1.44, s * 0.14, -0.38), (0.08, 0.14, 0.1), SKIN, **NS)
    m.box("Mouth", hc + V(1.43, 0, -0.68), (0.1, 0.9, 0.3), MOUTH, **NS)
    m.box("Teeth", hc + V(1.46, 0, -0.6), (0.08, 0.8, 0.12), TOOTH, **NS)
    for s in (1, -1):
        m.box(f"GrinCorner{s}", hc + V(1.4, s * 0.48, -0.56), (0.1, 0.22, 0.09), MOUTH, rot=Rx(s * 0.6), **NS)
    m.eyes(tuple(hc + V(1.05, 0.4, 0.15)), size=(0.52, 0.56), pupil=0.72, look=(0.35, 0.05), brow=False, depth=0.14)
    m.box("BrowL", hc + V(1.12, 0.42, 0.74), (0.16, 0.62, 0.15), FUR_D, rot=Rx(-0.28), **NS)    # cocked up (inner end raised)
    m.box("BrowR", hc + V(1.12, -0.4, 0.5), (0.16, 0.62, 0.17), FUR_D, rot=Rx(-0.3), **NS)     # pulled down
    for s in (1, -1):
        with m.bone(f"Ear_{LR(s)}", hc + V(0.0, s * 1.0, 0.1)):
            m.box(f"Ear{s}", hc + V(-0.05, s * 1.2, 0.12), (0.4, 0.42, 0.8), FUR, top=(0.85, 0.8))
            m.box(f"EarIn{s}", hc + V(0.06, s * 1.36, 0.12), (0.26, 0.12, 0.55), FACE, **NS)

# legs: short, bent, long dark feet
for s in (1, -1):
    with m.bone(f"Leg_{LR(s)}", (-0.05, s * 0.6, 1.6)):
        m.seg(f"Thigh{s}", V(-0.1, s * 0.6, 1.65), V(0.35, s * 0.78, 0.95), 0.82, 0.68, FUR)
        m.seg(f"Shin{s}", V(0.35, s * 0.78, 1.0), V(0.0, s * 0.8, 0.32), 0.66, 0.54, FUR_D)
        m.box(f"Foot{s}", (0.3, s * 0.82, 0.18), (1.05, 0.62, 0.36), SKIN, top=(0.9, 0.9), **NS)
        for k in range(3):
            m.box(f"Toe{s}{k}", (0.88, s * 0.82 + (k - 1) * 0.19, 0.12), (0.22, 0.16, 0.22), SKIN, **NS)

# arms: right hangs long to the knee, left raised holding the banana out to the side
with m.bone("Arm_R", (0.15, -1.05, 3.2)):
    m.box("ShoulderR", (0.15, -1.05, 3.15), (0.75, 0.6, 0.75), FUR)
    m.seg("UpperArmR", V(0.15, -1.1, 3.1), V(0.3, -1.45, 2.2), 0.6, 0.52, FUR)
    m.seg("ForearmR", V(0.3, -1.45, 2.25), V(0.55, -1.5, 1.2), 0.52, 0.46, FUR_D)
    m.box("HandR", (0.6, -1.5, 0.95), (0.55, 0.42, 0.62), SKIN, top=(0.9, 0.9), **NS)
with m.bone("Arm_L", (0.15, 1.05, 3.2)):
    m.box("ShoulderL", (0.15, 1.05, 3.15), (0.75, 0.6, 0.75), FUR)
    m.seg("UpperArmL", V(0.15, 1.1, 3.1), V(0.45, 1.62, 2.2), 0.6, 0.52, FUR)
    m.seg("ForearmL", V(0.45, 1.62, 2.25), V(1.0, 1.65, 2.75), 0.52, 0.46, FUR_D)
    h = V(1.12, 1.68, 2.82)
    m.box("HandL", h, (0.5, 0.5, 0.55), SKIN, **NS)
    pts = [h + V(-0.05, 0, -0.45), h + V(0.08, 0.05, 0.25), h + V(0.2, 0.18, 0.8), h + V(0.18, 0.36, 1.25)]
    m.box("BananaStem", pts[0] + V(0, 0, -0.1), (0.16, 0.16, 0.25), BAN_D, **NS)
    m.seg("Banana0", pts[0], pts[1], 0.36, 0.42, BAN)
    m.seg("Banana1", pts[1], pts[2], 0.42, 0.38, BAN)
    m.seg("Fruit", pts[2] - (pts[2] - pts[1]) * 0.1, pts[3], 0.32, 0.22, FRUIT, **NS)
    m.box("FruitTip", pts[3] + V(0, 0.02, 0.05), (0.18, 0.18, 0.14), lt(BAN_D, 0.4), **NS)
    for k, a in enumerate((0.0, 2.1, 4.2)):                 # peel flaps hanging down from the peel line
        d = V(math.cos(a), math.sin(a), 0)
        b = pts[2] + d * 0.18
        m.slab(f"Peel{k}", [(-0.18, 0), (0.18, 0), (0.12, -0.75), (0, -0.85), (-0.12, -0.75)], 0.08, BAN,
               origin=b, xaxis=(-math.sin(a), math.cos(a), 0), yaxis=(d * 0.45 + V(0, 0, 1)).normalized())

# tail: long, curling up behind into a question mark
pts = [V(-0.62, 0, 1.65), V(-1.35, 0, 1.5), V(-2.0, 0, 1.95), V(-2.3, 0, 2.75), V(-2.15, 0, 3.55), V(-1.7, 0, 3.9),
       V(-1.3, 0, 3.6)]
m.chain("Tail", pts, [0.44, 0.4, 0.38, 0.35, 0.32, 0.28, 0.24], FUR, bones="Tail")
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
