"""Dragon Koi (Divine) - style reference fish.
Run: python dragon_koi.py <out_dir> [--no-render]
Builds one textured mesh, exports .blend/.glb/.fbx + texture, renders previews.
"""
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Matrix

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
RENDER = "--no-render" not in sys.argv
NAME = "DragonKoi"
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------------------------------------------------------------- helpers
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

def lerp(a, b, t): return a + (b - a) * t
def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

PARTS = []
def make_obj(name, verts, faces, uvs):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    uvl = me.uv_layers.new(name="UVMap")
    flat = [c for f in uvs for c in f]
    uvl.data.foreach_set("uv", [x for c in flat for x in c])
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    PARTS.append(ob)
    return ob

def solidify(ob, thick):
    m = ob.modifiers.new("solid", "SOLIDIFY"); m.thickness = thick; m.offset = 0.0
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier="solid")

# ---- texture atlas layout (1024^2) ----
#  top half: body (u=t along length, v=around)
#  bottom-left 384px: fin gradient    bottom 384-512: two gradient strips
#  bottom-right: 8x8 flat swatches
def uv_body(t, v): return (0.001 + t * 0.998, 0.5 + 0.001 + v * 0.497)
def uv_fin(s, r):  return (0.004 + s * 0.367, 0.004 + r * 0.490)
def uv_strip(k, a, s): return ((384 + k*64 + 8 + a*48) / 1024, (6 + s*500) / 1024)
def uv_sw(i): return ((512 + (i % 8)*64 + 32) / 1024, ((i // 8)*64 + 32) / 1024)
SW = dict(iris=0, pupil=1, white=2, lip=3, rim=4, mouth=5)

# ---------------------------------------------------------------- body
L, R, H = 5.0, 0.78, 1.08
PT = [0, .02, .06, .12, .22, .35, .50, .65, .80, .90, 1.0]
PR = [0, .40, .62, .80, .94, 1.0, .93, .73, .47, .31, .25]
def r_of(t): return R * pchip(PT, PR, t)
def zc_of(t): return 0.06 * math.sin(math.pi * t) - 0.06 * (1 - t) ** 8
def w_of(t): return 0.80 - 0.28 * t * t
def x_of(t): return L / 2 - t * L
def axis(t): return Vector((x_of(t), 0, zc_of(t)))
def surf(t, th, k=1.0):
    r = r_of(t); s = math.sin(th)
    p = Vector((x_of(t), w_of(t) * r * math.cos(th), zc_of(t) + H * r * s * (0.88 if s < 0 else 1.0)))
    a = axis(t); return a + (p - a) * k

def build_body():
    N, M = 50, 28
    ts = [0.004 + 0.992 * (i / (N - 1)) ** 1.25 for i in range(N)]
    verts, faces, uvs = [], [], []
    for t in ts:
        for j in range(M):
            verts.append(surf(t, -math.pi / 2 + 2 * math.pi * j / M))
    for i in range(N - 1):
        for j in range(M):
            j2 = (j + 1) % M
            faces.append((i*M + j, i*M + j2, (i+1)*M + j2, (i+1)*M + j))
            uvs.append([uv_body(ts[i], j/M), uv_body(ts[i], (j+1)/M),
                        uv_body(ts[i+1], (j+1)/M), uv_body(ts[i+1], j/M)])
    hp = len(verts); verts.append(axis(0) + Vector((0.0, 0, 0)))
    tp = len(verts); verts.append(axis(1) - Vector((0.02, 0, 0)))
    last = (N - 1) * M
    for j in range(M):
        j2 = (j + 1) % M
        faces.append((hp, j2, j)); uvs.append([uv_body(0, (j+.5)/M), uv_body(ts[0], (j+1)/M), uv_body(ts[0], j/M)])
        faces.append((tp, last + j, last + j2)); uvs.append([uv_body(1, (j+.5)/M), uv_body(ts[-1], j/M), uv_body(ts[-1], (j+1)/M)])
    make_obj("Body", verts, faces, uvs)

# ---------------------------------------------------------------- fins
def build_fin(name, root, direc, length, wave, nu, nv, thick=0.025):
    verts, faces, uvs = [], [], []
    for a in range(nu + 1):
        s = a / nu
        R0, D, Ln = root(s), direc(s).normalized(), length(s)
        for b in range(nv + 1):
            r = b / nv
            verts.append(R0 + D * (Ln * r) + wave(s, r))
    for a in range(nu):
        for b in range(nv):
            i = a * (nv + 1) + b
            faces.append((i, i + nv + 1, i + nv + 2, i + 1))
            uvs.append([uv_fin(a/nu, b/nv), uv_fin((a+1)/nu, b/nv), uv_fin((a+1)/nu, (b+1)/nv), uv_fin(a/nu, (b+1)/nv)])
    ob = make_obj(name, verts, faces, uvs); solidify(ob, thick); return ob

def V(x, y, z): return Vector((x, y, z))

def build_fins():
    # dorsal "mane": flame-like crest along the back
    def d_len(s):
        env = math.sin(math.pi * s) ** 0.55 * (1.15 - 0.55 * s)
        f = (s * 8) % 1.0
        return 0.95 * env * (0.58 + 0.42 * f ** 1.4)
    build_fin("Dorsal",
              lambda s: surf(lerp(0.13, 0.74, s), math.pi / 2, 0.93),
              lambda s: V(lerp(-0.25, -0.85, s), 0, 1),
              d_len,
              lambda s, r: V(0, 0.05 * r ** 1.5 * math.sin(2 * math.pi * 3 * s + 2 * r), 0),
              72, 7)
    # tail: big double-lobed veil
    te = 0.985; re = r_of(te)
    def t_root(s): return V(x_of(te), 0, zc_of(te) + lerp(-1, 1, s) * H * re * 0.8)
    def t_dir(s):
        a = math.radians(lerp(-62, 62, s)); return V(-math.cos(a), 0, math.sin(a))
    def t_len(s):
        e = abs(2 * s - 1)
        return 2.0 * (0.5 + 0.5 * e ** 0.8) * (1 - 0.38 * e ** 6) * (1 + 0.045 * math.sin(12 * math.pi * s))
    build_fin("Tail", t_root, t_dir, t_len,
              lambda s, r: V(0, 0.24 * r ** 1.6 * math.sin(math.pi * 1.2 * r + 2 * s), 0),
              36, 11, 0.03)
    for side in (1, -1):
        # pectorals: long flowing "butterfly" fins
        rp = lambda s, side=side: surf(lerp(0.19, 0.25, s), -0.75, 0.92) * 1 if side > 0 else _mir(surf(lerp(0.19, 0.25, s), -0.75, 0.92))
        pd = lambda s, side=side: V(lerp(-0.35, -0.95, s), side * lerp(0.85, 0.35, s), lerp(-0.45, -0.25, s))
        pl = lambda s: 1.35 * (0.45 + 0.55 * math.sin(math.pi * (0.15 + 0.85 * s)) ** 0.8) * (1 + 0.05 * math.sin(10 * math.pi * s))
        pn = V(-0.2, side * 0.35, 1).normalized()
        build_fin(f"Pectoral_{'L' if side > 0 else 'R'}", rp, pd, pl,
                  lambda s, r, pn=pn: pn * (0.12 * r ** 1.8 * math.sin(2 * math.pi * 1.2 * s + 3 * r)), 20, 9)
        # pelvics
        build_fin(f"Pelvic_{'L' if side > 0 else 'R'}",
                  lambda s, side=side: _side(surf(lerp(0.42, 0.48, s), -1.15, 0.92), side),
                  lambda s, side=side: V(-0.65, side * lerp(0.45, 0.25, s), -0.7),
                  lambda s: 0.75 * (0.4 + 0.6 * math.sin(math.pi * (0.2 + 0.8 * s)) ** 0.8),
                  lambda s, r: V(0, 0, 0.05 * r * r * math.sin(5 * s + 2 * r)), 14, 8)
        # gill frills (dragon cheek spikes)
        def g_len(s):
            f = (s * 3) % 1.0
            return 0.55 * (0.45 + 0.55 * f ** 1.3) * (0.6 + 0.4 * math.sin(math.pi * s))
        build_fin(f"Frill_{'L' if side > 0 else 'R'}",
                  lambda s, side=side: _side(surf(0.15 + 0.01 * s, lerp(-0.45, 0.75, s), 0.95), side),
                  lambda s, side=side: V(-1, side * 0.55, lerp(-0.1, 0.35, s)),
                  g_len, lambda s, r: V(0, 0, 0), 24, 4, 0.02)
    # anal fin
    build_fin("Anal",
              lambda s: surf(lerp(0.66, 0.78, s), -math.pi / 2, 0.92),
              lambda s: V(-0.7, 0, -1),
              lambda s: 0.5 * math.sin(math.pi * s) ** 0.6 * (1.2 - 0.5 * s),
              lambda s, r: V(0, 0.03 * r * math.sin(6 * s), 0), 16, 6)

def _mir(p): return Vector((p.x, -p.y, p.z))
def _side(p, side): return p if side > 0 else _mir(p)

# ---------------------------------------------------------------- tubes
def catmull(pts, n):
    P = [pts[0] + (pts[0] - pts[1])] + pts + [pts[-1] + (pts[-1] - pts[-2])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2*p1) + (p2 - p0)*t + (2*p0 - 5*p1 + 4*p2 - p3)*t*t + (3*p1 - p0 - 3*p2 + p3)*t**3))
    out.append(pts[-1]); return out

def build_tube(name, ctrl, r0, r1, strip, K=8, sub=5, pw=1.0):
    pts = catmull(ctrl, sub); n = len(pts)
    seg = [0.0]
    for i in range(1, n): seg.append(seg[-1] + (pts[i] - pts[i-1]).length)
    T = [(pts[min(i+1, n-1)] - pts[max(i-1, 0)]).normalized() for i in range(n)]
    up = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((0, 1, 0))
    N0 = T[0].cross(up).normalized(); Ns = [N0]
    for i in range(1, n):
        ax = T[i-1].cross(T[i]); nn = Ns[-1].copy()
        if ax.length > 1e-6: nn = Matrix.Rotation(T[i-1].angle(T[i]), 3, ax.normalized()) @ nn
        Ns.append(nn)
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
            uvs.append([uv_strip(strip, k/K, s0), uv_strip(strip, (k+1)/K, s0), uv_strip(strip, (k+1)/K, s1), uv_strip(strip, k/K, s1)])
    tip = len(verts); verts.append(pts[-1]); base = len(verts); verts.append(pts[0])
    l0 = (rings - 1) * K
    for k in range(K):
        k2 = (k + 1) % K
        faces.append((l0 + k, l0 + k2, tip)); uvs.append([uv_strip(strip, k/K, .98), uv_strip(strip, (k+1)/K, .98), uv_strip(strip, .5, 1)])
        faces.append((k2, k, base)); uvs.append([uv_strip(strip, (k+1)/K, 0), uv_strip(strip, k/K, 0), uv_strip(strip, .5, 0)])
    make_obj(name, verts, faces, uvs)

def build_head_tubes():
    for side in (1, -1):
        sd = "L" if side > 0 else "R"
        hb = _side(surf(0.10, 1.12, 0.9), side)
        rel = lambda x, y, z: hb + V(x, side * y, z)
        build_tube(f"Horn_{sd}", [rel(0, 0, 0), rel(-0.12, .10, .35), rel(-0.45, .24, .62), rel(-0.95, .34, .70), rel(-1.25, .36, .62)],
                   0.10, 0.012, 0, pw=0.9)
        bp = rel(-0.2, .14, .45)
        build_tube(f"HornBranch_{sd}", [bp + V(0.06, 0, -0.08), bp, bp + V(0.06, side*.06, .22), bp + V(0.02, side*.1, .38)],
                   0.06, 0.01, 0)
        wb = _side(surf(0.035, -0.15, 0.9), side)
        relw = lambda x, y, z: wb + V(x, side * y, z)
        build_tube(f"Whisker_{sd}", [relw(0, 0, 0), relw(.15, .18, -.05), relw(.05, .55, -.2), relw(-.5, .85, -.35),
                                      relw(-1.1, .95, -.25), relw(-1.5, .8, -.02), relw(-1.62, .62, .12)], 0.05, 0.008, 1, pw=0.7)
        bb = _side(surf(0.02, -0.9, 0.85), side)
        build_tube(f"Barbel_{sd}", [bb, bb + V(.06, side*.08, -.12), bb + V(-.03, side*.12, -.27)], 0.03, 0.008, 1)

# ---------------------------------------------------------------- spheres / tori
def basis(n, upish=Vector((0, 0, 1))):
    X = n.normalized(); Z = (upish - X * upish.dot(X)).normalized(); Y = Z.cross(X)
    return Matrix((X, Y, Z)).transposed()

def build_sphere(name, center, rot, scale, sw, u=18, v=12):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    M = Matrix.Translation(center) @ rot.to_4x4() @ Matrix.Diagonal((*scale, 1))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    verts = [vv.co.copy() for vv in bm.verts]; faces = [tuple(vv.index for vv in f.verts) for f in bm.faces]; bm.free()
    make_obj(name, verts, faces, [[uv_sw(sw)] * len(f) for f in faces])

def build_torus(name, center, n, R1, r1, sw, U=24, Vn=8):
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
    make_obj(name, verts, faces, [[uv_sw(sw)] * 4 for f in faces])

def build_face():
    te, th = 0.085, 0.42
    for side in (1, -1):
        sd = "L" if side > 0 else "R"
        S = _side(surf(te, th), side)
        n = ((S - axis(te)).normalized() + V(0.38, 0, 0)).normalized()
        re = 0.19; C = S - n * 0.075
        Bm = basis(n)
        build_sphere(f"Eye_{sd}", C, Bm, (re, re, re), SW["iris"])
        build_sphere(f"Pupil_{sd}", C + n * (re - 0.025), Bm, (0.05, 0.05, 0.135), SW["pupil"], 14, 10)
        hl = (n * 0.9 + Bm.col[2] * 0.42 + V(0.25, 0, 0)).normalized()
        build_sphere(f"Glint_{sd}", C + hl * (re + 0.005), Bm, (0.042, 0.042, 0.042), SW["white"], 10, 6)
        d = re * 0.42
        build_torus(f"EyeRim_{sd}", C + n * d, n, math.sqrt(re*re - d*d) + 0.005, 0.032, SW["rim"])
    # puckered koi mouth
    mc = axis(0) + V(-0.03, 0, -0.03)
    build_torus("Lips", mc, V(1, 0, 0), 0.10, 0.048, SW["lip"], 20, 8)
    build_sphere("Mouth", mc + V(0.02, 0, 0), basis(V(1, 0, 0)), (0.03, 0.09, 0.08), SW["mouth"], 12, 8)

# ---------------------------------------------------------------- texture
def vnoise(X, Y, freq, seed):
    g = np.random.default_rng(seed).random((64, 64))
    x, y = X * freq, Y * freq
    xi, yi = np.floor(x).astype(int), np.floor(y).astype(int); xf, yf = x - xi, y - yi
    sx, sy = xf*xf*(3 - 2*xf), yf*yf*(3 - 2*yf)
    a = g[xi % 64, yi % 64]; b = g[(xi+1) % 64, yi % 64]; c = g[xi % 64, (yi+1) % 64]; d = g[(xi+1) % 64, (yi+1) % 64]
    return a + (b - a)*sx + (c - a)*sy + (a - b - c + d)*sx*sy

def c(*rgb): return np.array(rgb, float) / 255.0

PEARL, CREAM = c(247, 243, 236), c(253, 248, 236)
CRIMSON, GOLD = c(206, 30, 46), c(228, 162, 48)

def build_texture():
    S = 1024; img = np.zeros((S, S, 3))
    # ---- body
    hb = 512
    T, Vv = np.meshgrid((np.arange(S) + .5) / S, (np.arange(hb) + .5) / hb)
    X, Y = T * L, Vv * 4.6
    top = np.cos(2 * np.pi * (Vv - 0.5))
    col = PEARL + (CREAM - PEARL) * smooth(-0.2, -0.8, top)[..., None]
    # red koi patches + tancho crown on the head
    f = 0.65 * vnoise(X, Y, 1.0, 3) + 0.35 * vnoise(X, Y, 2.2, 4) + 0.45 * top - 0.80
    dcap = np.sqrt(((X - 0.42) / 0.3) ** 2 + ((Vv - 0.5) * 4.6 / 0.62) ** 2)
    fcap = 0.3 * (1 - dcap)
    f = np.where(T < 0.15, fcap, np.maximum(f, fcap))
    red = smooth(-0.015, 0.015, f)
    g = 0.7 * vnoise(X, Y, 1.6, 9) + 0.3 * vnoise(X, Y, 3.1, 11) + 0.25 * top - 0.66
    gold = smooth(-0.015, 0.015, g) * (1 - red) * smooth(0.16, 0.2, T)
    col = col * (1 - red[..., None]) + CRIMSON * red[..., None]
    col = col * (1 - gold[..., None]) + GOLD * gold[..., None]
    # overlapping scales (head-ward scale on top -> arcs bulge toward tail)
    s = 0.15; best_ci = np.full(X.shape, 1e9); edge = np.zeros(X.shape); inner = np.zeros(X.shape)
    c0 = np.floor(X / s)
    for di in (-1, 0, 1):
        ci = c0 + di; off = (ci % 2) * s / 2
        for dj in (-1, 0, 1):
            cj = np.floor((Y - off) / s) + dj
            d = np.hypot(X - ci * s, (Y - (cj * s + off)) * 1.15) / (s * 0.78)
            take = (d < 1) & (ci < best_ci)
            best_ci = np.where(take, ci, best_ci); edge = np.where(take, smooth(0.72, 0.97, d), edge)
            inner = np.where(take, d, inner)
    st = smooth(0.13, 0.19, T)[..., None] * (1 - 0.5 * smooth(-0.3, -0.9, top))[..., None]
    ecol = (c(222, 170, 80) * (1 - red - gold)[..., None] + c(150, 14, 34) * red[..., None] + c(176, 110, 28) * gold[..., None])
    e = (edge * 0.6)[..., None] * st
    col = col * (1 - e) + ecol * e
    col = col * (1 + 0.06 * st * (1 - inner[..., None]))
    img[512:] = col
    # ---- fin gradient (root crimson -> orange -> gold -> ivory tip) with rays
    rr = (np.arange(512) + .5) / 512; xx = np.arange(384)
    stops = [(0, c(176, 18, 38)), (0.4, c(232, 74, 48)), (0.72, c(246, 186, 80)), (1.0, c(255, 243, 210))]
    grad = np.zeros((512, 3))
    for k in range(3):
        (a0, c0_), (a1, c1_) = stops[k], stops[k + 1]
        m = (rr >= a0) & (rr <= a1); t = ((rr[m] - a0) / (a1 - a0))[:, None]; grad[m] = c0_ + (c1_ - c0_) * t
    ray = np.exp(-((xx % 12) - 6) ** 2 / 2.2)
    fin = grad[:, None, :] * (1 - 0.25 * ray[None, :, None] * (1 - 0.7 * rr)[:, None, None])
    img[:512, :384] = fin
    # ---- gradient strips: 0 horn (deep gold -> ivory), 1 whisker (gold -> pale gold)
    def strip(k, a, b, p=1.0):
        t = ((np.arange(512) + .5) / 512) ** p
        img[:512, 384 + 64*k: 448 + 64*k] = (a + (b - a) * t[:, None])[:, None, :]
    strip(0, c(196, 128, 36), c(255, 244, 214), 1.4)
    strip(1, c(222, 160, 50), c(255, 232, 160))
    # ---- swatches
    sw = {SW["iris"]: c(255, 196, 40), SW["pupil"]: c(18, 10, 16), SW["white"]: c(255, 255, 255),
          SW["lip"]: c(190, 40, 62), SW["rim"]: c(120, 14, 30), SW["mouth"]: c(60, 8, 22)}
    img[:512, 512:] = c(128, 128, 128)
    for i, v in sw.items():
        x0, y0 = 512 + (i % 8) * 64, (i // 8) * 64
        img[y0:y0 + 64, x0:x0 + 64] = v
    img = np.clip(img, 0, 1)
    im = bpy.data.images.new(f"{NAME}_Texture", S, S, alpha=False)
    rgba = np.concatenate([img, np.ones((S, S, 1))], axis=2).astype(np.float32)
    im.pixels.foreach_set(rgba.ravel())
    im.filepath_raw = os.path.join(OUT, f"{NAME}_Texture.png"); im.file_format = "PNG"; im.save()
    im.filepath = im.filepath_raw
    return im

# ---------------------------------------------------------------- assemble
build_body(); build_fins(); build_head_tubes(); build_face()
tex = build_texture()

for ob in PARTS: ob.select_set(True)
bpy.context.view_layer.objects.active = PARTS[0]
bpy.ops.object.join()
fish = bpy.context.active_object; fish.name = NAME; fish.data.name = NAME

# gentle swimming curve (tail swings sideways), then face +Y (= Roblox -Z / LookVector)
me = fish.data
for v in me.vertices:
    k = max(0.0, (L / 2 - v.co.x) / 7.0)
    v.co.y += 0.5 * k ** 2.2
me.transform(Matrix.Rotation(math.radians(90), 4, "Z"))
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
fish.location = (0, 0, 0)
bpy.ops.object.shade_smooth()

mat = bpy.data.materials.new(f"{NAME}_Mat")
nt = mat.node_tree
bsdf = nt.nodes["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.45
tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = tex
nt.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
me.materials.append(mat)

tris = sum(len(p.vertices) - 2 for p in me.polygons)
dims = fish.dimensions
print(f"TRIS {tris}  DIMS {dims.x:.2f} x {dims.y:.2f} x {dims.z:.2f}")

# ---------------------------------------------------------------- export
bpy.ops.object.select_all(action="DESELECT"); fish.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, f"{NAME}.glb"), export_format="GLB", use_selection=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, f"{NAME}.fbx"), use_selection=True, path_mode="COPY",
                         embed_textures=True, mesh_smooth_type="FACE")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"{NAME}.blend"))

