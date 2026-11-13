"""TFFA T-Rex (Prehistoric). Reference: the game icon. Golden studded blocks, huge head with the mouth wide open,
big white blade teeth, red mouth + pink tongue, white throat/jaw underside, ridge bumps on the snout,
square side eye with a heavy brow. Tiny arms, thick legs, long stepped tail."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

GOLD, GOLD2, CREAM = rgb(222, 150, 40), rgb(160, 96, 30), rgb(244, 240, 230)
m = Model("TRex", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.7, chamfer=0.14, jitter=0.09)

# ---- body, legs, tail
m.box("Body", (0, 0, 5.0), (5.4, 3.8, 3.8), GOLD, rot=Ry(-0.35), top=(0.85, 0.85))
m.box("Belly", (0.8, 0, 4.2), (3.6, 3.0, 2.6), CREAM, rot=Ry(-0.45), studs=False)
m.seg("Neck", (1.8, 0, 6.0), (3.0, 0, 7.6), 3.0, 2.6, GOLD, d0=3.2, d1=2.8)
m.chain("Tail", [(-2.3, 0, 5.3), (-4.4, 0, 5.4), (-6.3, 0, 5.6), (-8.0, 0, 6.0), (-9.3, 0, 6.5)],
        [3.0, 2.4, 1.8, 1.2, 0.6], GOLD)
for s in (1, -1):
    m.box(f"Thigh{s}", (-0.6, s * 1.9, 4.0), (2.8, 1.5, 3.4), GOLD, rot=Ry(0.25), top=(0.85, 0.9))
    m.seg(f"Shin{s}", (-0.9, s * 2.0, 2.6), (-0.3, s * 2.0, 0.7), 1.3, 1.1, GOLD)
    m.box(f"Foot{s}", (0.3, s * 2.0, 0.4), (2.4, 1.6, 0.8), GOLD2)
    for k in (-1, 0, 1):
        m.spike(f"Toe{s}{k}", (1.4, s * 2.0 + k * 0.5, 0.3), (1.9, s * 2.0 + k * 0.6, 0.12), 0.18, CLAW)
    # tiny arms with two claws
    m.seg(f"Arm{s}", (2.4, s * 1.5, 5.1), (3.0, s * 1.6, 4.3), 0.6, 0.5, GOLD)
    for k in (-1, 1):
        m.spike(f"ArmClaw{s}{k}", (3.05, s * 1.6 + k * 0.15, 4.2), (3.35, s * 1.6 + k * 0.18, 3.85), 0.1, CLAW)

# ---- head: upper skull opens up, lower jaw drops (mouth wide open like the icon)
H = V(3.2, 0, 7.5)                                     # jaw hinge
with m.frame(pivot=H, rot=Ry(-0.22)):                  # upper head tilted up
    m.box("Skull", (3.9, 0, 8.6), (2.8, 3.0, 2.4), GOLD, top=(0.9, 0.9))
    m.box("Snout", (6.2, 0, 8.45), (3.6, 2.5, 1.8), GOLD, top=(0.92, 0.9), bot=(1, 1))
    m.box("UpperGum", (6.0, 0, 7.5), (3.8, 2.2, 0.3), MOUTH, studs=False)
    for k, x in enumerate((5.0, 6.0, 7.0)):              # ridge bumps (crenellations) along the snout top
        m.box(f"Ridge{k}", (x, 0, 9.5 - 0.05 * k), (0.75, 1.7, 0.55), GOLD, studs=False)
    for s in (1, -1):
        for k, x in enumerate((4.6, 5.4, 6.2, 7.0, 7.7)):
            L = 1.2 if k in (1, 3) else 0.95
            m.spike(f"ToothU{s}{k}", (x, s * 1.02, 7.45), (x + 0.04, s * 0.98, 7.45 - L), 0.42, TOOTH, flat=0.3)
    m.box("EyeBase", (4.2, 0, 9.0), (1.6, 3.4, 1.5), GOLD, studs=False)        # socket bulge the eye sits on
    m.eyes((4.3, 1.72, 9.0), facing=(0.25, 1, 0), size=(1.35, 1.25), pupil=0.72, look=(0.0, 0.0), angry=0.0,
           brow_col=GOLD, brow_h=0.42, brow_up=0.66, brow_w=1.3, depth=0.36)
with m.frame(pivot=H, rot=Ry(0.55)):                   # lower jaw dropped
    m.box("Jaw", (5.4, 0, 6.75), (4.4, 2.3, 1.1), CREAM, bot=(0.95, 0.9))
    m.box("Tongue", (5.2, 0, 7.42), (3.6, 1.4, 0.3), TONGUE, studs=False)
    m.box("TongueBack", (3.7, 0, 7.75), (1.0, 1.3, 0.6), TONGUE, studs=False, rot=Ry(0.4))
    m.box("LowerGum", (5.4, 0, 7.3), (4.2, 2.0, 0.2), MOUTH, studs=False)
    for s in (1, -1):
        for k, x in enumerate((4.0, 4.65, 5.3, 5.95, 6.6, 7.2)):
            m.spike(f"ToothL{s}{k}", (x, s * 0.95, 7.3), (x - 0.04, s * 0.92, 7.95), 0.3, TOOTH, flat=0.3)
# throat fills the gap under the open mouth
m.box("Throat", (3.4, 0, 6.5), (2.0, 2.6, 2.0), CREAM, rot=Ry(0.2))
m.box("MouthBack", (3.9, 0, 7.5), (1.0, 2.0, 1.4), MOUTH, studs=False)

m.done(views=[("hero", 40, 10, 45), ("side", 90, 4, 50),
              ("icon", 35, -6, 50, "plain", (5.0, 0, 7.9, 3.4))])
