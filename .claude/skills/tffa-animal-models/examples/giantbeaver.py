"""TFFA GiantBeaver (Ice Age, Cannon Tame) - hero build: Castoroides, the bear-sized beaver.

Reference analysis (Castoroides on a riverbank in paleo-art, most important first):
1. Silhouette: a huge hunched round body (bear-sized), short legs, a big blunt head held forward, and a broad FLAT scaly
   paddle tail lying on the ground behind - the tail is a third of the body length.
2. Head: broad blunt head with a big muzzle, small round ears, small fierce eyes under heavy brows, black nose,
   whiskers, and the signature: HUGE ORANGE INCISORS, long and chisel-shaped, top and bottom.
3. Signature: the incisors, the scaly paddle tail (dark with a cross-hatched scale pattern), big webbed hind feet,
   a gnawed stick of wood held in the front paws.
4. Colours: rich chestnut brown + darker back, lighter belly/muzzle, orange teeth, dark grey tail and feet.
Bones: Body, Head, Ear_L/R, Leg_FL/FR/BL/BR, Tail1..2. Studded, fierce."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

FUR, FUR_D, BELLY, MUZ = rgb(132, 84, 50), rgb(94, 58, 34), rgb(172, 124, 82), rgb(184, 140, 100)
TEETH, TAILC, TAIL_L, WOOD, WOOD_L, BLK = rgb(246, 140, 36), rgb(66, 60, 62), rgb(104, 96, 98), rgb(120, 84, 50), rgb(232, 200, 150), rgb(28, 24, 24)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("GiantBeaver", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.5, chamfer=0.17, jitter=0.06)
m.gait = {"amp": 0.75}

body = m.bone("Body", (0, 0, 2.2)); body.__enter__()
m.box("Hips", (-0.9, 0, 2.15), (2.5, 3.0, 2.8), FUR, top=(0.78, 0.82), bot=(0.86, 0.86))
m.box("Chest", (0.85, 0, 2.3), (2.2, 2.7, 2.6), FUR, top=(0.8, 0.84), bot=(0.82, 0.86))
m.box("Back", (-0.4, 0, 3.65), (3.0, 1.6, 0.45), FUR_D, top=(0.7, 0.8))
m.box("Belly", (0.9, 0, 1.75), (1.0, 1.8, 1.6), BELLY, rot=Ry(-0.15), top=(0.85, 0.85))
for s in (1, -1):
    for k in range(3):
        b = V(0.6 - k * 0.8, s * 1.42, 3.1)
        m.spike(f"Shag{s}{k}", b, b + V(-0.5, s * 0.3, -0.6), 0.3, FUR_D, flat=0.55)

for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (1.3, s * 1.0, 2.0)):
        m.seg(f"Arm{s}", V(1.3, s * 1.05, 2.0), V(1.85, s * 0.8, 1.1), 0.75, 0.65, FUR)
        m.box(f"Paw{s}", (2.0, s * 0.62, 1.05), (0.6, 0.55, 0.55), FUR_D, **NS)
    with m.bone(f"Leg_B{LR(s)}", (-1.2, s * 1.2, 1.8)):
        m.box(f"Thigh{s}", (-1.1, s * 1.35, 1.3), (1.6, 0.8, 1.6), FUR, top=(0.85, 0.85), bot=(0.75, 0.8))
        m.box(f"Foot{s}", (-0.5, s * 1.4, 0.2), (1.9, 1.2, 0.4), TAILC, top=(0.9, 0.9))
        for t in (-1.5, -0.5, 0.5, 1.5):                     # webbed toes
            m.box(f"Toe{s}{t}", (0.5, s * 1.4 + t * 0.3, 0.17), (0.35, 0.24, 0.3), TAILC, **NS)
# gnawed stick held in both front paws
m.seg("Stick", V(2.15, -1.3, 1.05), V(2.15, 1.3, 1.25), 0.36, 0.32, WOOD, d0=0.36, d1=0.32)      # on Body: both paws swing around it
m.box("Gnaw", (2.15, 0.05, 1.15), (0.42, 0.55, 0.28), WOOD_L, **NS)
for k, y in enumerate((-0.9, 0.8)):
    m.spike(f"Twig{k}", (2.15, y, 1.2), (2.4, y + 0.2, 1.75), 0.08, WOOD, flat=0.8)
    m.box(f"Leaf{k}", (2.45, y + 0.22, 1.85), (0.3, 0.12, 0.22), rgb(110, 160, 70), **NS)

# broad flat scaly paddle tail lying on the ground
with m.bone("Tail1", (-2.1, 0, 1.6)):
    m.seg("TailBase", V(-2.0, 0, 1.6), V(-2.7, 0, 0.6), 1.2, 1.1, FUR_D)
with m.bone("Tail2", (-2.7, 0, 0.55), "Tail1"):
    c = V(-3.85, 0, 0.32)
    m.box("Paddle", c, (2.4, 1.9, 0.38), TAILC, top=(0.92, 0.92))
    for k in range(5):
        m.box(f"ScaleX{k}", c + V(-0.9 + k * 0.45, 0, 0.2), (0.06, 1.7, 0.04), TAIL_L, **NS)
    for k in range(3):
        m.box(f"ScaleY{k}", c + V(0, -0.55 + k * 0.55, 0.2), (2.2, 0.06, 0.04), TAIL_L, **NS)

with m.bone("Head", (2.0, 0, 2.7)), m.frame(pivot=(2.0, 0, 2.7), scale=1.15):
    hc = V(2.5, 0, 2.85)
    m.box("Head", hc, (1.6, 1.95, 1.5), FUR, top=(0.8, 0.85), bot=(0.88, 0.9))
    m.box("Muzzle", hc + V(0.95, 0, -0.32), (0.8, 1.45, 0.9), MUZ, top=(0.85, 0.85), bot=(0.9, 0.9))
    m.box("Nose", hc + V(1.38, 0, 0.0), (0.12, 0.5, 0.3), BLK, bot=(0.9, 0.6), **NS)
    for s in (1, -1):
        m.box(f"Incisor{s}", hc + V(1.3, s * 0.17, -0.95), (0.16, 0.3, 0.75), TEETH, top=(0.9, 1.0), **NS)
        m.box(f"IncisorB{s}", hc + V(1.22, s * 0.13, -1.38), (0.14, 0.24, 0.32), TEETH, **NS)
        for k in range(3):
            b = hc + V(1.35, s * 0.55, -0.25 - k * 0.12)
            m.seg(f"Whisker{s}{k}", b, b + V(0.1, s * 0.7, 0.15 - k * 0.15), 0.04, 0.03, rgb(240, 236, 228), **NS)
        with m.bone(f"Ear_{LR(s)}", hc + V(-0.4, s * 0.85, 0.55)):
            m.box(f"Ear{s}", hc + V(-0.4, s * 0.9, 0.6), (0.4, 0.35, 0.42), FUR_D, top=(0.7, 0.7))
    m.box("Chin", hc + V(0.85, 0, -0.95), (0.6, 0.8, 0.35), MUZ)
    m.eyes(tuple(hc + V(0.66, 0.6, 0.3)), facing=(0.8, 0.6, 0), size=(0.44, 0.32), pupil=0.75, look=(0.5, 0), angry=0.5,
           brow_col=BLK, brow_h=0.55, brow_up=0.75, depth=0.12)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
