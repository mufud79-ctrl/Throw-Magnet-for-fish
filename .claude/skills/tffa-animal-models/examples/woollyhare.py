"""TFFA WoollyHare (Ice Age, Cannon Tame) - hero build: a giant frost hare in its winter coat.

Reference analysis (an arctic/snowshoe hare in deep winter fur, most important first):
1. Silhouette: a round fluffy ball of a body with HUGE haunches, long upright ears (with black tips) standing tall in a
   slight V, enormous snowshoe hind feet, short front legs, a fluffy pom-pom tail - fur tufts break the outline everywhere.
2. Head: round head with big cheek fluff flaring sideways, small pink nose, buck teeth, big eyes with a determined,
   slightly cheeky frown (ready to box).
3. Signature: the woolly coat - tufts with frost-blue tips all over, black ear tips, fur-fringed snowshoe feet, a few
   icicles hanging from the belly fur.
4. Colours: snow white + cool grey shadow, frost blue, black ear tips, pink nose/inner ears.
Bones: Body, Head, Ear_L/R, Leg_FL/FR/BL/BR, Tail1 (hop gait). Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

WH, WH_D, FROST, TIP, PINK, ICE = rgb(248, 248, 252), rgb(208, 214, 228), rgb(170, 208, 250), rgb(54, 58, 72), rgb(250, 160, 172), rgb(196, 236, 255)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)
m = Model("WoollyHare", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.4, chamfer=0.16, jitter=0.04)
m.gait = {"hop": True}

body = m.bone("Body", (0, 0, 1.6)); body.__enter__()
m.box("Hips", (-0.6, 0, 1.5), (1.9, 1.85, 1.95), WH, top=(0.8, 0.85), bot=(0.85, 0.85))
m.box("Chest", (0.6, 0, 1.6), (1.5, 1.55, 1.6), WH, top=(0.82, 0.86), bot=(0.8, 0.85))
for k in range(14):                                          # woolly tufts with frost tips all over the coat
    a = math.pi * (0.1 + 0.8 * (k % 7) / 6); row = k // 7
    y, z = math.cos(a), math.sin(a)
    b = V(0.3 - row * 1.0, y * 0.88, 1.5 + z * 0.85)
    t = b + V(-0.45, y * 0.45, z * 0.35)
    m.spike(f"Tuft{k}", b, t, 0.3, WH if k % 2 else WH_D, flat=0.55)
    m.spike(f"TuftFrost{k}", b.lerp(t, 0.6), t + V(-0.06, y * 0.06, z * 0.05), 0.14, FROST, flat=0.55)
for k in range(3):
    b = V(0.4 - k * 0.5, (k - 1) * 0.4, 0.62)
    m.spike(f"Icicle{k}", b, b + V(0, 0, -0.42), 0.09, ICE, sides=4)
with m.bone("Tail1", (-1.5, 0, 1.9)):
    m.box("Tail", (-1.65, 0, 1.95), (0.6, 0.65, 0.6), WH, top=(0.8, 0.8), bot=(0.8, 0.8))
    m.spike("TailFluff", (-1.8, 0, 2.05), (-2.15, 0, 2.3), 0.22, WH_D, flat=0.6)

for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (0.8, s * 0.5, 1.2)):
        m.seg(f"Arm{s}", V(0.85, s * 0.5, 1.2), V(1.05, s * 0.55, 0.22), 0.42, 0.38, WH)
        m.box(f"Paw{s}", (1.15, s * 0.55, 0.15), (0.55, 0.45, 0.3), WH_D, top=(0.85, 0.9))
    with m.bone(f"Leg_B{LR(s)}", (-0.7, s * 0.8, 1.4)):
        m.box(f"Haunch{s}", (-0.65, s * 0.92, 1.15), (1.5, 0.45, 1.4), WH, top=(0.85, 0.85), bot=(0.75, 0.8))
        m.box(f"SnowShoe{s}", (-0.4, s * 0.95, 0.18), (2.1, 0.75, 0.36), WH_D, top=(0.88, 0.9))
        for k in range(3):                                   # fur fringe round the snowshoe foot
            b = V(0.55, s * 0.95 + (k - 1) * 0.22, 0.2)
            m.spike(f"ShoeFur{s}{k}", b, b + V(0.3, (k - 1) * 0.12, -0.08), 0.12, WH, flat=0.6)

with m.bone("Head", (1.2, 0, 2.1)), m.frame(pivot=(1.2, 0, 2.1), scale=1.2):
    hc = V(1.45, 0, 2.55)
    m.box("Head", hc, (1.2, 1.3, 1.1), WH, top=(0.8, 0.85), bot=(0.88, 0.9))
    for s in (1, -1):                                        # cheek fluff flaring sideways
        for k in range(2):
            b = hc + V(0.1, s * 0.55, -0.2 - 0.2 * k)
            m.spike(f"Cheek{s}{k}", b, b + V(-0.3, s * 0.55, -0.1 - 0.15 * k), 0.24, WH_D if k else WH, flat=0.55)
    m.box("Snout", hc + V(0.6, 0, -0.22), (0.4, 0.62, 0.42), WH, top=(0.85, 0.85))
    m.box("Nose", hc + V(0.82, 0, -0.08), (0.08, 0.2, 0.14), PINK, **NS)
    m.box("Mouth", hc + V(0.81, 0, -0.3), (0.06, 0.06, 0.18), TIP, **NS)
    m.box("BuckTeeth", hc + V(0.79, 0, -0.5), (0.08, 0.22, 0.2), TOOTH, **NS)
    m.eyes(tuple(hc + V(0.5, 0.36, 0.15)), facing=(0.9, 0.4, 0), size=(0.42, 0.4), pupil=0.75, look=(0.4, 0), angry=0.3,
           brow_col=TIP, brow_h=0.4, brow_up=0.75, depth=0.1)
    for s in (1, -1):                                        # long upright ears, black tips, facing forward
        with m.bone(f"Ear_{LR(s)}", hc + V(-0.2, s * 0.35, 0.5)):
            o = hc + V(-0.2, s * 0.32, 0.45); ax = V(-0.1, s * 0.25, 1.0).normalized(); wx = V(0, 1.0, -s * 0.25).normalized()
            m.slab(f"Ear{s}", [(-0.3, 0), (0.3, 0), (0.32, 1.3), (0.15, 1.9), (-0.15, 1.9), (-0.32, 1.3)], 0.16, WH,
                   origin=o, xaxis=wx, yaxis=ax)
            m.slab(f"EarIn{s}", [(-0.18, 0.15), (0.18, 0.15), (0.2, 1.25), (0, 1.45), (-0.2, 1.25)], 0.06, PINK,
                   origin=o + V(0.1, 0, 0), xaxis=wx, yaxis=ax)
            m.slab(f"EarTip{s}", [(-0.25, 1.55), (0.25, 1.55), (0.15, 1.95), (-0.15, 1.95)], 0.2, TIP,
                   origin=o, xaxis=wx, yaxis=ax)
body.__exit__(None, None, None)
m.done(views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
