"""Texture recipes painted with craft.py.  Run:  python3 craft/textures.py [names...]
Writes out/textures/<name>_{glow,rim,mid,core}.png (layered) or <name>.png (single) plus
out/textures/_preview_<name>.png."""
import os
import sys
import numpy as np
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(__file__))
from craft import SS, ss, noise, levels, blur, mblur, polar, split, sheet, save_white, preview  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), '..', 'out', 'textures')
D = np.pi / 180


def seqv(a, i):
    return a[min(len(a) - 1, max(0, i))]


# ================================================================ energy crescent
def energy_arc(i, seed=5, cell=256, a0=215, sweep=235, r_out=0.74, depth=0.62, tm=None, tongues=6, white=1.0):
    """Swoosh of feathery tongues: each tongue is a tapered band that flicks outward at its tip,
    painted with a hot outer edge, smudged streaks and organic (domain-warped) edges."""
    S = cell * SS
    H, W, VT = 420, 1500, -0.42           # strip rows span v in [VT, 1]
    head = seqv([0.6, 0.93, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], i)
    tail = seqv([0, 0, 0, 0.04, 0.11, 0.2, 0.3, 0.41, 0.52, 0.62, 0.71, 0.79, 0.86, 0.92, 0.96, 0.99], i)
    amp = seqv(tm or [0.7, 0.95, 1, 0.97, 0.9, 0.8, 0.7, 0.6, 0.5, 0.41, 0.33, 0.26, 0.19, 0.13, 0.08, 0.04], i)
    rng = np.random.default_rng(seed)
    T = [dict(a=0.0, b=1.0, th=0.62, off=0.0, flick=0.18)]
    for k in range(tongues - 1):
        a = rng.uniform(0.0, 0.7)
        T.append(dict(a=a, b=min(1.0, a + rng.uniform(0.25, 0.5)), th=rng.uniform(0.2, 0.42), off=rng.uniform(-0.1, 0.55), flick=rng.uniform(0.15, 0.45)))
    vr, u = np.mgrid[0:H, 0:W].astype(np.float32)
    v = VT + vr / (H - 1) * (1 - VT)
    u /= W - 1
    # organic edges: displace the strip with low-frequency noise
    dv = (noise(H, W, H * 0.4, W * 0.08, seed + 7, 3) - 0.5) * 0.09
    du = (noise(H, W, H * 0.3, W * 0.1, seed + 8, 3) - 0.5) * 0.012
    u2, v2 = u + du, v + dv
    flow = int(i * 31)
    n1 = np.roll(noise(H, W, H * 0.022, W * 0.32, seed, 5), flow, axis=1)
    n2 = np.roll(noise(H, W, H * 0.04, W * 0.2, seed + 1, 4), flow, axis=1)
    n3 = noise(H, W, H * 0.1, W * 0.06, seed + 2, 3)
    I = np.zeros((H, W), np.float32)
    for k, t in enumerate(T):
        a_ = max(t['a'], tail)
        b_ = min(t['b'], head)
        if b_ - a_ < 0.04:
            continue
        s = np.clip((u2 - a_) / (b_ - a_), 0, 1)
        win = ss((u2 - a_) / (b_ - a_), 0, 0.03) * ss((b_ - u2) / (b_ - a_), 0, 0.01)
        th = t['th'] * amp * np.maximum(np.sin(np.pi * np.clip(s ** 0.75, 0, 1)), 0) ** 0.7 + 1e-3
        c = t['off'] * amp - t['flick'] * s ** 3 * (0.6 + 0.4 * min(1, i / 4))   # tip flicks outward
        vv = (v2 - c) / th
        body = ss(vv, -0.06, 0.02) * ss(1 - vv, -0.1, 0.3)
        grad = np.clip(1 - vv, 0, 1) ** 1.1
        streak = 0.5 + 0.7 * levels(n1, 0.25, 0.85)
        I = np.maximum(I, body * (0.25 + 0.75 * grad) * streak * win * (1.0 if k == 0 else 0.9))
        I += np.exp(-np.clip(vv, 0, None) / 0.1) * ss(vv, -0.04, 0.0) * 0.5 * win * white
    wisp = levels(n2, 0.62, 0.95, 1.6) * ss(v, 0.3, 0.45) * ss(0.7 - v, 0, 0.2) * amp
    I += wisp * 0.35
    sc = np.clip((u - tail) / max(0.05, head - tail), 0, 1)
    I *= ss(n3 + sc * 1.6 - 0.35, 0, 0.35) ** 0.6
    I = mblur(I, 4)
    I = np.clip(I, 0, 1.3)
    return polar(I, S, r_out, r_out - depth, a0 * D, sweep * D, vtop=VT, spiral=0.06)


