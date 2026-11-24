"""Reusable anime VFX texture library, painted with photocraft.

    /tmp/bpyenv/bin/python vfx_textures.py [name ...] [--out DIR] [--previews]

Output (in assets/textures/ by default):
  layered textures -> <name>_glow.png, <name>_rim.png, <name>_mid.png, <name>_core.png
                      white layers: one ParticleEmitter per layer, same motion, different Color/LightEmission
  shaded textures  -> <name>.png   greyscale RGB carries painted light/shadow, Color tints it
Flipbooks are 4x4 (16 frames, 256 px cells, 1024 px sheet) unless the table says otherwise.

Every texture is generic on purpose (fire, smoke, dust, flash, rays, flecks, embers, rings, wind, slash,
cracks, lightning, beam, orb, wisps, speed lines) so one library serves every element: colour comes
from the emitter, not the PNG. See references/texture-library.md for the catalogue and Roblox settings.
"""
import os
import sys
import math
import argparse
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import photocraft as pc  # noqa: E402
from photocraft import SS, ss, levels, blur, mblur, coords, polar_of, noise, tnoise, lobes, shade  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "textures")
CELL = 256
S = CELL * SS          # working resolution of one cell
TAU = 2 * math.pi


def ease_out(t, p=3):
    return 1 - (1 - min(max(t, 0), 1)) ** p


def scroll(field, i, n, axis=0, frac=1.0):
    """Slice a tall/wide pre-made noise so features drift between frames (upward when axis=0)."""
    if axis == 0:
        h = field.shape[0] - S
        o = int(h * (1 - (i / max(1, n - 1)) * frac))
        return field[o:o + S, :S]
    w = field.shape[1] - S
    o = int(w * (i / max(1, n - 1)) * frac)
    return field[:S, o:o + S]


# ================================================================ FIRE
def fire_burst(n=16, seed=3):
    """Billowing anime explosion fire: a cluster of lobes blooms out fast, rolls upward with painted
    volume (lit top-left, hot core), the top tears into tongues, then the mass breaks up and burns out.
    Layered."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    base = [(0.0, -0.05, 0.42)]
    for k in range(13):
        a = rng.uniform(0, TAU)
        d = rng.uniform(0.18, 0.5)
        base.append((math.cos(a) * d, math.sin(a) * d * 0.85 + 0.04, rng.uniform(0.2, 0.34)))
    big1 = noise(S * 2, S, 150, 150, seed + 1, 3)
    big2 = noise(S * 2, S, 150, 150, seed + 2, 3)
    det = noise(S * 2, S, 34, 30, seed + 3, 4)
    tong = noise(S * 2, S, 110, 22, seed + 4, 3)
    frames = []
    for i in range(n):
        t = i / (n - 1)
        g = 0.42 + 0.58 * ease_out(t / 0.45)
        rise = t * 0.16
        cs = [(cx * g, cy * g + rise * (1.0 + cy), r * (0.55 + 0.45 * g)) for cx, cy, r in base]
        w1, w2 = scroll(big1, i, n, frac=0.5), scroll(big2, i, n, frac=0.5)
        xw = x + (w1 - 0.5) * 0.26
        yw = y + (w2 - 0.5) * 0.26
        F = lobes(xw, yw, cs, 1.15)
        d = scroll(det, i, n, frac=0.8)
        tg = scroll(tong, i, n, frac=1.0)
        upper = ss(y, -0.2, 0.55)
        near = ss(F, 0.05, 0.45)                        # tongues only grow out of the body
        H = F + (d - 0.5) * (0.35 + 0.55 * t) * near + (tg - 0.5) * 0.65 * upper * near - (0.12 + 0.95 * t ** 1.35)
        # painted gradient from the silhouette inward: thin rim, orange body, hot core deep inside
        edgeA = ss(H, 0.0, 0.05)
        dist = ndi.distance_transform_edt(H > 0)
        depth = 1 - np.exp(-dist / (S * (0.055 - 0.02 * t)))
        Fs = blur(F, 4)
        vol = shade(Fs, light=(-0.45, 0.85, 0.5), strength=75)
        crev = ss(Fs, 0.3, 0.9)
        I = edgeA * (0.22 + 0.78 * depth) * (0.5 + 0.62 * vol) * (0.78 + 0.22 * crev) * (1.08 - 0.4 * t)
        I = np.clip(I + 0.25 * ss(F, 1.2, 2.6) * (1 - t) ** 1.5 * edgeA, 0, 1)
        frames.append(I)
    return frames


def flame_lick(n=16, seed=11, width=0.5, tongues=1.0):
    """Looping column of rising flame tongues (burning ground, fire pillars, fists on fire). The noise
    scrolls exactly one period, so FlipbookMode = Loop is seamless. Layered."""
    x, y = coords(S)
    tall = tnoise(S, S, 200, 70, seed, 4)
    tg = tnoise(S, S, 150, 34, seed + 1, 3)
    wx = tnoise(S, S, 260, 260, seed + 2, 2)
    frames = []
    for i in range(n):
        o = int(S * i / n)
        a = np.roll(tall, -o, axis=0)
        b = np.roll(tg, -o * 2 % S, axis=0)
        c = np.roll(wx, -o, axis=0)
        h01 = (y + 1) / 2
        xw = x + (c - 0.5) * 0.35 * (0.2 + h01)
        wdt = width * (1 - h01) ** 0.75 + 0.03
        body = 1 - np.abs(xw) / wdt
        H = body * 0.9 + (a - 0.5) * (0.4 + 0.6 * h01) + (b - 0.5) * 0.9 * tongues * h01 - 0.15 - 0.55 * h01
        H *= ss(y, -1.0, -0.82)
        I = levels(H, 0.0, 0.5, 0.8)
        I = np.clip(I * (0.75 + 0.35 * (1 - h01)), 0, 1)
        frames.append(I)
    return frames


def aura_wisp(n=16, seed=21):
    """Thin rising aura wisps (haki, awakening, charge-ups). Loop. Layered."""
    return flame_lick(n, seed, width=0.32, tongues=1.6)


# ================================================================ SMOKE / DUST (shaded)
def _cloud_height(x, y, spheres):
    h = np.zeros_like(x)
    for cx, cy, r in spheres:
        d2 = (x - cx) ** 2 + (y - cy) ** 2
        h = np.maximum(h, np.sqrt(np.clip(r * r - d2, 0, None)))
    return h


def _cloud_frames(n, seed, layout, flatten=None, spread=(1.0, 1.0)):
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    spheres = layout(rng)
    edge = noise(S, S, 60, 60, seed + 5, 3)
    holes = noise(S, S, 70, 70, seed + 6, 4)
    alphas, values = [], []
    for i in range(n):
        t = i / (n - 1)
        g = 0.35 + 0.65 * ease_out(t / 0.55)
        sp = [(cx * g * spread[0], cy * g * spread[1] + t * 0.06, r * (0.55 + 0.45 * g)) for cx, cy, r in spheres]
        xw = x + (edge - 0.5) * 0.07
        yw = y + (edge - 0.5) * 0.07
        h = _cloud_height(xw, yw, sp)
        if flatten is not None:
            h *= ss(y, flatten - 0.02, flatten + 0.06)
        lam = shade(blur(h, 3.5), light=(-0.45, 0.65, 0.75), strength=150)
        occl = ss(h, 0.0, 0.16)                       # crevices between lobes go darker
        tone = pc.soft_posterize(np.clip(lam * 1.25 * (0.8 + 0.2 * occl), 0, 1), 3, softness=0.06)
        val = 0.6 + 0.4 * tone
        # thin warm-white rim on the lit side, bluish core shadow stays mid-grey
        rim = ss(h, 0.0, 0.03) * (1 - ss(h, 0.03, 0.08)) * ss(lam, 0.5, 0.8)
        val = np.clip(val + rim * 0.15, 0, 1)
        a = ss(h, 0.0, 0.012)
        diss = max(0.0, (t - 0.35) / 0.65)
        a *= ss(holes + 0.25 * (1 - h / (h.max() + 1e-6)), diss * 1.15, diss * 1.15 + 0.08)
        alphas.append(a * (1 - 0.25 * diss))
        values.append(val)
    return alphas, values


def smoke_puff(n=16, seed=31):
    """White anime cloud puff: cauliflower of round lobes, painted 3-tone shading (lit / mid / cool
    shadow), expands, then dissolves into holes. Shaded."""
    def layout(rng):
        sp = [(0, -0.02, 0.36), (-0.12, 0.1, 0.3), (0.14, 0.06, 0.3)]
        for _ in range(16):
            a = rng.uniform(0, TAU)
            d = rng.uniform(0.28, 0.46)
            sp.append((math.cos(a) * d, math.sin(a) * d * 0.82, rng.uniform(0.12, 0.22)))
        return sp
    return _cloud_frames(n, seed, layout)


def dust_burst(n=16, seed=41):
    """Ground dust thrown out sideways and up from an impact: low wide mass of lumpy lobes with a flat
    base, rolling outward. Shaded."""
    def layout(rng):
        sp = [(-0.18, -0.25, 0.3), (0.16, -0.22, 0.32), (0.0, -0.05, 0.3)]
        for k in range(18):
            u = rng.uniform(-1, 1)
            hgt = (1 - u * u) ** 0.8
            sp.append((u * 0.68, -0.4 + hgt * rng.uniform(0.1, 0.5), rng.uniform(0.11, 0.22) * (1.15 - 0.45 * abs(u))))
        return sp
    return _cloud_frames(n, seed, layout, flatten=-0.52, spread=(1.2, 1.0))


# ================================================================ FLASH / RAYS / ORB
def star_flash(n=16, seed=51):
    """Sharp multi-spike impact star: snaps open in 2 frames, spikes thin and retract, core fades. Layered."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    r, a = polar_of(x, y)
    spikes = [(rng.uniform(0, TAU), rng.uniform(0.75, 0.98), rng.uniform(0.035, 0.06)) for _ in range(6)]
    spikes += [(rng.uniform(0, TAU), rng.uniform(0.3, 0.62), rng.uniform(0.015, 0.03)) for _ in range(16)]
    frames = []
    for i in range(n):
        t = i / (n - 1)
        g = min(1.0, (i + 1) / 2.5)
        thin = (1 - t) ** 1.2
        F = np.zeros_like(x)
        for ang, L, w in spikes:
            da = np.angle(np.exp(1j * (a - ang)))
            Lk = L * g * (1 - 0.35 * t)
            wd = w * thin * (1 - np.clip(r / Lk, 0, 1)) ** 1.15
            F = np.maximum(F, ss(np.abs(da) * r, wd + 0.004, wd * 0.25) * (r < Lk))
        core = 1 - ss(r, 0.06, 0.2 * thin + 0.08)
        F = np.maximum(F, core * thin)
        F = pc.radial_smudge(F, S / 2, S / 2, 0.08, 10) * 0.6 + F * 0.6
        frames.append(np.clip(F, 0, 1))
    return frames


