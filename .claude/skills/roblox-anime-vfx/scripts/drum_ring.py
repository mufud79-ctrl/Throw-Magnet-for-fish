"""Raijin drum ring: one gold horseshoe arch carrying 8 taiko drums, built procedurally in Blender.

    /tmp/bpyenv/bin/python drum_ring.py [--god GLB] [--out DIR] [--export]

References: assets/source_art/god_mode/drum_sheet_v1.png (the drum) and drum_ring_sheet_v1.png (frame,
finials, tassels; the user picked 8 drums with a gold crest between the top pair).

Built in the god model's own space (Blender Z-up, the god faces -Y, 1.9 units tall, centred at the origin) so
the ring sits behind his shoulders without any fitting step.

Parts (each its own mesh, rigidly skinned to one bone of the DrumRing armature):
  Frame            the arch, cloud lumps, scrolls, end hooks, flame finials, crest, drum posts -> bone Root
  Drum_1..Drum_8   barrel, skins, rims, rivets, bands; pivot at the drum centre       -> bone Drum_i
  Tassel_1..8      cap, cord, tassel; pivot at the top so it can sway                 -> bone Tassel_i (child of Drum_i)
Drums are numbered left to right over the top (as seen from the front), which is also the Drum Barrage order.
One 1024 texture atlas (painted greyscale-free colour; the prop is not recoloured) serves every part.

Writes to OUT (default assets/meshes/drum_ring/): drum_ring.blend, drum_ring.glb, drum.glb (one drum, for close
ups), drum_ring_atlas.png, drum_ring.json (part stats), and with --god a preview god_with_ring.glb.
--export also writes drum_ring.fbx for Roblox (only after the user approved the model).
"""
import os
import sys
import math
import json
import argparse
import numpy as np
from PIL import Image, ImageFilter
import bpy
import bmesh
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
TAU = 2 * math.pi
ROBLOX_TRI_CAP = 20000

# ---------------------------------------------------------------- layout (god space, units = god model units)
C = np.array([0.0, 0.0, 0.50])        # arch centre: behind the neck/shoulders
R = 0.80                              # arch radius (centre line of the band)
ARC = 145.0                           # band runs from -ARC to +ARC degrees (0 = straight up); hooks continue it
DRUM_ANG = [-125, -90, -55, -20, 20, 55, 90, 125]   # left to right over the top, seen from the front
DRUM_R = 0.17                         # drum radius (skin)
DRUM_L = 0.26                         # drum length (front skin to back skin)
DRUM_Y = 0.39                         # drum centre depth (behind the mane, which ends at +0.23)
BAND_Y = DRUM_Y + DRUM_L / 2 + 0.05   # band centre depth (just behind the back rims)
BAND_W, BAND_D = 0.055, 0.03         # half width (radial) and half depth of the band

# ---------------------------------------------------------------- atlas regions (u0, v0, u1, v1) in 0..1, v up
REG = {
    "skin":   (0.0, 0.5, 0.5, 1.0),
    "red":    (0.5, 0.75, 1.0, 1.0),
    "gold":   (0.5, 0.5, 1.0, 0.75),
    "band":   (0.5, 0.375, 1.0, 0.5),
    "tassel": (0.0, 0.0, 0.25, 0.5),
    "dark":   (0.25, 0.25, 0.5, 0.5),
    "cream":  (0.25, 0.0, 0.5, 0.25),
}
ATLAS = 1024


