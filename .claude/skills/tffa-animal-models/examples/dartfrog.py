"""TFFA Frog (Jungle, Cannon Tame) - hero build: a strawberry poison dart frog.

Reference analysis (an iconic poison dart frog on a leaf, most important first):
1. Silhouette: a low wedge that sits UP at the front - the back slopes from the raised head down to the rump; hind
   legs folded in a big Z on each side (thigh forward, shin back, long foot forward), so the outline is wider than tall;
   front legs short and straight, splayed fingers.
2. Head: wide and flat with a long mouth line that curls up at the back corners (smug grin), two BULGING eye domes on top
   that break the silhouette; angry-ish brows because this frog is deadly, not cute.
3. Signature: warning colours - glossy red body with black spots, electric-blue legs (strawberry dart frog), round
   toe pads on every finger and toe, a puffed yellow-orange throat sac.
4. Colours: red + dark red, electric blue + light-blue pads, black spots, orange throat. White eyes so they read.
Bones: Body, Head, Leg_FL/FR/BL/BR (hop gait). Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

RED, RED_D, BLUE, PAD = rgb(226, 34, 40), rgb(164, 20, 30), rgb(34, 82, 216), rgb(110, 170, 255)
SPOT, THROAT, BELLY = rgb(26, 20, 30), rgb(255, 168, 50), rgb(238, 84, 60)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("Frog", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.4, chamfer=0.16, jitter=0.05)
m.gait = {"hop": True}

body = m.bone("Body", (0, 0, 1.2)); body.__enter__()
# body: wedge, raised at the front, sloping to the rump
m.hexa("Body", [(-1.85, -1.25, 0.45), (1.2, -1.45, 0.45), (1.2, 1.45, 0.45), (-1.85, 1.25, 0.45),
                (-1.5, -0.95, 1.85), (0.95, -1.3, 2.55), (0.95, 1.3, 2.55), (-1.5, 0.95, 1.85)], RED)
m.box("Belly", (-0.2, 0, 0.42), (2.6, 2.3, 0.2), BELLY, **NS)
m.box("Rump", (-1.75, 0, 1.05), (0.7, 2.0, 1.2), RED, top=(0.7, 0.75))
SLOPE = math.atan2(2.55 - 1.85, 0.95 + 1.5)
def ztop(x): return 1.85 + (x + 1.5) * math.tan(SLOPE)
for k, (x, y, w, a) in enumerate(((-1.05, 0.35, 0.55, 0.3), (-0.35, -0.45, 0.65, -0.4), (0.45, 0.3, 0.5, 0.7),
                                  (-1.2, -0.55, 0.38, 0.1), (0.25, -0.85, 0.36, 0.4), (-0.55, 0.85, 0.34, 0.9))):
    m.box(f"Spot{k}", (x, y, ztop(x) + 0.05), (w * 1.15, w, 0.16), SPOT, rot=Ry(-SLOPE) @ Rz(a), **NS)
for s in (1, -1):                                   # side spots
    for k, (x, z, w) in enumerate(((-0.9, 1.65, 0.42), (0.35, 1.95, 0.38), (-0.2, 1.75, 0.3))):
        yy = 1.25 + (x + 1.85) / 3.05 * 0.2 - (z - 0.45) / 1.6 * 0.3
        m.box(f"SideSpot{s}{k}", (x, s * (yy + 0.02), z), (w, 0.14, w * 0.85), SPOT, rot=Rx(s * 0.2), **NS)

# head: wide + flat, smug grin, bulging eye domes
with m.bone("Head", (1.0, 0, 1.9)):
    hc = V(1.75, 0, 2.05)
    m.box("Head", hc, (1.7, 3.0, 1.2), RED, top=(0.82, 0.88), bot=(0.92, 0.95))
    m.box("Throat", hc + V(0.05, 0, -0.85), (1.35, 2.1, 0.7), THROAT, top=(0.95, 0.95), bot=(0.75, 0.8))
    m.box("Mouth", hc + V(0.84, 0, -0.32), (0.1, 2.3, 0.1), SPOT, **NS)
    for s in (1, -1):
        m.box(f"MouthSide{s}", hc + V(0.3, s * 1.32, -0.3), (1.0, 0.1, 0.1), SPOT, rot=Rz(s * -0.25), **NS)
        m.box(f"Grin{s}", hc + V(-0.28, s * 1.36, -0.18), (0.32, 0.1, 0.1), SPOT, rot=Ry(-0.6) @ Rz(s * -0.25), **NS)
        m.box(f"Nostril{s}", hc + V(0.72, s * 0.32, 0.5), (0.14, 0.14, 0.08), SPOT, **NS)
        m.box(f"EyeDome{s}", hc + V(-0.2, s * 1.0, 0.75), (1.1, 0.95, 0.85), RED, top=(0.72, 0.75))
    m.eyes(tuple(hc + V(0.36, 1.02, 0.82)), facing=(1, 0.4, 0), size=(0.66, 0.6), pupil=0.75, look=(0.2, 0), angry=0.32,
           brow_col=RED_D, brow_h=0.42, brow_up=0.62, depth=0.16)
    for k, (x, y, w) in enumerate(((0.1, 0.0, 0.42), (-0.5, -0.4, 0.3), (0.45, 0.6, 0.26))):
        m.box(f"HeadSpot{k}", hc + V(x, y, 0.62), (w, w * 0.9, 0.08), SPOT, rot=Rz(0.5 * k), **NS)

def digit(name, root, ang, L, s, col=BLUE):
    tip = root + V(math.cos(ang) * L, s * math.sin(ang) * L, -0.04)
    m.seg(name, root, tip, 0.2, 0.16, col, **NS)
    m.box(name + "Pad", tip + V(0, 0, 0.02), (0.3, 0.3, 0.16), PAD, **NS)

for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (1.0, s * 1.25, 1.2)):
        m.seg(f"Arm{s}", V(1.0, s * 1.25, 1.35), V(1.5, s * 1.6, 0.3), 0.6, 0.45, BLUE)
        for k, a in enumerate((-0.4, 0.1, 0.6, 1.1)):
            digit(f"Finger{s}{k}", V(1.5, s * 1.6, 0.16), a, 0.55, s)
    with m.bone(f"Leg_B{LR(s)}", (-1.1, s * 1.2, 1.0)):
        m.seg(f"Thigh{s}", V(-1.35, s * 1.35, 1.05), V(0.4, s * 1.95, 0.85), 0.95, 0.72, BLUE, d0=1.05, d1=0.8)
        m.seg(f"Shin{s}", V(0.45, s * 2.0, 0.8), V(-1.4, s * 2.2, 0.38), 0.68, 0.48, BLUE)
        for k, t in enumerate((0.3, 0.68)):          # black speckles on the blue legs
            q = V(-1.35, s * 1.35, 1.05).lerp(V(0.4, s * 1.95, 0.85), t)
            m.box(f"ThighSpot{s}{k}", q + V(0, 0, 0.5), (0.36, 0.3, 0.1), SPOT, rot=Rz(s * 0.33 + k), **NS)
        q = V(0.45, s * 2.0, 0.8).lerp(V(-1.4, s * 2.2, 0.38), 0.5)
        m.box(f"ShinSpot{s}", q + V(0, s * 0.32, 0.1), (0.3, 0.1, 0.26), SPOT, **NS)
        m.box(f"Knee{s}", (0.42, s * 2.0, 0.8), (0.7, 0.7, 0.7), BLUE, top=(0.8, 0.8))
        m.seg(f"Foot{s}", V(-1.5, s * 2.2, 0.22), V(-0.45, s * 2.38, 0.16), 0.52, 0.42, BLUE, **NS)
        for k, a in enumerate((-0.35, 0.05, 0.45, 0.85)):
            digit(f"Toe{s}{k}", V(-0.45, s * 2.38, 0.14), a, 0.7 + 0.1 * (k == 1), s)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 14, 45), ("front", 0, 10, 45), ("side", 90, 6, 45)])
