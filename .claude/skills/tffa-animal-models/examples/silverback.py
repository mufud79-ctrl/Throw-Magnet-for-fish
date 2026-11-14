"""TFFA Gorilla (Jungle, Cannon Tame) - hero build on top of the reviewed TFFA gorilla (examples/gorilla.py, which
stays the untouched style reference).

Reference analysis (an enraged silverback, most important first):
1. Silhouette: knuckle-walking mound - head + shoulders are the highest point, the back slopes down to a low rump,
   arms are massive pillars longer than the legs, legs mostly hidden. Same mass as the in-game TFFA gorilla.
2. Head: tall sagittal crest, heavy brow ridge, angry white block eyes under thick black brows; the mouth ROARS open
   (crimson mouth, big white canines top and bottom) - the aggression the user asks for on big beasts.
3. Signature: the silver saddle across the lower back, a deep chest with two pec plates, round deltoids on top of the
   arms, knuckles + thumbs on the fists, bare dark feet with toes.
4. Colours: charcoal fur, silver saddle, dark leathery skin (chest, face plate, hands, feet), lighter grey muzzle.
5. Details: fur tufts on the forearms, two scars on the left shoulder.
Bones: Body, Head, Jaw, Leg_FL/FR (arms), Leg_BL/BR. Studded."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

FUR, FACE, CHEST, SOLE = rgb(62, 62, 70), rgb(98, 92, 98), rgb(44, 44, 52), rgb(40, 40, 46)
SILVER, SILVER_D, SCAR = rgb(150, 152, 164), rgb(120, 122, 134), rgb(96, 80, 88)
m = Model("Gorilla", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.6, chamfer=0.2)
LR = lambda s: "L" if s > 0 else "R"
NS = dict(studs=False)

m.bone("Body", (-0.5, 0, 3.6)).__enter__()
m.hexa("Back", [(-3.7, -2.9, 1.6), (2.4, -3.0, 1.6), (2.4, 3.0, 1.6), (-3.7, 2.9, 1.6),
                (-3.1, -2.1, 5.0), (1.6, -2.5, 7.7), (1.6, 2.5, 7.7), (-3.1, 2.1, 5.0)], FUR)
m.box("Shoulders", (1.6, 0, 5.4), (3.0, 6.6, 3.4), FUR, top=(0.7, 0.75))
m.box("Hips", (-2.3, 0, 2.3), (3.0, 5.4, 2.8), FUR, top=(0.85, 0.9))
# silver saddle: a lighter plate lying on the back slope plus a silver rump cap
m.hexa("Saddle", [(-3.5, -2.62, 3.5), (0.0, -2.88, 3.5), (0.0, 2.88, 3.5), (-3.5, 2.62, 3.5),
                  (-3.27, -2.27, 5.17), (0.0, -2.52, 6.97), (0.0, 2.52, 6.97), (-3.27, 2.27, 5.17)], SILVER)
m.box("SaddleRump", (-3.05, 0, 4.55), (1.3, 4.0, 1.2), SILVER_D, rot=Ry(-0.3), top=(0.7, 0.85))
# chest: dark leathery plate with two pecs
m.box("Chest", (2.9, 0, 3.8), (1.6, 3.6, 2.8), CHEST, rot=Ry(-0.2), **NS)
for s in (1, -1):
    m.box(f"Pec{s}", (3.45, s * 0.86, 4.45), (0.7, 1.55, 1.25), CHEST, rot=Ry(-0.2), top=(0.85, 0.9), **NS)
    m.box(f"Ab{s}", (3.25, s * 0.45, 3.05), (0.5, 0.75, 0.6), CHEST, rot=Ry(-0.2), **NS)

# head: highest point, crest slopes back, vertical face plate carries the eyes, roaring jaw on its own bone
with m.bone("Head", (3.3, 0, 5.4)), m.frame(pivot=(3.2, 0, 5.2), scale=1.25, move=(0.15, 0, -0.1)):
    m.box("Head", (2.7, 0, 6.6), (3.4, 3.6, 2.6), FUR, top=(0.42, 0.8), shift=(-0.95, 0))
    m.box("Crest", (2.3, 0, 7.95), (2.2, 1.0, 0.8), FUR, top=(0.5, 0.6), shift=(-0.4, 0))
    m.box("Face", (4.0, 0, 6.8), (1.0, 3.4, 2.1), CHEST, **NS)
    m.box("BrowRidge", (4.45, 0, 7.62), (0.7, 3.5, 0.55), FUR, top=(0.75, 0.95))
    m.box("Muzzle", (5.0, 0, 5.9), (2.8, 3.0, 1.15), FACE, top=(0.72, 0.85), shift=(-0.25, 0))
    m.box("MouthIn", (4.85, 0, 5.05), (2.1, 2.5, 1.0), MOUTH, **NS)
    m.box("Tongue", (4.7, 0, 4.72), (1.6, 1.8, 0.2), TONGUE, **NS)
    for s in (1, -1):
        m.box(f"Nostril{s}", (6.1, s * 0.45, 6.15), (0.16, 0.45, 0.24), NOSE, chamfer=0.05, **NS)
        m.box(f"Ear{s}", (2.6, s * 1.78, 6.9), (0.45, 0.2, 0.75), CHEST, rot=Ry(0.3), **NS)
        m.spike(f"Fang{s}", (5.95, s * 1.05, 5.4), (6.0, s * 1.0, 4.45), 0.24, TOOTH, flat=0.45)
    m.teeth("ToothT", (6.0, -0.6, 5.35), (6.0, 0.6, 5.35), 4, 0.32, 0.13)
    m.eyes((4.52, 0.8, 6.72), size=(1.5, 1.2), pupil=0.62, look=(0.8, -0.15), angry=0.38,
           brow_up=0.6, brow_h=0.46, brow_w=1.12, depth=0.22)
    with m.bone("Jaw", (3.9, 0, 5.0)), m.frame(pivot=(3.9, 0, 5.0), rot=Ry(0.32)):
        m.box("Jaw", (4.85, 0, 4.55), (2.3, 2.7, 0.7), FACE, top=(0.95, 0.95), bot=(0.8, 0.85))
        m.box("Chin", (5.75, 0, 4.45), (0.5, 2.0, 0.6), FACE, top=(0.9, 0.9))
        m.teeth("ToothB", (5.75, -0.5, 4.95), (5.75, 0.5, 4.95), 3, 0.26, 0.12, down=False)
        for s in (1, -1):
            m.spike(f"FangB{s}", (5.7, s * 0.95, 4.85), (5.75, s * 0.95, 5.55), 0.2, TOOTH, flat=0.45)

for s in (1, -1):
    sh, el, ha = V(2.0, s * 2.95, 5.4), V(2.7, s * 3.3, 3.0), V(3.0, s * 3.2, 0.9)
    with m.bone(f"Leg_F{LR(s)}", sh):            # knuckle-walking arms use the quadruped front-leg bones
        m.box(f"Deltoid{s}", (2.05, s * 3.05, 5.75), (2.6, 1.9, 2.0), FUR, top=(0.75, 0.75), bot=(0.9, 0.9))
        m.seg(f"UpperArm{s}", sh, el, 3.0, 2.7, FUR)
        m.seg(f"Forearm{s}", el + V(0, 0, 0.3), ha, 2.8, 3.1, FUR)
        m.box(f"Fist{s}", (3.25, s * 3.2, 0.55), (3.0, 3.0, 1.1), FUR, top=(0.9, 0.9))
        for k in range(4):
            m.box(f"Knuckle{s}{k}", (4.62, s * 3.2 + (k - 1.5) * 0.68, 0.62), (0.55, 0.6, 0.95), SOLE, top=(0.8, 0.85), **NS)
        m.box(f"Thumb{s}", (4.1, s * (3.2 - 1.55), 0.45), (0.9, 0.5, 0.55), SOLE, rot=Rz(s * -0.4), **NS)
    with m.bone(f"Leg_B{LR(s)}", (-2.3, s * 2.4, 2.4)):
        m.seg(f"Leg{s}", (-2.3, s * 2.4, 2.2), (-2.0, s * 2.6, 0.5), 2.6, 2.3, FUR)
        m.box(f"Foot{s}", (-1.7, s * 2.6, 0.35), (2.6, 2.0, 0.7), SOLE, **NS)
        for k in range(3):
            m.box(f"Toe{s}{k}", (-0.25, s * 2.6 + (k - 1) * 0.6, 0.3), (0.5, 0.5, 0.55), SOLE, **NS)
for j, (x, z, w, a) in enumerate(((2.4, 6.4, 1.0, 0.5), (1.8, 5.9, 0.8, -0.3))):
    m.box(f"Scar{j}", (x, 3.05 + 0.92, z), (w, 0.1, 0.14), SCAR, rot=Ry(a), **NS)

m.gait = {"amp": 0.8}
m.done(views=[("hero", 45, 10, 45), ("front", 0, 8, 45), ("side", 90, 5, 45)])