def ink_arc(i, seed=13, cell=256):
    S = cell * SS
    H, W = 220, 1400
    head = seqv([0.6, 0.92, 1], i)
    tail = seqv([0, 0, 0, 0, 0, 0, 0.03, 0.09, 0.17, 0.27, 0.38, 0.5, 0.62, 0.74, 0.86, 0.96], i)
    wm = seqv([0.75, 1, 1, 1, 0.97, 0.93, 0.87, 0.8, 0.71, 0.61, 0.5, 0.4, 0.3, 0.21, 0.13, 0.07], i)
    v, u = np.mgrid[0:H, 0:W].astype(np.float32)
    v /= H - 1
    u /= W - 1
    s = (u - tail) / max(0.05, head - tail)
    sc = np.clip(s, 0, 1)
    prof = np.maximum(np.sin(np.pi * sc ** 1.45), 0) ** 1.05      # needle at both ends, belly toward the head
    T = 0.95 * wm * prof + 1e-3
    wob = (noise(1, W, 1, W * 0.2, seed, 3)[0] - 0.5) * 0.1
    vv = (v - wob[None, :] * T) / T
    m = ss(1 - vv, 0, 0.025) * ss(vv + 0.02, 0, 0.025)
    for s0, ln in ((0.58, 0.9), (0.8, 0.6)):                         # inward spurs / barbs
        q = (sc - s0) / 0.1
        spur = (q > 0) & (q < 1)
        reach = T * (1 + ln * np.clip(1 - q, 0, 1) ** 1.6) * wm
        m = np.maximum(m, spur * ss(reach - v, 0, 0.012) * ss(v - T * 0.5, 0, 0.01))
    hair = noise(H, W, H * 0.025, W * 0.35, seed + 3, 4)
    m *= np.maximum(ss(sc, 0.0, 0.25), ss(hair, 0.42, 0.5))          # dry-brush split on the tail
    m *= ss(s, 0, 0.01) * ss(1 - s, 0, 0.003)
    m = levels(mblur(m, 1.2), 0.35, 0.65)
    return polar(m, S, 0.9, 0.9 - 0.27, 205 * D, 180 * D, spiral=0.12)



# ================================================================ helpers for the rest
def grid_xy(S):
    ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
    return (xs + 0.5) / S * 2 - 1, 1 - (ys + 0.5) / S * 2


def spikes_profile(W, n, seed, lmin, lmax, sharp=6.0, jitter=0.4):
    """1-D spiky length profile over u: n peaks with random lengths, smooth sharp tips."""
    rng = np.random.default_rng(seed)
    u = np.linspace(0, 1, W, dtype=np.float32)
    out = np.zeros(W, np.float32)
    for k in range(n):
        c = (k + 0.5 + rng.uniform(-jitter, jitter) * 0.5) / n
        L = rng.uniform(lmin, lmax)
        w = rng.uniform(0.35, 1.0) / n
        d = np.abs(((u - c + 0.5) % 1) - 0.5) / w
        out = np.maximum(out, L * np.clip(1 - d, 0, 1) ** (sharp / 4))
    return out


