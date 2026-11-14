"""TFFA Compy (Compsognathus, DinoLand) - hero build v2 on the user-approved T-Rex body (theropod archetype, scaled small).
v1 (a lean, spindly custom biped) was rejected; the T-Rex and Ankylosaurus were approved -> chunky TFFA proportions.

Reference analysis (iconic Compsognathus - the cheeky pack scavenger):
1. Silhouette: a pint-sized T-Rex: huge head, chunky body, thick legs, long tail - small but bold.
2. Head: the approved open-jawed T-Rex head, big eye under a heavy brow.
3. Signature (the twist): a little thief - a STOLEN DRUMSTICK clamped across its jaws; a spiky orange crest from the
   brow down the neck; dark stripes across the back and tail.
4. Colours: lime green, dark green stripes, yellow belly, orange crest, cream bone + brown meat.
Bones (theropod): Body, Neck, Head, Jaw, Tail1-4, Leg_L/R, Arm_L/R. Studded."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_archetypes import *

GRN, GRN_D, BELLY, CREST, MEAT, BONEC = rgb(124, 196, 72), rgb(50, 112, 40), rgb(246, 224, 124), rgb(246, 130, 40), rgb(198, 108, 56), rgb(248, 242, 226)

def compy_parts(m, c):
    S, s = c["S"], c["s"]
    with m.bone("Body"):
        for k, x in enumerate((1.4, 0.4, -0.6, -1.6)):
            m.box(f"Stripe{k}", S(x, 0, 6.95 + 0.36 * x), (0.5 * s, 3.4 * s, 0.25 * s), GRN_D, rot=Ry(-0.35), studs=False)
    for i, (x, z, w) in enumerate(((-4.4, 5.4, 2.4), (-6.3, 5.6, 1.8), (-8.0, 6.0, 1.2))):
        with m.bone(f"Tail{i + 1}"):
            m.box(f"TailStripe{i}", S(x, 0, z + w * 0.5), (0.5 * s, w * 0.9 * s, 0.2 * s), GRN_D, studs=False)
    with m.bone("Neck"):
        for k, t in enumerate((0.2, 0.55, 0.9)):
            p = S(1.8 + 1.2 * t - 0.6, 0, 6.0 + 1.6 * t + 1.45)
            m.spike(f"NeckCrest{k}", p, p + S(-0.9, 0, 1.2), 0.38 * s, CREST, flat=0.5)
    H_ = S(3.2, 0, 7.5)
    with m.bone("Head"), m.frame(pivot=H_, rot=Ry(-0.22)):
        for k, x in enumerate((4.6, 3.8, 3.0)):
            m.spike(f"HeadCrest{k}", S(x, 0, 9.75), S(x - 0.8, 0, 10.9 - 0.2 * k), 0.42 * s, CREST, flat=0.5)
        d0, d1 = S(6.4, -1.9, 7.1), S(6.4, 1.6, 7.1)                    # stolen drumstick across the open jaws
        m.seg("BoneShaft", d0, d1, 0.42 * s, 0.42 * s, BONEC, studs=False)
        for k, dz in enumerate((0.25, -0.25)): m.box(f"BoneKnob{k}", d0 + S(0, -0.15, dz), (0.55 * s, 0.5 * s, 0.6 * s), BONEC, studs=False)
        m.box("Meat", d1 + S(0, 0.55, 0), (1.5 * s, 1.4 * s, 1.5 * s), MEAT, top=(0.8, 0.8), bot=(0.8, 0.8), studs=False)
        m.box("MeatBite", d1 + S(0.6, 0.7, 0.45), (0.4 * s, 0.6 * s, 0.5 * s), rgb(242, 200, 170), studs=False)

out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "models", "TFFA", "Compy")
build("Compy", theropod, dict(s=0.4, snout=1.05, c1=GRN, c2=GRN_D, belly=BELLY, jitter=0.06, x=[compy_parts]), out,
      views=[("hero", 40, 10, 45), ("front", 0, 8, 45), ("side", 90, 4, 50), ("ref", 35, 4, 50)])
