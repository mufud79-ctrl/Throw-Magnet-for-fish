"""TFFA Spinosaurus (DinoLand) - hero build on the user-approved T-Rex body (theropod archetype) + bespoke parts.

Reference analysis (iconic Spinosaurus art, most important first):
1. Silhouette: the approved chunky T-Rex stance, but with a HUGE sail rising from neck to hips - the tallest thing,
   a fan of ribbed spines with membrane - and a long crocodile snout.
2. Head: long croc-like snout with the jaws open, big side eye with a heavy brow, nostril bumps; the twist: a FISH
   clamped across its jaws (the river hunter).
3. Signature: two-tone sail (red-orange membrane, golden top band, cream spines); darker stripes on the flanks;
   ridge scutes along the tail.
4. Colours: deep teal body, cream throat/jaw, red-orange + gold sail, silver-blue fish.
Bones (theropod): Body, Neck, Head, Jaw, Tail1-4, Leg_L/R, Arm_L/R. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_archetypes import *

TEAL, TEAL_D, SAIL, SAIL_T, SPINE, FISH, FISH_D = rgb(46, 120, 132), rgb(26, 76, 86), rgb(222, 74, 44), rgb(252, 186, 60), rgb(244, 234, 210), rgb(250, 168, 60), rgb(206, 96, 36)

def spino_parts(m, c):
    S, s = c["S"], c["s"]
    top = lambda x: 6.9 + 0.36 * x
    xs = [2.4, 1.55, 0.7, -0.15, -1.0, -1.85, -2.7]
    hs = [3.8, 6.0, 7.6, 8.2, 7.6, 6.0, 3.6]
    with m.bone("Body"):
        base = [(x, top(x) - 0.35) for x in xs]
        tips = [(x - 0.35, top(x) - 0.35 + h) for x, h in zip(xs, hs)]
        pts2 = [(base[0][0] + 0.5, base[0][1])] + tips + [(base[-1][0] - 0.5, base[-1][1])]
        m.slab("Sail", [(x * s, z * s) for x, z in pts2], 0.26 * s, SAIL, origin=(0, 0, 0), xaxis=(1, 0, 0), yaxis=(0, 0, 1))
        band = [(x, z - 2.0 * (h / 8.2)) for (x, z), h in zip(tips, hs)]
        m.slab("SailBand", [(x * s, z * s) for x, z in (tips + band[::-1])], 0.32 * s, SAIL_T, origin=(0, 0, 0), xaxis=(1, 0, 0), yaxis=(0, 0, 1))
        for k, ((bx, bz), (tx, tz)) in enumerate(zip(base, tips)):
            m.seg(f"Spine{k}", S(bx, 0, bz), S(tx, 0, tz + 0.2), 0.24 * s, 0.14 * s, SPINE, d0=0.4 * s, d1=0.3 * s, studs=False)
        for t in (1, -1):
            for j, x in enumerate((1.4, 0.4, -0.6, -1.6)):
                m.box(f"Stripe{t}{j}", S(x, t * 1.94, 5.3 + x * 0.3), (0.35 * s, 0.1 * s, 1.8 * s), TEAL_D, rot=Ry(-0.35), studs=False)
    for i, (x, z, w) in enumerate(((-4.4, 5.4, 2.4), (-6.3, 5.6, 1.8), (-8.0, 6.0, 1.2))):
        with m.bone(f"Tail{i + 1}"):
            for k in range(2): m.box(f"TailScute{i}{k}", S(x + 0.5 - k, 0, z + w * 0.52), (0.5 * s, 0.4 * s, 0.35 * s), TEAL_D, top=(0.6, 0.6), studs=False)
    H_ = S(3.2, 0, 7.5)
    with m.bone("Head"), m.frame(pivot=H_, rot=Ry(-0.22)):
        for t in (1, -1): m.box(f"Nostril{t}", S(8.2, t * 0.55, 9.3), (0.5 * s, 0.4 * s, 0.35 * s), TEAL_D, studs=False)
        m.box("BrowRidge", S(4.4, 0, 9.85), (1.6 * s, 3.0 * s, 0.4 * s), TEAL_D, top=(0.8, 0.9), studs=False)
        # fish clamped across the open jaws
        fc = S(8.0, 0, 6.15)
        m.box("Fish", fc, (1.2 * s, 4.6 * s, 1.15 * s), FISH, top=(0.8, 0.85), bot=(0.8, 0.85), studs=False)
        m.box("FishBack", fc + S(0, 0, 0.55), (0.9 * s, 3.8 * s, 0.3 * s), FISH_D, studs=False)
        m.slab("FishTail", [(0, 0), (1.1 * s, 0.85 * s), (1.1 * s, -0.85 * s)], 0.2 * s, FISH_D, origin=fc + S(0, -2.3, 0), xaxis=(0, -1, 0), yaxis=(0, 0, 1))
        for t in (1, -1): m.box(f"FishEye{t}", fc + S(t * 0.66, 1.65, 0.2), (0.05 * s, 0.35 * s, 0.35 * s), PUPIL, studs=False)

out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "models", "TFFA", "Spinosaurus")
build("Spinosaurus", theropod, dict(s=1.05, snout=1.55, c1=TEAL, c2=TEAL_D, belly=rgb(240, 232, 210), jitter=0.07, x=[spino_parts]), out,
      views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 50), ("ref", 55, 6, 50)])