def swirl_paint(i, seed, cell, r_in, r_out, density, streak_w, spin, grow, fade, band=None, along=0.12, spiral=0.0, clouds=0.0, gain=1.0):
    S = cell * SS
    H, W = 360, 1600
    v, u = np.mgrid[0:H, 0:W].astype(np.float32)
    v /= H - 1
    u /= W - 1
    n1 = np.roll(noise(H, W, H * streak_w, W * along, seed, 5), int(i * spin), axis=1)
    n2 = np.roll(noise(H, W, H * 0.2, W * 0.05, seed + 1, 3), int(i * spin * 0.6), axis=1)
    I = levels(n1, 1 - density, 1.0, 1.4) * (0.4 + 0.8 * n2)
    if clouds:
        nc = np.roll(noise(H, W, H * 0.35, W * 0.1, seed + 5, 4), int(i * spin * 0.8), axis=1)
        I = np.maximum(I, levels(nc, 0.45, 0.9, 1.2) * clouds * ss(v, 0.05, 0.3))
    if band:
        I *= ss(v, 0, band) * ss(1 - v, 0, band)
    g = seqv(grow, i)
    I *= ss(n2 + g * 1.4 - 0.7, 0, 0.3)
    I *= seqv(fade, i)
    if spiral:   # seamless twirl: shear each row around the circle (wraps), then smear along it
        for r in range(H):
            I[r] = np.roll(I[r], int(spiral * W * (r / (H - 1)) ** 1.3))
    I = ndi.gaussian_filter1d(I, 7, axis=1, mode='wrap')
    return polar(np.clip(I * gain, 0, 1.2), S, r_out, r_in, 0.0, 2 * np.pi)


def wind_arc(i, cell=256):
    return energy_arc(i, seed=9, cell=cell, a0=205, sweep=215, r_out=0.82, depth=0.42, tongues=4, white=0.6,
                      tm=[0.55, 0.8, 0.85, 0.82, 0.76, 0.68, 0.6, 0.51, 0.43, 0.35, 0.28, 0.22, 0.16, 0.11, 0.07, 0.03])


def energy_swirl(i, cell=256):
    return swirl_paint(i, 61, cell, 0.06, 0.86, 0.5, 0.05, 40, along=0.3, spiral=0.45, clouds=0.9, gain=1.5, grow= [0.3, 0.7, 1, 1, 1, 1, 1, 1, 0.9, 0.8, 0.65, 0.5, 0.35, 0.2, 0.1, 0.0],
                       fade=[0.8, 1, 1, 1, 1, 1, 0.95, 0.9, 0.82, 0.72, 0.6, 0.48, 0.36, 0.25, 0.15, 0.07])


def ground_swirl(i, cell=256):
    return swirl_paint(i, 21, cell, 0.12, 0.9, 0.5, 0.035, 55, along=0.35, spiral=0.3, gain=1.3, grow= [0.4, 0.8, 1, 1, 1, 1, 1, 1, 1, 0.9, 0.8, 0.65, 0.5, 0.35, 0.2, 0.1],
                       fade=[0.8, 1, 1, 1, 1, 1, 0.95, 0.9, 0.82, 0.72, 0.6, 0.48, 0.36, 0.25, 0.15, 0.07])


def ring_slash(i, cell=256):
    return swirl_paint(i, 33, cell, 0.42, 0.88, 0.55, 0.05, -70, along=0.3, spiral=0.12, gain=1.2, grow= [0.3, 0.7, 1, 1, 1, 1, 1, 1, 0.95, 0.85, 0.7, 0.55, 0.4, 0.25, 0.12, 0.04],
                       fade=[0.8, 1, 1, 1, 1, 0.95, 0.9, 0.85, 0.78, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1], band=0.25)


