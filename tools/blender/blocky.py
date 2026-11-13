"""Roblox-style part builder for environment props ("Grow a Garden" look).

Props are assembled from parts: block (studded on every face, 1 stud per cell), wedge, cylinder and ball
(smooth plastic), all in flat bright colours. Each prop gets its own atlas of colour cells: a studded and a
plain cell per colour, with the stud tile taken from tools/blender/stud.png. Neon parts go to <Name>_Glow.
Units: 1 Blender unit = 1 stud.
"""
import os, math
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix
from fishkit import Fish, V

HERE = os.path.dirname(os.path.abspath(__file__))
CELL, GRIDN = 128, 8          # 8x8 cells of 128px in a 1024 atlas -> 32 colours per prop

def rgb(r, g, b): return (r / 255, g / 255, b / 255)
# Roblox-ish BrickColor palette
WHITE, LGREY, GREY, DGREY, BLACK = rgb(242, 243, 243), rgb(163, 162, 165), rgb(108, 110, 114), rgb(70, 72, 78), rgb(30, 32, 38)
RED, PINK, MAGENTA, LAVENDER, PURPLE = rgb(196, 40, 28), rgb(255, 152, 220), rgb(180, 50, 170), rgb(180, 140, 255), rgb(98, 50, 200)
ORANGE, YELLOW, SAND, NOUGAT, TAN = rgb(230, 130, 50), rgb(245, 205, 48), rgb(215, 197, 154), rgb(204, 142, 105), rgb(180, 140, 95)
BROWN, RBROWN, DBROWN = rgb(124, 92, 70), rgb(105, 64, 40), rgb(80, 56, 40)
GREEN, LIME, DGREEN, MOSS = rgb(75, 151, 75), rgb(140, 200, 70), rgb(40, 110, 60), rgb(110, 140, 90)
BLUE, LBLUE, CYAN, NAVY, TEAL = rgb(13, 105, 172), rgb(128, 187, 219), rgb(40, 190, 236), rgb(20, 40, 100), rgb(40, 160, 150)
GOLD, ICE, SNOW, CORAL, TERRA, OBSID = rgb(239, 184, 56), rgb(175, 221, 255), rgb(250, 250, 252), rgb(255, 120, 100), rgb(190, 104, 80), rgb(40, 34, 52)
NEON = rgb(255, 255, 255)

def _stud_tile():
    im = bpy.data.images.load(os.path.join(HERE, "stud.png")); w, h = im.size
    px = np.array(im.pixels[:], np.float32).reshape(h, w, im.channels)[..., :3]
    cw, ch = w // 4, h // 4; tile = px[:ch, :cw]
    yi = (np.arange(CELL) * ch / CELL).astype(int); xi = (np.arange(CELL) * cw / CELL).astype(int)
    lum = tile[yi][:, xi] @ np.array([0.299, 0.587, 0.114])
    return np.clip(lum / np.median(lum), 0.55, 1.15)

