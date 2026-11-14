"""All 15 baits (fish food). Run: python baits.py [BaitName ...] [--no-render]

Output: models/Baits/<Rarity>/<Name>/ (glb, fbx, blend, textures, previews). Baits are static props:
finish(rig=False) skips the fish rig and animation clips. The atlas body region (top half) is used as a
free painting canvas: each part maps onto its own rectangle there and gets a procedural painter.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from mathutils import Vector, Matrix, Euler
from fishkit import Fish, V, c, lerp, smooth, vnoise, basis, catmull, pchip, scales

VIEWS = {"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50), "side": ((12.5, 0, 0.6), (0, 0, 0.2), 50)}
TAU = 2 * math.pi
CAM = V(1, -1, 0.42).normalized()        # direction to the hero camera in build space (+X front, -Y display side)

def E(x, y, z): return Euler((x, y, z)).to_matrix()
def fz(axis, hint=V(0, 0, 1)):
    """Rotation whose local Z = axis and local X ~ hint."""
    Z = Vector(axis).normalized(); X = hint - Z * hint.dot(Z)
    if X.length < 1e-6: X = V(1, 0, 0) - Z * Z.x
    X.normalize(); Y = Z.cross(X); return Matrix((X, Y, Z)).transposed()
def rot_axis(ax, ang): return Matrix.Rotation(ang, 3, Vector(ax).normalized())
def fbm(x, y, f, seed, o=3):
    s, w, tot = 0.0, 1.0, 0.0
    for k in range(o): s = s + w * vnoise(x, y, f * 2 ** k, seed + k); tot += w; w *= 0.5
    return s / tot
def mix(col, c2, m): m = np.clip(m, 0, 1)[..., None]; return col * (1 - m) + c2 * m
def solid(a, col): return np.zeros(a.shape + (3,)) + col
def seg_dist(px, py, p0, p1):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L2 = dx * dx + dy * dy + 1e-12
    t = np.clip(((px - p0[0]) * dx + (py - p0[1]) * dy) / L2, 0, 1)
    return np.hypot(px - p0[0] - t * dx, py - p0[1] - t * dy)
def n3(p, f=7.0, ph=0.0):   # cheap smooth 3D noise in -1..1
    return (math.sin(f * p.x + 1.3 + ph) * math.sin(f * 1.13 * p.y + 2.1 + ph) * math.sin(f * 0.91 * p.z + 0.7 + ph)
            + 0.5 * math.sin(2.1 * f * p.x + ph) * math.sin(1.9 * f * p.z + 2.4 + ph)) / 1.5


class Bait(Fish):
    def __init__(self, name, rarity, fin_styles=1):
        super().__init__(name, "Baits/" + rarity, L=1.0, R=0.3, H=1.0, PT=[0, 0.5, 1], PR=[1, 1, 1], fin_styles=fin_styles)
        self.regions = []

    # ---- UV regions in the atlas body half
    def ruv(self, rect, a, b):
        t0, v0, t1, v1 = rect
        a = min(max(a, 0.0), 1.0); b = min(max(b, 0.0), 1.0)
        return self.uv_body(t0 + a * (t1 - t0), v0 + b * (v1 - v0))
    def region(self, rect, painter): self.regions.append((rect, painter))

    # ---- mesh builders (all weld coincident points so smooth shading has no seams)
    def polys(self, name, flist, ulist, glow=False):
        key, verts, faces, uvs = {}, [], [], []
        for fp, fu in zip(flist, ulist):
            ids, uu = [], []
            for p, u in zip(fp, fu):
                k = (round(p.x, 5), round(p.y, 5), round(p.z, 5))
                if k not in key: key[k] = len(verts); verts.append(p.copy())
                i = key[k]
                if i in ids: continue
                ids.append(i); uu.append(u)
            if len(ids) >= 3: faces.append(tuple(ids)); uvs.append(uu)
        return self.make_obj(name, verts, faces, uvs, glow)

    def grid(self, name, P, nu, nv, uvf, glow=False):
        G = [[P(i, j) for j in range(nv + 1)] for i in range(nu + 1)]
        fl, ul = [], []
        for i in range(nu):
            for j in range(nv):
                cs = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
                fl.append([G[a][b] for a, b in cs]); ul.append([uvf(a, b, j) for a, b in cs])
        return self.polys(name, fl, ul, glow)

    def ell(self, name, C, rot, scale, rect=None, sw=0, nu=24, nv=16, deform=None, glow=False):
        """Deformable ellipsoid. UV: lon -> a, lat (south..north pole) -> b."""
        sx, sy, sz = scale
        def P(i, j):
            lon, lat = TAU * i / nu, -math.pi / 2 + math.pi * j / nv
            p = V(0, 0, -1) if j == 0 else V(0, 0, 1) if j == nv else V(math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat))
            if deform: p = deform(p)
            return C + rot @ V(p.x * sx, p.y * sy, p.z * sz)
        uvf = (lambda i, j, fj: self.ruv(rect, i / nu, j / nv)) if rect else (lambda i, j, fj: self.uv_sw(sw))
        return self.grid(name, P, nu, nv, uvf, glow)

    def rbox(self, name, C, rot, half, rnd, n, rects, deform=None, glow=False):
        """Rounded box; rects = 6 UV rects for faces +X,-X,+Y,-Y,+Z,-Z. deform(local_point, normal) -> point."""
        h = np.array(half, float); inner = h - rnd
        sp = lambda k: math.sin(math.pi / 2 * (-1 + 2 * k / n))
        fl, ul = [], []
        for fi, (ax, sg) in enumerate([(0, 1), (0, -1), (1, 1), (1, -1), (2, 1), (2, -1)]):
            ua, va = [x for x in range(3) if x != ax]
            def P(i, j):
                q = np.zeros(3); q[ax] = sg; q[ua] = sp(i); q[va] = sp(j)
                L = q * h; cl = np.clip(L, -inner, inner); d = L - cl
                nn = Vector((d / np.linalg.norm(d)).tolist()); p = Vector(cl.tolist()) + nn * rnd
                if deform: p = deform(p, nn)
                return C + rot @ p
            G = [[P(i, j) for j in range(n + 1)] for i in range(n + 1)]
            for i in range(n):
                for j in range(n):
                    cs = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
                    fl.append([G[a][b] for a, b in cs]); ul.append([self.ruv(rects[fi], a / n, b / n) for a, b in cs])
        return self.polys(name, fl, ul, glow)

    def slab(self, name, rfn, h, rnd, rect_top, rect_side, rect_bot=None, nth=64, nc=6, ne=4, bulge=0.0, glow=False, z0=0.0):
        """Extruded rounded outline r = rfn(theta) (numpy-safe), thickness 2h, pillow bulge on the caps."""
        rect_bot = rect_bot or rect_top
        rows = [("bot", k / nc) for k in range(nc + 1)]
        rows += [("edge", -math.pi / 2 + math.pi / 2 * k / ne, -1) for k in range(ne + 1)]
        rows += [("edge", math.pi / 2 * k / ne, 1) for k in range(ne + 1)]
        rows += [("top", 1 - k / nc) for k in range(nc + 1)]
        e0 = nc + 1; ne_rows = 2 * (ne + 1)
        def rz(i, j):
            th = TAU * i / nth; r = float(rfn(th)); rw = rows[j]
            if rw[0] == "bot": return th, (r - rnd) * rw[1], -h - bulge * (1 - rw[1] ** 2)
            if rw[0] == "top": return th, (r - rnd) * rw[1], h + bulge * (1 - rw[1] ** 2)
            ph = rw[1]; return th, r - rnd + rnd * math.cos(ph), rw[2] * (h - rnd) + rnd * math.sin(ph)
        def P(i, j):
            th, rr, z = rz(i, j); return V(rr * math.cos(th), rr * math.sin(th), z + z0)
        ths = np.linspace(0, TAU, 721); rs = rfn(ths); xs, ys = rs * np.cos(ths), rs * np.sin(ths)
        bb = (xs.min(), xs.max(), ys.min(), ys.max())
        def uvf(i, j, fj):
            kind = rows[fj][0]
            if kind == "edge" and rows[fj + 1][0] != "edge": kind = rows[fj + 1][0]
            if kind == "edge":
                return self.ruv(rect_side, i / nth, (j - e0) / (ne_rows - 1))
            th, rr, z = rz(i, j); x, y = rr * math.cos(th), rr * math.sin(th)
            a, b = (x - bb[0]) / (bb[1] - bb[0]), (y - bb[2]) / (bb[3] - bb[2])
            return self.ruv(rect_top, a, b) if kind == "top" else self.ruv(rect_bot, 1 - a, b)
        ob = self.grid(name, P, nth, len(rows) - 1, uvf, glow)
        info = dict(bb=bb, rfn=rfn, h=h, rnd=rnd, bulge=bulge, z0=z0)
        info["ztop"] = lambda x, y: z0 + h + bulge * (1 - min(1.0, math.hypot(x, y) / max(1e-6, float(rfn(math.atan2(y, x))) - rnd)) ** 2)
        info["xy"] = lambda a, b: (bb[0] + a * (bb[1] - bb[0]), bb[2] + b * (bb[3] - bb[2]))
        return ob, info

    def loft(self, name, ctrl, rfn, rect=None, sw=0, K=12, sub=8, ref=V(0, 0, 1), prof=None, cap0=None, ext=(0.5, 0.5), glow=False):
        """Tube with frames. Angle 0 = ref side ('top'), +pi/2 = T x N. UV: along -> a, around -> b."""
        pts = catmull([Vector(p) for p in ctrl], sub); n = len(pts)
        seg = [0.0]
        for i in range(1, n): seg.append(seg[-1] + (pts[i] - pts[i - 1]).length)
        S = [x / seg[-1] for x in seg]
        T = [(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(n)]
        Ns = [(ref - T[0] * ref.dot(T[0])).normalized()]
        for i in range(1, n):
            ax = T[i - 1].cross(T[i]); nn = Ns[-1].copy()
            if ax.length > 1e-6: nn = Matrix.Rotation(T[i - 1].angle(T[i]), 3, ax.normalized()) @ nn
            nn = (nn - T[i] * nn.dot(T[i])).normalized(); Ns.append(nn)
        Bs = [T[i].cross(Ns[i]) for i in range(n)]
        R = [float(rfn(s)) for s in S]
        pf = prof or (lambda s, a: 1.0)
        def ring(i, a, out=0.0):
            return pts[i] + (R[i] * pf(S[i], a) + out) * (math.cos(a) * Ns[i] + math.sin(a) * Bs[i])
        p0 = pts[0] - T[0] * R[0] * ext[0]; p1 = pts[-1] + T[-1] * R[-1] * ext[1]
        def P(i, j):
            if j == 0: return p0
            if j == n + 1: return p1
            return ring(j - 1, TAU * i / K)
        def uvf(i, j, fj):
            if cap0 is not None and fj == 0:
                if j == 0: return self.ruv(cap0, 0.5, 0.5)
                a = TAU * i / K; return self.ruv(cap0, 0.5 + 0.48 * math.cos(a), 0.5 + 0.48 * math.sin(a))
            if rect is None: return self.uv_sw(sw)
            al = 0.0 if j == 0 else 1.0 if j == n + 1 else S[j - 1]
            return self.ruv(rect, al, i / K)
        ob = self.grid(name, P, K, n + 1, uvf, glow)
        lo = dict(pts=pts, T=T, N=Ns, B=Bs, R=R, S=S)
        def at(s, a, out=0.0):
            i = int(np.clip(np.searchsorted(S, s) - 1, 0, n - 2)); t = (s - S[i]) / max(S[i + 1] - S[i], 1e-9)
            P_ = pts[i].lerp(pts[i + 1], t); N_ = Ns[i].lerp(Ns[i + 1], t).normalized(); B_ = Bs[i].lerp(Bs[i + 1], t).normalized()
            r = lerp(R[i], R[i + 1], t) * pf(s, a) + out
            return P_ + r * (math.cos(a) * N_ + math.sin(a) * B_)
        def frame(s):
            i = int(np.clip(round(s * (n - 1)), 0, n - 1)); return pts[i], T[i], Ns[i], Bs[i]
        lo["at"], lo["frame"] = at, frame
        return ob, lo

    def strokes(self, name, paths, r, glow=True, sw=0, K=6, step=0.02):
        """Polylines (lists of Vectors) as tubes with sharp corners (resampled every `step`)."""
        for k, path in enumerate(paths):
            pts = [path[0]]
            for a, b in zip(path[:-1], path[1:]):
                m = max(2, int((b - a).length / step))
                pts += [a.lerp(b, (q + 1) / m) for q in range(m)]
            pts.append(pts[-1] + (pts[-1] - pts[-2]) * 0.3)
            self.tube(f"{name}{k}", pts, r, r, K=K, sub=1, sw=sw, glow=glow)

    def xform(self, M, objs=None):
        M4 = M.to_4x4() if len(M) == 3 else M
        for ob in (objs or self.parts + self.glow): ob.data.transform(M4)

    # ---- texture + export
    def bake(self, sw, strips=None, fins=None, base=c(128, 128, 128), ray=0.0):
        def pb(T, Vv, top):
            col = np.zeros(T.shape + (3,)) + base
            for (t0, v0, t1, v1), fn in self.regions:
                m = (T >= t0 - 0.012) & (T <= t1 + 0.012) & (Vv >= v0 - 0.024) & (Vv <= v1 + 0.024)
                a = np.clip((T[m] - t0) / (t1 - t0), 0, 1); b = np.clip((Vv[m] - v0) / (v1 - v0), 0, 1)
                col[m] = np.clip(fn(a, b), 0, 1)
            return col
        fins = fins or [[(0, c(200, 200, 200)), (1, c(255, 255, 255))]] * self.fin_styles
        strips = strips or [(c(128, 128, 128), c(200, 200, 200), 1.0)] * 2
        self.texture(pb, fins, strips, sw, ray_strength=ray)

    def done(self, glow=None, k=1.0, scale=1.0, yaw=0.0):
        """yaw turns long items across the hero camera; the camera distance follows the item's extent."""
        if yaw: self.xform(Matrix.Rotation(yaw, 4, "Z"))
        if scale != 1.0: self.xform(Matrix.Scale(scale, 4))
        pts = np.array([v.co[:] for ob in self.parts + self.glow for v in ob.data.vertices])
        d = pts.max(0) - pts.min(0)
        cam = max(0.28 * d[2], 0.2 * max(d[0], d[1]))
        self.finish(bend=0.0, glow_color=glow, views=VIEWS, cam_scale=cam * k, rig=False)


