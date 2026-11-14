"""TFFA EmberWolf (Volcano) - hero build.

Reference analysis (iconic hellhound / fire wolf art, most important first):
1. Silhouette: a lean-but-muscular wolf on long legs in a hunting stance, head low and forward, hackles up - a mane of
   FLAMES rising off the neck and shoulders is the highest point and sweeps backward; tail ends in a torch flame.
2. Head: long wolf snout snarling open, the maw glowing with fire inside, burning yellow eyes under steep brows,
   tall swept-back ears, small curved obsidian horns (hellhound).
3. Signature: charcoal fur cracked over the ribs so the molten core glows through; flames in three layers (deep red
   outside, orange, glowing yellow core); embers drifting above the mane; glowing lava pawprints under the feet.
4. Colours: charcoal + ash-grey muzzle, red/orange flames, yellow-orange glow (one glow colour), obsidian claws/horns.
Bones: Body, Neck, Head, Jaw, Ear_L/R, Leg_FL/FR/BL/BR, Tail1..3. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector

FUR, FUR_D, ASH = rgb(52, 44, 46), rgb(32, 26, 28), rgb(96, 86, 86)
FL_R, FL_O, GL, OBS = rgb(206, 40, 22), rgb(250, 124, 30), rgb(255, 196, 70), rgb(26, 20, 26)
V = lambda *a: Vector(a); LR = lambda s: "L" if s > 0 else "R"

def flame(m, name, base, d, L, w, flat=0.55, front=(1, 0, 0)):
    """Three-layer flame tongue, layers FANNED toward `front` so every colour shows: deep red at the back (longest),
    orange in front of it, glowing yellow core in front (shortest)."""
    d = d.normalized(); f = Vector(front); f = (f - d * f.dot(d)); f = f.normalized() if f.length > 1e-3 else Vector((0, 0, 1))
    m.spike(f"{name}R", base, base + d * L, w, FL_R, flat=flat)
    m.spike(f"{name}O", base + f * w * 0.45, base + f * w * 0.3 + d * L * 0.8, w * 0.8, FL_O, flat=flat)
    m.spike(f"{name}Y", base + f * w * 0.85, base + f * w * 0.6 + d * L * 0.55, w * 0.55, GL, flat=flat, glow=True)

m = Model("EmberWolf", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.45, chamfer=0.16, jitter=0.06)
body = m.bone("Body", (0, 0, 3.5)); body.__enter__()
m.box("Chest", (1.2, 0, 3.65), (2.8, 2.85, 2.9), FUR, top=(0.82, 0.86), bot=(0.74, 0.84))
m.box("Waist", (-0.8, 0, 3.75), (2.0, 2.25, 1.95), FUR, top=(0.92, 0.92), bot=(0.86, 0.9))
m.box("Hips", (-2.3, 0, 3.65), (2.0, 2.55, 2.25), FUR, top=(0.84, 0.86), bot=(0.86, 0.9))
m.box("Back", (-0.6, 0, 4.62), (3.6, 1.2, 0.36), FUR_D, top=(0.7, 0.8))
for s in (1, -1):
    m.box(f"Haunch{s}", (-2.3, s * 1.12, 3.55), (1.5, 0.3, 1.55), FUR, top=(0.8, 0.8), bot=(0.7, 0.8))
    for j in range(4):           # molten ribs glowing through cracks in the fur
        x = 1.75 - j * 0.48
        m.box(f"Rib{s}{j}", (x, s * 1.27, 3.55), (0.12, 0.06, 1.25 - j * 0.12), GL, rot=Ry(0.32), glow=True, studs=False)
        m.box(f"RibCrust{s}{j}", (x + 0.13, s * 1.29, 3.55), (0.1, 0.05, 1.3 - j * 0.12), FL_R, rot=Ry(0.32), studs=False)
    m.box(f"Crack{s}", (-1.9, s * 1.14, 3.9), (0.9, 0.06, 0.1), GL, rot=Ry(0.5), glow=True, studs=False)
    m.box(f"CrackB{s}", (-2.35, s * 1.14, 3.55), (0.6, 0.06, 0.1), GL, rot=Ry(-0.6), glow=True, studs=False)
# flame mane: rows of three-tone flame tongues sweeping back off the neck and shoulders (hackles = highest point)
for k in range(7):
    x = 2.5 - k * 0.5; z = 5.0 - k * 0.07; L = 3.2 - abs(k - 2) * 0.3
    flame(m, f"Mane{k}", V(x, 0, z), V(-0.75, 0, 1.0), L, 0.7)
    for s in (1, -1):
        flame(m, f"ManeS{k}{s}", V(x + 0.1, s * 0.85, z - 0.3), V(-0.8, s * 0.6, 0.8), L * 0.75, 0.55, front=(0.3, s, 0))
for j, (x, y, z) in enumerate(((0.6, 0.4, 7.0), (-0.4, -0.6, 6.6), (1.5, -0.3, 7.4), (-1.2, 0.7, 6.2), (0.2, 0.9, 7.6))):
    m.box(f"Ember{j}", (x, y, z), (0.16, 0.16, 0.16), GL, rot=Rz(0.6) @ Rx(0.6), glow=True, studs=False)

# legs: long, front pair planted forward, hind pair with a strong hock
for s in (1, -1):
    with m.bone(f"Leg_F{LR(s)}", (1.6, s * 0.95, 3.4)):
        m.box(f"Shoulder{s}", (1.65, s * 1.1, 3.35), (1.3, 0.6, 1.6), FUR, top=(0.8, 0.8), bot=(0.8, 0.85))
        m.box(f"Elbow{s}", (1.6, s * 1.15, 2.6), (1.15, 0.75, 1.1), FUR, top=(0.9, 0.9), bot=(0.75, 0.8))
        m.seg(f"Forearm{s}", V(1.7, s * 1.12, 2.9), V(2.0, s * 1.15, 0.75), 1.05, 0.8, FUR)
        m.box(f"Paw{s}", (2.25, s * 1.15, 0.27), (1.3, 1.05, 0.54), FUR_D, top=(0.85, 0.9))
        for t in (-1, 0, 1): m.spike(f"Claw{s}{t}", V(2.7, s * 1.1 + t * 0.26, 0.24), V(3.05, s * 1.1 + t * 0.28, 0.05), 0.09, OBS, flat=0.4)
        m.box(f"PawPrint{s}", (2.3, s * 1.1, 0.03), (1.35, 1.05, 0.06), GL, glow=True, studs=False)
    with m.bone(f"Leg_B{LR(s)}", (-2.3, s * 0.95, 3.5)):
        m.box(f"Thigh{s}", (-2.25, s * 1.1, 2.75), (1.85, 1.0, 2.2), FUR, rot=Ry(-0.3), top=(0.85, 0.9), bot=(0.65, 0.75))
        m.seg(f"Hock{s}", V(-2.85, s * 1.1, 2.0), V(-2.6, s * 1.1, 0.7), 0.82, 0.72, FUR_D)
        m.box(f"HindPaw{s}", (-2.4, s * 1.1, 0.27), (1.25, 1.0, 0.54), FUR_D, top=(0.85, 0.9))
        for t in (-1, 0, 1): m.spike(f"HClaw{s}{t}", V(-1.92, s * 1.0 + t * 0.24, 0.24), V(-1.6, s * 1.0 + t * 0.26, 0.05), 0.08, OBS, flat=0.4)
        m.box(f"HPawPrint{s}", (-2.3, s * 1.0, 0.03), (1.3, 1.0, 0.06), GL, glow=True, studs=False)

# torch tail
pts = [V(-3.15, 0, 4.0), V(-3.9, 0, 4.5), V(-4.45, 0, 5.25), V(-4.7, 0, 5.95)]
m.chain("Tail", pts, [0.62, 0.55, 0.5, 0.48], FUR, bones="Tail")
with m.bone("Tail3"):
    for j, (d, L) in enumerate(((V(-0.3, 0, 1), 1.6), (V(-0.7, 0.35, 0.8), 1.1), (V(-0.7, -0.35, 0.8), 1.1), (V(0.25, 0, 1), 0.9))):
        flame(m, f"TailFlame{j}", pts[-1] + V(0, 0, -0.1), d, L * 1.5, 0.55 if j == 0 else 0.4)

# neck + head (low, forward), snarling with a glowing maw
with m.bone("Neck", (2.4, 0, 4.35)):
    m.seg("Neck", V(2.0, 0, 4.5), V(3.3, 0, 4.55), 1.75, 1.55, FUR, d0=1.9, d1=1.6)
with m.bone("Head", (3.2, 0, 4.5), "Neck"):
    hc = V(4.0, 0, 4.55)
    m.box("Head", hc, (1.7, 1.85, 1.5), FUR, top=(0.86, 0.88), bot=(0.88, 0.9))
    m.box("Brow", hc + V(0.62, 0, 0.6), (0.6, 1.65, 0.38), FUR_D, top=(0.7, 0.9))
    m.box("Snout", hc + V(1.45, 0, -0.32), (1.55, 1.05, 0.72), ASH, top=(0.86, 0.9), bot=(0.95, 0.95))
    m.box("Nose", hc + V(2.24, 0, -0.06), (0.16, 0.5, 0.3), OBS, bot=(0.9, 0.6), studs=False)
    for k in range(3): m.box(f"Wrinkle{k}", hc + V(1.0 + k * 0.25, 0, 0.08), (0.1, 0.8, 0.1), FUR_D, studs=False)
    m.box("Maw", hc + V(1.35, 0, -0.75), (1.4, 0.85, 0.32), MOUTH, studs=False)
    m.box("MawFire", hc + V(1.0, 0, -0.75), (0.9, 0.6, 0.28), GL, glow=True, studs=False)
    for t in (1, -1):
        for k, x in enumerate((1.4, 1.75, 2.05)):
            m.spike(f"ToothU{t}{k}", hc + V(x, t * 0.45, -0.68), hc + V(x + 0.02, t * 0.44, -0.95), 0.08, TOOTH, flat=0.3)
        m.spike(f"Fang{t}", hc + V(2.1, t * 0.36, -0.66), hc + V(2.14, t * 0.36, -1.18), 0.11, TOOTH, flat=0.35)
    m.eyes(tuple(hc + V(0.86, 0.6, 0.25)), facing=(0.8, 0.6, 0), size=(0.58, 0.32), pupil=0.75, look=(0.5, 0), angry=0.55,
           white=GL, glow_white=True, pupil_col=rgb(120, 20, 10), brow_col=OBS, brow_h=0.6, brow_up=0.75, depth=0.14)
    for s in (1, -1):
        with m.bone(f"Ear_{LR(s)}", hc + V(-0.4, s * 0.62, 0.7)):
            m.spike(f"Ear{s}", hc + V(-0.35, s * 0.62, 0.62), hc + V(-0.95, s * 0.82, 1.75), 0.36, FUR, flat=0.6)
            m.spike(f"EarIn{s}", hc + V(-0.24, s * 0.63, 0.7), hc + V(-0.8, s * 0.82, 1.45), 0.2, FL_R, flat=0.5)
        hp = [hc + V(0.35, s * 0.55, 0.78), hc + V(-0.1, s * 0.72, 1.25), hc + V(-0.7, s * 0.82, 1.4)]
        m.chain(f"Horn{s}", hp, [0.24, 0.18, 0.12], OBS, studs=False)
        m.spike(f"HornTip{s}", hp[-1], hp[-1] + V(-0.45, s * 0.05, -0.05), 0.06, OBS)
    with m.bone("Jaw", hc + V(0.3, 0, -0.6)), m.frame(pivot=hc + V(0.3, 0, -0.6), rot=Ry(0.4)):
        m.box("Jaw", hc + V(1.3, 0, -1.0), (1.55, 0.92, 0.36), ASH)
        m.box("JawFire", hc + V(1.1, 0, -0.85), (1.0, 0.6, 0.08), GL, glow=True, studs=False)
        for t in (1, -1):
            for k, x in enumerate((1.45, 1.8)):
                m.spike(f"ToothL{t}{k}", hc + V(x, t * 0.38, -0.82), hc + V(x - 0.02, t * 0.37, -0.6), 0.07, TOOTH, flat=0.3)
            m.spike(f"FangB{t}", hc + V(1.98, t * 0.33, -0.84), hc + V(2.0, t * 0.33, -0.42), 0.09, TOOTH, flat=0.35)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 28, 14, 45)], glow_color=GL)
