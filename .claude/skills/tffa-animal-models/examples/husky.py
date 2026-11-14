"""TFFA Husky (Arctic, Cannon Tame) - hero build: a lead sled dog.

Reference analysis (a Siberian husky leading a sled team, most important first):
1. Silhouette: athletic, deep-chested working dog leaning into the harness, thick neck ruff, tall pointed ears, a bushy
   tail curled up OVER the back (sickle tail), strong legs with white socks.
2. Head: the famous husky mask - dark cap with a widow's peak, white face, white "eyebrow" spots, dark eye liner;
   piercing ice-blue eyes with a determined frown, mouth open showing fangs and a tongue (working hard, not cute).
3. Signature: a bright red sled harness (chest strap, girth strap, back strap with a gold D-ring), the mask, the curled tail.
4. Colours: steel grey + dark charcoal saddle, white belly/face/socks, red harness + gold ring, ice-blue eyes.
Bones: Body, Neck, Head, Jaw, Ear_L/R, Leg_FL/FR/BL/BR, Tail1..3. Studded, muscular."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

GREY, DARK, WH, WH_D = rgb(112, 120, 136), rgb(60, 64, 78), rgb(246, 246, 250), rgb(214, 218, 228)
RED, RED_D, GOLD, ICE, BLK = rgb(220, 34, 40), rgb(160, 20, 28), rgb(255, 196, 40), rgb(110, 200, 255), rgb(26, 26, 32)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Husky", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.45, chamfer=0.16, jitter=0.05)

body = m.bone("Body", (0, 0, 3.0)); body.__enter__()
m.box("Chest", (1.2, 0, 3.0), (2.4, 2.2, 2.4), GREY, top=(0.82, 0.86), bot=(0.76, 0.84))
m.box("Waist", (-0.6, 0, 3.1), (1.8, 1.75, 1.6), GREY, top=(0.92, 0.92), bot=(0.86, 0.9))
m.box("Hips", (-2.0, 0, 3.0), (1.8, 2.0, 1.95), GREY, top=(0.82, 0.86), bot=(0.86, 0.9))
m.box("Saddle", (-0.5, 0, 3.95), (3.6, 1.55, 0.4), DARK, top=(0.7, 0.85))
m.box("Belly", (-0.3, 0, 2.15), (3.2, 1.35, 0.4), WH, **NS)
m.box("Bib", (2.25, 0, 2.9), (0.5, 1.7, 1.9), WH, rot=Ry(-0.25), top=(0.85, 0.9))
for s in (1, -1):
    m.box(f"Haunch{s}", (-2.0, s * 0.98, 2.95), (1.5, 0.3, 1.5), GREY, top=(0.8, 0.8), bot=(0.7, 0.8))
for k in range(9):                                          # thick neck ruff
    a = math.pi * (k + 0.5) / 9; y, z = math.cos(a), math.sin(a) * 0.9 - 0.1
    b = V(1.9, y * 1.0, 3.35 + z * 0.9)
    m.spike(f"Ruff{k}", b, b + V(-0.8, y * 0.55, z * 0.45), 0.42, GREY if k % 2 else WH_D, flat=0.55)
# red sled harness
m.box("HarnessGirth", (0.35, 0, 3.05), (0.42, 2.0, 2.55), RED, top=(0.72, 0.9), bot=(0.7, 0.85), **NS)
m.box("HarnessBack", (-0.9, 0, 4.12), (3.0, 0.42, 0.14), RED, **NS)
m.box("HarnessChest", (2.45, 0, 3.0), (0.16, 1.55, 0.42), RED, rot=Ry(-0.25), **NS)
for s in (1, -1):
    m.box(f"HarnessSide{s}", (1.4, s * 1.05, 3.55), (2.2, 0.12, 0.38), RED, rot=Ry(0.35), **NS)
m.box("DRing", (-2.3, 0, 4.25), (0.12, 0.5, 0.42), GOLD, **NS)
m.box("DRingHole", (-2.3, 0, 4.25), (0.14, 0.26, 0.2), RED_D, **NS)

for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (1.4, s * 0.85, 2.9)):
        m.box(f"Shoulder{s}", (1.45, s * 0.98, 2.85), (1.3, 0.55, 1.5), GREY, top=(0.8, 0.8), bot=(0.8, 0.85))
        m.seg(f"Forearm{s}", V(1.5, s * 0.98, 2.4), V(1.75, s * 1.0, 0.55), 0.85, 0.7, GREY)
        m.box(f"Sock{s}", (1.75, s * 1.0, 0.65), (0.78, 0.78, 0.9), WH, top=(0.95, 0.95))
        m.box(f"Paw{s}", (1.95, s * 1.0, 0.24), (1.05, 0.85, 0.48), WH, top=(0.85, 0.9))
        for t in (-1, 0, 1): m.spike(f"Claw{s}{t}", V(2.45, s * 1.0 + t * 0.22, 0.2), V(2.72, s * 1.0 + t * 0.24, 0.04), 0.07, BLK, flat=0.4)
    with m.bone(f"Leg_B{LR(s)}", (-2.0, s * 0.85, 3.0)):
        m.box(f"Thigh{s}", (-2.0, s * 0.98, 2.4), (1.6, 0.8, 1.9), GREY, rot=Ry(-0.3), top=(0.85, 0.9), bot=(0.65, 0.75))
        m.seg(f"Hock{s}", V(-2.5, s * 1.0, 1.75), V(-2.25, s * 1.0, 0.55), 0.68, 0.6, GREY)
        m.box(f"HSock{s}", (-2.25, s * 1.0, 0.6), (0.7, 0.7, 0.8), WH, top=(0.95, 0.95))
        m.box(f"HindPaw{s}", (-2.05, s * 1.0, 0.24), (1.0, 0.82, 0.48), WH, top=(0.85, 0.9))

# sickle tail curled over the back, white underside
pts = [V(-2.8, 0, 3.55), V(-3.35, 0, 4.4), V(-3.05, 0, 5.25), V(-2.3, 0, 5.45)]
m.chain("Tail", pts, [0.62, 0.82, 0.78, 0.5], GREY, bones="Tail")
with m.bone("Tail3"):
    m.spike("TailTip", pts[3] + V(-0.1, 0, 0), pts[3] + V(0.55, 0, -0.25), 0.36, WH, flat=0.8)
for i in range(2):
    with m.bone(f"Tail{i + 1}"):
        q = pts[i].lerp(pts[i + 1], 0.5)
        for s in (1, -1):
            m.spike(f"TailTuft{i}{s}", q + V(0, s * 0.3, 0), q + V(0.1, s * 0.75, -0.2), 0.3, WH_D, flat=0.55)

with m.bone("Neck", (2.0, 0, 3.6)):
    m.seg("Neck", V(1.7, 0, 3.6), V(2.85, 0, 4.1), 1.5, 1.3, GREY, d0=1.6, d1=1.35)
with m.bone("Head", (2.8, 0, 4.1), "Neck"), m.frame(pivot=(2.8, 0, 4.1), scale=1.1):
    hc = V(3.35, 0, 4.25)
    m.box("Head", hc, (1.45, 1.6, 1.25), WH, top=(0.84, 0.86), bot=(0.88, 0.9))
    m.box("Cap", hc + V(-0.15, 0, 0.45), (1.3, 1.62, 0.5), DARK, top=(0.78, 0.84))
    m.spike("WidowPeak", hc + V(0.5, 0, 0.6), hc + V(0.8, 0, 0.12), 0.32, DARK, flat=0.4)
    for s in (1, -1):
        m.box(f"CheekDark{s}", hc + V(-0.25, s * 0.78, 0.0), (0.95, 0.1, 0.55), DARK, **NS)
        m.box(f"BrowSpot{s}", hc + V(0.66, s * 0.4, 0.42), (0.1, 0.24, 0.16), WH, **NS)
    m.box("Snout", hc + V(1.05, 0, -0.3), (1.05, 0.88, 0.6), WH, top=(0.8, 0.88), bot=(0.92, 0.92))
    m.box("Nose", hc + V(1.6, 0, -0.08), (0.16, 0.42, 0.28), BLK, bot=(0.9, 0.6), **NS)
    m.box("Maw", hc + V(1.0, 0, -0.68), (0.95, 0.7, 0.26), MOUTH, **NS)
    for t in (1, -1):
        m.spike(f"Fang{t}", hc + V(1.42, t * 0.3, -0.6), hc + V(1.45, t * 0.3, -0.98), 0.08, TOOTH, flat=0.35)
        m.spike(f"Tooth{t}", hc + V(1.15, t * 0.36, -0.6), hc + V(1.16, t * 0.36, -0.82), 0.06, TOOTH, flat=0.3)
    m.eyes(tuple(hc + V(0.69, 0.42, 0.12)), facing=(0.9, 0.4, 0), size=(0.46, 0.32), pupil=0.75, look=(0.5, 0), angry=0.4,
           white=ICE, brow_col=DARK, brow_h=0.5, brow_up=0.78, depth=0.12)
    for s in (1, -1):
        with m.bone(f"Ear_{LR(s)}", hc + V(-0.25, s * 0.5, 0.65)):
            m.spike(f"Ear{s}", hc + V(-0.25, s * 0.52, 0.6), hc + V(-0.45, s * 0.66, 1.6), 0.4, DARK, flat=0.6)
            m.spike(f"EarIn{s}", hc + V(-0.13, s * 0.53, 0.68), hc + V(-0.33, s * 0.65, 1.35), 0.22, WH, flat=0.5)
    with m.bone("Jaw", hc + V(0.3, 0, -0.6)), m.frame(pivot=hc + V(0.3, 0, -0.6), rot=Ry(0.32)):
        m.box("Jaw", hc + V(0.95, 0, -0.9), (1.05, 0.72, 0.28), WH)
        m.box("Tongue", hc + V(1.15, 0.18, -0.85), (1.05, 0.42, 0.1), TONGUE, **NS)
        m.box("TongueTip", hc + V(1.65, 0.22, -1.0), (0.3, 0.38, 0.32), TONGUE, rot=Ry(0.9), **NS)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