def eye(f, nm, C, n, re, sw_white, sw_pupil, pupil_k=0.6):
    """Cartoon eye: white ball, big pupil, glint."""
    Bm = basis(n)
    f.sphere(f"Eye{nm}", C, Bm, (re,) * 3, sw_white, 14, 10)
    f.sphere(f"Pupil{nm}", C + n * re * 0.55, Bm, (re * 0.5, re * pupil_k, re * pupil_k), sw_pupil, 12, 8)
    hl = (n + Bm.col[2] * 0.6 + V(0.2, -0.2, 0)).normalized()
    f.sphere(f"Glint{nm}", C + hl * re * 1.0, Bm, (re * 0.2,) * 3, sw_white, 8, 6)


# ====================================================================== COMMON
def bread_crumbs():
    f = Bait("BreadCrumbs", "Common")
    CR, CB = (0.02, 0.04, 0.46, 0.96), (0.52, 0.04, 0.98, 0.96)
    def crust(a, b):
        x, y = a * 4, b * 2.2
        col = mix(solid(a, c(222, 158, 66)), c(168, 98, 38), smooth(0.45, 0.72, fbm(x, y, 3, 1)))
        col = mix(col, c(244, 196, 112), 0.6 * smooth(0.6, 0.8, fbm(x, y, 8, 5)))
        return mix(col, c(120, 66, 26), 0.5 * smooth(0.82, 0.9, vnoise(x, y, 18, 9)))
    def crumb(a, b):
        x, y = a * 4, b * 2.2
        col = mix(solid(a, c(252, 244, 222)), c(240, 222, 186), fbm(x, y, 4, 3) * 0.8)
        pore = smooth(0.7, 0.8, vnoise(x, y, 22, 11)) + smooth(0.74, 0.84, vnoise(x + 3, y, 34, 12))
        return mix(col, c(214, 188, 140), pore * 0.7)
    f.region(CR, crust); f.region(CB, crumb)
    chunks = [((0.06, 0.13, 0.12), (0.18, 0.13, 0.12), (0.1, 0.05, 0.4), 3),
              ((-0.17, -0.1, 0.11), (0.15, 0.14, 0.11), (-0.1, 0.12, -0.3), 0),
              ((0.21, -0.15, 0.1), (0.13, 0.12, 0.1), (0.05, -0.1, 0.9), 3),
              ((-0.01, -0.03, 0.31), (0.14, 0.12, 0.11), (0.3, -0.2, 0.25), 0)]
    for k, (C, half, eu, crumb_face) in enumerate(chunks):
        rects = [CR] * 6; rects[crumb_face] = CB
        if k == 3: rects[3] = CB
        cf = crumb_face
        def deform(p, nn, k=k, cf=cf):
            torn = abs(nn[[0, 0, 1, 1, 2, 2][cf]]) > 0.7 and nn[[0, 0, 1, 1, 2, 2][cf]] * (1 if cf % 2 == 0 else -1) > 0
            return p + nn * ((0.028 if torn else 0.012) * n3(p, 14 if torn else 9, k))
        f.rbox(f"Chunk{k}", V(*C), E(*eu), half, 0.05, 7, rects, deform)
    rng = np.random.default_rng(4)
    for k in range(6):
        a = rng.uniform(0, TAU); d = rng.uniform(0.33, 0.42); s = rng.uniform(0.025, 0.045)
        f.ell(f"Crumb{k}", V(d * math.cos(a), d * math.sin(a), s * 0.7), E(*rng.uniform(0, 3, 3)), (s, s * 0.8, s * 0.7),
              CB if k % 2 else CR, nu=8, nv=6, deform=lambda p, k=k: p * (1 + 0.25 * n3(p, 5, k)))
    f.bake({0: c(200, 140, 60)})
    f.done(scale=0.9)

def worm_rfn(r0, N, cl=None):
    env = lambda s: float(pchip([0, 0.06, 0.25, 0.85, 0.96, 1], [0.3, 0.7, 1, 0.96, 0.75, 0.45], s))
    def rfn(s):
        g = abs(math.sin(math.pi * s * N)) ** 0.6
        band = 0.16 * smooth(0.06, 0.0, abs(s - cl) - 0.05) if cl else 0.0
        return r0 * env(s) * (0.92 + 0.08 * g + band)
    return rfn

def earthworm():
    f = Bait("Earthworm", "Common")
    RW = (0.02, 0.04, 0.98, 0.96); N, CL = 34, 0.7
    def paint(a, b):
        top = np.cos(TAU * b)
        col = mix(solid(a, c(226, 156, 146)), c(176, 92, 88), smooth(-0.6, 0.7, top))
        col = mix(col, c(150, 74, 74), 0.35 * fbm(a * 8, b * 2, 3, 2))
        groove = smooth(0.12, 0.0, np.abs(((a * N) % 1.0) - 0.0)) + smooth(0.88, 1.0, (a * N) % 1.0)
        col = col * (1 - 0.28 * np.clip(groove, 0, 1))[..., None]
        cl = smooth(0.05, 0.03, np.abs(a - CL))
        return mix(col, mix(solid(a, c(244, 168, 140)), c(214, 120, 104), smooth(-0.5, 0.8, top)), cl)
    f.region(RW, paint)
    ctrl = [V(-0.46, 0.08, 0.05), V(-0.33, -0.1, 0.05), V(-0.12, -0.13, 0.05), V(0.04, 0.06, 0.055),
            V(0.2, 0.15, 0.06), V(0.36, 0.05, 0.08), V(0.44, -0.08, 0.17), V(0.42, -0.14, 0.27)]
    f.loft("Worm", ctrl, worm_rfn(0.052, N, CL), RW, K=10, sub=20)
    f.bake({0: c(200, 120, 110)})
    f.done(scale=0.8, yaw=math.radians(45))

