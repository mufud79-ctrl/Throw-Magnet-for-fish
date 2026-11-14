"""TFFA SnowOwl (Arctic, Cannon Tame) - hero build: a snowy owl landing with its wings raised.

Reference analysis (a snowy owl mid-landing, the classic wildlife-poster shot, most important first):
1. Silhouette: a round white body with a BIG round head, both wings raised high in a wide V (tips above the head) so the
   wingspan is ~2x the body width, thick feathered legs reaching down with black talons spread.
2. Head: flat facial disc, piercing golden-yellow eyes with a hard glare (heavy brows angled down), a small black hooked
   beak half-buried in the face feathers, tiny ear tufts.
3. Signature: pure white plumage with black bars/speckles - few on the face, more on the wings, with dark wing tips;
   fluffy feathered "boots" on the legs.
4. Colours: snow white + cool grey shadow, black barring, golden eyes, black beak + talons.
Bones: Body, Head, Wing_L/R, Leg_L/R, Tail1 (walk + fly). Studded body, feather blades unstudded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

WH, WH_D, GREY, BAR = rgb(250, 250, 252), rgb(212, 218, 230), rgb(150, 156, 172), rgb(44, 44, 54)
GOLD, BLK = rgb(255, 204, 40), rgb(28, 28, 34)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("SnowOwl", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.42, chamfer=0.16, jitter=0.04)

def feather(name, root, d, L, w, grad, side):
    d = V(*d).normalized(); sd = V(*side); sd = (sd - d * sd.dot(d)).normalized()
    pts = [(0, 0), (w / 2, L * 0.15), (w * 0.45, L * 0.8), (0, L), (-w * 0.45, L * 0.8), (-w / 2, L * 0.15)]
    m.slab(name, pts, 0.14, grad[0], origin=root, xaxis=sd, yaxis=d, grad=grad, chamfer=0.3)

body = m.bone("Body", (0, 0, 2.2)); body.__enter__()
m.seg("Body", V(-0.25, 0, 0.95), V(0.05, 0, 3.0), 2.2, 1.95, WH, d0=2.0, d1=1.8)
m.box("Chest", (0.6, 0, 2.1), (0.5, 1.7, 1.8), WH, top=(0.85, 0.85), bot=(0.8, 0.85))
for k, (y, z) in enumerate(((0.45, 2.4), (-0.35, 2.1), (0.1, 1.7), (-0.55, 1.45), (0.55, 1.25), (-0.1, 2.75))):  # chest bars
    m.box(f"ChestBar{k}", (0.88, y, z), (0.08, 0.36, 0.1), BAR, rot=Rx(0.25 * (k % 2 * 2 - 1)), **NS)
with m.bone("Tail1", (-0.7, 0, 1.2)):
    for k, y in enumerate((-0.3, 0.0, 0.3)):
        feather(f"Tail{k}", V(-0.7, y * 0.5, 1.15), (-1, y, -0.35), 1.3, 0.55, (WH, WH, WH_D), (0, 0, 1))

with m.bone("Head", (0.05, 0, 3.0)), m.frame(pivot=(0.05, 0, 3.0), scale=1.12):
    hc = V(0.15, 0, 3.75)
    m.box("Head", hc, (1.65, 1.95, 1.55), WH, top=(0.82, 0.86), bot=(0.9, 0.9))
    m.box("Disc", hc + V(0.78, 0, -0.05), (0.2, 1.65, 1.25), WH, top=(0.85, 0.9), bot=(0.8, 0.85))
    for s in (1, -1):
        m.spike(f"Tuft{s}", hc + V(0.0, s * 0.62, 0.7), hc + V(-0.2, s * 0.85, 1.15), 0.22, WH_D, flat=0.6)
    for k, (x, y) in enumerate(((-0.3, 0.5), (0.1, -0.4), (-0.5, -0.1))):            # a few speckles on the crown
        m.box(f"CrownBar{k}", hc + V(x, y, 0.78), (0.24, 0.1, 0.06), BAR, rot=Rz(0.6 * k), **NS)
    m.box("Beak", hc + V(0.95, 0, -0.18), (0.32, 0.3, 0.4), BLK, top=(0.6, 0.6), **NS)
    m.spike("BeakHook", hc + V(1.08, 0, -0.32), hc + V(1.12, 0, -0.62), 0.1, BLK, flat=0.6)
    m.eyes(tuple(hc + V(0.9, 0.48, 0.15)), size=(0.6, 0.5), pupil=0.72, look=(0.35, 0), angry=0.42, white=GOLD,
           brow_col=GREY, brow_h=0.5, brow_up=0.72, brow_w=1.2, depth=0.14)

for s in (1, -1):                       # wings raised high in a wide V, swept back so they read from front and side
    sh, el, tip = V(0.0, s * 1.0, 2.75), V(-0.4, s * 2.0, 3.6), V(-0.65, s * 3.0, 4.5)
    with m.bone(f"Wing_{LR(s)}", sh):
        m.seg(f"WingArm{s}", sh, el, 0.85, 0.7, WH)
        m.seg(f"WingHand{s}", el, tip, 0.6, 0.35, WH)
        N = 8
        for k in range(N):
            t = k / (N - 1); root = sh.lerp(el, t * 2) if t < 0.5 else el.lerp(tip, (t - 0.5) * 2)
            ang = 0.2 + t * 1.2
            d = (-0.8 * math.cos(ang), s * 0.55 * math.cos(ang), math.sin(ang))
            L = 1.5 + 1.5 * t ** 0.8
            g = (WH, WH, BAR) if k >= N - 3 else (WH, WH_D, GREY) if k % 2 else (WH, WH, WH_D)
            feather(f"Feather{s}{k}", root, d, L, 0.85, g, (-0.8, s * 0.55, 0))
        for j in range(3):                                                         # black bars across the coverts
            q = sh.lerp(el, 0.3 + 0.3 * j) + V(0.05, s * 0.05, 0.1)
            m.box(f"WingBar{s}{j}", q, (0.12, 0.42, 0.1), BAR, rot=Rx(s * 0.9), **NS)
    with m.bone(f"Leg_{LR(s)}", (0.0, s * 0.55, 1.2)):
        m.seg(f"Boot{s}", V(0.0, s * 0.55, 1.25), V(0.2, s * 0.6, 0.3), 0.75, 0.65, WH)
        m.box(f"BootFluff{s}", (0.25, s * 0.6, 0.35), (0.85, 0.75, 0.45), WH_D, top=(0.85, 0.85))
        for k in (-1, 0, 1):
            m.spike(f"Talon{s}{k}", V(0.55, s * 0.6 + k * 0.2, 0.22), V(0.95, s * 0.6 + k * 0.3, 0.02), 0.08, BLK, flat=0.5)
        m.spike(f"BackTalon{s}", V(-0.05, s * 0.6, 0.22), V(-0.45, s * 0.6, 0.02), 0.08, BLK, flat=0.5)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
