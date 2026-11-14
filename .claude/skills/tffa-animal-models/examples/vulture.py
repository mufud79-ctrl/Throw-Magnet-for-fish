"""TFFA Vulture (Desert, Cannon Tame) - hero build: a lappet-faced vulture mantling its wings.

Reference analysis (a vulture hunched over its find, wings mantled, most important first):
1. Silhouette: a hunched dark body with the bare neck thrust forward and LOW, both wings half-opened and held out and
   down like a cloak (mantling) so the outline is a wide menacing tent; long "finger" primaries at the wing tips.
2. Head: bare wrinkly pink-red head, a massive hooked beak (pale horn with a dark tip), small fierce eyes under a red
   skin brow ridge, loose skin folds (lappets) at the cheeks.
3. Signature: the fluffy cream ruff collar where the bare neck meets the body, the mantled wings, pale thigh feathers,
   grey scaly legs with dark talons.
4. Colours: dark chocolate-brown plumage + near-black primaries, cream ruff + thighs, pink-red head, horn-coloured beak.
Bones: Body, Neck, Head, Wing_L/R, Leg_L/R, Tail1 (walk + fly). Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

BRN, BRN_D, PRIM, RUFF = rgb(98, 70, 54), rgb(70, 50, 40), rgb(44, 36, 32), rgb(242, 232, 210)
SKIN, SKIN_D, BEAK, LEGC, BLK = rgb(232, 120, 112), rgb(196, 70, 70), rgb(222, 206, 168), rgb(150, 150, 160), rgb(30, 26, 26)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Vulture", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.4, chamfer=0.16, jitter=0.05)

def feather(name, root, d, L, w, col, side):
    d = V(*d).normalized(); sd = V(*side); sd = (sd - d * sd.dot(d)).normalized()
    pts = [(0, 0), (w / 2, L * 0.15), (w * 0.45, L * 0.8), (0, L), (-w * 0.45, L * 0.8), (-w / 2, L * 0.15)]
    m.slab(name, pts, 0.14, col, origin=root, xaxis=sd, yaxis=d, grad=(BRN_D, col, col), chamfer=0.3)

body = m.bone("Body", (0, 0, 2.3)); body.__enter__()
m.seg("Body", V(-0.9, 0, 1.6), V(0.55, 0, 2.9), 2.1, 1.9, BRN, d0=1.7, d1=1.8)
m.box("Hunch", (-0.1, 0, 3.15), (1.8, 1.7, 0.8), BRN_D, rot=Ry(0.3), top=(0.7, 0.8))
for k in range(12):                                          # fluffy ruff collar round the neck base
    a = 2 * math.pi * k / 12; y, z = math.cos(a), math.sin(a)
    b = V(0.85, y * 0.55, 3.0 + z * 0.5)
    m.spike(f"Ruff{k}", b, b + V(0.15, y * 0.55, z * 0.45 - 0.1), 0.34, RUFF if k % 2 else lt(RUFF, 0.0), flat=0.6)
m.box("RuffCore", (0.8, 0, 3.0), (0.7, 1.35, 1.2), RUFF, top=(0.8, 0.8))
with m.bone("Tail1", (-1.3, 0, 1.6)):
    for k, y in enumerate((-0.35, 0.0, 0.35)):
        feather(f"Tail{k}", V(-1.2, y * 0.5, 1.55), (-1, y, -0.5), 1.4, 0.6, PRIM, (0, 0, 1))

with m.bone("Neck", (0.95, 0, 3.0)):
    m.seg("Neck", V(0.95, 0, 3.0), V(1.65, 0, 2.95), 0.55, 0.48, SKIN, **NS)
with m.bone("Head", (1.6, 0, 2.95), "Neck"), m.frame(pivot=(1.6, 0, 2.95), scale=1.2):
    hc = V(1.95, 0, 3.05)
    m.box("Head", hc, (0.95, 0.85, 0.8), SKIN, top=(0.82, 0.86), bot=(0.88, 0.9))
    m.box("BrowRidge", hc + V(0.25, 0, 0.35), (0.45, 0.95, 0.2), SKIN_D, **NS)
    for s in (1, -1):
        m.box(f"Lappet{s}", hc + V(0.05, s * 0.45, -0.3), (0.45, 0.12, 0.45), SKIN_D, rot=Rx(s * 0.25), **NS)
        for k in range(2):
            m.box(f"Wrinkle{s}{k}", hc + V(-0.2 - k * 0.2, s * 0.43, 0.1), (0.06, 0.04, 0.4), SKIN_D, **NS)
    m.box("Beak", hc + V(0.72, 0, -0.02), (0.65, 0.5, 0.55), BEAK, top=(0.8, 0.85))
    m.seg("BeakTop", hc + V(0.95, 0, 0.1), hc + V(1.3, 0, -0.1), 0.42, 0.3, BEAK, d0=0.4, d1=0.3)
    m.spike("BeakHook", hc + V(1.28, 0, -0.08), hc + V(1.38, 0, -0.55), 0.17, rgb(70, 60, 54), flat=0.6)
    m.box("BeakLower", hc + V(0.8, 0, -0.32), (0.55, 0.42, 0.16), BEAK, **NS)
    m.eyes(tuple(hc + V(0.25, 0.42, 0.12)), facing=(0.4, 1, 0), size=(0.32, 0.26), pupil=0.62, look=(0.5, 0), angry=0.55,
           brow_col=SKIN_D, brow_h=0.6, brow_up=0.75, depth=0.1)

for s in (1, -1):                       # mantled wings: held out and down like a cloak, finger primaries at the tips
    sh, wr = V(0.35, s * 0.95, 3.0), V(-0.35, s * 2.3, 3.55)
    with m.bone(f"Wing_{LR(s)}", sh):
        m.seg(f"WingArm{s}", sh, wr, 0.9, 0.7, BRN)
        m.box(f"Coverts{s}", sh.lerp(wr, 0.5) + V(-0.1, 0, -0.1), (1.1, 1.2, 0.35), BRN_D, rot=Rx(s * -0.4), top=(0.85, 0.9))
        N = 7
        for k in range(N):
            t = k / (N - 1); root = sh.lerp(wr, 0.2 + 0.8 * t)
            d = (-0.45 - 0.2 * t, s * (0.15 + 0.75 * t), -1.0 + 0.45 * t)
            L = 1.7 + 1.0 * t
            feather(f"Feather{s}{k}", root, d, L, 0.8, BRN if t < 0.6 else PRIM, (-1, s * 0.4, 0))
        for k in range(4):                                   # long finger primaries splayed at the wrist
            d = (-0.5 + 0.25 * k, s * 1.0, -0.6 + 0.12 * k)
            feather(f"Finger{s}{k}", wr, d, 2.1 - 0.15 * k, 0.42, PRIM, (0, 0, 1))
    with m.bone(f"Leg_{LR(s)}", (-0.15, s * 0.55, 1.6)):
        m.box(f"Thigh{s}", (-0.1, s * 0.58, 1.3), (0.8, 0.6, 0.85), RUFF, top=(0.9, 0.9), bot=(0.75, 0.8))
        m.seg(f"Shank{s}", V(-0.05, s * 0.6, 0.95), V(0.05, s * 0.6, 0.2), 0.32, 0.28, LEGC, **NS)
        for k in (-1, 0, 1):
            m.spike(f"Talon{s}{k}", V(0.1, s * 0.6 + k * 0.17, 0.15), V(0.65, s * 0.6 + k * 0.28, 0.03), 0.09, BLK, flat=0.5)
        m.spike(f"BackTalon{s}", V(-0.05, s * 0.6, 0.15), V(-0.45, s * 0.6, 0.03), 0.08, BLK, flat=0.5)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