def corn_kernels():
    f = Bait("CornKernels", "Common")
    RK = (0.02, 0.04, 0.98, 0.96)
    def paint(a, b):
        col = mix(solid(a, c(255, 204, 30)), c(246, 150, 12), smooth(0.35, 0.65, b) * (1 - smooth(0.78, 0.92, b)) * 0.75)
        col = mix(col, c(255, 230, 96), smooth(0.86, 0.98, b) * 0.8)
        col = mix(col, c(255, 246, 196), 0.55 * np.exp(-((((a - 0.12) % 1.0) - 0.5) / 0.05) ** 2) * smooth(0.35, 0.6, b))
        col = mix(col, c(250, 238, 200), smooth(0.36, 0.24, b))
        return mix(col, c(214, 176, 112), smooth(0.1, 0.0, b))
    f.region(RK, paint)
    def kern(p):
        z = p.z; w = 0.3 + 0.7 * float(smooth(-1.0, 0.25, z))
        z2 = z if z < 0.35 else 0.35 + (z - 0.35) * 0.45
        sq = 1 + 0.18 * (1 - p.x * p.x) * float(smooth(-0.2, 0.4, z))
        return V(p.x * w * sq, p.y * w, z2 - 0.1 * (1 - p.x * p.x) * float(smooth(0.6, 1.0, z)))
    for k, (C, ax, hint) in enumerate([(V(0.0, 0.05, 0.2), V(-0.15, 0.2, 1), V(1, 1, 0)),
                                        (V(-0.12, -0.12, 0.13), V(-0.55, -0.6, 0.6), V(1, -1, 0.5)),
                                        (V(0.13, -0.08, 0.12), V(0.75, -0.25, 0.55), V(1, 1, 0))]):
        f.ell(f"Kernel{k}", C - Vector(ax).normalized() * 0.06, fz(ax, hint), (0.16, 0.075, 0.17), RK, nu=24, nv=16, deform=kern)
    f.bake({0: c(250, 200, 40)})
    f.done(scale=1.2)

# ====================================================================== UNCOMMON
def cricket():
    f = Bait("Cricket", "Uncommon")
    RA, RT, RH = (0.02, 0.04, 0.46, 0.96), (0.52, 0.04, 0.74, 0.96), (0.78, 0.04, 0.98, 0.96)
    WHITE, PUP, DARK, LEG = 0, 1, 2, 3
    def abdo(a, b):
        top = np.cos(TAU * a)
        col = mix(solid(a, c(176, 118, 60)), c(96, 58, 28), smooth(-0.3, 0.7, top))
        band = np.exp(-(((b * 7) % 1.0 - 0.5) / 0.12) ** 2) * smooth(0.15, 0.25, b)
        return mix(col, c(60, 36, 18), band * 0.6)
    def thor(a, b):
        top = np.cos(TAU * a)
        col = mix(solid(a, c(150, 96, 46)), c(84, 50, 24), smooth(-0.2, 0.8, top))
        return mix(col, c(200, 150, 90), 0.5 * smooth(0.3, 0.1, np.abs(b - 0.62)) * smooth(0.0, 0.5, top))
    def head(a, b):
        top = np.cos(TAU * a)
        return mix(solid(a, c(196, 146, 84)), c(80, 48, 22), smooth(0.0, 0.7, top))
    f.region(RA, abdo); f.region(RT, thor); f.region(RH, head)
    f.ell("Abdomen", V(-0.15, 0, 0.17), fz(V(-1, 0, 0.12)), (0.11, 0.12, 0.21), RA, nu=20, nv=14)
    f.ell("Thorax", V(0.08, 0, 0.2), fz(V(1, 0, 0.1)), (0.1, 0.105, 0.11), RT, nu=20, nv=12)
    f.ell("Head", V(0.24, 0, 0.22), fz(V(1, 0, -0.5)), (0.1, 0.095, 0.115), RH, nu=20, nv=12)
    for sd in (1, -1):
        n = V(0.55, sd * 0.8, 0.25).normalized()
        eye(f, f"_{sd}", V(0.27, sd * 0.065, 0.28), n, 0.052, WHITE, PUP)
        f.tube(f"Mandible{sd}", [V(0.32, sd * 0.03, 0.15), V(0.35, sd * 0.02, 0.11), V(0.34, sd * 0.01, 0.08)], 0.014, 0.005, K=6, sub=3, sw=DARK)
        f.tube(f"Antenna{sd}", [V(0.3, sd * 0.035, 0.31), V(0.38, sd * 0.09, 0.47), V(0.31, sd * 0.19, 0.63),
                                V(0.08, sd * 0.29, 0.71), V(-0.18, sd * 0.36, 0.66)], 0.012, 0.004, K=6, sub=6, sw=DARK)
        f.fin(f"Wing{sd}", lambda s, sd=sd: V(lerp(0.04, -0.36, s), sd * 0.015, lerp(0.295, 0.27, s)),
              lambda s, sd=sd: V(-0.12, sd * 1, -0.6), lambda s: 0.135 * math.sin(math.pi * (0.12 + 0.86 * s)) ** 0.5,
              lambda s, r: V(0, 0, -0.035 * r * r), 8, 4, 0.012, 0)
        f.tube(f"Femur{sd}", [V(-0.03, sd * 0.1, 0.14), V(-0.13, sd * 0.16, 0.24), V(-0.25, sd * 0.18, 0.34)], 0, 0, strip=0, K=8, sub=5,
               rfn=lambda s: float(pchip([0, 0.35, 1], [0.042, 0.05, 0.02], s)))
        f.tube(f"Tibia{sd}", [V(-0.25, sd * 0.18, 0.34), V(-0.34, sd * 0.2, 0.19), V(-0.43, sd * 0.21, 0.02)], 0.017, 0.012, K=6, sub=4, sw=LEG)
        for q in range(3):
            p = V(-0.25, sd * 0.18, 0.34).lerp(V(-0.43, sd * 0.21, 0.02), 0.3 + 0.22 * q)
            f.tube(f"Spike{sd}_{q}", [p, p + V(-0.03, sd * 0.01, 0.0), p + V(-0.055, sd * 0.015, 0.012)], 0.008, 0.002, K=4, sub=2, sw=DARK)
        f.tube(f"Foot{sd}", [V(-0.43, sd * 0.21, 0.02), V(-0.37, sd * 0.215, 0.012), V(-0.3, sd * 0.22, 0.014)], 0.012, 0.006, K=5, sub=3, sw=LEG)
        f.tube(f"MidLeg{sd}", [V(0.03, sd * 0.08, 0.13), V(0.0, sd * 0.2, 0.13), V(-0.06, sd * 0.26, 0.01), V(-0.02, sd * 0.3, 0.0)], 0.015, 0.008, K=5, sub=4, sw=LEG)
        f.tube(f"FrontLeg{sd}", [V(0.13, sd * 0.07, 0.13), V(0.19, sd * 0.17, 0.12), V(0.25, sd * 0.21, 0.01), V(0.3, sd * 0.22, 0.0)], 0.015, 0.008, K=5, sub=4, sw=LEG)
        f.tube(f"Cercus{sd}", [V(-0.33, sd * 0.03, 0.19), V(-0.42, sd * 0.07, 0.21), V(-0.5, sd * 0.1, 0.24)], 0.011, 0.003, K=5, sub=3, sw=DARK)
    f.bake({WHITE: c(255, 255, 255), PUP: c(16, 12, 10), DARK: c(60, 36, 18), LEG: c(150, 100, 52)},
           strips=[(c(100, 62, 30), c(196, 146, 84), 1.0)] * 2,
           fins=[[(0, c(120, 76, 36)), (0.6, c(170, 120, 66)), (1, c(214, 176, 120))]], ray=0.45)
    f.done(scale=1.1)

def shrimp():
    f = Bait("Shrimp", "Uncommon")
    RB = (0.02, 0.04, 0.98, 0.96); BLK, WHITE, LEG, ANT = 0, 1, 2, 3
    NS = 6
    def paint(a, b):
        top = np.cos(TAU * b)
        col = mix(solid(a, c(255, 196, 166)), c(246, 116, 74), smooth(-0.5, 0.6, top))
        col = mix(col, c(226, 70, 50), 0.6 * smooth(0.75, 0.98, a) * smooth(-0.3, 0.5, top))
        segp = np.clip((a - 0.32) / 0.62, 0, 1) * NS
        seam = np.exp(-((segp % 1.0) / 0.07) ** 2) * (a > 0.33) * (a < 0.95)
        col = mix(col, c(200, 70, 50), seam * 0.65)
        col = mix(col, c(255, 226, 206), np.exp(-(((segp % 1.0) - 0.2) / 0.1) ** 2) * (a > 0.33) * (a < 0.95) * 0.5)
        col = mix(col, c(190, 60, 40), 0.45 * np.exp(-((b - 0.0) / 0.03) ** 2) + 0.45 * np.exp(-((b - 1.0) / 0.03) ** 2))
        return mix(col, c(250, 150, 110), 0.3 * smooth(0.6, 0.8, fbm(a * 6, b * 2, 6, 3)) * (a < 0.32))
    f.region(RB, paint)
    def rfn(s):
        base = float(pchip([0, 0.05, 0.18, 0.32, 0.5, 0.8, 1.0], [0.08, 0.115, 0.125, 0.11, 0.095, 0.065, 0.04], s))
        if 0.32 < s < 0.95: base *= 0.95 + 0.05 * abs(math.sin(math.pi * (s - 0.32) / 0.62 * NS)) ** 0.5
        return base
    ctrl = [V(0.42, 0, 0.2), V(0.25, 0, 0.31), V(0.05, 0, 0.36), V(-0.15, 0, 0.32), V(-0.28, 0, 0.19),
            V(-0.28, 0, 0.07), V(-0.17, 0, 0.02)]
    ob, lo = f.loft("Body", ctrl, rfn, RB, K=12, sub=10, ref=V(0, 0, 1), ext=(0.9, 0.3))
    P0, T0, N0, B0 = lo["frame"](0.0); front = P0 - T0 * 0.09
    f.tube("Rostrum", [front + N0 * 0.04 - T0 * 0.0, front + N0 * 0.06 - T0 * 0.1, front + N0 * 0.09 - T0 * 0.2], 0.022, 0.003, K=6, sub=4, sw=LEG)
    for sd in (1, -1):
        ang = sd * 1.1
        base = lo["at"](0.05, ang); out = (lo["at"](0.05, ang, 1.0) - base).normalized()
        ec = base + out * 0.045 - T0 * 0.03
        f.tube(f"Stalk{sd}", [base - out * 0.01, base + out * 0.02 - T0 * 0.015, ec], 0.018, 0.016, K=6, sub=3, sw=LEG)
        f.sphere(f"Eye{sd}", ec, basis(out), (0.032,) * 3, BLK, 12, 8)
        f.sphere(f"Glint{sd}", ec + (out + V(0, 0, 0.8)).normalized() * 0.03, basis(out), (0.008,) * 3, WHITE, 6, 4)
        a0 = front + B0 * sd * 0.03 + N0 * 0.01
        f.tube(f"Antenna{sd}", [a0, a0 + V(0.1, sd * 0.05, 0.06), a0 + V(0.12, sd * 0.13, 0.28), a0 + V(-0.06, sd * 0.2, 0.46),
                                a0 + V(-0.36, sd * 0.24, 0.47), a0 + V(-0.6, sd * 0.22, 0.38)], 0.011, 0.003, K=5, sub=6, sw=ANT)
        f.tube(f"Antennule{sd}", [a0, a0 + V(0.09, sd * 0.06, 0.0), a0 + V(0.15, sd * 0.1, 0.04)], 0.009, 0.003, K=5, sub=3, sw=ANT)
        for q, s in enumerate(np.linspace(0.08, 0.26, 4)):
            b = lo["at"](float(s), math.pi - sd * 0.45, -0.01)
            f.tube(f"Leg{sd}_{q}", [b, b + V(0.03, sd * 0.05, -0.06), V(b.x + 0.07 - 0.02 * q, b.y + sd * 0.08, 0.005)], 0.011, 0.005, K=5, sub=3, sw=LEG)
        for q, s in enumerate(np.linspace(0.4, 0.8, 5)):
            b = lo["at"](float(s), math.pi - sd * 0.35, -0.01); o = (lo["at"](float(s), math.pi - sd * 0.35, 1) - b).normalized()
            _, Tq, _, _ = lo["frame"](float(s))
            f.tube(f"Swim{sd}_{q}", [b, b + o * 0.035 - Tq * 0.01, b + o * 0.06 - Tq * 0.03], 0.012, 0.004, K=5, sub=3, sw=LEG)
    P1, T1, N1, B1 = lo["frame"](1.0)
    for k, ang in enumerate([-1.0, -0.5, 0.0, 0.5, 1.0]):
        d = T1 * math.cos(ang) + B1 * math.sin(ang); Lk = 0.16 if k == 2 else 0.14
        f.fin(f"Fan{k}", lambda s, B1=B1, P1=P1: P1 + B1 * (s - 0.5) * 0.035 - T1 * 0.02, lambda s, d=d: d,
              lambda s, Lk=Lk: Lk * math.sin(math.pi * (0.08 + 0.84 * s)) ** 0.6, lambda s, r: N1 * 0.02 * r * r, 6, 4, 0.012, 0)
    f.bake({BLK: c(14, 12, 16), WHITE: c(255, 255, 255), LEG: c(248, 140, 100), ANT: c(232, 96, 66)},
           fins=[[(0, c(246, 120, 80)), (0.65, c(232, 70, 50)), (0.85, c(255, 170, 140)), (1, c(255, 236, 226))]], ray=0.3)
    f.done()