# ================================================================ texture atlas (painted)
def _noise(shape, scale, seed, octaves=4):
    rng = np.random.default_rng(seed)
    h, w = shape
    out = np.zeros(shape, np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = max(2, int(scale * 2 ** o))
        g = rng.standard_normal((s, s)).astype(np.float32)
        im = Image.fromarray(g).resize((w, h), Image.BICUBIC)
        out += amp * np.asarray(im)
        tot += amp
        amp *= 0.5
    out /= tot
    return (out - out.min()) / (np.ptp(out) + 1e-6)


def _lerp(a, b, t):
    t = t[..., None]
    return np.asarray(a, np.float32) * (1 - t) + np.asarray(b, np.float32) * t


def _hex(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def _tile_u(img):
    """Make an image wrap seamlessly in u: blend it with its mirror, weighted toward the edges."""
    w = img.shape[1]
    t = np.abs(np.linspace(-1, 1, w, dtype=np.float32)) ** 2
    t = t[None, :, None] if img.ndim == 3 else t[None, :]
    return img * (1 - 0.5 * t) + img[:, ::-1] * (0.5 * t)


def paint_skin(n):
    """Cream drumhead, black disc, gold three-comma tomoe (heads near the middle, tails sweeping outward)."""
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    x = (xx + 0.5) / n * 2 - 1
    y = 1 - (yy + 0.5) / n * 2
    r = np.hypot(x, y)
    aa = 2.5 / n
    cream = _lerp(_hex("#efe3c4"), _hex("#d9c79d"), _noise((n, n), 6, 11) * 0.8 + np.clip(r - 0.7, 0, 1))
    stain = _noise((n, n), 3, 12)
    cream = cream * (0.93 + 0.07 * stain[..., None])
    black = _lerp(_hex("#14131a"), _hex("#262532"), _noise((n, n), 10, 13) * 0.7)
    disc = np.clip((0.80 - r) / aa, 0, 1)
    # tomoe: union of discs along a spiral per comma
    tom = np.zeros((n, n), np.float32)
    for k in range(3):
        a0 = math.radians(90 + 120 * k)
        for t in np.linspace(0, 1, 420):
            ang = a0 - math.radians(150) * t                 # clockwise sweep
            rad = 0.27 + 0.42 * t ** 0.8
            w = 0.165 if t == 0 else 0.010 + 0.14 * (1 - t) ** 1.35
            cx, cy = rad * math.cos(ang), rad * math.sin(ang)
            d = np.hypot(x - cx, y - cy)
            tom = np.maximum(tom, np.clip((w - d) / aa, 0, 1))
    gold = _lerp(_hex("#b5821f"), _hex("#f1cd6a"), _noise((n, n), 8, 14) * 0.6 + 0.25 * (y * 0.5 + 0.5))
    # thin dark outline round the tomoe and the disc edge (painted, slightly soft)
    edge = np.clip(1 - np.abs(r - 0.80) / (aa * 3), 0, 1)
    img = cream
    img = _lerp(img, black, disc)
    img = _lerp(img, gold * 0.55, np.clip(edge * 0.9, 0, 1))
    tom_edge = np.clip(tom * (1 - tom) * 4, 0, 1)
    img = _lerp(img, gold, tom * disc)
    img = _lerp(img, gold * 0.45, tom_edge * disc * 0.8)
    return img


def paint_red(h, w):
    n = _noise((h, w), 5, 21)
    streak = np.asarray(Image.fromarray((_noise((h, 8), 6, 22) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)) / 255.0
    base = _lerp(_hex("#7e0f12"), _hex("#b8202a"), 0.55 * n + 0.45 * streak)
    return _tile_u(base)


def paint_gold(h, w, seed=31):
    n = _noise((h, w), 7, seed)
    m = _noise((h, w), 20, seed + 1)
    g = _lerp(_hex("#8c6116"), _hex("#e9c158"), np.clip(0.25 + 0.6 * n + 0.25 * (m > 0.7), 0, 1))
    hi = np.clip((m - 0.82) * 6, 0, 1)
    return _tile_u(_lerp(g, _hex("#fff0b8"), hi * 0.6))


def paint_band(h, w):
    """Gold strip with embossed cloud medallions along u (the band's length)."""
    g = paint_gold(h, w, 41)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    v = (yy + 0.5) / h
    u = (xx + 0.5) / w
    cells = 8
    cu = (u * cells) % 1.0 - 0.5
    cv = v - 0.5
    shade = np.zeros((h, w), np.float32)
    for (ox, oy, rr) in [(0, 0, 0.16), (-0.13, 0.08, 0.1), (0.13, 0.08, 0.1), (-0.12, -0.1, 0.1), (0.12, -0.1, 0.1)]:
        d = np.hypot(cu * 1.0 - ox, (cv - oy) * 0.5)
        ring = np.clip(1 - np.abs(d - rr) / 0.025, 0, 1)
        shade = np.maximum(shade, ring)
    border = np.clip(1 - np.minimum(v, 1 - v) / 0.06, 0, 1)
    g = g * (1 - 0.45 * shade[..., None]) * (1 - 0.35 * border[..., None])
    return g


def paint_tassel(h, w):
    xx = np.arange(w, dtype=np.float32)
    threads = 0.5 + 0.5 * np.sin(xx / w * TAU * 40 + _noise((1, w), 30, 51)[0] * 6)
    t = np.tile(threads, (h, 1)) * 0.6 + _noise((h, w), 12, 52) * 0.4
    return _lerp(_hex("#6e0c10"), _hex("#d0303a"), t)


def paint_atlas(path):
    img = np.zeros((ATLAS, ATLAS, 3), np.float32)

    def put(name, arr):
        u0, v0, u1, v1 = REG[name]
        x0, x1 = int(u0 * ATLAS), int(u1 * ATLAS)
        y0, y1 = int((1 - v1) * ATLAS), int((1 - v0) * ATLAS)
        img[y0:y1, x0:x1] = arr

    s = int(0.5 * ATLAS)
    put("skin", paint_skin(s))
    put("red", paint_red(int(0.25 * ATLAS), s))
    put("gold", paint_gold(int(0.25 * ATLAS), s))
    put("band", paint_band(int(0.125 * ATLAS), s))
    put("tassel", paint_tassel(s, int(0.25 * ATLAS)))
    put("dark", np.broadcast_to(_hex("#2a2016"), (int(0.25 * ATLAS), int(0.25 * ATLAS), 3)) * (0.8 + 0.4 * _noise((256, 256), 6, 61))[..., None])
    put("cream", paint_skin(s)[:256, :256] * 0 + _lerp(_hex("#efe3c4"), _hex("#d9c79d"), _noise((256, 256), 6, 71)))
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(path)
    return path


# ================================================================ geometry helpers (lists of verts/faces/uvs)
class Mesh:
    def __init__(self):
        self.V, self.F, self.UV = [], [], []

    def add(self, V, F, UV, region):
        u0, v0, u1, v1 = REG[region]
        o = len(self.V)
        self.V += [tuple(map(float, v)) for v in V]
        self.F += [tuple(k + o for k in f) for f in F]
        # inset 2 px so bilinear filtering never bleeds a neighbour region in
        pad = 2.0 / ATLAS
        self.UV += [[(u0 + pad + (u1 - u0 - 2 * pad) * min(max(a, 0), 1), v0 + pad + (v1 - v0 - 2 * pad) * min(max(b, 0), 1)) for a, b in c] for c in UV]
        return self

    def merge(self, other):
        o = len(self.V)
        self.V += other.V
        self.F += [tuple(k + o for k in f) for f in other.F]
        self.UV += other.UV
        return self

    def tris(self):
        return sum(len(f) - 2 for f in self.F)


def grid(f, nu, nv, closed_u=False, closed_v=False):
    """f(u, v) -> xyz on [0,1]^2. Quads; closed directions reuse the seam via duplicated verts (UV seam)."""
    us = np.linspace(0, 1, nu + 1)
    vs = np.linspace(0, 1, nv + 1)
    V = [f(u, v) for v in vs for u in us]
    idx = lambda i, j: j * (nu + 1) + i
    F, UV = [], []
    for j in range(nv):
        for i in range(nu):
            F.append((idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)))
            UV.append([(us[i], vs[j]), (us[i + 1], vs[j]), (us[i + 1], vs[j + 1]), (us[i], vs[j + 1])])
    return V, F, UV


def fan_cap(center, ring_pts, uv_center, ring_uv, flip=False):
    V = [center] + list(ring_pts)
    F, UV = [], []
    n = len(ring_pts)
    for i in range(n):
        a, b = 1 + i, 1 + (i + 1) % n
        f = (0, a, b) if not flip else (0, b, a)
        F.append(f)
        uvs = {0: uv_center, a: ring_uv[i], b: ring_uv[(i + 1) % n]}
        UV.append([uvs[k] for k in f])
    return V, F, UV


def frames_along(P, up_hint):
    """Tangent/normal/binormal per point of a polyline. up_hint is a fixed axis (planar curves)."""
    P = np.asarray(P, float)
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    B = np.tile(np.asarray(up_hint, float), (len(P), 1))
    N = np.cross(B, T)
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    B = np.cross(T, N)
    return T, N, B


def sweep(P, half_w, half_d, sides=8, up_hint=(0, 1, 0), caps=True, boxy=2.6):
    """Tube along polyline P; cross-section is a super-ellipse (boxy > 2 = squarer) of half_w (in-plane normal)
    by half_d (along up_hint). half_w/half_d: scalars or per-point arrays."""
    P = np.asarray(P, float)
    n = len(P)
    hw = np.broadcast_to(np.asarray(half_w, float), (n,))
    hd = np.broadcast_to(np.asarray(half_d, float), (n,))
    T, N, B = frames_along(P, up_hint)
    V, F, UV = [], [], []
    angs = np.linspace(0, TAU, sides + 1)
    for i in range(n):
        for a in angs:
            c, s = math.cos(a), math.sin(a)
            x = math.copysign(abs(c) ** (2 / boxy), c) * hw[i]
            y = math.copysign(abs(s) ** (2 / boxy), s) * hd[i]
            V.append(P[i] + N[i] * x + B[i] * y)
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    L /= L[-1] + 1e-12
    for i in range(n - 1):
        for k in range(sides):
            a, b = i * (sides + 1) + k, i * (sides + 1) + k + 1
            c, d = b + sides + 1, a + sides + 1
            F.append((a, b, c, d))
            UV.append([(L[i], k / sides), (L[i], (k + 1) / sides), (L[i + 1], (k + 1) / sides), (L[i + 1], k / sides)])
    if caps:
        for end, flip in ((0, True), (n - 1, False)):
            if hw[end] < 1e-4:
                continue
            ring = [V[end * (sides + 1) + k] for k in range(sides)]
            cv, cf, cu = fan_cap(P[end], ring, (0.5, 0.5), [(0.5 + 0.4 * math.cos(a), 0.5 + 0.4 * math.sin(a)) for a in angs[:-1]], flip=flip)
            o = len(V)
            V += cv
            F += [tuple(k + o for k in f) for f in cf]
            UV += cu
    return V, F, UV


def ellipsoid(c, r, nu=10, nv=6):
    c = np.asarray(c, float)
    r = np.broadcast_to(np.asarray(r, float), (3,))
    def f(u, v):
        th, ph = u * TAU, (v - 0.5) * math.pi
        return c + r * np.array([math.cos(ph) * math.cos(th), math.cos(ph) * math.sin(th), math.sin(ph)])
    V, F, UV = grid(f, nu, nv)
    return V, F, UV


def extrude_outline(pts2d, depth):
    """Flat 2D outline (list of (u, v)) -> closed slab, front at -depth/2 along local z. Triangulated faces."""
    bm = bmesh.new()
    vs = [bm.verts.new((u, v, 0.0)) for u, v in pts2d]
    face = bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=[face])
    ret = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    ext = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
    for v in ext:
        v.co.z += depth
    for v in bm.verts:
        v.co.z -= depth / 2
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.verts.ensure_lookup_table()
    V = [tuple(v.co) for v in bm.verts]
    us = [p[0] for p in pts2d]; vv = [p[1] for p in pts2d]
    u0, u1, v0, v1 = min(us), max(us), min(vv), max(vv)
    F, UV = [], []
    for f in bm.faces:
        idx = [v.index for v in f.verts]
        F.append(tuple(idx))
        UV.append([((V[k][0] - u0) / (u1 - u0 + 1e-9), (V[k][1] - v0) / (v1 - v0 + 1e-9)) for k in idx])
    bm.free()
    return V, F, UV


def place(V, origin, xaxis, yaxis, zaxis, scale=1.0):
    o = np.asarray(origin, float)
    M = np.stack([np.asarray(xaxis, float), np.asarray(yaxis, float), np.asarray(zaxis, float)], axis=1)
    return [tuple(o + M @ (np.asarray(v, float) * scale)) for v in V]


def arch_pt(deg, radius=R, y=BAND_Y):
    a = math.radians(deg)
    return np.array([C[0] + radius * math.sin(a), y, C[2] + radius * math.cos(a)])


def radial(deg):
    a = math.radians(deg)
    return np.array([math.sin(a), 0.0, math.cos(a)])


def tangent(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), 0.0, -math.sin(a)])


