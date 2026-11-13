"""Cannon Tame animals: blocky Roblox-part style (blocky.py). Run: python cannon_animals.py [Name ...] [--no-render]
Output: models/CannonTame/Animals/<Name>/"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Matrix
from blocky import *

def Rz(a): return Matrix.Rotation(a, 3, "Z")
def Ry(a): return Matrix.Rotation(a, 3, "Y")
def Rx(a): return Matrix.Rotation(a, 3, "X")
VIEWS = {"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50), "side": ((12.5, 0, 0.6), (0, 0, 0.2), 50), "front": ((2.5, 11, 2.0), (0, 0.6, 0.3), 45)}

def trex(f):
    G1, G2, BEL, MOUTH, IVORY, EYE = rgb(92, 140, 64), rgb(62, 94, 50), rgb(218, 198, 140), rgb(130, 36, 40), rgb(248, 240, 220), rgb(250, 200, 40)
    T = "top"
    # horizontal body balanced on the hips
    f.block("Body", V(0.6, 0, 4.7), (4.4, 2.8, 2.8), G1, Ry(-0.08), studs=T)
    f.block("Chest", V(2.6, 0, 4.95), (1.9, 2.5, 2.5), G1, Ry(-0.25), studs=T)
    f.block("Belly", V(1.0, 0, 3.32), (3.6, 2.4, 0.5), BEL, Ry(-0.08), studs=False)
    f.block("Neck", V(3.55, 0, 5.85), (1.7, 2.1, 2.1), G1, Ry(-0.6), studs=T)
    # massive head: skull, sloped snout, brow ridges, slit eyes, nostrils
    f.block("Skull", V(5.4, 0, 6.65), (3.6, 2.3, 1.7), G1, studs=False)
    f.wedge("SnoutSlope", V(6.2, 0, 7.7), (1.8, 2.3, 0.4), G1)
    f.block("Mouth", V(5.6, 0, 5.75), (3.0, 1.9, 0.4), MOUTH, studs=False)
    hinge = V(3.9, 0, 5.95); X = Matrix.Translation(hinge) @ Ry(0.2).to_4x4() @ Matrix.Translation(-hinge)
    f.block("Jaw", X @ V(5.5, 0, 5.4), (3.3, 2.1, 0.8), G1, Ry(0.2), studs=False)
    f.block("Throat", X @ V(5.0, 0, 4.98), (2.4, 1.7, 0.1), BEL, Ry(0.2), studs=False)
    for sy in (-1, 1):
        f.block(f"Brow{sy}", V(4.55, sy * 1.0, 7.55), (1.1, 0.4, 0.35), G2, Ry(0.15), studs=False)
        f.block(f"Eye{sy}", V(4.65, sy * 1.16, 7.12), (0.45, 0.06, 0.32), EYE, studs=False)
        f.block(f"Pupil{sy}", V(4.68, sy * 1.2, 7.12), (0.12, 0.04, 0.3), BLACK, studs=False)
        f.block(f"Nostril{sy}", V(6.95, sy * 0.5, 7.53), (0.25, 0.22, 0.06), BLACK, studs=False)
        for k in range(6): f.wedge(f"ToothU{sy}{k}", V(4.4 + 0.5 * k, sy * 0.95, 5.65), (0.26, 0.26, 0.38), IVORY, Ry(-math.pi / 2))
        for k in range(5): f.wedge(f"ToothL{sy}{k}", X @ V(4.6 + 0.5 * k, sy * 0.9, 5.88), (0.24, 0.24, 0.34), IVORY, Ry(0.2) @ Ry(math.pi / 2))
        # tiny two-claw arms
        f.block(f"UpperArm{sy}", V(3.05, sy * 1.35, 4.25), (0.8, 0.35, 0.35), G1, Ry(0.8), studs=False)
        f.block(f"Forearm{sy}", V(3.45, sy * 1.35, 3.95), (0.6, 0.3, 0.3), G1, Ry(-0.3), studs=False)
        for c in (-0.1, 0.1): f.wedge(f"ArmClaw{sy}{c}", V(3.8, sy * 1.35 + c, 3.85), (0.25, 0.14, 0.2), IVORY, Ry(-math.pi / 2))
        # powerful legs: thigh, shin, foot, three clawed toes
        f.block(f"Thigh{sy}", V(-0.2, sy * 1.6, 3.7), (2.3, 1.2, 2.7), G1, Ry(0.25), studs=T)
        f.block(f"Shin{sy}", V(-0.5, sy * 1.6, 1.6), (1.0, 1.0, 2.5), G1, Ry(-0.3), studs=False)
        f.block(f"Foot{sy}", V(0.35, sy * 1.6, 0.25), (2.0, 1.25, 0.5), G2, studs=T)
        for k in (-1, 0, 1): f.wedge(f"Toe{sy}{k}", V(1.5, sy * 1.6 + k * 0.38, 0.22), (0.4, 0.3, 0.44), IVORY)
    # long straight counterweight tail
    tail = [(-2.6, 4.8, 2.4, 2.4), (-4.6, 4.65, 2.2, 1.8), (-6.4, 4.45, 2.0, 1.35), (-8.0, 4.25, 1.8, 0.9), (-9.3, 4.05, 1.3, 0.55)]
    for k, (x, z, L, s_) in enumerate(tail): f.block(f"Tail{k}", V(x, 0, z), (L, s_, s_), G1, studs=T)
    # dark stripe bands wrapping the back and tail
    for k, (x, z, w, h, rot) in enumerate([(1.4, 4.7, 2.86, 2.86, -0.08), (-0.4, 4.7, 2.86, 2.86, -0.08), (-2.6, 4.8, 2.46, 2.46, 0), (-4.6, 4.65, 1.86, 1.86, 0), (-6.4, 4.45, 1.41, 1.41, 0), (-8.0, 4.25, 0.96, 0.96, 0)]):
        f.block(f"Stripe{k}", V(x, 0, z + h * 0.12), (0.5, w, h * 0.78), G2, Ry(rot), studs=False)

ANIMALS = [("TRex", trex)]

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for name, fn in ANIMALS:
        if want and name not in want: continue
        f = Brick(name, "CannonTame/Animals"); fn(f); f.done(None, VIEWS)