def spinner_lure():
    f = Bait("SpinnerLure", "Uncommon")
    RBL, RBO = (0.02, 0.04, 0.6, 0.96), (0.66, 0.04, 0.98, 0.96)
    SIL, RED, GOLD, THREAD, BLACK = 0, 1, 2, 3, 4
    def blade(a, b):
        s = a * 0.7 + b
        col = mix(solid(a, c(236, 186, 70)), c(255, 250, 214), np.exp(-((s - 0.8) / 0.09) ** 2))
        col = mix(col, c(150, 96, 26), 0.8 * np.exp(-((s - 1.25) / 0.1) ** 2))
        col = mix(col, c(255, 236, 160), 0.6 * np.exp(-((s - 0.35) / 0.06) ** 2))
        col = mix(col, c(190, 136, 40), 0.25 * smooth(0.5, 0.8, vnoise(a * 4, b * 2, 9, 3)))
        return mix(col, c(255, 244, 200), smooth(0.4, 0.5, np.abs(b - 0.5)) * 0.6)
    def body(a, b):
        top = np.cos(TAU * a)
        col = mix(solid(a, c(206, 152, 52)), c(255, 236, 170), np.exp(-((top - 0.85) / 0.25) ** 2))
        col = mix(col, c(120, 80, 20), smooth(-0.3, -0.9, top))
        bands = smooth(0.02, 0.0, np.abs(b - 0.55) - 0.07) + smooth(0.015, 0.0, np.abs(b - 0.35) - 0.02)
        return mix(col, c(214, 30, 40), bands)
    f.region(RBL, blade); f.region(RBO, body)
    Z = 0.3; A = lambda x: V(x, 0, Z)
    f.torus("EyeLoop", A(0.61), V(0, 1, 0), 0.045, 0.009, SIL, 16, 6)
    f.tube("Wire", [A(0.565), A(0.3), A(-0.32)], 0.009, 0.009, K=6, sub=2, sw=SIL)
    f.torus("Clevis", A(0.48), V(1, 0, 0), 0.022, 0.007, SIL, 12, 5)
    Q0, Q1 = V(0.47, -0.035, Z), V(0.06, -0.13, Z + 0.02)
    dX = (Q1 - Q0).normalized(); dW = V(0, -0.3, 0.95).normalized(); dW = (dW - dX * dW.dot(dX)).normalized(); dN = dX.cross(dW)
    L = (Q1 - Q0).length
    def BP(i, j):
        u, v = i / 10, -1 + 2 * j / 6
        w = 0.14 * math.sin(math.pi * min(1.0, u ** 0.8)) ** 0.7
        return Q0 + dX * (u * L) + dW * (v * w) + dN * (0.035 * (1 - v * v) * math.sin(math.pi * u))
    bl = f.grid("Blade", BP, 10, 6, lambda i, j, fj: f.ruv(RBL, i / 10, j / 6)); f.solidify(bl, 0.012)
    f.sphere("BeadA", A(0.4), Matrix.Identity(3), (0.032,) * 3, RED, 12, 8)
    f.sphere("BeadB", A(0.345), Matrix.Identity(3), (0.026,) * 3, GOLD, 12, 8)
    f.ell("Body", A(0.19), fz(V(-1, 0, 0)), (0.05, 0.05, 0.12), RBO, nu=16, nv=12,
          deform=lambda p: V(p.x, p.y, p.z) * (1.0 if p.z < 0 else 1 - 0.25 * p.z * p.z))
    f.sphere("BeadC", A(0.04), Matrix.Identity(3), (0.03,) * 3, RED, 12, 8)
    f.torus("Collar", A(-0.3), V(1, 0, 0), 0.022, 0.014, THREAD, 12, 6)
    for k, psi in enumerate([-math.pi / 2, math.pi / 6, 5 * math.pi / 6]):
        e = V(0, math.cos(psi), math.sin(psi)); A2 = lambda x, d=0.0: V(x, 0, Z) + e * d
        pts = [A2(-0.3), A2(-0.55), A2(-0.64, 0.035), A2(-0.645, 0.1), A2(-0.58, 0.135), A2(-0.52, 0.105)]
        f.tube(f"Hook{k}", pts, 0.011, 0.004, K=6, sub=4, sw=SIL, pw=3)
        tip = A2(-0.53, 0.11)
        f.tube(f"Barb{k}", [tip, tip + V(-0.025, 0, 0) - e * 0.02, tip + V(-0.04, 0, 0) - e * 0.03], 0.006, 0.002, K=4, sub=2, sw=SIL)
    for k in range(9):
        psi = TAU * k / 9 + 0.2; e = V(0, math.cos(psi), math.sin(psi)); side_ = V(1, 0, 0).cross(e)
        dvec = (V(-1, 0, 0) * 0.85 + e * 0.42).normalized(); b0 = A(-0.3) + e * 0.012
        f.fin(f"Feather{k}", lambda s, b0=b0, side_=side_: b0 + side_ * (s - 0.5) * 0.05, lambda s, dvec=dvec: dvec,
              lambda s, k=k: (0.34 + 0.04 * (k % 3)) * math.sin(math.pi * (0.06 + 0.88 * s)) ** 0.7,
              lambda s, r, e=e: e * 0.06 * r * r, 6, 5, 0.008, 0)
    f.bake({SIL: c(214, 220, 230), RED: c(220, 30, 40), GOLD: c(240, 196, 70), THREAD: c(30, 24, 26), BLACK: c(20, 20, 20)},
           fins=[[(0, c(150, 10, 22)), (0.35, c(222, 34, 40)), (0.8, c(255, 90, 76)), (1, c(255, 190, 170))]], ray=0.4)
    f.done(scale=0.85, yaw=math.radians(40))


# ====================================================================== RARE
def squid_chunk():
    f = Bait("SquidChunk", "Rare")
    RS, RC = (0.02, 0.04, 0.74, 0.96), (0.78, 0.2, 0.98, 0.8)
    RIM, CUP = 0, 1; AV = math.pi / 2 + 0.35
    def skin(a, b):
        ang = TAU * b
        under = smooth(0.0, 0.35, np.cos(ang - AV))
        col = mix(solid(a, c(150, 62, 150)), c(206, 120, 196), 0.5 * fbm(a * 10, b * 3, 3, 4))
        spots = smooth(0.62, 0.7, vnoise(a * 10, b * 3, 5, 9)); col = mix(col, c(90, 26, 96), spots * 0.8)
        col = mix(col, c(250, 236, 244), under)
        return mix(col, c(236, 190, 230), np.exp(-((np.cos(ang - AV) - 0.0) / 0.12) ** 2) * 0.6)
    def flesh(a, b):
        r = np.hypot(a - 0.5, b - 0.5) / 0.48
        col = mix(solid(a, c(252, 240, 240)), c(250, 206, 214), 0.5 + 0.5 * np.sin(r * 22))
        col = mix(col, c(220, 120, 150), smooth(0.25, 0.1, r))
        return mix(col, c(160, 70, 150), smooth(0.86, 0.98, r))
    f.region(RS, skin); f.region(RC, flesh)
    ctrl = [V(-0.42, 0, 0.17), V(-0.18, 0, 0.19), V(0.06, 0, 0.19), V(0.27, 0, 0.23), V(0.4, 0, 0.36), V(0.37, 0, 0.51),
            V(0.25, 0, 0.56), V(0.17, 0, 0.47), V(0.22, 0, 0.39), V(0.29, 0, 0.42)]
    rfn = lambda s: 0.165 * (1 - s) ** 0.85 + 0.018
    prof = lambda s, a: 1.0 - 0.12 * max(0.0, math.cos(a - AV)) ** 2
    ob, lo = f.loft("Tentacle", ctrl, rfn, RS, K=12, sub=7, ref=V(0, 0, 1), prof=prof, cap0=RC, ext=(0.0, 0.6))
    k = 0
    for row, da in ((0, -0.32), (1, 0.32)):
        for q in range(8):
            s = 0.06 + 0.1 * q + 0.05 * row
            if s > 0.86: continue
            r = rfn(s) * 0.36; a = AV + da
            p = lo["at"](s, a, -0.004); nrm = (lo["at"](s, a, 1.0) - lo["at"](s, a, 0.0)).normalized()
            f.torus(f"Sucker{k}", p + nrm * r * 0.15, nrm, r * 0.75, r * 0.35, RIM, 10, 5)
            f.sphere(f"Cup{k}", p + nrm * r * 0.05, basis(nrm), (r * 0.2, r * 0.6, r * 0.6), CUP, 8, 6); k += 1
    f.bake({RIM: c(250, 220, 236), CUP: c(200, 110, 160)})
    f.done(scale=1.15)

