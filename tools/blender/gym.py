"""Dumbbell-curl gear: 15 tiers, each a Dumbbell + preacher curl Bench, each tier cooler than the last.
Run: python gym.py [tier numbers ...] [--no-render]   ->  models/Gym/<NN>_<Theme>/<Theme>Dumbbell|<Theme>Bench
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix
from fishkit import Fish, V, lerp, smooth, c, basis, vnoise, scales

SW = dict(metal=0, accent=1, dark=2, glow=3, white=4, pad=5, eye=6, x=7)

class Prop(Fish):
    def __init__(self, name, folder):
        super().__init__(name, folder, L=3.0, R=0.5, H=1.0, PT=[0, 1], PR=[1, 1], fin_styles=1)
    def project(self, ob):
        """Box-project an object's UVs onto the painted pattern (body region of the atlas)."""
        me = ob.data; co = np.array([v.co[:] for v in me.vertices]); lo, hi = co.min(0), co.max(0); rg = np.maximum(hi - lo, 1e-4)
        uv = me.uv_layers[0].data
        for p in me.polygons:
            ax = int(np.argmax(np.abs(p.normal[:]))); a, b = [i for i in range(3) if i != ax]
            for li in p.loop_indices:
                q = (co[me.loops[li].vertex_index] - lo) / rg
                uv[li].uv = self.uv_body(float(q[a]) * 0.98 + 0.01, float(q[b]) * 0.98 + 0.01)
        return ob
    def box(self, name, center, size, rot=None, sw=0, bevel=0.05, glow=False, proj=True):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=size, verts=bm.verts)
        if bevel: bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(bevel, min(size) * 0.45), segments=2, affect="EDGES")
        M = Matrix.Translation(center) @ (rot.to_4x4() if rot else Matrix.Identity(4))
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        verts = [v.co.copy() for v in bm.verts]; faces = [tuple(v.index for v in fc.verts) for fc in bm.faces]; bm.free()
        ob = self.make_obj(name, verts, faces, [[self.uv_sw(sw)] * len(fc) for fc in faces], glow)
        return self.project(ob) if proj and not glow else ob
    def cyl(self, name, a, b, r, K=24, sw=0, glow=False, proj=True):
        ob = self.tube(name, [a, (a + b) / 2, b], r, r, K=K, sub=2, sw=sw, glow=glow)
        return self.project(ob) if proj and not glow else ob
    def rock(self, name, center, r, sw=0, seed=1, proj=True):
        ob = self.sphere(name, center, Matrix.Identity(3), (r, r, r), sw, 20, 14)
        for v in ob.data.vertices:
            d = v.co - center; k = 1 + 0.13 * math.sin(9 * d.x + seed) * math.cos(8 * d.y + 2 * seed) * math.sin(7 * d.z + seed)
            v.co = center + d * k
        return self.project(ob) if proj else ob
    def cracks(self, name, center, r, n, seed, rad=0.025):
        rng = np.random.default_rng(seed)
        for k in range(n):
            d = Vector(rng.normal(size=3)).normalized(); pts = []
            for i in range(5):
                pts.append(center + d * r * 1.02); d = (d + Vector(rng.normal(size=3)) * 0.35).normalized()
            self.tube(f"{name}{k}", pts, rad, rad * 0.5, K=5, sub=3, glow=True, sw=SW["glow"])