def god_rays(n=16, seed=61):
    """Radial streaks shooting out of an impact (world-space rays). Rays extend fast, then thin and fade.
    Layered. Use Orientation = FacingCamera for a sunburst or VelocityPerpendicular for a flat fan."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    r, a = polar_of(x, y)
    rays = [(rng.uniform(0, TAU), rng.uniform(0.5, 1.0), rng.uniform(0.012, 0.05), rng.uniform(0.4, 1.0)) for _ in range(26)]
    streak = noise(S, S, 8, 90, seed + 1, 3)
    frames = []
    for i in range(n):
        t = i / (n - 1)
        g = ease_out(t / 0.25, 2)
        F = np.zeros_like(x)
        for ang, L, w, op in rays:
            da = np.abs(np.angle(np.exp(1j * (a - ang))))
            Lk = L * (0.25 + 0.75 * g)
            wd = w * (1 - 0.6 * t) * (0.4 + r)
            ray = ss(da, wd, wd * 0.15) * ss(r, Lk, Lk * 0.55) * ss(r, 0.05, 0.16) * op
            F = np.maximum(F, ray)
        F *= 0.75 + 0.5 * streak
        F *= (1 - t) ** 0.9
        frames.append(np.clip(F, 0, 1))
    return frames


def orb_glow(n=16, seed=63):
    """Churning anime energy ball (loop): white-hot core, swirling streaks inside the body, a bright
    rim, and short flame-like tongues licking off the edge. Angle-periodic noise rolls one full period,
    so FlipbookMode = Loop is seamless. Layered."""
    H, W = 256, 1024
    sw = tnoise(H, W, 40, 160, seed, 4)            # rows = radius (outer -> centre), cols = angle
    tg = tnoise(H, W, 140, 70, seed + 1, 3)
    wob = tnoise(1, W, 1, 180, seed + 2, 2)[0]
    v = np.linspace(0, 1, H)[:, None]              # 0 = outer limit (r=0.98), 1 = centre
    frames = []
    for i in range(n):
        o = int(W * i / n)
        a = np.roll(sw, -o, axis=1)
        b = np.roll(tg, o * 2 % W, axis=1)
        w = np.roll(wob, -o)[None, :]
        r = 0.98 * (1 - v)                          # actual radius of each row
        edge = 0.46 + 0.035 * (w - 0.5) * 2         # wobbly silhouette
        inside = ss(r, edge + 0.012, edge - 0.012)
        body = inside * (0.5 + 0.32 * a + 0.25 * ss(r, edge * 0.55, 0.0))
        rim = ss(np.abs(r - (edge - 0.03)), 0.035, 0.006) * 0.95
        tl = 0.05 + 0.32 * levels(b, 0.35, 0.95)
        out = np.clip((r - edge) / tl, 0, 1)
        tongues = ss(r, edge - 0.02, edge + 0.01) * ss(out, 1.0, 0.75) * (1 - out) ** 0.8 * 0.8 * (tl > 0.07)
        core = ss(r, 0.2, 0.04) * np.ones_like(a)
        I = np.clip(np.maximum.reduce([body, rim, tongues, core]), 0, 1)
        I = mblur(I, 2, axis=0)
        frames.append(pc.polar_strip(I, S, 0.98, 0.0, 0.0, TAU))
    return frames


# ================================================================ FLECKS / EMBERS
def _poly_mask(pts, size):
    big = Image.new("L", (size, size), 0)
    ImageDraw.Draw(big).polygon([tuple(p) for p in pts], fill=255)
    return np.asarray(big, np.float32) / 255


def _painted(mask, soft=1.2):
    return np.clip(blur(mask, soft), 0, 1)


def flecks():
    """2x2 sheet of painted sparks, each with a hot centre and a soft painted halo: (1) uneven 4-point
    glint, (2) needle spark with a smear trail, (3) faceted light chip (lit / shadow face, rim
    highlight), (4) crystal shard with a tip glint. Shaded (grey value = painted tone).
    FlipbookLayout Grid2x2 + FlipbookStartRandom to mix them in one emitter."""
    rng = np.random.default_rng(73)
    x, y = coords(S)
    r, a = polar_of(x, y)
    alphas, vals = [], []
    # 1 glint: uneven arms, slightly off-axis, concave taper, small diagonal arms
    F = np.zeros_like(x)
    for k, L in enumerate([0.92, 0.52, 0.78, 0.46]):
        ang = k * math.pi / 2 + rng.uniform(-0.08, 0.08)
        da = np.abs(np.angle(np.exp(1j * (a - ang))))
        wd = 0.07 * (1 - np.clip(r / L, 0, 1)) ** 2.2
        F = np.maximum(F, ss(da * r, wd + 0.004, wd * 0.2) * (r < L))
    for k in range(4):
        ang = math.pi / 4 + k * math.pi / 2 + rng.uniform(-0.1, 0.1)
        da = np.abs(np.angle(np.exp(1j * (a - ang))))
        wd = 0.03 * (1 - np.clip(r / 0.3, 0, 1)) ** 2
        F = np.maximum(F, 0.8 * ss(da * r, wd + 0.003, wd * 0.2) * (r < 0.3))
    core = ss(r, 0.12, 0.02)
    halo = blur(F, S * 0.02) * 0.6 + np.exp(-r * 7) * 0.5
    alphas.append(np.clip(np.maximum.reduce([F, core, halo]), 0, 1))
    vals.append(np.clip(0.62 + 0.38 * np.maximum(core, F * ss(r, 0.5, 0.0)), 0, 1))
    # 2 needle spark: bright teardrop head at the top, smeared tail downward
    head = ss(np.hypot(x / 0.11, (y - 0.4) / 0.24), 1.0, 0.6)
    tail = ss(np.abs(x) / (0.09 * np.clip((y + 0.85) / 1.25, 0, 1) + 1e-3), 1.0, 0.35) * ss(y, -0.85, 0.3) * (y < 0.45)
    tail = mblur(tail, S * 0.02, axis=0) * np.clip((y + 0.85) / 1.3, 0, 1)
    F = np.maximum(head, tail * 0.85)
    halo = blur(F, S * 0.03) * 0.55
    alphas.append(np.clip(np.maximum(F, halo), 0, 1))
    vals.append(np.clip(0.6 + 0.4 * np.maximum(head, tail * ss(y, -0.3, 0.4)), 0, 1))
    # 3 light chip: soft-cornered, slightly irregular square, glowing hot from the centre out
    nz = noise(S, S, 50, 50, 77, 3)
    th = 0.3
    xr, yr = x * math.cos(th) - y * math.sin(th), x * math.sin(th) + y * math.cos(th)
    sq = np.maximum(np.abs(xr) * 1.05, np.abs(yr)) + (nz - 0.5) * 0.05
    m = ss(sq, 0.34, 0.3)
    inner = ss(sq, 0.3, 0.02)
    lit = 0.12 * ss(xr - yr, -0.3, 0.3)                       # one side catches more light
    halo = blur(m, S * 0.05) * 0.5
    alphas.append(np.clip(np.maximum(m, halo), 0, 1))
    vals.append(np.clip(np.where(m > 0.3, 0.6 + 0.3 * inner + lit + 0.15 * ss(sq, 0.12, 0.0), 0.62), 0, 1))
    # 4 crystal shard: tapered sliver, bright at the tip fading down its length, soft painted edges, tip glint
    th = 0.25
    xr, yr = x * math.cos(th) - y * math.sin(th), x * math.sin(th) + y * math.cos(th)
    w = 0.12 * np.clip((0.8 - yr) / 1.4, 0, 1) ** 0.6 * np.clip((yr + 0.8) / 0.25, 0, 1)
    m = ss(np.abs(xr) - w, 0.012, -0.012) * (np.abs(yr) < 0.8)
    m = blur(m, 1.6)
    along = np.clip((yr + 0.8) / 1.6, 0, 1)
    tx, ty = -math.sin(-th) * 0.62, math.cos(-th) * 0.62
    rr, aa = polar_of(x - tx, y - ty)
    gl = np.zeros_like(x)
    for ang in (0, math.pi / 2):
        da = np.abs(np.angle(np.exp(1j * (aa - ang))))
        da = np.minimum(da, math.pi - da)
        gl = np.maximum(gl, ss(da * rr, 0.025 * (1 - np.clip(rr / 0.26, 0, 1)) ** 2 + 0.003, 0.0) * (rr < 0.26))
    gl = np.maximum(gl, ss(rr, 0.06, 0.0))
    halo = blur(np.maximum(m, gl), S * 0.03) * 0.5
    alphas.append(np.clip(np.maximum.reduce([m * (0.55 + 0.45 * along), gl, halo]), 0, 1))
    vals.append(np.clip(0.6 + 0.4 * np.maximum(along ** 1.5 * (m > 0.3), gl), 0, 1))
    return alphas, vals


def embers(n=16, seed=71):
    """16 painted ember flakes (use FlipbookStartRandom): torn, irregular outlines from warped
    ellipses with a pointed tail, a glowing hot centre, a charred darker edge on one side and, on some,
    a fold line splitting two facets. Faint baked halo. Shaded."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    alphas, vals = [], []
    for i in range(n):
        rot = rng.uniform(0, TAU)
        el = rng.uniform(1.6, 3.0)
        xr, yr = x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot)
        nz = noise(S, S, rng.uniform(40, 80), rng.uniform(40, 80), seed * 10 + i, 3)
        tailw = 1 + 0.9 * ss(xr, 0.0, 0.5)                  # one end drawn out into a point
        d = np.hypot(xr / (0.5 * el / 2.2), yr * tailw / 0.24)
        field = 1 - d + (nz - 0.5) * 0.75
        m = ss(field, 0.0, 0.05)
        dist = ndi.distance_transform_edt(field > 0)
        depth = dist / (dist.max() + 1e-6)
        val = 0.42 + 0.58 * levels(depth, 0.05, 0.75, 0.75)
        char = ss(yr + (nz - 0.5) * 0.15, -0.05, -0.18)          # charred band on one side
        val = val * (1 - 0.4 * char)
        if rng.random() < 0.5:                                  # fold: two facets
            val = val * np.where(xr * 0.6 + yr > 0, 1.0, 0.82)
        halo = blur(m, S * 0.03) * 0.3
        alphas.append(np.clip(np.maximum(m, halo), 0, 1))
        vals.append(np.clip(np.where(m > 0.5, val, 0.6), 0, 1))
    return alphas, vals


# ================================================================ RINGS / WIND / SLASH (strokes)
def shock_ring():
    """Painted shockwave ring: crisp bright inner edge, streaky energy feathering outward. Layered."""
    H, W = 256, 2048
    st = tnoise(H, W, 30, 300, 81, 4)
    fine = tnoise(H, W, 10, 120, 82, 3)
    v = np.linspace(0, 1, H)[:, None]                  # 0 = outer edge, 1 = inner edge
    body = ss(v, 0.0, 0.75) * ss(v, 1.0, 0.94)
    feather = levels(v + (st - 0.5) * 0.9, 0.15, 0.95)
    edge = ss(v, 0.8, 0.93) * ss(v, 1.0, 0.95)
    I = np.clip(body * feather * (0.55 + 0.6 * fine) + edge * 0.9, 0, 1)
    I = mblur(I, 6, axis=1)
    return pc.polar_strip(I, S, 0.97, 0.55, 0.0, TAU)


def _stroke_strip(H, W, seed, lines=7, hot_edge=True):
    """A painted stroke strip: pressure taper along u, several streak filaments across v."""
    rng = np.random.default_rng(seed)
    u = np.linspace(0, 1, W)[None, :]
    v = np.linspace(0, 1, H)[:, None]
    I = np.zeros((H, W), np.float32)
    for k in range(lines):
        c = rng.uniform(0.1, 0.9)
        w = rng.uniform(0.03, 0.12)
        u0 = rng.uniform(0, 0.25)
        u1 = rng.uniform(0.6, 1.0)
        prof = ss(np.abs(v - c), w, w * 0.3)
        p = pc.taper((u - u0) / (u1 - u0), 0.1, 0.65) * ((u >= u0) & (u <= u1))
        I = np.maximum(I, prof * p * rng.uniform(0.55, 1.0))
    if hot_edge:
        I = np.maximum(I, ss(v, 0.18, 0.02) * pc.taper(u, 0.06, 0.7) * 1.0)
    I *= 0.7 + 0.5 * noise(H, W, 12, 160, seed + 3, 3)
    return np.clip(mblur(I, 5, axis=1), 0, 1)


def wind_arcs():
    """2x2 sheet of white wind arcs (swirls around ice/air moves, dash wind). Single white."""
    out = []
    for k, (sweep, ro, ri) in enumerate([(200, 0.9, 0.62), (150, 0.85, 0.7), (250, 0.92, 0.5), (120, 0.8, 0.66)]):
        strip = _stroke_strip(160, 900, 91 + k, lines=5, hot_edge=True)
        out.append(pc.polar_strip(strip, S, ro, ri, math.radians(170 - k * 25), math.radians(sweep)))
    return out


def slash(n=16, seed=101):
    """Painted crescent slash. The blade front travels along the arc over 4 frames (thick, white-hot,
    pointed), the trail behind it thins to a hairline, then the trail erodes from the swing start toward
    the front with a ragged dissolve. Layered. Final pose: front at the right (angle 0), trail sweeping
    counter-clockwise over the top; rotate/mirror the particle to aim it."""
    H, W = 300, 1400
    u = np.linspace(0, 1, W)[None, :]          # 0 = end of swing (right), 1 = swing start
    v = np.linspace(0, 1, H)[:, None]          # 0 = outer edge, 1 = inner edge
    st = noise(H, W, 26, 260, seed + 1, 4)
    feather = noise(H, W, 34, 110, seed + 2, 3)
    dis = noise(H, W, 30, 70, seed + 3, 4)
    frames = []
    for i in range(n):
        t = i / (n - 1)
        front = 1 - ease_out((i + 1) / 4.5, 2.2)
        erode = max(0.0, (t - 0.2) / 0.8) ** 1.05
        back = 1 - erode * (1 - front + 0.02)
        q = np.clip((u - front) / max(1e-3, back - front), 0, 1)
        inside = (u >= front) & (u <= back)
        # thickness: pointed tip, fat just behind the front, long taper to a hairline
        thick = (ss(u - front, 0.0, 0.07) * (1 - q) ** 1.15) * (1.0 - 0.3 * t)
        inner = thick * (1 + (feather - 0.5) * 0.5)
        body = ss(v, inner, inner * 0.55)
        grad = 1 - 0.55 * levels(v / np.maximum(thick, 1e-3), 0.15, 1.0)   # bright outer, falling inward
        streak = 0.82 + 0.3 * (st - 0.5)
        edge = ss(v, 0.12, 0.03) * ss(u - front, 0.0, 0.05) * (1 - q) ** 0.8
        I = np.maximum(body * grad * streak, edge) * inside
        I *= ss(u + (dis - 0.5) * 0.22 * (erode > 0), back + 0.03, back - 0.05)   # ragged tail
        I *= 1 - 0.35 * t
        frames.append(pc.polar_strip(np.clip(I, 0, 1), S, 0.93, 0.48, 0.0, math.radians(230))[::-1, :])
    return frames


# ================================================================ CRACKS / LIGHTNING
def _walk(rng, p, ang, step, n, jitter):
    pts = [p]
    for _ in range(n):
        ang += rng.uniform(-jitter, jitter)
        p = (p[0] + math.cos(ang) * step, p[1] + math.sin(ang) * step)
        pts.append(p)
    return pts, ang


