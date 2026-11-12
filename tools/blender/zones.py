"""Zone props: 10 zones x 6 unique props. Run: python zones.py [ZoneFolder ...] [--no-render]
Output: models/Zones/<NN>_<Zone>/<Prop>/  (no rig; glow parts in <Prop>_Glow)."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from mathutils import Vector, Matrix
from fishkit import V, lerp, c, basis
from gym import Prop as _Prop, pat, SW
import bmesh

class Prop(_Prop):
    """Chunky low-poly look for zone props: flat shading, few segments, thicker parts, hard chamfers, faceted rocks."""
    flat = True
    def sphere(self, name, center, rot, scale, sw, u=18, v=12, glow=False):
        return super().sphere(name, center, rot, scale, sw, max(6, min(u, 10)), max(4, min(v, 7)), glow)
    def tube(self, name, ctrl, r0, r1, strip=0, K=8, sub=5, pw=1.0, glow=False, sw=None, rfn=None):
        k = 1.35
        rf = (lambda s: rfn(s) * k) if rfn else None
        return super().tube(name, ctrl, r0 * k, max(r1 * k, r0 * k * 0.35), strip, max(4, min(K, 6)), min(sub, 3), pw, glow, sw, rf)
    def torus(self, name, center, n, R1, r1, sw, U=24, Vn=8, glow=False):
        return super().torus(name, center, n, R1, r1 * 1.3, sw, max(6, min(U, 14)), max(4, min(Vn, 5)), glow)
    def cyl(self, name, a, b, r, K=24, sw=0, glow=False, proj=True):
        return super().cyl(name, a, b, r * (1.4 if r < 0.16 else 1.0), max(6, min(K, 8)), sw, glow, proj)
    def box(self, name, center, size, rot=None, sw=0, bevel=0.05, glow=False, proj=True):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=size, verts=bm.verts)
        if bevel: bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(bevel * 1.4, min(size) * 0.3), segments=1, affect="EDGES")
        M_ = Matrix.Translation(center) @ (rot.to_4x4() if rot else Matrix.Identity(4))
        bmesh.ops.transform(bm, matrix=M_, verts=bm.verts)
        verts = [v.co.copy() for v in bm.verts]; faces = [tuple(v.index for v in fc.verts) for fc in bm.faces]; bm.free()
        ob = self.make_obj(name, verts, faces, [[self.uv_sw(sw)] * len(fc) for fc in faces], glow)
        return self.project(ob) if proj and not glow else ob
    def rock(self, name, center, r, sw=0, seed=1, proj=True):
        ob = _Prop.sphere(self, name, center, Matrix.Identity(3), (r, r, r), sw, 7, 5)
        rng = np.random.default_rng(seed + 100)
        for v in ob.data.vertices:
            d = v.co - center; v.co = center + d * float(rng.uniform(0.8, 1.15))
            if v.co.z < center.z - r * 0.55: v.co.z = center.z - r * 0.55   # flat bottom
        return self.project(ob) if proj else ob

M, A, D, G, W, P, E, X = (SW[k] for k in ("metal", "accent", "dark", "glow", "white", "pad", "eye", "x"))
I3 = Matrix.Identity(3)
def ring(center, R, n, a0=0.0, a1=2 * math.pi, axis="z", z=0.0):
    out = []
    for k in range(n):
        a = lerp(a0, a1, k / max(n - 1, 1))
        if axis == "z": out.append(center + V(R * math.cos(a), R * math.sin(a), z))
        elif axis == "y": out.append(center + V(R * math.cos(a), z, R * math.sin(a)))
        else: out.append(center + V(z, R * math.cos(a), R * math.sin(a)))
    return out
def blade(f, name, base, d, L, w=0.12, droop=0.4, sw=None, style=0, glow=False):
    side = d.cross(V(0, 0, 1)); side = side.normalized() if side.length > 1e-4 else V(1, 0, 0)
    f.fin(name, lambda s: base + side * lerp(-w, w, s), lambda s: d, lambda s: L * (1 - abs(2 * s - 1) ** 2) * 0.8 + L * 0.2,
          lambda s, r: V(d.x, d.y, 0).normalized() * droop * r * r if V(d.x, d.y, 0).length > 1e-3 else V(0, 0, 0), 6, 6, 0.03, style, glow)
def branchy(f, name, p, d, L, r, depth, rng, strip=0, leaf=None):
    q = p + d * L; mid = p + d * L * 0.5 + V(*rng.normal(0, 0.08 * L, 3))
    f.tube(name, [p, mid, q], r, r * 0.6, strip=strip, K=7, sub=3)
    if depth == 0:
        if leaf: leaf(q, d)
        return
    for k in range(2 if depth > 1 else 3):
        nd = (d + V(*rng.normal(0, 0.6, 3)) + V(0, 0, 0.3)).normalized()
        branchy(f, f"{name}_{k}", q, nd, L * 0.7, r * 0.6, depth - 1, rng, strip, leaf)

# ======================================================================== 1 POND
def lily_pads(f):
    for i, (x, y, r) in enumerate([(0, 0, 1.0), (1.7, 0.8, 0.7), (-1.4, 1.0, 0.8), (0.9, -1.5, 0.6), (-1.1, -1.3, 0.55)]):
        f.sphere(f"Pad{i}", V(x, y, 0.05), I3, (r, r, 0.06), P, 24, 6)
        f.box(f"Notch{i}", V(x + r * 0.55, y, 0.06), (r * 0.9, 0.06, 0.1), sw=D, bevel=0.01, proj=False)
    c0 = V(0, 0, 0.12)
    for k in range(9):
        a = 2 * math.pi * k / 9; d = V(math.cos(a), math.sin(a), 0.7).normalized()
        f.gem(f"Petal{k}", c0 + d * 0.25, basis(d), (0.3, 0.12, 0.05), X)
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.3; d = V(math.cos(a) * 0.5, math.sin(a) * 0.5, 1).normalized()
        f.gem(f"PetalIn{k}", c0 + d * 0.2, basis(d), (0.22, 0.09, 0.04), X)
    f.sphere("LotusCore", c0 + V(0, 0, 0.12), I3, (0.11, 0.11, 0.08), A, 12, 8)
def cattails(f):
    rng = np.random.default_rng(2)
    for i in range(7):
        x, y = rng.uniform(-0.7, 0.7, 2); h = rng.uniform(2.6, 3.8); b = V(x, y, 0); t = V(x + 0.12, y + 0.05, h)
        f.tube(f"Stalk{i}", [b, V(x + 0.04, y, h * 0.5), t], 0.05, 0.03, sw=P, K=6, sub=3)
        f.sphere(f"Tail{i}", t + V(-0.01, 0, -0.5), basis(V(0, 0, 1)), (0.48, 0.17, 0.17), D, 12, 8)
        f.tube(f"Spike{i}", [t + V(0, 0, -0.08), t + V(0.01, 0, 0.3)], 0.02, 0.005, sw=P, K=4, sub=1)
    for k in range(9):
        a = 2 * math.pi * k / 9; blade(f, f"Leaf{k}", V(0.6 * math.cos(a) * 0.5, 0.6 * math.sin(a) * 0.5, 0), V(0.3 * math.cos(a), 0.3 * math.sin(a), 1).normalized(), 2.2 + 0.4 * math.sin(3 * a))
def wooden_dock(f):
    for i, (x, y) in enumerate([(-1.6, -0.9), (-1.6, 0.9), (1.6, -0.9), (1.6, 0.9), (0, -0.9), (0, 0.9)]):
        f.cyl(f"Post{i}", V(x, y, -0.8), V(x, y, 0.75), 0.13, 10)
    for k in range(9):
        x = -1.8 + k * 0.45; f.box(f"Plank{k}", V(x, 0, 0.62), (0.4, 2.2, 0.1), Matrix.Rotation(0.03 * math.sin(k * 3), 3, "Z"), bevel=0.02)
    for y in (-0.9, 0.9): f.box(f"Beam{y}", V(0, y, 0.48), (3.7, 0.18, 0.18), bevel=0.02)
    f.torus("Rope", V(1.6, 0.9, 0.95), V(0, 0, 1), 0.16, 0.04, A, 16, 6)
    f.cyl("Bollard", V(1.6, 0.9, 0.67), V(1.6, 0.9, 1.15), 0.12, 10, proj=False)
def mossy_log(f):
    f.cyl("Log", V(-2, 0, 0.6), V(2, 0, 0.6), 0.6, 18)
    for sx in (-1, 1):
        f.cyl(f"Ring{sx}", V(sx * 1.97, 0, 0.6), V(sx * 2.03, 0, 0.6), 0.5, 18, X, proj=False)
    rng = np.random.default_rng(4)
    for k in range(8):
        x = rng.uniform(-1.7, 1.7); f.sphere(f"Moss{k}", V(x, rng.uniform(-0.25, 0.25), 1.12), I3, (rng.uniform(0.3, 0.5), 0.35, 0.12), P, 12, 6)
    for k in range(3):
        x = -1.2 + k * 0.5; f.cyl(f"MStem{k}", V(x, 0.45, 0.9), V(x, 0.5, 1.2), 0.04, 8, W, proj=False)
        f.sphere(f"MCap{k}", V(x, 0.5, 1.22), I3, (0.13, 0.13, 0.07), A, 10, 6)
def toadstools(f):
    for i, (x, y, h, r) in enumerate([(0, 0, 1.4, 0.8), (1.0, 0.4, 0.9, 0.55), (-0.8, 0.6, 0.6, 0.4)]):
        f.tube(f"Stem{i}", [V(x, y, 0), V(x, y, h)], 0, 0, sw=W, K=12, sub=4, rfn=lambda s, r=r: r * (0.35 - 0.1 * s))
        cap = V(x, y, h + r * 0.1); f.sphere(f"Cap{i}", cap, I3, (r, r, r * 0.55), P, 20, 12)
        for k in range(7):
            a = 2 * math.pi * k / 7 + i; el = 0.5 + 0.3 * (k % 2)
            d = V(math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el))
            f.sphere(f"Spot{i}{k}", cap + V(d.x * r, d.y * r, d.z * r * 0.55), basis(d), (0.02, r * 0.14, r * 0.14), W, 8, 6)
def row_boat(f):
    f.project(f.sphere("Hull", V(0, 0, 0.55), I3, (2.1, 0.9, 0.6), P, 24, 12))
    f.box("Deck", V(0, 0, 0.95), (3.3, 1.35, 0.08), sw=D, bevel=0.02, proj=False)
    for x in (-0.7, 0.6): f.box(f"Seat{x}", V(x, 0, 1.05), (0.35, 1.4, 0.1), bevel=0.02)
    for sy in (-1, 1):
        f.tube(f"Oar{sy}", [V(0.3, sy * 0.35, 1.05), V(-0.4, sy * 0.75, 1.0), V(-1.3, sy * 1.15, 0.85)], 0.05, 0.05, strip=1, K=6, sub=2)
        f.box(f"Blade{sy}", V(-1.55, sy * 1.27, 0.8), (0.6, 0.06, 0.26), Matrix.Rotation(sy * 0.42, 3, "Z"), sw=A, bevel=0.02, proj=False)
        f.torus(f"Oarlock{sy}", V(0.0, sy * 0.85, 1.0), V(0, 1, 0), 0.07, 0.025, M, 10, 5)

# ======================================================================== 2 RIVER
def river_stones(f):
    z = 0
    for i, r in enumerate((0.9, 0.7, 0.55, 0.42, 0.3)):
        f.rock(f"Cairn{i}", V(0.05 * i, 0, z + r * 0.7), r, seed=i); z += r * 1.2
    for i, (x, y, r) in enumerate([(1.4, 0.5, 0.45), (-1.3, -0.4, 0.55), (0.6, -1.2, 0.35)]): f.rock(f"Side{i}", V(x, y, r * 0.6), r, seed=10 + i)
def driftwood(f):
    pts = [V(-2.2, 0, 0.3), V(-0.6, 0.2, 0.55), V(0.9, -0.1, 0.45), V(2.3, 0.35, 0.8)]
    f.tube("Trunk", pts, 0.28, 0.08, strip=0, K=9)
    rng = np.random.default_rng(6)
    for k, p in enumerate((pts[1], pts[2], V(-1.5, 0.1, 0.4))):
        d = V(rng.uniform(-0.3, 0.6), rng.choice([-1, 1]) * rng.uniform(0.5, 1), rng.uniform(0.3, 0.7)).normalized()
        f.tube(f"Fork{k}", [p, p + d * 0.6, p + d * 1.2 + V(0, 0, 0.2)], 0.12, 0.03, strip=0, K=6)
    f.cyl("Root", V(-2.2, 0, 0.3), V(-2.35, 0, 0.3), 0.27, 9, X, proj=False)
def beaver_dam(f):
    f.project(f.sphere("Mound", V(0, 0, 0.0), I3, (2.2, 1.3, 0.55), D, 20, 10))
    rng = np.random.default_rng(7)
    for k in range(11):
        a = rng.uniform(0, math.pi); L = rng.uniform(1.8, 3.2); cz = rng.uniform(0.55, 1.05); cy = rng.uniform(-0.6, 0.6)
        d = V(math.cos(a) * L / 2, math.sin(a) * L / 2 * 0.4, rng.uniform(-0.2, 0.2))
        f.cyl(f"Stick{k}", V(rng.uniform(-0.6, 0.6), cy, cz) - d, V(rng.uniform(-0.6, 0.6), cy, cz) + d, rng.uniform(0.07, 0.14), 8)
def rope_bridge(f):
    sag = lambda x: 0.9 - 0.35 * (1 - (x / 3.2) ** 2)
    for k in range(13):
        x = -3.0 + k * 0.5; f.box(f"Plank{k}", V(x, 0, sag(x)), (0.35, 1.5, 0.08), Matrix.Rotation(0.06 * math.sin(k * 2.3), 3, "X"), bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1): f.cyl(f"Post{sx}{sy}", V(sx * 3.4, sy * 0.8, 0), V(sx * 3.4, sy * 0.8, 1.9), 0.12, 10)
    for sy in (-1, 1):
        f.tube(f"HandRope{sy}", [V(x, sy * 0.8, sag(x) + 0.85 + 0.15 * (x / 3.4) ** 2) for x in np.linspace(-3.4, 3.4, 9)], 0.04, 0.04, sw=A, K=6, sub=3)
        for x in np.linspace(-2.8, 2.8, 8):
            f.tube(f"Tie{sy}{x:.1f}", [V(x, sy * 0.76, sag(x)), V(x, sy * 0.8, sag(x) + 0.85)], 0.02, 0.02, sw=A, K=4, sub=1)
def water_wheel(f):
    hub = V(0, 0, 1.8)
    f.cyl("Axle", hub + V(0, -0.8, 0), hub + V(0, 0.8, 0), 0.12, 12, M, proj=False)
    for y in (-0.4, 0.4): f.torus(f"Rim{y}", hub + V(0, y, 0), V(0, 1, 0), 1.6, 0.08, X, 40, 6)
    for k in range(8):
        a = 2 * math.pi * k / 8
        for y in (-0.4, 0.4): f.box(f"Spoke{k}{y}", hub + V(0.8 * math.cos(a), y, 0.8 * math.sin(a)), (1.6, 0.12, 0.12), Matrix.Rotation(-a, 3, "Y"), bevel=0.02)
    for k in range(12):
        a = 2 * math.pi * k / 12 + 0.13; f.box(f"Paddle{k}", hub + V(1.75 * math.cos(a), 0, 1.75 * math.sin(a)), (0.08, 0.95, 0.5), Matrix.Rotation(-a, 3, "Y"), bevel=0.02)
    for sy in (-1, 1):
        for sx in (-1, 1): f.box(f"Leg{sy}{sx}", hub + V(sx * 0.6, sy * 0.75, -0.9), (0.15, 0.15, 2.0), Matrix.Rotation(-sx * 0.32, 3, "Y"), bevel=0.02)
def signpost(f):
    f.cyl("Pole", V(0, 0, 0), V(0, 0, 3.2), 0.12, 10)
    for k, (z, yaw) in enumerate([(2.7, 0.3), (2.2, 2.6), (1.7, 1.2)]):
        R = Matrix.Rotation(yaw, 3, "Z"); d = R @ V(1, 0, 0)
        f.box(f"Board{k}", V(0, 0, z) + d * 0.7, (1.3, 0.08, 0.36), R, sw=A, bevel=0.03, proj=False)
        f.gem(f"Arrow{k}", V(0, 0, z) + d * 1.42, R @ basis(V(1, 0, 0)), (0.22, 0.06, 0.24), A)
    f.sphere("Cap", V(0, 0, 3.25), I3, (0.16,) * 3, D, 10, 8)

# ======================================================================== 3 SWAMP
def mangrove_roots(f):
    f.tube("Trunk", [V(0, 0, 1.2), V(0.1, 0, 2.6), V(-0.1, 0.1, 4.0)], 0.35, 0.22, strip=0, K=9)
    for k in range(7):
        a = 2 * math.pi * k / 7; o = V(math.cos(a), math.sin(a), 0); p0 = V(0, 0, 1.3 + 0.1 * (k % 3))
        f.tube(f"Root{k}", [p0, p0 + o * 0.6 + V(0, 0, 0.3), p0 + o * 1.3 + V(0, 0, -0.4), o * 1.9], 0.16, 0.08, strip=0, K=7)
    for k in range(6):
        a = 2 * math.pi * k / 6; f.sphere(f"Canopy{k}", V(0.9 * math.cos(a), 0.9 * math.sin(a), 4.2 + 0.3 * math.sin(2 * a)), I3, (0.9, 0.9, 0.6), P, 14, 8)
    f.sphere("CanopyTop", V(0, 0, 4.7), I3, (1.0, 1.0, 0.7), P, 14, 8)
def stilt_hut(f):
    for i, (x, y) in enumerate([(-1, -1), (-1, 1), (1, -1), (1, 1)]): f.cyl(f"Stilt{i}", V(x, y, 0), V(x, y, 1.7), 0.1, 8)
    f.box("Floor", V(0, 0, 1.75), (2.7, 2.7, 0.2), bevel=0.03)
    f.box("Walls", V(0, 0, 2.65), (2.2, 2.2, 1.6), bevel=0.04)
    f.gem("Roof", V(0, 0, 3.75), Matrix.Rotation(math.pi / 4, 3, "Z"), (1.95, 1.95, 1.0), A)
    f.box("Door", V(1.11, 0, 2.4), (0.06, 0.7, 1.1), sw=D, bevel=0.02, proj=False)
    f.box("Window", V(0, 1.11, 2.8), (0.6, 0.06, 0.45), sw=G, bevel=0.02, glow=True)
    for sy in (-0.3, 0.3): f.cyl(f"Ladder{sy}", V(1.9, sy, 0), V(1.35, sy, 1.8), 0.05, 6)
    for k in range(5):
        t = (k + 0.5) / 5; f.cyl(f"Rung{k}", V(lerp(1.9, 1.35, t), -0.3, 1.8 * t), V(lerp(1.9, 1.35, t), 0.3, 1.8 * t), 0.04, 6)
def wisp_lantern(f):
    f.tube("Pole", [V(0, 0, 0), V(0, 0, 2.2), V(0.3, 0, 3.1), V(1.1, 0, 3.3)], 0.12, 0.07, strip=0, K=7)
    f.tube("Chain", [V(1.1, 0, 3.3), V(1.1, 0, 2.8)], 0.025, 0.025, sw=D, K=4, sub=1)
    lc = V(1.1, 0, 2.45)
    f.cyl("LTop", lc + V(0, 0, 0.32), lc + V(0, 0, 0.42), 0.3, 12, D, proj=False)
    f.cyl("LBot", lc + V(0, 0, -0.42), lc + V(0, 0, -0.32), 0.3, 12, D, proj=False)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2; f.cyl(f"LRod{k}", lc + V(0.25 * math.cos(a), 0.25 * math.sin(a), -0.35), lc + V(0.25 * math.cos(a), 0.25 * math.sin(a), 0.35), 0.025, 5, D, proj=False)
    f.sphere("Wisp", lc, I3, (0.2, 0.2, 0.24), G, 14, 10, glow=True)
    f.tube("WispTail", [lc + V(0, 0, 0.1), lc + V(-0.1, 0.05, 0.25), lc + V(0.05, 0, 0.32)], 0.08, 0.01, glow=True, sw=G, K=6, sub=3)
def gator_skull(f):
    c0 = V(0, 0, 0.45)
    f.sphere("Skull", c0, I3, (0.7, 0.55, 0.42), P, 18, 10)
    f.tube("Snout", [c0 + V(0.3, 0, 0), c0 + V(1.2, 0, -0.05), c0 + V(1.9, 0, -0.1)], 0.34, 0.18, sw=P, K=10)
    f.tube("Jaw", [c0 + V(0.1, 0, -0.32), c0 + V(1.1, 0, -0.35), c0 + V(1.8, 0, -0.32)], 0.2, 0.12, sw=P, K=10)
    for sy in (-1, 1):
        f.sphere(f"Socket{sy}", c0 + V(0.15, sy * 0.3, 0.25), I3, (0.15, 0.12, 0.12), D, 10, 6)
        f.sphere(f"Nostril{sy}", c0 + V(1.85, sy * 0.08, 0.05), I3, (0.05,) * 3, D, 8, 6)
        for k in range(6):
            p = c0 + V(0.6 + k * 0.22, sy * (0.26 - 0.015 * k), -0.18)
            f.tube(f"Tooth{sy}{k}", [p, p + V(0, 0, -0.12), p + V(0.01, 0, -0.18)], 0.04, 0.004, sw=W, K=5, sub=2)
def glow_shrooms(f):
    rng = np.random.default_rng(12)
    for i in range(7):
        x, y = rng.uniform(-0.8, 0.8, 2); h = rng.uniform(0.7, 2.0); r = 0.15 + 0.15 * h
        f.tube(f"Stem{i}", [V(x, y, 0), V(x + 0.1, y, h * 0.6), V(x + 0.05, y + 0.05, h)], 0.06, 0.04, sw=W, K=6, sub=3)
        f.sphere(f"Cap{i}", V(x + 0.05, y + 0.05, h + 0.02), I3, (r, r, r * 0.5), G, 14, 8, glow=True)
    f.project(f.sphere("Mud", V(0, 0, 0), I3, (1.3, 1.3, 0.25), D, 16, 8))
def dead_tree(f):
    rng = np.random.default_rng(13)
    hang = []
    branchy(f, "Trunk", V(0, 0, 0), V(0, 0, 1), 2.4, 0.32, 2, rng, leaf=lambda q, d: hang.append(q))
    for k, q in enumerate(hang):
        f.tube(f"Moss{k}", [q, q + V(0.03, 0, -0.4), q + V(0, 0.02, -0.8)], 0.05, 0.02, sw=P, K=5, sub=2)

# ======================================================================== 4 CORAL REEF
def brain_coral(f):
    f.project(f.sphere("Brain", V(0, 0, 0.65), I3, (1.3, 1.2, 0.95), P, 28, 16))
    f.rock("Base", V(0, 0, 0.15), 0.9, sw=D, seed=3, proj=False)
def staghorn(f):
    rng = np.random.default_rng(14)
    for k in range(5):
        a = 2 * math.pi * k / 5; branchy(f, f"Stag{k}", V(0.2 * math.cos(a), 0.2 * math.sin(a), 0), V(0.4 * math.cos(a), 0.4 * math.sin(a), 1).normalized(), 1.1, 0.16, 2, rng, strip=1)
def sea_fan(f):
    f.fin("Fan", lambda s: V(lerp(-0.15, 0.15, s), 0, 0.6), lambda s: V(lerp(-1.1, 1.1, s), 0, 1), lambda s: 2.2 * (0.6 + 0.4 * math.sin(math.pi * s)),
          lambda s, r: V(0, 0.15 * r * r * math.sin(5 * s), 0), 20, 10, 0.04, 0)
    f.tube("Stalk", [V(0, 0, 0), V(0, 0, 0.7)], 0.12, 0.09, strip=1, K=8, sub=2)
    f.rock("Holdfast", V(0, 0, 0.05), 0.35, sw=D, seed=2, proj=False)
def anemone(f):
    f.cyl("Column", V(0, 0, 0), V(0, 0, 0.7), 0.55, 20, P, proj=False)
    f.sphere("Disc", V(0, 0, 0.7), I3, (0.55, 0.55, 0.1), X, 20, 6)
    for k in range(22):
        a = 2 * math.pi * k / 22; rr = 0.45 if k % 2 else 0.3; p = V(rr * math.cos(a), rr * math.sin(a), 0.72); o = V(math.cos(a), math.sin(a), 0)
        f.tube(f"Tent{k}", [p, p + o * 0.25 + V(0, 0, 0.45), p + o * 0.55 + V(0.08 * math.sin(k), 0, 0.85)], 0.07, 0.03, strip=1, K=6, sub=3)
def giant_clam(f):
    hinge = V(-1.0, 0, 0.3)
    f.sphere("ShellBot", V(0, 0, 0.3), I3, (1.2, 1.0, 0.35), P, 22, 10)
    Rt = Matrix.Rotation(math.radians(-38), 3, "Y"); Mt = Matrix.Translation(hinge) @ Rt.to_4x4() @ Matrix.Translation(-hinge)
    f.sphere("ShellTop", Mt @ V(0, 0, 0.42), Rt, (1.2, 1.0, 0.3), P, 22, 10)
    for k in range(7):
        a = lerp(-1.1, 1.1, k / 6); d = V(math.cos(a), math.sin(a), 0)
        f.tube(f"RidgeB{k}", [hinge, hinge + d * 1.1 + V(0.9, 0, 0.0) * 0 + V(0, 0, 0.3), V(0, 0, 0.3) + V(1.15 * math.cos(a), 0.95 * math.sin(a), 0.05)], 0.06, 0.05, sw=A, K=5, sub=3)
    f.sphere("Mantle", V(0.05, 0, 0.5), I3, (1.0, 0.85, 0.1), X, 20, 6)
    f.sphere("Pearl", V(0.2, 0, 0.66), I3, (0.2,) * 3, W, 16, 10)
def tube_sponge(f):
    for i, (x, y, h, r) in enumerate([(0, 0, 2.2, 0.4), (0.7, 0.3, 1.6, 0.32), (-0.6, 0.4, 1.3, 0.3), (0.3, -0.7, 1.0, 0.28), (-0.4, -0.5, 1.8, 0.33)]):
        f.cyl(f"Tube{i}", V(x, y, 0), V(x, y, h), r, 16)
        f.torus(f"Lip{i}", V(x, y, h), V(0, 0, 1), r, 0.06, A, 18, 6)
        f.cyl(f"Hole{i}", V(x, y, h - 0.05), V(x, y, h + 0.005), r * 0.8, 16, D, proj=False)

# ======================================================================== 5 OPEN OCEAN
def buoy(f):
    f.project(f.sphere("Float", V(0, 0, 0.5), I3, (1.0, 1.0, 0.75), P, 22, 12))
    f.torus("Band", V(0, 0, 0.5), V(0, 0, 1), 0.98, 0.1, W, 32, 8)
    f.cyl("Mast", V(0, 0, 1.1), V(0, 0, 2.8), 0.12, 10, M, proj=False)
    for k in range(4):
        a = k * math.pi / 2; f.cyl(f"Cage{k}", V(0.35 * math.cos(a), 0.35 * math.sin(a), 1.2), V(0.15 * math.cos(a), 0.15 * math.sin(a), 2.6), 0.04, 6, M, proj=False)
    f.sphere("Lamp", V(0, 0, 2.95), I3, (0.22, 0.22, 0.28), G, 14, 10, glow=True)
    f.cyl("Weight", V(0, 0, -0.6), V(0, 0, -0.1), 0.25, 12, D, proj=False)
def floating_crates(f):
    for i, (x, y, s, yaw) in enumerate([(0, 0, 1.1, 0.2), (1.2, 0.6, 0.85, -0.4)]):
        R = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(0.12 * (i + 1), 3, "X")
        f.box(f"Crate{i}", V(x, y, s * 0.5), (s, s, s), R, bevel=0.04)
        f.box(f"Slat{i}", V(x, y, s * 0.5), (s * 1.03, s * 1.03, s * 0.18), R, sw=D, bevel=0.02, proj=False)
    bc = V(-1.1, 0.4, 0.45)
    f.tube("Barrel", [bc + V(0, -0.6, 0), bc, bc + V(0, 0.6, 0)], 0, 0, strip=1, K=16, sub=6, rfn=lambda s: 0.42 + 0.08 * math.sin(math.pi * s))
    for y in (-0.38, 0.38): f.torus(f"Hoop{y}", bc + V(0, y, 0), V(0, 1, 0), 0.47, 0.035, M, 24, 6)
def kelp_stalks(f):
    rng = np.random.default_rng(15)
    for i in range(4):
        x, y = rng.uniform(-0.8, 0.8, 2); h = rng.uniform(4.5, 6.5)
        pts = [V(x + 0.3 * math.sin(z * 1.3 + i), y + 0.2 * math.cos(z + i), z) for z in np.linspace(0, h, 6)]
        f.tube(f"Stalk{i}", pts, 0.08, 0.05, sw=P, K=6, sub=4)
        for k in range(5):
            p = pts[k + 1]; d = V(math.cos(k * 2.4 + i), math.sin(k * 2.4 + i), 0.6).normalized()
            blade(f, f"Frond{i}{k}", p, d, 1.1, w=0.18, droop=0.3)
            f.sphere(f"Bladder{i}{k}", p + d * 0.15, I3, (0.09,) * 3, A, 8, 6)
def life_ring(f):
    cen = V(0, 0, 1.1); n = V(1, 0, 0)
    f.torus("Ring", cen, n, 0.85, 0.27, P, 32, 12)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4; q = cen + V(0, 0.85 * math.cos(a), 0.85 * math.sin(a)); tng = V(0, -math.sin(a), math.cos(a))
        f.torus(f"Stripe{k}", q, tng, 0.285, 0.07, W, 16, 6)
    f.torus("Rope", cen + V(0.02, 0, 0), n, 1.13, 0.03, A, 40, 5)
    f.cyl("Hook", V(-0.3, 0, 0), V(-0.3, 0, 2.3), 0.07, 8, M, proj=False)
def message_bottle(f):
    f.project(f.sphere("Sand", V(0, 0, 0), I3, (1.4, 1.0, 0.25), D, 18, 8))
    prof = lambda s: 0.3 if s < 0.62 else lerp(0.3, 0.11, min(1, (s - 0.62) / 0.15))
    f.tube("Bottle", [V(-0.8, 0, 0.35), V(0.2, 0, 0.38), V(0.9, 0, 0.45)], 0, 0, sw=P, K=16, sub=8, rfn=prof)
    f.cyl("Cork", V(0.88, 0, 0.45), V(1.05, 0, 0.47), 0.1, 10, A, proj=False)
    f.cyl("Scroll", V(-0.5, 0, 0.35), V(0.2, 0, 0.37), 0.13, 12, W, proj=False)
    f.torus("Ribbon", V(-0.15, 0, 0.36), V(1, 0, 0), 0.14, 0.025, X, 14, 5)
def net_floats(f):
    z = lambda x, y: 0.25 + 0.5 * (1 - (x / 2) ** 2) * (1 - (y / 1.5) ** 2) * 0.3
    for k in range(7):
        y = lerp(-1.5, 1.5, k / 6); f.tube(f"NetX{k}", [V(x, y, z(x, y)) for x in np.linspace(-2, 2, 7)], 0.02, 0.02, sw=A, K=4, sub=2)
        x = lerp(-2, 2, k / 6); f.tube(f"NetY{k}", [V(x, y, z(x, y)) for y in np.linspace(-1.5, 1.5, 6)], 0.02, 0.02, sw=A, K=4, sub=2)
    for k in range(6): f.sphere(f"FloatBall{k}", V(lerp(-2, 2, k / 5), 1.55, 0.3), I3, (0.2, 0.2, 0.2), P, 12, 8)
    f.tube("EdgeRope", [V(x, 1.55, 0.3) for x in np.linspace(-2.1, 2.1, 5)], 0.04, 0.04, sw=M, K=6, sub=2)

# ======================================================================== 6 FROZEN SEA
def iceberg(f):
    for i, (x, y, s, h) in enumerate([(0, 0, 1.4, 3.2), (1.1, 0.5, 0.9, 2.0), (-1.0, -0.4, 1.0, 2.4), (0.4, -1.0, 0.7, 1.4)]):
        f.project(f.gem(f"Berg{i}", V(x, y, h * 0.35), basis(V(0.1 * i, 0.05, 1), V(1, 0, 0)), (h * 0.6, s, s * 0.9), P))
    f.project(f.sphere("Floe", V(0, 0, 0), I3, (2.4, 2.0, 0.25), W, 18, 8))
def ice_crystals(f):
    f.sphere("Snow", V(0, 0, 0), I3, (1.4, 1.4, 0.4), W, 18, 8)
    rng = np.random.default_rng(16)
    for k in range(9):
        a = 2 * math.pi * k / 9; d = V(0.5 * math.cos(a), 0.5 * math.sin(a), 1).normalized(); L = rng.uniform(0.7, 1.4)
        f.gem(f"Crystal{k}", V(0.5 * math.cos(a), 0.5 * math.sin(a), 0.2) + d * L * 0.9, basis(d), (L, 0.18, 0.18), P)
    f.gem("Core", V(0, 0, 1.3), basis(V(0, 0, 1)), (1.2, 0.3, 0.3), G, glow=True)
def igloo(f):
    f.project(f.sphere("Dome", V(0, 0, 0), I3, (1.7, 1.7, 1.5), P, 24, 14))
    f.project(f.cyl("Tunnel", V(1.2, 0, 0.35), V(2.1, 0, 0.35), 0.62, 16, P))
    f.sphere("Door", V(2.12, 0, 0.3), basis(V(1, 0, 0)), (0.05, 0.42, 0.5), D, 14, 8)
def ice_fishing_hut(f):
    f.box("Hut", V(0, 0, 0.9), (1.8, 1.5, 1.8), bevel=0.04)
    for sy in (-1, 1): f.box(f"Roof{sy}", V(0, sy * 0.45, 1.95), (2.0, 1.05, 0.12), Matrix.Rotation(sy * 0.45, 3, "X"), sw=W, bevel=0.03, proj=False)
    f.box("Door", V(0.91, 0, 0.7), (0.05, 0.6, 1.1), sw=D, bevel=0.02, proj=False)
    f.cyl("Chimney", V(-0.5, 0.4, 1.8), V(-0.5, 0.4, 2.6), 0.12, 10, D, proj=False)
    for k in range(3): f.sphere(f"Smoke{k}", V(-0.5 - 0.15 * k, 0.4, 2.8 + 0.3 * k), I3, (0.15 + 0.06 * k,) * 3, W, 10, 8)
    f.cyl("Hole", V(1.7, 0.3, 0.0), V(1.7, 0.3, 0.02), 0.4, 18, D, proj=False)
    f.tube("Rod", [V(1.4, 0.0, 0.1), V(1.6, 0.2, 0.8), V(1.75, 0.3, 1.2)], 0.03, 0.015, sw=A, K=5, sub=2)
    f.sphere("SnowBase", V(0, 0, 0), I3, (2.4, 2.0, 0.15), W, 18, 6)
def snowman(f):
    for i, (z, r) in enumerate([(0.85, 0.9), (2.15, 0.65), (3.1, 0.45)]): f.sphere(f"Ball{i}", V(0, 0, z), I3, (r,) * 3, W, 20, 12)
    f.tube("Carrot", [V(0.4, 0, 3.1), V(0.9, 0, 3.05)], 0.08, 0.01, sw=A, K=8, sub=2)
    for sy in (-1, 1):
        f.sphere(f"Eye{sy}", V(0.38, sy * 0.15, 3.25), I3, (0.05,) * 3, D, 8, 6)
        f.tube(f"Arm{sy}", [V(0, sy * 0.6, 2.3), V(0, sy * 1.2, 2.7), V(0.05, sy * 1.5, 2.9)], 0.05, 0.02, sw=X, K=5, sub=2)
    for k in range(3): f.sphere(f"Button{k}", V(0.64 - 0.04 * k, 0, 2.35 - 0.25 * k), I3, (0.06,) * 3, D, 8, 6)
    f.torus("Scarf", V(0, 0, 2.7), V(0, 0, 1), 0.45, 0.12, P, 20, 8)
    f.box("ScarfTail", V(0.25, 0.3, 2.35), (0.18, 0.08, 0.6), sw=P, bevel=0.03, proj=False)
    f.cyl("HatBrim", V(0, 0, 3.47), V(0, 0, 3.53), 0.45, 18, D, proj=False); f.cyl("Hat", V(0, 0, 3.5), V(0, 0, 4.1), 0.3, 18, D, proj=False)
def icicle_arch(f):
    pts = ring(V(0, 0, 0), 2.2, 9, 0, math.pi, axis="y")
    f.tube("Arch", pts, 0.38, 0.38, sw=P, K=10, sub=4)
    for k in range(1, 12):
        a = math.pi * k / 12; p = V(2.2 * math.cos(a), 0, 2.2 * math.sin(a) - 0.3); L = 0.4 + 0.3 * (k % 3)
        f.tube(f"Icicle{k}", [p, p + V(0, 0, -L)], 0.1, 0.005, sw=X, K=6, sub=1)
    for sx in (-1, 1): f.gem(f"Tip{sx}", V(sx * 2.2, 0, 0.2), basis(V(0, 0, 1)), (0.4, 0.45, 0.45), X)

# ======================================================================== 7 DEEP ABYSS
def whale_ribcage(f):
    spine = [V(x, 0, 1.8 + 0.3 * math.sin(x * 0.6)) for x in np.linspace(-3.5, 3.5, 7)]
    f.tube("Spine", spine, 0.22, 0.12, sw=P, K=8, sub=4)
    for k in range(7):
        x = lerp(-2.4, 2.4, k / 6); top = V(x, 0, 1.8 + 0.3 * math.sin(x * 0.6)); h = 1.2 + 0.5 * math.sin(math.pi * k / 6)
        for sy in (-1, 1):
            f.tube(f"Rib{k}{sy}", [top, top + V(0, sy * 0.9 * h, -0.2), top + V(0.1, sy * 1.2 * h, -1.2), V(x + 0.2, sy * 0.9 * h, 0)], 0.12, 0.05, sw=P, K=6)
def tube_worms(f):
    rng = np.random.default_rng(17)
    f.rock("Base", V(0, 0, 0.1), 0.9, sw=D, seed=8, proj=False)
    for i in range(11):
        x, y = rng.uniform(-0.7, 0.7, 2); h = rng.uniform(1.2, 2.6)
        f.tube(f"Worm{i}", [V(x, y, 0.3), V(x + 0.05, y, h * 0.5), V(x, y + 0.05, h)], 0, 0, sw=W, K=8, sub=4, rfn=lambda s: 0.09 * (1 + 0.15 * math.sin(s * 40)))
        f.sphere(f"Plume{i}", V(x, y + 0.05, h + 0.08), I3, (0.16, 0.16, 0.12), G, 10, 6, glow=True)
def submarine_wreck(f):
    R = Matrix.Rotation(0.25, 3, "Y") @ Matrix.Rotation(0.15, 3, "X")
    f.project(f.sphere("Hull", V(0, 0, 0.8), R, (2.7, 0.9, 0.9), P, 24, 12))
    f.box("Tower", V(0.3, 0, 1.75), (1.0, 0.5, 0.9), R, bevel=0.08)
    f.tube("Periscope", [V(0.5, 0, 2.1), V(0.6, 0, 2.7), V(0.85, 0, 2.75)], 0.06, 0.06, sw=M, K=6, sub=2)
    for k in range(4): f.sphere(f"Port{k}", V(-1.2 + 0.7 * k, 0.86, 0.75 + 0.18 * (k - 1.5) * 0.25), basis(V(0, 1, 0)), (0.16, 0.16, 0.04), G, 12, 6, glow=True)
    for k in range(4):
        a = k * math.pi / 2; f.gem(f"Prop{k}", V(-2.85, 0.35 * math.cos(a), 0.15 + 0.35 * math.sin(a)), basis(V(0, math.cos(a), math.sin(a))), (0.35, 0.06, 0.15), M)
def glow_polyps(f):
    for i in range(5):
        a = 2 * math.pi * i / 5; b = V(0.6 * math.cos(a), 0.6 * math.sin(a), 0); h = 1.4 + 0.4 * math.sin(i * 2)
        f.tube(f"Pen{i}", [b, b + V(0.05, 0, h * 0.5), b + V(0, 0.05, h)], 0.08, 0.04, sw=P, K=6, sub=3)
        f.fin(f"Feather{i}", lambda s, b=b, h=h: b + V(0, 0, lerp(0.4, h, s)), lambda s: V(0, 1, 0.3), lambda s: 0.35 * math.sin(math.pi * s) + 0.05,
              lambda s, r: V(0, 0, 0), 10, 3, 0.03, 0, glow=True)
        f.fin(f"FeatherB{i}", lambda s, b=b, h=h: b + V(0, 0, lerp(0.4, h, s)), lambda s: V(0, -1, 0.3), lambda s: 0.35 * math.sin(math.pi * s) + 0.05,
              lambda s, r: V(0, 0, 0), 10, 3, 0.03, 0, glow=True)
def eye_rock(f):
    c0 = V(0, 0, 1.1); f.rock("Rock", c0, 1.3, sw=P, seed=9)
    for k, (a, el, r) in enumerate([(0.2, 0.3, 0.22), (-0.4, 0.1, 0.16), (0.7, -0.1, 0.14), (0.0, -0.3, 0.18), (-0.2, 0.6, 0.12)]):
        d = V(math.cos(el) * math.cos(a), math.cos(el) * math.sin(a), math.sin(el))
        f.sphere(f"Eye{k}", c0 + d * 1.18, basis(d), (r,) * 3, G, 12, 8, glow=True)
        f.sphere(f"Pupil{k}", c0 + d * (1.18 + r * 0.82), basis(d), (r * 0.3, r * 0.2, r * 0.7), D, 8, 6)
def trench_spire(f):
    z = 0
    for i, r in enumerate((1.0, 0.8, 0.65, 0.5, 0.38, 0.26)):
        f.rock(f"Spire{i}", V(0.1 * math.sin(i), 0.1 * math.cos(i), z + r * 0.8), r, sw=P, seed=20 + i); z += r * 1.35
    rng = np.random.default_rng(21)
    for k in range(7):
        zz = rng.uniform(0.5, z - 0.5); a = rng.uniform(0, 2 * math.pi); rr = 0.9 * (1 - zz / z) + 0.25
        d = V(math.cos(a), math.sin(a), 0.4).normalized()
        f.gem(f"Vein{k}", V(rr * math.cos(a), rr * math.sin(a), zz), basis(d), (0.3, 0.08, 0.08), G, glow=True)

# ======================================================================== 8 VOLCANIC VENT
def black_smoker(f):
    z = 0
    for i, r in enumerate((1.0, 0.8, 0.65, 0.55)):
        f.rock(f"Chimney{i}", V(0.05 * i, 0, z + r * 0.8), r, sw=P, seed=30 + i); z += r * 1.3
    f.torus("Crater", V(0.15, 0, z + 0.1), V(0, 0, 1), 0.35, 0.12, G, 20, 8, glow=True)
    f.sphere("MagmaTop", V(0.15, 0, z + 0.1), I3, (0.32, 0.32, 0.08), G, 14, 6, glow=True)
    for k in range(4): f.sphere(f"Smoke{k}", V(0.2 + 0.2 * k, 0.1 * k, z + 0.6 + 0.55 * k), I3, (0.35 + 0.12 * k,) * 3, D, 12, 8)
def basalt_columns(f):
    rng = np.random.default_rng(31)
    for i in range(10):
        a = 2 * math.pi * i / 7 if i < 7 else 2 * math.pi * i / 3; rr = 0.75 if i < 7 else 0.3
        x, y = rr * math.cos(a), rr * math.sin(a); h = rng.uniform(0.8, 3.0) if i < 7 else rng.uniform(2.5, 3.6)
        f.cyl(f"Col{i}", V(x, y, 0), V(x, y, h), 0.36, 6)
def obsidian_shards(f):
    rng = np.random.default_rng(32)
    for k in range(9):
        a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(0, 0.9); d = V(0.4 * math.cos(a), 0.4 * math.sin(a), 1).normalized(); L = rng.uniform(0.6, 1.6)
        f.gem(f"Shard{k}", V(rr * math.cos(a), rr * math.sin(a), 0) + d * L * 0.8, basis(d), (L, 0.22, 0.14), P)
    f.rock("Base", V(0, 0, 0), 0.9, sw=D, seed=5, proj=False)
def magma_pool(f):
    for k in range(10):
        a = 2 * math.pi * k / 10; f.rock(f"Rim{k}", V(1.5 * math.cos(a), 1.5 * math.sin(a), 0.2), 0.45 + 0.1 * math.sin(3 * a), sw=P, seed=40 + k)
    f.sphere("Magma", V(0, 0, 0.25), I3, (1.45, 1.45, 0.12), G, 24, 6, glow=True)
    for k in range(4): f.sphere(f"Bubble{k}", V(0.6 * math.cos(k * 1.7), 0.6 * math.sin(k * 1.7), 0.38), I3, (0.12 + 0.04 * k,) * 3, G, 10, 6, glow=True)
def sulfur_crystals(f):
    f.rock("Rock", V(0, 0, 0.5), 1.0, sw=P, seed=33)
    rng = np.random.default_rng(34)
    for k in range(11):
        a = rng.uniform(0, 2 * math.pi); el = rng.uniform(0.2, 1.2); d = V(math.cos(el) * math.cos(a), math.cos(el) * math.sin(a), math.sin(el)); L = rng.uniform(0.4, 0.9)
        f.gem(f"Sulfur{k}", V(0, 0, 0.5) + d * (0.9 + L * 0.4), basis(d), (L, 0.15, 0.15), X)
def volcanic_bomb(f):
    c0 = V(0, 0, 1.2); f.rock("Bomb", c0, 1.2, sw=P, seed=35); f.cracks("Crack", c0, 1.2, 12, 36, 0.05)
    f.project(f.sphere("Crater", V(0, 0, 0), I3, (1.8, 1.8, 0.2), D, 18, 6))

# ======================================================================== 9 SUNKEN RUINS
def broken_pillar(f):
    f.box("Plinth", V(0, 0, 0.2), (1.4, 1.4, 0.4), bevel=0.05)
    f.tube("Column", [V(0, 0, 0.4), V(0, 0, 2.0), V(0, 0, 3.4)], 0, 0, sw=P, K=16, sub=4, rfn=lambda s: 0.5 * (1 - 0.08 * s))
    f.rock("Break", V(0.05, 0, 3.4), 0.48, sw=P, seed=50)
    f.cyl("Drum", V(1.0, 0.4, 0.45), V(2.2, 1.0, 0.45), 0.45, 16)
    f.box("Capital", V(-1.4, -0.6, 0.25), (1.0, 1.0, 0.5), Matrix.Rotation(0.4, 3, "Z"), bevel=0.06)
def statue_head(f):
    c0 = V(0, 0, 1.1); f.project(f.sphere("Head", c0, I3, (1.1, 1.0, 1.3), P, 22, 14))
    f.box("Nose", c0 + V(1.05, 0, -0.05), (0.3, 0.25, 0.5), Matrix.Rotation(-0.2, 3, "Y"), bevel=0.08)
    f.box("Brow", c0 + V(0.95, 0, 0.3), (0.2, 1.0, 0.15), bevel=0.05)
    f.box("Lips", c0 + V(0.98, 0, -0.5), (0.15, 0.5, 0.12), bevel=0.04)
    for sy in (-1, 1): f.sphere(f"Eye{sy}", c0 + V(0.92, sy * 0.3, 0.1), basis(V(1, 0, 0)), (0.06, 0.16, 0.1), D, 10, 6)
    for k in range(5):
        a = lerp(-1.2, 1.2, k / 4); f.gem(f"Crown{k}", c0 + V(0.6 * math.cos(a), 0.9 * math.sin(a), 1.1), basis(V(0, 0, 1)), (0.4, 0.12, 0.12), A)
def treasure_chest(f):
    f.box("Chest", V(0, 0, 0.45), (1.6, 1.0, 0.9), bevel=0.05)
    hinge = V(-0.5, 0, 0.9); Rl = Matrix.Rotation(math.radians(-60), 3, "Y"); Ml = Matrix.Translation(hinge) @ Rl.to_4x4() @ Matrix.Translation(-hinge)
    f.project(f.tube("Lid", [Ml @ V(0, -0.5, 0.9), Ml @ V(0, 0, 0.9), Ml @ V(0, 0.5, 0.9)], 0, 0, sw=P, K=16, sub=2, rfn=lambda s: 0.5))
    for x in (-0.55, 0.55): f.box(f"Band{x}", V(x, 0, 0.45), (0.12, 1.04, 0.94), sw=A, bevel=0.02, proj=False)
    f.box("Glow", V(0, 0, 0.88), (1.4, 0.85, 0.08), sw=G, bevel=0.02, glow=True)
    rng = np.random.default_rng(51)
    for k in range(12): f.sphere(f"Coin{k}", V(rng.uniform(-0.6, 0.6), rng.uniform(-0.35, 0.35), 0.95 + rng.uniform(0, 0.15)), basis(V(*rng.normal(size=3))), (0.03, 0.13, 0.13), A, 10, 4)
    for k in range(6): f.sphere(f"Spill{k}", V(1.0 + 0.2 * k, rng.uniform(-0.6, 0.6), 0.03), I3, (0.13, 0.13, 0.03), A, 10, 4)
def archway(f):
    for sx in (-1, 1): f.box(f"Pillar{sx}", V(sx * 1.6, 0, 1.2), (0.6, 0.7, 2.4), bevel=0.06)
    f.project(f.tube("Arch", ring(V(0, 0, 2.4), 1.6, 9, 0, math.pi, axis="y"), 0.34, 0.34, sw=P, K=8, sub=4))
    f.box("Keystone", V(0, 0, 4.0), (0.45, 0.75, 0.55), bevel=0.05)
    for k in range(4): f.tube(f"Vine{k}", [V(-1.6 + 0.1 * k, 0.37, 2.4 - 0.3 * k), V(-1.4, 0.4, 1.6 - 0.2 * k), V(-1.55, 0.38, 0.7 - 0.1 * k)], 0.04, 0.03, sw=X, K=5)
def amphorae(f):
    for i, (x, y, sc, lie) in enumerate([(0, 0, 1.0, False), (0.95, 0.35, 0.8, False), (-1.0, 0.5, 0.85, True)]):
        R = Matrix.Rotation(math.radians(80), 3, "Y") if lie else I3
        base = V(x, y, 0.42 * sc if lie else 0)
        L = lambda v, R=R, base=base, sc=sc: base + R @ (v * sc)
        f.sphere(f"Body{i}", L(V(0, 0, 0.75)), R, (0.48 * sc, 0.48 * sc, 0.6 * sc), P, 10, 7)
        f.cyl(f"Neck{i}", L(V(0, 0, 1.2)), L(V(0, 0, 1.6)), 0.17 * sc, 8, P, proj=False)
        f.torus(f"Lip{i}", L(V(0, 0, 1.6)), R @ V(0, 0, 1), 0.2 * sc, 0.05 * sc, A, 12, 5)
        f.cyl(f"Foot{i}", L(V(0, 0, 0.0)), L(V(0, 0, 0.2)), 0.22 * sc, 8, A, proj=False)
        for sy in (-1, 1):
            f.tube(f"Handle{i}{sy}", [L(V(0, sy * 0.17, 1.45)), L(V(0, sy * 0.42, 1.4)), L(V(0, sy * 0.4, 1.05))], 0.04 * sc, 0.04 * sc, sw=A, K=5, sub=3)
def trident_altar(f):
    for i, (s, h) in enumerate([(2.4, 0.3), (1.8, 0.3), (1.2, 0.3)]): f.box(f"Step{i}", V(0, 0, 0.15 + i * 0.3), (s, s, h), bevel=0.04)
    base = V(0, 0, 1.0)
    f.tube("Shaft", [base, base + V(0, 0, 1.5), base + V(0, 0, 3.0)], 0.07, 0.07, sw=A, K=8, sub=2)
    f.tube("Cross", [base + V(0, -0.45, 3.0), base + V(0, 0, 2.9), base + V(0, 0.45, 3.0)], 0.07, 0.07, sw=A, K=8, sub=3)
    for y in (-0.45, 0, 0.45):
        f.tube(f"Prong{y}", [base + V(0, y, 3.0), base + V(0, y, 3.6 + (0.2 if y == 0 else 0))], 0.06, 0.02, sw=A, K=6, sub=1)
        f.gem(f"Tip{y}", base + V(0, y, 3.7 + (0.2 if y == 0 else 0)), basis(V(0, 0, 1)), (0.2, 0.08, 0.08), G, glow=True)

# ======================================================================== 10 STARFALL LAKE
def fallen_star(f):
    for k in range(9):
        a = 2 * math.pi * k / 9; f.rock(f"Crater{k}", V(1.5 * math.cos(a), 1.5 * math.sin(a), 0.15), 0.4, sw=D, seed=60 + k, proj=False)
    c0 = V(0, 0, 0.8); n = V(0.3, 0, 1).normalized(); Bm = basis(n); u, v = Bm.col[1], Bm.col[2]
    f.sphere("StarCore", c0, I3, (0.42,) * 3, G, 16, 10, glow=True)
    for k in range(5):
        a = 2 * math.pi * k / 5; d = u * math.cos(a) + v * math.sin(a)
        f.gem(f"Arm{k}", c0 + d * 0.55, basis(d, n), (0.6, 0.3, 0.16), G, glow=True)
def star_crystal_tree(f):
    rng = np.random.default_rng(61)
    leaf = lambda q, d: f.gem(f"Leaf{len(f.glow)}", q + d * 0.15, basis(d), (0.32, 0.12, 0.12), G, glow=True)
    branchy(f, "Trunk", V(0, 0, 0), V(0, 0, 1), 1.8, 0.28, 2, rng, strip=0, leaf=leaf)
    f.project(f.sphere("Roots", V(0, 0, 0), I3, (0.9, 0.9, 0.2), P, 16, 6))
def telescope(f):
    top = V(0, 0, 1.8)
    for k in range(3):
        a = 2 * math.pi * k / 3; f.tube(f"Leg{k}", [top, V(0.9 * math.cos(a), 0.9 * math.sin(a), 0)], 0.06, 0.05, sw=A, K=6, sub=1)
    d = V(0.8, 0, 0.6).normalized()
    f.cyl("Tube", top - d * 0.8, top + d * 1.0, 0.22, 16, P)
    for t in (-0.6, 0.2, 0.9): f.torus(f"Band{t}", top + d * t, d, 0.23, 0.035, A, 18, 6)
    f.cyl("Lens", top + d * 1.0, top + d * 1.03, 0.19, 16, G, glow=True)
    f.cyl("Eyepiece", top - d * 0.8, top - d * 1.05, 0.08, 10, A, proj=False)
def meteor_chunk(f):
    c0 = V(0, 0, 1.0); f.rock("Meteor", c0, 1.1, sw=P, seed=62)
    rng = np.random.default_rng(63)
    for k in range(6):
        d = V(*rng.normal(size=3)).normalized()
        if d.z < -0.2: d.z = -d.z
        f.gem(f"Crystal{k}", c0 + d * 1.15, basis(d), (0.45, 0.13, 0.13), G, glow=True)
def constellation_stone(f):
    f.box("Stone", V(0, 0, 1.6), (0.7, 1.3, 3.2), Matrix.Rotation(0.06, 3, "Y"), bevel=0.15)
    pts = [V(0.38, -0.35, 2.7), V(0.38, 0.2, 2.4), V(0.38, -0.1, 1.9), V(0.38, 0.4, 1.4), V(0.38, -0.3, 0.9)]
    for k, p in enumerate(pts): f.sphere(f"Star{k}", p, basis(V(1, 0, 0)), (0.03, 0.09, 0.09), G, 10, 6, glow=True)
    for k in range(4): f.tube(f"Line{k}", [pts[k], pts[k + 1]], 0.015, 0.015, glow=True, sw=G, K=4, sub=1)
def nebula_portal(f):
    c0 = V(0, 0, 2.0)
    f.project(f.torus("Ring", c0, V(1, 0, 0), 1.7, 0.3, P, 40, 10))
    f.sphere("Swirl", c0, basis(V(1, 0, 0)), (0.05, 1.45, 1.45), G, 32, 8, glow=True)
    for k in range(6):
        a = 2 * math.pi * k / 6; f.gem(f"Rune{k}", c0 + V(0, 2.3 * math.cos(a), 2.3 * math.sin(a)), basis(V(1, 0, 0)), (0.08, 0.15, 0.25), G, glow=True)
    for sy in (-1, 1): f.box(f"Base{sy}", V(0, sy * 1.2, 0.25), (0.8, 0.8, 0.5), bevel=0.06)

# ======================================================================== zone table
def pal(m, a, d, g, w, p, x): return {M: m, A: a, D: d, G: g, W: w, P: p, X: x, E: c(20, 20, 24)}
FG = lambda a, b: [(0, a), (1, b)]
ZONES = [
 ("01_Pond", [("LilyPads", lily_pads, ("vinyl", c(70, 150, 60), c(110, 190, 80)), pal(c(110, 80, 50), c(250, 210, 60), c(40, 70, 30), c(255, 255, 255), c(250, 250, 240), c(80, 170, 70), c(250, 150, 190)), None),
             ("Cattails", cattails, ("vinyl", c(80, 140, 60), c(120, 180, 70)), pal(c(110, 80, 50), c(150, 110, 60), c(120, 70, 36), c(255, 255, 255), c(250, 250, 240), c(70, 140, 50), c(150, 200, 90)), None),
             ("WoodenDock", wooden_dock, ("wood", c(130, 90, 55), c(175, 130, 85)), pal(c(120, 120, 126), c(200, 180, 130), c(60, 40, 25), c(255, 255, 255), c(250, 250, 240), c(150, 110, 70), c(150, 110, 70)), None),
             ("MossyLog", mossy_log, ("wood", c(110, 75, 45), c(150, 105, 65)), pal(c(110, 80, 50), c(220, 70, 50), c(50, 35, 20), c(255, 255, 255), c(250, 245, 230), c(90, 160, 60), c(200, 160, 110)), None),
             ("Toadstools", toadstools, ("vinyl", c(220, 50, 40), c(240, 90, 60)), pal(c(110, 80, 50), c(250, 210, 60), c(40, 30, 20), c(255, 255, 255), c(250, 245, 230), c(220, 45, 40), c(200, 160, 110)), None),
             ("RowBoat", row_boat, ("wood", c(150, 95, 55), c(200, 140, 90)), pal(c(130, 90, 55), c(190, 140, 85), c(90, 60, 35), c(255, 255, 255), c(250, 245, 230), c(170, 110, 65), c(200, 160, 110)), None)]),
 ("02_River", [("RiverStones", river_stones, ("stone", c(150, 148, 142), c(122, 132, 104)), pal(c(140, 140, 140), c(200, 200, 200), c(80, 80, 80), c(255, 255, 255), c(250, 250, 250), c(150, 150, 150), c(180, 180, 180)), None),
              ("Driftwood", driftwood, ("wood", c(190, 180, 160), c(220, 210, 190)), pal(c(200, 190, 170), c(230, 220, 200), c(120, 110, 100), c(255, 255, 255), c(250, 250, 240), c(200, 190, 170), c(230, 220, 200)), None),
              ("BeaverDam", beaver_dam, ("wood", c(110, 75, 45), c(140, 100, 60)), pal(c(110, 80, 50), c(150, 110, 70), c(80, 60, 40), c(255, 255, 255), c(250, 250, 240), c(110, 80, 50), c(150, 110, 70)), None),
              ("RopeBridge", rope_bridge, ("wood", c(140, 100, 60), c(180, 135, 85)), pal(c(110, 80, 50), c(210, 180, 120), c(60, 40, 25), c(255, 255, 255), c(250, 250, 240), c(150, 110, 70), c(150, 110, 70)), None),
              ("WaterWheel", water_wheel, ("wood", c(130, 90, 55), c(170, 125, 80)), pal(c(80, 80, 88), c(200, 180, 130), c(60, 40, 25), c(255, 255, 255), c(250, 250, 240), c(150, 110, 70), c(110, 80, 50)), None),
              ("Signpost", signpost, ("wood", c(120, 85, 50), c(160, 115, 70)), pal(c(110, 80, 50), c(230, 200, 140), c(70, 50, 30), c(255, 255, 255), c(250, 250, 240), c(150, 110, 70), c(150, 110, 70)), None)]),
 ("03_Swamp", [("MangroveRoots", mangrove_roots, ("vinyl", c(60, 90, 40), c(90, 120, 50)), pal(c(80, 70, 50), c(120, 100, 70), c(40, 35, 25), c(255, 255, 255), c(240, 240, 230), c(70, 110, 45), c(100, 90, 60)), None),
              ("StiltHut", stilt_hut, ("wood", c(100, 80, 55), c(130, 105, 70)), pal(c(80, 70, 50), c(90, 110, 60), c(30, 25, 20), c(220, 255, 120), c(240, 240, 230), c(110, 90, 60), c(100, 90, 60)), c(220, 255, 120)),
              ("WispLantern", wisp_lantern, ("wood", c(60, 55, 45), c(90, 80, 60)), pal(c(70, 60, 45), c(120, 100, 70), c(30, 30, 28), c(160, 255, 140), c(240, 240, 230), c(80, 90, 60), c(100, 90, 60)), c(160, 255, 140)),
              ("GatorSkull", gator_skull, ("stone", c(220, 210, 180), c(150, 160, 110)), pal(c(200, 190, 160), c(220, 210, 180), c(40, 35, 30), c(255, 255, 255), c(245, 240, 225), c(220, 210, 180), c(200, 190, 160)), None),
              ("GlowShrooms", glow_shrooms, ("stone", c(60, 55, 40), c(70, 90, 40)), pal(c(80, 70, 50), c(120, 100, 70), c(50, 45, 35), c(200, 255, 90), c(230, 235, 220), c(90, 100, 60), c(100, 90, 60)), c(200, 255, 90)),
              ("DeadTree", dead_tree, ("wood", c(70, 70, 66), c(100, 98, 92)), pal(c(80, 78, 72), c(110, 108, 100), c(40, 40, 38), c(255, 255, 255), c(240, 240, 230), c(100, 130, 60), c(100, 90, 60)), None)]),
 ("04_CoralReef", [("BrainCoral", brain_coral, ("void", c(240, 120, 150), c(255, 190, 200)), pal(c(240, 130, 150), c(255, 200, 210), c(120, 100, 90), c(255, 255, 255), c(250, 245, 240), c(240, 130, 150), c(255, 200, 210)), None),
                   ("StaghornCoral", staghorn, ("vinyl", c(250, 140, 60), c(255, 200, 120)), pal(c(250, 140, 60), c(255, 140, 60), c(120, 80, 60), c(255, 255, 255), c(250, 245, 240), c(250, 140, 60), c(255, 200, 120)), None),
                   ("SeaFan", sea_fan, ("vinyl", c(150, 60, 190), c(200, 120, 230)), pal(c(150, 60, 190), c(170, 70, 210), c(80, 60, 70), c(255, 255, 255), c(250, 245, 240), c(150, 60, 190), c(200, 120, 230)), None),
                   ("Anemone", anemone, ("vinyl", c(120, 220, 160), c(200, 255, 210)), pal(c(120, 220, 160), c(120, 230, 170), c(80, 70, 70), c(255, 255, 255), c(250, 245, 240), c(230, 90, 140), c(255, 220, 110)), None),
                   ("GiantClam", giant_clam, ("vinyl", c(210, 200, 190), c(240, 235, 225)), pal(c(200, 190, 180), c(180, 165, 150), c(60, 50, 60), c(255, 255, 255), c(250, 248, 245), c(220, 210, 200), c(90, 60, 200)), None),
                   ("TubeSponge", tube_sponge, ("stone", c(250, 210, 60), c(240, 170, 50)), pal(c(250, 210, 60), c(255, 230, 120), c(90, 60, 30), c(255, 255, 255), c(250, 245, 240), c(250, 210, 60), c(255, 230, 120)), None)]),
 ("05_OpenOcean", [("Buoy", buoy, ("hazard", c(220, 40, 40), c(240, 240, 240)), pal(c(90, 96, 104), c(240, 240, 240), c(30, 30, 34), c(255, 240, 150), c(245, 245, 245), c(220, 40, 40), c(240, 240, 240)), c(255, 240, 150)),
                   ("FloatingCrates", floating_crates, ("wood", c(150, 110, 65), c(190, 150, 100)), pal(c(90, 90, 96), c(140, 100, 60), c(70, 50, 30), c(255, 255, 255), c(245, 245, 245), c(150, 110, 65), c(150, 110, 65)), None),
                   ("KelpStalks", kelp_stalks, ("vinyl", c(110, 120, 40), c(150, 150, 60)), pal(c(100, 110, 40), c(180, 160, 60), c(40, 40, 20), c(255, 255, 255), c(245, 245, 245), c(110, 120, 40), c(150, 150, 60)), None),
                   ("LifeRing", life_ring, ("vinyl", c(230, 60, 40), c(250, 90, 60)), pal(c(120, 120, 126), c(220, 200, 150), c(30, 30, 34), c(255, 255, 255), c(250, 250, 250), c(230, 60, 40), c(240, 240, 240)), None),
                   ("MessageBottle", message_bottle, ("stone", c(230, 210, 160), c(210, 190, 140)), pal(c(120, 120, 126), c(170, 120, 70), c(220, 200, 150), c(255, 255, 255), c(250, 245, 230), c(90, 170, 120), c(220, 50, 50)), None),
                   ("NetFloats", net_floats, ("vinyl", c(240, 140, 40), c(255, 180, 80)), pal(c(140, 110, 70), c(70, 90, 80), c(30, 30, 34), c(255, 255, 255), c(245, 245, 245), c(250, 140, 40), c(150, 110, 65)), None)]),
 ("06_FrozenSea", [("Iceberg", iceberg, ("ice", c(170, 220, 245), c(240, 250, 255)), pal(c(200, 230, 245), c(150, 210, 240), c(60, 90, 120), c(255, 255, 255), c(245, 250, 255), c(190, 230, 250), c(150, 210, 240)), None),
                   ("IceCrystals", ice_crystals, ("ice", c(150, 210, 245), c(230, 245, 255)), pal(c(200, 230, 245), c(150, 210, 240), c(60, 90, 120), c(120, 230, 255), c(245, 250, 255), c(170, 220, 250), c(150, 210, 240)), c(120, 230, 255)),
                   ("Igloo", igloo, ("carbon", c(225, 240, 250), c(0, 0, 0)), pal(c(200, 230, 245), c(150, 210, 240), c(40, 60, 80), c(255, 255, 255), c(245, 250, 255), c(230, 242, 252), c(150, 210, 240)), None),
                   ("IceFishingHut", ice_fishing_hut, ("wood", c(190, 50, 40), c(220, 80, 60)), pal(c(90, 90, 96), c(120, 90, 60), c(40, 40, 46), c(255, 255, 255), c(245, 250, 255), c(190, 50, 40), c(150, 110, 70)), None),
                   ("Snowman", snowman, ("vinyl", c(240, 245, 250), c(250, 252, 255)), pal(c(90, 90, 96), c(240, 130, 40), c(30, 30, 34), c(255, 255, 255), c(245, 250, 255), c(210, 40, 50), c(110, 80, 50)), None),
                   ("IcicleArch", icicle_arch, ("ice", c(170, 220, 245), c(240, 250, 255)), pal(c(200, 230, 245), c(150, 210, 240), c(60, 90, 120), c(255, 255, 255), c(245, 250, 255), c(180, 225, 248), c(220, 240, 255)), None)]),
 ("07_DeepAbyss", [("WhaleRibcage", whale_ribcage, ("stone", c(210, 205, 190), c(120, 140, 130)), pal(c(200, 195, 180), c(210, 205, 190), c(30, 30, 40), c(255, 255, 255), c(240, 238, 230), c(215, 210, 195), c(200, 195, 180)), None),
                   ("TubeWorms", tube_worms, ("stone", c(50, 50, 60), c(70, 60, 80)), pal(c(80, 80, 90), c(200, 60, 80), c(40, 40, 50), c(255, 70, 110), c(240, 236, 230), c(80, 80, 90), c(200, 60, 80)), c(255, 70, 110)),
                   ("SubmarineWreck", submarine_wreck, ("rust", c(80, 90, 96), c(150, 80, 40)), pal(c(90, 96, 104), c(150, 80, 40), c(30, 30, 36), c(120, 230, 255), c(240, 240, 240), c(90, 100, 106), c(150, 80, 40)), c(120, 230, 255)),
                   ("GlowPolyps", glow_polyps, ("stone", c(40, 40, 60), c(60, 50, 80)), pal(c(60, 60, 80), c(120, 80, 200), c(30, 30, 40), c(190, 120, 255), c(240, 240, 240), c(70, 60, 100), c(120, 80, 200)), c(190, 120, 255)),
                   ("EyeRock", eye_rock, ("stone", c(40, 42, 56), c(60, 50, 80)), pal(c(60, 60, 80), c(120, 80, 200), c(10, 10, 16), c(255, 230, 80), c(240, 240, 240), c(50, 52, 66), c(120, 80, 200)), c(255, 230, 80)),
                   ("TrenchSpire", trench_spire, ("stone", c(36, 40, 56), c(50, 60, 90)), pal(c(60, 60, 80), c(80, 120, 200), c(20, 20, 30), c(90, 220, 255), c(240, 240, 240), c(44, 48, 64), c(80, 120, 200)), c(90, 220, 255))]),
 ("08_VolcanicVent", [("BlackSmoker", black_smoker, ("obsidian", c(40, 34, 32), c(255, 110, 30)), pal(c(60, 50, 46), c(255, 110, 30), c(50, 46, 46), c(255, 120, 30), c(240, 240, 240), c(44, 38, 36), c(255, 110, 30)), c(255, 120, 30)),
                      ("BasaltColumns", basalt_columns, ("stone", c(56, 56, 60), c(80, 70, 66)), pal(c(60, 60, 64), c(90, 80, 76), c(30, 30, 32), c(255, 255, 255), c(240, 240, 240), c(60, 60, 64), c(90, 80, 76)), None),
                      ("ObsidianShards", obsidian_shards, ("obsidian", c(24, 20, 30), c(120, 60, 160)), pal(c(40, 36, 46), c(120, 60, 160), c(30, 26, 30), c(255, 255, 255), c(240, 240, 240), c(26, 22, 34), c(120, 60, 160)), None),
                      ("MagmaPool", magma_pool, ("obsidian", c(40, 34, 32), c(255, 110, 30)), pal(c(60, 50, 46), c(255, 110, 30), c(30, 26, 26), c(255, 110, 20), c(240, 240, 240), c(46, 40, 38), c(255, 110, 30)), c(255, 110, 20)),
                      ("SulfurCrystals", sulfur_crystals, ("stone", c(70, 60, 54), c(110, 100, 60)), pal(c(80, 70, 60), c(250, 220, 40), c(40, 36, 32), c(255, 255, 255), c(240, 240, 240), c(70, 60, 54), c(250, 225, 50)), None),
                      ("VolcanicBomb", volcanic_bomb, ("obsidian", c(36, 30, 30), c(200, 70, 20)), pal(c(60, 50, 46), c(255, 110, 30), c(40, 34, 32), c(255, 100, 20), c(240, 240, 240), c(40, 34, 32), c(255, 110, 30)), c(255, 100, 20))]),
 ("09_SunkenRuins", [("BrokenPillar", broken_pillar, ("marble", c(225, 220, 205), c(140, 170, 150)), pal(c(200, 195, 180), c(220, 200, 140), c(60, 70, 70), c(255, 255, 255), c(245, 242, 235), c(225, 220, 205), c(90, 150, 110)), None),
                     ("StatueHead", statue_head, ("marble", c(176, 172, 160), c(120, 116, 106)), pal(c(170, 165, 150), c(220, 190, 90), c(40, 40, 40), c(255, 255, 255), c(240, 238, 230), c(175, 170, 155), c(90, 140, 100)), None),
                     ("TreasureChest", treasure_chest, ("wood", c(120, 80, 45), c(160, 115, 70)), pal(c(120, 120, 126), c(240, 190, 60), c(40, 30, 20), c(255, 210, 90), c(245, 240, 230), c(130, 90, 50), c(240, 190, 60)), c(255, 210, 90)),
                     ("Archway", archway, ("marble", c(210, 205, 190), c(140, 170, 150)), pal(c(200, 195, 180), c(220, 200, 140), c(60, 70, 70), c(255, 255, 255), c(245, 242, 235), c(210, 205, 190), c(80, 140, 90)), None),
                     ("Amphorae", amphorae, ("vinyl", c(190, 100, 60), c(220, 140, 90)), pal(c(190, 100, 60), c(160, 80, 50), c(60, 40, 30), c(255, 255, 255), c(245, 240, 230), c(200, 110, 65), c(220, 150, 100)), None),
                     ("TridentAltar", trident_altar, ("marble", c(220, 215, 200), c(80, 180, 170)), pal(c(200, 195, 180), c(240, 190, 60), c(60, 70, 70), c(90, 240, 220), c(245, 242, 235), c(220, 215, 200), c(80, 180, 170)), c(90, 240, 220))]),
 ("10_StarfallLake", [("FallenStar", fallen_star, ("galaxy", c(30, 20, 80), c(150, 60, 200)), pal(c(70, 60, 110), c(200, 160, 255), c(40, 30, 70), c(255, 236, 140), c(250, 248, 255), c(60, 40, 120), c(200, 160, 255)), c(255, 236, 140)),
                      ("StarCrystalTree", star_crystal_tree, ("galaxy", c(30, 20, 80), c(120, 60, 200)), pal(c(60, 40, 110), c(160, 100, 230), c(30, 20, 60), c(120, 220, 255), c(250, 248, 255), c(50, 30, 100), c(200, 160, 255)), c(120, 220, 255)),
                      ("Telescope", telescope, ("gold", c(200, 150, 60), c(240, 200, 110)), pal(c(200, 150, 60), c(230, 180, 80), c(40, 30, 60), c(170, 220, 255), c(250, 248, 255), c(60, 40, 120), c(200, 160, 255)), c(170, 220, 255)),
                      ("MeteorChunk", meteor_chunk, ("galaxy", c(40, 30, 70), c(120, 70, 180)), pal(c(70, 60, 110), c(200, 160, 255), c(30, 20, 50), c(220, 140, 255), c(250, 248, 255), c(50, 40, 90), c(200, 160, 255)), c(220, 140, 255)),
                      ("ConstellationStone", constellation_stone, ("stone", c(50, 46, 80), c(70, 60, 110)), pal(c(70, 60, 110), c(200, 160, 255), c(30, 20, 50), c(255, 240, 190), c(250, 248, 255), c(56, 50, 90), c(200, 160, 255)), c(255, 240, 190)),
                      ("NebulaPortal", nebula_portal, ("stone", c(70, 64, 100), c(110, 90, 150)), pal(c(80, 70, 120), c(200, 160, 255), c(30, 20, 50), c(200, 120, 255), c(250, 248, 255), c(80, 70, 120), c(200, 160, 255)), c(200, 120, 255))]),
]

def build_prop(folder, name, fn, pattern, palette, glow):
    f = Prop(name, "Zones/" + folder)
    fn(f)
    co = np.concatenate([np.array([v.co[:] for v in o.data.vertices]) for o in f.parts + f.glow])
    size = float((co.max(0) - co.min(0)).max())
    a, b = pattern[1], pattern[2]
    f.texture(pat(*pattern), fin_stops=[FG(palette[P], palette[X])],
              strips=[(palette[M] * 0.7, palette[M] * 1.15, 1.0), (palette[A] * 0.6, palette[A] * 1.2, 1.0)], swatches=palette)
    hz = float(co[:, 2].max() - co[:, 2].min())
    f.finish(bend=0.0, rig=False, glow_color=glow, cam_scale=max(0.45, size / 5.8, hz / 3.6),
             views={"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50)})

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for folder, props in ZONES:
        for (name, fn, pattern, palette, glow) in props:
            if want and folder not in want and name not in want: continue
            build_prop(folder, name, fn, pattern, palette, glow)