# ================================================================ parts
def flame_outline(asym=0.0):
    """Three-tongue flame finial (u lateral, v up; base at v=0, tip at v=1)."""
    half = [(0.16, 0.0), (0.24, 0.08), (0.27, 0.19), (0.22, 0.30), (0.30, 0.36), (0.40, 0.47), (0.43, 0.60),
            (0.34, 0.52), (0.24, 0.48), (0.21, 0.58), (0.19, 0.70), (0.13, 0.82), (0.06, 0.92)]
    right = [(u, v) for u, v in half]
    left = [(-u, v) for u, v in reversed(half)]
    pts = right + [(0.0 + asym, 1.0)] + left
    return pts


def build_frame():
    m = Mesh()
    # main band, sampled finely, slightly thicker at the top
    degs = np.linspace(-ARC, ARC, 121)
    P = [arch_pt(d) for d in degs]
    w = BAND_W * (1.0 + 0.25 * np.cos(np.radians(degs)) ** 2)
    m.add(*sweep(P, w, BAND_D, sides=8, up_hint=(0, 1, 0), caps=False), "gold")
    for side in (-1, 1):
        Pb = [arch_pt(d, R + side * (BAND_W * (1.0 + 0.25 * math.cos(math.radians(d)) ** 2) - 0.008), BAND_Y - BAND_D) for d in degs]
        m.add(*sweep(Pb, 0.009, 0.009, sides=6, caps=True), "gold")
    # end hooks: curl outward and up, tapering to a talon point
    for side in (-1, 1):
        end = arch_pt(side * ARC)
        t_end = tangent(side * ARC) * side            # direction of travel at the end
        out = radial(side * ARC)
        q = end + out * 0.13
        r0, r1 = 0.13, 0.025
        v0 = (end - q)[[0, 2]]
        phi0 = math.atan2(v0[1], v0[0])
        tan_plus = np.array([-math.sin(phi0), math.cos(phi0)])
        sgn = 1 if np.dot(tan_plus, t_end[[0, 2]]) > 0 else -1
        pts, wd = [], []
        for t in np.linspace(0, 1, 28):
            ph = phi0 + sgn * math.radians(250) * t
            rr = r0 + (r1 - r0) * t
            pts.append(np.array([q[0] + rr * math.cos(ph), BAND_Y, q[2] + rr * math.sin(ph)]))
            wd.append(w[0] * (1 - 0.9 * t ** 1.3))
        m.add(*sweep(pts, wd, np.array(wd) * BAND_D / BAND_W, sides=8, caps=True), "gold")
    # cloud lumps + scroll pairs in every gap between drums (and between the last drums and the hooks)
    gaps = [-ARC + 6] + [(a + b) / 2 for a, b in zip(DRUM_ANG[:-1], DRUM_ANG[1:]) if not (a < 0 < b)] + [ARC - 6]
    rng = np.random.default_rng(7)
    for g in gaps:
        for k, (dr, dd, s) in enumerate([(-0.05, -6, 0.055), (0.0, 4, 0.065), (0.05, -2, 0.05)]):
            c = arch_pt(g + dd, R + dr, BAND_Y - 0.005)
            m.add(*ellipsoid(c, (s, 0.03, s * 0.8), 10, 6), "gold")
        # pair of mirrored scrolls on the front face of the lumps
        for sgn in (-1, 1):
            base = arch_pt(g + sgn * 3.0, R + 0.01, BAND_Y - 0.045)
            tg, rd = tangent(g), radial(g)
            pts, wd = [], []
            for t in np.linspace(0, 1, 30):
                ph = sgn * (math.pi * 0.5 + TAU * 1.25 * t)
                rr = 0.05 * (1 - 0.8 * t)
                p2 = base + sgn * tg * 0.04 + (tg * math.cos(ph) * sgn + rd * math.sin(ph)) * rr
                pts.append(p2)
                wd.append(0.014 * (1 - 0.55 * t))
            m.add(*sweep(pts, wd, 0.013, sides=6, caps=True), "gold")
    # posts from the band to the back of each drum
    for d in DRUM_ANG:
        c = arch_pt(d, R, 0)
        P = [np.array([c[0], DRUM_Y + DRUM_L / 2 - 0.01, c[2]]), np.array([c[0], BAND_Y, c[2]])]
        m.add(*sweep(P, 0.035, 0.035, sides=8, up_hint=(0, 0, 1)), "dark")
    # flame finials behind each drum, poking out past the rim
    for d in DRUM_ANG:
        rd, tg = radial(d), tangent(d)
        base = arch_pt(d, R + DRUM_R - 0.01, BAND_Y - 0.01)
        V, F, UV = extrude_outline(flame_outline(), 0.03)
        m.add(place(V, base, tg, rd, (0, -1, 0), 0.21), F, UV, "gold")
        m.add(*ellipsoid(base, (0.025, 0.025, 0.025), 8, 5), "gold")
    # crest between the top pair: big flame on a knob and scroll pair
    base = arch_pt(0, R + BAND_W, BAND_Y - 0.012)
    V, F, UV = extrude_outline(flame_outline(), 0.035)
    m.add(place(V, base - np.array([0, 0, 0.01]), (1, 0, 0), (0, 0, 1), (0, -1, 0), 0.34), F, UV, "gold")
    m.add(*ellipsoid(base, (0.05, 0.035, 0.045), 12, 6), "gold")
    m.add(*ellipsoid(arch_pt(0, R, BAND_Y - 0.03), (0.05, 0.02, 0.05), 12, 6), "gold")
    return m


