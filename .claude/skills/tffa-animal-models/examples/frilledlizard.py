"""TFFA Lizard (Desert, Cannon Tame) - hero build: a frilled lizard in full threat display.

Reference analysis (the frilled lizard's famous display, most important first):
1. Silhouette: low sprawling lizard with the FRONT RAISED on straight forelegs, head up, and a huge round frill flared open
   around the neck like an umbrella - the frill is wider than the body is long-ways tall and reads from every side;
   a long whip tail curving off to one side.
2. Head: wedge head with the mouth GAPING wide open (pale yellow-pink inside, a pink tongue, small pointed teeth),
   yellow eyes under angry brows.
3. Signature: the frill - red rim, orange middle, yellow centre, dark radial ribs like umbrella spokes; a row of small
   spikes down the spine; banded tail; long splayed toes.
4. Colours: sandy brown + darker bands, pale belly, red/orange/yellow frill, pale yellow mouth.
Bones: Body, Neck, Head, Jaw, Leg_FL/FR/BL/BR, Tail1..5. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

SKIN, SKIN_D, BELLY = rgb(184, 140, 84), rgb(122, 88, 50), rgb(226, 198, 146)
FR_R, FR_O, FR_Y, RIB = rgb(214, 50, 38), rgb(246, 128, 40), rgb(252, 208, 70), rgb(112, 36, 28)
MOUTHY, EYE = rgb(250, 202, 130), rgb(255, 204, 40)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Lizard", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.38, chamfer=0.16, jitter=0.06)

body = m.bone("Body", (0, 0, 1.2)); body.__enter__()
m.seg("Chest", V(-0.3, 0, 1.05), V(1.2, 0, 1.55), 1.35, 1.2, SKIN, d0=0.95, d1=1.0)
m.seg("Hips", V(-1.5, 0, 0.95), V(-0.2, 0, 1.05), 1.15, 1.35, SKIN, d0=0.8, d1=0.95)
m.box("Belly", (-0.2, 0, 0.62), (2.4, 0.95, 0.2), BELLY, rot=Ry(-0.1), **NS)
for k in range(7):                                           # spine spikes + dark bands
    x = 1.0 - k * 0.38; z = 1.55 + (x + 0.3) * 0.3 if x > -0.3 else 1.48 + (x + 0.3) * 0.05
    m.spike(f"Spine{k}", (x, 0, z + 0.4), (x - 0.25, 0, z + 0.78), 0.14, SKIN_D, flat=0.5)
    if k % 2 == 0:
        m.box(f"Band{k}", (x, 0, z + 0.3), (0.22, 1.15, 0.12), SKIN_D, rot=Ry(-0.25), **NS)
for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (0.9, s * 0.55, 1.4)):
        m.seg(f"Arm{s}", V(0.9, s * 0.55, 1.4), V(1.05, s * 1.15, 0.95), 0.45, 0.38, SKIN)
        m.seg(f"Forearm{s}", V(1.05, s * 1.15, 1.0), V(1.25, s * 1.25, 0.2), 0.38, 0.32, SKIN)
        for k, a in enumerate((-0.5, 0.0, 0.5, 1.0)):
            b = V(1.25, s * 1.25, 0.12)
            m.spike(f"Finger{s}{k}", b, b + V(math.cos(a) * 0.55, s * math.sin(a) * 0.55, -0.06), 0.07, SKIN_D, flat=0.6)
    with m.bone(f"Leg_B{LR(s)}", (-1.1, s * 0.5, 1.0)):
        m.seg(f"Thigh{s}", V(-1.1, s * 0.5, 1.0), V(-0.75, s * 1.35, 0.85), 0.55, 0.45, SKIN)
        m.seg(f"Shin{s}", V(-0.75, s * 1.35, 0.9), V(-1.0, s * 1.45, 0.18), 0.42, 0.34, SKIN)
        for k, a in enumerate((-0.3, 0.15, 0.6, 1.05)):
            b = V(-1.0, s * 1.45, 0.12)
            m.spike(f"Toe{s}{k}", b, b + V(math.cos(a) * 0.7, s * math.sin(a) * 0.7, -0.06), 0.07, SKIN_D, flat=0.6)

pts = [V(-1.4, 0, 0.95), V(-2.4, 0.25, 0.7), V(-3.35, 0.8, 0.45), V(-4.1, 1.55, 0.35), V(-4.6, 2.35, 0.3), V(-4.85, 3.05, 0.28)]
ws = [0.85, 0.65, 0.48, 0.34, 0.22, 0.1]
m.chain("Tail", pts, ws, SKIN, bones="Tail")
for i in range(1, 5):
    with m.bone(f"Tail{i + 1}"):
        q = pts[i].lerp(pts[i + 1], 0.45)
        m.box(f"TailBand{i}", q + V(0, 0, ws[i] * 0.3), (ws[i] * 0.55, ws[i] * 1.05, ws[i] * 0.55), SKIN_D, **NS)

with m.bone("Neck", (1.2, 0, 1.6)):
    m.seg("Neck", V(1.1, 0, 1.55), V(1.85, 0, 2.05), 0.95, 0.85, SKIN, d0=0.9, d1=0.8)
with m.bone("Head", (1.8, 0, 2.05), "Neck"):
    # the frill: an umbrella collar flared open round the neck, facing forward
    o = V(1.75, 0, 2.15)
    def disc(nm, R, r2, col, dx, n=16):
        P = [((R if k % 2 == 0 else r2) * math.cos(2 * math.pi * k / n), (R if k % 2 == 0 else r2) * math.sin(2 * math.pi * k / n))
             for k in range(n)]
        m.slab(nm, P, 0.12, col, origin=o + V(dx, 0, 0), xaxis=(0, 1, 0), yaxis=(0.25, 0, 1), chamfer=0.3)
    disc("FrillRed", 1.9, 1.62, FR_R, 0.0)
    disc("FrillOrange", 1.45, 1.3, FR_O, 0.1)
    disc("FrillYellow", 0.95, 0.9, FR_Y, 0.2)
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8; d = V(0.25 * math.sin(a) * 0.24, math.cos(a), math.sin(a)).normalized()
        m.seg(f"Rib{k}", o + V(0.26, 0, 0) + d * 0.7, o + V(0.08, 0, 0) + d * 1.72, 0.1, 0.07, RIB, d0=0.08, d1=0.06, **NS)
    hc = V(2.35, 0, 2.2)
    m.box("Head", hc, (1.1, 0.95, 0.62), SKIN, top=(0.8, 0.85), bot=(0.9, 0.9))
    m.box("Snout", hc + V(0.65, 0, -0.02), (0.6, 0.75, 0.4), SKIN, top=(0.8, 0.85))
    m.box("MouthIn", hc + V(0.45, 0, -0.35), (0.95, 0.75, 0.3), MOUTHY, **NS)
    m.teeth("ToothT", hc + V(0.9, -0.28, -0.22), hc + V(0.9, 0.28, -0.22), 4, 0.12, 0.05)
    m.eyes(tuple(hc + V(0.1, 0.47, 0.12)), facing=(0.3, 1, 0), size=(0.36, 0.32), pupil=0.75, look=(0.4, 0), angry=0.5,
           white=EYE, brow_col=SKIN_D, brow_h=0.5, brow_up=0.75, depth=0.1)
    with m.bone("Jaw", hc + V(-0.35, 0, -0.3)), m.frame(pivot=hc + V(-0.35, 0, -0.3), rot=Ry(0.6)):
        m.box("Jaw", hc + V(0.4, 0, -0.45), (1.25, 0.8, 0.25), BELLY)
        m.box("Tongue", hc + V(0.4, 0, -0.32), (0.8, 0.45, 0.08), TONGUE, **NS)
        m.teeth("ToothB", hc + V(0.95, -0.25, -0.35), hc + V(0.95, 0.25, -0.35), 3, 0.1, 0.05, down=False)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
