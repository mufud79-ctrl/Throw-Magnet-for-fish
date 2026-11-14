"""TFFA Camel (Desert, Cannon Tame) - hero build: a grumpy caravan dromedary.

Reference analysis (a dromedary in a desert caravan, most important first):
1. Silhouette: tall on long knobbly legs, ONE big hump as the highest point of the body, a long neck that dips down in a
   U from the chest and rises to a head held high and forward, thin tail with a tuft.
2. Head: long head with a heavy droopy split upper lip, buck teeth showing, slit nostrils, half-closed unimpressed eyes
   under heavy lids with long lashes (the camel's famous grumpy look), small round ears, a tuft of hair on top.
3. Signature: a colourful woven saddle blanket draped over the hump (red with gold + teal stripes, gold tassels),
   shaggy hair on the throat and hump, calloused knees, wide two-toed foot pads.
4. Colours: sandy tan + darker shag, cream muzzle, red/gold/teal blanket.
Bones: Body, Neck, Head, Jaw, Ear_L/R, Leg_FL/FR/BL/BR, Tail1..2. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

TAN, TAN_D, CREAM, PAD = rgb(214, 164, 100), rgb(164, 116, 66), rgb(238, 208, 160), rgb(120, 86, 56)
RED, GOLD, TEAL, BLK = rgb(200, 40, 44), rgb(255, 196, 40), rgb(36, 150, 160), rgb(30, 24, 22)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Camel", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.45, chamfer=0.16, jitter=0.06)
m.gait = {"amp": 0.75}

body = m.bone("Body", (0, 0, 4.6)); body.__enter__()
m.box("Chest", (1.0, 0, 4.6), (2.4, 1.95, 2.1), TAN, top=(0.82, 0.86), bot=(0.72, 0.84))
m.box("Waist", (-0.5, 0, 4.75), (1.6, 1.75, 1.7), TAN, top=(0.92, 0.92), bot=(0.86, 0.9))
m.box("Hips", (-1.8, 0, 4.65), (1.8, 1.8, 1.9), TAN, top=(0.8, 0.86), bot=(0.86, 0.9))
m.box("Hump", (-0.35, 0, 6.0), (2.5, 1.55, 1.4), TAN, top=(0.5, 0.62))
m.box("HumpTop", (-0.35, 0, 6.85), (1.2, 0.9, 0.6), TAN_D, top=(0.6, 0.7))
for k in range(4):                                           # shag on the hump crest
    b = V(0.2 - k * 0.38, (k % 2 - 0.5) * 0.4, 7.1)
    m.spike(f"HumpShag{k}", b, b + V(-0.45, 0, 0.45), 0.24, TAN_D, flat=0.55)
# woven saddle blanket draped over the hump
m.box("Blanket", (-0.35, 0, 5.75), (2.7, 2.08, 1.0), RED, top=(0.62, 0.78), **NS)
for s in (1, -1):
    m.box(f"BlanketSide{s}", (-0.35, s * 1.0, 4.85), (2.5, 0.12, 1.25), RED, **NS)
    m.box(f"Stripe{s}", (-0.35, s * 1.07, 5.0), (2.5, 0.06, 0.18), GOLD, **NS)
    m.box(f"StripeT{s}", (-0.35, s * 1.07, 4.62), (2.5, 0.06, 0.14), TEAL, **NS)
    for k in range(5):                                       # gold tassels
        x = -1.45 + k * 0.55
        m.seg(f"TasselCord{s}{k}", V(x, s * 1.03, 4.25), V(x, s * 1.05, 3.85), 0.06, 0.06, GOLD, **NS)
        m.box(f"Tassel{s}{k}", (x, s * 1.05, 3.75), (0.18, 0.18, 0.26), GOLD, top=(0.6, 0.6), **NS)

for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (1.3, s * 0.75, 4.3)):
        m.box(f"Shoulder{s}", (1.3, s * 0.82, 4.2), (1.1, 0.5, 1.4), TAN, top=(0.8, 0.8), bot=(0.8, 0.85))
        m.seg(f"Upper{s}", V(1.35, s * 0.82, 4.0), V(1.5, s * 0.82, 2.25), 0.82, 0.62, TAN)
        m.box(f"Knee{s}", (1.5, s * 0.82, 2.2), (0.55, 0.55, 0.5), PAD, top=(0.85, 0.85))
        m.seg(f"Lower{s}", V(1.5, s * 0.82, 2.2), V(1.55, s * 0.82, 0.4), 0.58, 0.52, TAN)
        m.box(f"Foot{s}", (1.7, s * 0.82, 0.18), (0.95, 0.8, 0.36), PAD, top=(0.88, 0.9))
        m.box(f"ToeSplit{s}", (2.05, s * 0.82, 0.2), (0.3, 0.06, 0.3), BLK, **NS)
    with m.bone(f"Leg_B{LR(s)}", (-1.9, s * 0.75, 4.5)):
        m.box(f"Thigh{s}", (-1.95, s * 0.82, 3.9), (1.3, 0.62, 1.9), TAN, rot=Ry(-0.25), top=(0.85, 0.9), bot=(0.6, 0.7))
        m.seg(f"Shin{s}", V(-2.2, s * 0.84, 3.15), V(-1.95, s * 0.84, 0.4), 0.62, 0.52, TAN)
        m.box(f"Hock{s}", (-2.15, s * 0.84, 2.45), (0.5, 0.52, 0.45), PAD, **NS)
        m.box(f"HFoot{s}", (-1.8, s * 0.84, 0.18), (0.95, 0.8, 0.36), PAD, top=(0.88, 0.9))
pts = [V(-2.7, 0, 5.1), V(-2.95, 0, 4.3), V(-2.95, 0, 3.5)]
m.chain("Tail", pts, [0.22, 0.18, 0.16], TAN_D, bones="Tail")
with m.bone("Tail2"):
    m.box("TailTuft", (-2.95, 0, 3.25), (0.32, 0.32, 0.6), PAD, top=(0.5, 0.5), bot=(0.8, 0.8))

# neck: dips down in a U from the chest, then rises to the head
with m.bone("Neck", (1.9, 0, 4.9)):
    m.seg("NeckLow", V(1.7, 0, 5.0), V(2.75, 0, 4.55), 1.15, 1.0, TAN, d0=1.3, d1=1.0)
    m.seg("NeckUp", V(2.6, 0, 4.45), V(3.35, 0, 6.15), 1.0, 0.85, TAN, d0=1.05, d1=0.9)
    for k in range(4):                                       # throat shag
        b = V(2.4 + k * 0.25, 0, 4.15 + k * 0.32)
        m.spike(f"Throat{k}", b, b + V(-0.1, 0, -0.55), 0.26, TAN_D, flat=0.6)
with m.bone("Head", (3.3, 0, 6.1), "Neck"), m.frame(pivot=(3.3, 0, 6.1), scale=1.4):
    hc = V(3.6, 0, 6.5)
    m.box("Head", hc, (1.15, 1.0, 0.95), TAN, top=(0.8, 0.85), bot=(0.9, 0.9))
    m.spike("HeadTuft", hc + V(-0.2, 0, 0.45), hc + V(-0.45, 0, 0.95), 0.26, TAN_D, flat=0.6)
    m.box("Muzzle", hc + V(0.95, 0, -0.18), (1.0, 0.82, 0.72), CREAM, top=(0.85, 0.9))
    for s in (1, -1):                                        # heavy droopy split upper lip
        m.box(f"Lip{s}", hc + V(1.42, s * 0.2, -0.42), (0.42, 0.38, 0.4), CREAM, top=(0.9, 0.9), bot=(0.75, 0.8))
        m.box(f"Nostril{s}", hc + V(1.47, s * 0.24, 0.08), (0.06, 0.08, 0.24), BLK, rot=Rx(s * 0.4), **NS)
        with m.bone(f"Ear_{LR(s)}", hc + V(-0.35, s * 0.45, 0.35)):
            m.box(f"Ear{s}", hc + V(-0.4, s * 0.55, 0.4), (0.25, 0.3, 0.32), TAN_D, top=(0.6, 0.6))
    m.box("LipSplit", hc + V(1.64, 0, -0.42), (0.08, 0.06, 0.35), PAD, **NS)
    for s in (1, -1):
        m.box(f"BuckTooth{s}", hc + V(1.5, s * 0.1, -0.68), (0.14, 0.16, 0.2), TOOTH, **NS)
    m.eyes(tuple(hc + V(0.2, 0.52, 0.12)), facing=(0.35, 1, 0), size=(0.44, 0.36), pupil=0.7, look=(0.4, -0.2), angry=-0.15,
           brow_col=TAN_D, brow_h=0.62, brow_up=0.36, brow_w=1.25, depth=0.12)          # heavy half-closed lids
    for s in (1, -1):
        for k in range(3):                                   # long lashes under the lid
            m.box(f"Lash{s}{k}", hc + V(0.06 + k * 0.13, s * 0.6, 0.12), (0.04, 0.06, 0.16), BLK, rot=Rx(s * 0.5), **NS)
    with m.bone("Jaw", hc + V(0.6, 0, -0.45)):
        m.box("Jaw", hc + V(1.05, 0, -0.62), (0.9, 0.62, 0.32), CREAM, top=(0.95, 0.95))
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
