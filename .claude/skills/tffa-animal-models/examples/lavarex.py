"""TFFA LavaRex (Volcano) - hero build on the reviewed T-Rex (theropod archetype) + bespoke lava armour.

Reference analysis (iconic "lava / magma T-Rex" art, most important first):
1. Silhouette: the reviewed T-Rex - huge open-jawed head, thick legs, long tail - but its back is a ridge of cooling
   BASALT PLATES with obsidian spikes, and smoking volcanic vents rise from the shoulders.
2. Head: dark rock skull with brow plates + horns, glowing eyes, the open jaws dripping strings of magma between the
   teeth, a molten glow deep in the throat.
3. Signature: glowing lava cracks running between every plate and branching across the flanks, thighs and tail; the
   belly is molten and cracked; vents glow at the top.
4. Colours: basalt grey-brown, darker plates, obsidian spikes, molten orange belly, orange-red glow (one glow colour).
Bones (theropod): Body, Neck, Head, Jaw, Tail1-4, Leg_L/R, Arm_L/R. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_archetypes import *

ROCK, PLATE, OBS, BEL, GL = rgb(66, 54, 52), rgb(40, 32, 34), rgb(30, 22, 30), rgb(244, 132, 40), rgb(255, 112, 24)

def lava_armour(m, c):
    S, s = c["S"], c["s"]
    top = lambda x: 6.9 + 0.36 * x                    # back top line of the leaning body box
    with m.bone("Body"):
        for k, x in enumerate((1.9, 0.85, -0.2, -1.25)):
            z = top(x)
            m.box(f"Plate{k}", S(x, 0, z + 0.12), (1.05 * s, 2.7 * s, 0.45 * s), PLATE, rot=Ry(-0.35), top=(0.8, 0.85))
            m.box(f"PlateCrack{k}", S(x - 0.55, 0, z - 0.05), (0.14 * s, 2.5 * s, 0.3 * s), GL, rot=Ry(-0.35), glow=True, studs=False)
            m.spike(f"Spike{k}", S(x, 0, z + 0.3), S(x - 0.4, 0, z + 1.5 - 0.1 * k), 0.36 * s, OBS, flat=0.45)
            m.spike(f"SpikeGlow{k}", S(x - 0.25, 0, z + 0.95 - 0.06 * k), S(x - 0.4, 0, z + 1.5 - 0.1 * k), 0.13 * s, GL, flat=0.45, glow=True)
            for t in (1, -1):
                m.box(f"SidePlate{k}{t}", S(x - 0.1, t * 1.6, z - 0.75), (0.95 * s, 0.4 * s, 0.9 * s), PLATE, rot=Ry(-0.35) @ Rx(t * 0.45), top=(0.8, 0.85))
        for t in (1, -1):        # smoking volcanic vents on the shoulders
            b = S(1.4, t * 1.05, top(1.4) + 0.2)
            m.box(f"Vent{t}", b, (0.95 * s, 0.95 * s, 0.9 * s), PLATE, top=(0.45, 0.45))
            m.box(f"VentLava{t}", b + S(0, 0, 0.46), (0.42 * s, 0.42 * s, 0.1 * s), GL, glow=True, studs=False)
            for j in range(3):
                m.box(f"Smoke{t}{j}", b + S(-0.15 * j, 0, 0.75 + j * 0.45), ((0.55 - j * 0.1) * s,) * 3, rgb(84, 78, 82), rot=Rz(j * 0.5), studs=False)
            for j, (x, z, l, a) in enumerate(((1.6, 5.2, 1.4, 0.6), (0.2, 4.6, 1.6, -0.4), (-1.2, 5.6, 1.2, 0.3), (0.9, 3.8, 1.1, -0.8), (-0.6, 3.9, 1.0, 0.9))):
                m.box(f"Crack{t}{j}", S(x, t * 1.96, z), (l * s, 0.1 * s, 0.17 * s), GL, rot=Ry(a), glow=True, studs=False)
                m.box(f"CrackB{t}{j}", S(x + 0.35, t * 1.96, z + 0.3), (l * 0.45 * s, 0.1 * s, 0.13 * s), GL, rot=Ry(a + 1.1), glow=True, studs=False)
            for j, (x, z) in enumerate(((1.4, 3.6), (0.4, 3.2), (1.0, 4.4))):        # molten belly cracks
                m.box(f"BellyCrack{t}{j}", S(x, t * 1.0, z), (0.9 * s, 0.1 * s, 0.14 * s), GL, rot=Ry(0.4 + j), glow=True, studs=False)
    for t in (1, -1):             # cracks on the thighs
        with m.bone(f"Leg_{'L' if t > 0 else 'R'}"):
            m.box(f"ThighCrack{t}", S(-0.5, t * 2.68, 4.1), (1.6 * s, 0.1 * s, 0.16 * s), GL, rot=Ry(0.9), glow=True, studs=False)
            m.box(f"ThighCrack2{t}", S(-0.9, t * 2.68, 3.4), (0.9 * s, 0.1 * s, 0.14 * s), GL, rot=Ry(-0.5), glow=True, studs=False)
            m.box(f"KneePlate{t}", S(-0.75, t * 2.2, 2.5), (1.2 * s, 0.5 * s, 1.0 * s), PLATE, top=(0.8, 0.8))
    for i, (x, z, w) in enumerate(((-4.4, 5.4, 2.4), (-6.3, 5.6, 1.8), (-8.0, 6.0, 1.2))):   # tail plates + spikes + cracks
        with m.bone(f"Tail{i + 1}"):
            m.box(f"TailPlate{i}", S(x, 0, z + w * 0.48), (1.1 * s, w * 0.75 * s, 0.35 * s), PLATE, top=(0.8, 0.85))
            m.spike(f"TailSpike{i}", S(x, 0, z + w * 0.55), S(x - 0.35, 0, z + w * 0.55 + 1.0 - 0.2 * i), (0.3 - 0.05 * i) * s, OBS, flat=0.45)
            for t in (1, -1):
                m.box(f"TailCrack{i}{t}", S(x + 0.2, t * w * 0.5, z), (1.0 * s, 0.1 * s, 0.14 * s), GL, rot=Ry(0.4 * t), glow=True, studs=False)
    H_ = S(3.2, 0, 7.5)
    with m.bone("Head"), m.frame(pivot=H_, rot=Ry(-0.22)):     # same frame as the theropod head
        m.box("SkullPlate", S(4.0, 0, 9.95), (2.4 * s, 2.4 * s, 0.4 * s), PLATE, top=(0.8, 0.85))
        m.box("SkullCrack", S(4.0, 0, 10.18), (2.0 * s, 0.12 * s, 0.06 * s), GL, glow=True, studs=False)
        for t in (1, -1):
            m.spike(f"BrowHorn{t}", S(4.6, t * 1.15, 9.95), S(3.9, t * 1.55, 10.9), 0.28 * s, OBS, flat=0.6)
            m.box(f"CheekPlate{t}", S(3.6, t * 1.55, 8.2), (1.4 * s, 0.3 * s, 1.0 * s), PLATE, top=(0.8, 0.8))
            for k, x in enumerate((4.9, 5.7, 6.6)):            # magma drool strings across the open jaws
                L = 0.9 + 0.25 * (k % 2)
                m.box(f"Drool{t}{k}", S(x, t * 0.62, 7.25 - L / 2), (0.12 * s, 0.12 * s, L * s), GL, glow=True, studs=False)
                m.box(f"DroolBlob{t}{k}", S(x, t * 0.62, 7.25 - L), (0.22 * s, 0.22 * s, 0.22 * s), GL, glow=True, studs=False)
        m.box("ThroatGlow", S(4.2, 0, 7.45), (1.0 * s, 1.6 * s, 0.9 * s), GL, glow=True, studs=False)
        for k, x in enumerate((5.0, 6.0, 7.0)): m.box(f"RidgeCrack{k}", S(x, 0, 9.74), (0.12 * s, 1.5 * s, 0.06 * s), GL, glow=True, studs=False)

out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "models", "TFFA", "LavaRex")
build("LavaRex", theropod, dict(s=1.0, c1=ROCK, c2=PLATE, belly=BEL, iris=rgb(255, 150, 40), eye_glow=True, glow=GL, jitter=0.08, x=[lava_armour]), out,
      views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 50), ("ref", 35, -4, 50)])
