"""TFFA MagmaSlug (Volcano) - hero build.

Reference analysis (giant slug/snail art crossed with an erupting volcano - the twist is the shell):
1. Silhouette: a long, low, soft slug body gliding forward with its head reared up, and on its back an ERUPTING
   VOLCANO for a shell - a tall rocky cone, the highest point, with lava bursting from the crater.
2. Head: two long eye stalks with glowing eyes and heavy lids, two short feelers, a wide mouth with a lava drip.
3. Signature: glowing lava flows running down the cone; molten blobs and rocks flying out of the crater; a glowing
   seam where the soft foot meets the ground; a lava slime trail behind; crusted rock patches on the body.
4. Colours: dark rock-brown body, rusty underside, grey-black cone with darker ledges, molten orange glow (one glow
   colour), red-orange crust around the lava.
Bones: Body, Head, Tent0/1_<j> (eye stalks), Tail1-2. Crawl gait. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

BODY, BODY_D, FOOT, ROCK, ROCK_D = rgb(124, 70, 56), rgb(70, 40, 36), rgb(176, 84, 46), rgb(70, 64, 70), rgb(42, 38, 44)
GL, CRUST = rgb(255, 128, 30), rgb(214, 60, 22)
V = lambda *a: Vector(a)

m = Model("MagmaSlug", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.42, chamfer=0.2, jitter=0.06)
m.gait = {"crawl": True}
body = m.bone("Body", (0, 0, 0.8)); body.__enter__()
m.box("Front", (1.9, 0, 0.72), (2.4, 2.0, 1.4), BODY, top=(0.84, 0.86), bot=(1.0, 1.0))
m.box("Mid", (-0.2, 0, 0.68), (2.6, 2.3, 1.35), BODY, top=(0.85, 0.86), bot=(1.0, 1.0))
m.box("Sole", (0.3, 0, 0.12), (6.2, 2.5, 0.24), FOOT, top=(0.96, 0.96))
for s in (1, -1):
    m.box(f"Seam{s}", (0.3, s * 1.26, 0.2), (5.8, 0.06, 0.1), GL, glow=True, studs=False)
    for j, (x, z, r) in enumerate(((1.6, 0.9, 0.5), (0.2, 0.7, 0.45), (2.4, 0.55, 0.32))):
        m.box(f"Crust{s}{j}", (x, s * (1.02 if x > 1 else 1.17), z), (r, 0.08, r * 0.7), BODY_D, studs=False)
with m.bone("Tail1", (-1.4, 0, 0.6)):
    m.box("Rear", (-2.2, 0, 0.52), (2.0, 1.9, 1.0), BODY, top=(0.8, 0.82))
    with m.bone("Tail2", (-3.0, 0, 0.45)):
        m.box("TailTip", (-3.65, 0, 0.36), (1.5, 1.2, 0.62), BODY, top=(0.62, 0.65))
        for k, (x, y, l) in enumerate(((-4.8, 0.0, 1.2), (-6.0, 0.25, 1.0), (-7.0, -0.1, 0.7))):    # lava slime trail
            m.box(f"Trail{k}", (x, y, 0.03), (l, 1.0 - k * 0.2, 0.06), GL, glow=True, studs=False)

# erupting volcano shell
cone = [(-0.25, 1.75, 3.2, 2.75, 1.25), (-0.4, 2.8, 2.4, 2.05, 0.95), (-0.5, 3.6, 1.7, 1.5, 0.75)]
for i, (x, z, l, w, h) in enumerate(cone):
    m.box(f"Cone{i}", (x, 0, z), (l, w, h), ROCK, top=(0.78, 0.78), bot=(1.0, 1.0))
    m.box(f"Ledge{i}", (x, 0, z - h / 2 + 0.08), (l + 0.12, w + 0.12, 0.16), ROCK_D, studs=False)
for k in range(6):            # jagged crater rim
    a = 2 * math.pi * k / 6 + 0.3; p = V(-0.5 + math.cos(a) * 0.55, math.sin(a) * 0.5, 4.1)
    m.box(f"Rim{k}", p, (0.5, 0.45, 0.45 + 0.15 * (k % 2)), ROCK_D, rot=Rz(a), top=(0.6, 0.6))
m.box("CraterLava", (-0.5, 0, 4.05), (0.85, 0.75, 0.16), GL, glow=True, studs=False)
for k, (x, y, z, r) in enumerate(((-0.45, 0.05, 4.6, 0.38), (-0.3, -0.2, 5.15, 0.3), (-0.65, 0.25, 5.5, 0.24), (-0.2, 0.3, 5.9, 0.2), (-0.55, -0.3, 6.1, 0.16))):
    m.box(f"Burst{k}", (x, y, z), (r, r, r * 1.2), GL, rot=Rz(k) @ Rx(k * 0.7), glow=True, studs=False)
for k, (x, y, z) in enumerate(((0.3, 0.6, 5.3), (-1.2, -0.5, 5.0), (-0.9, 0.8, 5.8))):
    m.box(f"Bomb{k}", (x, y, z), (0.28, 0.28, 0.28), ROCK_D, rot=Rz(k) @ Rx(k), studs=False)
for f, (a, length) in enumerate(((0.4, 1.0), (2.4, 0.9), (4.2, 1.0))):     # lava flows down the cone
    d = V(math.cos(a), math.sin(a), 0)
    for j, (r, z) in enumerate(((0.62, 3.75), (1.0, 3.05), (1.38, 2.25))):
        p = V(-0.5, 0, 0) + d * r * (1.0 + 0.05 * j); p.z = z
        m.box(f"FlowCrust{f}{j}", p - d * 0.05, (0.56, 0.56, 0.85), CRUST, rot=Rz(a), studs=False)
        m.box(f"Flow{f}{j}", p + d * 0.12, (0.42, 0.42, 0.8), GL, rot=Rz(a), glow=True, studs=False)

# head: reared up, eye stalks with lidded glowing eyes, feelers, lava-dripping mouth
with m.bone("Head", (2.8, 0, 1.0)), m.frame(pivot=(2.8, 0, 1.0), scale=1.25):
    hc = V(3.55, 0, 1.75)
    m.box("Neck", (3.1, 0, 1.2), (1.3, 1.6, 1.3), BODY, top=(0.85, 0.9))
    m.box("Head", hc, (1.5, 1.6, 1.3), BODY, top=(0.84, 0.86), bot=(0.92, 0.92))
    m.box("Mouth", hc + V(0.76, 0, -0.32), (0.08, 1.1, 0.24), CRUST, studs=False)
    m.box("Drip", hc + V(0.78, 0.25, -0.62), (0.12, 0.12, 0.5), GL, glow=True, studs=False)
    m.box("DripBlob", hc + V(0.78, 0.25, -0.9), (0.2, 0.2, 0.2), GL, glow=True, studs=False)
    for s in (1, -1):
        m.seg(f"Feeler{s}", hc + V(0.55, s * 0.5, -0.35), hc + V(1.15, s * 0.75, -0.55), 0.22, 0.14, BODY_D, studs=False)
    for k, s in ((0, 1), (1, -1)):
        pts = [hc + V(0.1, s * 0.42, 0.55), hc + V(0.35, s * 0.62, 1.4), hc + V(0.7, s * 0.75, 2.05)]
        m.chain(f"Stalk{k}", pts, [0.32, 0.26, 0.22], BODY, bones=[f"Tent{k}_0", f"Tent{k}_1"], studs=False)
        with m.bone(f"Tent{k}_1"):
            e = pts[-1] + V(0.12, 0, 0.18)
            m.box(f"EyeBall{k}", e, (0.55, 0.55, 0.55), GL, glow=True, studs=False)
            m.box(f"Slit{k}", e + V(0.28, 0, 0), (0.04, 0.1, 0.36), PUPIL, studs=False)
            m.box(f"Lid{k}", e + V(0.02, 0, 0.24), (0.62, 0.62, 0.22), BODY_D, rot=Ry(0.4), studs=False)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 14, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 30, 18, 45)], glow_color=GL)
