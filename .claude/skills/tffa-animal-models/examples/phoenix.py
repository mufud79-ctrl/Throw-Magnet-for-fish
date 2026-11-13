"""TFFA Phoenix (mythic). Reference: the phoenix thumbnail. Faceted low-poly bird, NO studs: orange-red body,
wings raised high made of long blade feathers with orange->yellow gradients, swept yellow crest, short hooked beak,
long tail streamers ending in diamond tips, orange legs with grey claws."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

BODY, BODY2, YEL, ORG, DEEP = rgb(236, 92, 24), rgb(250, 150, 30), rgb(255, 222, 60), rgb(246, 128, 26), rgb(212, 52, 18)
BEAK, CLAWC = rgb(250, 140, 40), rgb(150, 150, 165)
m = Model("Phoenix", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, chamfer=0.1)
NS = dict(studs=False)

def feather(name, root, direction, length, width, grad=(DEEP, ORG, YEL), side=(0, 1, 0)):
    """Long blade feather (3-stop gradient base -> tip) lying in the plane of direction and side."""
    d = V(*direction).normalized(); sd = V(*side); sd = (sd - d * sd.dot(d)).normalized()
    pts = [(0, 0), (width / 2, length * 0.18), (width * 0.42, length * 0.8), (0, length), (-width * 0.42, length * 0.8), (-width / 2, length * 0.18)]
    m.slab(name, pts, 0.16, grad[0], origin=root, xaxis=sd, yaxis=d, grad=grad, chamfer=0.3)

# body: plump, low, leaning forward; yellow-orange chest
LIFT = -1.1
LR = lambda s: "L" if s > 0 else "R"
with m.frame(move=(0, 0, LIFT)):
    body = m.bone("Body", (0, 0, 4.0)); body.__enter__()
    m.seg("Body", (-1.5, 0, 3.5), (1.0, 0, 4.7), 2.6, 2.3, BODY, d0=2.3, d1=2.6, **NS)
    m.seg("Chest", (0.5, 0, 3.4), (1.45, 0, 5.0), 2.0, 1.7, BODY2, d0=1.2, d1=1.2, **NS)
    with m.bone("Neck", (0.9, 0, 4.6)): m.seg("Neck", (0.9, 0, 4.6), (1.5, 0, 5.9), 1.6, 1.3, BODY, **NS)
    head = m.bone("Head", (1.4, 0, 5.6), "Neck"); head.__enter__()
    m.box("Head", (1.75, 0, 6.2), (1.5, 1.35, 1.25), BODY, top=(0.8, 0.85), **NS)
    m.box("Beak", (2.7, 0, 6.05), (0.8, 0.55, 0.55), BEAK, top=(0.5, 0.7), shift=(0.1, 0), **NS)
    m.spike("BeakHook", (3.0, 0, 6.0), (3.2, 0, 5.6), 0.22, BEAK)
    m.eyes((2.15, 0.58, 6.35), facing=(0.6, 1, 0), size=(0.42, 0.28), pupil=0.7, look=(0.6, 0), angry=0.4,
           white=YEL, brow_col=DEEP, brow_h=0.5, brow_up=0.7, depth=0.1)
    for k in range(5):                                     # big swept-back crest
        feather(f"Crest{k}", (1.5 - k * 0.12, 0, 6.7), (-1, (k - 2) * 0.12, 1.3 - k * 0.22), 2.2 + k * 0.25, 0.5, (ORG, YEL, YEL))
    head.__exit__(None, None, None)

    # wings: raised fans of many separate blade feathers (outer ones longest, pointing up)
    for s in (1, -1):
        sh, el, tip = V(0.1, s * 1.0, 4.9), V(-0.5, s * 2.0, 6.6), V(-0.9, s * 2.5, 8.4)
        wing = m.bone(f"Wing_{LR(s)}", sh); wing.__enter__()
        m.seg(f"WingArm{s}", sh, el, 0.9, 0.7, BODY, **NS)
        m.seg(f"WingHand{s}", el, tip, 0.7, 0.4, ORG, **NS)
        N = 9
        for k in range(N):
            t = k / (N - 1); root = sh.lerp(el, t * 2) if t < 0.5 else el.lerp(tip, (t - 0.5) * 2)
            ang = 0.25 + t * 1.15                            # inner feathers lean back, outer ones point up
            d = (-0.8 * math.cos(ang), s * 0.6 * math.cos(ang), math.sin(ang))    # fan spreads out sideways + up
            L = 2.2 + 3.6 * t ** 0.8
            g = (DEEP, ORG, YEL) if t < 0.3 else (ORG, YEL, YEL)
            feather(f"Feather{s}{k}", root, d, L, 0.62, g, side=(-0.8, s * 0.6, 0))       # feathers lie in the wing plane (swept back ~37 deg)
        wing.__exit__(None, None, None)

    # tail: streamers fanning up/back, big diamond gems, short feather fan at the base
    tl = m.bone("Tail1", (-1.5, 0, 3.5)); tl.__enter__()
    for k, (y, z) in enumerate(((0.9, 1.8), (0.3, 0.9), (-0.3, 0.9), (-0.9, 1.8))):
        a, b = V(-1.6, 0, 3.4), V(-5.0, y, 2.4 + z)
        m.seg(f"Streamer{k}", a, b, 0.24, 0.14, ORG, **NS)
        u = (b - a).normalized()
        m.slab(f"TailGem{k}", [(0, -0.75), (0.5, 0), (0, 0.75), (-0.5, 0)], 0.3, ORG, origin=b + u * 0.7,
               xaxis=(0, 1, 0), yaxis=u, grad=(ORG, YEL))
    for k in range(3):
        feather(f"TailFan{k}", (-1.5, 0, 3.6), (-1, (k - 1) * 0.5, -0.1), 2.2, 0.9, (DEEP, ORG, ORG), side=(0, 0, 1))
    tl.__exit__(None, None, None); body.__exit__(None, None, None)

# legs
for s in (1, -1):
  with m.bone(f"Leg_{LR(s)}", (-0.3, s * 0.7, 2.4)):
    m.seg(f"Thigh{s}", (-0.3, s * 0.7, 2.4), (0.3, s * 0.75, 1.2), 0.9, 0.6, BODY, **NS)
    m.seg(f"Shin{s}", (0.3, s * 0.75, 1.3), (0.1, s * 0.75, 0.25), 0.45, 0.38, ORG, **NS)
    for k in (-1, 0, 1):
        m.spike(f"Toe{s}{k}", (0.15, s * 0.75 + k * 0.2, 0.15), (0.75, s * 0.75 + k * 0.35, 0.05), 0.1, CLAWC)
    m.spike(f"BackToe{s}", (0.0, s * 0.75, 0.15), (-0.5, s * 0.75, 0.05), 0.1, CLAWC)

m.done(views=[("hero", 55, 8, 45), ("front", 0, 6, 45)])
