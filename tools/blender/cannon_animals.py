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
    G1, G2, BEL, MOUTH, IVORY = rgb(96, 182, 74), rgb(52, 120, 56), rgb(244, 222, 150), rgb(150, 36, 44), rgb(250, 244, 226)
    # body + belly
    f.block("Body", V(0, 0, 3.6), (3.8, 2.8, 2.8), G1, Ry(-0.15))
    f.block("Belly", V(0.8, 0, 2.45), (2.6, 2.4, 0.6), BEL, Ry(-0.15))
    f.block("Neck", V(1.95, 0, 4.7), (1.6, 2.0, 1.8), G1, Ry(-0.45))
    f.block("NeckBelly", V(2.45, 0, 4.2), (1.0, 1.7, 0.9), BEL, Ry(-0.45))
    # head: skull, snout, open lower jaw, mouth, teeth
    f.block("Skull", V(3.3, 0, 5.6), (2.6, 2.4, 1.7), G1, studs=False)
    f.block("Snout", V(4.75, 0, 5.45), (1.5, 2.0, 1.2), G1, studs=False)
    f.block("Mouth", V(4.0, 0, 4.75), (2.8, 1.8, 0.6), MOUTH, Ry(0.12), studs=False)
    hinge = V(2.4, 0, 4.7); X = Matrix.Translation(hinge) @ Ry(0.32).to_4x4() @ Matrix.Translation(-hinge)
    f.block("Jaw", X @ V(3.9, 0, 4.25), (3.0, 2.0, 0.7), G1, Ry(0.32), studs=False)
    f.block("JawBelly", X @ V(3.7, 0, 3.92), (2.4, 1.6, 0.1), BEL, Ry(0.32), studs=False)
    for sy in (-1, 1):
        for k in range(4):
            f.wedge(f"ToothU{sy}{k}", V(3.5 + 0.55 * k, sy * 0.8, 4.65), (0.3, 0.32, 0.45), WHITE, Ry(-math.pi / 2))
        for k in range(3):
            f.wedge(f"ToothL{sy}{k}", X @ V(3.8 + 0.6 * k, sy * 0.75, 4.75), (0.28, 0.3, 0.4), WHITE, Ry(0.32) @ Ry(math.pi / 2))
        # eyes: white + pupil + angry brow
        f.block(f"EyeW{sy}", V(3.55, sy * 1.22, 5.85), (0.75, 0.12, 0.7), WHITE, studs=False)
        f.block(f"Pupil{sy}", V(3.75, sy * 1.29, 5.8), (0.35, 0.08, 0.45), BLACK, studs=False)
        f.block(f"Brow{sy}", V(3.6, sy * 1.18, 6.35), (1.1, 0.3, 0.3), G2, Ry(0.3 if sy > 0 else 0.3) @ Rx(0), studs=False)
        f.block(f"Nostril{sy}", V(5.2, sy * 0.45, 6.08), (0.3, 0.25, 0.08), BLACK, studs=False)
        # tiny arms with claws
        f.block(f"Arm{sy}", V(1.8, sy * 1.35, 3.7), (1.0, 0.45, 0.45), G1, Ry(0.6), studs=False)
        f.block(f"Hand{sy}", V(2.2, sy * 1.35, 3.25), (0.45, 0.45, 0.6), G1, studs=False)
        f.wedge(f"Claw{sy}", V(2.45, sy * 1.35, 2.85), (0.3, 0.3, 0.3), IVORY, Ry(-math.pi / 2))
        # legs: thigh, shin, foot, toes
        f.block(f"Thigh{sy}", V(-0.5, sy * 1.45, 2.9), (1.9, 1.0, 2.2), G1, Ry(0.15))
        f.block(f"Shin{sy}", V(-0.75, sy * 1.45, 1.25), (0.9, 0.9, 1.7), G2, Ry(-0.2))
        f.block(f"Foot{sy}", V(-0.2, sy * 1.45, 0.25), (1.8, 1.1, 0.5), G2)
        for k in (-1, 0, 1):
            f.wedge(f"Toe{sy}{k}", V(0.85, sy * 1.45 + k * 0.33, 0.2), (0.4, 0.28, 0.4), IVORY)
    # tail: tapering chain of blocks
    for k, (x, z, s, rot) in enumerate([(-2.3, 3.75, 2.1, 0.1), (-3.75, 3.45, 1.6, 0.2), (-5.0, 3.05, 1.2, 0.3), (-6.05, 2.6, 0.8, 0.4)]):
        f.block(f"Tail{k}", V(x, 0, z), (2.0, s, s), G1, Ry(rot))
    # back spikes + stripes
    spine = [(1.4, 6.1), (0.5, 5.4), (-0.6, 5.25), (-1.7, 5.0), (-2.9, 4.75), (-4.1, 4.35), (-5.2, 3.8)]
    for k, (x, z) in enumerate(spine):
        s = 0.95 - 0.08 * k
        f.wedge(f"Spike{k}", V(x, 0, z), (s, 0.35, s), G2, Rz(math.pi))
    for k, x in enumerate((-0.9, 0.2, 1.2)):
        f.block(f"Stripe{k}", V(x, 0, 4.95 + 0.17 * x * 0.8), (0.35, 2.85, 0.12), G2, Ry(-0.15), studs=False)

ANIMALS = [("TRex", trex)]

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for name, fn in ANIMALS:
        if want and name not in want: continue
        f = Brick(name, "CannonTame/Animals"); fn(f); f.done(None, VIEWS)