def _lines_to_field(polys, size, widths):
    big = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(big)
    for pts, w in zip(polys, widths):
        for j in range(len(pts) - 1):
            ww = max(1, int(w * (1 - 0.7 * j / max(1, len(pts) - 1))))
            d.line([pts[j], pts[j + 1]], fill=255, width=ww)
            d.ellipse([pts[j + 1][0] - ww / 2, pts[j + 1][1] - ww / 2, pts[j + 1][0] + ww / 2, pts[j + 1][1] + ww / 2], fill=255)
    return np.asarray(big, np.float32) / 255


def _glow_lines(line, size):
    """Painted energy line: hot core + inner halo + wide bloom -> intensity."""
    halo = blur(line, size * 0.006)
    bloom = blur(line, size * 0.025)
    return np.clip(line * 1.0 + halo * 0.9 + bloom * 1.6, 0, 1)


def crack_glow(seed=111):
    """Glowing ground/air fissures radiating from a centre with branches and loose fragments. Layered.
    Quake ground cracks, magma vents, glass-shatter cores."""
    rng = np.random.default_rng(seed)
    c = S / 2
    polys, widths = [], []
    for k in range(10):
        ang = k / 10 * TAU + rng.uniform(-0.3, 0.3)
        pts, a2 = _walk(rng, (c, c), ang, S * 0.022, int(rng.uniform(12, 21)), 0.45)
        polys.append(pts)
        widths.append(S * 0.011)
        for j in range(3, len(pts) - 3, 4):
            if rng.random() < 0.6:
                bp, _ = _walk(rng, pts[j], a2 + rng.choice([-1, 1]) * rng.uniform(0.5, 1.1), S * 0.016, int(rng.uniform(3, 8)), 0.5)
                polys.append(bp)
                widths.append(S * 0.006)
    line = _lines_to_field(polys, S, widths)
    frag = np.zeros_like(line)
    for _ in range(26):
        a, d = rng.uniform(0, TAU), rng.uniform(0.15, 0.45) * S
        px, py = c + math.cos(a) * d, c + math.sin(a) * d
        s = rng.uniform(0.006, 0.014) * S
        pts = [(px + math.cos(b) * s * rng.uniform(0.6, 1.4), py + math.sin(b) * s * rng.uniform(0.6, 1.4)) for b in np.linspace(0, TAU, 5)[:-1] + rng.uniform(0, 1)]
        frag = np.maximum(frag, _poly_mask(pts, S))
    I = _glow_lines(np.maximum(line, frag), S)
    x, y = coords(S)
    r, _ = polar_of(x, y)
    return I * ss(r, 1.0, 0.8)


def glass_shatter(seed=121):
    """Shattered-air pane (quake punch): radial cracks + broken concentric rings, faint pane facets
    with refraction highlights. Layered."""
    rng = np.random.default_rng(seed)
    c = S / 2
    rays = 13
    angs = np.sort(rng.uniform(0, TAU, rays))
    polys, widths, ray_pts = [], [], []
    for ang in angs:
        pts, _ = _walk(rng, (c, c), ang, S * rng.uniform(0.028, 0.038), 13, 0.22)
        polys.append(pts)
        widths.append(S * 0.008)
        ray_pts.append(pts)
    for k in range(rays):
        for ring in sorted(rng.choice(np.arange(2, 12), size=int(rng.integers(1, 3)), replace=False)):
            if rng.random() < 0.35:
                continue
            ring2 = int(np.clip(ring + rng.integers(-2, 3), 1, 12))
            p, q = ray_pts[k][ring], ray_pts[(k + 1) % rays][ring2]
            m = ((p[0] + q[0]) / 2 + rng.normal(0, S * 0.012), (p[1] + q[1]) / 2 + rng.normal(0, S * 0.012))
            polys.append([p, m, q])
            widths.append(S * 0.0045)
    line = _lines_to_field(polys, S, widths)
    # facets: random flat brightness per cell between cracks (refraction look)
    x, y = coords(S)
    r, a = polar_of(x, y)
    sector = np.floor(((a + math.pi) / TAU) * rays * 1.0 + noise(S, S, 120, 120, seed + 1, 2) * 1.5)
    band = np.floor(r * 7 + noise(S, S, 100, 100, seed + 2, 2) * 1.2)
    facet = (np.sin(sector * 12.9898 + band * 78.233) * 43758.5453) % 1.0
    pane = (0.03 + 0.09 * facet ** 2) * ss(r, 0.9, 0.4)
    I = np.clip(_glow_lines(line, S) + pane, 0, 1)
    return I * ss(r, 1.0, 0.85)


def lightning(n=16, seed=131):
    """Anime lightning strike: three forked bolts draw in from the centre over 2 frames, hold the SAME
    paths while flickering (tiny vertex jitter, brightness pulses, branches popping on and off), then
    break apart from the tips and fade. Layered."""
    rng = np.random.default_rng(seed)
    bolts = []
    for k in range(3):
        ang = k / 3 * TAU + rng.uniform(-0.5, 0.5)
        pts, a2 = _walk(rng, (S / 2 + rng.normal(0, S * 0.02), S / 2 + rng.normal(0, S * 0.02)), ang, S * 0.045, 9, 0.5)
        brs = []
        for j in (2, 4, 6):
            bp, _ = _walk(rng, pts[j], a2 + rng.uniform(-1.3, 1.3), S * 0.03, int(rng.integers(3, 6)), 0.9)
            brs.append((j, bp))
        bolts.append((pts, brs))
    flick = [1.0, 1.0, 0.75, 1.0, 0.6, 0.95, 0.8, 1.0, 0.7, 0.9, 0.8, 0.65, 0.5, 0.38, 0.25, 0.12]
    frames = []
    for i in range(n):
        fr = np.random.default_rng(seed * 100 + i)
        reveal = min(1.0, (i + 1) / 2.0)
        breakup = max(0.0, (i - 9) / 6)
        polys, widths = [], []
        for pts, brs in bolts:
            npts = len(pts)
            keep = max(2, int(round(npts * reveal * (1 - 0.75 * breakup))))
            jit = [(px + fr.normal(0, S * 0.004), py + fr.normal(0, S * 0.004)) if 0 < q < npts - 1 else (px, py) for q, (px, py) in enumerate(pts)]
            polys.append(jit[:keep])
            widths.append(S * 0.012 * (1 - 0.5 * breakup))
            for j, bp in brs:
                if j < keep - 1 and fr.random() < (0.85 if i < 3 else 0.55):
                    bkeep = max(2, int(round(len(bp) * (1 - breakup))))
                    polys.append([jit[j]] + [(px + fr.normal(0, S * 0.004), py + fr.normal(0, S * 0.004)) for px, py in bp[1:bkeep]])
                    widths.append(S * 0.007 * (1 - 0.5 * breakup))
        line = _lines_to_field(polys, S, widths)
        frames.append(_glow_lines(line, S) * flick[i])
    return frames


# ================================================================ BEAM / SPEED LINES
def beam_strip():
    """Tileable beam/trail strip (u along the beam, v across): hot core line, streaky energy body.
    1024x256 output. Layered. Use with Beam.TextureMode = Wrap and TextureSpeed for flow."""
    H, W = 256 * SS, 1024 * SS
    v = np.linspace(-1, 1, H)[:, None]
    st = tnoise(H, W, 14, 380, 141, 4)
    st2 = tnoise(H, W, 40, 900, 142, 3)
    wob = (tnoise(1, W, 1, 300, 143, 2)[0] - 0.5) * 0.25
    vv = np.abs(v + wob[None, :] * 0.4)
    core = ss(vv, 0.12, 0.03)
    body = ss(vv, 0.75 + (st2 - 0.5) * 0.5, 0.2) * (0.45 + 0.75 * st)
    I = np.clip(np.maximum(core, body), 0, 1)
    return mblur(I, 8, axis=1)


def speedlines():
    """Full-screen anime speed lines converging on an empty centre. Single white, alpha only. 1024 px."""
    rng = np.random.default_rng(151)
    N = 1024 * SS
    x, y = coords(N)
    r, a = polar_of(x, y)
    F = np.zeros((N, N), np.float32)
    for _ in range(170):
        ang = rng.uniform(0, TAU)
        r0 = rng.uniform(0.45, 0.85)
        w = rng.uniform(0.002, 0.009)
        da = np.abs(np.angle(np.exp(1j * (a - ang))))
        wd = w * ss(r, r0, r0 + 0.5) * r
        F = np.maximum(F, ss(da * r, wd + 0.0015, wd * 0.2) * ss(r, r0, r0 + 0.25) * rng.uniform(0.5, 1.0))
    return F