def saw_blade(i, cell=256, seed=41):
    """Curved blade: serrated outer edge (fine long teeth), dark body, white teeth and screentone."""
    S = cell * SS
    H, W, VT = 300, 1400, -0.35
    open_ = seqv([0.4, 0.75, 0.95, 1, 1, 1, 1, 1, 0.97, 0.93, 0.87, 0.79, 0.69, 0.57, 0.43, 0.28], i)
    wm = seqv([0.7, 1, 1, 1, 1, 0.97, 0.93, 0.88, 0.82, 0.74, 0.65, 0.55, 0.44, 0.33, 0.22, 0.12], i)
    vr, u = np.mgrid[0:H, 0:W].astype(np.float32)
    v = VT + vr / (H - 1) * (1 - VT)
    u /= W - 1
    s = u / open_
    sc = np.clip(s, 0, 1)
    T = 0.9 * wm * np.maximum(np.sin(np.pi * sc ** 0.9), 0) ** 0.6 + 1e-3
    N = 26
    ph = (sc * N) % 1.0
    tooth = (ph ** 1.6) * 0.32 * T / 0.9 + 0.0                         # sawtooth: ramp then drop
    edge = -tooth                                                      # outer boundary (v < 0 = teeth)
    body = ss(v - edge, -0.006, 0.006) * ss(T - v, 0, 0.04) * (s <= 1)
    teeth = body * ss(-v, -0.01, 0.06)
    tone_u, tone_v = (u * 120) % 1 - 0.5, (vr / (H - 1) * 22) % 1 - 0.5
    dotr = 0.42 * ss(v, T * 0.25, T * 0.55) * ss(T * 0.95 - v, 0, T * 0.2)
    tone = (np.hypot(tone_u, tone_v) < dotr) * body
    I = body * 0.36 + np.maximum(teeth * 0.95, tone * 0.85)
    I *= ss(s, 0, 0.02)
    return polar(np.clip(I, 0, 1), S, 0.9, 0.9 - 0.62, 200 * D, 160 * D, vtop=VT, spiral=0.1)


def star4(i, cell=512):
    S = cell * SS
    x, y = grid_xy(S)
    sc = [0.6, 1, 0.82, 0.5][i]
    rot = [0.0, 0.05, 0.09, 0.12][i] + np.pi / 4
    xr, yr = x * np.cos(rot) + y * np.sin(rot), -x * np.sin(rot) + y * np.cos(rot)
    ax, ay = np.abs(xr) / sc, np.abs(yr) / sc
    # concave astroid-like star: |x|^p + |y|^p < 1 with p < 1
    f = ax ** 0.42 + ay ** 0.42
    m = ss(1.0 - f + 0.06, 0, 0.03) * ss(0.92 - np.hypot(ax, ay), 0, 0.02)
    ridge = np.exp(-np.minimum(ax, ay) / 0.012) * m
    r = np.hypot(ax, ay)
    I = m * 0.35 + ridge * 0.6 + np.exp(-r / 0.07) * 0.9
    edge = m * (1 - ss(1.0 - f + 0.06, 0.03, 0.09))
    return np.clip(np.maximum(I, edge * 0.12), 0, 1.2), edge


def rift(i, cell=256, seed=101):
    S = cell * SS
    x, y = grid_xy(S)
    open_ = seqv([0.35, 0.75, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], i)
    hm = seqv([0.6, 1, 1.1, 1.05, 1, 0.95, 0.88, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.22, 0.14, 0.07], i)
    W = S
    uu = np.linspace(-1, 1, W, dtype=np.float32)
    env = np.maximum(np.sin(np.pi * np.clip((uu / (0.92 * open_) + 1) / 2, 0, 1)), 0) ** 0.6 * hm
    top = spikes_profile(W, 26, seed, 0.04, 0.24, 8) * env
    bot = spikes_profile(W, 22, seed + 1, 0.03, 0.18, 8) * env
    cyl = (noise(1, W, 1, W * 0.25, seed + 2, 3)[0] - 0.5) * 0.18
    yy = y - cyl[None, :]
    up = top[None, :] + 0.05 * env[None, :]
    dn = bot[None, :] + 0.04 * env[None, :]
    m = ss(up - yy, 0, 0.012) * ss(yy + dn, 0, 0.012)
    edgeT = np.exp(-np.abs(yy - 0.02 * env[None, :]) / 0.008) * (env[None, :] > 0.05)
    I = m * 0.36 + edgeT * 0.8 * ss(m, 0, 0.5)
    return np.clip(I, 0, 1)


