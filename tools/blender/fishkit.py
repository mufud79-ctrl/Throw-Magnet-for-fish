"""Shared toolkit for building the stylised fish models.

Each fish script creates a Fish, builds parts with the helpers below, paints the
texture and calls finish(). Output per fish (in models/<Rarity>/<Name>/):
  <Name>.glb / .fbx / .blend   - textured mesh <Name> (+ <Name>_Glow mesh if any)
  <Name>_Texture.png           - clean texture
  <Name>_Texture_Studs.png     - same texture with Roblox studs overlaid on the body
  previews/*.png
"""
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Matrix

TEX = 1024
STUD_TILE_CELLS = 4   # studs per side in tools/blender/stud.png

def V(x, y, z): return Vector((x, y, z))
def lerp(a, b, t): return a + (b - a) * t
def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)
def c(*rgb): return np.array(rgb, float) / 255.0
def mir(p): return Vector((p.x, -p.y, p.z))
def side(p, s): return p if s > 0 else mir(p)

def pchip(xs, ys, x):
    xs = np.asarray(xs, float); ys = np.asarray(ys, float)
    h = np.diff(xs); d = np.diff(ys) / h
    m = np.zeros_like(ys)
    with np.errstate(divide="ignore", invalid="ignore"):
        hm = 2.0 / (1.0 / d[:-1] + 1.0 / d[1:])
    m[1:-1] = np.where(d[:-1] * d[1:] > 0, hm, 0.0)
    m[0] = d[0]; m[-1] = d[-1]
    i = int(np.clip(np.searchsorted(xs, x) - 1, 0, len(h) - 1))
    t = (x - xs[i]) / h[i]
    return ((2*t**3 - 3*t**2 + 1) * ys[i] + (t**3 - 2*t**2 + t) * h[i] * m[i]
            + (-2*t**3 + 3*t**2) * ys[i+1] + (t**3 - t**2) * h[i] * m[i+1])

def catmull(pts, n):
    P = [pts[0] + (pts[0] - pts[1])] + pts + [pts[-1] + (pts[-1] - pts[-2])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2*p1) + (p2 - p0)*t + (2*p0 - 5*p1 + 4*p2 - p3)*t*t + (3*p1 - p0 - 3*p2 + p3)*t**3))
    out.append(pts[-1]); return out

def basis(n, upish=Vector((0, 0, 1))):
    X = n.normalized(); Z = (upish - X * upish.dot(X)).normalized(); Y = Z.cross(X)
    return Matrix((X, Y, Z)).transposed()

def vnoise(X, Y, freq, seed):
    g = np.random.default_rng(seed).random((64, 64))
    x, y = X * freq, Y * freq
    xi, yi = np.floor(x).astype(int), np.floor(y).astype(int); xf, yf = x - xi, y - yi
    sx, sy = xf*xf*(3 - 2*xf), yf*yf*(3 - 2*yf)
    a = g[xi % 64, yi % 64]; b = g[(xi+1) % 64, yi % 64]; cc = g[xi % 64, (yi+1) % 64]; d = g[(xi+1) % 64, (yi+1) % 64]
    return a + (b - a)*sx + (cc - a)*sy + (a - b - cc + d)*sx*sy

def scales(X, Y, s, squash=1.15, rad=0.78):
    """Overlapping fish scales. Returns (edge 0..1, distance-from-centre 0..1)."""
    best = np.full(X.shape, 1e9); edge = np.zeros(X.shape); inner = np.zeros(X.shape)
    c0 = np.floor(X / s)
    for di in (-1, 0, 1):
        ci = c0 + di; off = (ci % 2) * s / 2
        for dj in (-1, 0, 1):
            cj = np.floor((Y - off) / s) + dj
            d = np.hypot(X - ci * s, (Y - (cj * s + off)) * squash) / (s * rad)
            take = (d < 1) & (ci < best)
            best = np.where(take, ci, best); edge = np.where(take, smooth(0.72, 0.97, d), edge)
            inner = np.where(take, d, inner)
    return edge, inner

