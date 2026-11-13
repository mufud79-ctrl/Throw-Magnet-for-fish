"""Cannon Tame animals: blocky Roblox-part style (blocky.py). Run: python cannon_animals.py [Name ...] [--no-render]
Output: models/CannonTame/Animals/<Name>/"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Matrix
from blocky import *
from animalkit import *
from zones_blocky import seg

def Rz(a): return Matrix.Rotation(a, 3, "Z")
def Ry(a): return Matrix.Rotation(a, 3, "Y")
def Rx(a): return Matrix.Rotation(a, 3, "X")
VIEWS = {"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50), "side": ((12.5, 0, 0.6), (0, 0, 0.2), 50), "front": ((2.5, 11, 2.0), (0, 0.6, 0.3), 45), "face": ((1.75, 3.5, 1.4), (0, 2.2, 0.92), 50)}

def trex(f):
    G1, G2, BEL, MOUTH, IVORY, EYE = rgb(92, 140, 64), rgb(62, 94, 50), rgb(218, 198, 140), rgb(130, 36, 40), rgb(248, 240, 220), rgb(250, 200, 40)
    T = True   # studs on every face of the big parts
    # horizontal body balanced on the hips
    f.block("Body", V(0.6, 0, 4.7), (4.4, 2.8, 2.8), G1, Ry(-0.08), studs=T)
    f.block("Chest", V(2.6, 0, 4.95), (1.9, 2.5, 2.5), G1, Ry(-0.25), studs=T)
    f.block("Belly", V(1.0, 0, 3.32), (3.6, 2.4, 0.5), BEL, Ry(-0.08), studs=False)
    f.block("Neck", V(3.55, 0, 5.85), (1.7, 2.1, 2.1), G1, Ry(-0.6), studs=T)
    # ---- head: deep cranium + wide cheeks, tapering sloped snout, hinged open jaw
    ORANGE_EYE, SOCKET, TONGUE = rgb(255, 160, 30), rgb(40, 60, 36), rgb(210, 90, 100)
    f.block("Cranium", V(4.8, 0, 6.75), (1.9, 2.5, 2.0), G1, studs=T)
    f.block("Cheeks", V(4.6, 0, 5.95), (1.4, 2.8, 1.2), G1, studs=T)
    f.block("Snout", V(6.75, 0, 6.6), (2.7, 1.9, 1.3), G1, Ry(0.05), studs=T)
    f.wedge("Bridge", V(5.95, 0, 7.48), (1.4, 2.0, 0.56), G1)
    f.block("HeadPatch", V(5.0, 0, 7.76), (1.7, 1.6, 0.06), G2, studs=False)
    f.block("Lip", V(6.65, 0, 5.98), (2.8, 1.96, 0.2), G2, studs=False)
    f.block("Mouth", V(6.4, 0, 5.62), (2.9, 1.7, 0.6), MOUTH, studs=False)
    hinge = V(4.6, 0, 5.55); X = Matrix.Translation(hinge) @ Ry(0.3).to_4x4() @ Matrix.Translation(-hinge)
    f.block("Jaw", X @ V(6.2, 0, 5.2), (3.2, 1.8, 0.62), G1, Ry(0.3), studs=T)
    f.block("Chin", X @ V(6.0, 0, 4.86), (2.6, 1.5, 0.1), BEL, Ry(0.3), studs=False)
    f.block("Tongue", X @ V(5.9, 0, 5.56), (2.0, 1.0, 0.12), TONGUE, Ry(0.3), studs=False)
    for sy in (-1, 1):
        for k in range(6):                           # upper row: sharp, evenly spaced, growing to a fang
            x = 5.15 + 0.46 * k; l = 0.34 + 0.05 * k + (0.18 if k == 4 else 0); top = V(x, sy * 0.8, 5.9)
            f.cyl(f"ToothU{sy}{k}", top, top - V(0, 0, l), 0.15 + 0.01 * k, IVORY, 4, r1=0.0)
        for k in range(5):                           # lower row on the hinged jaw
            x = 5.3 + 0.46 * k; l = 0.3 + 0.04 * k + (0.14 if k == 3 else 0); base = V(x, sy * 0.7, 5.5)
            f.cyl(f"ToothL{sy}{k}", X @ base, X @ (base + V(0, 0, l)), 0.14, IVORY, 4, r1=0.0)
    for k, yy in enumerate((-0.45, 0.0, 0.45)):      # incisors across the snout tip
        top = V(7.95, yy, 5.92); f.cyl(f"Incisor{k}", top, top - V(0, 0, 0.32), 0.12, IVORY, 4, r1=0.0)
    for sy in (-1, 1):
        f.block(f"Socket{sy}", V(5.15, sy * 1.26, 7.05), (0.85, 0.06, 0.62), SOCKET, studs=False)
        f.block(f"Eye{sy}", V(5.2, sy * 1.29, 7.03), (0.56, 0.05, 0.46), ORANGE_EYE, studs=False)
        f.block(f"Pupil{sy}", V(5.24, sy * 1.315, 7.03), (0.14, 0.04, 0.42), BLACK, studs=False)
        f.block(f"Glint{sy}", V(5.08, sy * 1.33, 7.17), (0.1, 0.03, 0.1), WHITE, studs=False)
        f.block(f"Brow{sy}", V(5.25, sy * 1.12, 7.45), (1.35, 0.55, 0.36), G2, Ry(0.34) @ Rx(sy * 0.12), studs=False)
        f.block(f"Nostril{sy}", V(7.8, sy * 0.45, 7.26), (0.3, 0.26, 0.06), BLACK, studs=False)
        # tiny two-claw arms
        f.block(f"UpperArm{sy}", V(3.05, sy * 1.35, 4.25), (0.8, 0.35, 0.35), G1, Ry(0.8), studs=False)
        f.block(f"Forearm{sy}", V(3.45, sy * 1.35, 3.95), (0.6, 0.3, 0.3), G1, Ry(-0.3), studs=False)
        for c in (-0.1, 0.1): f.wedge(f"ArmClaw{sy}{c}", V(3.8, sy * 1.35 + c, 3.85), (0.25, 0.14, 0.2), IVORY, Ry(-math.pi / 2))
        # powerful legs: thigh, shin, foot, three clawed toes
        f.block(f"Thigh{sy}", V(-0.2, sy * 1.6, 3.7), (2.3, 1.2, 2.7), G1, Ry(0.25), studs=T)
        f.block(f"Shin{sy}", V(-0.5, sy * 1.6, 1.6), (1.0, 1.0, 2.5), G1, Ry(-0.3), studs=T)
        f.block(f"Foot{sy}", V(0.35, sy * 1.6, 0.25), (2.0, 1.25, 0.5), G2, studs=T)
        for k in (-1, 0, 1): f.wedge(f"Toe{sy}{k}", V(1.5, sy * 1.6 + k * 0.38, 0.22), (0.4, 0.3, 0.44), IVORY)
    # long straight counterweight tail
    tail = [(-2.6, 4.8, 2.4, 2.4), (-4.6, 4.65, 2.2, 1.8), (-6.4, 4.45, 2.0, 1.35), (-8.0, 4.25, 1.8, 0.9), (-9.3, 4.05, 1.3, 0.55)]
    for k, (x, z, L, s_) in enumerate(tail): f.block(f"Tail{k}", V(x, 0, z), (L, s_, s_), G1, studs=T)
    # dark stripe bands wrapping the back and tail
    for k, (x, z, w, h, rot) in enumerate([(1.4, 4.7, 2.86, 2.86, -0.08), (-0.4, 4.7, 2.86, 2.86, -0.08), (-2.6, 4.8, 2.46, 2.46, 0), (-4.6, 4.65, 1.86, 1.86, 0), (-6.4, 4.45, 1.41, 1.41, 0), (-8.0, 4.25, 0.96, 0.96, 0)]):
        f.block(f"Stripe{k}", V(x, 0, z + h * 0.12), (0.5, w, h * 0.78), G2, Ry(rot), studs=T)


# ====================================================================== extras (fn(f, c) closures)
IV, PINKC, TAN2, CREAM = rgb(248, 240, 220), rgb(255, 170, 185), rgb(200, 160, 100), rgb(245, 235, 210)
def comb(col=RED):
    def fn(f, c):
        f.block("Comb", c["hc"] + V(0, 0, c["hs"] * 0.62), (c["hs"] * 0.6, 0.2, c["hs"] * 0.35), col, studs=False)
        f.block("Wattle", c["hc"] + V(c["hs"] * 0.48, 0, -c["hs"] * 0.48), (0.16, 0.22, 0.32), col, studs=False)
    return fn
def tufts(col):
    def fn(f, c):
        for sy in (1, -1): f.block(f"Tuft{sy}", c["hc"] + V(-0.1, sy * c["hs"] * 0.32, c["hs"] * 0.6), (0.25, 0.16, 0.45), col, Rx(-sy * 0.3), studs=False)
    return fn
def bill_tip(col=BLACK):
    def fn(f, c): f.block("BillTip", c["hc"] + V(c["hs"] / 2 + 1.25, 0, -c["hs"] * 0.1), (0.3, 0.62, 0.62), col, studs=False)
    return fn
def ruff(col=WHITE):
    def fn(f, c): f.block("Ruff", V(c["L"] * 0.42, 0, c["z0"] + c["H"] / 2 + 0.05), (0.9, c["W"] * 0.9, 0.5), col, studs=False)
    return fn
def horns(kind, col=IV, glow=False):
    def fn(f, c):
        hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
        for sy in (1, -1):
            if kind == "cow":
                f.block(f"Horn{sy}", hc + V(-hl * 0.15, sy * (hw / 2 + 0.2), hh * 0.45), (0.22, 0.6, 0.22), col, Rx(sy * 0.5), studs=False)
                f.block(f"HornTip{sy}", hc + V(-hl * 0.15, sy * (hw / 2 + 0.42), hh * 0.75), (0.18, 0.18, 0.35), col, studs=False)
            elif kind == "goat":
                f.block(f"Horn{sy}", hc + V(-hl * 0.35, sy * hw * 0.22, hh * 0.75), (0.75, 0.2, 0.22), col, Ry(0.75), studs=False)
                f.block(f"HornTip{sy}", hc + V(-hl * 0.75, sy * hw * 0.22, hh * 0.85), (0.4, 0.18, 0.18), col, Ry(-0.3), studs=False)
            elif kind == "ram":
                for k in range(6):
                    a = k * 1.0; f.block(f"Ram{sy}{k}", hc + V(-hl * 0.15 + 0.45 * math.cos(a), sy * (hw / 2 + 0.15), hh * 0.15 + 0.45 * math.sin(a)), (0.3, 0.3, 0.3), col, Ry(-a), studs=False)
            elif kind == "ossicone":
                f.block(f"Ossicone{sy}", hc + V(-hl * 0.2, sy * hw * 0.22, hh * 0.75), (0.16, 0.16, 0.5), c["C2"], studs=False)
                f.block(f"OssiTip{sy}", hc + V(-hl * 0.2, sy * hw * 0.22, hh * 1.05), (0.26, 0.26, 0.18), BLACK, studs=False)
            elif kind == "antler":
                b = hc + V(-hl * 0.2, sy * hw * 0.3, hh * 0.5)
                f.block(f"Beam{sy}", b + V(-0.1, sy * 0.15, 0.55), (0.18, 0.18, 1.1), col, Rx(-sy * 0.35), studs=False)
                for k, z in enumerate((0.45, 0.85)): f.block(f"Tine{sy}{k}", b + V(0.15, sy * (0.3 + 0.12 * k), z + 0.1), (0.5, 0.14, 0.14), col, Ry(-0.6), studs=False)
        if kind == "rhino":
            sc, sl, sh = c["sc"], c["sl"], c["sh"]
            f.cyl("HornBig", sc + V(sl * 0.2, 0, sh / 2), sc + V(sl * 0.35, 0, sh / 2 + 1.0 * c.get("hornk", 1.0)), 0.3, col, 4, r1=0.0)
            f.cyl("HornSmall", sc + V(-sl * 0.3, 0, sh / 2), sc + V(-sl * 0.25, 0, sh / 2 + 0.5), 0.22, col, 4, r1=0.0)
        if kind == "unicorn":
            b = hc + V(hl * 0.3, 0, hh * 0.5); f.cyl("UniHorn", b, b + V(0.45, 0, 1.3), 0.18, col, 6, glow=glow, r1=0.0)
    return fn
def tusks(kind="walrus", col=IV):
    def fn(f, c):
        sc, sl, sw, sh = c["sc"], c["sl"], c["sw"], c["sh"]
        for sy in (1, -1):
            b = sc + V(sl * 0.3, sy * sw * 0.3, -sh * 0.4)
            if kind == "walrus": f.cyl(f"Tusk{sy}", b, b + V(0.15, 0, -1.2), 0.12, col, 6, r1=0.03)
            elif kind == "up": f.cyl(f"Tusk{sy}", b + V(0, sy * 0.1, 0.1), b + V(0.25, sy * 0.25, 0.55), 0.1, col, 6, r1=0.02)
            elif kind == "mammoth": seg(f, f"Tusk{sy}", [b, b + V(0.7, sy * 0.25, -0.7), b + V(1.6, sy * 0.45, -0.4), b + V(2.0, sy * 0.3, 0.4)], 0.18, col, r_end=0.07, K=6)
    return fn
def trunk(col):
    def fn(f, c):
        sc, sl = c["sc"], c["sl"]; b = sc + V(sl / 2 - 0.1, 0, 0)
        seg(f, "Trunk", [b, b + V(0.4, 0, -0.8), b + V(0.5, 0, -1.8), b + V(0.85, 0, -2.4)], 0.32, col, r_end=0.2, K=6)
    return fn
def mane_back(col, n=5):
    def fn(f, c):
        hc = c["hc"]
        for k in range(n):
            t = k / max(n - 1, 1); p = V(lerp(hc.x - c["hl"] * 0.3, c["L"] / 2 - 0.6, t), 0, lerp(hc.z + c["hh"] * 0.45, c["z0"] + c["H"] / 2, t))
            f.block(f"ManeB{k}", p + V(0, 0, 0.2), (0.6, 0.3, 0.55), col, studs=False)
    return fn
def beard(col):
    def fn(f, c): f.block("Beard", c["sc"] + V(-0.05, 0, -c["sh"] * 0.7), (0.3, 0.3, 0.5), col, studs=False)
    return fn
def wool(col=WHITE):
    def fn(f, c):
        for k, (x, y, z) in enumerate([(0.6, 1, 0.3), (-0.6, 1, 0.3), (0.6, -1, 0.3), (-0.6, -1, 0.3), (0, 0, 1), (0.8, 0, 1), (-0.8, 0, 1)]):
            f.block(f"Wool{k}", V(x * c["L"] / 2, y * (c["W"] / 2 + 0.1), c["z0"] + z * c["H"] / 2 + 0.05), (c["L"] * 0.35, 0.55 if y else c["W"] * 0.5, c["H"] * 0.35), col)
    return fn
def mask(col=BLACK, face=WHITE):
    def fn(f, c):
        hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
        f.block("FaceWhite", hc + V(hl * 0.25, 0, hh * 0.3), (hl * 0.55, hw + 0.04, hh * 0.18), face, studs=False)
        f.block("Mask", hc + V(hl * 0.22, 0, hh * 0.12), (hl * 0.6, hw + 0.05, hh * 0.32), col, studs=False)
    return fn
def eye_patches(col):
    def fn(f, c):
        hc, hs = c["hc"], c["hs"]
        for sy in (1, -1): f.block(f"Patch{sy}", hc + V(hs * 0.45, sy * hs * 0.25, hs * 0.1), (0.1, hs * 0.32, hs * 0.38), col, Rx(sy * 0.35), studs=False)
    return fn
def hump(n=1, col=None):
    def fn(f, c):
        for k in range(n): f.block(f"Hump{k}", V((0.45 - 0.9 * k) * c["L"] / 2 if n > 1 else 0, 0, c["z0"] + c["H"] / 2 + 0.45), (c["L"] * 0.32, c["W"] * 0.75, 1.0), col or c["C1"])
    return fn
def shell(col, spot=None, spikes=False):
    def fn(f, c):
        L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
        f.block("Shell", V(-0.1, 0, z0 + H * 0.35), (L * 1.05, W * 1.15, H * 0.95), col)
        f.block("ShellTop", V(-0.1, 0, z0 + H * 0.95), (L * 0.75, W * 0.8, H * 0.35), col)
        if spot:
            for k in range(6): f.block(f"Scute{k}", V(-L * 0.35 + L * 0.14 * k, 0, z0 + H * 1.13), (0.45, W * 0.55, 0.08), spot, studs=False)
        if spikes:
            for k in range(5):
                for sy in (1, -1): f.cyl(f"Spike{k}{sy}", V(-L * 0.4 + L * 0.2 * k, sy * W * 0.58, z0 + H * 0.5), V(-L * 0.4 + L * 0.2 * k, sy * (W * 0.58 + 0.6), z0 + H * 0.65), 0.18, IV, 4, r1=0.0)
    return fn
def club_tail(col):
    def fn(f, c): f.block("Club", V(-c["L"] / 2 - 4.5, 0, c["z0"] - 0.8), (0.9, 1.2, 0.8), col)
    return fn
def plates(col, n=7):
    def fn(f, c):
        for k in range(n):
            t = k / (n - 1); h = 0.6 + 1.0 * math.sin(math.pi * t); x = lerp(c["L"] / 2 - 0.4, -c["L"] / 2 - 1.5, t)
            for sy in ((1,) if k % 2 else (-1,)):
                f.wedge(f"Plate{k}", V(x, sy * 0.25, c["z0"] + c["H"] / 2 + h / 2 - 0.05 - 0.3 * max(0, t - 0.7) * 3), (0.8, 0.22, h), col, Rz(math.pi))
        for sy in (1, -1):
            for k in range(2): f.cyl(f"Thag{sy}{k}", V(-c["L"] / 2 - 4.6 + 0.5 * k, 0, c["z0"] - 0.6), V(-c["L"] / 2 - 4.9 + 0.5 * k, sy * 0.9, c["z0"] - 0.2), 0.15, IV, 4, r1=0.0)
    return fn
def frill(col, hcol=IV):
    def fn(f, c):
        hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
        f.block("Frill", hc + V(-hl * 0.55, 0, hh * 0.35), (0.35, hw * 1.7, hh * 1.6), col, Ry(0.35))
        for sy in (1, -1): f.cyl(f"BrowHorn{sy}", hc + V(0, sy * hw * 0.28, hh * 0.45), hc + V(1.1, sy * hw * 0.32, hh * 0.45 + 1.0), 0.18, hcol, 4, r1=0.0)
        f.cyl("NoseHorn", c["sc"] + V(0, 0, c["sh"] / 2), c["sc"] + V(0.15, 0, c["sh"] / 2 + 0.5), 0.16, hcol, 4, r1=0.0)
    return fn
def crest(col):
    def fn(f, c):
        hc, hh = c["hc"], c["hh"]; seg(f, "Crest", [hc + V(0, 0, hh * 0.45), hc + V(-0.9, 0, hh * 0.95), hc + V(-1.9, 0, hh * 1.25)], 0.28, col, r_end=0.18, K=6)
    return fn
def sail(col, glow=False):
    def fn(f, c):
        S = c["S"]
        for k, (x, h) in enumerate([(2.0, 1.6), (1.1, 2.6), (0.2, 3.1), (-0.8, 3.0), (-1.9, 2.4), (-2.9, 1.6), (-3.9, 0.9)]):
            f.block(f"Sail{k}", S(x, 0, 6.0 + h / 2 - (0.0 if x > -1 else 0.25)), (0.95 * c["s"], 0.25 * c["s"], h * c["s"]), col, glow=glow, studs=False)
    return fn
def wings(col, span=1.0, glow=False, membrane=None):
    def fn(f, c):
        L, W, H, z0 = c.get("L", 2), c.get("W", 1.4), c.get("H", 1.4), c.get("z0", 2)
        for sy in (1, -1):
            for k in range(3):
                f.block(f"Wing{sy}{k}", V(L * 0.1 - 0.55 * k, sy * (W / 2 + (0.9 + 0.7 * k) * span), z0 + H * 0.5 + (0.35 + 0.35 * k) * span),
                        ((1.6 - 0.25 * k) * span, (1.6 - 0.1 * k) * span, 0.18), (membrane or col) if k else col, Rx(-sy * 0.45), glow=glow, studs=False)
    return fn
def spine_spikes(col, n=6, glow=False):
    def fn(f, c):
        for k in range(n):
            x = lerp(c["L"] / 2 - 0.4, -c["L"] / 2 + 0.3, k / max(n - 1, 1)); f.wedge(f"Spine{k}", V(x, 0, c["z0"] + c["H"] / 2 + 0.25), (0.6, 0.25, 0.55), col, Rz(math.pi), glow=glow)
    return fn
def hedgehog_spikes(col):
    def fn(f, c):
        L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
        for i in range(4):
            for j in range(5):
                a = lerp(-1.3, 1.3, j / 4); x = lerp(L * 0.35, -L * 0.45, i / 3); b = V(x, W * 0.5 * math.sin(a), z0 + H * 0.4 * math.cos(a))
                d = V(-0.4, math.sin(a), math.cos(a)).normalized(); f.cyl(f"Quill{i}{j}", b, b + d * 0.55, 0.13, col, 4, r1=0.0)
    return fn
def fangs(col=IV):
    def fn(f, c):
        sc, sl, sw, sh = c["sc"], c["sl"], c["sw"], c["sh"]
        for sy in (1, -1): f.cyl(f"Fang{sy}", sc + V(sl * 0.1, sy * sw * 0.3, -sh * 0.35), sc + V(sl * 0.2, sy * sw * 0.3, -sh * 0.35 - 0.95), 0.12, col, 4, r1=0.0)
    return fn
def buck_teeth(col=WHITE):
    def fn(f, c): f.block("Teeth", c["sc"] + V(c["sl"] / 2 - 0.05, 0, -c["sh"] * 0.55), (0.1, 0.3, 0.3), col, studs=False)
    return fn
def fur_coat(col, n=6):
    def fn(f, c):
        L, W, H, z0, lh = c["L"], c["W"], c["H"], c["z0"], c["lh"]
        f.block("Coat", V(0, 0, z0 + 0.1), (L * 1.06, W * 1.1, H * 1.05), col)
        for k in range(n):
            x = lerp(-L * 0.45, L * 0.45, k / (n - 1))
            for sy in (1, -1): f.block(f"Fringe{k}{sy}", V(x, sy * W * 0.55, z0 - H * 0.55), (L / n * 0.9, 0.2, 0.6), dk(col, 0.85), studs=False)
    return fn
def glow_bits(col, n=8, seed=3, where="body", size=0.35):
    def fn(f, c):
        rng = np.random.default_rng(seed); L, W, H, z0 = c.get("L", 3), c.get("W", 1.5), c.get("H", 1.5), c.get("z0", 2)
        for k in range(n):
            sy = 1 if k % 2 else -1
            if where == "body": p = V(rng.uniform(-L / 2 + 0.3, L / 2 - 0.3), sy * (W / 2 + 0.03), z0 + rng.uniform(-H * 0.3, H * 0.35)); sz = (size * rng.uniform(0.7, 1.3), 0.06, size * rng.uniform(0.3, 1.0))
            else: p = V(rng.uniform(-L / 2 + 0.3, L / 2 - 0.3), rng.uniform(-W / 3, W / 3), z0 + H / 2 + 0.03); sz = (size, size, 0.06)
            f.block(f"Glow{k}", p, sz, col, Rx(rng.uniform(-.5, .5)) if where == "body" else None, studs=False, glow=True)
    return fn
def flame_mane(col):
    def fn(f, c):
        hc, hl, hh = c["hc"], c["hl"], c["hh"]
        for k in range(5): f.wedge(f"Flame{k}", hc + V(-hl * 0.5 - 0.45 * k, 0, hh * 0.55 - 0.12 * k), (0.8, 0.5, 0.9 - 0.08 * k), col, Rz(math.pi), glow=True)
        f.block("TailFlame", V(-c["L"] / 2 - 1.0, 0, c["z0"] + c["H"] * 0.6), (0.7, 0.5, 0.7), col, Ry(0.6), glow=True, studs=False)
    return fn
def headdress(gold=GOLD, blue=BLUE):
    def fn(f, c):
        hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
        f.block("Nemes", hc + V(-hl * 0.2, 0, hh * 0.25), (hl * 0.85, hw * 1.25, hh * 0.9), gold)
        for k in range(3): f.block(f"NemesStripe{k}", hc + V(-hl * 0.2, 0, hh * (0.0 + 0.25 * k)), (hl * 0.87, hw * 1.27, 0.1), blue, studs=False)
        for sy in (1, -1): f.block(f"Lappet{sy}", hc + V(-hl * 0.05, sy * hw * 0.6, -hh * 0.6), (0.4, 0.3, 1.0), gold)
    return fn
def astro(suit=WHITE, accent=ORANGE):
    def fn(f, c):
        hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
        f.block("Collar", hc + V(-hl * 0.45, 0, -hh * 0.35), (0.3, hw * 1.25, hh * 0.9), LGREY)
        f.block("Pack", V(-0.2, 0, c["z0"] + c["H"] / 2 + 0.4), (c["L"] * 0.45, c["W"] * 0.7, 0.8), suit)
        f.block("PackLight", V(-0.2, 0, c["z0"] + c["H"] / 2 + 0.82), (0.3, 0.3, 0.08), CYAN, studs=False, glow=True)
        f.block("SuitStripe", V(0, 0, c["z0"]), (0.35, c["W"] + 0.06, c["H"] + 0.04), accent, studs=False)
        f.cyl("Antenna", hc + V(-hl * 0.2, hw * 0.3, hh / 2), hc + V(-hl * 0.2, hw * 0.3, hh / 2 + 0.8), 0.05, LGREY, 6)
        f.ball("AntennaTip", hc + V(-hl * 0.2, hw * 0.3, hh / 2 + 0.85), 0.14, RED, glow=False)
    return fn
def hole_ring(col):
    def fn(f, c): f.cyl("Ring", V(0, 0, c["z0"] - 0.05), V(0, 0, c["z0"] + 0.05), max(c["L"], c["W"]) * 0.8, col, 24, glow=True)
    return fn
def chimera_bits(goat=CREAM, snake=GREEN):
    def fn(f, c):
        b = V(-c["L"] * 0.15, 0, c["z0"] + c["H"] / 2 + 0.55); f.block("GoatHead", b, (0.8, 0.7, 0.8), goat)
        for sy in (1, -1): f.block(f"GoatHorn{sy}", b + V(-0.35, sy * 0.25, 0.5), (0.6, 0.15, 0.18), IV, Ry(0.7), studs=False)
        t = V(-c["L"] / 2, 0, c["z0"] + c["H"] * 0.2)
        seg(f, "SnakeTail", [t, t + V(-0.8, 0, 0.5), t + V(-1.4, 0, 1.4), t + V(-1.2, 0, 2.2)], 0.22, snake, K=6)
        f.block("SnakeHead", t + V(-1.0, 0, 2.4), (0.6, 0.45, 0.35), snake, studs=False)
    return fn
def whiskers(col=CREAM):
    def fn(f, c):
        for sy in (1, -1): f.block(f"Whisk{sy}", c["sc"] + V(c["sl"] * 0.3, sy * (c["sw"] / 2 + 0.25), -0.05), (0.06, 0.55, 0.06), col, studs=False)
    return fn
def crescent(col):
    def fn(f, c): f.block("Crescent", c["hc"] + V(c["hl"] * 0.3, 0, c["hh"] * 0.52), (0.35, 0.35, 0.06), col, Rz(0.78), glow=True, studs=False)
    return fn
def talons(col=YELLOW):
    def fn(f, c):
        for sy in (1, -1): f.block(f"Talon{sy}", V(c["L"] / 2 - c["lw"] / 2 - 0.05, sy * (c["W"] / 2 - c["lw"] / 2), 0.15), (c["lw"] + 0.3, c["lw"] + 0.1, 0.3), col, studs=False)
    return fn
def beak_head(col=YELLOW):
    def fn(f, c): f.wedge("HookTip", c["sc"] + V(c["sl"] / 2 + 0.1, 0, -0.1), (0.3, c["sw"] * 0.8, 0.4), col, Ry(math.pi / 2))
    return fn
def rex_cracks(col):
    def fn(f, c):
        S = c["S"]
        for k, (x, z, a) in enumerate([(1.0, 4.6, 0.5), (-0.4, 4.4, -0.4), (-2.6, 4.7, 0.3), (-4.6, 4.5, -0.5), (0.4, 5.6, 0.1)]):
            for sy in (1, -1): f.block(f"Crack{k}{sy}", S(x, sy * 1.42, z), (1.2 * c["s"], 0.06, 0.18 * c["s"]), col, Rx(0) @ Ry(a), glow=True, studs=False)
    return fn

# ====================================================================== special body types
def frog(f, P):
    C1, BEL = P["c1"], P.get("belly", YELLOW)
    f.block("Body", V(0, 0, 0.6), (1.8, 1.6, 1.0), C1); f.block("Belly", V(0.25, 0, 0.35), (1.3, 1.5, 0.4), BEL, studs=False)
    f.block("Mouth", V(0.91, 0, 0.62), (0.04, 1.1, 0.05), dk(C1, 0.45), studs=False)
    for sy in (1, -1):
        f.block(f"EyeBump{sy}", V(0.45, sy * 0.5, 1.15), (0.6, 0.55, 0.4), C1)
        f.ball(f"EyeW{sy}", V(0.55, sy * 0.52, 1.42), 0.3, WHITE, u=12, v=8)
        f.ball(f"Pupil{sy}", V(0.78, sy * 0.52, 1.45), (0.1, 0.16, 0.18), BLACK, u=8, v=6)
        f.block(f"Thigh{sy}", V(-0.55, sy * 0.95, 0.4), (1.0, 0.45, 0.7), C1); f.block(f"BackFoot{sy}", V(-0.1, sy * 1.05, 0.08), (0.9, 0.5, 0.16), dk(C1), studs=False)
        f.block(f"FrontLeg{sy}", V(0.65, sy * 0.65, 0.25), (0.25, 0.25, 0.5), C1, studs=False)
    for fn in P.get("x", []): fn(f, dict(L=1.8, W=1.6, H=1.0, z0=0.6, C1=C1))
def seal(f, P):
    C1, C2 = P["c1"], P.get("c2", dk(P["c1"])); s = P.get("s", 1.0); S = lambda x, y, z: V(x * s, y * s, z * s); Z = lambda *a: tuple(v * s for v in a)
    for k, (x, w, h) in enumerate([(0.9, 1.6, 1.4), (-0.4, 1.4, 1.1), (-1.5, 1.0, 0.75), (-2.3, 0.6, 0.45)]): f.block(f"Body{k}", S(x, 0, h / 2), Z(1.4, w, h), C1)
    hc = S(1.9, 0, 1.45); f.block("Head", hc, Z(1.0, 1.0, 0.9), C1); f.block("Muzzle", hc + S(0.55, 0, -0.18), Z(0.35, 0.7, 0.45), P.get("muzzle", lt(C1)), studs=False)
    f.block("Nose", hc + S(0.74, 0, -0.05), Z(0.05, 0.3, 0.14), BLACK, studs=False)
    eyes(f, hc, 1.0 * s, 1.0 * s, 0.9 * s, P.get("angry", False), YELLOW, C2, 1.1, fwd=0.2)
    for sy in (1, -1):
        f.block(f"Flipper{sy}", S(1.0, sy * 0.95, 0.15), Z(0.9, 0.5, 0.15), C2, Rz(sy * 0.4), studs=False)
        f.block(f"TailFlip{sy}", S(-2.85, sy * 0.35, 0.12), Z(0.6, 0.5, 0.12), C2, Rz(sy * 0.6), studs=False)
    c = dict(hc=hc, sc=hc + S(0.55, 0, -0.18), sl=0.35 * s, sw=0.7 * s, sh=0.45 * s, C1=C1, C2=C2)
    for fn in P.get("x", []): fn(f, c)
def snake(f, P):
    C1, C2 = P["c1"], P.get("c2", dk(P["c1"]))
    for k in range(10):
        a = 2 * math.pi * k / 10; r = 1.3; f.block(f"Coil{k}", V(r * math.cos(a), r * math.sin(a), 0.35), (0.95, 0.75, 0.7), C1, Rz(a + math.pi / 2))
        if k % 2 == 0: f.block(f"Diamond{k}", V(r * math.cos(a), r * math.sin(a), 0.71), (0.45, 0.45, 0.06), C2, Rz(a + math.pi / 4), studs=False)
    pts = [V(1.3, 0, 0.5), V(0.6, 0.2, 1.3), V(0.3, 0.1, 2.2), V(0.6, 0, 2.8)]
    seg(f, "Neck", pts, 0.38, C1, r_end=0.32, K=6)
    hc = V(1.05, 0, 2.95); f.block("Head", hc, (1.0, 0.8, 0.5), C1)
    eyes(f, hc, 1.0, 0.8, 0.5, True, YELLOW, C2, 1.3, fwd=0.1)
    f.block("Tongue", hc + V(0.7, 0, -0.1), (0.45, 0.08, 0.04), RED, studs=False)
    for k in range(3): f.block(f"Rattle{k}", V(-1.0 - 0.25 * k, -0.9, 0.55 + 0.3 * k), (0.3, 0.32, 0.25), TAN, studs=False)
def scorpion(f, P):
    C1, C2 = P["c1"], P.get("c2", dk(P["c1"]))
    f.block("Body", V(0, 0, 0.6), (2.0, 1.4, 0.6), C1); f.block("Head", V(1.2, 0, 0.6), (0.6, 1.1, 0.5), C1)
    eyes(f, V(1.2, 0, 0.6), 0.6, 1.1, 0.5, True, RED, C2, 1.2, fwd=0.3)
    for sy in (1, -1):
        for k in range(4): f.block(f"Leg{sy}{k}", V(0.6 - 0.45 * k, sy * 1.0, 0.35), (0.14, 0.9, 0.14), C2, Rx(sy * 0.6), studs=False)
        f.block(f"Arm{sy}", V(1.8, sy * 0.75, 0.6), (1.0, 0.3, 0.3), C1, Rz(-sy * 0.4), studs=False)
        f.block(f"ClawA{sy}", V(2.45, sy * 1.0, 0.65), (0.7, 0.35, 0.35), C1, studs=False); f.block(f"ClawB{sy}", V(2.45, sy * 0.72, 0.6), (0.55, 0.18, 0.22), C2, studs=False)
    pts = [V(-1.0, 0, 0.7), V(-1.8, 0, 1.2), V(-2.0, 0, 2.0), V(-1.6, 0, 2.7), V(-0.9, 0, 2.9)]
    for k in range(4):
        a, b = pts[k], pts[k + 1]; d = b - a; f.block(f"TailSeg{k}", (a + b) / 2, (0.5 - 0.05 * k, 0.5 - 0.05 * k, d.length + 0.1), C1, d.to_track_quat("Z", "X").to_matrix())
    f.cyl("Stinger", V(-0.9, 0, 2.9), V(-0.45, 0, 2.5), 0.2, BLACK, 4, r1=0.0)
def blob(f, P):
    C1 = P["c1"]; L, W, H = P.get("size", (2.6, 2.0, 1.6))
    f.ball("Blob", V(0, 0, H * 0.5), (L / 2, W / 2, H / 2), C1, u=16, v=10)
    f.block("Base", V(0, 0, 0.12), (L * 0.85, W * 0.85, 0.24), dk(C1), studs=False)
    hc = V(L * 0.25, 0, H * 0.65)
    for k, sy in enumerate(P.get("eye_y", (0.35, -0.35))):
        stalk = P.get("stalks", False); p = hc + V(L * 0.2, sy, 0.15 + (0.6 if stalk else 0))
        if stalk: f.cyl(f"Stalk{k}", hc + V(L * 0.15, sy, 0), p, 0.08, C1, 6)
        f.ball(f"EyeW{k}", p, 0.25, WHITE, u=10, v=6); f.ball(f"EyeP{k}", p + V(0.17, 0, 0), 0.12, BLACK, u=8, v=5)
    for fn in P.get("x", []): fn(f, dict(L=L, W=W, H=H, z0=H * 0.5, C1=C1))
def golem(f, P):
    C1, C2, G = P["c1"], P.get("c2", dk(P["c1"])), P.get("glowc", ORANGE)
    f.block("Torso", V(0, 0, 3.6), (1.8, 3.0, 2.6), C1, Ry(-0.15)); f.block("Head", V(0.6, 0, 5.3), (1.2, 1.3, 1.1), C2)
    f.block("EyeL", V(1.21, 0.3, 5.4), (0.05, 0.3, 0.15), G, studs=False, glow=True); f.block("EyeR", V(1.21, -0.3, 5.4), (0.05, 0.3, 0.15), G, studs=False, glow=True)
    for sy in (1, -1):
        f.block(f"Shoulder{sy}", V(0.1, sy * 1.9, 4.4), (1.4, 1.2, 1.2), C2); f.block(f"Arm{sy}", V(0.5, sy * 2.0, 2.6), (0.95, 0.95, 2.6), C1, Ry(-0.3))
        f.block(f"Fist{sy}", V(1.0, sy * 2.0, 1.0), (1.3, 1.3, 1.2), C2); f.block(f"Leg{sy}", V(-0.2, sy * 0.85, 1.2), (1.1, 1.1, 2.4), C1); f.block(f"Foot{sy}", V(0.1, sy * 0.85, 0.2), (1.5, 1.3, 0.4), C2)
    for k, (x, y, z, a) in enumerate([(0.92, 0.6, 3.8, 0.4), (0.92, -0.5, 3.2, -0.6), (0.92, 0.1, 4.4, 0.0), (0.92, -0.2, 2.6, 0.8)]): f.block(f"Crack{k}", V(x, y, z), (0.06, 0.9, 0.15), G, Rx(a), studs=False, glow=True)
def whale(f, P):
    C1, BEL = P["c1"], P.get("belly", lt(P["c1"], 0.5))
    f.block("Body", V(0, 0, 2.2), (7.0, 3.4, 3.2), C1); f.block("Head", V(4.0, 0, 2.0), (1.6, 3.0, 2.6), C1)
    f.block("Belly", V(1.0, 0, 0.95), (7.4, 3.0, 0.9), BEL, studs=False)
    for k in range(4): f.block(f"Groove{k}", V(1.0, 0, 0.55), (7.0, 0.1 + 0.6 * k, 0.04), dk(BEL, 0.85), studs=False) if False else None
    for sy in (1, -1):
        p = V(3.6, sy * 1.53, 2.6); f.block(f"Eye{sy}", p, (0.35, 0.05, 0.4), BLACK, studs=False); f.block(f"Glint{sy}", p + V(-0.05, sy * 0.03, 0.1), (0.1, 0.04, 0.1), WHITE, studs=False)
        f.block(f"Fin{sy}", V(1.8, sy * 2.2, 1.0), (1.6, 1.4, 0.25), C1, Rx(sy * 0.4), studs=False)
        f.wedge(f"Fluke{sy}", V(-5.2, sy * 1.0, 2.8), (1.2, 2.0, 0.3), C1, Rz(math.pi / 2 * sy - math.pi / 2))
    f.block("TailStock", V(-4.3, 0, 2.6), (1.8, 1.4, 1.2), C1)
    for fn in P.get("x", []): fn(f, dict(L=7, W=3.4, H=3.2, z0=2.2, C1=C1))
def kraken(f, P):
    C1, C2 = P["c1"], P.get("c2", dk(P["c1"]))
    f.ball("Mantle", V(-0.4, 0, 4.2), (1.8, 1.7, 2.4), C1, u=14, v=10); f.block("Head", V(0.6, 0, 2.4), (2.2, 2.6, 1.8), C1)
    eyes(f, V(0.6, 0, 2.4), 2.2, 2.6, 1.8, True, YELLOW, C2, 1.0, fwd=0.3)
    for k in range(8):
        a = 2 * math.pi * k / 8; o = V(math.cos(a), math.sin(a), 0); b = V(0.6, 0, 1.5) + o * 0.9
        seg(f, f"Tent{k}", [b, b + o * 1.0 + V(0, 0, -1.1), b + o * 2.2 + V(0, 0, -1.4), b + o * 3.0 + V(0, 0, -0.8), b + o * 3.2 + V(0, 0, 0.0)], 0.4, C1, r_end=0.15, K=6)
        f.ball(f"Sucker{k}", b + o * 2.2 + V(0, 0, -1.75), 0.15, C2, u=8, v=5)
def dragon(f, P):
    c = quad(f, P)
    return c

# ====================================================================== zones and animals
G_ = rgb
Q, B, A = quad, bird, ape
ZONES = [
 ("01_Farm", [
   ("Chicken", B, dict(body=(1.6, 1.3, 1.4), leg=0.6, head=0.9, c1=WHITE, beak_c=YELLOW, x=[comb()])),
   ("Duck", B, dict(body=(1.8, 1.3, 1.1), leg=0.45, head=0.9, c1=rgb(150, 130, 105), head_c=rgb(40, 120, 70), beak=(0.55, 0.5, 0.15), beak_c=ORANGE, belly=rgb(200, 190, 170))),
   ("Pig", Q, dict(body=(2.6, 1.8, 1.6), legs=(0.7, 0.5), head=(1.3, 1.5, 1.3), neck=(0, 0.5), c1=PINKC, snout=(0.35, 0.8, 0.6), snout_c=rgb(255, 140, 160), nose_c=rgb(200, 90, 110), ears="floppy", tail="curly")),
   ("Sheep", Q, dict(body=(2.4, 1.9, 1.7), legs=(0.9, 0.4), head=(1.0, 1.0, 1.1), neck=(0.1, 0.6), c1=WHITE, leg_c=DGREY, head_c=DGREY, snout_c=DGREY, ears="floppy", ear_c=DGREY, tail="short", x=[wool()])),
   ("Goat", Q, dict(body=(2.4, 1.3, 1.4), legs=(1.1, 0.4), head=(1.1, 0.9, 1.0), neck=(0.5, 0.9), c1=rgb(230, 225, 210), ears="floppy", tail="short", feet=DGREY, x=[horns("goat", rgb(170, 150, 120)), beard(rgb(200, 190, 170))])),
   ("Cow", Q, dict(body=(3.2, 1.9, 1.9), legs=(1.2, 0.55), head=(1.3, 1.2, 1.3), neck=(0.2, 0.4), c1=WHITE, pattern="patches", pat_c=BLACK, snout=(0.45, 0.9, 0.7), snout_c=PINKC, nose_c=rgb(200, 90, 110), ears="floppy", tail="tuft", tail_tip=BLACK, feet=DGREY, x=[horns("cow")])),
   ("Horse", Q, dict(body=(3.2, 1.4, 1.7), legs=(2.0, 0.5), head=(1.6, 0.9, 1.0), neck=(1.4, 1.0), c1=BROWN, snout=(0.6, 0.75, 0.7), snout_c=NOUGAT, ears="point", tail="tuft", tail_c=DBROWN, tail_tip=DBROWN, feet=DBROWN, x=[mane_back(DBROWN)])),
 ]),
 ("02_Forest", [
   ("Squirrel", Q, dict(body=(1.4, 0.9, 1.0), legs=(0.45, 0.3), head=(0.9, 0.85, 0.85), neck=(0.1, 0.8), c1=rgb(190, 100, 50), belly=CREAM, ears="point", tail="up", snout=(0.25, 0.45, 0.35))),
   ("Rabbit", Q, dict(body=(1.5, 1.1, 1.1), legs=(0.4, 0.35), head=(1.0, 0.95, 0.9), neck=(0.1, 0.8), c1=rgb(200, 180, 160), belly=WHITE, ears="long", tail="short", tail_c=WHITE, snout=(0.25, 0.5, 0.4), nose_c=PINKC)),
   ("Hedgehog", Q, dict(body=(1.4, 1.1, 0.9), legs=(0.25, 0.25), head=(0.7, 0.7, 0.6), neck=(0, 0.3), c1=rgb(225, 195, 155), snout=(0.4, 0.3, 0.3), ears="tiny", x=[hedgehog_spikes(rgb(110, 80, 55))])),
   ("Fox", Q, dict(body=(2.0, 0.9, 1.0), legs=(0.8, 0.3), head=(1.0, 1.0, 0.9), neck=(0.2, 0.7), c1=rgb(230, 120, 40), belly=WHITE, snout=(0.6, 0.45, 0.4), snout_c=WHITE, ears="point", tail="bushy", feet=DBROWN)),
   ("Raccoon", Q, dict(body=(1.8, 1.2, 1.1), legs=(0.5, 0.35), head=(1.0, 1.1, 0.9), neck=(0.1, 0.6), c1=GREY, snout=(0.35, 0.45, 0.35), snout_c=WHITE, ears="round", tail="bushy", tail_tip=BLACK, x=[mask()])),
   ("Owl", B, dict(body=(1.3, 1.3, 1.8), leg=0.3, head=1.3, c1=BROWN, belly=CREAM, beak=(0.25, 0.25, 0.3), beak_c=YELLOW, eye=1.5, upright=True, x=[tufts(BROWN)])),
   ("BrownBear", Q, dict(body=(3.2, 2.2, 2.2), legs=(1.0, 0.8), head=(1.5, 1.6, 1.4), neck=(0.2, 0.4), c1=BROWN, snout=(0.6, 0.9, 0.7), snout_c=TAN2, ears="round", tail="short", angry=True)),
 ]),
 ("03_Savanna", [
   ("Meerkat", A, dict(torso=(0.75, 0.6, 1.4), leg=0.4, head=0.7, c1=rgb(205, 175, 125), arm=0.7, arm_w=0.2, lean=0.05, ears="tiny", tail="long", x=[eye_patches(DBROWN)])),
   ("Warthog", Q, dict(body=(2.4, 1.4, 1.4), legs=(0.7, 0.4), head=(1.4, 1.3, 1.2), neck=(0, 0.3), c1=rgb(130, 110, 95), snout=(0.5, 0.9, 0.6), ears="point", tail="tuft", angry=True, x=[tusks("up"), mane_back(DBROWN, 6)])),
   ("Zebra", Q, dict(body=(3.0, 1.3, 1.6), legs=(1.8, 0.45), head=(1.5, 0.85, 0.95), neck=(1.2, 1.0), c1=WHITE, pattern="stripes", pat_c=BLACK, pat_n=7, snout=(0.5, 0.7, 0.6), snout_c=DGREY, ears="point", tail="tuft", tail_tip=BLACK, feet=BLACK, x=[mane_back(BLACK)])),
   ("Ostrich", B, dict(body=(2.0, 1.5, 1.4), leg=2.5, neck=2.0, head=0.7, c1=BLACK, neck_c=rgb(220, 180, 170), head_c=rgb(220, 180, 170), leg_c=rgb(220, 180, 170), beak=(0.35, 0.3, 0.2), beak_c=TAN, wing_c=WHITE, tail_c=WHITE)),
   ("Hyena", Q, dict(body=(2.2, 1.2, 1.4), legs=(1.0, 0.4), head=(1.2, 1.1, 1.0), neck=(0.3, 0.5), c1=rgb(190, 160, 110), pattern="spots", pat_c=DBROWN, snout=(0.5, 0.6, 0.5), snout_c=DBROWN, ears="round", tail="tuft", angry=True, x=[mane_back(DBROWN, 4)])),
   ("Giraffe", Q, dict(body=(2.6, 1.4, 1.8), legs=(2.6, 0.45), head=(1.2, 0.8, 0.8), neck=(3.6, 1.15), c1=rgb(235, 185, 80), pattern="spots", pat_c=rgb(150, 90, 40), pat_n=7, snout=(0.45, 0.6, 0.55), ears="point", tail="tuft", tail_tip=DBROWN, feet=DBROWN, x=[horns("ossicone"), mane_back(rgb(150, 90, 40), 6)])),
   ("Rhino", Q, dict(body=(3.4, 2.0, 2.0), legs=(1.0, 0.8), head=(1.6, 1.3, 1.2), neck=(0.1, 0.2), c1=GREY, snout=(0.9, 1.1, 0.9), ears="point", tail="short", angry=True, x=[horns("rhino")])),
 ]),
 ("04_Jungle", [
   ("Frog", frog, dict(c1=rgb(90, 190, 70), belly=rgb(230, 230, 120))),
   ("Toucan", B, dict(body=(1.4, 1.1, 1.5), leg=0.5, head=1.0, c1=BLACK, belly=YELLOW, beak=(1.4, 0.6, 0.6), beak_c=ORANGE, x=[bill_tip()])),
   ("Monkey", A, dict(torso=(1.0, 0.8, 1.3), leg=0.7, head=1.0, c1=BROWN, face_c=NOUGAT, ears="round", ear_c=NOUGAT, tail="long")),
   ("Sloth", A, dict(torso=(1.4, 1.1, 1.5), leg=0.5, head=1.0, lean=0.1, c1=rgb(170, 150, 120), face_c=CREAM, ears=None, x=[eye_patches(DBROWN)])),
   ("Panther", Q, dict(body=(2.8, 1.2, 1.3), legs=(1.0, 0.45), head=(1.2, 1.1, 1.0), neck=(0.3, 0.5), c1=rgb(40, 40, 52), snout=(0.4, 0.6, 0.5), ears="point", tail="long", angry=True, iris=rgb(170, 230, 60))),
   ("Crocodile", Q, dict(body=(4.0, 1.8, 1.0), legs=(0.5, 0.5), sprawl=0.35, head=(1.6, 1.5, 0.8), neck=(0, 0.1), c1=rgb(70, 110, 60), belly=CREAM, snout=(2.0, 1.1, 0.55), tail="thick", angry=True, x=[spine_spikes(rgb(50, 80, 45), 7), fangs()])),
   ("Gorilla", A, dict(torso=(2.0, 1.5, 2.2), leg=1.1, head=1.3, c1=rgb(55, 55, 62), face_c=rgb(110, 110, 118), belly=rgb(110, 110, 118), angry=True, arm_w=0.65)),
 ]),
 ("05_Arctic", [
   ("Penguin", B, dict(body=(1.4, 1.4, 2.0), leg=0.25, head=1.1, c1=BLACK, belly=WHITE, beak=(0.4, 0.3, 0.2), upright=True, wing=0.5)),
   ("ArcticFox", Q, dict(body=(2.0, 0.9, 1.0), legs=(0.7, 0.3), head=(1.0, 1.0, 0.9), neck=(0.2, 0.7), c1=WHITE, snout=(0.5, 0.45, 0.4), ears="point", tail="bushy", tail_tip=LBLUE, iris=LBLUE)),
   ("Seal", seal, dict(c1=rgb(150, 160, 170))),
   ("SnowOwl", B, dict(body=(1.3, 1.3, 1.8), leg=0.3, head=1.3, c1=WHITE, belly=SNOW, beak=(0.25, 0.25, 0.3), beak_c=DGREY, eye=1.5, upright=True, x=[tufts(WHITE)])),
   ("Husky", Q, dict(body=(2.4, 1.2, 1.4), legs=(1.1, 0.45), head=(1.2, 1.1, 1.1), neck=(0.3, 0.6), c1=GREY, belly=WHITE, snout=(0.5, 0.6, 0.5), snout_c=WHITE, ears="point", tail="up", tail_c=GREY, iris=LBLUE)),
   ("Walrus", seal, dict(c1=rgb(150, 100, 70), s=1.4, angry=True, x=[tusks("walrus"), whiskers()])),
   ("PolarBear", Q, dict(body=(3.4, 2.3, 2.3), legs=(1.1, 0.85), head=(1.6, 1.6, 1.4), neck=(0.3, 0.4), c1=WHITE, snout=(0.6, 0.9, 0.7), ears="round", tail="short", angry=True, iris=LBLUE)),
 ]),
 ("06_Desert", [
   ("Lizard", Q, dict(body=(2.0, 0.9, 0.6), legs=(0.35, 0.3), sprawl=0.3, head=(0.9, 0.8, 0.6), neck=(0, 0.2), c1=rgb(180, 170, 90), pattern="spots", pat_c=rgb(120, 110, 50), snout=(0.5, 0.6, 0.35), tail="long")),
   ("Scorpion", scorpion, dict(c1=rgb(60, 50, 50), c2=rgb(140, 60, 40))),
   ("FennecFox", Q, dict(body=(1.8, 0.9, 1.0), legs=(0.7, 0.3), head=(1.0, 1.0, 0.9), neck=(0.2, 0.7), c1=SAND, belly=WHITE, snout=(0.5, 0.45, 0.4), ears="fennec", tail="bushy", tail_tip=BLACK)),
   ("Rattlesnake", snake, dict(c1=rgb(190, 160, 100), c2=rgb(110, 80, 50))),
   ("Camel", Q, dict(body=(3.0, 1.4, 1.6), legs=(2.4, 0.45), head=(1.3, 0.8, 0.8), neck=(1.8, 1.0), c1=TAN2, snout=(0.5, 0.65, 0.6), ears="tiny", tail="tuft", x=[hump(2)])),
   ("Vulture", B, dict(body=(1.8, 1.4, 1.4), leg=0.6, neck=0.4, head=0.7, c1=rgb(70, 55, 45), neck_c=rgb(230, 150, 140), head_c=rgb(230, 150, 140), beak=(0.4, 0.3, 0.3), beak_c=LGREY, angry=True, x=[ruff()])),
   ("SphinxCat", Q, dict(body=(2.2, 1.2, 1.3), legs=(0.9, 0.4), head=(1.1, 1.1, 1.0), neck=(0.3, 0.7), c1=rgb(230, 190, 160), snout=(0.35, 0.55, 0.45), ears="fennec", tail="long", iris=rgb(120, 220, 120), x=[headdress()])),
 ]),
 ("07_IceAge", [
   ("WoollyHare", Q, dict(body=(1.7, 1.3, 1.3), legs=(0.4, 0.4), head=(1.1, 1.0, 1.0), neck=(0.1, 0.8), c1=CREAM, ears="long", tail="short", snout=(0.25, 0.5, 0.4), nose_c=PINKC, x=[wool(SNOW)])),
   ("GiantBeaver", Q, dict(body=(2.6, 1.6, 1.4), legs=(0.5, 0.5), head=(1.2, 1.3, 1.1), neck=(0.1, 0.4), c1=rgb(120, 80, 50), snout=(0.4, 0.8, 0.55), snout_c=rgb(150, 110, 75), ears="tiny", tail="flat", tail_tip=rgb(70, 60, 55), x=[buck_teeth(rgb(240, 180, 80))])),
   ("GiantSloth", A, dict(torso=(2.4, 1.8, 2.6), leg=1.0, head=1.3, lean=0.2, c1=rgb(160, 120, 80), face_c=TAN2, arm_w=0.6)),
   ("Glyptodon", Q, dict(body=(3.0, 2.4, 1.4), legs=(0.6, 0.6), head=(1.0, 1.0, 0.8), neck=(0, 0.2), c1=rgb(120, 100, 80), ears="tiny", tail="thick", x=[shell(rgb(160, 130, 90), rgb(110, 85, 60))])),
   ("WoollyRhino", Q, dict(body=(3.6, 2.1, 2.1), legs=(1.0, 0.8), head=(1.6, 1.3, 1.2), neck=(0.1, 0.2), c1=rgb(140, 100, 60), snout=(0.9, 1.1, 0.9), ears="point", tail="short", angry=True, x=[horns("rhino"), fur_coat(rgb(150, 105, 60))])),
   ("Sabertooth", Q, dict(body=(2.8, 1.4, 1.5), legs=(1.1, 0.5), head=(1.3, 1.2, 1.1), neck=(0.3, 0.5), c1=rgb(210, 160, 90), pattern="stripes", pat_c=rgb(150, 100, 50), pat_n=4, snout=(0.45, 0.7, 0.55), ears="round", tail="short", angry=True, x=[fangs()])),
   ("Mammoth", Q, dict(body=(4.2, 2.6, 2.8), legs=(1.8, 0.9), head=(2.0, 2.0, 2.0), neck=(0, 0.3), c1=rgb(120, 75, 45), snout=(0.5, 0.9, 0.9), ears="tiny", tail="short", x=[tusks("mammoth"), trunk(rgb(120, 75, 45)), fur_coat(rgb(130, 82, 48), 7), hump(1, rgb(110, 68, 40))])),
 ]),
 ("08_DinoLand", [
   ("Compy", trexlike, dict(s=0.32, c1=rgb(150, 200, 70), c2=rgb(90, 140, 50))),
   ("Parasaurolophus", Q, dict(body=(3.6, 2.0, 2.2), legs=(1.6, 0.7), head=(1.3, 1.0, 1.0), neck=(1.6, 0.9), c1=rgb(70, 160, 150), pattern="stripes", pat_c=rgb(40, 110, 110), snout=(0.9, 0.8, 0.4), snout_c=rgb(200, 180, 120), tail="thick", x=[crest(rgb(230, 140, 60))])),
   ("Triceratops", Q, dict(body=(3.8, 2.6, 2.4), legs=(1.2, 0.9), head=(1.8, 1.8, 1.6), neck=(0, 0.2), c1=rgb(200, 120, 60), snout=(0.6, 0.9, 0.7), tail="thick", x=[frill(rgb(240, 180, 70))])),
   ("Stegosaurus", Q, dict(body=(4.0, 2.2, 2.4), legs=(1.3, 0.9), head=(1.1, 0.9, 0.8), neck=(0.8, 0.0), c1=rgb(110, 150, 80), belly=CREAM, snout=(0.5, 0.6, 0.45), tail="thick", x=[plates(rgb(230, 120, 60))])),
   ("Ankylosaurus", Q, dict(body=(4.0, 2.8, 1.6), legs=(0.8, 0.9), head=(1.4, 1.6, 1.0), neck=(0, 0.1), c1=rgb(140, 120, 70), snout=(0.4, 1.0, 0.6), tail="thick", angry=True, x=[shell(rgb(120, 100, 60), rgb(90, 75, 45), spikes=True), club_tail(rgb(100, 85, 55))])),
   ("TRex", "trex", None),
   ("Spinosaurus", trexlike, dict(s=1.15, snout=1.5, c1=rgb(60, 110, 140), c2=rgb(35, 70, 95), x=[sail(rgb(220, 90, 60))])),
 ]),
 ("09_Volcano", [
   ("MagmaSlug", blob, dict(c1=rgb(60, 45, 45), size=(3.0, 1.6, 1.2), stalks=True, glow=rgb(255, 120, 30), x=[glow_bits(rgb(255, 120, 30), 6, 4, "top", 0.4)])),
   ("FireSalamander", Q, dict(body=(2.2, 1.0, 0.65), legs=(0.4, 0.32), sprawl=0.3, head=(1.0, 0.9, 0.6), neck=(0, 0.2), c1=rgb(40, 36, 40), snout=(0.4, 0.7, 0.35), tail="long", glow=rgb(255, 140, 30), x=[glow_bits(rgb(255, 140, 30), 10, 5, "body", 0.35)])),
   ("EmberWolf", Q, dict(body=(2.6, 1.2, 1.4), legs=(1.1, 0.45), head=(1.2, 1.1, 1.0), neck=(0.3, 0.6), c1=rgb(55, 50, 52), snout=(0.5, 0.6, 0.5), ears="point", angry=True, iris=ORANGE, glow=rgb(255, 120, 30), x=[flame_mane(rgb(255, 120, 30))])),
   ("ObsidianGolem", golem, dict(c1=rgb(40, 34, 52), c2=rgb(70, 50, 100), glowc=rgb(200, 90, 255), glow=rgb(200, 90, 255))),
   ("LavaDrake", Q, dict(body=(3.2, 1.8, 1.8), legs=(1.2, 0.7), head=(1.4, 1.1, 1.0), neck=(1.6, 0.8), c1=rgb(170, 40, 30), belly=rgb(255, 170, 60), snout=(0.8, 0.8, 0.6), tail="dragon", angry=True, iris=ORANGE, glow=rgb(255, 110, 20),
        x=[horns("goat", rgb(40, 30, 30)), wings(rgb(120, 30, 25), 1.0, False, rgb(255, 110, 20)), spine_spikes(rgb(60, 30, 30), 6)])),
   ("LavaRex", trexlike, dict(s=1.1, c1=rgb(55, 45, 45), c2=rgb(30, 25, 28), belly=rgb(255, 140, 40), iris=rgb(255, 120, 30), eye_glow=True, glow=rgb(255, 110, 20), x=[rex_cracks(rgb(255, 110, 20))])),
   ("Phoenix", B, dict(body=(2.0, 1.4, 1.6), leg=0.9, head=1.0, c1=rgb(230, 70, 30), belly=rgb(255, 200, 60), beak_c=YELLOW, spread=True, wing_c=rgb(255, 150, 30), wing_glow=True, tail_glow=True, tail_c=rgb(255, 200, 60), glow=rgb(255, 160, 40), angry=True, x=[comb(rgb(255, 210, 60))])),
 ]),
 ("10_MythicIsles", [
   ("Jackalope", Q, dict(body=(1.6, 1.1, 1.1), legs=(0.45, 0.35), head=(1.0, 0.95, 0.9), neck=(0.1, 0.8), c1=rgb(190, 150, 110), belly=WHITE, ears="long", tail="short", tail_c=WHITE, snout=(0.25, 0.5, 0.4), nose_c=PINKC, x=[horns("antler", rgb(230, 210, 170))])),
   ("Griffin", Q, dict(body=(2.8, 1.5, 1.6), legs=(1.1, 0.5), head=(1.2, 1.1, 1.1), neck=(0.6, 0.8), c1=rgb(210, 160, 90), head_c=WHITE, neck_c=WHITE, snout=(0.55, 0.5, 0.45), snout_c=YELLOW, nose_c=YELLOW, tail="tuft", angry=True, x=[wings(rgb(140, 100, 60), 1.0), talons(), beak_head()])),
   ("Pegasus", Q, dict(body=(3.2, 1.4, 1.7), legs=(2.0, 0.5), head=(1.6, 0.9, 1.0), neck=(1.4, 1.0), c1=WHITE, snout=(0.6, 0.75, 0.7), snout_c=rgb(240, 230, 240), ears="point", tail="tuft", tail_c=LBLUE, tail_tip=LBLUE, feet=GOLD, x=[mane_back(LBLUE), wings(WHITE, 1.1)])),
   ("Unicorn", Q, dict(body=(3.2, 1.4, 1.7), legs=(2.0, 0.5), head=(1.6, 0.9, 1.0), neck=(1.4, 1.0), c1=WHITE, snout=(0.6, 0.75, 0.7), snout_c=rgb(255, 230, 245), ears="point", tail="tuft", tail_c=PINK, tail_tip=LAVENDER, feet=GOLD, glow=rgb(255, 220, 120), x=[mane_back(PINK), horns("unicorn", GOLD, True)])),
   ("Chimera", Q, dict(body=(2.8, 1.5, 1.6), legs=(1.1, 0.55), head=(1.3, 1.2, 1.1), neck=(0.3, 0.5), c1=rgb(210, 160, 90), mane=rgb(140, 70, 40), snout=(0.45, 0.7, 0.55), ears="round", angry=True, x=[chimera_bits()])),
   ("Kraken", kraken, dict(c1=rgb(170, 50, 90), c2=rgb(110, 30, 60))),
   ("CelestialDragon", Q, dict(body=(3.4, 1.8, 1.8), legs=(1.3, 0.7), head=(1.5, 1.2, 1.1), neck=(1.8, 0.8), c1=rgb(245, 245, 255), belly=GOLD, snout=(0.9, 0.85, 0.65), tail="dragon", tail_tip=GOLD, angry=True, iris=CYAN, glow=rgb(120, 230, 255),
        x=[horns("goat", GOLD), wings(rgb(240, 240, 255), 1.15, False, rgb(200, 230, 255)), spine_spikes(rgb(120, 230, 255), 6, True), whiskers(GOLD)])),
 ]),
 ("11_Space", [
   ("MoonBunny", Q, dict(body=(1.6, 1.2, 1.2), legs=(0.45, 0.38), head=(1.1, 1.0, 1.0), neck=(0.1, 0.8), c1=rgb(200, 205, 220), pattern="spots", pat_c=rgb(150, 155, 175), pat_n=3, ears="long", tail="short", tail_c=WHITE, snout=(0.25, 0.5, 0.4), nose_c=PINKC, glow=rgb(255, 240, 150), x=[crescent(rgb(255, 240, 150))])),
   ("AlienBlob", blob, dict(c1=rgb(110, 230, 90), size=(2.4, 2.2, 2.0), eye_y=(0.45, 0.0, -0.45), glow=rgb(200, 255, 120), x=[glow_bits(rgb(200, 255, 120), 4, 9, "top", 0.3)])),
   ("SpaceCat", Q, dict(body=(2.2, 1.2, 1.3), legs=(0.9, 0.42), head=(1.2, 1.15, 1.05), neck=(0.3, 0.7), c1=rgb(70, 50, 120), snout=(0.35, 0.55, 0.45), ears="point", tail="long", iris=CYAN, glow=rgb(150, 220, 255), x=[glow_bits(rgb(150, 220, 255), 10, 11, "body", 0.22), astro(rgb(220, 220, 235), rgb(120, 200, 255))])),
   ("AstroDog", Q, dict(body=(2.4, 1.3, 1.4), legs=(1.0, 0.45), head=(1.2, 1.1, 1.1), neck=(0.3, 0.6), c1=WHITE, snout=(0.5, 0.6, 0.5), snout_c=rgb(240, 220, 200), ears="floppy", ear_c=rgb(200, 140, 90), tail="short", glow=CYAN, x=[astro()])),
   ("StarWhale", whale, dict(c1=rgb(40, 40, 110), belly=rgb(120, 110, 200), glow=rgb(255, 240, 180), x=[glow_bits(rgb(255, 240, 180), 14, 21, "body", 0.3), glow_bits(rgb(255, 240, 180), 8, 22, "top", 0.3)])),
   ("GalaxyDragon", Q, dict(body=(3.4, 1.8, 1.8), legs=(1.3, 0.7), head=(1.5, 1.2, 1.1), neck=(1.8, 0.8), c1=rgb(60, 30, 110), belly=rgb(40, 160, 200), snout=(0.9, 0.85, 0.65), tail="dragon", tail_tip=MAGENTA, angry=True, iris=MAGENTA, glow=rgb(255, 120, 230),
        x=[horns("goat", rgb(200, 160, 255)), wings(rgb(40, 20, 80), 1.2, False, rgb(120, 60, 200)), spine_spikes(rgb(255, 120, 230), 6, True), glow_bits(rgb(255, 240, 200), 10, 31, "body", 0.2)])),
   ("BlackHoleBeast", Q, dict(body=(2.8, 1.4, 1.6), legs=(1.1, 0.5), head=(1.3, 1.2, 1.1), neck=(0.3, 0.5), c1=rgb(20, 18, 28), snout=(0.5, 0.65, 0.5), ears="point", tail="long", angry=True, iris=rgb(200, 90, 255), glow=rgb(200, 90, 255),
        x=[hole_ring(rgb(200, 90, 255)), spine_spikes(rgb(120, 50, 200), 6, True)])),
 ]),
]

def build(folder, name, fn, P):
    f = Brick(name, "CannonTame/Animals/" + folder)
    if fn == "trex": trex(f); glow = None
    else: fn(f, P); glow = P.get("glow")
    if not f.glow: glow = None
    elif glow is None: glow = rgb(255, 255, 255)
    f.done(glow, {"hero": VIEWS["hero"], "face": VIEWS["face"]} if "--face" in sys.argv else {"hero": VIEWS["hero"]})

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for folder, animals in ZONES:
        for name, fn, P in animals:
            if want and folder not in want and name not in want: continue
            build(folder, name, fn, P)