# ---------------------------------------------------------------- painted patterns (T, V in 0..1)
def pat(kind, a, b):
    def f(T, Vv, top):
        X, Y = T * 4, Vv * 4; n = vnoise(X, Y, 2.5, 7); n2 = vnoise(X, Y, 7, 8)
        if kind == "rust":
            m = smooth(0.55, 0.62, n * 0.7 + n2 * 0.3); col = a * (0.85 + 0.25 * n2)[..., None]
            return col * (1 - m[..., None]) + b * (0.8 + 0.4 * n)[..., None] * m[..., None]
        if kind == "rubber": return a * (0.9 + 0.2 * n2)[..., None]
        if kind == "chrome":
            band = 0.5 + 0.5 * np.sin(Vv * 18 + 2 * np.sin(T * 6)); return a + (b - a) * band[..., None]
        if kind == "vinyl": return a + (b - a) * smooth(0.2, 0.9, Vv)[..., None]
        if kind == "gold":
            ring = np.abs(np.sin(np.hypot(T - 0.5, Vv - 0.5) * 40 + 3 * n)); return a + (b - a) * smooth(0.85, 0.98, ring)[..., None]
        if kind == "ice":
            f_ = np.abs(np.sin(X * 3 + Y * 5 + 4 * n)); return a + (b - a) * smooth(0.6, 1.0, f_)[..., None]
        if kind == "obsidian":
            cr = smooth(0.06, 0.0, np.abs(n - 0.5)); return a * (0.8 + 0.4 * n2)[..., None] * (1 - cr[..., None]) + b * cr[..., None]
        if kind == "stone":
            moss = smooth(0.58, 0.66, n); return a * (0.8 + 0.4 * n2)[..., None] * (1 - moss[..., None]) + b * moss[..., None]
        if kind == "carbon":
            w = ((np.floor(X * 12) + np.floor(Y * 12)) % 2)[..., None]; return a * (0.85 + 0.3 * w) + b * 0.0
        if kind == "hazard":
            s = (np.floor((X + Y) * 3) % 2)[..., None]; return a * s + b * (1 - s)
        if kind == "scales":
            e, inner = scales(X * 1.2, Y * 1.2, 0.18); col = a + (b - a) * (1 - inner)[..., None] * 0.6
            return col * (1 - 0.6 * e[..., None]) + b * 0.6 * e[..., None]
        if kind == "galaxy":
            neb = a * (1 - n[..., None]) + b * n[..., None]; st = smooth(0.9, 0.93, vnoise(X, Y, 25, 9))
            return neb * (1 - st[..., None]) + c(255, 250, 230) * st[..., None]
        if kind == "marble":
            v = smooth(0.04, 0.0, np.abs(np.sin(X * 2 + 5 * n) * 0.5)); return a * (1 - v[..., None]) + b * v[..., None]
        if kind == "void":
            sw = 0.5 + 0.5 * np.sin(np.arctan2(Vv - 0.5, T - 0.5) * 3 + np.hypot(T - 0.5, Vv - 0.5) * 30 + 4 * n)
            return a + (b - a) * smooth(0.7, 1.0, sw)[..., None]
        if kind == "wood":
            g = 0.5 + 0.5 * np.sin(Y * 30 + 6 * n); return a + (b - a) * g[..., None] * 0.5
        if kind == "ocean":
            e, inner = scales(X * 1.4, Y * 1.4, 0.16); return (a + (b - a) * n[..., None]) * (1 - 0.35 * e[..., None])
        raise KeyError(kind)
    return f

# ---------------------------------------------------------------- dumbbell heads (sd = +1/-1 side, x0 = start)
def head_plates(f, sd, x0, t):
    x = x0
    for i, (r, w) in enumerate(t.get("plates", [(0.42, 0.14), (0.36, 0.12), (0.3, 0.1)])):
        f.cyl(f"Plate{sd}{i}", V(x, 0, 0), V(x + sd * w, 0, 0), r); f.torus(f"Rim{sd}{i}", V(x + sd * w / 2, 0, 0), V(1, 0, 0), r, 0.025, SW["accent"], 28, 6)
        x += sd * (w + 0.015)
    f.cyl(f"Bolt{sd}", V(x, 0, 0), V(x + sd * 0.06, 0, 0), 0.12, 16, SW["metal"], proj=False)
def head_hex(f, sd, x0, t, glow=False):
    f.cyl(f"Hex{sd}", V(x0, 0, 0), V(x0 + sd * 0.42, 0, 0), 0.4, 6)
    f.torus(f"HexRing{sd}", V(x0 + sd * 0.21, 0, 0), V(1, 0, 0), 0.43 if glow else 0.36, 0.035, SW["glow"] if glow else SW["accent"], 6, 6, glow=glow)
    if glow:
        for k, xx in enumerate((0.06, 0.36)):
            f.torus(f"HexRing2{sd}{k}", V(x0 + sd * xx, 0, 0), V(1, 0, 0), 0.43, 0.03, SW["glow"], 6, 6, glow=True)
        f.cyl(f"Core{sd}", V(x0 + sd * 0.42, 0, 0), V(x0 + sd * 0.47, 0, 0), 0.24, 6, SW["glow"], glow=True)
        for k in range(6):
            a = 2 * math.pi * k / 6 + math.pi / 6; o = V(0, 0.47 * math.cos(a), 0.47 * math.sin(a))
            f.box(f"Fin{sd}{k}", V(x0 + sd * 0.21, 0, 0) + o, (0.3, 0.05, 0.05), Matrix.Rotation(a, 3, "X"), sw=SW["accent"], bevel=0.01, proj=False)
def head_sphere(f, sd, x0, t):
    f.sphere(f"Ball{sd}", V(x0 + sd * 0.34, 0, 0), Matrix.Identity(3), (0.38,) * 3, SW["pad"], 24, 16)
    f.torus(f"Band{sd}", V(x0 + sd * 0.34, 0, 0), V(1, 0, 0), 0.37, 0.05, SW["accent"], 28, 8)
