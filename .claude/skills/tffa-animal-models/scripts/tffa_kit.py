"""TFFA kit: build Roblox animals in the "Throw Food For Animals" style with Blender (bpy as a Python module).

Style in one line: chunky chamfered blocks, flat faceted shading, saturated flat colours, a recessed-square
stud texture (1 cell = 1 stud) on the big parts, block eyes (white slab, black square pupil, thick black brow),
white spike teeth/claws/horns. Rare/fantasy animals: faceted low-poly, gradients, no studs.

Build space: +X = forward (head), +Y = animal's left, +Z = up, ground at z = 0, 1 unit = 1 Roblox stud.
Export turns the model so it faces Roblox forward (-Z) and puts the pivot at the ground centre.

    from tffa_kit import *
    m = Model("Gorilla", "models/TFFA/Jungle")
    m.box("Torso", (0, 0, 5), (6, 5, 4), GREY, top=(0.8, 0.8), rot=Ry(-0.2))
    m.seg("Arm", (2, 3, 6), (3, 3, 1), 2.0, 1.8, GREY)
    m.eyes(...)
    m.done()
"""
import os, sys, math
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix

TEX, CELL = 1024, 64                 # atlas: 16 x 16 cells of 64 px
GRID = TEX // CELL
HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------- maths helpers
def V(x, y=0.0, z=0.0): return Vector((x, y, z)) if not hasattr(x, "__len__") else Vector(x)
def Rx(a): return Matrix.Rotation(a, 3, "X")
def Ry(a): return Matrix.Rotation(a, 3, "Y")
def Rz(a): return Matrix.Rotation(a, 3, "Z")
def lerp(a, b, t): return a + (b - a) * t
def rgb(r, g, b): return (r / 255, g / 255, b / 255)
def hexc(h): h = h.lstrip("#"); return rgb(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
def dk(c, k=0.75): return tuple(x * k for x in c)
def lt(c, k=0.35): return tuple(x + (1 - x) * k for x in c)
def mix(a, b, t): return tuple(lerp(x, y, t) for x, y in zip(a, b))

# TFFA palette (sRGB). Saturated, a touch brighter than BrickColors.
WHITE, OFFWHITE, BLACK = rgb(248, 248, 248), rgb(236, 232, 222), rgb(22, 22, 26)
PUPIL = rgb(18, 18, 22)
TOOTH, CLAW, HORN = rgb(250, 250, 246), rgb(245, 245, 240), rgb(240, 236, 226)
MOUTH, TONGUE, GUM = rgb(178, 18, 52), rgb(244, 110, 150), rgb(130, 14, 40)
PINK, NOSE = rgb(255, 160, 175), rgb(40, 34, 36)
FIXED = set()          # extra colours (rounded _k tuples) that mutations keep, e.g. FIXED.add(_k(MOUTH))

# ----------------------------------------------------------------------------- stud tile
def stud_tile(color, variant=0, n=CELL, jitter=0.035):
    """One stud cell: flat colour with a recessed square (dark top/left lip, light bottom/right lip).
    Matches the TFFA in-game "Studs" surface (subtle, about 45% of the cell)."""
    c = np.array(color, np.float32)
    rng = np.random.default_rng(variant * 7919 + int(sum(color) * 1000))
    jit = 1.0 + ((variant - 1.5) / 1.5 * jitter if variant else 0.0) + rng.uniform(-0.01, 0.01)
    img = np.ones((n, n, 3), np.float32) * c * jit
    a0, a1 = int(n * 0.3), int(n * 0.7); w = max(2, n // 20)
    img[a0:a1, a0:a1] *= 0.92                                      # recessed floor (slightly darker)
    # image rows go top->bottom in our numpy (we flip when saving), so row a0 = visual top
    img[a0:a0 + w, a0:a1] = c * jit * 0.70                         # top lip: shadow
    img[a0:a1, a0:a0 + w] = c * jit * 0.78                         # left lip: shadow
    img[a1 - w:a1, a0:a1] = np.minimum(c * jit * 1.18 + 0.05, 1)   # bottom lip: light
    img[a0:a1, a1 - w:a1] = np.minimum(c * jit * 1.07 + 0.02, 1)   # right lip: light
    return np.clip(img, 0, 1)

# ----------------------------------------------------------------------------- model
class Model:
    def __init__(self, name, folder=None, stud=1.0, chamfer=0.12, jitter=0.035, faceted=False):
        """name: asset name. folder: output dir (default <repo>/models/TFFA/<name>). stud: world size of one stud
        cell (1.0 = true Roblox studs; raise it for big animals so the pattern stays readable).
        chamfer: default bevel as a fraction of a part's smallest dimension (0.08-0.18 reads as TFFA)."""
        self.name, self.stud, self.chamfer, self.jitter = name, stud, chamfer, jitter
        self.faceted = faceted     # faceted look (rare/mythic): no studs anywhere
        root = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
        self.out = os.path.abspath(folder) if folder else os.path.join(root, "models", "TFFA", name)
        os.makedirs(self.out, exist_ok=True)
        self.render_on = "--no-render" not in sys.argv
        self.cells = {}            # key -> atlas index
        self.parts, self.glow, self._xf = [], [], []
        self.bones, self._bstack = {}, []      # rig: name -> (pivot in build space, parent)
        bpy.ops.wm.read_factory_settings(use_empty=True)

    # ------------------------------------------------------------------ atlas
    def _cell(self, key):
        if key not in self.cells:
            assert len(self.cells) < GRID * GRID, "atlas full: too many colours/variants"
            self.cells[key] = len(self.cells)
        r, c = divmod(self.cells[key], GRID); ins = 2.5 / TEX
        return (c * CELL / TEX + ins, r * CELL / TEX + ins, (c + 1) * CELL / TEX - ins, (r + 1) * CELL / TEX - ins)
    def _uv(self, box, a, b):
        u0, v0, u1, v1 = box; return (u0 + (u1 - u0) * min(max(a, 0), 1), v0 + (v1 - v0) * min(max(b, 0), 1))
    def _plain(self, color): return self._uv(self._cell(("p", _k(color))), 0.5, 0.5)

    # ------------------------------------------------------------------ core: chamfered hexahedron
    def hexa(self, name, C, color, chamfer=None, studs=True, glow=False, grad=None, seed=0):
        """General 8-corner block. C = 8 corners: bottom (-x-y, +x-y, +x+y, -x+y) then top in the same order.
        studs: True (all big faces), 'top', 'sides' or False. grad=(c0, c1) paints a bottom->top gradient instead."""
        C = [Vector(p) for p in C]
        # cells per axis (shared by opposite faces so neighbouring faces line up)
        E = {"x": [(C[1] - C[0]).length, (C[2] - C[3]).length, (C[5] - C[4]).length, (C[6] - C[7]).length],
             "y": [(C[3] - C[0]).length, (C[2] - C[1]).length, (C[7] - C[4]).length, (C[6] - C[5]).length],
             "z": [(C[4] - C[0]).length, (C[5] - C[1]).length, (C[6] - C[2]).length, (C[7] - C[3]).length]}
        ex, ey, ez = (max(E[k]) for k in "xyz")
        g = self.stud
        ch = self.chamfer if chamfer is None else chamfer
        off = min(ex, ey, ez) * ch if ch > 0 else 0.0
        # grid lines per axis; lines inside the chamfer zone are dropped (the bevel would invert those thin cells)
        lines, unit = {}, {}
        for k in "xyz":
            n = max(1, round(max(E[k]) / g)); r = off * 1.15 / max(min(E[k]), 1e-6)
            ts = [0.0] + [i / n for i in range(1, n) if r < i / n < 1 - r] + [1.0]
            lines[k], unit[k] = ts, 1.0 / n
        if off > 0:   # never bevel wider than the outermost cell
            off = min(off, 0.9 * min((lines[k][1] if len(lines[k]) > 1 else 1) * min(E[k]) for k in "xyz"))
        # faces: (corner a, corner b(=a+U), corner c, corner d(=a+V), u-axis, v-axis, kind)
        F = [(0, 3, 2, 1, "y", "x", "bottom"), (4, 5, 6, 7, "x", "y", "top"),
             (0, 1, 5, 4, "x", "z", "side"), (1, 2, 6, 5, "y", "z", "side"),
             (2, 3, 7, 6, "x", "z", "side"), (3, 0, 4, 7, "y", "z", "side")]
        bm = bmesh.new(); cid = bm.faces.layers.int.new("cid"); vmap = {}
        info = []
        def vert(p):
            k = tuple(round(x, 5) for x in p)
            if k not in vmap: vmap[k] = bm.verts.new(p)
            return vmap[k]
        lo = min(p.z for p in C); hi = max(p.z for p in C)
        for a, b, c, d, ua, va, kind in F:
            A, B, Cc, D = C[a], C[b], C[c], C[d]
            P = lambda s, t: (A * (1 - s) + B * s) * (1 - t) + (D * (1 - s) + Cc * s) * t
            fu, fv = (B - A).length, (D - A).length
            st = bool(studs) and not self.faceted and not grad and (studs is True or (studs == "top" and kind == "top") or
                                               (studs == "sides" and kind == "side")) and min(fu, fv) >= 0.55 * g
            U_, V_ = lines[ua], lines[va]
            for i in range(len(U_) - 1):
                for j in range(len(V_) - 1):
                    s0, s1, t0, t1 = U_[i], U_[i + 1], V_[j], V_[j + 1]
                    q = [P(s0, t0), P(s1, t0), P(s1, t1), P(s0, t1)]
                    if (q[1] - q[0]).cross(q[3] - q[0]).length < 1e-9: continue
                    f = bm.faces.new([vert(p) for p in q])
                    whole = abs((s1 - s0) - unit[ua]) < 1e-6 and abs((t1 - t0) - unit[va]) < 1e-6   # merged edge cells stay plain
                    f[cid] = len(info); info.append((q[0], q[1] - q[0], q[3] - q[0], st and whole, (i * 31 + j * 17 + seed) % 4))
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        new = set()
        if off > 0:
            sharp = [e for e in bm.edges if len(e.link_faces) == 2 and e.link_faces[0].normal.angle(e.link_faces[1].normal, 0) > 0.35]
            if sharp:
                res = bmesh.ops.bevel(bm, geom=sharp, offset=off, segments=1, profile=0.5, affect="EDGES", clamp_overlap=True)
                new = set(res["faces"])
        uvl = bm.loops.layers.uv.new("UVMap")
        pc = self._plain(color)
        for f in bm.faces:
            if f in new:
                for l in f.loops: l[uvl].uv = pc if not grad else self._grad_uv(grad, l.vert.co.z, lo, hi)
                continue
            o, U, W, st, var = info[f[cid]]
            if grad:
                for l in f.loops: l[uvl].uv = self._grad_uv(grad, l.vert.co.z, lo, hi)
            elif st:
                box = self._cell(("s", _k(color), var))
                for l in f.loops:
                    d = l.vert.co - o
                    l[uvl].uv = self._uv(box, d.dot(U) / U.length_squared, d.dot(W) / W.length_squared)
            else:
                for l in f.loops: l[uvl].uv = pc
        return self._obj(name, bm, glow)

    def _grad_uv(self, grad, z, lo, hi):
        box = self._cell(_gkey(grad))
        return self._uv(box, 0.5, (z - lo) / max(hi - lo, 1e-6))

    def frame(self, pivot=(0, 0, 0), scale=1.0, rot=None, move=(0, 0, 0)):
        """Context manager: parts built inside are scaled/rotated about pivot, then moved. Nestable.
        Use it to resize a head, pose a limb or tilt a tail without recomputing coordinates:
            with m.frame(pivot=(3, 0, 6), scale=1.25): ...head parts..."""
        import contextlib
        p = Vector(pivot); sc = scale if hasattr(scale, "__len__") else (scale,) * 3
        M = Matrix.Translation(p + Vector(move)) @ (rot or Matrix.Identity(3)).to_4x4() @ Matrix.Diagonal((*sc, 1)) @ Matrix.Translation(-p)
        @contextlib.contextmanager
        def cm():
            self._xf.append(M)
            try: yield
            finally: self._xf.pop()
        return cm()

    def bone(self, name, head=None, parent=None):
        """Context manager: parts built inside are skinned (rigidly) to bone `name`, pivoting at `head`.
        Standard names (shared clips work across a family): Body, Neck, Head, Jaw, Ear_L/R, Tail1..n,
        Leg_FL/FR/BL/BR (quadrupeds) or Leg_L/R + Arm_L/R (bipeds), Wing_L/R, Fin_L/R, Tent<k>_<j>.
        Omit head to re-enter an existing bone. parent defaults to the enclosing bone, else Body (Body -> Root)."""
        import contextlib
        if name not in self.bones:                        # first definition wins (re-entering keeps the pivot)
            p = Vector(head) if head is not None else Vector((0, 0, 0))
            for M in reversed(self._xf): p = M @ p
            par = parent or (self._bstack[-1] if self._bstack else ("Root" if name == "Body" else "Body"))
            self.bones[name] = (p, par if par != name else "Root", head is not None)
        @contextlib.contextmanager
        def cm():
            self._bstack.append(name)
            try: yield
            finally: self._bstack.pop()
        return cm()

    def _obj(self, name, bm, glow):
        for M in reversed(self._xf): bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = False
        ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
        ob["bone"] = self._bstack[-1] if self._bstack else "Body"
        ob.vertex_groups.new(name=ob["bone"]).add(list(range(len(me.vertices))), 1.0, "REPLACE")
        (self.glow if glow else self.parts).append(ob); return ob

    # ------------------------------------------------------------------ friendly primitives
    def box(self, name, center, size, color, rot=None, top=(1, 1), shift=(0, 0), bot=(1, 1), **kw):
        """Chamfered block. top/bot scale the top/bottom face (x, y) -> frustums, wedges, rounded-looking domes.
        shift moves the top face (x, y) for leaning shapes. rot: 3x3 matrix (Rx/Ry/Rz products)."""
        sx, sy, sz = (s / 2 for s in size)
        C = []
        for z, (kx, ky), (dx, dy) in ((-sz, bot, (0, 0)), (sz, top, shift)):
            for X, Y in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                C.append(Vector((X * sx * kx + dx, Y * sy * ky + dy, z)))
        R = rot or Matrix.Identity(3); c = Vector(center)
        return self.hexa(name, [c + R @ p for p in C], color, **kw)

    def seg(self, name, a, b, w0, w1, color, d0=None, d1=None, up=None, roll=0.0, **kw):
        """Tapered block from point a to point b (limbs, necks, tail pieces). w = width (side to side),
        d = depth (front/back, defaults to w). Square-ish cross-section, chamfered."""
        a, b = Vector(a), Vector(b); ax = (b - a).normalized()
        up = Vector(up) if up else (Vector((1, 0, 0)) if abs(ax.x) < 0.9 else Vector((0, 0, 1)))
        side = ax.cross(up).normalized(); fwd = side.cross(ax).normalized()
        if roll: side, fwd = side * math.cos(roll) + fwd * math.sin(roll), fwd * math.cos(roll) - side * math.sin(roll)
        d0 = d0 or w0; d1 = d1 or w1
        C = []
        for p, w, d in ((a, w0, d0), (b, w1, d1)):
            for X, Y in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                C.append(p + fwd * (X * d / 2) + side * (Y * w / 2))
        return self.hexa(name, C, color, **kw)

    def chain(self, name, pts, widths, color, depths=None, overlap=0.18, bones=None, **kw):
        """Stepped tapering chain of segs through pts (tails, trunks, necks, tentacles). widths per point.
        bones: a bone name prefix (e.g. "Tail" -> Tail1, Tail2, ...) or a list; each segment gets its own bone pivoting
        at its start point, parented to the previous one, so the chain can wag."""
        depths = depths or widths
        names = bones if isinstance(bones, (list, tuple)) else ([f"{bones}{i + 1}" for i in range(len(pts) - 1)] if bones else None)
        for i in range(len(pts) - 1):
            a, b = Vector(pts[i]), Vector(pts[i + 1]); d = (b - a)
            a2, b2 = a - d * overlap * (i > 0), b + d * overlap * (i < len(pts) - 2)
            if names:
                with self.bone(names[i], a, None if i == 0 else names[i - 1]):
                    self.seg(f"{name}{i}", a2, b2, widths[i], widths[i + 1], color, depths[i], depths[i + 1], **kw)
            else:
                self.seg(f"{name}{i}", a2, b2, widths[i], widths[i + 1], color, depths[i], depths[i + 1], **kw)

    def spike(self, name, base, tip, r, color, sides=4, rot=0.0, flat=1.0, glow=False):
        """Pyramid spike: teeth, claws, horns, spines. flat < 1 makes a blade: thin across the animal (Y),
        wide along the jaw/body (X) - TFFA teeth are flat white triangles seen face-on from the side."""
        base, tip = Vector(base), Vector(tip); ax = (tip - base).normalized()
        thin = Vector((0, 1, 0)) if abs(ax.y) < 0.9 else Vector((0, 0, 1))
        u = (thin - ax * thin.dot(ax)).normalized(); w = ax.cross(u)            # u: thin axis, w: wide axis
        bm = bmesh.new(); ring = []
        for k in range(sides):
            t = rot + 2 * math.pi * k / sides + (math.pi / 4 if sides == 4 else 0)
            ring.append(bm.verts.new(base + u * math.cos(t) * r * flat + w * math.sin(t) * r))
        tv = bm.verts.new(tip)
        for k in range(sides): bm.faces.new([ring[k], ring[(k + 1) % sides], tv])
        bm.faces.new(list(reversed(ring)))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        uvl = bm.loops.layers.uv.new("UVMap"); pc = self._plain(color)
        for f in bm.faces:
            for l in f.loops: l[uvl].uv = pc
        return self._obj(name, bm, glow)

    def slab(self, name, pts, thick, color, origin=(0, 0, 0), xaxis=(1, 0, 0), yaxis=(0, 0, 1), chamfer=0.25,
             grad=None, glow=False):
        """Flat plate from a 2D outline (ears, feathers, wings, fins, leaves, crests). The outline lives in the plane
        spanned by xaxis/yaxis at origin, thickness along their cross product. grad=(c0, c1) runs along yaxis."""
        o, X, Y = Vector(origin), Vector(xaxis).normalized(), Vector(yaxis).normalized()
        N = X.cross(Y).normalized()
        bm = bmesh.new()
        ring = [bm.verts.new(o + X * x + Y * y - N * thick / 2) for x, y in pts]
        f = bm.faces.new(ring)
        ext = bmesh.ops.extrude_face_region(bm, geom=[f])
        top = [v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=top, vec=N * thick)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        if chamfer > 0:
            sharp = [e for e in bm.edges if len(e.link_faces) == 2 and e.link_faces[0].normal.angle(e.link_faces[1].normal, 0) > 0.35]
            bmesh.ops.bevel(bm, geom=sharp, offset=thick * chamfer, segments=1, profile=0.5, affect="EDGES", clamp_overlap=True)
        ys = [y for _, y in pts]; lo, hi = min(ys), max(ys)
        uvl = bm.loops.layers.uv.new("UVMap"); pc = self._plain(color)
        for f in bm.faces:
            for l in f.loops:
                if grad:
                    t = (l.vert.co - o).dot(Y); box = self._cell(_gkey(grad))
                    l[uvl].uv = self._uv(box, 0.5, (t - lo) / max(hi - lo, 1e-6))
                else: l[uvl].uv = pc
        return self._obj(name, bm, glow)

    def poly(self, name, pts, thick, color, chamfer=0.25, grad=None, glow=False, mirror=False):
        """Thick plate through 3D outline points (wing membranes, big fins, feather fans, frills).
        The plate is extruded both ways along the outline's average normal. mirror=True also builds the y -> -y copy.
        grad=(c0, c1) runs bottom (low z) -> top (high z)."""
        for s in ((1, -1) if mirror else (1,)):
            P = [Vector((p[0], p[1] * s, p[2])) for p in pts]
            n = Vector((0, 0, 0))
            for i in range(len(P)):
                a, b = P[i], P[(i + 1) % len(P)]
                n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
            n.normalize()
            bm = bmesh.new(); ring = [bm.verts.new(p - n * thick / 2) for p in P]
            f = bm.faces.new(ring)
            ext = bmesh.ops.extrude_face_region(bm, geom=[f])
            bmesh.ops.translate(bm, verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)], vec=n * thick)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            if chamfer > 0:
                sharp = [e for e in bm.edges if len(e.link_faces) == 2 and e.link_faces[0].normal.angle(e.link_faces[1].normal, 0) > 0.35]
                bmesh.ops.bevel(bm, geom=sharp, offset=thick * chamfer, segments=1, profile=0.5, affect="EDGES", clamp_overlap=True)
            lo = min(p.z for p in P); hi = max(p.z for p in P)
            uvl = bm.loops.layers.uv.new("UVMap"); pc = self._plain(color)
            for f in bm.faces:
                for l in f.loops: l[uvl].uv = self._grad_uv(grad, l.vert.co.z, lo, hi) if grad else pc
            self._obj(f"{name}{s if mirror else ''}", bm, glow)

    def ball(self, name, center, size, color, rot=None, segs=(8, 6), glow=False):
        """Low-poly faceted ball (eyes of fantasy animals, pom-poms, berries). Flat shaded."""
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=segs[0], v_segments=segs[1], radius=1.0)
        s = size if hasattr(size, "__len__") else (size,) * 3
        M = Matrix.Translation(Vector(center)) @ ((rot or Matrix.Identity(3)).to_4x4()) @ Matrix.Diagonal((*s, 1))
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        uvl = bm.loops.layers.uv.new("UVMap"); pc = self._plain(color)
        for f in bm.faces:
            for l in f.loops: l[uvl].uv = pc
        return self._obj(name, bm, glow)

    # ------------------------------------------------------------------ TFFA face kit
    def eyes(self, left, facing=(1, 0, 0), size=(1.2, 1.0), pupil=0.6, look=(0.4, -0.08), brow=True, angry=0.3,
             brow_col=BLACK, white=WHITE, pupil_col=PUPIL, brow_h=0.38, brow_up=0.6, brow_w=1.15, brow_fwd=0.06,
             depth=0.2, glow_pupil=False, glow_white=False):
        """TFFA block eyes, built for the LEFT eye and mirrored to the right (y -> -y).
        left: centre of the left eye's white, sitting on the head surface. facing: outward normal of that surface
        ((1,0,0) = front-facing eyes like the gorilla; (0.3,1,0) = side eyes like a T-Rex or horse).
        size: (w, h) of the white. pupil: square pupil size as a fraction of the white's height.
        look: pupil offset (toward the nose/front, up) as fractions of the free space (-1..1).
        angry: brow tilt in radians, inner/front end down (negative = worried/cute). brow=False for no brow."""
        c = Vector(left); f = Vector(facing).normalized(); up0 = Vector((0, 0, 1))
        h = up0.cross(f).normalized(); up = f.cross(h).normalized(); toward = -h     # toward the nose / front
        M = Matrix((f, h, up)).transposed()
        w, hh = size; pw = hh * pupil
        parts = [("EyeW", _hexa_pts(c, M, depth, w, hh), white, glow_white)]
        pc = c + f * (depth * 0.4) + toward * (w / 2 - pw * 0.45) * look[0] + up * (hh / 2 - pw / 2) * look[1]
        parts.append(("Pupil", _hexa_pts(pc, M, depth, pw * 0.9, pw), pupil_col, glow_pupil))
        if brow:
            bc = c + up * hh * brow_up + f * (depth * 0.15 + brow_fwd)
            Mb = Matrix.Rotation(angry, 3, f) @ M
            parts.append(("Brow", _hexa_pts(bc, Mb, depth * 1.4, w * brow_w, hh * brow_h), brow_col, False))
        for s in (1, -1):
            for nm, P, col, gl in parts:
                P2 = P if s > 0 else [Vector((p.x, -p.y, p.z)) for p in P]
                self.hexa(f"{nm}{s}", P2, col, chamfer=0.1, studs=False, glow=gl)

    def teeth(self, name, start, end, n, length, r, color=TOOTH, down=True, fangs=(), sides=3):
        """Row of white spike teeth from start to end, pointing down (upper jaw) or up (lower jaw)."""
        a, b = Vector(start), Vector(end)
        for k in range(n):
            p = a.lerp(b, (k + 0.5) / n); L = length * (1.35 if k in fangs else 1.0)
            self.spike(f"{name}{k}", p, p + Vector((0, 0, -L if down else L)), r, color, sides=sides)

    # ------------------------------------------------------------------ texture, export, previews
    def _atlas(self):
        img = np.ones((TEX, TEX, 3), np.float32) * 0.5
        for key, idx in self.cells.items():
            r, c = divmod(idx, GRID); y0, x0 = r * CELL, c * CELL
            if key[0] == "p": tile = np.ones((CELL, CELL, 3), np.float32) * np.array(key[1])
            elif key[0] == "s": tile = stud_tile(key[1], key[2], jitter=self.jitter)[::-1]          # flip: numpy row 0 = image bottom
            else:                                                # gradient: ("g", c0, c1[, c2]) stops 0 / (0.35) / 1
                cols = [np.array(c) for c in key[1:]]; stops = [0, 1] if len(cols) == 2 else [0, 0.35, 1]
                t = np.linspace(0, 1, CELL)
                tile = np.stack([np.interp(t, stops, [c[i] for c in cols]) for i in range(3)], -1)[:, None, :]
                tile = np.repeat(tile, CELL, axis=1)
            img[y0:y0 + CELL, x0:x0 + CELL] = tile
        return np.clip(img, 0, 1)

    def _detail(self):
        """Grey detail map: stud shading relative to the cell colour (1.0 = flat). Alpha 0 = fixed colours that a
        mutation must not recolour (eye whites, pupils, brows, teeth, claws). Used for rainbow/gold/etc. variants."""
        img = np.ones((TEX, TEX, 4), np.float32)
        for key, idx in self.cells.items():
            r, c = divmod(idx, GRID); y0, x0 = r * CELL, c * CELL
            col = np.array(key[1]); lum = float(col @ np.array([0.299, 0.587, 0.114]))
            if key[0] == "s": img[y0:y0 + CELL, x0:x0 + CELL, :3] = (stud_tile(key[1], key[2], jitter=self.jitter)[::-1] / np.maximum(col, 1e-3)).mean(2, keepdims=True) * 0.5
            else: img[y0:y0 + CELL, x0:x0 + CELL, :3] = 0.5
            fixed = key[0] != "g" and (lum > 0.86 or lum < 0.1 or tuple(key[1]) in FIXED)
            img[y0:y0 + CELL, x0:x0 + CELL, 3] = 0.0 if fixed else 1.0
        return np.clip(img, 0, 1)

    def _save_png(self, arr, nm):
        im = bpy.data.images.new(nm, arr.shape[1], arr.shape[0], alpha=True)
        rgba = np.concatenate([arr, np.ones(arr.shape[:2] + (1,), np.float32)], axis=2) if arr.shape[2] == 3 else arr
        im.pixels.foreach_set(rgba.astype(np.float32).ravel())
        im.filepath_raw = os.path.join(self.out, f"{nm}.png"); im.file_format = "PNG"; im.save()
        im.filepath = im.filepath_raw; return im

    def _join(self, objs, name):
        bpy.ops.object.select_all(action="DESELECT")
        for ob in objs: ob.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join()
        ob = bpy.context.active_object; ob.name = name; ob.data.name = name; return ob

    def done(self, glow_color=None, views=None):
        """Bake the atlas, join, export GLB/FBX/.blend and render previews.
        views: list of (label, azimuth_deg, elevation_deg, lens_mm[, variant]); azimuth 0 = looking at the animal's
        face, 90 = its left side. variant 'rainbow' previews the rainbow mutation (preview only)."""
        self.tex = self._save_png(self._atlas(), f"{self.name}_Texture")
        self.detail = self._save_png(self._detail(), f"{self.name}_Detail")
        body = self._join(self.parts, self.name); objs = [body]
        glow = self._join(self.glow, f"{self.name}_Glow") if self.glow else None
        if glow: objs.append(glow)
        co = np.array([v.co[:] for o in objs for v in o.data.vertices])
        lo, hi = co.min(0), co.max(0)
        shift = Matrix.Translation(Vector((-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2])))
        R = Matrix.Rotation(math.radians(90), 4, "Z")      # build +X forward -> Blender +Y -> glTF/Roblox -Z
        for o in objs:
            o.data.transform(R @ shift); o.location = (0, 0, 0)
        mat = bpy.data.materials.new(f"{self.name}_Mat")
        bsdf = mat.node_tree.nodes["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.6
        tn = mat.node_tree.nodes.new("ShaderNodeTexImage"); tn.image = self.tex; tn.interpolation = "Closest"
        mat.node_tree.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
        body.data.materials.append(mat)
        if glow:
            gc = glow_color or (1, 1, 1); gm = bpy.data.materials.new(f"{self.name}_Glow_Neon")
            gb = gm.node_tree.nodes["Principled BSDF"]
            gb.inputs["Base Color"].default_value = (*[x ** 2.2 for x in gc], 1)
            gb.inputs["Emission Color"].default_value = (*[x ** 2.2 for x in gc], 1)
            gb.inputs["Emission Strength"].default_value = 2.0
            glow.data.materials.append(gm)
        self.xform = R @ shift
        arm = self._rig(objs, R @ shift, hi[2] - lo[2])
        tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs}
        d = body.dimensions
        print(f"TRIS {tris}  SIZE (studs) W {d.x:.1f} x L {d.y:.1f} x H {d.z:.1f}")
        for n_, t in tris.items(): assert t < 20000, f"{n_} has {t} triangles (Roblox limit 20k)"
        bpy.ops.object.select_all(action="DESELECT")
        for o in objs + [arm]: o.select_set(True)
        base = os.path.join(self.out, self.name)
        import tffa_anim
        clips = tffa_anim.add_clips(arm, self)
        arm.animation_data.action = clips[0]
        bpy.ops.export_scene.gltf(filepath=base + ".glb", export_format="GLB", use_selection=True, export_animations=True,
                                  export_animation_mode="ACTIONS", export_skins=True)
        bpy.ops.export_scene.fbx(filepath=base + ".fbx", use_selection=True, path_mode="COPY", embed_textures=True,
                                 mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=True,
                                 bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True)
        os.makedirs(os.path.join(self.out, "anims"), exist_ok=True)
        for act in clips:                       # one FBX per clip for Roblox's Animation Editor (Import > From FBX Animation)
            arm.animation_data.action = act
            bpy.context.scene.frame_start, bpy.context.scene.frame_end = 0, int(act["frames"])
            bpy.ops.object.select_all(action="DESELECT"); arm.select_set(True)
            for o in objs: o.select_set(True)
            bpy.ops.export_scene.fbx(filepath=os.path.join(self.out, "anims", f"{self.name}_{act['clip']}.fbx"), use_selection=True,
                                     add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                                     bake_anim_force_startend_keying=True, mesh_smooth_type="FACE", embed_textures=False, path_mode="STRIP")
        arm.animation_data.action = clips[0]; bpy.context.scene.frame_set(0)
        print("CLIPS", [f"{a['clip']}({a['frames']}f)" for a in clips])
        bpy.ops.wm.save_as_mainfile(filepath=base + ".blend")
        self.objs, self.arm, self.clips = objs, arm, clips
        if self.render_on:
            import tffa_render
            tffa_render.render(self, views or [("hero", 35, 14, 50)])
            if os.environ.get("TFFA_ANIM_PREVIEW", "1") != "0": tffa_render.anim_strip(self)
        print("DONE", base)

    def _rig(self, objs, X, height):
        """Armature in final space. All bones point straight up with roll 0, so every bone shares the same local axes:
        X = animal's right (pitch: + nose up / leg swings forward), Y = up (yaw: + turns left), Z = backward
        (roll: + lowers the animal's LEFT side). That is what makes one clip work on every animal of a family."""
        B = dict(self.bones)
        co = np.array([v.co[:] for o in objs for v in o.data.vertices])
        if "Body" not in B or not B["Body"][2]:
            c = (co.min(0) + co.max(0)) / 2
            B["Body"] = (X.inverted() @ Vector((c[0], c[1], c[2] * 0.8)), "Root", True)
        ad = bpy.data.armatures.new(f"{self.name}_Rig"); arm = bpy.data.objects.new(f"{self.name}_Rig", ad)
        bpy.context.scene.collection.objects.link(arm)
        bpy.ops.object.select_all(action="DESELECT"); arm.select_set(True); bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="EDIT")
        L = max(0.3, height * 0.08)
        root = ad.edit_bones.new("Root"); root.head = (0, 0, 0); root.tail = (0, 0, L); root.roll = 0
        made = {"Root": root}
        def make(n):
            if n in made: return made[n]
            p, par, _ = B[n]; parent = make(par if par in B or par == "Root" else "Body")
            eb = ad.edit_bones.new(n); h = X @ p; eb.head = h; eb.tail = h + Vector((0, 0, L)); eb.roll = 0
            eb.parent = parent; made[n] = eb; return eb
        for n in B: make(n)
        bpy.ops.object.mode_set(mode="OBJECT")
        for o in objs:
            o.parent = arm; md = o.modifiers.new("Armature", "ARMATURE"); md.object = arm
        arm["height"] = float(height)
        return arm


def _k(c): return tuple(round(float(x), 4) for x in c)
def _gkey(grad): return ("g",) + tuple(_k(c) for c in grad)

def _hexa_pts(center, M, depth, w, h):
    """8 corners of a thin block centred at center, axes from M columns (facing, lateral, up)."""
    out = []
    for z in (-h / 2, h / 2):
        for X, Y in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            out.append(center + M @ Vector((X * depth / 2, Y * w / 2, z)))
    return out