# ---------------------------------------------------------------- previews
if RENDER:
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 1400, 1000
    sc.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("W"); sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.42, 0.55, 0.68, 1); bg.inputs[1].default_value = 0.9
    def light(name, loc, energy, size):
        ld = bpy.data.lights.new(name, "AREA"); ld.energy = energy; ld.size = size
        lo = bpy.data.objects.new(name, ld); lo.location = loc; sc.collection.objects.link(lo)
        tc = lo.constraints.new("TRACK_TO"); tc.target = fish
    light("Key", (6, 5, 8), 2200, 6); light("Fill", (-7, 2, 2), 700, 8); light("Rim", (0, -8, 5), 1200, 5)
    cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    tgt = bpy.data.objects.new("Tgt", None); sc.collection.objects.link(tgt)
    tc = cam.constraints.new("TRACK_TO"); tc.target = tgt
    views = {"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50), "side": ((12.5, 0, 0.6), (0, 0, 0.2), 50),
             "top": ((0, 0, 13), (0, 0, 0), 50), "front": ((2.2, 8.5, 1.0), (0, 1.5, 0.2), 40)}
    for nm, (loc, tg, lens) in views.items():
        cam.location = loc; tgt.location = tg; cam_d.lens = lens
        if nm == "top": cam.location = (0.0001, 0, 13)
        sc.render.filepath = os.path.join(OUT, "previews", f"{NAME}_{nm}.png")
        bpy.ops.render.render(write_still=True)
print("DONE")