def build_drum():
    """One drum in local space: centre at the origin, axis along Y (front skin at -Y)."""
    m = Mesh()
    nu = 28
    bulge = 0.10

    def rad_at(t):                      # t: 0 front .. 1 back
        return DRUM_R * (1.0 + bulge * math.sin(math.pi * t))

    def barrel(u, v):
        a = u * TAU
        y = -DRUM_L / 2 + v * DRUM_L
        r = rad_at(v)
        return (r * math.cos(a), y, r * math.sin(a))

    m.add(*grid(barrel, nu, 8), "red")
    # skins (recessed slightly), planar UV into the tomoe region; back skin mirrored
    for y, flip in ((-DRUM_L / 2 + 0.006, False), (DRUM_L / 2 - 0.006, True)):
        ring = [(DRUM_R * 0.97 * math.cos(a), y, DRUM_R * 0.97 * math.sin(a)) for a in np.linspace(0, TAU, nu, endpoint=False)]
        # u from x (mirrored for the back so the tomoe reads correctly from behind), v from z
        ruv = [(0.5 + (0.5 if not flip else -0.5) * p[0] / DRUM_R * 1.0 / 0.97 * 0.97, 0.5 + 0.5 * p[2] / DRUM_R) for p in ring]
        V, F, UV = fan_cap((0, y, 0), ring, (0.5, 0.5), ruv, flip=not flip)
        m.add(V, F, UV, "skin")
    # rims (fat torus at both ends)
    for y in (-DRUM_L / 2, DRUM_L / 2):
        def rim(u, v, y=y):
            a, b = u * TAU, v * TAU
            rr, mr = DRUM_R * 1.02, DRUM_R * 0.085
            return ((rr + mr * math.cos(b)) * math.cos(a), y + mr * math.sin(b) * 1.1, (rr + mr * math.cos(b)) * math.sin(a))
        m.add(*grid(rim, nu, 6), "gold")
        # rivets: low domes on the rim's outer face
        for a in np.linspace(0, TAU, 22, endpoint=False):
            rr = DRUM_R * 1.02 + DRUM_R * 0.06
            c = (rr * math.cos(a), y + (0.011 if y > 0 else -0.011), rr * math.sin(a))
            V, F, UV = ellipsoid(c, (0.0095, 0.0095, 0.0095), 8, 4)
            m.add(V, F, UV, "gold")
    # two raised bands with embossed clouds (u runs round the drum)
    for t in (0.33, 0.67):
        y0 = -DRUM_L / 2 + t * DRUM_L
        def band(u, v, y0=y0, t=t):
            a = u * TAU
            hw = 0.027
            r = rad_at(t) + 0.006 + 0.004 * math.sin(math.pi * v)
            return (r * math.cos(a), y0 - hw + 2 * hw * v, r * math.sin(a))
        m.add(*grid(band, nu, 2), "band")
    return m