def shard_nova(i, cell=256, seed=111):
    S = cell * SS
    H, W = 400, 1600
    grow = seqv([0.35, 0.75, 1, 1.04, 1.04, 1.02, 1, 0.97, 0.92, 0.85, 0.76, 0.65, 0.52, 0.38, 0.25, 0.12], i)
    L = spikes_profile(W, 17, seed, 0.45, 0.95, 5) * grow
    vr = np.linspace(0, 1, H, dtype=np.float32)[:, None]             # row 0 = outer (r = 0.95)
    rr = 0.95 * (1 - vr)
    inside = ss(L[None, :] - rr, 0, 0.02) * ss(rr - 0.06, 0, 0.03)
    grad = np.clip(rr / np.maximum(L[None, :], 1e-3), 0, 1)
    dl = np.gradient(L)
    lit = np.exp(-np.abs(dl)[None, :] * 0) * ss(dl[None, :], 0, 1e-4)  # lit side of each shard
    I = inside * (0.36 + 0.1 * grad) + inside * lit * 0.55 * ss(grad, 0.2, 0.6)
    return polar(np.clip(I, 0, 1), S, 0.95, 0.0, 0.0, 2 * np.pi)


def shard_fan(i, cell=256, seed=121):
    S = cell * SS
    H, W = 420, 900
    grow = seqv([0.3, 0.7, 1, 1.05, 1.05, 1.03, 1, 0.96, 0.9, 0.82, 0.72, 0.6, 0.46, 0.32, 0.2, 0.1], i)
    base = seqv([0.5, 0.9, 1, 0.95, 0.88, 0.8, 0.7, 0.6, 0.5, 0.4, 0.32, 0.24, 0.16, 0.1, 0.05, 0], i)
    L = spikes_profile(W, 13, seed, 0.9, 1.75, 4, 0.6) * grow
    vr = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    rr = 1.8 * (1 - vr)
    inside = ss(L[None, :] - rr, 0, 0.03) * ss(rr - 0.04, 0, 0.02)
    dl = np.gradient(L)
    I = inside * 0.36 + inside * ss(dl[None, :], 0, 1e-4) * 0.5 * ss(rr / np.maximum(L[None, :], 1e-3), 0.1, 0.5)
    I += np.exp(-rr / (0.22 * base + 1e-3)) * base * 1.0                # bright jagged base burst
    out = polar(np.clip(I, 0, 1.2), S, 1.8, 0.0, (90 + 38) * D, 76 * D, cy=-0.9)
    return out


def blobs(i, cell=256, seed=83):
    S = cell * SS
    x, y = grid_xy(S)
    rng = np.random.default_rng(seed)
    I = np.zeros((S, S), np.float32)
    for k in range(8):
        cx, cy, R0 = rng.uniform(-0.5, 0.5), rng.uniform(-0.35, 0.35), rng.uniform(0.16, 0.34)
        b, dd = rng.uniform(0, 3), rng.uniform(9, 15)
        life = ss(i, b, b + 2.5) * (1 - ss(i, dd - 3, dd))
        R = R0 * (0.6 + 0.4 * life)
        if life < 0.02:
            continue
        r = np.hypot(x - cx, y - cy - i * 0.01) / R
        rim = np.exp(-np.abs(r - 0.93) / 0.05) * (r < 1.02)
        fill = ss(1.0 - r, 0, 0.04) * 0.32
        hi = np.exp(-np.hypot(x - cx + R * 0.35, y - cy - i * 0.01 - R * 0.38) / (R * 0.1)) * 0.9
        I = np.maximum(I, (fill + rim * 0.75 + hi) * life)
    return np.clip(I, 0, 1)


