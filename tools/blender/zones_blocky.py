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

# ======================================================================== POND
def lily_pads(f):
    for i, (x, y, r) in enumerate([(0, 0, 2.2), (3.8, 1.6, 1.6), (-3.2, 2.0, 1.8), (1.8, -3.4, 1.4), (-2.6, -2.9, 1.2)]):
        f.cyl(f"Pad{i}", V(x, y, 0), V(x, y, 0.3), r, GREEN, 20)
        f.block(f"Vein{i}", V(x + r * 0.45, y, 0.33), (r * 0.9, 0.22, 0.06), DGREEN, Rz(0.3 * i), studs=False)
    for k in range(8):
        a = 2 * math.pi * k / 8
        f.block(f"Petal{k}", V(0.65 * math.cos(a), 0.65 * math.sin(a), 0.75), (1.1, 0.55, 0.18), PINK, Rz(a) @ Ry(-0.55), studs=False)
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.4
        f.block(f"PetalIn{k}", V(0.35 * math.cos(a), 0.35 * math.sin(a), 1.0), (0.75, 0.4, 0.15), WHITE, Rz(a) @ Ry(-1.0), studs=False)
    f.block("Center", V(0, 0, 0.75), (0.6, 0.6, 0.5), YELLOW)
def cattails(f):
    f.block("Dirt", V(0, 0, 0.2), (4, 4, 0.4), DBROWN)
    rng = np.random.default_rng(2)
    for i in range(7):
        x, y = rng.uniform(-1.3, 1.3, 2); h = rng.uniform(5, 7.5)
        f.block(f"Stalk{i}", V(x, y, h / 2), (0.3, 0.3, h), GREEN, Rz(rng.uniform(0, 1)))
        f.cyl(f"Head{i}", V(x, y, h - 2.4), V(x, y, h - 0.6), 0.45, RBROWN, 10)
        f.block(f"Tip{i}", V(x, y, h + 0.3), (0.15, 0.15, 0.9), GREEN, studs=False)
    for k in range(9):
        a = 2 * math.pi * k / 9; L = rng.uniform(3, 4.5)
        f.block(f"Leaf{k}", V(math.cos(a) * 0.9, math.sin(a) * 0.9, L / 2 + 0.2), (0.2, 0.7, L), LIME, Rz(a) @ Ry(0.35), studs=False)
def wooden_dock(f):
    for i, (x, y) in enumerate([(-4.5, -2.2), (-4.5, 2.2), (0, -2.2), (0, 2.2), (4.5, -2.2), (4.5, 2.2)]):
        f.cyl(f"Post{i}", V(x, y, -1), V(x, y, 2.6), 0.4, BROWN, 12)
    for y in (-2.2, 2.2): f.block(f"Beam{y}", V(0, y, 1.85), (10, 0.6, 0.5), RBROWN)
    for k in range(10):
        f.block(f"Plank{k}", V(-4.5 + k, 0, 2.3), (0.9, 5.4, 0.4), NOUGAT if k % 2 else TAN)
    f.cyl("Bollard", V(4.5, 2.2, 2.5), V(4.5, 2.2, 3.6), 0.35, DGREY, 12); f.ball("BollardTop", V(4.5, 2.2, 3.6), 0.42, DGREY)
    f.cyl("LampPole", V(-4.5, -2.2, 2.5), V(-4.5, -2.2, 5.5), 0.15, BLACK, 8)
    f.block("Lamp", V(-4.5, -2.2, 5.8), (0.7, 0.7, 0.8), YELLOW, studs=False, glow=True)
def mossy_log(f):
    f.cyl("Log", V(-4, 0, 1.3), V(4, 0, 1.3), 1.3, BROWN, 12)
    for sx in (-1, 1): f.cyl(f"End{sx}", V(sx * 4.0, 0, 1.3), V(sx * 4.08, 0, 1.3), 1.15, NOUGAT, 12)
    for k, (x, w) in enumerate([(-2.2, 2.2), (0.6, 1.8), (2.6, 1.4)]): f.block(f"Moss{k}", V(x, 0, 2.6), (w, 1.8, 0.45), GREEN)
    for k, x in enumerate((-1.0, 1.8)):
        f.cyl(f"MStem{k}", V(x, 1.0, 2.2), V(x, 1.0, 3.0), 0.15, WHITE, 8); f.cyl(f"MCap{k}", V(x, 1.0, 3.0), V(x, 1.0, 3.3), 0.45, RED, 10)
def toadstools(f):
    for i, (x, y, h, r) in enumerate([(0, 0, 3.2, 2.2), (2.8, 1.2, 2.0, 1.4), (-2.2, 1.6, 1.3, 0.9)]):
        f.cyl(f"Stem{i}", V(x, y, 0), V(x, y, h), r * 0.32, WHITE, 12)
        f.cyl(f"Cap{i}", V(x, y, h), V(x, y, h + r * 0.35), r, RED, 16)
        f.cyl(f"Dome{i}", V(x, y, h + r * 0.35), V(x, y, h + r * 0.6), r * 0.65, RED, 16)
        for k in range(5):
            a = 2 * math.pi * k / 5 + i; rr = r * 0.82
            f.block(f"Spot{i}{k}", V(x + rr * math.cos(a), y + rr * math.sin(a), h + r * 0.36), (r * 0.3, r * 0.3, 0.12), WHITE, Rz(a), studs=False)
        f.block(f"SpotTop{i}", V(x, y, h + r * 0.61), (r * 0.4, r * 0.4, 0.12), WHITE, studs=False)
def row_boat(f):
    f.block("Bottom", V(0, 0, 0.3), (6, 2.4, 0.6), BROWN)
    for sy in (-1, 1): f.block(f"Side{sy}", V(0, sy * 1.4, 1.0), (6, 0.4, 1.4), RBROWN)
    f.block("Stern", V(-3.2, 0, 1.0), (0.4, 3.2, 1.4), RBROWN)
    f.wedge("Bow", V(3.9, 0, 0.85), (1.8, 3.2, 1.7), RBROWN)
    for x in (-1.5, 1.2): f.block(f"Seat{x}", V(x, 0, 1.35), (0.8, 2.4, 0.25), NOUGAT)
    for sy in (-1, 1):
        f.block(f"Oar{sy}", V(-0.3, sy * 2.2, 1.6), (4.5, 0.2, 0.2), TAN, Rz(sy * -0.35), studs=False)
        f.block(f"Blade{sy}", V(-2.4, sy * 2.95, 1.6), (1.2, 0.12, 0.6), TAN, Rz(sy * -0.35), studs=False)

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

ZONES = [
 ("01_Pond", [("LilyPads", lily_pads, None), ("Cattails", cattails, None), ("WoodenDock", wooden_dock, rgb(255, 220, 120)),
              ("MossyLog", mossy_log, None), ("Toadstools", toadstools, None), ("RowBoat", row_boat, None)]),
 ("08_VolcanicVent", [("BlackSmoker", black_smoker, rgb(255, 120, 30)), ("BasaltColumns", basalt_columns, None), ("ObsidianShards", obsidian_shards, None),
                      ("MagmaPool", magma_pool, rgb(255, 110, 20)), ("SulfurCrystals", sulfur_crystals, None), ("VolcanicBomb", volcanic_bomb, rgb(255, 100, 20))]),
]

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for folder, props in ZONES:
        for name, fn, glow in props:
            if want and folder not in want and name not in want: continue
            f = Brick(name, "Zones/" + folder); fn(f); f.done(glow)
