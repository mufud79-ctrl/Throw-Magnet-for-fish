"""TFFA GiantSloth (Ice Age, Cannon Tame) - hero build: Megatherium reared up on its hind legs.

Reference analysis (the classic Megatherium museum/paleo-art pose, most important first):
1. Silhouette: a towering pear - reared up on stout hind legs, braced on a thick tail like a tripod, a massive pot belly,
   long heavy arms raised outward with enormous curved claws (the threat display), small head on a thick neck at the top.
2. Head: a long narrow head with a tapering muzzle and a prehensile upper lip, small fierce eyes under heavy brows,
   a heavy jaw, small ears hidden in fur.
3. Signature: the THREE huge hooked claws on each hand (as long as the forearm), shaggy fur hanging off the arms, back
   and belly sides, frost on the shoulders, huge clawed feet turned inward.
4. Colours: earthy ochre-brown + darker shag, tan face and belly, ivory claws, frost white.
Bones: Body, Neck, Head, Arm_L/R, Leg_L/R, Tail1..2 (biped). Studded, fierce + muscular."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

FUR, FUR_D, TAN, CLAWC, FROST, BLK = rgb(168, 124, 80), rgb(118, 82, 50), rgb(212, 176, 128), rgb(236, 222, 190), rgb(232, 244, 255), rgb(30, 24, 22)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("GiantSloth", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.55, chamfer=0.17, jitter=0.07)
m.gait = {"amp": 0.6}

body = m.bone("Body", (0, 0, 3.4)); body.__enter__()
m.box("Hips", (-0.3, 0, 2.6), (2.8, 3.4, 2.2), FUR, top=(0.95, 0.95), bot=(0.85, 0.85))
m.seg("Torso", V(-0.3, 0, 2.8), V(0.2, 0, 6.6), 3.6, 2.6, FUR, d0=3.0, d1=2.2)
m.box("Belly", (1.05, 0, 3.8), (0.6, 2.6, 2.8), TAN, rot=Ry(-0.08), top=(0.8, 0.85), bot=(0.85, 0.85))
m.box("Shoulders", (0.15, 0, 6.4), (2.4, 3.6, 1.5), FUR, top=(0.75, 0.8))
for s in (1, -1):
    m.box(f"Frost{s}", (0.1, s * 1.2, 7.18), (1.4, 1.0, 0.18), FROST, **NS)
    for k in range(5):                                       # shag hanging off the flanks and back
        b = V(-0.9 + k * 0.1, s * (1.55 - k * 0.05), 6.0 - k * 0.75)
        m.spike(f"Shag{s}{k}", b, b + V(-0.35, s * 0.35, -1.0), 0.45, FUR_D if k % 2 else FUR, flat=0.55)
for k in range(4):
    b = V(-1.25, (k - 1.5) * 0.7, 5.6 - k * 0.2)
    m.spike(f"BackShag{k}", b, b + V(-0.5, 0, -1.1), 0.45, FUR_D, flat=0.55)
pts = [V(-1.2, 0, 2.3), V(-2.4, 0, 1.2), V(-3.3, 0, 0.45)]
m.chain("Tail", pts, [1.6, 1.15, 0.75], FUR, bones="Tail")

for s in (1, -1):
    with m.bone(f"Leg_{LR(s)}", (-0.2, s * 1.2, 2.3)):
        m.box(f"Thigh{s}", (-0.1, s * 1.35, 1.8), (2.0, 1.4, 2.0), FUR, top=(0.85, 0.85), bot=(0.75, 0.8))
        m.seg(f"Shin{s}", V(0.05, s * 1.4, 1.2), V(0.15, s * 1.45, 0.35), 1.3, 1.2, FUR_D)
        m.box(f"Foot{s}", (0.45, s * 1.45, 0.3), (1.8, 1.3, 0.6), FUR_D, rot=Rz(s * 0.15), top=(0.85, 0.9))
        for t in (-1, 0, 1):
            b = V(1.3, s * 1.45 + t * 0.38, 0.28)
            m.spike(f"FootClaw{s}{t}", b, b + V(0.45, 0, -0.22), 0.12, CLAWC, flat=0.5)
    with m.bone(f"Arm_{LR(s)}", (0.3, s * 1.75, 6.4)):   # arms raised outward, huge claws (threat display)
        m.box(f"Deltoid{s}", (0.3, s * 1.85, 6.4), (1.5, 1.2, 1.5), FUR, top=(0.8, 0.8))
        el, wr = V(0.9, s * 2.9, 6.0), V(1.7, s * 3.3, 7.3)
        m.seg(f"UpperArm{s}", V(0.3, s * 1.95, 6.3), el, 1.25, 1.05, FUR)
        m.seg(f"Forearm{s}", el, wr, 1.05, 0.9, FUR)
        for k in range(2):
            b = el.lerp(wr, 0.3 + 0.4 * k)
            m.spike(f"ArmShag{s}{k}", b, b + V(-0.5, s * 0.25, -0.9), 0.32, FUR_D, flat=0.55)
        m.box(f"Hand{s}", wr + V(0.2, 0, 0.35), (0.9, 0.95, 0.75), FUR_D, top=(0.85, 0.9))
        for t in (-1, 0, 1):                                 # three enormous hooked claws, curving forward + down
            b = wr + V(0.45, t * 0.3, 0.75)
            p1, p2 = b + V(0.55, t * 0.08, 0.75), b + V(1.35, t * 0.12, 0.65)
            m.seg(f"Claw{s}{t}", b, p1, 0.26, 0.2, CLAWC, **NS)
            m.seg(f"ClawMid{s}{t}", p1, p2, 0.2, 0.14, CLAWC, **NS)
            m.spike(f"ClawTip{s}{t}", p2, p2 + V(0.4, 0, -0.55), 0.08, CLAWC, flat=0.6)

with m.bone("Neck", (0.3, 0, 6.9)):
    m.seg("Neck", V(0.2, 0, 6.8), V(0.75, 0, 7.8), 1.7, 1.4, FUR, d0=1.6, d1=1.3)
with m.bone("Head", (0.7, 0, 7.8), "Neck"), m.frame(pivot=(0.7, 0, 7.8), scale=1.45):
    hc = V(1.15, 0, 8.15)
    m.box("Head", hc, (1.5, 1.35, 1.2), FUR, top=(0.8, 0.85), bot=(0.88, 0.9))
    m.box("Muzzle", hc + V(1.0, 0, -0.2), (0.95, 0.95, 0.8), TAN, top=(0.8, 0.85), bot=(0.88, 0.9))
    m.box("Lip", hc + V(1.55, 0, -0.1), (0.35, 0.6, 0.45), TAN, top=(0.7, 0.8))
    m.box("Nose", hc + V(1.72, 0, 0.05), (0.08, 0.32, 0.16), BLK, **NS)
    m.box("Mouth", hc + V(1.2, 0, -0.52), (0.8, 0.82, 0.06), BLK, **NS)
    m.box("Brow", hc + V(0.35, 0, 0.55), (0.55, 1.4, 0.32), FUR_D, top=(0.75, 0.9))
    m.eyes(tuple(hc + V(0.62, 0.48, 0.22)), facing=(0.8, 0.6, 0), size=(0.42, 0.3), pupil=0.72, look=(0.5, 0), angry=0.55,
           brow_col=BLK, brow_h=0.6, brow_up=0.75, depth=0.12)
    for s in (1, -1):
        m.box(f"Ear{s}", hc + V(-0.4, s * 0.7, 0.35), (0.3, 0.22, 0.3), FUR_D, **NS)
    for k in range(3):
        b = hc + V(-0.2 - k * 0.25, (k - 1) * 0.35, 0.6)
        m.spike(f"HeadShag{k}", b, b + V(-0.5, 0, 0.35), 0.24, FUR_D, flat=0.55)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