def glow_worm():
    f = Bait("GlowWorm", "Rare")
    RW = (0.02, 0.04, 0.98, 0.96); N = 30
    rng = np.random.default_rng(8)
    spots = []
    for q, s in enumerate(np.arange(0.1, 0.93, 0.064)):
        for sd in (1, -1):
            spots.append((float(s + (0.032 if sd < 0 else 0)), sd * (math.pi / 2 + rng.uniform(-0.2, 0.2))))
    def paint(a, b):
        top = np.cos(TAU * b)
        col = mix(solid(a, c(70, 56, 120)), c(22, 22, 52), smooth(-0.5, 0.6, top))
        col = mix(col, c(40, 30, 80), 0.4 * fbm(a * 8, b * 2, 3, 2))
        groove = smooth(0.12, 0.0, (a * N) % 1.0) + smooth(0.88, 1.0, (a * N) % 1.0)
        col = col * (1 - 0.35 * np.clip(groove, 0, 1))[..., None]
        halo = np.zeros_like(a)
        for s, ang in spots:
            db = ((b - (ang / TAU) % 1.0 + 0.5) % 1.0) - 0.5
            halo = np.maximum(halo, np.exp(-(((a - s) * 18) ** 2 + (db * 12) ** 2)))
        halo = np.maximum(halo, smooth(0.12, 0.0, a) * 0.8)
        return mix(col, c(60, 200, 220), halo * 0.75)
    f.region(RW, paint)
    ctrl = [V(-0.5, 0.12, 0.06), V(-0.32, -0.08, 0.06), V(-0.08, -0.13, 0.065), V(0.1, 0.06, 0.07), V(0.27, 0.14, 0.11),
            V(0.4, 0.02, 0.28), V(0.36, -0.1, 0.46), V(0.27, -0.15, 0.53)]
    rfn = worm_rfn(0.06, N)
    ob, lo = f.loft("Worm", ctrl, rfn, RW, K=10, sub=18)
    for k, (s, ang) in enumerate(spots):
        p = lo["at"](s, ang, -0.008); nrm = (lo["at"](s, ang, 1.0) - lo["at"](s, ang, 0.0)).normalized()
        rr = 0.022 * (0.7 + 0.3 * math.sin(math.pi * s))
        f.sphere(f"Spot{k}", p, basis(nrm), (0.014, rr, rr), 0, 8, 6, glow=True)
    P0, T0, _, _ = lo["frame"](0.0)
    f.sphere("TailGlow", P0 + T0 * 0.005, basis(T0), (0.07, 0.036, 0.036), 0, 12, 8, glow=True)
    p, Tm, _, _ = lo["frame"](0.74)
    f.torus("GlowBand", p, Tm, rfn(0.74) + 0.002, 0.011, 0, 18, 5, glow=True)
    f.bake({0: c(40, 30, 80)})
    f.done(glow=c(80, 240, 255), scale=1.1, yaw=math.radians(45))

def krill_painter(seed):
    rng = np.random.default_rng(seed); asp = 0.75
    kr = []
    for q in range(rng.integers(2, 4)):
        kr.append((rng.uniform(0.28, 0.72), rng.uniform(0.25, 0.75) * asp, rng.uniform(0, TAU), rng.uniform(0.2, 0.28), rng.uniform(0.6, 0.85)))
    def paint(a, b):
        x, y = a, b * asp
        e = np.minimum(np.minimum(a, 1 - a), np.minimum(b, 1 - b) * asp)
        col = mix(solid(a, c(150, 206, 240)), c(196, 234, 252), smooth(0.3, 0.05, e))
        col = mix(col, c(120, 186, 230), 0.4 * fbm(x * 3, y * 3, 2, seed))
        for (cx, cy, rot, sz, dep) in kr:
            best = np.full(a.shape, 9.0); bi = np.zeros(a.shape)
            for i in range(22):
                t = i / 21; th = rot + t * 3.6
                px, py = cx + 0.5 * sz * math.cos(th), cy + 0.5 * sz * math.sin(th)
                w = sz * (0.16 - 0.1 * t)
                d = np.hypot(x - px, y - py) - w
                bi = np.where(d < best, t, bi); best = np.minimum(best, d)
            ins = smooth(0.006, -0.004, best)
            kc = mix(solid(a, c(250, 140, 130)), c(214, 70, 76), np.exp(-(((bi * 7) % 1.0 - 0.5) / 0.15) ** 2) * 0.7)
            kc = mix(kc, c(255, 200, 190), smooth(-0.012, -0.03, best) * 0.4)
            hx, hy = cx + 0.5 * sz * math.cos(rot) + 0.04 * sz * math.cos(rot + 1.5), cy + 0.5 * sz * math.sin(rot) + 0.04 * sz * math.sin(rot + 1.5)
            kc = mix(kc, c(20, 16, 24), smooth(0.022 * sz / 0.25, 0.012 * sz / 0.25, np.hypot(x - hx, y - hy)))
            th0 = rot - 0.2
            ant = seg_dist(x, y, (cx + 0.5 * sz * math.cos(rot), cy + 0.5 * sz * math.sin(rot)),
                           (cx + 0.5 * sz * math.cos(rot) + 0.3 * sz * math.cos(th0 - 1.2), cy + 0.5 * sz * math.sin(rot) + 0.3 * sz * math.sin(th0 - 1.2)))
            ins2 = smooth(0.005, 0.002, ant)
            kc = mix(kc, c(200, 80, 80), ins2)
            m = np.maximum(ins, ins2) * dep
            col = mix(col, kc * 0.82 + c(150, 206, 240) * 0.18, m)
        crack = smooth(0.012, 0.0, np.abs(fbm(x * 2, y * 2, 2.5, seed + 7) - 0.5)) * smooth(0.25, 0.1, e + 0.1 * vnoise(x, y, 4, seed))
        col = mix(col, c(236, 248, 255), crack * 0.8)
        bub = smooth(0.82, 0.86, vnoise(x, y, 16, seed + 3)); col = mix(col, c(230, 246, 255), bub * 0.6)
        frost = smooth(0.11, 0.02, e + 0.05 * (fbm(x, y, 12, seed + 5) - 0.5))
        return mix(col, c(244, 251, 255), frost)
    return paint