def head_crystal(f, sd, x0, t):
    cx = V(x0 + sd * 0.36, 0, 0)
    f.gem(f"CoreGem{sd}", cx, basis(V(sd, 0, 0)), (0.36, 0.26, 0.26), SW["glow"], glow=True)
    for k in range(6):
        a = 2 * math.pi * k / 6; d = Vector((sd * 0.35, math.cos(a), math.sin(a))).normalized()
        f.gem(f"Shard{sd}{k}", cx + d * 0.22, basis(d), (0.26, 0.09, 0.09), SW["pad"])
    f.torus(f"Cage{sd}", cx - V(sd * 0.2, 0, 0), V(1, 0, 0), 0.24, 0.035, SW["accent"], 6, 6)
def head_lava(f, sd, x0, t):
    cx = V(x0 + sd * 0.38, 0, 0); f.rock(f"Rock{sd}", cx, 0.4, seed=3 + sd); f.cracks(f"Crack{sd}_", cx, 0.4, 9, 10 + sd)
def head_tiki(f, sd, x0, t):
    cx = V(x0 + sd * 0.3, 0, 0)
    f.box(f"Tiki{sd}", cx, (0.5, 0.62, 0.78), bevel=0.08)
    fx = cx + V(sd * 0.26, 0, 0)
    for yy in (-0.14, 0.14):
        f.sphere(f"TEye{sd}{yy}", fx + V(0, yy, 0.12), Matrix.Identity(3), (0.05, 0.09, 0.07), SW["dark"], 10, 6)
    f.box(f"TMouth{sd}", fx + V(0, 0, -0.16), (0.06, 0.34, 0.1), sw=SW["dark"], bevel=0.02, proj=False)
    f.box(f"TBrow{sd}", fx + V(0, 0, 0.26), (0.08, 0.5, 0.08), sw=SW["accent"], bevel=0.02, proj=False)
    for k in range(4):
        a = k * 1.6 + sd
        f.sphere(f"Moss{sd}{k}", cx + V(0.1 * math.sin(a), 0.3 * math.cos(a), 0.36), Matrix.Identity(3), (0.1, 0.1, 0.06), SW["pad"], 10, 6)
def head_canister(f, sd, x0, t):
    a, b = V(x0, 0, 0), V(x0 + sd * 0.55, 0, 0)
    f.cyl(f"CapA{sd}", a, a + V(sd * 0.08, 0, 0), 0.36, 24, SW["dark"], proj=False)
    f.cyl(f"CapB{sd}", b - V(sd * 0.08, 0, 0), b, 0.36, 24, SW["dark"], proj=False)
    f.cyl(f"Goo{sd}", a + V(sd * 0.08, 0, 0), b - V(sd * 0.08, 0, 0), 0.27, 20, SW["glow"], glow=True)
    for k in range(4):
        q = math.pi / 4 + k * math.pi / 2; o = V(0, 0.31 * math.cos(q), 0.31 * math.sin(q))
        f.cyl(f"Rod{sd}{k}", a + o, b + o, 0.035, 8, SW["metal"], proj=False)
    f.cyl(f"Haz{sd}", a + V(sd * 0.25, 0, 0), a + V(sd * 0.32, 0, 0), 0.3, 24)
def head_kraken(f, sd, x0, t):
    cx = V(x0 + sd * 0.36, 0, 0)
    f.sphere(f"KBody{sd}", cx, Matrix.Identity(3), (0.38, 0.36, 0.36), SW["pad"], 22, 14)
    for yy in (-0.14, 0.14):
        f.sphere(f"KEye{sd}{yy}", cx + V(sd * 0.3, yy, 0.12), basis(V(sd, 0, 0)), (0.06, 0.07, 0.07), SW["glow"], 10, 6, glow=True)
    for k in range(6):
        a = 2 * math.pi * k / 6; d = V(0, math.cos(a), math.sin(a)); p = cx + d * 0.3 + V(sd * 0.05, 0, 0)
        f.tube(f"Tent{sd}{k}", [p, p + d * 0.2 + V(sd * 0.15, 0, 0), p + d * 0.32 + V(sd * 0.32, 0, 0) + d.cross(V(1, 0, 0)) * 0.1,
                                p + d * 0.26 + V(sd * 0.42, 0, 0) + d.cross(V(1, 0, 0)) * 0.22], 0.07, 0.01, strip=1, K=8, sub=5)
