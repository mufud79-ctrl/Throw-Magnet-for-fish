"""TFFA Gorilla (Jungle). Compact mound: big crested head low at the front, dome back, massive short arms,
legs mostly hidden. Face = huge white eyes + thick angry black brows above a big muzzle block."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

FUR, FACE, CHEST, SOLE = rgb(62, 62, 70), rgb(98, 92, 98), rgb(44, 44, 52), rgb(40, 40, 46)
m = Model("Gorilla", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.6, chamfer=0.2)

# body mass: one big wedge that is tallest at the head and slopes down to the rump
# exact corners (hexa) give full control of the back line: high at the shoulders, sloping to the rump
m.hexa("Back", [(-3.7, -2.9, 1.6), (2.4, -3.0, 1.6), (2.4, 3.0, 1.6), (-3.7, 2.9, 1.6),
                (-3.1, -2.1, 5.0), (1.6, -2.5, 7.7), (1.6, 2.5, 7.7), (-3.1, 2.1, 5.0)], FUR)
m.box("Shoulders", (1.6, 0, 5.4), (3.0, 6.6, 3.4), FUR, top=(0.7, 0.75))
m.box("Hips", (-2.3, 0, 2.3), (3.0, 5.4, 2.8), FUR, top=(0.85, 0.9))
m.box("Chest", (2.9, 0, 3.8), (1.6, 3.6, 2.8), CHEST, rot=Ry(-0.2), studs=False)

# head: the highest point; crest slopes back from the brows; vertical face plate carries the eyes
with m.frame(pivot=(3.2, 0, 5.2), scale=1.25, move=(0.15, 0, -0.1)):   # big TFFA head
    m.box("Head", (2.7, 0, 6.6), (3.4, 3.6, 2.6), FUR, top=(0.42, 0.8), shift=(-0.95, 0))
    m.box("Face", (4.0, 0, 6.8), (1.0, 3.4, 2.1), FUR)
    m.box("Muzzle", (5.0, 0, 5.45), (2.8, 3.0, 1.9), FACE, top=(0.72, 0.85), shift=(-0.25, 0))
    for s in (1, -1):
        m.box(f"Nostril{s}", (6.1, s * 0.45, 5.95), (0.16, 0.45, 0.24), NOSE, studs=False, chamfer=0.05)
        m.box(f"Ear{s}", (2.6, s * 1.78, 6.9), (0.45, 0.2, 0.75), CHEST, studs=False, rot=Ry(0.3))
    m.eyes((4.52, 0.8, 6.72), size=(1.5, 1.2), pupil=0.62, look=(0.8, -0.15), angry=0.2,
           brow_up=0.6, brow_h=0.42, brow_w=1.12, depth=0.22)

for s in (1, -1):
    sh, el, ha = V(2.0, s * 2.95, 5.4), V(2.7, s * 3.3, 3.0), V(3.0, s * 3.2, 0.9)
    m.seg(f"UpperArm{s}", sh, el, 3.0, 2.7, FUR)
    m.seg(f"Forearm{s}", el + V(0, 0, 0.3), ha, 2.8, 3.1, FUR)
    m.box(f"Fist{s}", (3.25, s * 3.2, 0.55), (3.0, 3.0, 1.1), FUR, top=(0.9, 0.9))
    m.seg(f"Leg{s}", (-2.3, s * 2.4, 2.2), (-2.0, s * 2.6, 0.5), 2.6, 2.3, FUR)
    m.box(f"Foot{s}", (-1.7, s * 2.6, 0.35), (2.6, 2.0, 0.7), SOLE, studs=False)

m.done(views=[("hero", 50, 10, 40), ("rainbow", 55, 4, 30, "rainbow"), ("side", 90, 5, 50), ("front", 0, 8, 50)])