def frozen_krill():
    f = Bait("FrozenKrill", "Rare")
    rects = []
    for r in range(2):
        for q in range(3):
            rect = (0.02 + q * 0.33, 0.03 + r * 0.5, 0.31 + q * 0.33, 0.47 + r * 0.5); rects.append(rect)
            f.region(rect, krill_painter(20 + 3 * r + q))
    FROST, SHARD, PINK, BLK, WHITE = 0, 1, 2, 3, 4
    C = V(0, 0, 0.36); Rb = E(0.1, -0.07, 0.12)
    f.rbox("Ice", C, Rb, (0.34, 0.34, 0.32), 0.07, 9, rects, deform=lambda p, nn: p + nn * 0.006 * n3(p, 11))
    corners = [Rb @ V(sx * 0.31, sy * 0.31, 0.3) + C for sx, sy in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    rng = np.random.default_rng(5)
    for k, p in enumerate(corners):
        for q in range(2):
            ax = (p - C).normalized() + V(*rng.uniform(-0.4, 0.4, 3)); ax.z += 0.6
            f.gem(f"Frost{k}_{q}", p + ax.normalized() * 0.02, fz(ax), (0.022, 0.022, 0.07 + 0.03 * q), FROST)
    for k in range(5):
        a = TAU * k / 5 + 0.4; p = V(0.5 * math.cos(a), 0.5 * math.sin(a), 0.03)
        f.gem(f"Shard{k}", p, fz(V(math.cos(a) * 0.5, math.sin(a) * 0.5, 1)), (0.035, 0.03, 0.07), SHARD)
    top = Rb @ V(0.08, -0.12, 0.3) + C
    kp = [top + V(-0.06, 0.04, -0.06), top + V(0.0, 0.0, 0.0), top + V(0.06, -0.03, 0.07), top + V(0.15, -0.05, 0.1)]
    f.tube("KrillBody", kp, 0, 0, strip=0, K=8, sub=6, rfn=lambda s: 0.034 * (1 - 0.35 * s) * (0.92 + 0.08 * abs(math.sin(s * 18))))
    hd = kp[-1]; d = (kp[-1] - kp[-2]).normalized()
    for sd in (1, -1):
        ec = hd + V(0, sd * 0.025, 0.018)
        f.sphere(f"KrillEye{sd}", ec, Matrix.Identity(3), (0.014,) * 3, BLK, 8, 6)
        f.tube(f"KrillAnt{sd}", [hd + d * 0.02, hd + d * 0.08 + V(0, sd * 0.03, 0.05), hd + d * 0.12 + V(0, sd * 0.07, 0.12)], 0.005, 0.002, K=4, sub=3, sw=PINK)
    f.bake({FROST: c(240, 250, 255), SHARD: c(176, 222, 248), PINK: c(240, 120, 110), BLK: c(16, 14, 20), WHITE: c(255, 255, 255)},
           strips=[(c(236, 100, 96), c(255, 176, 160), 1.0)] * 2)
    f.done()


# ====================================================================== EPIC
def raw_steak():
    f = Bait("RawSteak", "Epic")
    RT, RSD = (0.02, 0.04, 0.62, 0.96), (0.68, 0.04, 0.98, 0.96)
    BONE, BLOOD, MARROW = 0, 1, 2
    def rfn(th):
        re_ = 1 / np.sqrt((np.cos(th) / 0.55) ** 2 + (np.sin(th) / 0.42) ** 2)
        return re_ * (1 + 0.07 * np.cos(2 * th + 0.6) + 0.05 * np.sin(3 * th) + 0.05 * np.cos(th))
    BX, BY = -0.24, 0.1
    holder = {}
    def top(a, b):
        x, y = holder["info"]["xy"](a, b); th = np.arctan2(y, x)
        rho = np.hypot(x, y) / (rfn(th) - 0.05)
        q = fbm(x * 2, y * 2, 2.5, 3)
        col = mix(solid(a, c(176, 22, 34)), c(222, 64, 62), fbm(x * 2, y * 2, 3, 1))
        vein = smooth(0.035, 0.0, np.abs(fbm(x * 2 + q, y * 2 - q, 2.2, 7) - 0.5)) * (0.4 + 0.6 * fbm(x, y, 3, 2))
        col = mix(col, c(252, 226, 220), vein)
        col = mix(col, c(250, 214, 208), smooth(0.8, 0.88, vnoise(x * 2, y * 2, 14, 4)) * 0.8)
        col = mix(col, c(255, 140, 140), smooth(0.66, 0.8, fbm(x * 2, y * 2, 5, 11)) * 0.35)
        col = mix(col, c(130, 10, 22), smooth(0.7, 0.84, rho) * 0.5)
        fat = smooth(0.84, 0.88, rho + 0.03 * fbm(x * 2, y * 2, 8, 5))
        col = mix(col, mix(solid(a, c(252, 238, 226)), c(240, 190, 180), 0.6 * fbm(x * 3, y * 3, 6, 6)), fat)
        d = np.hypot(x - BX, y - BY)
        col = mix(col, c(246, 236, 214), smooth(0.105, 0.095, d))
        return mix(col, c(150, 46, 46), smooth(0.06, 0.05, d))
    def side_(a, b):
        col = mix(solid(a, c(250, 232, 220)), c(236, 176, 170), 0.6 * fbm(a * 12, b * 2, 3, 8))
        col = mix(col, c(200, 60, 66), smooth(0.03, 0.0, np.abs(fbm(a * 14, b, 3, 9) - 0.5)) * 0.5)
        return col
    f.region(RT, top); f.region(RSD, side_)
    ob, info = f.slab("Steak", rfn, 0.1, 0.06, RT, RSD, nth=64, nc=6, ne=3, bulge=0.025); holder["info"] = info
    f.tube("Bone", [V(BX, BY, 0), V(-0.55, 0.22, 0.0), V(-0.78, 0.32, 0.0)], 0.07, 0.065, K=12, sub=4, strip=0)
    end = V(-0.8, 0.33, 0.0); perp = V(-0.33, 0.78, 0).normalized() * 0.05
    for sd in (1, -1):
        f.sphere(f"Knob{sd}", end + perp * sd * 1.15, Matrix.Identity(3), (0.085,) * 3, BONE, 16, 10)
    M = rot_axis(V(1, 1, 0), math.radians(42)); f.xform(M)
    lift = V(0, 0, 0.5); f.xform(Matrix.Translation(lift))
    rng = np.random.default_rng(3)
    for k, th in enumerate([-1.2, -0.6, -0.15]):
        r = float(rfn(th)) - 0.02; p = M @ V(r * math.cos(th), r * math.sin(th), -0.08) + lift
        Ld = 0.12 + 0.06 * k
        f.tube(f"Drip{k}", [p + V(0, 0, 0.02), p + V(0.004, 0, -Ld * 0.5), p + V(0, 0, -Ld)], 0, 0, K=8, sub=5, sw=BLOOD,
               rfn=lambda s: 0.022 * (1 - 0.5 * math.sin(math.pi * s * 0.8)) + 0.012 * smooth(0.6, 0.95, s))
        f.sphere(f"DripBulb{k}", p + V(0, 0, -Ld - 0.015), Matrix.Identity(3), (0.03, 0.03, 0.036), BLOOD, 10, 8)
        q = p + V(0.01, -0.01, -Ld - 0.09 - 0.05 * k)
        f.sphere(f"Drop{k}", q, Matrix.Identity(3), (0.022, 0.022, 0.03), BLOOD, 10, 8)
        f.tube(f"DropTip{k}", [q + V(0, 0, 0.01), q + V(0, 0, 0.035), q + V(0, 0, 0.055)], 0.02, 0.002, K=8, sub=3, sw=BLOOD)
    f.bake({BONE: c(246, 236, 212), BLOOD: c(168, 8, 22), MARROW: c(150, 46, 46)},
           strips=[(c(214, 200, 170), c(252, 246, 230), 0.8)] * 2)
    f.done()

def magma_pepper():
    f = Bait("MagmaPepper", "Epic")
    RP = (0.02, 0.04, 0.98, 0.96); ROCK = 0
    ctrl = [V(0.38, 0.0, 0.5), V(0.22, -0.02, 0.44), V(0.04, -0.05, 0.31), V(-0.14, -0.05, 0.18), V(-0.3, 0.0, 0.1),
            V(-0.43, 0.06, 0.08), V(-0.52, 0.12, 0.15), V(-0.54, 0.14, 0.24)]
    rfn = lambda s: 0.17 * float(pchip([0, 0.04, 0.14, 0.4, 0.75, 1], [0.62, 0.92, 1, 0.82, 0.42, 0.08], s))
    prof = lambda s, a: (1 + 0.07 * math.cos(3 * a)) * (1 + 0.05 * math.sin(23 * s + 2 * a) * math.sin(17 * s - 3 * a))
    rng = np.random.default_rng(11)
    cracks = []
    for k in range(7):
        s, a = rng.uniform(0.06, 0.6), rng.uniform(0, TAU); pts = [(s, a)]
        for q in range(rng.integers(6, 10)):
            s += rng.uniform(0.03, 0.05); a += rng.normal(0, 0.35)
            if s > 0.93: break
            pts.append((s, a))
        cracks.append(pts)
    Ltot = 1.35
    def paint(a, b):
        x, y = a * 6, b * 2
        col = mix(solid(a, c(56, 44, 46)), c(26, 20, 24), fbm(x, y, 3, 2))
        col = mix(col, c(96, 74, 66), smooth(0.62, 0.78, fbm(x, y, 7, 5)) * 0.6)
        col = mix(col, c(14, 10, 12), smooth(0.75, 0.82, vnoise(x, y, 14, 3)) * 0.7)
        d = np.full(a.shape, 9.0)
        for pts in cracks:
            for (s0, a0), (s1, a1) in zip(pts[:-1], pts[1:]):
                da = ((a1 - a0) + math.pi) % TAU - math.pi
                circ = TAU * rfn((s0 + s1) / 2)
                bb = ((b * TAU - a0 + math.pi) % TAU - math.pi) * circ / TAU
                d = np.minimum(d, seg_dist(a * Ltot, bb, (s0 * Ltot, 0.0), (s1 * Ltot, da * circ / TAU)))
        col = mix(col, c(150, 30, 10), smooth(0.08, 0.015, d))
        col = mix(col, c(255, 110, 20), smooth(0.03, 0.008, d))
        return mix(col, c(120, 40, 20), smooth(0.08, 0.0, a) * 0.6)
    f.region(RP, paint)
    ob, lo = f.loft("Pepper", ctrl, rfn, RP, K=14, sub=8, prof=prof, ext=(0.35, 0.4))
    for k, pts in enumerate(cracks):
        path = []
        for (s0, a0), (s1, a1) in zip(pts[:-1], pts[1:]):
            for q in range(3):
                t = q / 3; path.append(lo["at"](lerp(s0, s1, t), lerp(a0, a0 + ((a1 - a0 + math.pi) % TAU - math.pi), t), 0.002))
        path.append(lo["at"](pts[-1][0], pts[-1][1], 0.002))
        if len(path) >= 3: f.tube(f"Crack{k}", path, 0.015, 0.006, K=5, sub=2, sw=0, glow=True)
    P0, T0, N0, B0 = lo["frame"](0.0); top = P0 - T0 * rfn(0.0) * 0.3
    for k in range(5):
        a = TAU * k / 5; d = (math.cos(a) * N0 + math.sin(a) * B0)
        lp = top + d * 0.07 - T0 * 0.01
        f.ell(f"Calyx{k}", lp, fz(-T0, d), (0.08, 0.045, 0.03), sw=ROCK, nu=10, nv=6)
    f.ell("CalyxCap", top - T0 * 0.02, fz(-T0, N0), (0.07, 0.07, 0.05), sw=ROCK, nu=12, nv=8)
    up = -T0
    flames = [(0.0, 0.0, 0.46), (2.0, 0.7, 0.28), (4.2, 0.7, 0.25)]
    for k, (ang, lean, Lf) in enumerate(flames):
        d = (math.cos(ang) * N0 + math.sin(ang) * B0); b0 = top - T0 * 0.04 + d * 0.025 * (k > 0)
        pts = [b0, b0 + up * Lf * 0.3 + d * lean * 0.06, b0 + up * Lf * 0.6 + d * lean * 0.05 - d.cross(up) * 0.03,
               b0 + up * Lf * 0.85 + d * (0.02 + lean * 0.08) + d.cross(up) * 0.02, b0 + up * Lf + d * lean * 0.14]
        f.tube(f"Flame{k}", pts, 0, 0, K=8, sub=5, sw=0, glow=True,
               rfn=lambda s, Lf=Lf: Lf * 0.24 * math.sin(math.pi * min(1.0, 0.25 + s)) ** 0.8 * (1 - 0.85 * s) + 0.002)
    for k in range(3):
        p = top + up * (0.52 + 0.06 * k) + (N0 * math.cos(k * 2.3) + B0 * math.sin(k * 2.3)) * 0.12
        f.gem(f"Ember{k}", p, E(k, k * 2, 0.5), (0.018, 0.018, 0.026), 0, glow=True)
    f.bake({ROCK: c(42, 32, 34)})
    f.done(glow=c(255, 122, 28), scale=1.2, yaw=math.radians(45))


# ====================================================================== LEGENDARY
def phantom_jelly():
    f = Bait("PhantomJelly", "Legendary")
    RB = (0.02, 0.04, 0.98, 0.96); C = V(0, 0, 0.95); S = (0.46, 0.46, 0.4); LOB = 8
    def paint(a, b):
        lon = TAU * a; up = smooth(0.42, 0.55, b)
        col = mix(solid(a, c(176, 160, 228)), c(232, 228, 255), smooth(0.5, 0.95, b))
        col = mix(col, c(176, 236, 244), smooth(0.62, 0.5, b) * up)
        canal = np.exp(-((np.cos(lon * LOB) - 1) / 0.03) ** 2) * smooth(0.55, 0.65, b) * (1 - smooth(0.9, 0.98, b))
        col = mix(col, c(196, 176, 240), canal * 0.8)
        col = mix(col, c(250, 248, 255), smooth(0.65, 0.85, fbm(a * 6, b * 3, 3, 4)) * 0.35 * up)
        under = 1 - up
        return mix(col, mix(solid(a, c(130, 116, 196)), c(170, 230, 236), smooth(0.38, 0.1, b)), under)
    f.region(RB, paint)
    def bell(p):
        lat = math.asin(max(-1.0, min(1.0, p.z))); rho = math.cos(lat); lon = math.atan2(p.y, p.x)
        rim = math.exp(-(lat / 0.35) ** 2)
        sc = 1 + 0.06 * math.cos(LOB * lon) * rim
        if lat >= 0: z = -0.18 + 1.18 * math.sin(lat)
        else: z = -0.18 * rho * rho + 0.06 * (1 - rho * rho)
        z -= 0.08 * (0.5 + 0.5 * math.cos(LOB * lon)) * rim
        return V(p.x * sc, p.y * sc, z)
    f.ell("Bell", C, Matrix.Identity(3), S, RB, nu=32, nv=20, deform=bell)
    f.sphere("Core", V(0, 0, 0.72), Matrix.Identity(3), (0.14, 0.14, 0.13), 0, 18, 12, glow=True)
    for k in range(LOB):
        lam = TAU * k / LOB
        f.sphere(f"Rhopalia{k}", C + V(0.49 * math.cos(lam), 0.49 * math.sin(lam), -0.26 * 0.4), basis(V(math.cos(lam), math.sin(lam), 0)),
                 (0.026, 0.026, 0.026), 0, 10, 6, glow=True)
    for k in range(LOB):
        lam = TAU * (k + 0.5) / LOB; root = C + V(0.43 * math.cos(lam), 0.43 * math.sin(lam), -0.075)
        o = V(math.cos(lam), math.sin(lam), 0); w = 0.05 * math.sin(k * 1.7)
        pts = [root, root + o * 0.02 + V(-0.03, 0, -0.2), root + V(-0.12, w, -0.45), root + V(-0.24, -w, -0.68), root + V(-0.38, w * 1.5, -0.86)]
        f.tube(f"Tentacle{k}", pts, 0.018, 0.003, strip=0, K=6, sub=6)
    for k in range(4):
        lam = TAU * k / 4; d = V(math.cos(lam), math.sin(lam), 0); sd = V(-d.y, d.x, 0)
        U = C + V(0, 0, -0.04) + d * 0.08
        f.fin(f"OralArm{k}", lambda s, U=U, sd=sd: U + sd * (s - 0.5) * 0.07, lambda s, d=d: (V(-0.25, 0, -1) + d * 0.25).normalized(),
              lambda s: 0.62 * (0.75 + 0.25 * math.sin(math.pi * s)),
              lambda s, r, sd=sd, d=d, k=k: sd * 0.04 * math.sin(9 * r + 3 * s + k) + d * 0.06 * r * r, 6, 8, 0.01, 0)
    f.bake({0: c(200, 190, 240)}, strips=[(c(200, 186, 244), c(214, 250, 248), 1.0)] * 2,
           fins=[[(0, c(190, 170, 240)), (0.5, c(214, 206, 250)), (1, c(220, 252, 248))]], ray=0.25)
    f.done(glow=c(160, 255, 230))

GLYPHS = [
    [[(0, -1), (0, 1)], [(0, 0.25), (0.6, 0.75)], [(0, -0.3), (0.6, 0.2)]],
    [[(0, -1), (0, 1), (0.6, 0.5), (0, 0)], [(0, 0), (0.6, -1)]],
    [[(0, -1), (0, 1)], [(-0.6, 1), (0, 0.3), (0.6, 1)]],
    [[(0, 1), (0.55, 0.3), (0, -0.4), (-0.55, 0.3), (0, 1)], [(-0.55, -1), (0, -0.4), (0.55, -1)]],
    [[(0, -1), (0, 1)], [(0, 0.6), (0.5, 0), (0, -0.6)]],
    [[(-0.55, -1), (0.55, 1)], [(0.55, -1), (-0.55, 1)], [(-0.3, 0), (0.3, 0)]],
]

def rune_cookie():
    f = Bait("RuneCookie", "Legendary")
    RT, RSD = (0.02, 0.04, 0.62, 0.96), (0.68, 0.04, 0.98, 0.96); BARN, MOSS = 0, 1
    def rfn(th):
        bite = np.exp(-((((th - 2.3) + np.pi) % TAU - np.pi) / 0.22) ** 2)
        return 0.6 * (1 + 0.03 * np.cos(14 * th)) * (1 - 0.13 * bite)
    segs2d = []; strokes = []
    def place(gl, cx, cy, ang, sc):
        ca, sa = math.cos(ang), math.sin(ang)
        for st in gl:
            pts = [(cx + sc * (u * ca - v * sa), cy + sc * (u * sa + v * ca)) for u, v in st]
            strokes.append(pts); segs2d.extend(zip(pts[:-1], pts[1:]))
    for k, gl in enumerate(GLYPHS):
        a = TAU * k / 6 + 0.25; place(gl, 0.37 * math.cos(a), 0.37 * math.sin(a), a - math.pi / 2, 0.075)
    place([[(-0.7, -0.45), (0.7, -0.45), (0, 0.75), (-0.7, -0.45)], [(0, -0.05), (0, 0.25)]], 0, 0, 0.0, 0.1)
    holder = {}
    def top(a, b):
        x, y = holder["info"]["xy"](a, b); th = np.arctan2(y, x); rho = np.hypot(x, y) / (rfn(th) - 0.06)
        col = mix(solid(a, c(176, 156, 122)), c(122, 106, 86), fbm(x * 2, y * 2, 2.5, 1))
        col = mix(col, c(206, 190, 156), smooth(0.6, 0.75, fbm(x * 2, y * 2, 6, 2)) * 0.6)
        col = mix(col, c(84, 72, 60), smooth(0.015, 0.0, np.abs(fbm(x * 2, y * 2, 1.8, 3) - 0.5)) * 0.8)
        col = mix(col, c(90, 128, 96), smooth(0.55, 0.75, fbm(x * 2 + 5, y * 2, 3, 4)) * smooth(0.6, 0.95, rho) * 0.8)
        for k in range(10):
            ang = TAU * k / 10 + 0.1
            col = mix(col, c(96, 82, 66), smooth(0.022, 0.014, np.hypot(x - 0.5 * math.cos(ang), y - 0.5 * math.sin(ang))))
        d = np.full(a.shape, 9.0)
        for p0, p1 in segs2d: d = np.minimum(d, seg_dist(x, y, p0, p1))
        col = mix(col, c(90, 160, 140), smooth(0.05, 0.02, d) * 0.6)
        col = mix(col, c(52, 44, 40), smooth(0.026, 0.016, d))
        return mix(col, c(214, 200, 168), smooth(0.86, 0.98, rho) * 0.5)
    def side_(a, b):
        col = mix(solid(a, c(160, 140, 110)), c(110, 96, 78), fbm(a * 14, b * 2, 3, 6))
        col = mix(col, c(90, 78, 64), np.exp(-(((b * 4) % 1.0 - 0.5) / 0.08) ** 2) * 0.5)
        return mix(col, c(90, 128, 96), smooth(0.6, 0.75, fbm(a * 14, b * 2, 4, 9)) * 0.7)
    f.region(RT, top); f.region(RSD, side_)
    ob, info = f.slab("Cookie", rfn, 0.1, 0.06, RT, RSD, nth=84, nc=7, ne=3, bulge=0.03); holder["info"] = info
    paths = [[V(x, y, info["ztop"](x, y)) for x, y in st] for st in strokes]
    f.strokes("Rune", paths, 0.013, glow=True)
    f.torus("RuneRing", V(0, 0, info["ztop"](0.2, 0.0) - 0.004), V(0, 0, 1), 0.2, 0.012, 0, 40, 6, glow=True)
    for k, (th, s) in enumerate([(-0.9, 0.05), (-0.6, 0.035), (3.6, 0.045)]):
        r = float(rfn(th)) - 0.05; p = V(r * math.cos(th), r * math.sin(th), 0.07)
        f.ell(f"Barnacle{k}", p, fz(V(math.cos(th) * 0.4, math.sin(th) * 0.4, 1)), (s, s, s * 0.8), sw=BARN, nu=10, nv=6,
              deform=lambda q: V(q.x * (1 - 0.3 * max(q.z, 0)), q.y * (1 - 0.3 * max(q.z, 0)), q.z))
        f.ell(f"BarnHole{k}", p + V(0, 0, s * 0.75), Matrix.Identity(3), (s * 0.45, s * 0.45, s * 0.12), sw=MOSS, nu=8, nv=4)
    M = rot_axis(V(1, 1, 0), math.radians(55)); f.xform(M); f.xform(Matrix.Translation(V(0, 0, 0.62)))
    f.bake({BARN: c(222, 214, 196), MOSS: c(60, 70, 60)})
    f.done(glow=c(70, 255, 200), scale=1.25)


# ====================================================================== MYTHIC / CELESTIAL
def dragon_pearl():
    f = Bait("DragonPearl", "Mythic")
    RP, RCL, RBS = (0.02, 0.04, 0.5, 0.96), (0.56, 0.04, 0.98, 0.46), (0.56, 0.54, 0.98, 0.96)
    GOLD, CRIMSON, DGOLD, NAIL = 0, 1, 2, 3
    C = V(0, 0, 0.8); R = 0.36
    n = V(0.72, -0.72, 0.3).normalized(); e1 = n.cross(V(0, 0, 1)).normalized(); e2 = e1.cross(n)
    arms = []
    for k in range(2):
        pts = []
        for i in range(34):
            t = i / 33; rho = 1.05 * t; beta = math.pi * k + 3.2 * math.pi * t
            pts.append((math.cos(rho) * n + math.sin(rho) * (math.cos(beta) * e1 + math.sin(beta) * e2)).normalized())
        arms.append(pts)
    def pearl(a, b):
        lon, lat = TAU * a, math.pi * (b - 0.5)
        P = np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)], -1)
        col = solid(a, c(250, 246, 240))
        col = mix(col, c(255, 214, 226), smooth(0.45, 0.75, fbm(a * 4, b * 2, 2, 3)) * 0.6)
        col = mix(col, c(214, 236, 255), smooth(0.5, 0.8, fbm(a * 4 + 7, b * 2, 2, 5)) * 0.5)
        col = mix(col, c(255, 236, 196), smooth(0.55, 0.8, fbm(a * 4 + 3, b * 2, 2, 7)) * 0.5)
        best = np.full(a.shape, -1.0)
        for pts in arms:
            for q in pts: best = np.maximum(best, P @ np.array(q[:]))
        ang = np.arccos(np.clip(best, -1, 1))
        col = mix(col, c(255, 200, 120), smooth(0.25, 0.04, ang) * 0.75)
        return mix(col, c(236, 226, 220), smooth(-0.6, -1.0, np.sin(lat)) * 0.4)
    def claw(a, b):
        e, inner = scales(a * 8, b * 3, 0.32)
        col = mix(solid(a, c(236, 172, 52)), c(255, 226, 130), (1 - inner) * 0.5)
        col = mix(col, c(150, 88, 18), e * 0.75)
        return mix(col, c(255, 240, 180), np.exp(-((np.cos(TAU * b) - 1) / 0.15) ** 2) * 0.4)
    def base(a, b):
        e, inner = scales(a * 10, b * 3, 0.35)
        col = mix(solid(a, c(228, 162, 48)), c(255, 220, 120), (1 - inner) * 0.4)
        col = mix(col, c(140, 80, 16), e * 0.6)
        return mix(col, c(206, 30, 46), smooth(0.04, 0.0, np.abs(b - 0.62) - 0.04))
    f.region(RP, pearl); f.region(RCL, claw); f.region(RBS, base)
    f.ell("Pearl", C, Matrix.Identity(3), (R, R, R), RP, nu=28, nv=18)
    for k, pts in enumerate(arms):
        path = [C + q * (R + 0.002) for q in pts]
        f.tube(f"Swirl{k}", path, 0, 0, K=6, sub=1, sw=0, glow=True, rfn=lambda s: 0.022 * (1 - 0.75 * s) + 0.004)
    f.sphere("SwirlEye", C + n * (R - 0.01), basis(n), (0.03, 0.045, 0.045), 0, 10, 8, glow=True)
    f.ell("Pedestal", V(0, 0, 0.13), Matrix.Identity(3), (0.32, 0.32, 0.15), RBS, nu=28, nv=10,
          deform=lambda p: V(p.x * (1 - 0.35 * max(p.z, 0)), p.y * (1 - 0.35 * max(p.z, 0)), p.z if p.z > 0 else p.z * 0.25))
    f.torus("BaseRing", V(0, 0, 0.1), V(0, 0, 1), 0.3, 0.03, DGOLD, 32, 6)
    f.torus("NeckRing", V(0, 0, 0.3), V(0, 0, 1), 0.13, 0.03, CRIMSON, 24, 6)
    f.tube("Neck", [V(0, 0, 0.2), V(0, 0, 0.32), V(0, 0, 0.47)], 0.14, 0.1, K=14, sub=3, strip=0)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2; o = V(math.cos(a), math.sin(a), 0)
        f.gem(f"Gem{k}", V(0, 0, 0.13) + o * 0.29, fz(o, V(0, 0, 1)), (0.045, 0.035, 0.035), CRIMSON)
    def sph(phi, lat, rr): return C + rr * V(math.cos(lat) * math.cos(phi), math.cos(lat) * math.sin(phi), math.sin(lat))
    for k, deg in enumerate([15, -105, 105, -165]):
        phi = math.radians(deg); o = V(math.cos(phi), math.sin(phi), 0)
        pts = [V(0, 0, 0.32) + o * 0.08, sph(phi, math.radians(-62), R + 0.06), sph(phi, math.radians(-25), R + 0.055),
               sph(phi, math.radians(12), R + 0.05), sph(phi, math.radians(36), R + 0.025)]
        rf = lambda s: lerp(0.075, 0.036, s) * (1 + 0.2 * math.exp(-((s - 0.38) / 0.07) ** 2) + 0.18 * math.exp(-((s - 0.7) / 0.07) ** 2))
        ob, lo = f.loft(f"Talon{k}", pts, rf, RCL, K=9, sub=5, ref=o)
        tip = pts[-1]; inward = (C - tip).normalized()
        f.tube(f"Nail{k}", [tip - inward * 0.01, tip + V(0, 0, 0.05) + inward * 0.04, tip + V(0, 0, 0.03) + inward * 0.11], 0.034, 0.003,
               K=7, sub=4, sw=NAIL)
    for k in range(4):
        phi = math.radians(-45 + 90 * k + (0 if k else 0)); o = V(math.cos(phi), math.sin(phi), 0)
        if k == 0: continue
        sd = V(-o.y, o.x, 0); b0 = V(0, 0, 0.36) + o * 0.1
        f.fin(f"Frill{k}", lambda s, b0=b0, sd=sd: b0 + sd * (s - 0.5) * 0.12, lambda s, o=o: (o + V(0, 0, 0.7)).normalized(),
              lambda s: 0.24 * math.sin(math.pi * (0.05 + 0.9 * s)) ** 0.6, lambda s, r, o=o, sd=sd: o * 0.06 * r * r + sd * 0.03 * math.sin(6 * r + 2 * s),
              6, 5, 0.012, 0)
    f.bake({GOLD: c(230, 166, 50), CRIMSON: c(206, 30, 46), DGOLD: c(190, 124, 30), NAIL: c(150, 16, 34)},
           strips=[(c(196, 128, 36), c(255, 228, 140), 1.0)] * 2,
           fins=[[(0, c(176, 18, 38)), (0.4, c(232, 74, 48)), (0.72, c(246, 186, 80)), (1.0, c(255, 243, 210))]], ray=0.3)
    f.done(glow=c(255, 190, 80), scale=1.35)