def gradient(n, stops):
    rr = (np.arange(n) + .5) / n; out = np.zeros((n, 3))
    for k in range(len(stops) - 1):
        (a0, c0_), (a1, c1_) = stops[k], stops[k + 1]
        m = (rr >= a0) & (rr <= a1); t = ((rr[m] - a0) / (a1 - a0))[:, None]; out[m] = c0_ + (c1_ - c0_) * t
    return out


class Fish:
    """Body = lofted ellipse cross-sections along X (head at +X during build)."""

    def __init__(self, name, rarity, L, R, H, PT, PR, zc=None, w=None, belly=0.88, fin_styles=1):
        self.name, self.rarity = name, rarity
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        default = os.path.join(root, "models", rarity, name)
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        self.out = os.path.abspath(args[0]) if args else default
        self.render = "--no-render" not in sys.argv
        os.makedirs(self.out, exist_ok=True)
        self.L, self.R, self.H, self.PT, self.PR, self.belly = L, R, H, PT, PR, belly
        self.zc = zc or (lambda t: 0.0)
        self.w = w or (lambda t: 0.8)
        self.fin_styles = fin_styles
        self.parts, self.glow = [], []
        bpy.ops.wm.read_factory_settings(use_empty=True)

    # ---- body shape
    def r_of(self, t): return self.R * pchip(self.PT, self.PR, t)
    def x_of(self, t): return self.L / 2 - t * self.L
    def axis(self, t): return Vector((self.x_of(t), 0, self.zc(t)))
    def surf(self, t, th, k=1.0):
        r = self.r_of(t); s = math.sin(th)
        p = Vector((self.x_of(t), self.w(t) * r * math.cos(th),
                    self.zc(t) + self.H * r * s * (self.belly if s < 0 else 1.0)))
        a = self.axis(t); return a + (p - a) * k
    def circ(self, t):
        a = self.w(t) * self.r_of(t); b = self.H * self.r_of(t) * (1 + self.belly) / 2
        return math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))

    # ---- atlas: top half body | bottom-left fins (384px) | 2 strips | 8x8 swatches
    def uv_body(self, t, v): return (0.001 + t * 0.998, 0.5 + 0.001 + v * 0.497)
    def uv_fin(self, s, r, style=0):
        w = 384 / self.fin_styles
        return ((style * w + 4 + s * (w - 8)) / TEX, 0.004 + r * 0.490)
    def uv_strip(self, k, a, s): return ((384 + k*64 + 8 + a*48) / TEX, (6 + s*500) / TEX)
    def uv_sw(self, i): return ((512 + (i % 8)*64 + 32) / TEX, ((i // 8)*64 + 32) / TEX)

    # ---- mesh helpers
    def make_obj(self, name, verts, faces, uvs, glow=False):
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(v) for v in verts], [], faces)
        uvl = me.uv_layers.new(name="UVMap")
        uvl.data.foreach_set("uv", [x for f in uvs for cc in f for x in cc])
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free()
        (self.glow if glow else self.parts).append(ob)
        return ob

    def solidify(self, ob, thick):
        m = ob.modifiers.new("solid", "SOLIDIFY"); m.thickness = thick; m.offset = 0.0
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier="solid")

    def body(self, N=50, M=28):
        ts = [0.004 + 0.992 * (i / (N - 1)) ** 1.25 for i in range(N)]
        verts, faces, uvs = [], [], []
        uvb = self.uv_body
        for t in ts:
            for j in range(M):
                verts.append(self.surf(t, -math.pi / 2 + 2 * math.pi * j / M))
        for i in range(N - 1):
            for j in range(M):
                j2 = (j + 1) % M
                faces.append((i*M + j, i*M + j2, (i+1)*M + j2, (i+1)*M + j))
                uvs.append([uvb(ts[i], j/M), uvb(ts[i], (j+1)/M), uvb(ts[i+1], (j+1)/M), uvb(ts[i+1], j/M)])
        hp = len(verts); verts.append(self.axis(0))
        tp = len(verts); verts.append(self.axis(1) - Vector((0.02, 0, 0)))
        last = (N - 1) * M
        for j in range(M):
            j2 = (j + 1) % M
            faces.append((hp, j2, j)); uvs.append([uvb(0, (j+.5)/M), uvb(ts[0], (j+1)/M), uvb(ts[0], j/M)])
            faces.append((tp, last + j, last + j2)); uvs.append([uvb(1, (j+.5)/M), uvb(ts[-1], j/M), uvb(ts[-1], (j+1)/M)])
        return self.make_obj("Body", verts, faces, uvs)

    def fin(self, name, root, direc, length, wave, nu, nv, thick=0.025, style=0, glow=False):
        verts, faces, uvs = [], [], []
        for a in range(nu + 1):
            s = a / nu
            R0, D, Ln = root(s), direc(s).normalized(), length(s)
            for b in range(nv + 1):
                r = b / nv
                verts.append(R0 + D * (Ln * r) + wave(s, r))
        uf = lambda s, r: self.uv_fin(s, r, style)
        for a in range(nu):
            for b in range(nv):
                i = a * (nv + 1) + b
                faces.append((i, i + nv + 1, i + nv + 2, i + 1))
                uvs.append([uf(a/nu, b/nv), uf((a+1)/nu, b/nv), uf((a+1)/nu, (b+1)/nv), uf(a/nu, (b+1)/nv)])
        ob = self.make_obj(name, verts, faces, uvs, glow); self.solidify(ob, thick); return ob

    def tube(self, name, ctrl, r0, r1, strip=0, K=8, sub=5, pw=1.0, glow=False, sw=None):
        pts = catmull(ctrl, sub); n = len(pts)
        seg = [0.0]
        for i in range(1, n): seg.append(seg[-1] + (pts[i] - pts[i-1]).length)
        T = [(pts[min(i+1, n-1)] - pts[max(i-1, 0)]).normalized() for i in range(n)]
        up = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((0, 1, 0))
        Ns = [T[0].cross(up).normalized()]
        for i in range(1, n):
            ax = T[i-1].cross(T[i]); nn = Ns[-1].copy()
            if ax.length > 1e-6: nn = Matrix.Rotation(T[i-1].angle(T[i]), 3, ax.normalized()) @ nn
            Ns.append(nn)
        uvs_f = (lambda k, a, s: self.uv_sw(sw)) if sw is not None else self.uv_strip
        verts, faces, uvs = [], [], []
        for i in range(n - 1):
            s = seg[i] / seg[-1]; r = lerp(r0, r1, s ** pw)
            B = T[i].cross(Ns[i])
            for k in range(K):
                a = 2 * math.pi * k / K
                verts.append(pts[i] + r * (math.cos(a) * Ns[i] + math.sin(a) * B))
        rings = n - 1
        for i in range(rings - 1):
            for k in range(K):
                k2 = (k + 1) % K
                faces.append((i*K + k, i*K + k2, (i+1)*K + k2, (i+1)*K + k))
                s0, s1 = seg[i] / seg[-1], seg[i+1] / seg[-1]
                uvs.append([uvs_f(strip, k/K, s0), uvs_f(strip, (k+1)/K, s0), uvs_f(strip, (k+1)/K, s1), uvs_f(strip, k/K, s1)])
        tip = len(verts); verts.append(pts[-1]); base = len(verts); verts.append(pts[0])
        l0 = (rings - 1) * K
        for k in range(K):
            k2 = (k + 1) % K
            faces.append((l0 + k, l0 + k2, tip)); uvs.append([uvs_f(strip, k/K, .98), uvs_f(strip, (k+1)/K, .98), uvs_f(strip, .5, 1)])
            faces.append((k2, k, base)); uvs.append([uvs_f(strip, (k+1)/K, 0), uvs_f(strip, k/K, 0), uvs_f(strip, .5, 0)])
        return self.make_obj(name, verts, faces, uvs, glow)

    def sphere(self, name, center, rot, scale, sw, u=18, v=12, glow=False):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
        M = Matrix.Translation(center) @ rot.to_4x4() @ Matrix.Diagonal((*scale, 1))
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        verts = [vv.co.copy() for vv in bm.verts]; faces = [tuple(vv.index for vv in f.verts) for f in bm.faces]; bm.free()
        return self.make_obj(name, verts, faces, [[self.uv_sw(sw)] * len(f) for f in faces], glow)

    def torus(self, name, center, n, R1, r1, sw, U=24, Vn=8, glow=False):
        Bm = basis(n); X, Y, Z = Bm.col[0], Bm.col[1], Bm.col[2]
        verts, faces = [], []
        for i in range(U):
            a = 2 * math.pi * i / U; ring = math.cos(a) * Y + math.sin(a) * Z
            for j in range(Vn):
                b = 2 * math.pi * j / Vn
                verts.append(center + ring * (R1 + r1 * math.cos(b)) + X * (r1 * math.sin(b)))
        for i in range(U):
            for j in range(Vn):
                i2, j2 = (i + 1) % U, (j + 1) % Vn
                faces.append((i*Vn + j, i2*Vn + j, i2*Vn + j2, i*Vn + j2))
        return self.make_obj(name, verts, faces, [[self.uv_sw(sw)] * 4 for f in faces], glow)

    def gem(self, name, center, rot, scale, sw, glow=False):
        """Octahedron (diamond) gem."""
        pts = [V(1, 0, 0), V(-1, 0, 0), V(0, 1, 0), V(0, -1, 0), V(0, 0, 1), V(0, 0, -1)]
        M = Matrix.Translation(center) @ rot.to_4x4() @ Matrix.Diagonal((*scale, 1))
        verts = [M @ p for p in pts]
        faces = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]
        return self.make_obj(name, verts, faces, [[self.uv_sw(sw)] * 3 for f in faces], glow)

    def eyes(self, te, th, re, iris, pupil, rim, white, pupil_scale=(0.05, 0.05, 0.135), fwd=0.38, sink=0.075,
             rim_r=0.032, glint=0.042):
        for sd in (1, -1):
            nm = "L" if sd > 0 else "R"
            S = side(self.surf(te, th), sd)
            n = ((S - self.axis(te)).normalized() + V(fwd, 0, 0)).normalized()
            C = S - n * sink; Bm = basis(n)
            self.sphere(f"Eye_{nm}", C, Bm, (re, re, re), iris)
            self.sphere(f"Pupil_{nm}", C + n * (re - 0.025), Bm, pupil_scale, pupil, 14, 10)
            hl = (n * 0.9 + Bm.col[2] * 0.42 + V(0.25, 0, 0)).normalized()
            self.sphere(f"Glint_{nm}", C + hl * (re + 0.005), Bm, (glint,) * 3, white, 10, 6)
            if rim is not None:
                d = re * 0.42
                self.torus(f"EyeRim_{nm}", C + n * d, n, math.sqrt(re*re - d*d) + 0.005, rim_r, rim)

    # ---- texture
    def texture(self, paint_body, fin_stops, strips, swatches, ray_period=12, ray_strength=0.25):
        """paint_body(T, Vv, top) -> (512,1024,3) colours. T,Vv in 0..1, top=+1 dorsal..-1 belly."""
        S = TEX; img = np.full((S, S, 3), 0.5)
        T, Vv = np.meshgrid((np.arange(S) + .5) / S, (np.arange(512) + .5) / 512)
        top = np.cos(2 * np.pi * (Vv - 0.5))
        img[512:] = paint_body(T, Vv, top)
        w = 384 // self.fin_styles
        for k, stops in enumerate(fin_stops):
            grad = gradient(512, stops); xx = np.arange(w); rr = (np.arange(512) + .5) / 512
            ray = np.exp(-((xx % ray_period) - ray_period / 2) ** 2 / 2.2)
            img[:512, k*w:(k+1)*w] = grad[:, None, :] * (1 - ray_strength * ray[None, :, None] * (1 - 0.7 * rr)[:, None, None])
        for k, (a, b, p) in enumerate(strips):
            t = ((np.arange(512) + .5) / 512) ** p
            img[:512, 384 + 64*k: 448 + 64*k] = (a + (b - a) * t[:, None])[:, None, :]
        for i, v in swatches.items():
            x0, y0 = 512 + (i % 8) * 64, (i // 8) * 64
            img[y0:y0 + 64, x0:x0 + 64] = v
        self.img = np.clip(img, 0, 1)
        self.img_studs = self.img.copy()
        self.img_studs[512:] = self.studs(self.img[512:], T, Vv)
        self.tex = self._save(self.img, f"{self.name}_Texture")
        self._save(self.img_studs, f"{self.name}_Texture_Studs")

    def studs(self, col, T, Vv, spacing=float(os.environ.get("STUD_SPACING", 0.5)), rad=0.3):
        """Roblox studs on the body at true scale (1 Blender unit = 1 stud).
        Uses tools/blender/stud.png (one tile = one stud) if present, else a procedural stud."""
        X = T * self.L
        C = np.array([self.circ(t) for t in T[0]])[None, :]
        Y = Vv * C
        amt = smooth(0.03, 0.09, T) * (1 - smooth(0.93, 0.99, T))
        tile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stud.png")
        if os.path.exists(tile):
            im = bpy.data.images.load(tile); w, h = im.size
            px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, im.channels)
            rgb = px[..., :3]; a = px[..., 3] if im.channels == 4 else np.ones((h, w))
            lum = rgb @ np.array([0.299, 0.587, 0.114])
            ref = np.median(lum[a > 0.5]) if (a > 0.5).any() else 0.5
            fac = np.where(a > 0, 1 + (lum / max(ref, 1e-3) - 1) * a, 1.0)
            n = STUD_TILE_CELLS                       # stud.png holds an n x n grid of studs
            flip = np.where(Vv < 0.5, 1.0, -1.0)    # keep the tile upright on both sides
            u = ((X * flip / (spacing * n)) % 1.0 * w).astype(int).clip(0, w - 1)
            v = ((Y * flip / (spacing * n)) % 1.0 * h).astype(int).clip(0, h - 1)
            f = 1 + (fac[v, u] - 1) * amt
            return np.clip(col * f[..., None], 0, 1)
        cx = (np.floor(X / spacing) + 0.5) * spacing; cy = (np.floor(Y / spacing) + 0.5) * spacing
        dx, dy = (X - cx) / rad, (Y - cy) / rad
        up = np.where(Vv < 0.5, 1.0, -1.0)            # texture direction pointing toward the back
        lx, ly = -0.45, 0.89 * up                     # light from front-top
        d = np.hypot(dx, dy) + 1e-6
        inside = 1 - smooth(0.96, 1.02, d)
        lit = (dx * lx + dy * ly) / d * smooth(0.45, 0.95, d) * inside   # +1 lit side, -1 shaded side
        outline = np.exp(-((d - 1.0) / 0.07) ** 2)
        ds = np.hypot(dx + lx * 0.22, dy + ly * 0.22)
        drop = (1 - smooth(0.92, 1.12, ds)) * (1 - inside)
        dark = np.clip(0.30 * np.maximum(-lit, 0) + 0.22 * outline + 0.22 * drop, 0, 1) * amt
        light = np.clip(0.45 * np.maximum(lit, 0) + 0.06 * inside, 0, 1) * amt
        out = col + (1 - col) * light[..., None]
        out = out * (1 - dark[..., None])
        # light colours can't brighten, so give the whole stud top a faint tint shift
        out = out * (1 - 0.05 * inside * amt)[..., None]
        return np.clip(out, 0, 1)

    def _save(self, arr, nm):
        im = bpy.data.images.new(nm, TEX, TEX, alpha=False)
        rgba = np.concatenate([arr, np.ones((TEX, TEX, 1))], axis=2).astype(np.float32)
        im.pixels.foreach_set(rgba.ravel())
        im.filepath_raw = os.path.join(self.out, f"{nm}.png"); im.file_format = "PNG"; im.save()
        im.filepath = im.filepath_raw
        return im

    # ---- assemble / export / preview
    def _join(self, objs, name):
        bpy.ops.object.select_all(action="DESELECT")
        for ob in objs: ob.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.join()
        ob = bpy.context.active_object; ob.name = name; ob.data.name = name
        return ob

    def finish(self, bend=0.5, bend_len=7.0, glow_color=None, views=None, cam_scale=1.0):
        fish = self._join(self.parts, self.name)
        objs = [fish]
        glow = None
        if self.glow:
            glow = self._join(self.glow, f"{self.name}_Glow"); objs.append(glow)
        for ob in objs:
            for v in ob.data.vertices:
                k = max(0.0, (self.L / 2 - v.co.x) / bend_len)
                v.co.y += bend * k ** 2.2
            ob.data.transform(Matrix.Rotation(math.radians(90), 4, "Z"))
        co = np.array([v.co[:] for v in fish.data.vertices])
        center = Vector(((co.min(0) + co.max(0)) / 2).tolist())
        for ob in objs:
            ob.data.transform(Matrix.Translation(-center)); ob.location = (0, 0, 0)
            bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True)
            bpy.context.view_layer.objects.active = ob; bpy.ops.object.shade_smooth()

        mat = bpy.data.materials.new(f"{self.name}_Mat")
        bsdf = mat.node_tree.nodes["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.45
        tn = mat.node_tree.nodes.new("ShaderNodeTexImage"); tn.image = self.tex
        mat.node_tree.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
        fish.data.materials.append(mat)
        if glow:
            gcol = (*[x ** 2.2 for x in glow_color], 1.0)
            gm = bpy.data.materials.new(f"{self.name}_Glow_Neon")
            gb = gm.node_tree.nodes["Principled BSDF"]
            gb.inputs["Base Color"].default_value = gcol
            gb.inputs["Emission Color"].default_value = gcol
            gb.inputs["Emission Strength"].default_value = 1.6
            glow.data.materials.append(gm)

        tris = {ob.name: sum(len(p.vertices) - 2 for p in ob.data.polygons) for ob in objs}
        d = fish.dimensions
        print(f"TRIS {tris}  DIMS {d.x:.2f} x {d.y:.2f} x {d.z:.2f}")

        bpy.ops.object.select_all(action="DESELECT")
        for ob in objs: ob.select_set(True)
        base = os.path.join(self.out, self.name)
        bpy.ops.export_scene.gltf(filepath=base + ".glb", export_format="GLB", use_selection=True)
        bpy.ops.export_scene.fbx(filepath=base + ".fbx", use_selection=True, path_mode="COPY",
                                 embed_textures=True, mesh_smooth_type="FACE")
        bpy.ops.wm.save_as_mainfile(filepath=base + ".blend")
        if self.render:
            self._previews(fish, views, cam_scale)
        print("DONE")

    def _previews(self, fish, views, k):
        sc = bpy.context.scene
        sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 48
        sc.cycles.use_denoising = True
        sc.render.resolution_x, sc.render.resolution_y = 1400, 1000
        sc.view_settings.view_transform = "Standard"
        world = bpy.data.worlds.new("W"); sc.world = world
        bg = world.node_tree.nodes["Background"]
        bg.inputs[0].default_value = (0.42, 0.55, 0.68, 1); bg.inputs[1].default_value = 0.9
        def light(name, loc, energy, size):
            ld = bpy.data.lights.new(name, "AREA"); ld.energy = energy; ld.size = size
            lo = bpy.data.objects.new(name, ld); lo.location = loc; sc.collection.objects.link(lo)
            lo.constraints.new("TRACK_TO").target = fish
        light("Key", (6, 5, 8), 2200, 6); light("Fill", (-7, 2, 2), 700, 8); light("Rim", (0, -8, 5), 1200, 5)
        cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d)
        sc.collection.objects.link(cam); sc.camera = cam
        tgt = bpy.data.objects.new("Tgt", None); sc.collection.objects.link(tgt)
        cam.constraints.new("TRACK_TO").target = tgt
        views = views or {"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50), "side": ((12.5, 0, 0.6), (0, 0, 0.2), 50),
                          "front": ((2.2, 8.5, 1.0), (0, 1.5, 0.2), 40)}
        mat = fish.data.materials[0]
        studs_img = bpy.data.images.get(f"{self.name}_Texture_Studs")
        tn = [n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"][0]
        shots = list(views.items()) + [("hero_studs", views["hero"])]
        for nm, (loc, tg, lens) in shots:
            tn.image = studs_img if nm.endswith("studs") else self.tex
            cam.location = Vector(loc) * k; tgt.location = Vector(tg) * k; cam_d.lens = lens
            sc.render.filepath = os.path.join(self.out, "previews", f"{self.name}_{nm}.png")
            bpy.ops.render.render(write_still=True)
        tn.image = self.tex