def fire_burst(i, cell=256, seed=7):
    S = cell * SS
    H, W = 400, 1400
    f = i / 15
    R = 0.25 + 0.6 * (1 - (1 - min(1, f * 4)) ** 2)
    er = max(0, (f - 0.35) / 0.65)
    vr = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    rr = 0.95 * (1 - vr)
    spk = spikes_profile(W, 21, seed + i % 3, 0.6, 1.0, 3, 0.8)
    n = noise(H, W, H * 0.12, W * 0.04, seed + i, 4)
    heat = 1 - rr / (R * (0.55 + 0.55 * spk[None, :])) + (n - 0.5) * 0.5 - er * (0.5 + n)
    heat = mblur(heat, 8, axis=0)                                       # radial smear
    I = np.clip(heat * 1.4, 0, 1.2)
    return polar(I, S, 0.95, 0.0, 0.0, 2 * np.pi)


def ink_spikes(i, cell=512, seed=71):
    S = cell * SS
    H, W = 400, 1800
    g = [0.65, 1, 1, 0.9][i]
    th = [1, 1, 0.65, 0.35][i]
    L = spikes_profile(W, 34, seed, 0.4, 0.95, 9, 0.5) * g
    vr = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    rr = 0.95 * (1 - vr)
    m = ss(L[None, :] * th ** 0.3 - rr, 0, 0.015) * ss(rr - 0.12 - (1 - th) * 0.3, 0, 0.02)
    ring = np.exp(-np.abs(rr - 0.17) / 0.012) * levels(noise(H, W, H, W * 0.1, seed, 3), 0.4, 0.7) * th
    return polar(np.clip(np.maximum(m, ring), 0, 1), S, 0.95, 0.0, 0.0, 2 * np.pi)


def glint(i, cell=256):
    S = cell * SS
    x, y = grid_xy(S)
    s = [0.45, 1, 0.7, 0.35][i]
    ax, ay = np.abs(x) / s, np.abs(y) / s
    ray = lambda a, b, w: np.exp(-b / w) * np.clip(1 - a, 0, 1) ** 1.5
    I = ray(ax, ay, 0.02) + ray(ay, ax, 0.02)
    xd, yd = np.abs(x + y) / 1.414 / s, np.abs(x - y) / 1.414 / s
    I += 0.5 * (ray(xd * 2.6, yd, 0.015) + ray(yd * 2.6, xd, 0.015))
    r = np.hypot(x, y) / s
    I += np.exp(-r / 0.05) + 0.35 * np.exp(-r / 0.2)
    return np.clip(I, 0, 1)


def sparkle(i, cell=64):
    return glint([1, 3, 2, 0][i], cell * 2)[:: 2, :: 2] if False else glint([1, 3, 2, 0][i], cell)


def flare(i, cell=512, seed=91):
    S = cell * SS
    x, y = grid_xy(S)
    r = np.hypot(x, y)
    a = np.arctan2(y, x)
    rays = noise(1, 2048, 1, 6, seed, 2)[0]
    idx = ((a + np.pi) / (2 * np.pi) * 2047).astype(int)
    rv = levels(rays[idx], 0.45, 1.0, 2.0)
    I = np.exp(-r / 0.05) + 0.6 * np.exp(-r / 0.16) + rv * np.exp(-r / 0.35) * 0.7
    I += np.exp(-np.abs(y) / 0.008) * np.clip(1 - np.abs(x), 0, 1) ** 2 * 0.8
    return np.clip(I, 0, 1)


def line(i, cell=1024):
    S = cell * SS
    x, y = grid_xy(S)
    w = 0.006 * np.clip(1 - np.abs(y) / 0.95, 0, 1) ** 0.4 + 1e-4
    return np.clip(np.exp(-(x / w) ** 2) + 0.25 * np.exp(-np.abs(x) / (w * 5)) * (np.abs(y) < 0.95), 0, 1)