def stardust_morsel():
    f = Bait("StardustMorsel", "Celestial")
    RT, RSD = (0.02, 0.04, 0.62, 0.96), (0.68, 0.04, 0.98, 0.96); LILAC, PINK, MINT, BLUE = 0, 1, 2, 3
    def rfn(th): return 0.26 + 0.27 * ((1 + np.cos(5 * (th - math.pi / 2))) / 2) ** 1.8
    holder = {}
    def top(a, b):
        x, y = holder["info"]["xy"](a, b); th = np.arctan2(y, x); rho = np.hypot(x, y) / (rfn(th) - 0.09)
        n1, n2 = fbm(x * 2, y * 2, 2.2, 1), fbm(x * 2 + 4, y * 2, 2.6, 5)
        col = mix(solid(a, c(46, 22, 104)), c(206, 60, 186), smooth(0.45, 0.75, n1))
        col = mix(col, c(70, 170, 255), smooth(0.5, 0.78, n2) * 0.8)
        col = mix(col, c(20, 10, 50), smooth(0.4, 0.2, n1 + n2 * 0.3) * 0.6)
        st = smooth(0.86, 0.9, vnoise(x * 2, y * 2, 40, 7)) + smooth(0.9, 0.93, vnoise(x * 2, y * 2, 70, 8))
        col = mix(col, c(255, 255, 255), st)
        return mix(col, c(255, 186, 236), smooth(0.8, 1.0, rho) * 0.75)
    def side_(a, b):
        col = mix(solid(a, c(255, 170, 230)), c(170, 130, 255), 0.5 + 0.5 * np.cos(TAU * b))
        return mix(col, c(255, 255, 255), smooth(0.86, 0.9, vnoise(a * 20, b * 2, 30, 9)))
    f.region(RT, top); f.region(RSD, side_)
    ob, info = f.slab("Star", rfn, 0.1, 0.09, RT, RSD, nth=80, nc=5, ne=3, bulge=0.07); holder["info"] = info
    core = lambda th: 0.4 * rfn(th)
    for sd in (1, -1):
        cob, _ = f.slab(f"Core{sd}", core, 0.03, 0.028, RT, RSD, nth=60, nc=3, ne=2, bulge=0.035, glow=True, z0=sd * 0.15)
    M = rot_axis(V(1, 1, 0), math.radians(58)); f.xform(M); cen = V(0, 0, 0.75); f.xform(Matrix.Translation(cen))
    for ri, (nrm, Rr, cnt, sw_) in enumerate([(V(0.35, 0.3, 1), 0.74, 6, LILAC), (V(-0.5, 0.25, 1), 0.62, 5, MINT)]):
        nrm = nrm.normalized(); Bm = basis(nrm); Y, Zr = Bm.col[1], Bm.col[2]
        f.torus(f"Orbit{ri}", cen, nrm, Rr, 0.009, sw_, 48, 4)
        for k in range(cnt):
            a = TAU * k / cnt + ri * 0.5; p = cen + Rr * (math.cos(a) * Y + math.sin(a) * Zr)
            if ri == 0:
                u = V(1, 1, 0).normalized(); vv = CAM.cross(u).normalized(); Mr = Matrix((u, CAM, vv)).transposed()
                s = 0.8 + 0.4 * (k % 2)
                f.gem(f"SparkA{k}", p, Mr, (0.02 * s, 0.012 * s, 0.085 * s), 0, glow=True)
                f.gem(f"SparkB{k}", p, Mr, (0.085 * s, 0.012 * s, 0.02 * s), 0, glow=True)
            else:
                f.sphere(f"Candy{k}", p, E(k, 2 * k, 0), (0.035,) * 3, [PINK, BLUE, MINT][k % 3], 12, 8)
    f.bake({LILAC: c(220, 196, 255), PINK: c(255, 150, 220), MINT: c(150, 255, 220), BLUE: c(130, 190, 255)})
    f.done(glow=c(255, 236, 150), scale=1.05)


BAITS = [("BreadCrumbs", bread_crumbs), ("Earthworm", earthworm), ("CornKernels", corn_kernels),
         ("Cricket", cricket), ("Shrimp", shrimp), ("SpinnerLure", spinner_lure),
         ("SquidChunk", squid_chunk), ("GlowWorm", glow_worm), ("FrozenKrill", frozen_krill),
         ("RawSteak", raw_steak), ("MagmaPepper", magma_pepper),
         ("PhantomJelly", phantom_jelly), ("RuneCookie", rune_cookie),
         ("DragonPearl", dragon_pearl), ("StardustMorsel", stardust_morsel)]

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for name, fn in BAITS:
        if not want or name in want:
            print(f"=== {name}"); fn()