def head_dragon(f, sd, x0, t):
    X = V(sd, 0, 0); Bm = basis(X); cx = V(x0 + sd * 0.3, 0, 0)
    f.sphere(f"Skull{sd}", cx, Bm, (0.36, 0.3, 0.3), SW["pad"], 20, 12)
    f.tube(f"Snout{sd}", [cx, cx + X * 0.3 + V(0, 0, -0.04), cx + X * 0.52 + V(0, 0, -0.08)], 0.22, 0.1, sw=SW["pad"], K=12)
    for yy in (-1, 1):
        f.sphere(f"DEye{sd}{yy}", cx + X * 0.22 + V(0, yy * 0.18, 0.1), basis(V(sd * 0.4, yy, 0.3)), (0.05, 0.05, 0.05), SW["glow"], 10, 6, glow=True)
        f.tube(f"DHorn{sd}{yy}", [cx + V(0, yy * 0.15, 0.18), cx + V(-sd * 0.15, yy * 0.25, 0.42), cx + V(-sd * 0.42, yy * 0.3, 0.55)], 0.08, 0.008, strip=1, K=8)
        for k in range(3):
            p = cx + X * (0.18 + 0.12 * k) + V(0, yy * 0.11, -0.12)
            f.tube(f"Fang{sd}{yy}{k}", [p, p + V(0, 0, -0.07), p + V(sd * 0.01, 0, -0.12)], 0.03, 0.003, K=5, sub=2, sw=SW["white"])
def head_planet(f, sd, x0, t):
    cx = V(x0 + sd * 0.38, 0, 0)
    f.project(f.sphere(f"Planet{sd}", cx, Matrix.Identity(3), (0.38,) * 3, SW["pad"], 24, 16))
    f.torus(f"PRing{sd}", cx, V(sd * 0.5, 0.3, 1), 0.56, 0.035, SW["glow"], 40, 6, glow=True)
    f.sphere(f"Moon{sd}", cx + V(0, 0.55, 0.3), Matrix.Identity(3), (0.08,) * 3, SW["white"], 10, 8)
def head_angel(f, sd, x0, t):
    cx = V(x0 + sd * 0.36, 0, 0)
    f.project(f.sphere(f"Orb{sd}", cx, Matrix.Identity(3), (0.36,) * 3, SW["pad"], 24, 16))
    f.torus(f"Halo{sd}", cx + V(sd * 0.05, 0, 0), V(1, 0, 0), 0.48, 0.04, SW["glow"], 36, 8, glow=True)
    for yy in (1, -1):
        f.fin(f"Wing{sd}{yy}", lambda s, yy=yy: cx + V(-sd * 0.05, yy * 0.25, lerp(0.15, -0.05, s)),
              lambda s, yy=yy: V(-sd * 0.3, yy * 1.0, lerp(0.9, 0.2, s)), lambda s: 0.5 * (0.84 + 0.16 * abs(math.sin(math.pi * 5 * s)) ** 0.5) * (1 - 0.4 * s),
              lambda s, r: V(0, 0, 0), 14, 6, 0.03, 0)
def head_void(f, sd, x0, t):
    cx = V(x0 + sd * 0.4, 0, 0)
    f.sphere(f"Hole{sd}", cx, Matrix.Identity(3), (0.34,) * 3, SW["dark"], 24, 16)
    f.sphere(f"Disk{sd}", cx, basis(V(sd * 0.3, 0.2, 1)), (0.04, 0.62, 0.62), SW["glow"], 32, 6, glow=True)
    f.torus(f"Event{sd}", cx, V(1, 0, 0), 0.36, 0.03, SW["accent"], 32, 6)
    for k in range(8):
        a = 2 * math.pi * k / 8; d = V(sd * 0.25, math.cos(a), math.sin(a)).normalized()
        f.tube(f"VSpike{sd}{k}", [cx + d * 0.3, cx + d * 0.5, cx + d * 0.72], 0.06, 0.005, strip=1, K=6, sub=2)
HEADS = dict(plates=head_plates, hex=head_hex, hexglow=lambda f, sd, x0, t: head_hex(f, sd, x0, t, True), sphere=head_sphere,
             crystal=head_crystal, lava=head_lava, tiki=head_tiki, canister=head_canister, kraken=head_kraken, dragon=head_dragon,
             planet=head_planet, angel=head_angel, void=head_void)

