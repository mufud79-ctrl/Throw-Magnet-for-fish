"""Headless photo-craft for Roblox VFX sprite sheets.

Pro VFX textures are painted, not drawn as vectors. This module reproduces the image-editor
workflow with numpy/scipy, so every texture is smooth and painterly with no brush stamps:

  * paint a straight STRIP (u = along the stroke, v = across it) from smooth gradients,
    pressure-tapered masks and anisotropic streak noise
  * motion-blur along the stroke (smudge), levels/curves for crisp-but-soft edges
  * bend the strip with a POLAR COORDINATES warp into a crescent (the classic slash workflow)
  * supersample 2x and downsample with Lanczos

Every painted result is an intensity image I (0..1). It is split into four WHITE layers with
soft thresholds, so stacked emitters give smooth white -> colour -> dark gradients in Roblox:
  core = hottest values, mid = body, rim = outer fringe, glow = blurred I.
"""
import numpy as np
from scipy import ndimage as ndi
from PIL import Image

SS = 2  # supersampling factor


# ---------------------------------------------------------------- basics
def ss(x, a, b):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def noise(h, w, sy, sx, seed, octaves=4, persist=0.55):
    """Smooth value noise, anisotropic: feature size sy (rows) x sx (cols) in pixels."""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gh = max(2, int(np.ceil(h / (sy / 2 ** o))) + 2)
        gw = max(2, int(np.ceil(w / (sx / 2 ** o))) + 2)
        g = rng.random((gh, gw)).astype(np.float32)
        up = ndi.zoom(g, ((h + 1) / (gh - 1), (w + 1) / (gw - 1)), order=3, mode='wrap')[:h, :w]
        out += up * amp
        tot += amp
        amp *= persist
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def levels(x, lo, hi, gamma=1.0):
    return np.clip((x - lo) / (hi - lo), 0, 1) ** gamma


def blur(x, s):
    return ndi.gaussian_filter(x, s) if s > 0 else x


def mblur(x, s, axis=1):
    """motion blur along an axis (smudge along the stroke)."""
    return ndi.gaussian_filter1d(x, s, axis=axis, mode='nearest')


# ---------------------------------------------------------------- polar warp
def polar(strip, size, r_out, r_in, a0, sweep, cx=0.0, cy=0.0, vtop=0.0, spiral=0.0):
    """Bend a strip (rows = v from outer edge to inner edge, cols = u along the arc) into a
    crescent. Cell coords: x,y in [-1,1], y up. Angle runs a0 -> a0 - sweep (clockwise)."""
    H, W = strip.shape
    ys, xs = np.mgrid[0:size, 0:size].astype(np.float32)
    x = (xs + 0.5) / size * 2 - 1 - cx
    y = 1 - (ys + 0.5) / size * 2 - cy
    r = np.hypot(x, y)
    a = np.arctan2(y, x)
    u = ((a0 - a) % (2 * np.pi)) / sweep
    v = (r_out - spiral * u - r) / (r_out - r_in)          # strip row 0 sits at v = vtop (<0 = outside r_out)
    valid = (u >= 0) & (u <= 1) & (v >= vtop) & (v <= 1)
    cu = np.clip(u, 0, 1) * (W - 1)
    cv = np.clip((v - vtop) / (1 - vtop), 0, 1) * (H - 1)
    out = ndi.map_coordinates(strip, [cv, cu], order=1, mode='nearest')
    out[~valid] = 0
    return out


# ---------------------------------------------------------------- layer split + sheets
def split(I, glow_sigma, th):
    """I -> dict of white-layer alphas. th = (rim_lo, rim_hi, mid_lo, mid_hi, core_lo, core_hi)."""
    rl, rh, ml, mh, cl, ch = th
    return {
        'glow': np.clip(blur(I, glow_sigma) * 1.6, 0, 1),
        'rim': ss(I, rl, rh),
        'mid': ss(I, ml, mh),
        'core': ss(I, cl, ch),
    }


def edge_fade(cell):
    n = cell
    t = np.linspace(-1, 1, n)
    e = np.maximum(np.abs(t)[None, :], np.abs(t)[:, None])
    return ss(0.97 - e, 0, 0.05)


def sheet(frames, grid, cell_out, fade=True):
    """frames: list of 2D float arrays (supersampled cells) -> 2D sheet at output resolution."""
    S = cell_out * grid
    out = np.zeros((S, S), np.float32)
    for i, f in enumerate(frames):
        img = Image.fromarray(np.clip(f * 255, 0, 255).astype(np.uint8), 'L')
        img = img.resize((cell_out, cell_out), Image.LANCZOS)
        a = np.asarray(img, np.float32) / 255 * (edge_fade(cell_out) if fade else 1)
        r, c = divmod(i, grid)
        out[r * cell_out:(r + 1) * cell_out, c * cell_out:(c + 1) * cell_out] = a
    return out


def save_white(alpha, path, value=None):
    a = np.clip(alpha * 255, 0, 255).astype(np.uint8)
    v = np.full_like(a, 255) if value is None else np.clip(value * 255, 0, 255).astype(np.uint8)
    Image.fromarray(np.dstack([v, v, v, a]), 'RGBA').save(path, optimize=True)


def preview(layers, pal, bg, path):
    """Tinted composite of the 4 layers (glow additive, rim/mid over, core additive)."""
    H, W = layers['mid'].shape
    out = np.ones((H, W, 3), np.float32) * np.array(bg, np.float32)
    def hexc(h):
        return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)
    out += layers['glow'][..., None] * hexc(pal['glow']) * 0.8
    for k in ('rim', 'mid'):
        a = layers[k][..., None]
        out = out * (1 - a) + hexc(pal[k]) * a
    out += layers['core'][..., None] * hexc(pal['core'])
    Image.fromarray(np.clip(out * 255, 0, 255).astype(np.uint8)).save(path)


def tnoise(h, w, sy, sx, seed, octaves=4, persist=0.55):
    """Seamlessly TILEABLE noise (periodic in both axes) via FFT-filtered white noise.
    sy, sx = feature size in pixels along rows / cols (anisotropic streaks: sy small, sx large)."""
    rng = np.random.default_rng(seed)
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        wn = rng.standard_normal((h, w))
        ay, ax = sy / 2 ** o / 3.0, sx / 2 ** o / 3.0
        g = np.exp(-2 * np.pi ** 2 * ((fy * ay) ** 2 + (fx * ax) ** 2))
        n = np.real(np.fft.ifft2(np.fft.fft2(wn) * g)).astype(np.float32)
        n = (n - n.mean()) / (n.std() + 1e-6)
        out += n * amp
        tot += amp
        amp *= persist
    out /= tot
    return np.clip(out * 0.22 + 0.5, 0, 1)