def spark(i, cell=256):
    S = cell * SS
    x, y = grid_xy(S)
    w = 0.05 * np.clip(1 - np.abs(y - 0.25) / 0.7, 0, 1) ** 0.8 + 1e-4
    return np.clip(np.exp(-(x / w) ** 2) * (np.abs(y) < 0.95) + 0.3 * np.exp(-np.hypot(x, (y - 0.3) * 0.5) / 0.08), 0, 1)


def thin_ring(i, cell=512):
    S = cell * SS
    x, y = grid_xy(S)
    r, a = np.hypot(x, y), np.arctan2(y, x)
    seg = np.exp(-(((a - i * 1.3 + np.pi) % (2 * np.pi) - np.pi) / 0.8) ** 2)
    return np.clip(np.exp(-np.abs(r - 0.86) / (0.004 + 0.008 * seg)) * (0.5 + 0.5 * seg), 0, 1)


def mist(i, cell=256, seed=3):
    S = cell * SS
    x, y = grid_xy(S)
    f = i / 15
    sc = 0.85 + f * 0.25
    d = np.hypot(x / sc, (y + 0.05 - f * 0.1) / (sc * 0.8))
    n = noise(S, S, S * 0.3, S * 0.3, seed + i // 4, 5)
    n2 = noise(S, S, S * 0.08, S * 0.12, seed + 9, 4)
    dens = (1 - d) * 1.2 + (n - 0.5) * 1.6 + (n2 - 0.5) * 0.7 - f * 0.85
    return np.clip(ss(dens, -0.05, 0.6) * 0.8, 0, 1)


def dust(i, cell=256, seed=29):
    S = cell * SS
    x, y = grid_xy(S)
    f = i / 15
    sc = 0.8 + f * 0.25
    d = np.hypot(x / sc, (y + 0.1) / (sc * 0.72))
    n = noise(S, S, S * 0.25, S * 0.25, seed, 5)
    dens = (1 - d) * 1.5 + (n - 0.5) * 1.2 - f * 1.0
    return np.clip(ss(dens, 0.0, 0.3) * 0.9, 0, 1), np.clip(0.62 + y * 0.35 + (n - 0.5) * 0.5, 0.3, 1)


def bokeh(i, cell=128):
    S = cell * SS
    x, y = grid_xy(S)
    r = np.hypot(x, y)
    return np.clip(np.maximum(ss(0.3 - r, 0, 0.18), np.clip(1 - r / 0.92, 0, 1) ** 2.4 * 0.7), 0, 1)

# ================================================================ registry
PAL = {
    'blue': {'glow': '#2f5bff', 'rim': '#14208a', 'mid': '#6f8cff', 'core': '#ffffff', 'bg': (0.05, 0.08, 0.19)},
    'navy': {'glow': '#2f5bff', 'rim': '#e8eeff', 'mid': '#0c1660', 'core': '#ffffff', 'bg': (0.05, 0.08, 0.19)},
    'wind': {'glow': '#a0b0c0', 'rim': '#3a4250', 'mid': '#b8c2cc', 'core': '#ffffff', 'bg': (0.24, 0.27, 0.33)},
    'dark': {'glow': '#8090a0', 'rim': '#08080c', 'mid': '#4a505c', 'core': '#ffffff', 'bg': (0.24, 0.27, 0.33)},
    'fire': {'glow': '#ff6a10', 'rim': '#c02008', 'mid': '#ff9a20', 'core': '#fff6d0', 'bg': (0.12, 0.12, 0.16)},
}
E = (0.02, 0.12, 0.14, 0.42, 0.55, 0.9)        # thresholds for painted energy
B = (0.02, 0.08, 0.2, 0.3, 0.6, 0.85)          # thresholds for body-at-0.36 graphics (rim fringe, flat mid, bright core)
RECIPES = {
    'wisp_arc': dict(kind='layered', grid=4, fn=energy_arc, glow=10, th=E, pal='blue'),
    'trail_arc': dict(kind='layered', grid=4, fn=wind_arc, glow=8, th=E, pal='wind'),
    'energy_swirl': dict(kind='layered', grid=4, fn=energy_swirl, glow=10, th=(0.03, 0.15, 0.18, 0.5, 0.6, 0.95), pal='blue'),
    'swirl_disk': dict(kind='layered', grid=4, fn=ground_swirl, glow=8, th=(0.03, 0.15, 0.18, 0.5, 0.6, 0.95), pal='blue'),
    'ring_slash': dict(kind='layered', grid=4, fn=ring_slash, glow=8, th=(0.03, 0.15, 0.18, 0.5, 0.62, 0.95), pal='dark'),
    'saw_fan': dict(kind='layered', grid=4, fn=saw_blade, glow=6, th=B, pal='navy'),
    'rift': dict(kind='layered', grid=4, fn=rift, glow=6, th=B, pal='navy'),
    'shard_nova': dict(kind='layered', grid=4, fn=shard_nova, glow=6, th=B, pal='navy'),
    'shard_fan': dict(kind='layered', grid=4, fn=shard_fan, glow=8, th=B, pal='navy'),
    'blobs': dict(kind='layered', grid=4, fn=blobs, glow=8, th=(0.02, 0.1, 0.2, 0.3, 0.55, 0.85), pal='navy'),
    'fire_burst': dict(kind='layered', grid=4, fn=fire_burst, glow=14, th=(0.02, 0.12, 0.15, 0.4, 0.6, 0.95), pal='fire'),
    'star4': dict(kind='layered', grid=2, fn=star4, glow=12, th=B, pal='navy'),
    'ink_arc': dict(kind='single', grid=4, fn=ink_arc),
    'ink_spikes': dict(kind='single', grid=2, fn=ink_spikes),
    'glint': dict(kind='single', grid=2, fn=glint, cell=256),
    'sparkle': dict(kind='single', grid=2, fn=sparkle, cell=64),
    'flare': dict(kind='single', grid=1, fn=flare, cell=512),
    'line': dict(kind='single', grid=1, fn=line, cell=1024),
    'spark': dict(kind='single', grid=1, fn=spark, cell=256),
    'thin_ring': dict(kind='single', grid=2, fn=thin_ring),
    'mist': dict(kind='single', grid=4, fn=mist),
    'dust': dict(kind='single', grid=4, fn=dust),
    'bokeh': dict(kind='single', grid=1, fn=bokeh, cell=128),
}


def build(name):
    R = RECIPES[name]
    g, cell = R['grid'], R.get('cell', 1024 // R['grid'])
    raw = [R['fn'](i, cell=cell) for i in range(g * g)]
    frames = [r[0] if isinstance(r, tuple) else r for r in raw]
    values = [r[1] for r in raw] if isinstance(raw[0], tuple) else None
    os.makedirs(OUT, exist_ok=True)
    if R['kind'] == 'layered':
        per = [split(f, R['glow'] * SS, R['th']) for f in frames]
        layers = {k: sheet([p[k] for p in per], g, cell) for k in ('glow', 'rim', 'mid', 'core')}
        for k, a in layers.items():
            save_white(a, os.path.join(OUT, f'{name}_{k}.png'))
        pal = PAL[R.get('pal', 'blue')]
        preview(layers, pal, pal['bg'], os.path.join(OUT, f'_preview_{name}.png'))
    else:
        a = sheet(frames, g, cell)
        val = sheet(values, g, cell) if values is not None else None
        save_white(a, os.path.join(OUT, f'{name}.png'), val)
        bg = np.ones(a.shape + (3,), np.float32) * np.array([0.55, 0.62, 0.8], np.float32)
        from PIL import Image
        Image.fromarray(np.clip(bg * (1 - a[..., None]) * 255, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f'_preview_{name}.png'))
    print(name, 'ok')


if __name__ == '__main__':
    for n in (sys.argv[1:] or RECIPES):
        build(n)
