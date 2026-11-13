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
VIEWS = {"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50), "side": ((12.5, 0, 0.6), (0, 0, 0.2), 50), "front": ((2.5, 11, 2.0), (0, 0.6, 0.3), 45), "face": ((1.75, 3.5, 1.4), (0, 2.2, 0.92), 50)}

def trex(f):
    G1, G2, BEL, MOUTH, IVORY, EYE = rgb(92, 140, 64), rgb(62, 94, 50), rgb(218, 198, 140), rgb(130, 36, 40), rgb(248, 240, 220), rgb(250, 200, 40)
    T = "top"
    # horizontal body balanced on the hips
    f.block("Body", V(0.6, 0, 4.7), (4.4, 2.8, 2.8), G1, Ry(-0.08), studs=T)
    f.block("Chest", V(2.6, 0, 4.95), (1.9, 2.5, 2.5), G1, Ry(-0.25), studs=T)
    f.block("Belly", V(1.0, 0, 3.32), (3.6, 2.4, 0.5), BEL, Ry(-0.08), studs=False)
    f.block("Neck", V(3.55, 0, 5.85), (1.7, 2.1, 2.1), G1, Ry(-0.6), studs=T)
    # ---- head: deep cranium + wide cheeks, tapering sloped snout, hinged open jaw
    ORANGE_EYE, SOCKET, TONGUE = rgb(255, 160, 30), rgb(40, 60, 36), rgb(210, 90, 100)
    f.block("Cranium", V(4.8, 0, 6.75), (1.9, 2.5, 2.0), G1, studs=False)
    f.block("Cheeks", V(4.6, 0, 5.95), (1.4, 2.8, 1.2), G1, studs=False)
    f.block("Snout", V(6.75, 0, 6.6), (2.7, 1.9, 1.3), G1, Ry(0.05), studs=False)
    f.wedge("Bridge", V(5.95, 0, 7.48), (1.4, 2.0, 0.56), G1)
    f.block("HeadPatch", V(5.0, 0, 7.76), (1.7, 1.6, 0.06), G2, studs=False)
    f.block("Lip", V(6.65, 0, 5.98), (2.8, 1.96, 0.2), G2, studs=False)
    f.block("Mouth", V(6.4, 0, 5.62), (2.9, 1.7, 0.6), MOUTH, studs=False)
    hinge = V(4.6, 0, 5.55); X = Matrix.Translation(hinge) @ Ry(0.3).to_4x4() @ Matrix.Translation(-hinge)
    f.block("Jaw", X @ V(6.2, 0, 5.2), (3.2, 1.8, 0.62), G1, Ry(0.3), studs=False)
    f.block("Chin", X @ V(6.0, 0, 4.86), (2.6, 1.5, 0.1), BEL, Ry(0.3), studs=False)
    f.block("Tongue", X @ V(5.9, 0, 5.56), (2.0, 1.0, 0.12), TONGUE, Ry(0.3), studs=False)
    for sy in (-1, 1):
        for k in range(5):
            l = 0.62 if k == 3 else 0.45
            f.wedge(f"ToothU{sy}{k}", V(5.35 + 0.48 * k, sy * 0.82, 5.88 - l / 2), (0.34, 0.3, l), IVORY, Ry(-math.pi / 2))
        for k in range(4):
            l = 0.55 if k == 2 else 0.4; p = V(5.35 + 0.5 * k, sy * 0.72, 5.52 + l / 2)
            f.wedge(f"ToothL{sy}{k}", X @ p, (0.3, 0.28, l), IVORY, Ry(0.3) @ Ry(math.pi / 2))
        f.block(f"Socket{sy}", V(5.15, sy * 1.26, 7.05), (0.85, 0.06, 0.62), SOCKET, studs=False)
        f.block(f"Eye{sy}", V(5.2, sy * 1.29, 7.03), (0.56, 0.05, 0.46), ORANGE_EYE, studs=False)
        f.block(f"Pupil{sy}", V(5.24, sy * 1.315, 7.03), (0.14, 0.04, 0.42), BLACK, studs=False)
        f.block(f"Glint{sy}", V(5.08, sy * 1.33, 7.17), (0.1, 0.03, 0.1), WHITE, studs=False)
        f.block(f"Brow{sy}", V(5.2, sy * 1.12, 7.52), (1.3, 0.55, 0.36), G2, Ry(-0.28) @ Rx(sy * 0.12), studs=False)
        f.block(f"Nostril{sy}", V(7.8, sy * 0.45, 7.26), (0.3, 0.26, 0.06), BLACK, studs=False)
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
