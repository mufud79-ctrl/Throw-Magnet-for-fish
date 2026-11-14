"""TFFA Ankylosaurus (DinoLand) - hero build.

Reference analysis (iconic ankylosaur art, most important first):
1. Silhouette: a living tank - very low and WIDE, a broad domed armoured back is the widest/highest mass, short thick
   splayed legs, head held low, and a huge tail club swung out to the side.
2. Head: small triangular armoured head with a dark beak, horns at the back and cheek corners pointing back/out,
   angry side eyes under heavy brow plates.
3. Signature: the back is a grid of raised bony scutes (tan with a darker rim); big cream spikes run along both flanks
   (largest at the shoulders); a collar of plates behind the head; spikes along the tail; a knobbly spiked club.
4. Colours: olive green body, tan scutes, cream bone spikes, pale belly.
Bones: Body, Head, Leg_FL/FR/BL/BR, Tail1..3. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

BODY, BODY_D, SCUTE, SCUTE_D, BONE, BELLY = rgb(122, 144, 66), rgb(80, 98, 44), rgb(214, 188, 126), rgb(150, 124, 76), rgb(242, 234, 212), rgb(206, 200, 150)
V = lambda *a: Vector(a); LR = lambda s: "L" if s > 0 else "R"

m = Model("Ankylosaurus", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.5, chamfer=0.16, jitter=0.06)
m.gait = {"amp": 0.8}
body = m.bone("Body", (0, 0, 2.2)); body.__enter__()
m.box("Lower", (0, 0, 1.75), (5.0, 3.7, 1.4), BODY, top=(1.0, 1.0), bot=(0.88, 0.9))
m.box("Belly", (0.2, 0, 1.12), (4.2, 3.0, 0.3), BELLY, studs=False)
m.box("Shell", (-0.1, 0, 2.75), (5.3, 4.3, 1.5), BODY, top=(0.78, 0.8), bot=(1.0, 1.0))
m.box("ShellTop", (-0.15, 0, 3.6), (3.9, 3.0, 0.4), BODY, top=(0.85, 0.85))
for i, x in enumerate((-1.8, -0.9, 0.0, 0.9, 1.8)):           # scute grid on the dome
    for j, y in enumerate((-0.95, 0.0, 0.95)):
        z = 3.85 - 0.05 * abs(y)
        m.box(f"ScuteRim{i}{j}", (x, y, z), (0.74, 0.7, 0.18), SCUTE_D, studs=False)
        m.box(f"Scute{i}{j}", (x, y, z + 0.12), (0.6, 0.56, 0.24), SCUTE, top=(0.65, 0.65), studs=False)
    for s in (1, -1):                                          # side scutes on the slope
        m.box(f"SideScute{i}{s}", (x, s * 1.85, 3.1), (0.62, 0.5, 0.45), SCUTE, rot=Rx(s * 0.75), top=(0.65, 0.7), studs=False)
for s in (1, -1):                                              # flank spikes, largest at the shoulders
    for k, (x, L) in enumerate(((1.9, 1.5), (1.0, 1.3), (0.1, 1.15), (-0.8, 1.05), (-1.7, 0.95), (-2.4, 0.8))):
        b = V(x, s * 2.05, 2.25)
        m.spike(f"FlankSpike{s}{k}", b, b + V(-0.35, s * L, 0.25), 0.3, BONE, flat=0.5)
for k in range(2):                                             # collar plates behind the head
    for j, y in enumerate((-0.7, 0.0, 0.7)):
        m.box(f"Collar{k}{j}", (2.55 + k * 0.35, y, 3.15 - k * 0.25), (0.42, 0.6, 0.38), SCUTE, top=(0.6, 0.6), studs=False)

for sx in (1, -1):
    for s in (1, -1):
        x = sx * 1.7; y = s * 1.55
        with m.bone(f"Leg_{'F' if sx > 0 else 'B'}{LR(s)}", (x, y, 1.6)):
            m.box(f"Leg{sx}{s}", (x, y, 0.8), (1.15, 1.05, 1.6), BODY, top=(1.0, 1.0), bot=(0.9, 0.9))
            m.box(f"Foot{sx}{s}", (x + 0.12, y, 0.18), (1.35, 1.2, 0.36), BODY_D, studs=False)
            for t in (-1, 0, 1): m.spike(f"Toe{sx}{s}{t}", V(x + 0.75, y + t * 0.35, 0.18), V(x + 1.0, y + t * 0.38, 0.05), 0.11, BONE, flat=0.5)

pts = [V(-2.5, 0, 2.45), V(-4.0, 0.35, 2.15), V(-5.4, 0.95, 1.95), V(-6.4, 1.5, 1.85)]
m.chain("Tail", pts, [1.5, 1.05, 0.72, 0.55], BODY, bones="Tail")
for i in (1, 2):
    with m.bone(f"Tail{i}"):
        q = pts[i].lerp(pts[i + 1], 0.4); w = [1.05, 0.72][i - 1]
        for s in (1, -1): m.spike(f"TailSpike{i}{s}", q + V(0, s * w * 0.45, 0.1), q + V(-0.3, s * (w * 0.45 + 0.7), 0.25), 0.2, BONE, flat=0.5)
        m.box(f"TailScute{i}", q + V(0, 0, w * 0.5), (0.55, w * 0.6, 0.22), SCUTE, top=(0.65, 0.65), studs=False)
with m.bone("Tail3"):
    c = pts[-1] + V(-0.75, 0.35, 0.05)
    cf = m.frame(pivot=pts[-1], scale=1.5); cf.__enter__()
    m.box("Club", c, (1.4, 1.7, 1.05), SCUTE, top=(0.8, 0.8), bot=(0.8, 0.8))
    for s in (1, -1):
        m.box(f"ClubLobe{s}", c + V(0.05, s * 0.75, 0), (1.0, 0.7, 0.9), SCUTE, top=(0.75, 0.75), bot=(0.75, 0.75))
        m.spike(f"ClubSpike{s}", c + V(0.1, s * 1.0, 0.1), c + V(-0.1, s * 1.7, 0.25), 0.22, BONE, flat=0.5)
    m.spike("ClubTop", c + V(0, 0, 0.45), c + V(-0.2, 0, 1.15), 0.24, BONE, flat=0.5)
    for k, (dx, dy) in enumerate(((-0.4, 0.4), (0.3, -0.45), (0.35, 0.4), (-0.35, -0.4))):
        m.box(f"ClubKnob{k}", c + V(dx, dy, 0.56), (0.32, 0.32, 0.2), SCUTE_D, studs=False)
    cf.__exit__(None, None, None)

with m.bone("Head", (2.6, 0, 2.2)), m.frame(pivot=(2.6, 0, 2.2), scale=1.3):
    hc = V(3.35, 0, 2.05)
    m.box("Head", hc, (1.55, 1.75, 1.15), BODY, top=(0.8, 0.84), bot=(0.92, 0.92))
    m.box("Snout", hc + V(0.85, 0, -0.2), (0.6, 1.25, 0.75), BODY, top=(0.85, 0.85))
    m.box("Beak", hc + V(1.25, 0, -0.32), (0.32, 1.0, 0.5), rgb(54, 44, 40), bot=(0.8, 0.8), studs=False)
    m.box("HeadPlate", hc + V(-0.05, 0, 0.62), (1.4, 1.5, 0.22), SCUTE, top=(0.8, 0.8), studs=False)
    for s in (1, -1):
        m.box(f"BrowPlate{s}", hc + V(0.35, s * 0.72, 0.5), (0.7, 0.45, 0.3), SCUTE, studs=False)
        m.spike(f"Horn{s}", hc + V(-0.55, s * 0.8, 0.45), hc + V(-1.05, s * 1.35, 0.8), 0.22, BONE, flat=0.6)
        m.spike(f"CheekHorn{s}", hc + V(-0.3, s * 0.85, -0.3), hc + V(-0.65, s * 1.4, -0.55), 0.2, BONE, flat=0.6)
    m.eyes(tuple(hc + V(0.25, 0.88, 0.12)), facing=(0.35, 1, 0), size=(0.55, 0.48), pupil=0.68, look=(0.35, 0), angry=0.4,
           brow_col=BODY_D, brow_h=0.42, brow_up=0.7, depth=0.13)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 14, 45), ("front", 0, 10, 45), ("side", 90, 6, 45), ("ref", 35, 22, 45)])