# ================================================================ MESH STRIPS (UV u along the stroke, v across)
def slash_strip():
    """For crescent shells: u = head (0) -> tail (1), v = outer edge (0) -> inner edge (1). White-hot leading
    rim, painted body falling off inward with streaks, ragged inner feather, tail breaking up. 1024x256. Shaded."""
    H, W = 256 * SS, 1024 * SS
    u = np.linspace(0, 1, W)[None, :]
    v = np.linspace(0, 1, H)[:, None]
    st = noise(H, W, 18, 300, 161, 4)
    fe = noise(H, W, 40, 120, 162, 3)
    br = noise(H, W, 30, 80, 163, 4)
    rim = ss(v, 0.1, 0.02)
    body = ss(v, 0.85 + (fe - 0.5) * 0.4, 0.35) * (0.6 + 0.4 * st)
    along = ss(u + (br - 0.5) * 0.3, 1.0, 0.55)
    A = np.clip(np.maximum(rim, body) * along, 0, 1)
    V = np.clip(0.62 + 0.38 * np.maximum(rim, ss(v, 0.35, 0.05) * 0.6), 0, 1)
    return pc.down_rect(A, W // SS, H // SS), pc.down_rect(V, W // SS, H // SS)


def energy_strip():
    """Tileable (in u) streaky energy for rings, spheres, tubes and swirls: soft at both v edges, flowing
    filaments along u. Scroll it (shell 'scroll') for motion. 1024x256. Shaded."""
    H, W = 256 * SS, 1024 * SS
    v = np.linspace(-1, 1, H)[:, None]
    st = tnoise(H, W, 16, 420, 171, 4)
    st2 = tnoise(H, W, 50, 900, 172, 3)
    edge = ss(np.abs(v), 1.0, 0.55 + (st2 - 0.5) * 0.4)
    fil = levels(st, 0.35, 0.85)
    A = np.clip(edge * (0.35 + 0.75 * fil), 0, 1)
    V = np.clip(0.62 + 0.38 * fil * ss(np.abs(v), 0.7, 0.1), 0, 1)
    return mblur(A, 6, axis=1)[::SS, ::SS], mblur(V, 6, axis=1)[::SS, ::SS]


def edge_strip():
    """Tileable shockwave band: crisp hot edge at v=0, streaky fade to nothing at v=1. 1024x256. Shaded."""
    H, W = 256 * SS, 1024 * SS
    v = np.linspace(0, 1, H)[:, None]
    st = tnoise(H, W, 26, 360, 181, 4)
    rim = ss(v, 0.12, 0.03)
    body = levels(1 - v + (st - 0.5) * 0.7, 0.15, 0.95) * ss(v, 0.0, 0.05)
    A = np.clip(np.maximum(rim, body * 0.85), 0, 1)
    V = np.clip(0.62 + 0.38 * np.maximum(rim, ss(v, 0.4, 0.0) * 0.5), 0, 1) * np.ones((1, W))
    return mblur(A, 6, axis=1)[::SS, ::SS], mblur(V, 6, axis=1)[::SS, ::SS]


def wind_strip():
    """Tileable wispy wind filaments for tornado swirls and dash sleeves. 1024x256. White."""
    H, W = 256 * SS, 1024 * SS
    v = np.linspace(-1, 1, H)[:, None]
    wob = tnoise(H, W, 60, 500, 191, 3)
    lines = np.abs(np.sin((v + (wob - 0.5) * 0.5) * 9.0))
    gaps = tnoise(H, W, 30, 260, 192, 3)
    A = ss(lines, 0.86, 0.98) * levels(gaps, 0.35, 0.7) * ss(np.abs(v), 1.0, 0.6)
    return mblur(np.clip(A, 0, 1), 8, axis=1)[::SS, ::SS]



# ================================================================ SOURCE ART (AI-generated paintings -> layered white textures)
ART = os.path.join(HERE, "..", "assets", "source_art")


def art(name, lo=0.04, hi=0.9, gamma=0.9):
    """Load a painted silhouette from assets/source_art (Figma / Meshy image generation, greyscale, black or
    transparent background) and turn brightness into a layered intensity image."""
    im = np.asarray(Image.open(os.path.join(ART, name + ".png")).convert("RGBA"), np.float32) / 255
    lum = im[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)
    I = levels(lum * im[..., 3], lo, hi, gamma)
    img = Image.fromarray(np.ascontiguousarray(I, dtype=np.float32)).resize((S * 2 // 2 * 2, S * 2 // 2 * 2), Image.LANCZOS)
    return np.clip(np.asarray(img, np.float32), 0, 1)


def dragon_head():
    """Roaring energy dragon head, side profile facing right (Figma image generation, repainted into layers). Layered."""
    return art("dragon_head", 0.05, 0.85)


def phoenix_wing():
    """Spread phoenix wing of flame feathers, root at the left (Figma image generation). Layered."""
    return art("phoenix_wing")


def giant_fist():
    """Giant energy fist punching right with a flame trail (Figma image generation). Layered."""
    return art("giant_fist")


def water_shark():
    """Charging shark of splashing water, facing right (Figma image generation). Layered."""
    return art("water_shark")


def palm_strike():
    """Giant open palm strike with a radiating ring (Figma image generation). Layered."""
    return art("palm_strike")



# ================================================================ ELEMENT TEXTURES (each element gets its own painted matter)
def _ballistic(o, ang, speed, g, s):
    return (o[0] + math.cos(ang) * speed * s, o[1] + math.sin(ang) * speed * s - 0.5 * g * s * s)


def _jets(x, y, o, tend, reach, t, g, tear_after, thin_k, steps=16):
    cs = []
    for ang, sp, r0 in tend:
        for k in range(steps + 1):
            sk = k / steps * reach
            px, py = _ballistic(o, ang, sp, g, sk)
            rad = r0 * (1 - 0.7 * sk) ** 0.8 * (1 - thin_k * t)
            if t > tear_after and k > steps * 0.62:
                if k % 3:
                    continue
                rad *= 1.3
            cs.append((px, py, rad))
    return cs


def magma_splash(n=16, seed=201):
    """Molten crown: thick globby jets flung up out of a bulging pool, tips tearing into globs, a cracked
    crust creeping over the mass as it cools and sags. Layered (hot inside, cooling crust outside)."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    o = (0.0, -0.8)
    tend = [(math.radians(rng.uniform(62, 118)), rng.uniform(1.7, 2.2), rng.uniform(0.11, 0.17)) for _ in range(7)]
    crust = noise(S, S, 22, 22, seed + 1, 4)
    edge = noise(S, S, 46, 46, seed + 2, 3)
    frames = []
    for i in range(n):
        t = i / (n - 1)
        reach = ease_out(t / 0.42, 2)
        pool = [(o[0], o[1] + 0.05, 0.42 * (1 - 0.3 * t)), (o[0] - 0.3, o[1], 0.26), (o[0] + 0.3, o[1], 0.26)]
        cs = pool + _jets(x, y, o, tend, reach, t, 2.6, 0.35, 0.4)
        xw, yw = x + (edge - 0.5) * 0.06, y + (edge - 0.5) * 0.06
        F = lobes(xw, yw, cs, 1.25)
        H = F - 0.25
        edgeA = ss(H, 0.0, 0.04)
        dist = ndi.distance_transform_edt(H > 0)
        depth = 1 - np.exp(-dist / (S * 0.04))
        vol = shade(blur(F, 4), light=(-0.4, 0.8, 0.5), strength=60)
        cracks = ss(np.abs(crust - 0.5), 0.03, 0.0) * ss(t, 0.2, 0.65)
        I = edgeA * (0.22 + 0.78 * depth) * (0.65 + 0.45 * vol) * (1.05 - 0.5 * t) * (1 - 0.65 * cracks)
        frames.append(np.clip(I, 0, 1))
    return frames


def lava_drops(n=16, seed=211):
    """16 molten globs (FlipbookStartRandom): smooth blobs glowing from the centre, laced with dark cooling
    veins. Shaded."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    alphas, vals = [], []
    for i in range(n):
        el = rng.uniform(1.0, 1.7)
        rot = rng.uniform(0, TAU)
        xr, yr = x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot)
        nz = noise(S, S, 90, 90, seed * 7 + i, 2)
        d = np.hypot(xr / (0.42 * el), yr / 0.42) + (nz - 0.5) * 0.22
        m = ss(d, 1.0, 0.95)
        depth = levels(1 - d, 0.0, 0.75)
        vein = ss(np.abs(noise(S, S, 34, 34, seed * 11 + i, 3) - 0.5), 0.045, 0.0) * ss(depth, 0.7, 0.1)
        alphas.append(np.clip(np.maximum(m, blur(m, S * 0.03) * 0.3), 0, 1))
        vals.append(np.clip(np.where(m > 0.5, (0.55 + 0.45 * depth) * (1 - 0.5 * vein), 0.55), 0, 1))
    return alphas, vals


def light_burst(n=16, seed=221):
    """Radiant light explosion: hot core, a dense fan of sharp rays of mixed length, a thin expanding
    ring and a few glints riding the rays. Layered."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    r, a = polar_of(x, y)
    rays = [(rng.uniform(0, TAU), rng.uniform(0.35, 1.0), rng.uniform(0.006, 0.03)) for _ in range(44)]
    glints = [(rng.uniform(0, TAU), rng.uniform(0.3, 0.7), rng.uniform(0.04, 0.08)) for _ in range(9)]
    frames = []
    for i in range(n):
        t = i / (n - 1)
        g = ease_out((i + 1) / 3, 2)
        thin = (1 - t) ** 1.4
        F = np.zeros_like(x)
        for ang, L, w in rays:
            da = np.abs(np.angle(np.exp(1j * (a - ang))))
            Lk = L * g
            wd = w * thin * (1 - np.clip(r / Lk, 0, 1)) ** 0.9 + 0.001
            F = np.maximum(F, ss(da * (r + 0.05), wd, wd * 0.2) * (r < Lk) * (0.6 + 0.4 * (L > 0.7)))
        core = ss(r, 0.1 + 0.12 * g * thin, 0.02) * (0.4 + 0.6 * thin)
        rr = 0.15 + 0.8 * ease_out(t / 0.6, 2)
        ring = ss(np.abs(r - rr), 0.02 + 0.02 * t, 0.003) * (1 - t) * 0.8
        gl = np.zeros_like(x)
        if 0.15 < t < 0.8:
            for ang, rad, sz in glints:
                gx, gy = math.cos(ang) * rad, math.sin(ang) * rad
                gr, ga = polar_of(x - gx, y - gy)
                arm = np.minimum(np.abs(np.sin(ga)), np.abs(np.cos(ga)))
                gl = np.maximum(gl, ss(arm * gr, 0.012 * (1 - np.clip(gr / sz, 0, 1)) + 0.002, 0.0) * (gr < sz))
        frames.append(np.clip(np.maximum.reduce([F, core, ring, gl * (1 - abs(t - 0.45) * 2)]), 0, 1))
    return frames


def shock_ripple(n=16, seed=231):
    """Quake air ripples: three thin, broken concentric rings launched one after another, each with a crisp
    leading edge and a streaky trailing fade. Layered."""
    x, y = coords(S)
    r, a = polar_of(x, y)
    H, W = 64, 1024
    gaps = [tnoise(H, W, 40, 120, seed + k, 3)[H // 2] for k in range(3)]
    st = tnoise(H, W, 6, 60, seed + 9, 3)[H // 2]
    ai = ((a + math.pi) / TAU * (W - 1)).astype(int)
    frames = []
    for i in range(n):
        t = i / (n - 1)
        F = np.zeros_like(x)
        for k in range(3):
            tk = (t - k * 0.12) / 0.7
            if tk <= 0 or tk >= 1:
                continue
            rk = 0.1 + 0.85 * ease_out(tk, 2)
            seg = levels(gaps[k][ai], 0.32, 0.6)
            lead = ss(r, rk + 0.012, rk - 0.004) * ss(r, rk - 0.09, rk - 0.004)
            trail = levels(1 - (rk - r) / 0.09, 0, 1) * (r < rk) * (r > rk - 0.09)
            F = np.maximum(F, (lead * 0.95 + trail * 0.45 * (0.5 + 0.5 * st[ai])) * seg * (1 - tk) ** 0.8)
        frames.append(np.clip(F, 0, 1))
    return frames


def _shard_poly(c, ang, L, w, base=0.05):
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca
    b0 = (c[0] + ca * base, c[1] + sa * base)
    mid = (c[0] + ca * (base + L * 0.35), c[1] + sa * (base + L * 0.35))
    tip = (c[0] + ca * (base + L), c[1] + sa * (base + L))
    left = (mid[0] + px * w, mid[1] + py * w)
    right = (mid[0] - px * w, mid[1] - py * w)
    return [b0, left, tip], [b0, tip, right]


def _to_px(pts, size):
    return [((p[0] + 1) / 2 * size, (1 - (p[1] + 1) / 2) * size) for p in pts]


def ice_burst(n=16, seed=241):
    """Faceted ice shards bursting from a frost core: shards shoot out (lit / shadow halves = painted
    facets, bright edges), then crack into fragments that drift and fade. Layered."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    r, _ = polar_of(x, y)
    shards = [(rng.uniform(0, TAU), rng.uniform(0.45, 0.85), rng.uniform(0.05, 0.1)) for _ in range(13)]
    frames = []
    for i in range(n):
        t = i / (n - 1)
        g = ease_out((i + 1) / 3, 2)
        crack = max(0.0, (t - 0.35) / 0.65)
        lit = np.zeros_like(x)
        dark = np.zeros_like(x)
        for ang, L, w in shards:
            Lk, wk = L * g * (1 - 0.2 * crack), w * (1 - 0.3 * crack)
            pieces = 1 if crack <= 0 else 3
            for p in range(pieces):
                off = crack * 0.22 * (p + 1) / pieces
                seg_l = Lk / pieces
                c = (math.cos(ang) * (off + p * seg_l), math.sin(ang) * (off + p * seg_l))
                A, B = _shard_poly(c, ang + rng.uniform(-0.05, 0.05) * crack, seg_l * (0.92 if pieces > 1 else 1), wk, base=0.04 if p == 0 else 0.0)
                lit = np.maximum(lit, _poly_mask(_to_px(A, S), S))
                dark = np.maximum(dark, _poly_mask(_to_px(B, S), S))
        m = np.maximum(lit, dark)
        edge = np.clip(m - ndi.grey_erosion(m, size=(5, 5)), 0, 1)
        core = ss(r, 0.18 * (1 - 0.6 * t) + 0.02, 0.0) * (1 - t)
        mist = blur(ss(r, 0.35, 0.05), S * 0.02) * (1 - t) * 0.45
        I = np.maximum.reduce([lit * 0.82, dark * 0.55, edge * 0.95, core, mist]) * (1 - 0.65 * crack ** 1.5)
        frames.append(np.clip(blur(I, 1.0), 0, 1))
    return frames


def frost_mist(n=16, seed=251):
    """Curling cold mist: soft wisps swirled by a domain warp that winds tighter toward the centre, expanding
    and thinning out. Shaded (soft alpha, cool highlights)."""
    x, y = coords(S)
    r, a = polar_of(x, y)
    base = noise(S, S, 70, 70, seed, 4)
    fine = noise(S, S, 24, 24, seed + 1, 3)
    alphas, vals = [], []
    for i in range(n):
        t = i / (n - 1)
        g = 0.45 + 0.55 * ease_out(t / 0.6)
        tw = (1.6 - r) * (0.8 + 1.2 * t)
        xs = x * np.cos(tw) - y * np.sin(tw)
        ys = x * np.sin(tw) + y * np.cos(tw)
        f = pc.sample(base, np.clip(xs / g, -1, 1), np.clip(ys / g, -1, 1))
        wisps = levels(f + (fine - 0.5) * 0.3, 0.42 + 0.25 * t, 0.75)
        A = wisps * ss(r, 0.95 * g, 0.4 * g) * (1 - 0.6 * t)
        alphas.append(np.clip(A * 0.85, 0, 1))
        vals.append(np.clip(0.78 + 0.22 * levels(f, 0.5, 0.9), 0, 1))
    return alphas, vals


def ice_chips(n=16, seed=261):
    """16 crystal chips (FlipbookStartRandom): faceted shards with a lit and a shadow face and a bright edge. Shaded."""
    rng = np.random.default_rng(seed)
    alphas, vals = [], []
    for i in range(n):
        ang = rng.uniform(0, TAU)
        A, B = _shard_poly((-math.cos(ang) * 0.4, -math.sin(ang) * 0.4), ang, rng.uniform(0.7, 0.95), rng.uniform(0.12, 0.25), base=0.0)
        la, lb = _poly_mask(_to_px(A, S), S), _poly_mask(_to_px(B, S), S)
        m = blur(np.maximum(la, lb), 1.2)
        edge = np.clip(m - ndi.grey_erosion(m, size=(7, 7)), 0, 1)
        alphas.append(np.clip(np.maximum(m, blur(m, S * 0.03) * 0.35), 0, 1))
        vals.append(np.clip(np.where(m > 0.4, np.maximum(la * 1.0 + lb * 0.68, edge), 0.7), 0, 1))
    return alphas, vals


def void_smoke(n=16, seed=271):
    """Inky void tendrils: spiral arms of ragged smoke unwinding outward from a dense centre, then shredding
    into wisps. Layered (paint the core dark and the fringe glowing with the kit colours)."""
    x, y = coords(S)
    r, a = polar_of(x, y)
    nz = noise(S, S, 40, 40, seed, 4)
    nz2 = noise(S, S, 90, 90, seed + 1, 3)
    frames = []
    for i in range(n):
        t = i / (n - 1)
        g = 0.3 + 0.7 * ease_out(t / 0.55)
        arms = np.cos(5 * (a + 2.4 * r - 1.6 * t) + (nz2 - 0.5) * 3)
        body = levels(arms, 0.1 - 0.4 * (1 - r / g), 0.8) * ss(r, g, g * 0.55)
        center = ss(r, 0.35 * g, 0.0)
        F = np.maximum(body, center) + (nz - 0.5) * 0.35
        diss = max(0.0, (t - 0.4) / 0.6)
        F = F - diss * 0.7
        I = levels(F, 0.18, 0.95, 0.9)
        frames.append(np.clip(I, 0, 1))
    return frames


def void_orb(n=16, seed=281):
    """Black-hole accretion (loop): spiral arms draining into a bright event-horizon ring, hollow centre
    (pair with a black Neon sphere). Angle-periodic, seamless loop. Layered."""
    H, W = 256, 1024
    sw = tnoise(H, W, 30, 220, seed, 4)
    v = np.linspace(0, 1, H)[:, None]          # 0 = outer (r=0.98), 1 = centre
    rr = 0.98 * (1 - v)
    frames = []
    for i in range(n):
        o = int(W * i / n)
        u = np.linspace(0, 1, W)[None, :]
        spiral = np.cos((u * 3 + rr * 4.0) * TAU - i / n * TAU * 3)
        arms = levels(spiral + (np.roll(sw, -o, axis=1) - 0.5) * 1.2, 0.2, 1.0) * ss(rr, 0.9, 0.5) * ss(rr, 0.25, 0.34)
        horizon = ss(np.abs(rr - 0.3), 0.05, 0.008)
        I = np.clip(np.maximum(arms * 0.75, horizon) * (rr > 0.22), 0, 1)
        frames.append(pc.polar_strip(I, S, 0.98, 0.0, 0.0, TAU))
    return frames


def electric_burst(n=16, seed=291):
    """Electric discharge: short jagged arcs fire out of a flash in all directions, re-strike along similar
    paths every two frames, then flicker out. Layered."""
    rng = np.random.default_rng(seed)
    dirs = [rng.uniform(0, TAU) for _ in range(11)]
    frames = []
    for i in range(n):
        t = i / (n - 1)
        fr = np.random.default_rng(seed * 50 + i // 2)
        g = ease_out((i + 1) / 2.5, 2)
        polys, widths = [], []
        for d in dirs:
            pts, a2 = _walk(fr, (S / 2, S / 2), d + fr.uniform(-0.25, 0.25), S * 0.045 * g, 8, 0.9)
            polys.append(pts)
            widths.append(S * 0.009)
            if fr.random() < 0.6:
                j = int(fr.integers(2, 6))
                bp, _ = _walk(fr, pts[j], a2 + fr.uniform(-1.2, 1.2), S * 0.025, 4, 1.0)
                polys.append(bp)
                widths.append(S * 0.005)
        line = _lines_to_field(polys, S, widths)
        x, y = coords(S)
        core = ss(np.hypot(x, y), 0.16 * (1 - t), 0.0)
        flick = [1, 1, 0.8, 1, 0.7, 0.95, 0.6, 0.9, 0.55, 0.8, 0.45, 0.6, 0.3, 0.35, 0.15, 0.08][i]
        frames.append(np.clip(np.maximum(_glow_lines(line, S), core) * flick, 0, 1))
    return frames


def haki_burst(n=16, seed=301):
    """Conqueror-style ink burst: thick ragged spikes splash out in two frames, then thin, retract and
    break into droplets, with thin crackles around. Layered (kit paints core black, middle red)."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    r, a = polar_of(x, y)
    spikes = [(rng.uniform(0, TAU), rng.uniform(0.5, 0.95), rng.uniform(0.07, 0.15)) for _ in range(15)]
    rag = noise(S, S, 18, 18, seed + 1, 4)
    frames = []
    for i in range(n):
        t = i / (n - 1)
        g = ease_out((i + 1) / 2.2, 2)
        thin = (1 - t) ** 1.2
        F = np.zeros_like(x)
        for ang, L, w in spikes:
            da = np.abs(np.angle(np.exp(1j * (a - ang))))
            Lk = L * g * (1 - 0.3 * t)
            wd = w * thin * (1 - np.clip(r / Lk, 0, 1)) ** 1.4 + 0.004
            F = np.maximum(F, levels((wd - da * (r + 0.08)) / wd + (rag - 0.5) * 0.9, 0.0, 0.6) * (r < Lk))
        hub = ss(r, 0.22 * thin + 0.05, 0.08 * thin) + (rag - 0.5) * 0.3
        F = np.maximum(F, levels(hub, 0.2, 0.8))
        if t > 0.3:
            drops = ss(noise(S, S, 10, 10, seed + i, 2), 0.82, 0.86) * ss(r, 0.95, 0.5) * (1 - t)
            F = np.maximum(F, drops)
        frames.append(np.clip(F * (1 - 0.3 * t), 0, 1))
    return frames


def blade_cuts(n=16, seed=311):
    """Crossing sword cuts: 4 razor lines slash across the centre one after another (each drawn end to end
    in a frame), then split into two parallel halves that drift apart and fade. Layered."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    cuts = [(rng.uniform(0, math.pi), rng.uniform(-0.15, 0.15), k * 0.06) for k in range(4)]
    frames = []
    for i in range(n):
        t = i / (n - 1)
        F = np.zeros_like(x)
        for ang, off, t0 in cuts:
            tk = (t - t0) / (1 - t0)
            if tk <= 0:
                continue
            ca, sa = math.cos(ang), math.sin(ang)
            u = x * ca + y * sa
            v = -x * sa + y * ca - off
            draw = ease_out(tk / 0.12, 2)
            split = max(0.0, (tk - 0.2) / 0.8) * 0.07
            prof = 1 - np.clip(np.abs(u) / 0.95, 0, 1) ** 1.5
            w = 0.022 * prof * (1 - 0.6 * max(0.0, tk - 0.2))
            reveal = u < (-0.95 + 1.9 * draw)
            for sgn in ((0,) if split == 0 else (-1, 1)):
                F = np.maximum(F, ss(np.abs(v - sgn * split), w + 0.003, w * 0.2) * reveal * (1 - max(0.0, tk - 0.35) / 0.65))
        frames.append(np.clip(F, 0, 1))
    return frames


def water_splash(n=16, seed=321):
    """Water splash: a fan of slim jets bursts up out of a churned base, tips breaking into strings of
    droplets that arc and fall; bright streaks run along the water. Layered."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    o = (0.0, -0.82)
    tend = [(math.radians(rng.uniform(55, 125)), rng.uniform(1.8, 2.5), rng.uniform(0.045, 0.08)) for _ in range(13)]
    streak = noise(S, S, 60, 8, seed + 1, 3)
    edge = noise(S, S, 30, 30, seed + 2, 3)
    frames = []
    for i in range(n):
        t = i / (n - 1)
        reach = ease_out(t / 0.4, 2) * (1 + 0.35 * max(0.0, t - 0.4))
        base = [(o[0] + dx, o[1] + 0.04, 0.2 * (1 - 0.5 * t)) for dx in (-0.3, -0.12, 0.0, 0.14, 0.3)]
        cs = base + _jets(x, y, o, tend, reach, t, 3.4, 0.25, 0.5, steps=18)
        F = lobes(x + (edge - 0.5) * 0.04, y + (edge - 0.5) * 0.04, cs, 1.4)
        H = F - 0.3
        edgeA = ss(H, 0.0, 0.05)
        dist = ndi.distance_transform_edt(H > 0)
        depth = 1 - np.exp(-dist / (S * 0.02))
        I = edgeA * (0.35 + 0.45 * depth) * (0.7 + 0.5 * streak) * (1 - 0.55 * max(0.0, t - 0.45))
        frames.append(np.clip(I, 0, 1))
    return frames


def spray_puff(n=16, seed=331):
    """Water spray: a soft round mist burst threaded with fine droplets, expanding and fading out from
    the middle. Shaded (bright mist, subtle cool shading)."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    r, a = polar_of(x, y)
    base = noise(S, S, 50, 50, seed, 4)
    drops = [(rng.uniform(0, TAU), rng.uniform(0.1, 0.9), rng.uniform(0.008, 0.02)) for _ in range(60)]
    alphas, vals = [], []
    for i in range(n):
        t = i / (n - 1)
        g = 0.4 + 0.6 * ease_out(t / 0.5)
        mist = levels(base + 0.55 - r / g, 0.35 + 0.35 * t, 0.85) * ss(r, g, g * 0.5)
        D = np.zeros_like(x)
        for ang, rad, sz in drops:
            rr = rad * g * 1.05
            D = np.maximum(D, ss(np.hypot(x - math.cos(ang) * rr, y - math.sin(ang) * rr), sz * (1 - 0.5 * t), sz * 0.3))
        A = np.maximum(mist * (0.85 - 0.5 * t), D * (1 - t * 0.7))
        alphas.append(np.clip(A, 0, 1))
        vals.append(np.clip(0.8 + 0.2 * levels(base, 0.5, 0.9) * (1 - D) + 0.2 * D, 0, 1))
    return alphas, vals


def water_drops(n=16, seed=341):
    """16 water droplets (FlipbookStartRandom): round and teardrop shapes, darker refraction rim and a sharp
    highlight. Shaded."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    alphas, vals = [], []
    for i in range(n):
        el = rng.uniform(1.0, 2.2)
        rot = rng.uniform(0, TAU)
        xr, yr = x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot)
        tear = 1 + 0.6 * ss(yr, 0.0, 0.6) * (el > 1.4)
        d = np.hypot(xr * tear / 0.36, yr / (0.36 * el))
        m = ss(d, 1.0, 0.92)
        rim = ss(d, 0.7, 0.95) * m
        hl = ss(np.hypot(xr + 0.12, yr - 0.14 * el), 0.09, 0.03)
        alphas.append(np.clip(m * (0.75 + 0.25 * rim), 0, 1))
        vals.append(np.clip(np.where(m > 0.3, 0.8 - 0.25 * rim + hl * 0.4, 0.8), 0, 1))
    return alphas, vals



# ================================================================ THUNDER FRUIT (fractal lightning, painted in layers)
def _frac_path(rng, a, b, rough=0.2, depth=5, decay=0.5):
    """Midpoint-displacement lightning path from a to b (pixel coords)."""
    pts = [np.array(a, float), np.array(b, float)]
    disp = rough * np.linalg.norm(pts[1] - pts[0])
    for _ in range(depth):
        new = [pts[0]]
        for p, q in zip(pts[:-1], pts[1:]):
            d = q - p
            n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
            new += [(p + q) / 2 + n * rng.normal(0, disp), q]
        pts = new
        disp *= decay
    return pts


def _bolt_tree(rng, a, b, w0, depth=2, branches=5, rough=0.2, inten=1.0, spread=(0.35, 0.9)):
    """Main fractal path plus recursive tapering, dimming branches. Returns [(pts, w_start, w_end, intensity, rank)]."""
    main = _frac_path(rng, a, b, rough)
    out = [(main, w0, w0 * 0.35, inten, 0)]
    if depth <= 0:
        return out
    L = np.linalg.norm(np.array(b, float) - np.array(a, float))
    for _ in range(branches):
        i = int(rng.uniform(0.12, 0.8) * (len(main) - 2)) + 1
        p, q = main[i], main[min(len(main) - 1, i + 4)]
        d = (q - p) / (np.linalg.norm(q - p) + 1e-9)
        ang = rng.choice([-1, 1]) * rng.uniform(*spread)
        c, s = math.cos(ang), math.sin(ang)
        d2 = np.array([d[0] * c - d[1] * s, d[0] * s + d[1] * c])
        ln = L * rng.uniform(0.15, 0.42) * (1 - i / len(main)) ** 0.5
        wb = w0 * (1 - i / len(main)) * 0.5 + 1
        for item in _bolt_tree(rng, p, p + d2 * ln, wb, depth - 1, max(1, branches // 2), rough * 1.1, inten * 0.7, spread):
            out.append((item[0], item[1], item[2], item[3], item[4] + 1))
    return out


def _render_bolts(bolts, size, keep=1.0, jitter=0.0, rng=None, width_k=1.0, tip_cut=0.0):
    """Draw tapered bolts (max-blended), each truncated to `keep` of its length (branches lose tips first
    by tip_cut). Returns the hot core line field 0..1."""
    F = np.zeros((size, size), np.float32)
    for pts, w0, w1, inten, rank in bolts:
        k = keep * (1 - tip_cut * min(rank, 2) / 2)
        n = max(2, int(len(pts) * k))
        P = pts[:n]
        if jitter and rng is not None:
            P = [p + rng.normal(0, jitter, 2) if 0 < j < len(P) - 1 else p for j, p in enumerate(P)]
        img = Image.new("L", (size, size), 0)
        d = ImageDraw.Draw(img)
        for j in range(len(P) - 1):
            t = j / max(1, len(pts) - 1)
            w = max(1.0, (w0 + (w1 - w0) * t) * width_k)
            d.line([tuple(P[j]), tuple(P[j + 1])], fill=int(255 * min(1, inten)), width=int(round(w)))
            r = w / 2
            d.ellipse([P[j + 1][0] - r, P[j + 1][1] - r, P[j + 1][0] + r, P[j + 1][1] + r], fill=int(255 * min(1, inten)))
        F = np.maximum(F, np.asarray(img, np.float32) / 255)
    return F


def _electric_glow(core, size, k_inner=1.0, k_outer=1.0, k_haze=0.35, cool=0.0):
    """Painted electricity: white-hot core, tight inner glow, wide bloom, faint ion haze. `cool` (0..1) shifts
    energy from the core into the glow as the bolt cools in the afterglow."""
    inner = blur(core, size * (0.004 + 0.004 * cool))
    outer = blur(core, size * (0.016 + 0.01 * cool))
    haze = blur(core, size * 0.05)
    return np.clip(core * (1 - 0.55 * cool) + inner * (0.55 + 0.25 * cool) * k_inner + outer * (0.42 + 0.2 * cool) * k_outer + haze * k_haze * 0.5, 0, 1)


STRIKE = [  # (keep, brightness, width, jitter, cool, tip_cut) per frame: leader, return stroke, re-strikes, afterglow
    (0.55, 0.55, 0.45, 0, 0.0, 0.0), (1, 1.0, 1.25, 0, 0.0, 0.0), (1, 0.95, 1.1, 1, 0.0, 0.0), (1, 0.5, 0.8, 1, 0.1, 0.0),
    (1, 0.9, 1.05, 2, 0.05, 0.0), (1, 0.55, 0.85, 2, 0.15, 0.1), (1, 0.8, 0.95, 3, 0.15, 0.15), (1, 0.6, 0.8, 3, 0.3, 0.25),
    (1, 0.5, 0.7, 3, 0.4, 0.35), (1, 0.42, 0.62, 3, 0.5, 0.45), (1, 0.34, 0.55, 3, 0.6, 0.55), (1, 0.27, 0.5, 3, 0.7, 0.65),
    (1, 0.2, 0.45, 3, 0.78, 0.75), (1, 0.14, 0.4, 3, 0.85, 0.85), (1, 0.08, 0.35, 3, 0.9, 0.95), (1, 0.03, 0.3, 3, 0.95, 1.0)]


def thunder_bolt(n=16, seed=406):
    """Sky-to-ground lightning strike (top to bottom of the cell): a stepped leader, the full white-hot return
    stroke with branches, two re-strike flickers, then a cooling afterglow where branch tips die first. Layered."""
    rng = np.random.default_rng(seed)
    bolts = _bolt_tree(rng, (S * 0.5 + rng.normal(0, S * 0.04), S * 0.02), (S * 0.5 + rng.normal(0, S * 0.05), S * 0.98), S * 0.011, depth=2, branches=4, rough=0.3, spread=(0.2, 0.55))
    frames = []
    for i in range(n):
        keep, br, wk, jit, cool, cut = STRIKE[i]
        fr = np.random.default_rng(seed * 10 + jit)
        core = _render_bolts(bolts, S, keep, S * 0.003 * jit, fr, wk, cut)
        frames.append(_electric_glow(core, S, cool=cool) * br)
    return frames


def thunder_burst(n=16, seed=411):
    """Electric impact: a flash core and 7 fractal bolts striking outward in 2 frames, flickering, then cooling
    from the tips inward; a thin shock ring rides out. Layered."""
    rng = np.random.default_rng(seed)
    c = (S / 2, S / 2)
    bolts = []
    for k in range(7):
        a = k / 7 * TAU + rng.uniform(-0.3, 0.3)
        L = S * rng.uniform(0.33, 0.47)
        bolts += _bolt_tree(rng, c, (c[0] + math.cos(a) * L, c[1] + math.sin(a) * L), S * 0.009, depth=1, branches=3, rough=0.32)
    x, y = coords(S)
    r, _ = polar_of(x, y)
    frames = []
    for i in range(n):
        keep, br, wk, jit, cool, cut = STRIKE[i]
        keep = min(1.0, (i + 1) / 2.0)
        fr = np.random.default_rng(seed * 10 + jit)
        core = _render_bolts(bolts, S, keep, S * 0.003 * jit, fr, wk, cut)
        I = _electric_glow(core, S, cool=cool) * br
        flash = ss(r, 0.22 * (1 - cool) + 0.04, 0.0) * (1 - cool) ** 1.5
        rr = 0.12 + 0.8 * ease_out(i / 10)
        ring = ss(np.abs(r - rr), 0.018, 0.004) * max(0.0, 1 - i / 11) * 0.8
        frames.append(np.clip(np.maximum.reduce([I, flash, ring]), 0, 1))
    return frames


def thunder_arc(n=16, seed=421):
    """Crackling arcs (loop): short fractal arcs jump around a centre, re-striking every 2 frames, for charged
    hands, auras and the god-mode body. Layered."""
    frames = []
    for i in range(n):
        fr = np.random.default_rng(seed * 100 + i // 2)
        bolts = []
        for _ in range(3):
            a = fr.uniform(0, TAU)
            r0, r1 = S * fr.uniform(0.08, 0.2), S * fr.uniform(0.3, 0.46)
            a1 = a + fr.uniform(-0.8, 0.8)
            bolts += _bolt_tree(fr, (S / 2 + math.cos(a) * r0, S / 2 + math.sin(a) * r0), (S / 2 + math.cos(a1) * r1, S / 2 + math.sin(a1) * r1),
                                S * 0.006, depth=1, branches=2, rough=0.3)
        core = _render_bolts(bolts, S)
        frames.append(_electric_glow(core, S, k_haze=0.2) * (0.85 + 0.15 * (i % 2)))
    return frames


def plasma_orb(n=16, seed=431):
    """Charged plasma ball (loop): white-hot core fading through the body to a soft fresnel edge (no hard
    outline), swirling energy streaks rotating inside, short arcs crawling over the surface and a flickering
    corona with discharges leaving it. Layered."""
    x, y = coords(S)
    r, a = polar_of(x, y)
    R = 0.34
    sw = tnoise(256, 1024, 30, 140, seed, 4)            # angle-periodic swirl field (rows = radius, cols = angle)
    frames = []
    for i in range(n):
        fr = np.random.default_rng(seed * 100 + i // 2)
        o = int(1024 * i / n)
        rot = np.roll(sw, -o, axis=1)
        rr = np.clip(r / R, 0, 1)
        ai = (((a + math.pi) / TAU) * 1023).astype(int)
        ri = (np.clip(rr + 0.15 * np.sin(a * 3 + i * 0.4), 0, 1) * 255).astype(int)
        swirl = rot[ri, ai]
        inside = ss(r, R + 0.01, R - 0.02)
        core = ss(r, R * 0.55, 0.0) ** 1.4
        body = inside * (0.38 + 0.3 * levels(swirl, 0.35, 0.85) * (0.4 + 0.6 * rr))
        fres = inside * ss(rr, 0.55, 0.98) * 0.35
        corona = (1 - ss(r, R, R + 0.07 + 0.03 * fr.random())) * (r > R - 0.01) * 0.45
        bolts = []
        for _ in range(4):           # arcs hugging the surface
            a0 = fr.uniform(0, TAU)
            span = fr.uniform(0.5, 1.1)
            pts = [(S / 2 + math.cos(a0 + span * k / 6) * S * R * 0.5 * fr.uniform(0.92, 1.06), S / 2 + math.sin(a0 + span * k / 6) * S * R * 0.5 * fr.uniform(0.92, 1.06)) for k in range(7)]
            for p, q in zip(pts[:-1], pts[1:]):
                bolts.append((_frac_path(fr, p, q, rough=0.25, depth=3), S * 0.006, S * 0.004, 1.0, 1))
        for _ in range(2):           # discharges leaving the corona
            a0 = fr.uniform(0, TAU)
            p = (S / 2 + math.cos(a0) * S * R * 0.5, S / 2 + math.sin(a0) * S * R * 0.5)
            q = (S / 2 + math.cos(a0 + fr.uniform(-0.35, 0.35)) * S * fr.uniform(0.3, 0.44), S / 2 + math.sin(a0 + fr.uniform(-0.35, 0.35)) * S * fr.uniform(0.3, 0.44))
            bolts += _bolt_tree(fr, p, q, S * 0.005, depth=0, rough=0.3)
        arcs = _electric_glow(_render_bolts(bolts, S), S, k_haze=0.1)
        frames.append(np.clip(np.maximum.reduce([body + core * 0.75 + fres, corona, arcs]), 0, 1))
    return frames


def storm_cloud(n=16, seed=441):
    """Dark storm cloud: heavy billowing lobes with painted underside shadow; lightning flashing inside lights
    patches of it from within on a few frames. Shaded (tint deep navy; the flashes stay bright)."""
    rng = np.random.default_rng(seed)

    def layout(r):
        sp = [(0, 0.05, 0.46), (-0.4, -0.02, 0.36), (0.42, 0.0, 0.38)]
        for _ in range(18):
            a = r.uniform(0, TAU)
            d = r.uniform(0.3, 0.6)
            sp.append((math.cos(a) * d * 1.25, math.sin(a) * d * 0.5 + 0.05, r.uniform(0.16, 0.3)))
        return sp
    alphas, vals = _cloud_frames(n, seed, layout, spread=(1.15, 0.85))
    x, y = coords(S)
    out_v = []
    for i, (a, v) in enumerate(zip(alphas, vals)):
        v = 0.42 + 0.5 * (v - 0.6) / 0.4           # heavy base tone, painted lit tops
        if i in (2, 3, 6, 9, 10):                    # internal flashes
            cx, cy = rng.uniform(-0.4, 0.4), rng.uniform(-0.15, 0.2)
            fl = ss(np.hypot(x - cx, (y - cy) * 1.4), 0.6, 0.0) * (1.0 if i in (2, 6, 9) else 0.55)
            v = np.clip(v + fl * 1.1, 0, 1)
        out_v.append(np.clip(v, 0, 1))
    return alphas, out_v


def lichtenberg(seed=451):
    """Electrical burn on the ground: a dense fractal branching figure radiating from the strike point,
    glowing hot at first (layered, tint cyan/white) - pair with scorch_burn underneath."""
    rng = np.random.default_rng(seed)
    c = (S / 2, S / 2)
    bolts = []
    for k in range(9):
        a = k / 9 * TAU + rng.uniform(-0.25, 0.25)
        L = S * rng.uniform(0.34, 0.48)
        bolts += _bolt_tree(rng, c, (c[0] + math.cos(a) * L, c[1] + math.sin(a) * L), S * 0.008, depth=3, branches=5, rough=0.3, spread=(0.3, 1.0))
    core = _render_bolts(bolts, S)
    x, y = coords(S)
    r, _ = polar_of(x, y)
    I = _electric_glow(core, S, k_outer=0.6, k_haze=0.15)
    return np.clip(np.maximum(I, ss(r, 0.07, 0.0)), 0, 1) * ss(r, 0.98, 0.8)


def scorch_burn(seed=451):
    """Dark burn mark matching lichtenberg (same branches, thicker, soot halo). Shaded: tint near-black."""
    rng = np.random.default_rng(seed)
    c = (S / 2, S / 2)
    bolts = []
    for k in range(9):
        a = k / 9 * TAU + rng.uniform(-0.25, 0.25)
        L = S * rng.uniform(0.34, 0.48)
        bolts += _bolt_tree(rng, c, (c[0] + math.cos(a) * L, c[1] + math.sin(a) * L), S * 0.012, depth=3, branches=6, rough=0.3, spread=(0.3, 1.0))
    core = _render_bolts(bolts, S, width_k=1.8)
    x, y = coords(S)
    r, _ = polar_of(x, y)
    nz = noise(S, S, 40, 40, seed + 1, 4)
    soot = ss(r + (nz - 0.5) * 0.25, 0.55, 0.1) * 0.55
    A = np.clip(np.maximum(blur(core, 1.5), soot), 0, 1) * ss(r, 0.98, 0.8)
    V = np.clip(0.18 + 0.25 * nz - 0.12 * blur(core, 2), 0, 1)
    return [A], [V]


def static_sparks(n=16, seed=461):
    """16 tiny electric crackles (FlipbookStartRandom): Y and zig-zag micro arcs with a bright pinpoint. Shaded."""
    alphas, vals = [], []
    for i in range(n):
        rng = np.random.default_rng(seed * 7 + i)
        a = rng.uniform(0, TAU)
        p = (S / 2 - math.cos(a) * S * 0.3, S / 2 - math.sin(a) * S * 0.3)
        q = (S / 2 + math.cos(a) * S * 0.32, S / 2 + math.sin(a) * S * 0.32)
        bolts = _bolt_tree(rng, p, q, S * 0.016, depth=1, branches=2, rough=0.3)
        core = _render_bolts(bolts, S)
        I = _electric_glow(core, S, k_haze=0.1)
        alphas.append(I)
        vals.append(np.clip(0.65 + 0.35 * core, 0, 1))
    return alphas, vals


def ion_haze(n=16, seed=471):
    """Faint ionised air: thin wispy veils that drift and thin out (behind arcs, inside god mode aura). Shaded."""
    x, y = coords(S)
    r, a = polar_of(x, y)
    base = blur(noise(S, S, 140, 60, seed, 3), S * 0.01)
    alphas, vals = [], []
    for i in range(n):
        t = i / (n - 1)
        g = 0.5 + 0.5 * ease_out(t / 0.6)
        f = pc.sample(base, np.clip(x / g, -1, 1), np.clip(y / g + t * 0.2, -1, 1))
        A = blur(levels(f, 0.45 + 0.2 * t, 0.9), S * 0.008) * ss(r, g * 0.95, g * 0.3) * (1 - 0.7 * t) * 0.55
        alphas.append(np.clip(A, 0, 1))
        vals.append(np.clip(0.8 + 0.2 * f, 0, 1))
    return alphas, vals


def _strip_path(rng, W, H, amp=0.22, depth=7, decay=0.55):
    """Periodic 1-D midpoint displacement: y offsets across the strip, same height at both ends (wraps)."""
    ys = np.zeros(2)
    disp = amp * H
    for _ in range(depth):
        mid = (ys[:-1] + ys[1:]) / 2 + rng.normal(0, disp, len(ys) - 1)
        out = np.empty(len(ys) * 2 - 1)
        out[0::2], out[1::2] = ys, mid
        ys = out
        disp *= decay
    ys = ys - (ys[0] + ys[-1]) / 2
    ys = ys * min(1.0, (H * 0.3) / (np.abs(ys).max() + 1e-6)) + H / 2
    xs = np.linspace(0, W, len(ys))
    return [np.array([x_, y_]) for x_, y_ in zip(xs, ys)]


def _thunder_strip(seed):
    """Tileable lightning ribbon for Beams/Trails (u along, wraps): a sharp zig-zag bolt pinned to the same
    height at both ends, with a few short branches. 1024x256. Layered. Swap the 4 variants every ~0.05 s."""
    def fn():
        rng = np.random.default_rng(seed)
        W, H = 1024 * SS, 256 * SS
        main = _strip_path(rng, W, H)
        img = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(img)
        for j in range(len(main) - 1):
            d.line([tuple(main[j]), tuple(main[j + 1])], fill=255, width=int(H * 0.024))
        for _ in range(4):
            i = int(rng.uniform(0.08, 0.92) * (len(main) - 1))
            p = main[i]
            end = (p[0] + rng.uniform(70, 180) * SS, p[1] + rng.choice([-1, 1]) * rng.uniform(0.12, 0.28) * H)
            br = _frac_path(rng, p, end, rough=0.3, depth=4)
            for j in range(len(br) - 1):
                w = max(1, int(H * 0.013 * (1 - j / len(br))))
                d.line([tuple(br[j]), tuple(br[j + 1])], fill=210, width=w)
        core = np.asarray(img, np.float32) / 255
        inner = ndi.gaussian_filter(core, H * 0.012, mode="wrap")
        outer = ndi.gaussian_filter(core, H * 0.05, mode="wrap")
        return np.clip(core + inner * 0.6 + outer * 0.45, 0, 1)
    return fn


def storm_flash(n=16, seed=441):
    """Additive companion to storm_cloud: the light of lightning flashing inside the cloud on frames 2, 3, 6,
    9, 10 (same timing). Stack it over storm_cloud with LightEmission 1. White."""
    rng = np.random.default_rng(seed)
    x, y = coords(S)
    out = []
    for i in range(n):
        F = np.zeros_like(x)
        if i in (2, 3, 6, 9, 10):
            cx, cy = rng.uniform(-0.4, 0.4), rng.uniform(-0.15, 0.2)
            F = ss(np.hypot(x - cx, (y - cy) * 1.4), 0.6, 0.0) * (1.0 if i in (2, 6, 9) else 0.55)
        out.append(F)
    return out


# ================================================================ THUNDER CEL (v2: anime cel lightning, Enel reference)
# Reference study (anime Goro Goro lightning): a thin white core inside a FLAT saturated body with a hard edge and
# only a tight halo; jagged angular runs with short hooked branches all along every bolt; bolts bunch into a
# crackling bush. So each layer is painted explicitly with hard anti-aliased edges instead of being thresholded
# out of one soft glow field: core = thin hot line, mid = flat body band, rim = filled silhouette a little wider
# (the dark outline when tinted indigo, alpha-blended), glow = tight halo.
def _jag_path(rng, a, b, seg=(0.07, 0.16), dev=(16, 31), run_p=0.25):
    """Angular lightning: straight runs whose heading alternates side of the target line by 16-31 deg, so
    consecutive kinks land at ~30-60 deg (the approved shape rule); now and then a longer straighter run."""
    a, b = np.array(a, float), np.array(b, float)
    L = np.linalg.norm(b - a) + 1e-9
    pts, p, side = [a], a.copy(), rng.choice([-1, 1])
    for _ in range(80):
        to = b - p
        dist = np.linalg.norm(to)
        if dist < L * seg[1] * 0.9:
            pts.append(b)
            break
        base = math.atan2(to[1], to[0])
        dv = math.radians(rng.uniform(*dev))
        ln = L * rng.uniform(*seg)
        if rng.random() < run_p:
            ln *= 1.7
            dv *= 0.35
        ang = base + side * dv
        side = -side if rng.random() < 0.85 else side
        p = p + np.array([math.cos(ang), math.sin(ang)]) * min(ln, dist)
        pts.append(p.copy())
    return pts


def _micro(rng, pts, k=0.045, sub=(2, 4)):
    """Fine jagged detail inside each straight run: split it into 2-4 pieces with small perpendicular kicks, so a
    run still reads straight from afar but crackles up close (the anime bolt texture)."""
    out = [np.array(pts[0], float)]
    for p, q in zip(pts[:-1], pts[1:]):
        p, q = np.array(p, float), np.array(q, float)
        d = q - p
        ln = np.linalg.norm(d) + 1e-9
        nrm = np.array([-d[1], d[0]]) / ln
        n = int(rng.integers(sub[0], sub[1] + 1))
        for i in range(1, n):
            out.append(p + d * (i / n + rng.uniform(-0.08, 0.08) / n) + nrm * ln * rng.uniform(-k, k))
        out.append(q)
    return out


def _cel_tree(rng, a, b, w0, forks=2, hooks=0.55, depth=1, seg=(0.07, 0.16), t0=0.0, tip=0.25):
    """Main jagged bolt (with micro-jags) + forks (recursive, thinner) + short hooked barbs that taper to points.
    Returns [(pts, widths, t0)]: per-vertex widths (thick-thin pulse, tapering to the tip) and t0 = where along the
    parent the bolt starts (0..1) so the draw-in follows the trunk."""
    main = _micro(rng, _jag_path(rng, a, b, seg))
    n = len(main)
    pulse = np.convolve(rng.uniform(0.7, 1.25, n + 4), np.ones(3) / 3, "same")[2:n + 2]
    widths = w0 * pulse * np.linspace(1.0, tip, n)
    out = [(main, widths, t0)]
    L = np.linalg.norm(np.array(b, float) - np.array(a, float))
    for j in range(2, n - 1):                                      # hooks: short pointed barbs
        if rng.random() < hooks * 0.5:
            d = main[j] - main[j - 1]
            h = math.atan2(d[1], d[0]) + rng.choice([-1, 1]) * math.radians(rng.uniform(35, 75))
            ln = L * rng.uniform(0.02, 0.05)
            q = main[j] + np.array([math.cos(h), math.sin(h)]) * ln
            pts = [main[j], q]
            if rng.random() < 0.6:
                h2 = h + rng.choice([-1, 1]) * math.radians(rng.uniform(30, 60))
                pts.append(q + np.array([math.cos(h2), math.sin(h2)]) * ln * rng.uniform(0.5, 0.9))
            wj = widths[j] * 0.6
            out.append((pts, np.linspace(wj, 0.0, len(pts)), t0 + (1 - t0) * j / n))
    if depth > 0:
        for _ in range(forks):                                     # forks: real branches, pointed tips
            j = min(int(rng.uniform(0.15, 0.7) * (n - 1)) + 1, n - 2)
            d = main[j + 1] - main[j]
            h = math.atan2(d[1], d[0]) + rng.choice([-1, 1]) * math.radians(rng.uniform(25, 50))
            ln = L * rng.uniform(0.2, 0.4) * (1 - j / n) ** 0.5
            end = main[j] + np.array([math.cos(h), math.sin(h)]) * ln
            out += _cel_tree(rng, main[j], end, widths[j] * 0.55, forks=1, hooks=hooks * 0.7, depth=depth - 1, seg=seg,
                             t0=t0 + (1 - t0) * j / n, tip=0.0)
    return out


def _cel_draw(bolts, W, H, k=1.0, keep=1.0, jitter=0.0, rng=None, wrap=False):
    """Fill each bolt as one tapered polygon (mitred joins, pointed tips): width scaled by k. keep = how far the
    strike has drawn along the trunk (child bolts start when the trunk reaches them). wrap tiles in x."""
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    offs = (-W, 0, W) if wrap else (0,)
    for pts, ws, t0 in bolts:
        vis = 1.0 if keep >= 1 else max(0.0, min(1.0, (keep - t0) / max(1e-6, 1 - t0)))
        if vis <= 0:
            continue
        P = [np.array(q, float) for q in pts]
        Wd = np.array(ws, float) * k
        if vis < 1:
            f = (len(P) - 1) * vis
            m = int(f)
            P, Wd = P[:m + 2], Wd[:m + 2].copy()
            if m + 1 < len(pts):
                P[-1] = pts[m] + (np.array(pts[m + 1]) - pts[m]) * (f - m)
            Wd[-1] = 0.0                                     # the drawing head is pointed too
        if len(P) < 2:
            continue
        if jitter and rng is not None:
            P = [q + rng.normal(0, jitter, 2) if 0 < j < len(P) - 1 else q for j, q in enumerate(P)]
        left, right = [], []
        for j in range(len(P)):
            a_ = P[max(0, j - 1)]; b_ = P[min(len(P) - 1, j + 1)]
            t = b_ - a_
            t = t / (np.linalg.norm(t) + 1e-9)
            nrm = np.array([-t[1], t[0]])
            miter = 1.0
            if 0 < j < len(P) - 1:
                t1 = P[j] - P[j - 1]; t1 /= (np.linalg.norm(t1) + 1e-9)
                miter = min(2.0, 1.0 / max(0.35, abs(np.dot(np.array([-t1[1], t1[0]]), nrm))))
            h = max(0.0, Wd[j]) / 2 * miter
            left.append(P[j] + nrm * h); right.append(P[j] - nrm * h)
        poly = left + right[::-1]
        for ox in offs:
            d.polygon([(q[0] + ox, q[1]) for q in poly], fill=255)
    return np.asarray(img, np.float32) / 255


CEL_K = {"core": 1.0, "mid": 2.5, "rim": 3.7}


def _cel_layers(bolts, W, H, br=1.0, keep=1.0, jitter=0.0, rng=None, cool=0.0, wrap=False, extra=None):
    """Explicit cel layers. cool (0..1): the hot core thins away first, the body narrows, the outline lingers."""
    out = {}
    for L, k in CEL_K.items():
        kk = k * ((1 - cool) if L == "core" else (1 - 0.45 * cool) if L == "mid" else (1 - 0.25 * cool))
        f = _cel_draw(bolts, W, H, kk, keep, jitter, np.random.default_rng(rng) if rng is not None else None, wrap) if kk > 0.05 else np.zeros((H, W), np.float32)
        out[L] = f
    if extra:
        for L, f in extra.items():
            out[L] = np.maximum(out[L], f)
    sig = H * 0.012 if wrap else W * 0.012
    out["glow"] = np.clip(ndi.gaussian_filter(out["rim"], sig, mode="wrap" if wrap else "constant") * 1.3, 0, 1) * 0.75
    a = br
    return {L: np.clip(f * a, 0, 1) for L, f in out.items()}


# per frame: (keep, brightness, jitter step, cool) - draw-in over 2 frames, hold with re-strike flicker, cool
CEL_STRIKE = [(0.5, 0.9, 0, 0), (1, 1, 0, 0), (1, 1, 1, 0), (1, 0.55, 1, 0.05), (1, 1, 2, 0.05), (1, 0.85, 2, 0.12),
              (1, 0.5, 3, 0.2), (1, 0.9, 3, 0.25), (1, 0.75, 3, 0.35), (1, 0.65, 3, 0.45), (1, 0.55, 3, 0.55),
              (1, 0.45, 3, 0.65), (1, 0.35, 3, 0.75), (1, 0.25, 3, 0.85), (1, 0.15, 3, 0.92), (1, 0.06, 3, 1.0)]


def thunder_bolt_v2():
    """Sky-to-ground strike, cel: jagged trunk with hooked barbs and two forks; draws in over 2 frames, re-strikes,
    then cools (core thins out first, outline lingers)."""
    rng = np.random.default_rng(1406)
    m = S * 0.07
    bolts = _cel_tree(rng, (S * 0.5, m), (S * 0.5 + rng.normal(0, S * 0.04), S - m), S * 0.012, forks=2, hooks=0.6)
    frames = []
    for i, (keep, br, jit, cool) in enumerate(CEL_STRIKE):
        frames.append(_cel_layers(bolts, S, S, br, keep, S * 0.0025 * jit, 7 + jit, cool))
    return frames


def thunder_burst_v2():
    """Electric impact, cel: an anime star flash (sharp uneven spikes, white hot) with 8 jagged hooked bolts
    striking out in 2 frames, re-striking, then cooling from the tips. No ring (rings read as vector circles)."""
    rng = np.random.default_rng(1411)
    c = np.array([S / 2, S / 2])
    bolts = []
    for k in range(8):
        a = k / 8 * TAU + rng.uniform(-0.25, 0.25)
        L = S * rng.uniform(0.3, 0.43)
        bolts += _cel_tree(rng, c, c + np.array([math.cos(a), math.sin(a)]) * L, S * 0.009, forks=1, hooks=0.5, depth=1)
    x, y = coords(S)
    r, ang = polar_of(x, y)
    spikes = np.abs(np.cos(ang * 3.5 + 0.4)) ** 6 * 0.6 + np.abs(np.cos(ang * 2.5 + 1.3)) ** 10 * 0.4   # uneven star
    frames = []
    for i, (keep, br, jit, cool) in enumerate(CEL_STRIKE):
        keep = min(1.0, (i + 1) / 2.0)
        star_r = (0.06 + 0.22 * spikes) * max(0.0, 1 - i / 5) ** 1.2
        star = ss(r, star_r + 0.004, star_r - 0.004) if i < 5 else np.zeros_like(r)
        extra = {"core": ss(r, star_r * 0.55 + 0.003, star_r * 0.55 - 0.003) if i < 5 else np.zeros_like(r), "mid": star,
                 "rim": ss(r, star_r * 1.25 + 0.006, star_r * 1.25 - 0.006) if i < 5 else np.zeros_like(r)}
        frames.append(_cel_layers(bolts, S, S, br, keep, S * 0.0025 * jit, 11 + jit, cool, extra=extra))
    return frames


def thunder_arc_v2():
    """Crackling arcs (loop), cel: 4 short jagged hooked arcs bunched around the centre like a crackling bush,
    re-striking on new paths every 2 frames."""
    frames = []
    for i in range(16):
        fr = np.random.default_rng(1421 * 100 + i // 2)
        bolts = []
        for _ in range(4):
            a = fr.uniform(0, TAU)
            r0, r1 = S * fr.uniform(0.04, 0.14), S * fr.uniform(0.3, 0.44)
            a1 = a + fr.uniform(-0.6, 0.6)
            bolts += _cel_tree(fr, (S / 2 + math.cos(a) * r0, S / 2 + math.sin(a) * r0), (S / 2 + math.cos(a1) * r1, S / 2 + math.sin(a1) * r1),
                               S * 0.0075, forks=1, hooks=0.6, depth=1, seg=(0.12, 0.26))
        frames.append(_cel_layers(bolts, S, S, 0.85 + 0.15 * (i % 2)))
    return frames


def _thunder_strip_v2(seed):
    """Tileable cel lightning ribbon (u along, wraps in u): a jagged trunk across the strip (same height at both
    ends) with hooked barbs and short forks, all kept inside v 0.1..0.9 so nothing is chopped at the ribbon edge.
    1024x256. Swap the 4 variants every ~0.05 s."""
    def fn():
        rng = np.random.default_rng(seed)
        W, H = 1024 * SS, 256 * SS
        lo, hi = H * 0.1, H * 0.9
        for _ in range(200):                                  # retry until the whole bolt stays inside the band
            bolts = _cel_tree(rng, (0, H / 2), (W, H / 2), H * 0.028, forks=3, hooks=0.6, depth=1, seg=(0.025, 0.06), tip=1.0)
            bolts[0][1][-1] = bolts[0][1][0]                  # same trunk width at both ends: no seam where it wraps
            ys = [q[1] for pts, _, _ in bolts for q in pts]
            if min(ys) > lo + H * 0.04 and max(ys) < hi - H * 0.04:
                break
        return _cel_layers(bolts, W, H, wrap=True)
    return fn


# ================================================================ registry
# kind: 'layered' (white layers), 'shaded' (alpha + grey value), 'white' (alpha only)
LIB = {
    #  name           (fn,            kind,      grid, glow sigma, palette for previews)
    "fire_burst":    (fire_burst,    "layered", 4, 7, "fire"),
    "flame_lick":    (flame_lick,    "layered", 4, 6, "fire"),
    "aura_wisp":     (aura_wisp,     "layered", 4, 6, "haki"),
    "smoke_puff":    (smoke_puff,    "shaded",  4, 0, "smoke"),
    "dust_burst":    (dust_burst,    "shaded",  4, 0, "dust"),
    "star_flash":    (star_flash,    "layered", 4, 6, "light"),
    "god_rays":      (god_rays,      "layered", 4, 5, "white"),
    "orb_glow":      (orb_glow,      "layered", 4, 6, "light"),
    "flecks":        (flecks,        "shaded",  2, 0, "spark"),
    "embers":        (embers,        "shaded",  4, 0, "ember"),
    "shock_ring":    (shock_ring,    "layered", 1, 5, "quake"),
    "wind_arcs":     (wind_arcs,     "white",   2, 0, "ice"),
    "slash":         (slash,         "layered", 4, 6, "slash"),
    "crack_glow":    (crack_glow,    "layered", 1, 5, "quake"),
    "glass_shatter": (glass_shatter, "layered", 1, 5, "quake"),
    "lightning":     (lightning,     "layered", 4, 5, "haki"),
    "beam_strip":    (beam_strip,    "layered", 0, 6, "light"),
    "speedlines":    (speedlines,    "white",   0, 0, "white"),
    "slash_strip":   (slash_strip,   "strip",   0, 0, "slash"),
    "energy_strip":  (energy_strip,  "strip",   0, 0, "quake"),
    "edge_strip":    (edge_strip,    "strip",   0, 0, "light"),
    "wind_strip":    (wind_strip,    "white",   0, 0, "white"),
    "dragon_head":   (dragon_head,   "layered", 1, 5, "fire"),
    "phoenix_wing":  (phoenix_wing,  "layered", 1, 5, "slash"),
    "giant_fist":    (giant_fist,    "layered", 1, 5, "fire"),
    "water_shark":   (water_shark,   "layered", 1, 4, "slash"),
    "palm_strike":   (palm_strike,   "layered", 1, 5, "light"),
    "magma_splash":  (magma_splash,  "layered", 4, 6, "magma"),
    "lava_drops":    (lava_drops,    "shaded",  4, 0, "ember"),
    "light_burst":   (light_burst,   "layered", 4, 5, "light"),
    "shock_ripple":  (shock_ripple,  "layered", 4, 4, "quake"),
    "ice_burst":     (ice_burst,     "layered", 4, 5, "ice"),
    "frost_mist":    (frost_mist,    "shaded",  4, 0, "mist"),
    "ice_chips":     (ice_chips,     "shaded",  4, 0, "icechip"),
    "void_smoke":    (void_smoke,    "layered", 4, 6, "dark"),
    "void_orb":      (void_orb,      "layered", 4, 5, "dark"),
    "electric_burst": (electric_burst, "layered", 4, 5, "thunder"),
    "haki_burst":    (haki_burst,    "layered", 4, 5, "haki"),
    "blade_cuts":    (blade_cuts,    "layered", 4, 4, "slash"),
    "water_splash":  (water_splash,  "layered", 4, 4, "water"),
    "spray_puff":    (spray_puff,    "shaded",  4, 0, "spray"),
    "water_drops":   (water_drops,   "shaded",  4, 0, "spray"),
    "thunder_bolt":  (thunder_bolt,  "layered", 4, 5, "thunder"),
    "thunder_burst": (thunder_burst, "layered", 4, 5, "thunder"),
    "thunder_arc":   (thunder_arc,   "layered", 4, 4, "thunder"),
    "plasma_orb":    (plasma_orb,    "layered", 4, 5, "thunder"),
    "storm_cloud":   (storm_cloud,   "shaded",  4, 0, "storm"),
    "lichtenberg":   (lichtenberg,   "layered", 1, 4, "thunder"),
    "scorch_burn":   (scorch_burn,   "shaded",  1, 0, "soot"),
    "static_sparks": (static_sparks, "shaded",  4, 0, "spark_blue"),
    "ion_haze":      (ion_haze,      "shaded",  4, 0, "ion"),
    "storm_flash":   (storm_flash,   "white",   4, 0, "ion"),
    "thunder_strip_1": (_thunder_strip(481), "layered", 0, 5, "thunder"),
    "thunder_strip_2": (_thunder_strip(482), "layered", 0, 5, "thunder"),
    "thunder_strip_3": (_thunder_strip(483), "layered", 0, 5, "thunder"),
    "thunder_strip_4": (_thunder_strip(484), "layered", 0, 5, "thunder"),
    # v2 cel set (anime reference): explicit hard-edged layers
    "thunder_bolt_v2":  (thunder_bolt_v2,  "cel", 4, 0, "thunder"),
    "thunder_burst_v2": (thunder_burst_v2, "cel", 4, 0, "thunder"),
    "thunder_arc_v2":   (thunder_arc_v2,   "cel", 4, 0, "thunder"),
    "thunder_strip_v2_1": (_thunder_strip_v2(2481), "cel", 0, 0, "thunder"),
    "thunder_strip_v2_2": (_thunder_strip_v2(2482), "cel", 0, 0, "thunder"),
    "thunder_strip_v2_3": (_thunder_strip_v2(2483), "cel", 0, 0, "thunder"),
    "thunder_strip_v2_4": (_thunder_strip_v2(2484), "cel", 0, 0, "thunder"),
}

PALETTES = {
    "fire":  {"glow": "#ff5a14", "rim": "#d8321a", "mid": "#ff9226", "core": "#fff1b8"},
    "light": {"glow": "#ffc824", "rim": "#ffa81a", "mid": "#ffe56a", "core": "#ffffff"},
    "quake": {"glow": "#2cf0c4", "rim": "#11b894", "mid": "#8cffe6", "core": "#ffffff"},
    "ice":   {"glow": "#8fd8ff", "rim": "#5ab4ff", "mid": "#ffffff", "core": "#ffffff"},
    "haki":  {"glow": "#ff1e3c", "rim": "#2a0010", "mid": "#ff2a48", "core": "#ffe0e6"},
    "slash": {"glow": "#4aa8ff", "rim": "#1e5cff", "mid": "#9fd2ff", "core": "#ffffff"},
    "white": {"glow": "#ffffff", "rim": "#dfe8ff", "mid": "#ffffff", "core": "#ffffff"},
    "smoke": {"mid": "#f4f1ec"},
    "dust":  {"mid": "#e8d6b0"},
    "ember": {"mid": "#ff8a2a", "additive": True},
    "spark": {"mid": "#ffe27a", "additive": True},
    "magma": {"glow": "#ff3a0a", "rim": "#3a0a04", "mid": "#ff6a1a", "core": "#ffd27a"},
    "dark": {"glow": "#7a2cff", "rim": "#c9a0ff", "mid": "#3a1068", "core": "#0a0012"},
    "thunder": {"glow": "#3a8cff", "rim": "#2a1a9a", "mid": "#6fe0ff", "core": "#ffffff"},
    "storm": {"mid": "#2a3350"},
    "soot": {"mid": "#1a1612"},
    "spark_blue": {"mid": "#9fe8ff", "additive": True},
    "ion": {"mid": "#7fc8ff", "additive": True},
    "water": {"glow": "#3ab0ff", "rim": "#0a5cc0", "mid": "#8fd4ff", "core": "#ffffff"},
    "mist": {"mid": "#e6f6ff"},
    "icechip": {"mid": "#bfe8ff", "additive": True},
    "spray": {"mid": "#e8f6ff"},
}


def build(name, out):
    fn, kind, grid, gsig, _ = LIB[name]
    res = fn()
    paths = []
    if kind in ("layered", "cel"):
        frames = res if isinstance(res, list) else [res]
        per = frames if kind == "cel" else [pc.split(f, glow_sigma=gsig * SS) for f in frames]
        for L in ("glow", "rim", "mid", "core"):
            if grid == 0:                                   # rectangular strip
                h, w = per[0][L].shape
                a = pc.down_rect(per[0][L], w // SS, h // SS)
            elif grid == 1:
                a = pc.down(per[0][L], CELL * 2) * pc.edge_fade(CELL * 2)
            else:
                a = pc.sheet([p[L] for p in per], grid, CELL)
            p = os.path.join(out, f"{name}_{L}.png")
            pc.save_white(a, p)
            paths.append(p)
    elif kind == "strip":
        A, V = res
        p = os.path.join(out, f"{name}.png")
        pc.save_white(A, p, V)
        paths.append(p)
    elif kind == "shaded":
        alphas, vals = res
        if grid == 1:
            A = pc.down(alphas[0], CELL * 2) * pc.edge_fade(CELL * 2)
            V = pc.down(vals[0], CELL * 2)
        else:
            A = pc.sheet(alphas, grid, CELL)
            V = pc.sheet(vals, grid, CELL, fade=False)
        p = os.path.join(out, f"{name}.png")
        pc.save_white(A, p, V)
        paths.append(p)
    else:  # white
        frames = res if isinstance(res, list) else [res]
        if grid == 0:
            h, w = frames[0].shape
            A = frames[0] if name.endswith("_strip") else pc.down_rect(frames[0], w // SS, h // SS)
        elif grid == 1:
            A = pc.down(frames[0], CELL * 2) * pc.edge_fade(CELL * 2)
        else:
            A = pc.sheet(frames, grid, CELL)
        p = os.path.join(out, f"{name}.png")
        pc.save_white(A, p)
        paths.append(p)
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    pc.ensure(a.out)
    for nm in a.names or list(LIB):
        for p in build(nm, a.out):
            print("wrote", os.path.relpath(p, a.out))


if __name__ == "__main__":
    main()