# ---------------------------------------------------------------- bench frames
def frame_parts(f, t):
    st = t["frame"]; posts = [(V(0, 0, 0.2), V(0, 0, 1.38)), (V(0.95, 0, 0.2), V(0.88, 0, 1.9))]
    if st in ("steel", "gold", "hover", "hazard", "void"):
        for i, (a, b) in enumerate(posts): f.cyl(f"Post{i}", a, b, 0.09, 12, SW["metal"], proj=False)
        if st != "hover":
            f.cyl("Rail", V(-0.6, 0, 0.12), V(1.4, 0, 0.12), 0.08, 12, SW["metal"], proj=False)
            for x in (-0.6, 1.4): f.cyl(f"Foot{x}", V(x, -0.55, 0.08), V(x, 0.55, 0.08), 0.08, 12, SW["metal"], proj=False)
    if st == "bricks":
        for i, x in enumerate((-0.35, 0.35, 0.95)):
            for j in range(3 if x < 0.9 else 5):
                f.box(f"Brick{i}{j}", V(x, 0, 0.16 + j * 0.3), (0.5, 0.9 if x < 0.9 else 0.4, 0.28), bevel=0.04)
    if st in ("ice", "rock"):
        for i, (x, h) in enumerate(((0.0, 1.3), (0.92, 1.85))):
            if st == "ice": f.box(f"Block{i}", V(x, 0, h / 2), (0.6, 0.9, h), bevel=0.06)
            else:
                for j in range(int(h / 0.45) + 1): f.rock(f"Stone{i}{j}", V(x, 0, 0.25 + j * 0.42), 0.32, seed=i * 7 + j)
    if st == "log":
        for i, (a, b) in enumerate(posts): f.cyl(f"Log{i}", a - V(0, 0, 0.2), b, 0.2, 14)
        f.cyl("LogBase", V(-0.7, 0, 0.18), V(1.5, 0, 0.18), 0.2, 14)
        for k in range(5):
            a = k * 1.3; f.tube(f"Vine{k}", [V(0.95 + 0.2 * math.cos(a + z), 0.2 * math.sin(a + z), 0.3 + z * 0.4) for z in (0, 1, 2, 3)], 0.03, 0.02, sw=SW["pad"], K=6)
    if st == "ship":
        for i, (a, b) in enumerate(posts): f.cyl(f"Mast{i}", a - V(0, 0, 0.2), b, 0.13, 16)
        f.box("Deck", V(0.4, 0, 0.1), (2.2, 1.3, 0.2), bevel=0.04)
        for z in (0.5, 0.9): f.torus(f"Rope{z}", V(0, 0, z), V(0, 0, 1), 0.14, 0.03, SW["accent"], 16, 6)
    if st == "claw":
        for i, (a, b) in enumerate(posts): f.cyl(f"Post{i}", a, b, 0.11, 12, SW["metal"], proj=False)
        for x in (-0.5, 1.3):
            for yy in (-0.5, 0.5):
                p = V(x, yy, 0.3)
                f.tube(f"Claw{x}{yy}", [p + V(0, -yy * 0.5, 0.0), p, p + V(0, yy * 0.15, -0.2), p + V(0, yy * 0.05, -0.28)], 0.09, 0.01, strip=1, K=8)
                f.cyl(f"Leg{x}{yy}", p + V(0, -yy * 0.5, 0), V(0.4 if x < 0 else 0.6, 0, 0.3), 0.07, 10, SW["metal"], proj=False)
    if st == "asteroid":
        f.rock("Asteroid", V(0.4, 0, 0.35), 0.75, seed=5)
        for i, (a, b) in enumerate(posts): f.cyl(f"Post{i}", a + V(0, 0, 0.4), b, 0.08, 12, SW["metal"], proj=False)
        for k in range(5): f.sphere(f"Rubble{k}", V(0.4 + 1.1 * math.cos(k * 1.3), 1.1 * math.sin(k * 1.3), 0.3 + 0.2 * math.sin(k)), Matrix.Identity(3), (0.12,) * 3, SW["dark"], 8, 6)
    if st == "cloud":
        for k in range(9):
            a = k * 0.7; f.sphere(f"Cloud{k}", V(0.4 + 0.9 * math.cos(a), 0.6 * math.sin(a), 0.25 + 0.1 * math.sin(3 * a)), Matrix.Identity(3), (0.42, 0.42, 0.32), SW["white"], 16, 10)
        for i, (a, b) in enumerate(posts): f.cyl(f"Pillar{i}", a + V(0, 0, 0.2), b, 0.12, 16)
    if st == "hover":
        for i, x in enumerate((0.0, 0.95)):
            f.cyl(f"Pad{i}", V(x, 0, 0.0), V(x, 0, 0.08), 0.45, 24, SW["dark"], proj=False)
            f.torus(f"HoverRing{i}", V(x, 0, 0.04), V(0, 0, 1), 0.45, 0.04, SW["glow"], 32, 6, glow=True)
            f.cyl(f"Beam{i}", V(x, 0, 0.09), V(x, 0, 0.2), 0.3, 24, SW["glow"], glow=True)
    if st == "hazard":
        f.box("HazBase", V(0.4, 0, 0.15), (2.1, 1.2, 0.25), bevel=0.04)
        for yy in (-0.5, 0.5): f.cyl(f"Tank{yy}", V(1.3, yy, 0.3), V(1.3, yy, 0.9), 0.15, 16, SW["glow"], glow=True)
    if st == "void":
        for k in range(10):
            a = 2 * math.pi * k / 10; p = V(0.4 + 1.2 * math.cos(a), 0.9 * math.sin(a), 0.05)
            f.tube(f"Spike{k}", [p, p + V(0, 0, 0.4), p + V(-0.1 * math.cos(a), -0.1 * math.sin(a), 0.75)], 0.12, 0.006, strip=1, K=6, sub=3)
        f.torus("VoidRing", V(0.4, 0, 0.05), V(0, 0, 1), 1.15, 0.05, SW["glow"], 48, 6, glow=True)
    if st == "gold":
        for i, (a, b) in enumerate(posts): f.torus(f"GoldRing{i}", (a + b) / 2, b - a, 0.13, 0.04, SW["accent"], 16, 6)

