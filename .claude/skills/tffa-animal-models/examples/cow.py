"""TFFA Cow (Farm) - the generic studded QUADRUPED template: copy this for dogs, pigs, sheep, horses, cats, bears...
Big head (about 45% of the height) with a light muzzle block, front-facing block eyes, short thick legs, chunky body."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

BODY, SPOT, MUZ, HOOF = rgb(246, 246, 244), rgb(40, 40, 46), rgb(250, 168, 180), rgb(60, 52, 50)
m = Model("Cow", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.5, chamfer=0.16)

# body: one chunky box, slightly higher at the shoulders; patches are thin plates on the surface
m.box("Body", (-0.3, 0, 3.1), (5.2, 3.4, 2.8), BODY, top=(0.92, 0.9))
m.box("Patch1", (-1.4, 1.72, 3.3), (1.8, 0.1, 1.5), SPOT)
m.box("Patch2", (0.9, -1.72, 3.0), (1.6, 0.1, 1.3), SPOT)
m.box("Patch3", (-0.6, 0, 4.52), (1.6, 1.8, 0.1), SPOT)
m.box("Udder", (-1.2, 0, 1.6), (1.2, 1.2, 0.5), MUZ, studs=False)

# legs: short and thick, dark hooves
for sx in (1, -1):
    for s in (1, -1):
        x = sx * 1.8 - 0.3
        m.box(f"Leg{sx}{s}", (x, s * 1.1, 1.05), (1.1, 1.1, 2.1), BODY)
        m.box(f"Hoof{sx}{s}", (x + 0.05, s * 1.1, 0.25), (1.2, 1.2, 0.5), HOOF, studs=False)

# head: big block in front of the body, pink muzzle, horns, ears
with m.frame(pivot=(2.6, 0, 4.0), scale=1.15):
    m.box("Head", (3.0, 0, 4.4), (2.2, 2.8, 2.4), BODY)
    m.box("Muzzle", (4.35, 0, 3.75), (0.9, 2.4, 1.3), MUZ, top=(0.9, 0.95))
    for s in (1, -1):
        m.box(f"Nostril{s}", (4.82, s * 0.5, 3.85), (0.08, 0.26, 0.3), dk(MUZ, 0.6), studs=False, chamfer=0.05)
        m.box(f"Ear{s}", (2.6, s * 1.75, 4.9), (0.5, 0.9, 0.35), BODY, rot=Rx(s * 0.3))
        m.spike(f"Horn{s}", (2.7, s * 0.8, 5.5), (2.6, s * 1.25, 6.3), 0.22, HORN, sides=5)
    m.box("HeadPatch", (3.2, 0.9, 5.62), (1.0, 0.9, 0.1), SPOT)
    m.eyes((4.12, 0.62, 4.65), size=(0.85, 0.85), pupil=0.62, look=(0.3, -0.1), angry=-0.1, brow_h=0.3, brow_up=0.68)

# tail with a dark tuft
m.seg("Tail", (-2.9, 0, 4.0), (-3.3, 0, 2.6), 0.3, 0.25, BODY, studs=False)
m.box("TailTuft", (-3.35, 0, 2.3), (0.5, 0.5, 0.6), SPOT, studs=False)

m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45)])
