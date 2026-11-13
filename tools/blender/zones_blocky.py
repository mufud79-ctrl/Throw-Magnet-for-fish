"""Zone props in the blocky Roblox part style (see blocky.py). Run: python zones_blocky.py [Zone or Prop ...] [--no-render]"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from mathutils import Vector, Matrix
from blocky import *

def Rz(a): return Matrix.Rotation(a, 3, "Z")
def Ry(a): return Matrix.Rotation(a, 3, "Y")
def Rx(a): return Matrix.Rotation(a, 3, "X")

# ======================================================================== helpers (minimal curves allowed)
def seg(f, name, pts, r, color, r_end=None, K=8, glow=False, joints=True):
    """Chunky curved shape as a chain of cylinders with ball joints."""
    r_end = r if r_end is None else r_end; n = len(pts) - 1
    for i in range(n):
        ra, rb = lerp(r, r_end, i / n), lerp(r, r_end, (i + 1) / n)
        f.cyl(f"{name}{i}", pts[i], pts[i + 1], ra, color, K, glow, r1=rb)
        if joints and 0 < i: f.ball(f"{name}J{i}", pts[i], ra, color, glow=glow, u=8, v=6)
def bubbles(f, name, base, n, seed, spread=0.8, h=6.0):
    rng = np.random.default_rng(seed)
    for k in range(n):
        z = rng.uniform(0.5, h); f.ball(f"{name}{k}", Vector(base) + V(rng.uniform(-spread, spread), rng.uniform(-spread, spread), z), 0.12 + 0.25 * rng.random(), BUBBLE, u=10, v=6)
def block_arc(f, name, center, R, a0, a1, n, size, color, plane="xz"):
    for k in range(n):
        a = lerp(a0, a1, (k + 0.5) / n)
        p = Vector(center) + (V(R * math.cos(a), 0, R * math.sin(a)) if plane == "xz" else V(0, R * math.cos(a), R * math.sin(a)))
        rot = Ry(-a + math.pi / 2) if plane == "xz" else Rx(a - math.pi / 2)
        f.block(f"{name}{k}", p, size, color, rot)
class Xf:
    """Tilt a whole assembly: positions and rotations through T about origin O."""
    def __init__(self, T, O=(0, 0, 0)): self.T, self.O = T, Vector(O)
    def p(self, v): return self.O + self.T @ Vector(v)
    def r(self, R=None): return self.T @ (R if R is not None else Matrix.Identity(3))
def lerp(a, b, t): return a + (b - a) * t
BUBBLE = rgb(200, 240, 255)

# ======================================================================== 1 POND (freshwater, seen from below)
def lily_pads(f):
    rng = np.random.default_rng(1)
    for i, (x, y, r) in enumerate([(0, 0, 2.2), (3.8, 1.6, 1.6), (-3.2, 2.0, 1.8), (1.8, -3.4, 1.4), (-2.6, -2.9, 1.2)]):
        f.cyl(f"Pad{i}", V(x, y, 9.7), V(x, y, 10.0), r, GREEN, 20)
        f.block(f"Vein{i}", V(x + r * 0.45, y, 9.66), (r * 0.9, 0.22, 0.06), DGREEN, Rz(0.3 * i), studs=False)
        seg(f, f"Stem{i}", [V(x * 0.3, y * 0.3, 0.3), V(x * 0.55 + rng.uniform(-.5, .5), y * 0.55, 4), V(x * 0.85, y * 0.85, 7.5), V(x, y, 9.7)], 0.14, GREEN, K=6)
    for k in range(8):
        a = 2 * math.pi * k / 8
        f.block(f"Petal{k}", V(0.65 * math.cos(a), 0.65 * math.sin(a), 10.45), (1.1, 0.55, 0.18), PINK, Rz(a) @ Ry(-0.55), studs=False)
    f.block("Center", V(0, 0, 10.45), (0.6, 0.6, 0.5), YELLOW)
    f.rocks("Roots", V(0, 0, 0), 1.6, DBROWN, 3, seed=2)
def reeds(f):
    f.block("Mud", V(0, 0, 0.2), (4.4, 4.4, 0.4), DBROWN)
    rng = np.random.default_rng(2)
    for i in range(11):
        x, y = rng.uniform(-1.6, 1.6, 2); h = rng.uniform(6, 10); t = rng.uniform(-.12, .12)
        f.block(f"Reed{i}", V(x, y, h / 2), (0.3, 0.3, h), GREEN if i % 2 else LIME, Ry(t) @ Rz(rng.uniform(0, 1)))
        if i % 4 == 0: f.cyl(f"Head{i}", V(x + t * h * 0.8, y, h - 2.2), V(x + t * h * 0.9, y, h - 0.6), 0.45, RBROWN, 10)
def sunken_rowboat(f):
    X = Xf(Ry(0.18) @ Rx(0.32) @ Rz(0.3), (0, 0, 0.9))
    f.cyl("Sand", V(0, 0, -0.2), V(0, 0, 0.2), 5.0, SAND, 16)
    f.block("Bottom", X.p((0, 0, 0)), (6, 2.4, 0.6), BROWN, X.r())
    for sy in (-1, 1): f.block(f"Side{sy}", X.p((0, sy * 1.4, 0.7)), (6, 0.4, 1.4), RBROWN, X.r())
    f.block("Stern", X.p((-3.2, 0, 0.7)), (0.4, 3.2, 1.4), RBROWN, X.r())
    f.wedge("Bow", X.p((3.9, 0, 0.55)), (1.8, 3.2, 1.7), RBROWN, X.r())
    f.block("Hole", X.p((0.8, -1.42, 0.8)), (1.2, 0.5, 0.8), BLACK, X.r(), studs=False)
    f.block("Seat", X.p((-1.5, 0, 1.05)), (0.8, 2.4, 0.25), NOUGAT, X.r())
    f.block("LoosePlank", V(3.6, 2.6, 0.35), (2.2, 0.6, 0.25), NOUGAT, Rz(0.6))
    for k in range(3): seg(f, f"Weed{k}", [V(-1 + k, 2.2, 0.2), V(-0.8 + k, 2.4, 2.0), V(-1.1 + k, 2.2, 3.6)], 0.12, LIME, K=6)
def sunken_log(f):
    f.cyl("Log", V(-4, 0, 1.3), V(3.2, 0, 1.3), 1.3, BROWN, 10)
    f.cyl("Hollow", V(-4.05, 0, 1.3), V(-3.6, 0, 1.3), 0.85, BLACK, 10)
    for k in range(4):
        a = k * math.pi / 2; f.wedge(f"Splinter{k}", V(3.5, 0.7 * math.cos(a), 1.3 + 0.7 * math.sin(a)), (0.8, 0.6, 0.9), NOUGAT, Rx(a))
    for k in range(5):
        x = -3 + 1.5 * k; seg(f, f"Weed{k}", [V(x, 0.4, 2.5), V(x + 0.3, 0.6, 4.0), V(x - 0.1, 0.4, 5.6), V(x + 0.2, 0.5, 6.8)], 0.13, GREEN if k % 2 else LIME, K=6)
    for k, (x, w) in enumerate([(-2.2, 2.0), (1.0, 1.6)]): f.block(f"Moss{k}", V(x, 0, 2.6), (w, 1.6, 0.4), MOSS)
def giant_pond_snail(f):
    f.block("Foot", V(0.4, 0, 0.45), (5.0, 1.8, 0.9), MOSS)
    for i, (x, z, r, c) in enumerate([(-0.6, 2.2, 1.9, NOUGAT), (-0.2, 3.0, 1.3, BROWN), (0.1, 3.6, 0.8, NOUGAT)]): f.ball(f"Shell{i}", V(x, 0, z), r, c)
    f.cyl("Band", V(-0.6, -1.95, 2.2), V(-0.6, 1.95, 2.2), 1.0, RBROWN, 16)
    for sy in (-1, 1):
        f.cyl(f"Stalk{sy}", V(2.6, sy * 0.4, 0.9), V(3.1, sy * 0.6, 2.2), 0.14, MOSS, 8); f.ball(f"Eye{sy}", V(3.1, sy * 0.6, 2.3), 0.28, BLACK)
def dock_pilings(f):
    for i, (x, y) in enumerate([(-2, -2), (-2, 2), (2, -2), (2, 2)]):
        f.cyl(f"Piling{i}", V(x, y, 0), V(x, y, 14), 0.55, BROWN, 10)
        for k in range(5): f.ball(f"Barnacle{i}{k}", V(x + 0.5 * math.cos(k * 2.1), y + 0.5 * math.sin(k * 2.1), 0.6 + 0.5 * k), 0.22, WHITE, u=8, v=5)
        f.block(f"Algae{i}", V(x, y, 1.2), (1.3, 1.3, 2.2), MOSS)
    for z in (12.5, 7): f.block(f"Cross{z}", V(0, -2, z), (4.6, 0.4, 0.6), RBROWN, Rx(0)); f.block(f"CrossB{z}", V(0, 2, z), (4.6, 0.4, 0.6), RBROWN)
    f.block("Deck", V(0, 0, 14.2), (5.6, 5.6, 0.4), NOUGAT)
    seg(f, "Rope", [V(2.55, 2, 9), V(2.6, 2.4, 9.4), V(2.2, 2.6, 9.8), V(1.8, 2.3, 10.2)], 0.12, TAN, K=6)

# ======================================================================== 2 RIVER
def river_boulders(f):
    f.rocks("Boulder", V(0, 0, 0), 3.4, LGREY, 5, seed=3, color2=GREY)
    for k, (x, y) in enumerate([(-0.6, 0.3), (0.8, -0.4)]): f.block(f"MossCap{k}", V(x, y, 2.6), (1.6, 1.4, 0.3), GREEN, Rz(k))
def driftwood_snag(f):
    pts = [V(-3.5, 0, 0), V(-1.5, 0.3, 1.8), V(0.5, -0.2, 3.4), V(2.5, 0.4, 4.6)]
    seg(f, "Trunk", pts, 0.8, SAND, r_end=0.4, K=8)
    rng = np.random.default_rng(6)
    for k, p in enumerate(pts[1:3]):
        for sd in (-1, 1):
            d = V(rng.uniform(-.2, .6), sd * rng.uniform(.6, 1), rng.uniform(.3, .8)).normalized()
            seg(f, f"Branch{k}{sd}", [p, p + d * 1.4, p + d * 2.6 + V(0, 0, 0.4)], 0.38, SAND, r_end=0.18, K=6)
    f.rocks("Base", V(-3.5, 0, 0), 1.6, GREY, 3, seed=7)
def beaver_dam_wall(f):
    rng = np.random.default_rng(7)
    for row in range(5):
        for k in range(3):
            y = -3 + k * 2.2 + rng.uniform(-.4, .4); z = 0.45 + row * 0.85; t = rng.uniform(-.25, .25)
            f.cyl(f"Log{row}{k}", V(-0.4 + 0.2 * row, y - 1.6, z), V(-0.4 + 0.2 * row + t, y + 1.6, z + t), 0.42, BROWN if (row + k) % 2 else RBROWN, 8)
    for k in range(8): f.block(f"Stick{k}", V(rng.uniform(-1, 1), rng.uniform(-3, 3), rng.uniform(0.5, 4)), (0.2, 0.2, 2.4), TAN, Rx(rng.uniform(-1.2, 1.2)) @ Ry(rng.uniform(-.5, .5)), studs=False)
    f.block("Mud", V(0, 0, 0.3), (3, 7.5, 0.6), DBROWN)
def mussel_bed(f):
    f.rocks("Bed", V(0, 0, 0), 3.0, GREY, 3, seed=8, color2=DGREY)
    rng = np.random.default_rng(9)
    for k in range(10):
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0.2, 1.4); p = V(r * math.cos(a), r * math.sin(a), 1.7 + rng.uniform(0, .5)); R = Rz(a) @ Ry(rng.uniform(-.6, .6))
        f.ball(f"ShellA{k}", p + R @ V(0, 0.12, 0), (0.55, 0.22, 0.3), NAVY, R, u=10, v=6); f.ball(f"ShellB{k}", p + R @ V(0, -0.12, 0), (0.55, 0.22, 0.3), NAVY, R, u=10, v=6)
        if k % 3 == 0: f.block(f"Pearl{k}", p + V(0, 0, 0.25), (0.25, 0.25, 0.25), ORANGE, studs=False)
def stream_weed(f):
    f.block("Gravel", V(0, 0, 0.2), (4, 4, 0.4), TAN)
    rng = np.random.default_rng(10)
    for i in range(9):
        x, y = rng.uniform(-1.4, 1.4, 2); z, t = 0.4, 0.15; p = V(x, y, z)
        for s in range(3):
            L = rng.uniform(1.8, 2.6); d = V(math.sin(t), 0, math.cos(t))
            f.block(f"Blade{i}{s}", p + d * L / 2, (0.12, 0.5, L), LIME if (i + s) % 2 else GREEN, Ry(t), studs=False); p = p + d * L; t += 0.35
def sunken_bridge_post(f):
    for k in range(4): f.block(f"Stone{k}", V(0.05 * k, 0, 0.9 + k * 1.8), (2.6 - 0.15 * k, 2.6 - 0.15 * k, 1.8), LGREY if k % 2 else GREY, Rz(0.08 * k))
    f.block("Cap", V(0, 0, 7.6), (3.2, 3.2, 0.6), GREY)
    f.block("PlankA", V(2.4, 0.4, 3.3), (5.5, 0.9, 0.3), NOUGAT, Ry(0.9))
    f.block("PlankB", V(-2.2, -0.5, 1.4), (4.5, 0.9, 0.3), TAN, Ry(-0.4) @ Rz(0.5))
    seg(f, "Rope", [V(1.35, 1.0, 6.8), V(1.6, 1.2, 5.5), V(2.0, 1.0, 4.4)], 0.12, TAN, K=6)
    f.block("Moss", V(0, 0, 0.6), (2.9, 2.9, 1.2), MOSS)

# ======================================================================== 3 SWAMP
def mangrove_roots(f):
    f.cyl("Trunk", V(0, 0, 4), V(0, 0, 9.5), 1.2, DBROWN, 10)
    for k in range(10):
        a = 2 * math.pi * k / 10; o = V(math.cos(a), math.sin(a), 0)
        seg(f, f"Root{k}", [V(0, 0, 4.6) + o * 0.8, o * 2.4 + V(0, 0, 4.6), o * 4.0 + V(0, 0, 2.8), o * 4.6 + V(0, 0, 0)], 0.5, BROWN if k % 2 else RBROWN, r_end=0.3, K=6)
        f.block(f"Algae{k}", o * 4.6 + V(0, 0, 0.35), (0.9, 0.9, 0.7), MOSS, Rz(a))
    for k, (x, y, z, s_) in enumerate([(0, 0, 10.6, 3.6), (1.6, 0.8, 9.8, 2.6), (-1.5, -0.9, 10.0, 2.8), (0.4, -1.8, 9.6, 2.2)]):
        f.block(f"Leaves{k}", V(x, y, z), (s_, s_, s_ * 0.7), GREEN if k % 2 else DGREEN, Rz(0.4 * k))
def gator_skull(f):
    BONE, BONE2 = rgb(236, 228, 205), rgb(214, 202, 172)
    f.block("Mud", V(0.5, 0, 0.15), (7, 4.6, 0.3), DBROWN)
    f.block("Cranium", V(-1, 0, 1.3), (2.4, 2.6, 2.0), BONE, studs=False)
    f.wedge("Brow", V(-1.6, 0, 2.6), (1.2, 2.6, 0.7), BONE2)
    f.block("Snout", V(1.5, 0, 1.0), (3.2, 1.6, 1.0), BONE, studs=False); f.block("Tip", V(3.4, 0, 0.95), (0.9, 1.3, 0.8), BONE2, studs=False)
    f.block("Jaw", V(1.2, 0, 0.42), (4.2, 1.5, 0.4), BONE2, studs=False)
    for sy in (-1, 1):
        f.block(f"Socket{sy}", V(-0.4, sy * 1.0, 1.75), (0.9, 0.7, 0.8), BLACK, studs=False)
        f.block(f"Nostril{sy}", V(3.6, sy * 0.3, 1.36), (0.3, 0.25, 0.1), BLACK, studs=False)
        for k in range(6): f.wedge(f"Tooth{sy}{k}", V(0.2 + 0.6 * k, sy * 0.72, 0.42), (0.3, 0.28, 0.45), WHITE, Ry(-math.pi / 2))
def bog_glow_bulbs(f):
    f.rocks("Mud", V(0, 0, 0), 3.6, DBROWN, 4, seed=12, color2=MOSS)
    rng = np.random.default_rng(12)
    for i in range(7):
        a = 2 * math.pi * i / 7; r = rng.uniform(0.3, 1.2); h = rng.uniform(2.5, 5.5); b = V(r * math.cos(a), r * math.sin(a), 1.0)
        seg(f, f"Stem{i}", [b, b + V(0.2, 0, h * 0.5), b + V(0, 0.2, h)], 0.1, MOSS, K=6)
        f.ball(f"Bulb{i}", b + V(0, 0.2, h + 0.4), 0.5 + 0.15 * h / 5, LIME, glow=True, u=10, v=7)
def sunken_lantern(f):
    f.block("Mud", V(0, 0, 0.15), (4, 3, 0.3), DBROWN)
    X = Xf(Ry(math.pi / 2 - 0.2), (0, 0, 1.2))
    f.cyl("Top", X.p((0, 0, 1.0)), X.p((0, 0, 1.3)), 0.9, BLACK, 8); f.cyl("Bottom", X.p((0, 0, -1.3)), X.p((0, 0, -1.0)), 0.9, BLACK, 8)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2; f.block(f"Rod{k}", X.p((0.7 * math.cos(a), 0.7 * math.sin(a), 0)), (0.18, 0.18, 2.1), BLACK, X.r(), studs=False)
    f.block("Flame", X.p((0, 0, 0)), (0.9, 0.9, 1.6), YELLOW, X.r(), studs=False, glow=True)
    seg(f, "Handle", [X.p((0, -0.6, 1.3)), X.p((0, -0.5, 1.9)), X.p((0, 0.5, 1.9)), X.p((0, 0.6, 1.3))], 0.08, BLACK, K=6)
def cypress_knees(f):
    rng = np.random.default_rng(14)
    for i in range(6):
        a = 2 * math.pi * i / 6; r = 0 if i == 0 else rng.uniform(1.2, 2.4); h = rng.uniform(1.5, 4.5); b = V(r * math.cos(a), r * math.sin(a), 0)
        f.cyl(f"Knee{i}", b, b + V(0, 0, h), rng.uniform(0.5, 0.8), BROWN if i % 2 else RBROWN, 8, r1=0.18)
    f.block("Mud", V(0, 0, 0.15), (6, 6, 0.3), DBROWN)
def methane_vent(f):
    f.rocks("Mound", V(0, 0, 0), 4.4, DBROWN, 5, seed=15, color2=MOSS)
    f.cyl("Mouth", V(0, 0, 2.6), V(0, 0, 3.0), 1.0, BLACK, 10)
    bubbles(f, "Bubble", V(0, 0, 3.0), 16, 16, 0.7, 9)

# ======================================================================== 4 CORAL REEF
def brain_coral(f):
    f.rocks("Base", V(0, 0, 0), 2.4, LGREY, 3, seed=3)
    f.ball("Brain", V(0, 0, 2.3), (2.6, 2.4, 1.9), PINK, u=16, v=10)
    for k in range(4): seg(f, f"Ridge{k}", [V(-2.0, -1.2 + 0.8 * k, 2.6 + 0.3 * math.sin(k)), V(-0.6, -1.0 + 0.8 * k, 3.7), V(0.8, -1.3 + 0.8 * k, 3.7), V(2.0, -1.1 + 0.8 * k, 2.7)], 0.22, MAGENTA, K=6)
def staghorn(f):
    rng = np.random.default_rng(14)
    def branch(name, p, d, L, r, depth):
        q = p + d * L; seg(f, name, [p, p + d * L * 0.5 + V(*rng.normal(0, .15, 3)), q], r, ORANGE, r_end=r * 0.7, K=6)
        if depth == 0: f.ball(name + "T", q, r * 0.8, YELLOW, u=8, v=6); return
        for k in range(2): branch(f"{name}_{k}", q, (d + V(*rng.normal(0, .55, 3)) + V(0, 0, .3)).normalized(), L * 0.7, r * 0.7, depth - 1)
    for k in range(5):
        a = 2 * math.pi * k / 5; branch(f"Stag{k}", V(0.3 * math.cos(a), 0.3 * math.sin(a), 0), V(0.45 * math.cos(a), 0.45 * math.sin(a), 1).normalized(), 2.4, 0.38, 2)
def sea_fan(f):
    f.cyl("Stalk", V(0, 0, 0), V(0, 0, 1.6), 0.35, PURPLE, 8)
    for k in range(9):
        a = lerp(0.25, math.pi - 0.25, k / 8); f.block(f"Rib{k}", V(3.0 * math.cos(a) * 0.5, 0, 1.6 + 3.0 * math.sin(a) * 0.5), (0.16, 0.16, 3.0), LAVENDER, Ry(math.pi / 2 - a), studs=False)
    for k in range(4):
        r = 1.0 + 0.6 * k; block_arc(f, f"Arc{k}_", V(0, 0, 1.6), r, 0.2, math.pi - 0.2, 6 + 2 * k, (0.14, 0.14, r * 0.55), MAGENTA)
def anemone(f):
    f.cyl("Column", V(0, 0, 0), V(0, 0, 1.6), 1.3, MAGENTA, 12)
    f.cyl("Disc", V(0, 0, 1.6), V(0, 0, 1.8), 1.3, CORAL, 12)
    for k in range(16):
        a = 2 * math.pi * k / 16; rr = 1.0 if k % 2 else 0.6; b = V(rr * math.cos(a), rr * math.sin(a), 1.7); d = V(0.5 * math.cos(a), 0.5 * math.sin(a), 1).normalized()
        f.cyl(f"Tent{k}", b, b + d * 1.6, 0.18, GREEN, 6, r1=0.12); f.ball(f"Tip{k}", b + d * 1.7, 0.2, LIME, u=8, v=6)
def giant_clam(f):
    for k in range(5):
        y = -1.6 + 0.8 * k; f.block(f"Bot{k}", V(0, y, 0.6), (3.2, 0.8, 1.2), WHITE if k % 2 else SAND)
    hinge = V(-1.6, 0, 1.2); X = Xf(Ry(-0.7), hinge)
    for k in range(5):
        y = -1.6 + 0.8 * k; f.block(f"Top{k}", X.p((1.6, y, 0.3)), (3.2, 0.8, 0.6), WHITE if k % 2 else SAND, X.r())
    f.block("Mantle", V(0.1, 0, 1.25), (2.8, 3.6, 0.2), BLUE, studs=False)
    f.ball("Pearl", V(0.3, 0, 1.75), 0.55, WHITE)
    bubbles(f, "Bubble", V(0.3, 0, 2.2), 5, 17, 0.4, 3)
def tube_sponge(f):
    for i, (x, y, h, r) in enumerate([(0, 0, 5.0, 0.9), (1.6, 0.6, 3.6, 0.7), (-1.3, 0.8, 2.9, 0.65), (0.6, -1.5, 2.2, 0.6), (-0.9, -1.0, 4.0, 0.7)]):
        f.cyl(f"Tube{i}", V(x, y, 0), V(x, y, h), r, YELLOW if i % 2 else ORANGE, 10)
        f.cyl(f"Hole{i}", V(x, y, h - 0.1), V(x, y, h + 0.02), r * 0.7, DBROWN, 10)

# ======================================================================== 5 OPEN OCEAN
def mooring_buoy(f):
    f.block("Anchor", V(0, 0, 0.6), (2.4, 2.4, 1.2), GREY)
    for k in range(18):
        z = 1.3 + k * 0.7; f.block(f"Link{k}", V(0.15 * math.sin(k * 0.5), 0, z), (0.18, 0.45 if k % 2 else 0.18, 0.7), DGREY, studs=False)
    top = 1.3 + 18 * 0.7
    f.ball("Float", V(0, 0, top + 1.2), (1.6, 1.6, 1.3), RED)
    f.cyl("Band", V(0, 0, top + 0.9), V(0, 0, top + 1.5), 1.62, WHITE, 16)
    f.cyl("Mast", V(0, 0, top + 2.3), V(0, 0, top + 3.8), 0.18, DGREY, 8)
    f.block("Light", V(0, 0, top + 4.0), (0.5, 0.5, 0.5), YELLOW, studs=False, glow=True)
def kelp_stalks(f):
    rng = np.random.default_rng(15)
    f.rocks("Holdfast", V(0, 0, 0), 2.0, DGREY, 3, seed=4)
    for i in range(4):
        x, y = rng.uniform(-1, 1, 2); h = rng.uniform(10, 15)
        pts = [V(x + 0.6 * math.sin(z * 0.6 + i), y + 0.4 * math.cos(z * 0.5 + i), z) for z in np.linspace(0.5, h, 6)]
        seg(f, f"Stalk{i}", pts, 0.16, rgb(120, 130, 40), K=6)
        for k in range(1, 6):
            p = pts[k]; a = k * 2.3 + i
            f.block(f"Leaf{i}{k}", p + V(0.8 * math.cos(a), 0.8 * math.sin(a), 0.4), (1.6, 0.5, 0.1), rgb(150, 160, 50), Rz(a) @ Ry(-0.4), studs=False)
            f.ball(f"Float{i}{k}", p + V(0.2 * math.cos(a), 0.2 * math.sin(a), 0), 0.22, YELLOW, u=8, v=6)
def sunken_container(f):
    X = Xf(Rx(0.12) @ Rz(0.35), (0, 0, 1.75))
    f.block("Box", X.p((0, 0, 0)), (9, 3.4, 3.4), RED, X.r())
    for k in range(9): f.block(f"Rib{k}", X.p((-4 + k, 0, 0)), (0.2, 3.55, 3.55), rgb(160, 30, 24), X.r(), studs=False)
    for sy in (-1, 1): f.block(f"Door{sy}", X.p((4.55, sy * 0.85, 0)), (0.12, 1.6, 3.2), rgb(170, 34, 26), X.r(), studs=False)
    for k in range(7): f.ball(f"Barnacle{k}", X.p((-3.5 + k, 1.75, -1.2 + 0.3 * (k % 3))), 0.25, WHITE, u=8, v=5)
    for k in range(3): seg(f, f"Weed{k}", [X.p((-3 + 2.5 * k, 0, 1.7)), X.p((-3 + 2.5 * k, 0.3, 3.4)), X.p((-2.7 + 2.5 * k, 0, 5))], 0.13, LIME, K=6)
def crab_trap(f):
    s = (3.2, 2.4, 1.8); hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
    for x in (-hx, hx):
        for y in (-hy, hy): f.block(f"Post{x}{y}", V(x, y, hz), (0.2, 0.2, s[2]), YELLOW, studs=False)
    for z in (0, s[2]):
        for y in (-hy, hy): f.block(f"RailX{z}{y}", V(0, y, z), (s[0], 0.2, 0.2), YELLOW, studs=False)
        for x in (-hx, hx): f.block(f"RailY{z}{x}", V(x, 0, z), (0.2, s[1], 0.2), YELLOW, studs=False)
    for k in range(5): f.block(f"Mesh{k}", V(-hx + 0.55 * (k + 1), 0, s[2]), (0.08, s[1], 0.08), LGREY, studs=False)
    f.block("CrabBody", V(0, 0, 0.45), (1.0, 0.8, 0.4), RED)
    for sy in (-1, 1): f.block(f"Claw{sy}", V(0.7, sy * 0.45, 0.45), (0.5, 0.3, 0.3), RED, studs=False)
    seg(f, "Line", [V(0, 0, s[2]), V(0.3, 0.2, 5), V(0, 0, 9)], 0.06, TAN, K=5)
    f.ball("BuoyFloat", V(0, 0, 9.4), 0.5, ORANGE)
def sunken_anchor(f):
    f.cyl("Sand", V(0, 0, -0.2), V(0, 0, 0.2), 4.0, SAND, 16)
    X = Xf(Ry(1.25), (0, 0, 1.0))
    f.block("Shank", X.p((0, 0, 2.2)), (0.6, 0.6, 5.0), DGREY, X.r())
    f.block("Stock", X.p((0, 0, 4.4)), (0.4, 3.2, 0.4), DGREY, X.r())
    seg(f, "Arms", [X.p((-2.0, 0, 1.2)), X.p((-1.2, 0, -0.1)), X.p((0, 0, -0.4)), X.p((1.2, 0, -0.1)), X.p((2.0, 0, 1.2))], 0.32, DGREY, K=8)
    for sx in (-1, 1): f.wedge(f"Fluke{sx}", X.p((sx * 2.1, 0, 1.5)), (0.9, 0.5, 1.0), DGREY, X.r(Rz(math.pi / 2 - sx * math.pi / 2)))
    f.cyl("Ring", X.p((0, -0.1, 5.0)), X.p((0, 0.1, 5.0)), 0.6, GREY, 10)
    for k in range(6): f.block(f"Chain{k}", V(-1.8 - 0.6 * k, 0.4 * math.sin(k), 0.3), (0.6, 0.3 if k % 2 else 0.15, 0.3 if k % 2 else 0.15), GREY, studs=False)
def drift_net(f):
    for k in range(7):
        x = -3 + k; f.block(f"V{k}", V(x, 0, 3.0 + 0.2 * math.sin(k)), (0.06, 0.06, 6), LGREY, studs=False)
    for k in range(7):
        z = 0.2 + k; f.block(f"H{k}", V(0, 0, z), (6.2, 0.06, 0.06), LGREY, studs=False)
    for k in range(7): f.ball(f"Float{k}", V(-3 + k, 0, 6.4), 0.35, ORANGE, u=10, v=6)
    for k in range(4): f.block(f"Weight{k}", V(-3 + 2 * k, 0, 0.1), (0.4, 0.4, 0.3), DGREY)
    f.cyl("Bottle", V(0.4, 0.15, 2.4), V(1.3, 0.2, 2.9), 0.25, LIME, 8)

# ======================================================================== 6 FROZEN SEA
def ice_crystals(f):
    f.rocks("Base", V(0, 0, 0), 2.2, SNOW, 3, seed=16, color2=ICE)
    rng = np.random.default_rng(16)
    for k in range(9):
        a = 2 * math.pi * k / 9; h = rng.uniform(2, 4.5)
        f.block(f"Crystal{k}", V(0.9 * math.cos(a), 0.9 * math.sin(a), 1.5 + h * 0.35), (0.6, 0.6, h), ICE if k % 2 else LBLUE, Rz(a) @ Ry(0.45) @ Rz(math.pi / 4))
    f.block("Core", V(0, 0, 3.6), (0.9, 0.9, 4.0), CYAN, Rz(math.pi / 4), studs=False, glow=True)
def iceberg_chunk(f):
    f.rocks("Berg", V(0, 0, 0), 4.6, ICE, 5, seed=17, color2=SNOW)
    for k in range(3): f.block(f"Layer{k}", V(0, 0, 0.8 + k * 1.2), (5.5 - k, 5.0 - k, 0.15), LBLUE, Rz(0.3 * k), studs=False)
def icicle_arch(f):
    block_arc(f, "Arch", V(0, 0, 0), 4.0, 0.0, math.pi, 11, (1.4, 1.6, 1.4), ICE)
    for k in range(1, 10):
        a = math.pi * k / 10; p = V(3.3 * math.cos(a), 0, 3.3 * math.sin(a))
        f.cyl(f"Icicle{k}", p, p + V(0, 0, -0.8 - 0.4 * (k % 3)), 0.22, SNOW, 6, r1=0.02)
def frozen_relic(f):
    f.block("Ice", V(0, 0, 1.4), (3.0, 3.0, 2.8), LBLUE)
    f.block("Blade", V(0, 0, 3.6), (0.3, 0.9, 2.0), LGREY, studs=False)
    f.block("Guard", V(0, 0, 4.7), (0.4, 2.0, 0.3), GOLD, studs=False); f.block("Grip", V(0, 0, 5.3), (0.3, 0.3, 1.0), RBROWN, studs=False)
    f.block("Gem", V(0, 0, 6.0), (0.5, 0.5, 0.5), CYAN, Rx(0.6) @ Ry(0.6), studs=False, glow=True)
    for k in range(4): f.block(f"Frost{k}", V(1.6 * math.cos(k * 1.57), 1.6 * math.sin(k * 1.57), 0.2), (0.8, 0.8, 0.4), SNOW)
def polar_sea_stars(f):
    f.rocks("Rock", V(0, 0, 0), 3.4, GREY, 3, seed=18, color2=LGREY)
    for i, (x, y, z, col) in enumerate([(-0.6, 0.2, 2.4, ORANGE), (0.9, -0.6, 2.2, PURPLE), (0.2, 1.0, 1.9, RED)]):
        for k in range(5):
            a = 2 * math.pi * k / 5 + i; f.block(f"Arm{i}{k}", V(x + 0.45 * math.cos(a), y + 0.45 * math.sin(a), z), (0.9, 0.32, 0.18), col, Rz(a), studs=False)
        f.ball(f"Middle{i}", V(x, y, z + 0.05), (0.3, 0.3, 0.15), col, u=8, v=5)
def white_soft_coral(f):
    rng = np.random.default_rng(19)
    f.rocks("Base", V(0, 0, 0), 2.0, GREY, 3, seed=19)
    for i in range(7):
        a = 2 * math.pi * i / 7; b = V(0.6 * math.cos(a), 0.6 * math.sin(a), 1.0); h = rng.uniform(2, 3.8); d = V(0.4 * math.cos(a), 0.4 * math.sin(a), 1).normalized()
        seg(f, f"Stalk{i}", [b, b + d * h * 0.5 + V(0, 0, 0.2), b + d * h], 0.25, WHITE, r_end=0.18, K=6)
        for k in range(3): f.ball(f"Puff{i}{k}", b + d * h + V(0.3 * math.cos(k * 2.1), 0.3 * math.sin(k * 2.1), 0.2), 0.32, ICE if k % 2 else WHITE, u=8, v=6)

# ======================================================================== 7 DEEP ABYSS
def whale_ribcage(f):
    spine = [V(x, 0, 3.6 + 0.4 * math.sin(x * 0.4)) for x in np.linspace(-6, 6, 9)]
    for k, p in enumerate(spine): f.block(f"Vert{k}", p, (1.0, 0.9, 0.9), WHITE, Rz(0.2 * k))
    for k in range(7):
        x = lerp(-4.5, 4.5, k / 6); top = V(x, 0, 3.6 + 0.4 * math.sin(x * 0.4)); h = 2.2 + 0.8 * math.sin(math.pi * k / 6)
        for sy in (-1, 1): seg(f, f"Rib{k}{sy}", [top, top + V(0, sy * 1.6 * h / 2.2, -0.3), top + V(0.2, sy * 2.2 * h / 2.2, -2.2), V(x + 0.3, sy * 1.7 * h / 2.2, 0)], 0.22, WHITE, r_end=0.12, K=6)
def tube_worms(f):
    f.rocks("Base", V(0, 0, 0), 2.6, DGREY, 3, seed=8, color2=BLACK)
    rng = np.random.default_rng(17)
    for i in range(10):
        x, y = rng.uniform(-1.2, 1.2, 2); h = rng.uniform(2.5, 6)
        f.cyl(f"Worm{i}", V(x, y, 1.0), V(x, y, h), 0.22, WHITE, 8)
        f.ball(f"Plume{i}", V(x, y, h + 0.25), (0.42, 0.42, 0.32), RED, glow=True, u=8, v=6)
def submarine_wreck(f):
    X = Xf(Ry(0.2) @ Rx(0.18), (0, 0, 1.6))
    f.cyl("Hull", X.p((-5, 0, 0)), X.p((4, 0, 0)), 1.7, rgb(110, 90, 70), 12)
    f.ball("Nose", X.p((4, 0, 0)), (1.6, 1.7, 1.7), rgb(110, 90, 70), X.r())
    f.block("Tower", X.p((0.5, 0, 2.0)), (2.4, 1.0, 1.8), rgb(120, 70, 40), X.r())
    f.cyl("Periscope", X.p((0.9, 0, 2.9)), X.p((0.9, 0, 4.2)), 0.15, DGREY, 8)
    for k in range(4): f.cyl(f"Port{k}", X.p((-2.5 + 1.5 * k, 1.68, 0.3)), X.p((-2.5 + 1.5 * k, 1.8, 0.3)), 0.35, CYAN, 10, glow=True)
    for k in range(4): f.wedge(f"Blade{k}", X.p((-5.3, 0, 0)) + X.r() @ V(0, 0.6 * math.cos(k * 1.57), 0.6 * math.sin(k * 1.57)), (0.4, 0.3, 1.0), GOLD, X.r(Rx(k * 1.57)))
    f.block("Hole", X.p((-1.0, -1.6, -0.2)), (1.6, 0.4, 1.2), BLACK, X.r(), studs=False)
def glow_polyps(f):
    f.rocks("Base", V(0, 0, 0), 2.2, DGREY, 3, seed=21)
    for i in range(5):
        a = 2 * math.pi * i / 5; b = V(0.9 * math.cos(a), 0.9 * math.sin(a), 1.0); h = 2.4 + 0.6 * math.sin(i * 2)
        f.cyl(f"Pen{i}", b, b + V(0, 0, h), 0.15, LAVENDER, 6)
        for k in range(4):
            z = 0.8 + k * (h - 0.8) / 4
            for sd in (-1, 1): f.block(f"Plume{i}{k}{sd}", b + V(0, sd * 0.35, z), (0.12, 0.6, 0.35), PURPLE, Rz(a) @ Rx(sd * 0.4), studs=False, glow=True)
def eye_rock(f):
    f.rocks("Rock", V(0, 0, 0), 4.5, DGREY, 5, seed=9, color2=BLACK)
    for k, (x, y, z, r) in enumerate([(2.0, 0.4, 2.2, 0.55), (1.8, -1.0, 1.4, 0.4), (1.2, 1.3, 2.8, 0.35), (2.2, -0.2, 0.9, 0.3)]):
        f.ball(f"Eye{k}", V(x, y, z), r, YELLOW, glow=True, u=10, v=7)
        f.block(f"Slit{k}", V(x + r * 0.85, y, z), (0.08, r * 0.35, r * 1.3), BLACK, studs=False)
def trench_spire(f):
    z = 0
    for i, s in enumerate((3.4, 2.8, 2.3, 1.8, 1.4, 1.0)):
        f.block(f"Spire{i}", V(0.15 * math.sin(i), 0.15 * math.cos(i), z + s * 0.5), (s, s, s), DGREY if i % 2 else NAVY, Rz(0.5 * i) @ Rx(0.1)); z += s * 0.95
    rng = np.random.default_rng(21)
    for k in range(6):
        zz = rng.uniform(0.6, z - 1); a = rng.uniform(0, 2 * math.pi); rr = 1.6 * (1 - zz / z) + 0.4
        f.block(f"Vein{k}", V(rr * math.cos(a), rr * math.sin(a), zz), (0.5, 0.5, 1.2), CYAN, Rz(a) @ Ry(0.6), studs=False, glow=True)

# ======================================================================== VOLCANIC VENT
def black_smoker(f):
    z = 0
    for i, s in enumerate((5.0, 4.2, 3.5, 2.8)):
        f.block(f"Stack{i}", V(0.1 * i, 0, z + s * 0.3), (s, s, s * 0.6), DGREY if i % 2 else BLACK, Rz(0.4 * i)); z += s * 0.6
    f.block("Vent", V(0.3, 0, z + 0.05), (2.0, 2.0, 0.2), ORANGE, Rz(1.6), studs=False, glow=True)
    for k in range(3): f.ball(f"Smoke{k}", V(0.6 + 0.6 * k, 0.3 * k, z + 1.4 + 1.5 * k), 0.9 + 0.35 * k, LGREY if k % 2 else GREY)
def basalt_columns(f):
    rng = np.random.default_rng(31)
    pts = [(0, 0)] + [(1.85 * math.cos(a), 1.85 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1]] + [(3.4 * math.cos(a), 3.4 * math.sin(a)) for a in np.linspace(0.3, 2 * math.pi + 0.3, 6)[:-1]]
    for i, (x, y) in enumerate(pts):
        h = rng.uniform(5, 9) if i == 0 else rng.uniform(2, 7) if i < 7 else rng.uniform(1, 3.5)
        f.cyl(f"Col{i}", V(x, y, 0), V(x, y, h), 1.0, DGREY if i % 2 else GREY, 6)
        f.cyl(f"Top{i}", V(x, y, h), V(x, y, h + 0.15), 0.85, LGREY, 6)
def obsidian_shards(f):
    f.rocks("Base", V(0, 0, 0), 2.6, DGREY, 4, seed=5, color2=BLACK)
    rng = np.random.default_rng(32)
    for k in range(8):
        a = 2 * math.pi * k / 8 + rng.uniform(-.2, .2); h = rng.uniform(2.5, 5.5); t = rng.uniform(0.2, 0.5)
        p = V(1.0 * math.cos(a), 1.0 * math.sin(a), h * 0.45)
        f.block(f"Shard{k}", p, (0.8, 0.8, h), OBSID if k % 3 else PURPLE, Rz(a) @ Ry(t) @ Rz(math.pi / 4), studs=False)
def magma_pool(f):
    for k in range(10):
        a = 2 * math.pi * k / 10; f.rocks(f"Rim{k}_", V(3.6 * math.cos(a), 3.6 * math.sin(a), 0), 1.8, DGREY, 2, seed=40 + k, color2=BLACK)
    f.cyl("Lava", V(0, 0, 0.1), V(0, 0, 0.5), 3.4, ORANGE, 24, glow=True)
    for k in range(4): f.block(f"Crust{k}", V(1.5 * math.cos(k * 1.7), 1.5 * math.sin(k * 1.7), 0.55), (1.0, 0.8, 0.2), BLACK, Rz(k), studs=False)
    for k in range(3): f.ball(f"Bubble{k}", V(-1.2 + 1.1 * k, 0.8 - 0.9 * k, 0.6), 0.35 + 0.1 * k, ORANGE, glow=True)
def sulfur_crystals(f):
    f.rocks("Base", V(0, 0, 0), 3.0, GREY, 4, seed=33, color2=DGREY)
    rng = np.random.default_rng(34)
    for k in range(9):
        a = rng.uniform(0, 2 * math.pi); h = rng.uniform(1.5, 3.5); t = rng.uniform(0.2, 0.8)
        f.block(f"Sulfur{k}", V(1.1 * math.cos(a), 1.1 * math.sin(a), 1.6 + h * 0.3), (0.7, 0.7, h), YELLOW, Rz(a) @ Ry(t))
def volcanic_bomb(f):
    f.cyl("Scorch", V(0, 0, 0), V(0, 0, 0.15), 4.0, BLACK, 20)
    f.rocks("Bomb", V(0, 0, 0.5), 3.4, DGREY, 6, seed=35, color2=BLACK)
    rng = np.random.default_rng(36)
    for k in range(7):
        a = rng.uniform(0, 2 * math.pi); z = rng.uniform(1.0, 3.2)
        f.block(f"Crack{k}", V(1.75 * math.cos(a), 1.75 * math.sin(a), z), (0.25, 2.0, 0.25), ORANGE, Rz(a) @ Rx(rng.uniform(-.8, .8)), studs=False, glow=True)

# ======================================================================== 9 SUNKEN RUINS
def broken_pillar(f):
    f.block("Plinth", V(0, 0, 0.5), (3.2, 3.2, 1.0), SAND)
    f.cyl("Column", V(0, 0, 1.0), V(0, 0, 7.0), 1.1, WHITE, 12)
    f.rocks("Break", V(0, 0, 6.6), 1.6, WHITE, 3, seed=50, color2=SAND)
    f.cyl("Drum", V(2.2, 1.2, 1.0), V(4.4, 2.6, 1.0), 1.0, WHITE, 12)
    f.block("Capital", V(-2.6, -1.4, 0.6), (2.4, 2.4, 1.2), SAND, Rz(0.4))
    for k in range(3): seg(f, f"Weed{k}", [V(1.2 * math.cos(k * 2), 1.2 * math.sin(k * 2), 1.0), V(1.3 * math.cos(k * 2), 1.3 * math.sin(k * 2), 2.6), V(1.1 * math.cos(k * 2), 1.1 * math.sin(k * 2), 4.0)], 0.12, LIME, K=6)
def statue_head(f):
    X = Xf(Ry(0.25) @ Rx(0.15), (0, 0, 2.2))
    f.block("Head", X.p((0, 0, 0)), (3.2, 3.0, 3.6), LGREY, X.r())
    f.block("Nose", X.p((1.75, 0, -0.1)), (0.5, 0.7, 1.2), LGREY, X.r())
    f.block("Brow", X.p((1.65, 0, 0.7)), (0.3, 2.4, 0.35), GREY, X.r())
    f.block("Mouth", X.p((1.65, 0, -1.0)), (0.2, 1.2, 0.3), DGREY, X.r(), studs=False)
    for sy in (-1, 1): f.block(f"Eye{sy}", X.p((1.62, sy * 0.7, 0.3)), (0.15, 0.6, 0.3), BLACK, X.r(), studs=False)
    for k in range(5): f.block(f"Crown{k}", X.p((-0.6 + 0.3 * k, -1.2 + 0.6 * k, 2.1)), (0.5, 0.5, 0.9), GOLD, X.r())
    f.block("Moss", X.p((-0.8, 0, 1.85)), (1.8, 2.6, 0.2), MOSS, X.r())
    f.cyl("Sand", V(0, 0, -0.2), V(0, 0, 0.3), 3.6, SAND, 16)
def treasure_chest(f):
    f.block("Chest", V(0, 0, 1.0), (3.2, 2.0, 2.0), BROWN)
    for x in (-1.1, 1.1): f.block(f"Band{x}", V(x, 0, 1.0), (0.3, 2.1, 2.1), GOLD, studs=False)
    hinge = V(-1.6, 0, 2.0); X = Xf(Ry(-1.0), hinge)
    f.block("Lid", X.p((1.6, 0, 0.35)), (3.2, 2.0, 0.7), RBROWN, X.r())
    f.block("Glow", V(0, 0, 2.0), (2.9, 1.7, 0.15), GOLD, studs=False, glow=True)
    rng = np.random.default_rng(51)
    for k in range(9): f.cyl(f"Coin{k}", V(rng.uniform(1.8, 3.6), rng.uniform(-1.5, 1.5), 0.05 + 0.12 * (k % 3)), V(0, 0, 0) + V(rng.uniform(1.8, 3.6), rng.uniform(-1.5, 1.5), 0.15 + 0.12 * (k % 3)), 0.35, GOLD, 10)
def archway(f):
    for sx in (-1, 1):
        for k in range(3): f.block(f"Pillar{sx}{k}", V(sx * 3.4, 0, 0.9 + k * 1.8), (1.6, 1.8, 1.8), SAND if k % 2 else WHITE)
    block_arc(f, "Arch", V(0, 0, 5.4), 3.4, 0.0, math.pi, 9, (1.4, 1.8, 1.2), WHITE)
    f.block("Keystone", V(0, 0, 8.9), (1.0, 2.0, 1.2), GOLD)
    for k in range(3): f.ball(f"Coral{k}", V(-3.4 + 0.5 * k, 0.9, 1 + k), 0.35, CORAL if k % 2 else PINK, u=8, v=6)
def amphorae(f):
    for i, (x, y, sc, lie) in enumerate([(0, 0, 1.0, False), (2.0, 0.8, 0.8, False), (-2.0, 1.0, 0.85, True)]):
        R = Ry(math.radians(80)) if lie else Matrix.Identity(3); base = V(x, y, 1.0 * sc if lie else 0)
        L = lambda v, R=R, base=base, sc=sc: base + R @ (Vector(v) * sc)
        f.ball(f"Body{i}", L((0, 0, 1.6)), (1.1 * sc, 1.1 * sc, 1.3 * sc), TERRA, R, u=10, v=7)
        f.cyl(f"Neck{i}", L((0, 0, 2.6)), L((0, 0, 3.4)), 0.4 * sc, TERRA, 8)
        f.cyl(f"Lip{i}", L((0, 0, 3.4)), L((0, 0, 3.6)), 0.55 * sc, rgb(160, 80, 60), 8)
        f.cyl(f"Foot{i}", L((0, 0, 0)), L((0, 0, 0.5)), 0.5 * sc, rgb(160, 80, 60), 8)
        f.cyl(f"Band{i}", L((0, 0, 1.8)), L((0, 0, 2.1)), 1.08 * sc, DBROWN, 10)
        for sd in (-1, 1): seg(f, f"Handle{i}{sd}", [L((0, sd * 0.4, 3.1)), L((0, sd * 0.95, 3.0)), L((0, sd * 0.95, 2.3))], 0.1 * sc, rgb(160, 80, 60), K=6)
def trident_altar(f):
    for i, s in enumerate((5.0, 3.8, 2.6)): f.block(f"Step{i}", V(0, 0, 0.35 + i * 0.7), (s, s, 0.7), WHITE if i % 2 else SAND)
    b = V(0, 0, 2.1)
    f.cyl("Shaft", b, b + V(0, 0, 6.5), 0.18, GOLD, 8)
    f.block("Cross", b + V(0, 0, 6.5), (0.3, 1.8, 0.3), GOLD, studs=False)
    for y in (-0.8, 0, 0.8):
        h = 1.6 if y == 0 else 1.2; f.block(f"Prong{y}", b + V(0, y, 6.5 + h / 2), (0.25, 0.25, h), GOLD, studs=False)
        f.block(f"Tip{y}", b + V(0, y, 6.6 + h), (0.35, 0.35, 0.35), TEAL, Rx(0.78) @ Ry(0.78), studs=False, glow=True)

# ======================================================================== 10 STARFALL LAKE
def fallen_star(f):
    for k in range(9):
        a = 2 * math.pi * k / 9; f.rocks(f"Crater{k}_", V(3.6 * math.cos(a), 3.6 * math.sin(a), 0), 1.6, OBSID, 2, seed=60 + k, color2=NAVY)
    X = Xf(Ry(0.35), (0, 0, 1.5))
    f.ball("Core", X.p((0, 0, 0)), 0.9, YELLOW, glow=True)
    for k in range(5):
        a = 2 * math.pi * k / 5; d = V(0, math.cos(a), math.sin(a))
        f.wedge(f"Arm{k}", X.p(d * 1.4), (1.6, 0.6, 1.4), YELLOW, X.r(Rx(a) @ Rz(-math.pi / 2)), glow=True)
def star_crystal_coral(f):
    rng = np.random.default_rng(61)
    f.rocks("Base", V(0, 0, 0), 2.0, OBSID, 3, seed=61)
    for i in range(5):
        a = 2 * math.pi * i / 5; b = V(0.5 * math.cos(a), 0.5 * math.sin(a), 1.0); d = V(0.5 * math.cos(a), 0.5 * math.sin(a), 1).normalized()
        q = b + d * 2.2; seg(f, f"Branch{i}", [b, b + d * 1.1 + V(0, 0, 0.2), q], 0.3, PURPLE, r_end=0.18, K=6)
        for k in range(2):
            d2 = (d + V(*rng.normal(0, .5, 3))).normalized(); q2 = q + d2 * 1.2
            seg(f, f"Twig{i}{k}", [q, q2], 0.16, PURPLE, K=6)
            f.block(f"Crystal{i}{k}", q2 + d2 * 0.4, (0.35, 0.35, 0.9), CYAN, Rz(a) @ Ry(0.5), studs=False, glow=True)
def meteor_chunk(f):
    f.rocks("Meteor", V(0, 0, 0), 4.0, OBSID, 5, seed=62, color2=PURPLE)
    rng = np.random.default_rng(63)
    for k in range(6):
        a = rng.uniform(0, 2 * math.pi); z = rng.uniform(1.2, 3.0)
        f.block(f"Crystal{k}", V(1.9 * math.cos(a), 1.9 * math.sin(a), z), (0.6, 0.6, 1.6), MAGENTA, Rz(a) @ Ry(0.9), studs=False, glow=True)
def constellation_stone(f):
    f.block("Stone", V(0, 0, 3.5), (1.6, 3.0, 7.0), NAVY, Ry(0.05))
    pts = [V(0.85, -0.8, 6.0), V(0.85, 0.4, 5.3), V(0.85, -0.2, 4.1), V(0.85, 0.9, 3.0), V(0.85, -0.6, 1.8)]
    for k, p in enumerate(pts): f.block(f"Star{k}", p, (0.15, 0.45, 0.45), YELLOW, Rx(0.78), studs=False, glow=True)
    for k in range(4):
        a, b = pts[k], pts[k + 1]; d = b - a
        f.block(f"Line{k}", (a + b) / 2, (0.1, 0.08, d.length), YELLOW, d.to_track_quat("Z", "X").to_matrix(), studs=False, glow=True)
    f.block("Base", V(0, 0, 0.3), (2.6, 4.0, 0.6), DGREY)
def nebula_portal(f):
    block_arc(f, "Ring", V(0, 0, 4.2), 3.6, -0.15, 2 * math.pi - 0.15, 16, (1.2, 1.4, 1.2), GREY, plane="yz")
    f.cyl("Swirl", V(-0.1, 0, 4.2), V(0.1, 0, 4.2), 3.0, MAGENTA, 24, glow=True)
    for k in range(6):
        a = 2 * math.pi * k / 6; f.block(f"Rune{k}", V(0.8, 5.0 * math.cos(a), 4.2 + 5.0 * math.sin(a)), (0.2, 0.6, 0.8), CYAN, studs=False, glow=True)
    for sy in (-1, 1): f.block(f"Foot{sy}", V(0, sy * 2.2, 0.4), (2.2, 2.0, 0.8), DGREY)
def orbiting_orbs(f):
    f.block("Pedestal", V(0, 0, 0.8), (2.4, 2.4, 1.6), NAVY); f.block("Top", V(0, 0, 1.75), (2.8, 2.8, 0.3), GOLD)
    for i, (r, h, col, a) in enumerate([(2.2, 4.0, ORANGE, 0.0), (3.0, 5.5, CYAN, 2.1), (1.6, 6.8, LAVENDER, 4.2)]):
        p = V(r * math.cos(a), r * math.sin(a), h)
        seg(f, f"Arm{i}", [V(0, 0, 1.9), V(0, 0, h * 0.6), p], 0.08, GOLD, K=6)
        f.ball(f"Planet{i}", p, 0.6 + 0.2 * i, col)
        if i == 1: f.cyl("PlanetRing", p - V(0, 0, 0.05), p + V(0, 0, 0.05), 1.4, WHITE, 20, glow=True)

G_ = lambda r, g, b: rgb(r, g, b)
ZONES = [
 ("01_Pond", [("LilyPads", lily_pads, None), ("Reeds", reeds, None), ("SunkenRowBoat", sunken_rowboat, None),
              ("SunkenLog", sunken_log, None), ("GiantPondSnail", giant_pond_snail, None), ("DockPilings", dock_pilings, None)]),
 ("02_River", [("RiverBoulders", river_boulders, None), ("DriftwoodSnag", driftwood_snag, None), ("BeaverDamWall", beaver_dam_wall, None),
               ("MusselBed", mussel_bed, None), ("StreamWeed", stream_weed, None), ("SunkenBridgePost", sunken_bridge_post, None)]),
 ("03_Swamp", [("MangroveRoots", mangrove_roots, None), ("GatorSkull", gator_skull, None), ("BogGlowBulbs", bog_glow_bulbs, G_(200, 255, 90)),
               ("SunkenLantern", sunken_lantern, G_(255, 220, 120)), ("CypressKnees", cypress_knees, None), ("MethaneVent", methane_vent, None)]),
 ("04_CoralReef", [("BrainCoral", brain_coral, None), ("StaghornCoral", staghorn, None), ("SeaFan", sea_fan, None),
                   ("Anemone", anemone, None), ("GiantClam", giant_clam, None), ("TubeSponge", tube_sponge, None)]),
 ("05_OpenOcean", [("MooringBuoy", mooring_buoy, G_(255, 230, 120)), ("KelpStalks", kelp_stalks, None), ("SunkenContainer", sunken_container, G_(120, 230, 255)),
                   ("CrabTrap", crab_trap, None), ("SunkenAnchor", sunken_anchor, None), ("DriftNet", drift_net, None)]),
 ("06_FrozenSea", [("IceCrystals", ice_crystals, G_(120, 230, 255)), ("IcebergChunk", iceberg_chunk, None), ("IcicleArch", icicle_arch, None),
                   ("FrozenRelic", frozen_relic, G_(120, 230, 255)), ("PolarSeaStars", polar_sea_stars, None), ("WhiteSoftCoral", white_soft_coral, None)]),
 ("07_DeepAbyss", [("WhaleRibcage", whale_ribcage, None), ("TubeWorms", tube_worms, G_(255, 70, 110)), ("SubmarineWreck", submarine_wreck, G_(120, 230, 255)),
                   ("GlowPolyps", glow_polyps, G_(190, 120, 255)), ("EyeRock", eye_rock, G_(255, 230, 80)), ("TrenchSpire", trench_spire, G_(90, 220, 255))]),
 ("08_VolcanicVent", [("BlackSmoker", black_smoker, G_(255, 120, 30)), ("BasaltColumns", basalt_columns, None), ("ObsidianShards", obsidian_shards, None),
                      ("MagmaPool", magma_pool, G_(255, 110, 20)), ("SulfurCrystals", sulfur_crystals, None), ("VolcanicBomb", volcanic_bomb, G_(255, 100, 20))]),
 ("09_SunkenRuins", [("BrokenPillar", broken_pillar, None), ("StatueHead", statue_head, None), ("TreasureChest", treasure_chest, G_(255, 210, 90)),
                     ("Archway", archway, None), ("Amphorae", amphorae, None), ("TridentAltar", trident_altar, G_(90, 240, 220))]),
 ("10_StarfallLake", [("FallenStar", fallen_star, G_(255, 236, 140)), ("StarCrystalCoral", star_crystal_coral, G_(120, 220, 255)), ("MeteorChunk", meteor_chunk, G_(220, 140, 255)),
                      ("ConstellationStone", constellation_stone, G_(255, 240, 190)), ("NebulaPortal", nebula_portal, G_(200, 120, 255)), ("OrbitingOrbs", orbiting_orbs, G_(255, 255, 255))]),
]

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for folder, props in ZONES:
        for name, fn, glow in props:
            if want and folder not in want and name not in want: continue
            f = Brick(name, "Zones/" + folder); fn(f); f.done(glow)