class Brick(Fish):
    flat = "keep"
    def __init__(self, name, folder, grid=1.0):
        super().__init__(name, folder, L=3.0, R=0.5, H=1.0, PT=[0, 1], PR=[1, 1], fin_styles=1)
        self.cells, self.grid = {}, grid

    # ---- atlas cells
    def cell(self, color, studs):
        key = (tuple(round(x, 4) for x in color), bool(studs))
        if key not in self.cells:
            assert len(self.cells) < GRIDN * GRIDN, "too many colours in one prop"
            self.cells[key] = len(self.cells)
        r, c_ = divmod(self.cells[key], GRIDN); ins = 4 / 1024
        return (c_ * CELL / 1024 + ins, r * CELL / 1024 + ins, (c_ + 1) * CELL / 1024 - ins, (r + 1) * CELL / 1024 - ins)
    def _uv(self, cellbox, a, b):
        u0, v0, u1, v1 = cellbox; return (u0 + (u1 - u0) * a, v0 + (v1 - v0) * b)

    def _place(self, verts, center, rot):
        R = rot if rot is not None else Matrix.Identity(3)
        return [Vector(center) + R @ Vector(v) for v in verts]
    def _smooth(self, ob, flags):
        ob.data.polygons.foreach_set("use_smooth", flags)

    # ---- parts
    def block(self, name, center, size, color, rot=None, studs=True, glow=False):
        hx, hy, hz = (s / 2 for s in size); g = self.grid
        faces_def = [((-hx, -hy, hz), (2 * hx, 0, 0), (0, 2 * hy, 0)), ((-hx, hy, -hz), (2 * hx, 0, 0), (0, -2 * hy, 0)),
                     ((hx, -hy, -hz), (0, 2 * hy, 0), (0, 0, 2 * hz)), ((-hx, hy, -hz), (0, -2 * hy, 0), (0, 0, 2 * hz)),
                     ((hx, hy, -hz), (-2 * hx, 0, 0), (0, 0, 2 * hz)), ((-hx, -hy, -hz), (2 * hx, 0, 0), (0, 0, 2 * hz))]
        key, verts, faces, uvs = {}, [], [], []
        def vid(p):
            k = tuple(round(x, 5) for x in p)
            if k not in key: key[k] = len(verts); verts.append(p)
            return key[k]
        for o, U, W in faces_def:
            o, U, W = Vector(o), Vector(U), Vector(W)
            nu, nv = max(1, round(U.length / g)), max(1, round(W.length / g))
            st = studs and U.length >= 0.6 * g and W.length >= 0.6 * g
            cb = self.cell(color, st)
            for i in range(nu):
                for j in range(nv):
                    q = [o + U * (i / nu) + W * (j / nv), o + U * ((i + 1) / nu) + W * (j / nv),
                         o + U * ((i + 1) / nu) + W * ((j + 1) / nv), o + U * (i / nu) + W * ((j + 1) / nv)]
                    faces.append(tuple(vid(p) for p in q))
                    uvs.append([self._uv(cb, 0, 0), self._uv(cb, 1, 0), self._uv(cb, 1, 1), self._uv(cb, 0, 1)] if st else [self._uv(cb, .5, .5)] * 4)
        ob = self.make_obj(name, self._place(verts, center, rot), faces, uvs, glow)
        self._smooth(ob, [False] * len(faces)); return ob

    def wedge(self, name, center, size, color, rot=None, glow=False):
        """Roblox WedgePart: full height at -X, sloping down to +X."""
        hx, hy, hz = (s / 2 for s in size)
        verts = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz), (-hx, -hy, hz), (-hx, hy, hz)]
        faces = [(0, 3, 2, 1), (0, 4, 5, 3), (1, 2, 5, 4), (0, 1, 4), (3, 5, 2)]
        cb = self.cell(color, False)
        ob = self.make_obj(name, self._place(verts, center, rot), faces, [[self._uv(cb, .5, .5)] * len(f_) for f_ in faces], glow)
        self._smooth(ob, [False] * len(faces)); return ob

    def cyl(self, name, a, b, r, color, K=16, glow=False, r1=None):
        a, b = Vector(a), Vector(b); ax = (b - a).normalized(); r1 = r if r1 is None else r1
        up = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
        u = ax.cross(up).normalized(); w = ax.cross(u)
        ring = lambda p, rr: [p + (u * math.cos(2 * math.pi * k / K) + w * math.sin(2 * math.pi * k / K)) * rr for k in range(K)]
        verts = ring(a, r) + ring(b, r1) + [a, b]
        faces = [(k, (k + 1) % K, K + (k + 1) % K, K + k) for k in range(K)]
        faces += [((k + 1) % K, k, 2 * K) for k in range(K)] + [(K + k, K + (k + 1) % K, 2 * K + 1) for k in range(K)]
        cb = self.cell(color, False)
        ob = self.make_obj(name, verts, faces, [[self._uv(cb, .5, .5)] * len(f_) for f_ in faces], glow)
        self._smooth(ob, [K > 6] * K + [False] * (2 * K)); return ob

    def ball(self, name, center, size, color, rot=None, glow=False, u=16, v=10):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
        s = size if isinstance(size, (tuple, list)) else (size,) * 3
        M_ = Matrix.Translation(center) @ (rot.to_4x4() if rot else Matrix.Identity(4)) @ Matrix.Diagonal((*s, 1))
        bmesh.ops.transform(bm, matrix=M_, verts=bm.verts)
        verts = [x.co.copy() for x in bm.verts]; faces = [tuple(x.index for x in f_.verts) for f_ in bm.faces]; bm.free()
        cb = self.cell(color, False)
        ob = self.make_obj(name, verts, faces, [[self._uv(cb, .5, .5)] * len(f_) for f_ in faces], glow)
        self._smooth(ob, [True] * len(faces)); return ob

    def rocks(self, name, center, size, color, n=4, seed=1, color2=None):
        """Classic Roblox rock: a cluster of rotated blocks."""
        rng = np.random.default_rng(seed)
        for k in range(n):
            s = size * rng.uniform(0.55, 1.0); off = Vector((rng.uniform(-.5, .5) * size, rng.uniform(-.5, .5) * size, 0))
            R = Matrix.Rotation(rng.uniform(0, 3), 3, "Z") @ Matrix.Rotation(rng.uniform(-.35, .35), 3, "X") @ Matrix.Rotation(rng.uniform(-.35, .35), 3, "Y")
            self.block(f"{name}{k}", Vector(center) + off + Vector((0, 0, s * 0.35)), (s, s * rng.uniform(.7, 1), s * rng.uniform(.6, .9)),
                       color2 if (color2 and k % 2) else color, R)

    # ---- texture + export
    def done(self, glow=None, views=None):
        tile = _stud_tile(); img = np.ones((1024, 1024, 3), np.float32) * 0.5
        for (color, st), idx in self.cells.items():
            r, c_ = divmod(idx, GRIDN)
            img[r * CELL:(r + 1) * CELL, c_ * CELL:(c_ + 1) * CELL] = np.array(color)[None, None, :] * (tile[..., None] if st else 1.0)
        img = np.clip(img, 0, 1)
        self.tex = self._save(img, f"{self.name}_Texture"); self._save(img, f"{self.name}_Texture_Studs")
        co = np.concatenate([np.array([v.co[:] for v in o.data.vertices]) for o in self.parts + self.glow])
        size = float((co.max(0) - co.min(0)).max()); hz = float(co[:, 2].max() - co[:, 2].min())
        self.finish(bend=0.0, rig=False, glow_color=glow, cam_scale=max(0.45, size / 5.8, hz / 3.6),
                    views=views or {"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50)})
