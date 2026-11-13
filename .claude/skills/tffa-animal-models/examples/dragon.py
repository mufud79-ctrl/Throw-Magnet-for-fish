"""TFFA Red Dragon (fantasy/high rarity). Reference: the burger thumbnail. Faceted low-poly, NO studs: red angular
body, pale pink-lilac segmented belly plates from throat to tail, white swept horns, red cheek frills, white claws,
huge raised wings (dark membrane, red arm bones, lilac wrist knobs). Stands up on four legs, chest high."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *

RED, DRED, MEM, BELLY, KNOB = rgb(188, 22, 32), rgb(130, 12, 24), rgb(118, 12, 24), rgb(214, 166, 206), rgb(200, 180, 220)
m = Model("RedDragon", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=1.0, chamfer=0.1)
NS = dict(studs=False)

LR = lambda s: "L" if s > 0 else "R"
m.bone("Body", (-0.4, 0, 3.6)).__enter__()      # rig: parts default to the Body bone
# ---- torso: chunky, chest high, hips low; big lilac belly shield covers the whole front
m.seg("Torso", (-1.2, 0, 2.6), (0.5, 0, 5.8), 3.8, 4.0, RED, d0=3.6, d1=3.2, **NS)
m.seg("Hips", (-2.0, 0, 2.2), (-0.4, 0, 3.0), 3.4, 3.4, RED, d0=2.8, d1=2.8, **NS)
m.seg("ChestPlate", (1.15, 0, 1.4), (2.05, 0, 6.0), 2.6, 2.2, BELLY, d0=0.7, d1=0.7, **NS)
m.seg("BellyPoint", (1.2, 0, 1.9), (1.4, 0, 0.15), 1.8, 0.3, BELLY, d0=0.7, d1=0.4, **NS)   # lower belly/tail tip
for k in range(3):                                         # a few big chevron segments across the belly shield
    z = 2.4 + k * 1.25
    m.box(f"BellySeg{k}", (1.5 + k * 0.2, 0, z), (0.6, 2.5 - k * 0.1, 0.14), dk(BELLY, 0.86), rot=Ry(-0.26), **NS)

# ---- neck + head (short thick neck, big angular head with a crown of frills)
m.chain("Neck", [(0.6, 0, 5.4), (1.1, 0, 7.2), (1.4, 0, 8.9)], [2.2, 1.8, 1.6], RED, bones="Neck", **NS)
m.chain("NeckBelly", [(1.75, 0, 5.6), (2.0, 0, 7.2), (2.2, 0, 8.7)], [1.7, 1.4, 1.2], BELLY, depths=[0.5, 0.5, 0.5], bones="Neck", **NS)
m.bone("Head", (1.4, 0, 8.9), "Neck2")
with m.bone("Head"), m.frame(pivot=(1.5, 0, 8.2), scale=1.25, move=(0, 0, 1.0)):
    m.box("Head", (2.0, 0, 8.9), (2.0, 2.0, 1.5), RED, top=(0.75, 0.8), **NS)
    m.box("Snout", (3.3, 0, 8.65), (1.7, 1.4, 0.95), RED, top=(0.75, 0.8), bot=(1, 0.85), **NS)
    m.box("Jaw", (2.9, 0, 8.05), (1.9, 1.25, 0.45), RED, rot=Ry(0.15), **NS)
    m.box("Mouth", (3.0, 0, 8.25), (1.7, 1.15, 0.2), MOUTH, **NS)
    for s in (1, -1):
        for k, x in enumerate((2.5, 3.0, 3.5, 3.9)):
            m.spike(f"Tooth{s}{k}", (x, s * 0.55, 8.3), (x, s * 0.53, 8.0), 0.12, TOOTH, flat=0.4)
        m.spike(f"Horn{s}", (1.6, s * 0.6, 9.5), (0.9, s * 1.2, 11.0), 0.32, HORN, sides=5)
        for k in range(4):                                # frill crown around the face
            m.spike(f"Frill{s}{k}", (1.6 - k * 0.15, s * 0.9, 9.4 - k * 0.4), (1.4 - k * 0.2, s * (1.55 - k * 0.08), 9.6 - k * 0.5), 0.26, RED)
        m.box(f"Nostril{s}", (4.15, s * 0.3, 8.9), (0.1, 0.2, 0.12), DRED, chamfer=0.05, **NS)
    m.spike("Crest", (2.2, 0, 9.55), (1.7, 0, 10.4), 0.28, RED)
    m.eyes((2.85, 0.6, 9.25), facing=(1, 0.8, 0.2), size=(0.55, 0.32), pupil=0.75, look=(0.5, 0), angry=0.45,
           white=rgb(255, 214, 60), brow_col=DRED, brow_h=0.5, brow_up=0.75, depth=0.14)

# ---- legs (front straight, hind crouched) with white claws
for s in (1, -1):
  with m.bone(f"Leg_F{LR(s)}", (0.6, s * 1.7, 4.6)):
    m.seg(f"UpperArm{s}", (0.6, s * 1.7, 4.8), (1.0, s * 2.2, 2.6), 1.5, 1.25, RED, **NS)
    m.seg(f"Forearm{s}", (1.0, s * 2.2, 2.8), (1.2, s * 2.15, 0.5), 1.15, 1.0, RED, **NS)
    m.box(f"Paw{s}", (1.4, s * 2.15, 0.3), (1.4, 1.3, 0.6), RED, top=(0.8, 0.85), **NS)
    for k in (-1, 0, 1): m.spike(f"Claw{s}{k}", (2.05, s * 2.15 + k * 0.38, 0.25), (2.4, s * 2.15 + k * 0.42, 0.05), 0.12, CLAW)
  with m.bone(f"Leg_B{LR(s)}", (-1.4, s * 1.8, 3.0)):
    m.box(f"Thigh{s}", (-1.4, s * 1.8, 2.2), (2.2, 1.2, 2.2), RED, rot=Ry(0.3), top=(0.8, 0.9), **NS)
    m.seg(f"Shin{s}", (-1.8, s * 1.9, 1.6), (-1.0, s * 1.9, 0.4), 0.9, 0.8, RED, **NS)
    m.box(f"Foot{s}", (-0.6, s * 1.9, 0.3), (1.4, 1.1, 0.6), RED, top=(0.8, 0.85), **NS)
    for k in (-1, 0, 1):
        m.spike(f"HClaw{s}{k}", (0.1, s * 1.9 + k * 0.35, 0.25), (0.45, s * 1.9 + k * 0.4, 0.05), 0.12, CLAW)

# ---- tail: back and down, belly-coloured underside, spade tip
m.chain("Tail", [(-2.6, 0, 2.6), (-4.2, 0, 1.6), (-5.6, 0, 1.0), (-7.0, 0, 0.8)], [1.8, 1.3, 0.8, 0.45], RED, bones="Tail", **NS)
with m.bone("Tail3"): m.slab("TailSpade", [(0, 0), (0.9, 0.6), (1.6, 0), (0.9, -0.6)], 0.2, RED, origin=(-7.6, 0, 0.8), xaxis=(-1, 0, 0), yaxis=(0, 1, 0))

# ---- wings: huge membranes raised up and out, facing forward (the front silhouette is mostly wing)
for s in (1, -1):
    sh, wr, tip = V(-0.6, s * 1.5, 6.2), V(-0.9, s * 2.5, 10.4), V(-1.7, s * 4.9, 15.2)
    wing = m.bone(f"Wing_{LR(s)}", sh); wing.__enter__()
    m.seg(f"WingArm{s}", sh, wr, 0.75, 0.6, RED, **NS)
    m.seg(f"WingFinger{s}", wr, tip, 0.55, 0.25, RED, **NS)
    m.ball(f"WingKnob{s}", wr + V(0.1, 0, 0.1), 0.45, KNOB)
    m.poly(f"Wing{s}", [sh, wr, tip, (-1.9, s * 5.9, 11.2), (-1.8, s * 5.4, 8.2), (-1.4, s * 4.0, 6.6), (-1.0, s * 2.6, 5.4)],
           0.2, MEM)
    for k, (p, q) in enumerate(((wr, V(-1.85, s * 5.7, 9.8)), (wr, V(-1.5, s * 4.6, 7.2)))):   # finger bones
        m.seg(f"WingBone{s}{k}", p, q, 0.3, 0.14, RED, **NS)
    wing.__exit__(None, None, None)

m.done(views=[("front", 0, 6, 45), ("hero", 40, 12, 45), ("side", 90, 4, 50)])
