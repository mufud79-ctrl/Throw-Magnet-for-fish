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
}


def build(name, out):
    fn, kind, grid, gsig, _ = LIB[name]
    res = fn()
    paths = []
    if kind == "layered":
        frames = res if isinstance(res, list) else [res]
        per = [pc.split(f, glow_sigma=gsig * SS) for f in frames]
        for L in ("glow", "rim", "mid", "core"):
            if grid == 0:                                   # rectangular strip
                h, w = frames[0].shape
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