def build_tassel():
    """Local space: pivot (top) at the origin, hanging along -Z."""
    m = Mesh()
    m.add(*ellipsoid((0, 0, -0.012), (0.016, 0.016, 0.016), 8, 5), "gold")
    m.add(*sweep([(0, 0, -0.02), (0, 0, -0.05)], 0.006, 0.006, sides=6, up_hint=(1, 0, 0)), "tassel")
    m.add(*ellipsoid((0, 0, -0.058), (0.02, 0.02, 0.014), 8, 5), "gold")

    def skirt(u, v):
        a = u * TAU
        z = -0.065 - v * 0.12
        r = 0.016 + 0.022 * math.sqrt(v) - 0.006 * v
        return (r * math.cos(a), r * math.sin(a), z)
    m.add(*grid(skirt, 12, 5), "tassel")
    # close the bottom
    ring = [(0.032 * math.cos(a), 0.032 * math.sin(a), -0.185) for a in np.linspace(0, TAU, 12, endpoint=False)]
    m.add(*fan_cap((0, 0, -0.19), ring, (0.5, 0.0), [(i / 12, 0.05) for i in range(12)], flip=True), "tassel")
    return m


# ================================================================ Blender scene
def to_object(name, mesh, mat, origin=(0, 0, 0), sharp_deg=50):
    me = bpy.data.meshes.new(name)
    o = np.asarray(origin, float)
    me.from_pydata([tuple(np.asarray(v) - o) for v in mesh.V], [], mesh.F)
    uvl = me.uv_layers.new(name="UVMap")
    for poly, corners in zip(me.polygons, mesh.UV):
        for li, c in zip(poly.loop_indices, corners):
            uvl.data[li].uv = c
    me.validate()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.location = tuple(o)
    ob.data.materials.append(mat)
    # merge the duplicated seam verts that share a position (keeps UV seams, smooth shading across them)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    me.set_sharp_from_angle(angle=math.radians(sharp_deg))
    return ob