def bench(t, folder):
    f = Prop(t["theme"] + "Bench", folder)
    pp = bool(t.get("pad_pat"))
    seat = f.box("Seat", V(0, 0, 1.5), (1.15, 1.2, 0.28), sw=SW["pad"], bevel=0.1, proj=pp)
    rot = Matrix.Rotation(math.radians(-40), 3, "Y")
    f.box("ArmPad", V(0.98, 0, 2.15), (0.3, 1.3, 0.95), rot, sw=SW["pad"], bevel=0.1, proj=pp)
    f.box("SeatBase", V(0, 0, 1.33), (1.0, 1.05, 0.08), sw=SW["metal"], bevel=0.02, proj=False)
    f.box("PadBase", V(0.9, 0, 2.0), (0.08, 1.15, 0.85), rot, sw=SW["metal"], bevel=0.02, proj=False)
    frame_parts(f, t)
    if t.get("bench_extra"): t["bench_extra"](f, t)
    fit_avatar(f)
    finish(f, t, 0.78)

# Resize to a ~5-stud R15 avatar: seat ~1.8 high x 2 wide, arm pad top ~3 high x 2.2 wide, base ~3 long.
# Structural parts stretch; decorations move with the layout but keep their shape (uniform scale).
FIT = Matrix.Diagonal((1.45, 1.65, 1.22, 1.0)); FIT_U = 1.3
STRUCT = ("Seat", "ArmPad", "PadBase", "Post", "Rail", "Foot", "Brick", "Block", "Log", "Deck", "Mast", "Leg", "HazBase",
          "PadTrim", "Pillar", "Pad", "Beam")
def fit_avatar(f):
    for ob in f.parts + f.glow:
        if ob.name.startswith(STRUCT) and not ob.name.startswith("PadSpike"):
            ob.data.transform(FIT); continue
        co = np.array([v.co[:] for v in ob.data.vertices]); cen = Vector(co.mean(0).tolist())
        ob.data.transform(Matrix.Translation(FIT @ cen) @ Matrix.Scale(FIT_U, 4) @ Matrix.Translation(-cen))

def dumbbell(t, folder):
    f = Prop(t["theme"] + "Dumbbell", folder); hl = 0.5
    f.tube("Handle", [V(-hl - 0.1, 0, 0), V(0, 0, 0), V(hl + 0.1, 0, 0)], 0, 0, strip=0, K=12, sub=6,
           rfn=lambda s: 0.085 * (1 + 0.07 * max(0.0, math.sin(s * 140))))
    for sd in (1, -1):
        f.torus(f"Collar{sd}", V(sd * hl, 0, 0), V(1, 0, 0), 0.1, 0.045, SW["metal"], 20, 8)
        HEADS[t["head"]](f, sd, sd * (hl + 0.04), t)
    finish(f, t, 0.48)

