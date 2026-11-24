"""photocraft: headless 'image editor' for painted anime VFX textures.

Pro Roblox VFX textures are painted in Photoshop/Krita, not drawn as vectors. This module reproduces that
workflow on float images with numpy + scipy, so results read as hand-painted (soft-but-defined edges,
internal light and shadow, smudged energy streaks), without fake brush-stroke stamps:

  * forms      : metaball lobes, domain-warped fractal noise (organic, flowing silhouettes)
  * volume     : heightfield lighting (normal from gradient, key light + rim light) = painted shading
  * edges      : levels/curves on a soft field -> crisp edge with a 1-2 px painted falloff
  * smudge     : directional (motion) blur along a stroke or radially from a centre
  * strokes    : paint a straight strip (u = along, v = across) then bend it with a polar warp
  * layers     : split an intensity image into WHITE layers (glow / rim / mid / core). Stacked emitters
                 with different Colors rebuild a smooth white -> colour -> dark gradient in Roblox.

All painting happens at SS x resolution and is downsampled with Lanczos at the end.
Coordinates: x, y in [-1, 1], y up.
"""
import os
import numpy as np
from scipy import ndimage as ndi
from PIL import Image

SS = 2


# ---------------------------------------------------------------- basic maths
def ss(x, a, b):
    """smoothstep from a to b (a > b allowed for a falling edge)."""
    t = np.clip((x - a) / (b - a + 1e-12), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def levels(x, lo, hi, gamma=1.0):
    return np.clip((x - lo) / (hi - lo + 1e-12), 0, 1) ** gamma


def blur(x, s):
    return ndi.gaussian_filter(x, s, mode="constant") if s > 0 else x


def mblur(x, s, axis=1):
    """Smudge along one axis (motion blur)."""
    return ndi.gaussian_filter1d(x, s, axis=axis, mode="nearest") if s > 0 else x


def coords(n, m=None, cx=0.0, cy=0.0):
    m = m or n
    ys, xs = np.mgrid[0:m, 0:n].astype(np.float32)
    x = (xs + 0.5) / n * 2 - 1 - cx
    y = 1 - (ys + 0.5) / m * 2 - cy
    return x, y


def polar_of(x, y):
    return np.hypot(x, y), np.arctan2(y, x)


# ---------------------------------------------------------------- noise
def noise(h, w, sy, sx, seed, octaves=4, persist=0.55):
    """Smooth value noise in [0,1]; feature size sy (rows) x sx (cols) in pixels (anisotropic allowed)."""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gh = max(3, int(np.ceil(h / max(1.0, sy / 2 ** o))) + 3)
        gw = max(3, int(np.ceil(w / max(1.0, sx / 2 ** o))) + 3)
        g = rng.random((gh, gw)).astype(np.float32)
        up = ndi.zoom(g, ((h + 2) / (gh - 1), (w + 2) / (gw - 1)), order=3, mode="reflect")[:h, :w]
        out += up * amp
        tot += amp
        amp *= persist
    out /= tot
    lo, hi = np.percentile(out, 1), np.percentile(out, 99)
    return np.clip((out - lo) / (hi - lo + 1e-6), 0, 1)


def tnoise(h, w, sy, sx, seed, octaves=4, persist=0.55):
    """Seamlessly tileable noise (periodic both axes) from FFT-filtered white noise, in [0,1]."""
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
        out += (n - n.mean()) / (n.std() + 1e-6) * amp
        tot += amp
        amp *= persist
    out /= tot
    return np.clip(out * 0.22 + 0.5, 0, 1)


def sample(img, x, y):
    """Bilinear sample a 2D array at normalised coords x, y in [-1,1] (y up)."""
    h, w = img.shape
    cols = (x + 1) / 2 * w - 0.5
    rows = (1 - y) / 2 * h - 0.5
    return ndi.map_coordinates(img, [rows, cols], order=1, mode="reflect")


def warp(img, dx, dy):
    """Displace an image by per-pixel offsets (pixels)."""
    h, w = img.shape
    rr, cc = np.mgrid[0:h, 0:w].astype(np.float32)
    return ndi.map_coordinates(img, [rr - dy, cc - dx], order=1, mode="constant")


# ---------------------------------------------------------------- forms
def lobes(x, y, centres, falloff=2.0):
    """Soft metaball field: sum of (1 - d/r)^falloff over circles (cx, cy, r). Returns >= 0."""
    f = np.zeros_like(x)
    for cx, cy, r in centres:
        d = np.hypot(x - cx, y - cy) / r
        f += np.clip(1 - d, 0, 1) ** falloff
    return f


def shade(height, light=(-0.55, 0.75, 0.55), rim=0.0, strength=6.0):
    """Painted volume: lambert of the heightfield normal against a key light, plus an optional
    rim term on edges facing away. Returns 0..1."""
    gy, gx = np.gradient(height)
    nx, ny, nz = -gx * strength, gy * strength, np.ones_like(height)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    L = np.array(light, np.float32)
    L = L / np.linalg.norm(L)
    lam = (nx * L[0] + ny * L[1] + nz * L[2]) / ln
    out = np.clip(lam, 0, 1)
    if rim:
        out = np.clip(out + rim * (1 - nz / ln) ** 2, 0, 1)
    return out


def soft_posterize(v, steps, softness=0.06):
    """Anime-painted tones: quantise to `steps` bands with soft transitions (not hard vector bands)."""
    q = v * (steps - 1)
    base = np.floor(q)
    frac = q - base
    return np.clip((base + ss(frac, 0.5 - softness * steps, 0.5 + softness * steps)) / (steps - 1), 0, 1)


def polar_strip(strip, size, r_out, r_in, a0, sweep, cx=0.0, cy=0.0, vtop=0.0, flare=0.0):
    """Bend a painted strip (rows = v from outer edge to inner edge, cols = u along the arc) into an
    arc. Angle runs a0 -> a0 - sweep (clockwise, radians). flare widens the band toward the head (u=0)."""
    H, W = strip.shape
    x, y = coords(size, cx=cx, cy=cy)
    r, a = polar_of(x, y)
    u = ((a0 - a) % (2 * np.pi)) / sweep
    width = (r_out - r_in) * (1 + flare * (1 - np.clip(u, 0, 1)))
    v = (r_out - r) / width
    valid = (u >= 0) & (u <= 1) & (v >= vtop) & (v <= 1)
    cu = np.clip(u, 0, 1) * (W - 1)
    cv = np.clip((v - vtop) / (1 - vtop), 0, 1) * (H - 1)
    out = ndi.map_coordinates(strip, [cv, cu], order=1, mode="nearest")
    out[~valid] = 0
    return out


def radial_smudge(img, cx_px, cy_px, amount=0.06, steps=12):
    """Zoom blur from a centre (energy flying outward). amount = fraction of radius."""
    h, w = img.shape
    rr, cc = np.mgrid[0:h, 0:w].astype(np.float32)
    acc = np.zeros_like(img)
    for k in range(steps):
        s = 1 - amount * k / steps
        acc += ndi.map_coordinates(img, [cy_px + (rr - cy_px) * s, cx_px + (cc - cx_px) * s], order=1, mode="constant")
    return acc / steps


def taper(u, head=0.08, tail=0.6, power=1.0):
    """Pressure curve along a stroke: rises over `head`, holds, falls over the last `tail`."""
    return (ss(u, 0, head) * ss(u, 1.0, 1.0 - tail)) ** power


# ---------------------------------------------------------------- layers + output
LAYER_TH = {
    # (lo, hi) soft thresholds on intensity for each white layer
    "rim": (0.06, 0.2),
    "mid": (0.34, 0.5),
    "core": (0.7, 0.86),
}


def split(I, glow_sigma=6.0, th=None, glow_gain=1.4):
    th = th or LAYER_TH
    out = {k: ss(I, lo, hi) for k, (lo, hi) in th.items()}
    out["glow"] = np.clip(blur(I, glow_sigma) * glow_gain, 0, 1)
    return out


def edge_fade(n, margin=0.03):
    t = np.linspace(-1, 1, n)
    e = np.maximum(np.abs(t)[None, :], np.abs(t)[:, None])
    return ss(e, 1.0 - margin * 0.5, 1.0 - margin * 2)


def down(a, size):
    """Lanczos downsample of a float image (32-bit float, no banding)."""
    img = Image.fromarray(np.ascontiguousarray(a, dtype=np.float32))
    return np.clip(np.asarray(img.resize((size, size), Image.LANCZOS), np.float32), 0, 1)


def down_rect(a, w, h):
    img = Image.fromarray(np.ascontiguousarray(a, dtype=np.float32))
    return np.clip(np.asarray(img.resize((w, h), Image.LANCZOS), np.float32), 0, 1)


def sheet(frames, grid, cell, fade=True):
    """frames: supersampled square cells -> one grid sheet at output resolution."""
    S = cell * grid
    out = np.zeros((S, S), np.float32)
    ef = edge_fade(cell) if fade else 1.0
    for i, f in enumerate(frames):
        r, c = divmod(i, grid)
        out[r * cell:(r + 1) * cell, c * cell:(c + 1) * cell] = down(f, cell) * ef
    return out


def save_white(alpha, path, value=None):
    """White (or greyscale `value`) RGB + alpha PNG. Roblox Color multiplies RGB."""
    a = np.clip(alpha * 255 + 0.5, 0, 255).astype(np.uint8)
    v = np.full_like(a, 255) if value is None else np.clip(value * 255 + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(np.dstack([v, v, v, a]), "RGBA").save(path, optimize=True)


def hexc(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)


def composite(layers, pal, bg, single_value=None):
    """Approximate Roblox stacking: glow additive (LightEmission 1), rim/mid alpha-over, core additive
    on top. `layers` may also be {'single': alpha} with optional greyscale value (shaded textures)."""
    H, W = next(iter(layers.values())).shape
    out = bg.copy() if isinstance(bg, np.ndarray) else np.ones((H, W, 3), np.float32) * hexc(bg)
    if "single" in layers:
        a = layers["single"][..., None]
        val = single_value[..., None] if single_value is not None else 1.0
        col = hexc(pal.get("mid", "#ffffff")) * val
        if pal.get("additive"):
            return np.clip(out + col * a, 0, 1)
        return np.clip(out * (1 - a) + col * a, 0, 1)
    if "glow" in layers:
        out = out + layers["glow"][..., None] * hexc(pal["glow"]) * pal.get("glow_k", 0.7)
    for k in ("rim", "mid"):
        if k in layers:
            a = layers[k][..., None]
            out = out * (1 - a) + hexc(pal[k]) * a
    if "core" in layers:
        out = out + layers["core"][..., None] * hexc(pal["core"])
    return np.clip(out, 0, 1)


def to_img(rgb):
    return Image.fromarray(np.clip(rgb * 255 + 0.5, 0, 255).astype(np.uint8), "RGB")


def ensure(path):
    os.makedirs(path, exist_ok=True)
    return path