def make_material(atlas_path):
    mat = bpy.data.materials.new("DrumRing")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(atlas_path)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.42
    bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def build_scene(atlas_path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mat = make_material(atlas_path)
    stats = {}

    arm_data = bpy.data.armatures.new("DrumRing")
    arm = bpy.data.objects.new("DrumRing", arm_data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones
    root = eb.new("Root")
    root.head = tuple(C + np.array([0, BAND_Y, 0]))
    root.tail = tuple(C + np.array([0, BAND_Y, 0.25]))
    drum_centres, tassel_tops = [], []
    for i, d in enumerate(DRUM_ANG, 1):
        c = arch_pt(d, R, DRUM_Y)
        b = eb.new(f"Drum_{i}")
        b.head = tuple(c)
        b.tail = tuple(c + np.array([0, -0.15, 0]))          # points out of the front skin (recoil axis)
        b.parent = root
        top = c + np.array([0, 0, -DRUM_R * (1.0 + 0.10) - 0.005])
        t = eb.new(f"Tassel_{i}")
        t.head = tuple(top)
        t.tail = tuple(top + np.array([0, 0, -0.18]))
        t.parent = b
        drum_centres.append(c)
        tassel_tops.append(top)
    bpy.ops.object.mode_set(mode="OBJECT")

    def bind(ob, bone):
        ob.parent = arm
        vg = ob.vertex_groups.new(name=bone)
        vg.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
        mod = ob.modifiers.new("Armature", "ARMATURE")
        mod.object = arm

    frame = build_frame()
    ob = to_object("Frame", frame, mat)
    bind(ob, "Root")
    stats["Frame"] = len(ob.data.polygons), sum(len(p.vertices) - 2 for p in ob.data.polygons)
    drum = build_drum()
    tassel = build_tassel()
    for i, (c, top) in enumerate(zip(drum_centres, tassel_tops), 1):
        dm = Mesh().merge(drum)
        dm.V = [tuple(np.asarray(v) + c) for v in dm.V]
        ob = to_object(f"Drum_{i}", dm, mat, origin=c)
        bind(ob, f"Drum_{i}")
        stats[f"Drum_{i}"] = len(ob.data.polygons), sum(len(p.vertices) - 2 for p in ob.data.polygons)
        tm = Mesh().merge(tassel)
        tm.V = [tuple(np.asarray(v) + top) for v in tm.V]
        ob = to_object(f"Tassel_{i}", tm, mat, origin=top)
        bind(ob, f"Tassel_{i}")
        stats[f"Tassel_{i}"] = len(ob.data.polygons), sum(len(p.vertices) - 2 for p in ob.data.polygons)
    for k, (polys, tris) in stats.items():
        assert tris <= ROBLOX_TRI_CAP, (k, tris)
    return arm, stats


def export_glb(path, objects=None):
    bpy.ops.object.select_all(action="DESELECT")
    if objects:
        for o in objects:
            o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=bool(objects),
                              export_apply=False, export_skins=True, export_animations=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "assets", "meshes", "drum_ring"))
    ap.add_argument("--god", default=None, help="god GLB to import for a preview GLB with the ring")
    ap.add_argument("--export", action="store_true", help="also write the Roblox FBX (after approval)")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    os.makedirs(a.out, exist_ok=True)
    atlas = paint_atlas(os.path.join(a.out, "drum_ring_atlas.png"))
    arm, stats = build_scene(atlas)
    total = sum(t for _, t in stats.values())
    print(json.dumps({k: {"polys": p, "tris": t} for k, (p, t) in stats.items()}, indent=0))
    print("total tris", total)
    with open(os.path.join(a.out, "drum_ring.json"), "w") as f:
        json.dump({"parts": {k: {"polys": p, "tris": t} for k, (p, t) in stats.items()}, "total_tris": total,
                   "drum_angles_deg": DRUM_ANG, "arch_centre": C.tolist(), "arch_radius": R,
                   "units": "god model units (god is 1.9 tall); Blender Z-up, front -Y"}, f, indent=1)
    export_glb(os.path.join(a.out, "drum_ring.glb"))
    # single drum (for close-ups)
    d1 = bpy.data.objects["Drum_4"]
    export_glb(os.path.join(a.out, "drum.glb"), [d1])
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(a.out, "drum_ring.blend"))
    if a.export:
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.export_scene.fbx(filepath=os.path.join(a.out, "drum_ring.fbx"), use_selection=False,
                                 add_leaf_bones=False, axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True)
    if a.god:
        bpy.ops.import_scene.gltf(filepath=a.god)
        export_glb(os.path.join(a.out, "god_with_ring.glb"))


if __name__ == "__main__":
    main()