def finish(f, t, cam):
    a, b = t["pat"][1], t["pat"][2]
    f.texture(pat(t["pat"][0], a, b), fin_stops=[t.get("fin", [(0, a), (1, b)])],
              strips=[(t["metal"] * 0.7, t["metal"] * 1.15, 1.0), (t["accent"] * 0.6, t["accent"] * 1.2, 1.0)],
              swatches={SW["metal"]: t["metal"], SW["accent"]: t["accent"], SW["dark"]: t.get("dark", c(20, 20, 24)),
                        SW["glow"]: t.get("glow", c(255, 255, 255)), SW["white"]: c(250, 248, 240), SW["pad"]: t["pad"], SW["eye"]: c(20, 20, 20)})
    f.finish(bend=0.0, rig=False, glow_color=t.get("glow"), cam_scale=cam,
             views={"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50), "side": ((12.5, 0, 0.6), (0, 0, 0.2), 50)})

ROT = Matrix.Rotation(math.radians(-40), 3, "Y")
PAD_TOP = V(0.98, 0, 2.15) + ROT @ V(0, 0, 0.5)
def glow_trim(f, t):
    f.box("SeatTrim", V(0, 0, 1.37), (1.22, 1.27, 0.05), sw=SW["glow"], bevel=0.01, glow=True)
    f.box("PadTrim", V(0.98, 0, 2.15) + ROT @ V(-0.16, 0, 0), (0.05, 1.37, 1.0), ROT, sw=SW["glow"], bevel=0.01, glow=True)
def shards(f, t):
    for k, (x, yy) in enumerate(((0.0, 0.4), (0.0, -0.4), (0.92, 0.4), (0.92, -0.4))):
        h = 1.3 if x < 0.5 else 1.85
        f.gem(f"IceShard{k}", V(x + 0.25, yy, h * 0.6), basis(V(0.3, yy, 1)), (0.25, 0.07, 0.07), SW["glow"], glow=True)
def kraken_bench(f, t):
    for i, (x, h) in enumerate(((0.0, 1.35), (0.9, 1.9))):
        pts = [V(x + 0.2 * math.cos(a), 0.2 * math.sin(a), 0.2 + a / 12 * h) for a in np.linspace(0, 11, 12)]
        f.tube(f"Tentacle{i}", pts, 0.08, 0.02, strip=1, K=8, sub=3)
def dragon_bench(f, t):
    for yy in (-1, 1):
        b = PAD_TOP + V(0, yy * 0.45, 0)
        f.tube(f"BHorn{yy}", [b, b + V(0.1, yy * 0.1, 0.35), b + V(0.4, yy * 0.15, 0.6), b + V(0.7, yy * 0.1, 0.62)], 0.1, 0.01, strip=1, K=8)
        f.fin(f"BWing{yy}", lambda s, yy=yy: V(lerp(-0.5, 0.3, s), yy * 0.6, 1.55), lambda s, yy=yy: V(-0.4, yy * 1.0, lerp(0.9, 0.3, s)),
              lambda s: 0.9 * (0.55 + 0.45 * ((s * 4) % 1.0) ** 1.5) * (1 - 0.3 * s), lambda s, r: V(0, 0, 0), 24, 5, 0.03, 0)
def galaxy_bench(f, t):
    f.torus("Orbit", V(0.4, 0, 1.3), V(0.2, 0.3, 1), 1.35, 0.03, SW["glow"], 48, 6, glow=True)
    for k in range(3):
        a = k * 2.1; f.project(f.sphere(f"MiniPlanet{k}", V(0.4 + 1.35 * math.cos(a), 1.35 * math.sin(a), 1.3 - 0.3 * math.sin(a)), Matrix.Identity(3), (0.14,) * 3, SW["pad"], 12, 8))
def angel_bench(f, t):
    f.torus("BHalo", PAD_TOP + V(0.15, 0, 0.45), V(0.3, 0, 1), 0.38, 0.045, SW["glow"], 36, 8, glow=True)
    for yy in (-1, 1):
        f.fin(f"AngelWing{yy}", lambda s, yy=yy: V(lerp(-0.5, 0.4, s), yy * 0.6, lerp(1.6, 1.75, s)), lambda s, yy=yy: V(-0.5, yy * 0.8, lerp(1.0, 0.5, s)),
              lambda s: 1.2 * (0.84 + 0.16 * abs(math.sin(math.pi * 6 * s)) ** 0.5) * (1 - 0.35 * s), lambda s, r: V(0, 0, 0.2 * r * r), 30, 6, 0.03, 0)
def void_bench(f, t):
    glow_trim(f, t)
    for k in range(5):
        b = PAD_TOP + V(0, lerp(-0.55, 0.55, k / 4), 0)
        f.tube(f"PadSpike{k}", [b, b + V(0.1, 0, 0.25), b + V(0.25, 0, 0.45)], 0.07, 0.005, strip=1, K=6, sub=2)
def lava_bench(f, t): glow_trim(f, t)

TIERS = [
 dict(theme="Rusty", head="plates", pat=("rust", c(104, 104, 110), c(150, 76, 36)), frame="bricks", metal=c(90, 90, 96), accent=c(120, 70, 40), pad=c(120, 90, 60)),
 dict(theme="Rubber", head="hex", pat=("rubber", c(36, 36, 40), c(36, 36, 40)), frame="steel", metal=c(70, 72, 78), accent=c(210, 40, 40), pad=c(40, 40, 46)),
 dict(theme="Chrome", head="plates", pat=("chrome", c(150, 156, 168), c(240, 244, 250)), frame="steel", metal=c(200, 205, 214), accent=c(40, 40, 46),
      pad=c(200, 30, 40), plates=[(0.46, 0.12), (0.4, 0.1), (0.34, 0.1), (0.28, 0.08)]),
 dict(theme="NeonSport", head="sphere", pat=("vinyl", c(255, 80, 170), c(255, 150, 210)), frame="steel", metal=c(240, 240, 244), accent=c(40, 220, 210), pad=c(40, 210, 200)),
 dict(theme="Golden", head="plates", pat=("gold", c(226, 170, 50), c(255, 226, 130)), frame="gold", metal=c(236, 186, 60), accent=c(255, 240, 200), pad=c(250, 246, 236),
      plates=[(0.48, 0.14), (0.42, 0.12), (0.34, 0.1)]),
 dict(theme="Crystal", head="crystal", pat=("ice", c(150, 210, 240), c(235, 248, 255)), frame="ice", bench_extra=shards, pad_pat=True, metal=c(200, 230, 245), accent=c(120, 200, 255), pad=c(170, 220, 245), glow=c(120, 230, 255)),
 dict(theme="Lava", head="lava", pat=("obsidian", c(40, 30, 30), c(255, 110, 30)), frame="rock", bench_extra=lava_bench, pad_pat=True, metal=c(50, 40, 38), accent=c(255, 110, 30), pad=c(120, 30, 20), glow=c(255, 120, 30)),
 dict(theme="Tiki", head="tiki", pat=("stone", c(120, 116, 100), c(70, 120, 50)), frame="log", pad_pat=True, metal=c(110, 76, 44), accent=c(200, 160, 60), pad=c(70, 140, 60)),
 dict(theme="Cyber", head="hexglow", pat=("carbon", c(40, 44, 52), c(0, 0, 0)), frame="hover", bench_extra=glow_trim, pad_pat=True, metal=c(60, 64, 74), accent=c(0, 230, 255), pad=c(30, 32, 40), glow=c(0, 230, 255)),
 dict(theme="Toxic", head="canister", pat=("hazard", c(250, 210, 30), c(30, 30, 30)), frame="hazard", bench_extra=glow_trim, metal=c(90, 96, 90), accent=c(250, 210, 30), pad=c(60, 70, 50), glow=c(150, 255, 40)),
 dict(theme="Kraken", head="kraken", pat=("ocean", c(20, 90, 110), c(60, 170, 170)), frame="ship", bench_extra=kraken_bench, pad_pat=True, metal=c(120, 80, 46), accent=c(40, 150, 150), pad=c(20, 60, 100), glow=c(90, 240, 255)),
 dict(theme="Dragon", head="dragon", pat=("scales", c(170, 24, 30), c(240, 180, 60)), frame="claw", bench_extra=dragon_bench, pad_pat=True, metal=c(60, 20, 24), accent=c(236, 180, 60), pad=c(150, 20, 30), glow=c(255, 90, 30)),
 dict(theme="Galaxy", head="planet", pat=("galaxy", c(30, 20, 80), c(150, 60, 200)), frame="asteroid", bench_extra=galaxy_bench, pad_pat=True, metal=c(70, 60, 110), accent=c(200, 160, 255), pad=c(70, 40, 140), glow=c(200, 160, 255)),
 dict(theme="Angelic", head="angel", pat=("marble", c(245, 244, 240), c(220, 180, 80)), frame="cloud", bench_extra=angel_bench, pad_pat=True, metal=c(240, 236, 228), accent=c(236, 196, 90), pad=c(250, 250, 255), glow=c(255, 220, 120),
      fin=[(0, c(255, 255, 255)), (0.8, c(250, 246, 236)), (1, c(236, 196, 90))]),
 dict(theme="Void", head="void", pat=("void", c(16, 8, 28), c(150, 60, 255)), frame="void", bench_extra=void_bench, pad_pat=True, metal=c(30, 20, 44), accent=c(190, 80, 255), pad=c(28, 14, 44), glow=c(190, 80, 255)),
]

if __name__ == "__main__":
    want = [int(a) for a in sys.argv[1:] if a.isdigit()]; bench_only = "--bench-only" in sys.argv
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for i, t in enumerate(TIERS, 1):
        if want and i not in want: continue
        folder = f"Gym/{i:02d}_{t['theme']}"
        if not bench_only: dumbbell(t, folder)
        bench(t, folder)
