"""TFFA Glyptodon (Ice Age, Cannon Tame) - hero build: the car-sized armoured armadillo.

Reference analysis (a Glyptodon in paleo-art, most important first):
1. Silhouette: a huge high DOME shell (like an upturned bowl, the size of a small car) that hides almost the whole body,
   only short stubby legs below it; a small armoured head poking out at the front; a thick armoured tail ending in a
   spiked club.
2. Head: a small blunt head with a bony plated cap on top, deep snout, small grumpy eyes under heavy brows.
3. Signature: the shell's ROSETTE pattern - every plate a raised light rosette inside a darker ring - a scalloped rim
   round the bottom edge, ringed tail armour, the spiked tail club.
4. Colours: sandy-ochre shell + darker rings, lighter rosettes, grey-brown skin, ivory spikes.
Bones: Body, Head, Leg_FL/FR/BL/BR, Tail1..3. Studded, fierce."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

SHELL, SHELL_D, ROSE, SKIN, SKIN_D = rgb(184, 146, 96), rgb(118, 88, 54), rgb(222, 190, 136), rgb(124, 104, 88), rgb(92, 76, 64)
SPIKE, BLK = rgb(236, 224, 196), rgb(30, 24, 22)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Glyptodon", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.55, chamfer=0.17, jitter=0.07)
m.gait = {"amp": 0.6}

body = m.bone("Body", (0, 0, 2.4)); body.__enter__()
m.box("Belly", (0, 0, 1.6), (4.2, 3.0, 1.4), SKIN, **NS)
m.box("ShellBase", (0, 0, 2.55), (5.6, 4.1, 1.7), SHELL, top=(0.97, 0.95), bot=(0.95, 0.95))
m.box("ShellMid", (0, 0, 3.75), (5.3, 3.85, 1.0), SHELL, top=(0.86, 0.84))
m.box("ShellTop", (0, 0, 4.6), (4.5, 3.2, 0.9), SHELL, top=(0.62, 0.62))
for s in (1, -1):
    m.box(f"Rim{s}", (0, s * 2.02, 1.82), (5.7, 0.2, 0.4), SHELL_D, **NS)
    for k in range(9):                                       # scalloped rim
        m.box(f"Scallop{s}{k}", (-2.5 + k * 0.62, s * 2.08, 1.55), (0.4, 0.14, 0.3), SHELL_D, top=(0.6, 1.0), **NS)
for e in (1, -1):
    m.box(f"RimEnd{e}", (e * 2.82, 0, 1.82), (0.2, 4.0, 0.4), SHELL_D, **NS)
def rosette(nm, c, n, big=0.66):                             # raised light rosette inside a darker ring, facing n
    n = V(*n).normalized(); up = V(0, 0, 1) if abs(n.z) < 0.9 else V(1, 0, 0)
    a = up.cross(n).normalized(); b = n.cross(a)
    M = Matrix((a, b, n)).transposed()
    m.box(nm + "Ring", c, (big, big, 0.12), SHELL_D, rot=M, **NS)
    m.box(nm + "Rose", c + n * 0.07, (big * 0.6, big * 0.6, 0.12), ROSE, rot=M, top=(0.75, 0.75), **NS)
from mathutils import Matrix
for s in (1, -1):
    for k in range(7):
        x = -2.25 + k * 0.75
        rosette(f"RS{s}{k}", V(x, s * 2.02, 2.55), (0, s, 0))
        if 0 < k < 6: rosette(f"RM{s}{k}", V(x, s * 1.78, 3.6), (0, s, 0.35))
        if 1 < k < 5: rosette(f"RT{s}{k}", V(x, s * 1.24, 4.62), (0, s, 1.0))
for k in range(4):
    for j in (-1, 0, 1):
        rosette(f"RTop{k}{j}", V(-1.05 + k * 0.7, j * 0.6, 5.06), (0, 0, 1), 0.56)
for e in (1, -1):
    for k in (-1, 0, 1):
        rosette(f"RE{e}{k}", V(e * 2.8, k * 1.1, 2.55), (e, 0, 0))

for s in (1, -1):
    for f, x in (("F", 1.75), ("B", -1.75)):
        with m.bone(f"Leg_{f}{LR(s)}", (x, s * 1.35, 2.0)):
            m.seg(f"Leg{f}{s}", V(x, s * 1.35, 2.0), V(x + 0.1, s * 1.4, 0.4), 1.25, 1.15, SKIN)
            m.box(f"Foot{f}{s}", (x + 0.25, s * 1.4, 0.28), (1.4, 1.3, 0.56), SKIN_D, top=(0.88, 0.9))
            for t in (-1, 0, 1):
                b = V(x + 0.92, s * 1.4 + t * 0.38, 0.26)
                m.spike(f"Claw{f}{s}{t}", b, b + V(0.35, 0, -0.2), 0.1, SPIKE, flat=0.5)

# armoured tail: ringed segments ending in a spiked club
pts = [V(-2.7, 0, 2.3), V(-3.8, 0, 2.0), V(-4.8, 0, 1.75), V(-5.5, 0, 1.6)]
ws = [1.25, 1.05, 0.9, 0.85]
m.chain("Tail", pts, ws, SHELL, bones="Tail")
for i in range(3):
    with m.bone(f"Tail{i + 1}"):
        q = pts[i].lerp(pts[i + 1], 0.55); d = (pts[i + 1] - pts[i]).normalized()
        m.seg(f"TailRing{i}", q - d * 0.1, q + d * 0.1, ws[i] + 0.15, ws[i] + 0.15, SHELL_D, **NS)
with m.bone("Tail3"):
    c = pts[-1] + V(-0.25, 0, 0)
    m.box("Club", c, (1.1, 1.25, 1.15), SHELL_D, top=(0.85, 0.85), bot=(0.85, 0.85))
    for k in range(6):
        a = 2 * math.pi * k / 6; d = V(0, math.cos(a), math.sin(a))
        m.spike(f"ClubSpike{k}", c + d * 0.5, c + d * 1.15 + V(-0.15, 0, 0), 0.18, SPIKE, flat=0.8)
    m.spike("ClubTip", c + V(-0.5, 0, 0), c + V(-1.15, 0, 0), 0.2, SPIKE, flat=0.8)

with m.bone("Head", (2.7, 0, 2.2)), m.frame(pivot=(2.7, 0, 2.2), scale=1.15):
    hc = V(3.3, 0, 2.05)
    m.box("Head", hc, (1.35, 1.55, 1.2), SKIN, top=(0.82, 0.86), bot=(0.88, 0.9))
    m.box("Snout", hc + V(0.85, 0, -0.18), (0.6, 1.05, 0.9), SKIN, top=(0.85, 0.85))
    m.box("Nose", hc + V(1.17, 0, -0.05), (0.08, 0.5, 0.3), BLK, **NS)
    m.box("Mouth", hc + V(1.0, 0, -0.5), (0.4, 0.95, 0.06), BLK, **NS)
    m.box("Cap", hc + V(0.0, 0, 0.66), (1.3, 1.45, 0.32), SHELL, top=(0.85, 0.85))
    rosette("RCap", hc + V(0.0, 0, 0.83), (0, 0, 1), 0.6)
    m.eyes(tuple(hc + V(0.4, 0.75, 0.15)), facing=(0.5, 1, 0), size=(0.36, 0.28), pupil=0.72, look=(0.4, 0), angry=0.5,
           brow_col=BLK, brow_h=0.6, brow_up=0.75, depth=0.12)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 14, 45), ("front", 0, 8, 45), ("side", 90, 6, 45)])
