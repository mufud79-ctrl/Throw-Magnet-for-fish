"""Full-colour fire textures for MESH VFX (the rework: modern Roblox anime VFX are mesh-led - swirl / crescent / ring /
sphere meshes with painted, scrolling colour textures - with particles only as garnish).

Unlike the greyscale particle sheets, these carry their own colour ramp (dark red edge -> crimson -> orange -> yellow ->
pale core), banded like anime cel paint, with torn edges and flow streaks. Played on SpecialMesh shells (Textured,
alpha-blended), tinted white. UV conventions follow scripts/vfx_meshes.py:
  fx_fire_band   1024x256  u along (TILES in u), v across: v=0 outer torn edge ... v=1 inner edge   swirl / tube / ribbons
  fx_fire_slash  1024x256  u = head (0) -> tail (1), v = outer (0) -> inner (1)                    crescent meshes
  fx_fire_ring   1024x256  u around (TILES), v = outer leading edge (0) -> inner (1)               ring / disc meshes
  fx_fire_ball   512x512   u around (TILES), v pole -> pole                                        sphere / dome bursts
    /tmp/bpyenv/bin/python fire_mesh_textures.py
"""
import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photocraft import ss, tnoise, noise  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "textures")
# colour ramp (intensity -> colour), anime-banded
RAMP = [(0.00, "#5a0c08"), (0.18, "#9a1a0e"), (0.34, "#e0401a"), (0.52, "#ff8a14"), (0.70, "#ffc81e"), (0.86, "#ffe680"), (1.0, "#fff8d8")]


def hexc(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)


def colorize(I, bands=7, soft=0.03):
    """Intensity -> RGB through RAMP, posterized into soft bands (cel look, not a smooth airbrush)."""
    q = np.floor(np.clip(I, 0, 0.999) * bands) / bands
    fr = (np.clip(I, 0, 0.999) * bands) % 1.0
    q = q + ss(fr, 1 - soft * bands, 1.0) / bands
    out = np.zeros(I.shape + (3,), np.float32)
    xs = [p for p, _ in RAMP]
    cs = np.stack([hexc(c) for _, c in RAMP])
    for ch in range(3):
        out[..., ch] = np.interp(q, xs, cs[:, ch])
    return out


def save(rgb, a, name):
    img = np.dstack([np.clip(rgb, 0, 1), np.clip(a, 0, 1)])
    Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(OUT, name + ".png"), optimize=True)
    print("wrote", name)


def shear_rows(f, amt):
    H, W = f.shape
    return np.stack([np.roll(f[r], int(amt[r])) for r in range(H)])


def band(W=1024, H=256, seed=1, lean=0.08):
    """Shared flame band field: torn tongues on the outer edge leaning back along u, a fat body, a hot line inside."""
    u = (np.arange(W) + 0.5) / W
    v = (np.arange(H) + 0.5) / H
    U, V = np.meshgrid(u, v)
    tong = tnoise(H, W, 30, 70, seed, 3)
    tong = shear_rows(tong, (1 - v) * W * lean)
    streak = tnoise(H, W, 10, 200, seed + 1, 3)
    det = tnoise(H, W, 24, 40, seed + 2, 4)
    body = ss(V, 0.18, 0.42) * ss(V, 1.0, 0.82)                       # the fat body, soft inner fade
    edge = (tong - 0.42) * 1.6 * ss(V, 0.05, 0.35) * ss(V, 0.5, 0.3)  # tongues tear off the outer side
    F = body + edge + (det - 0.5) * 0.25
    alpha = ss(F, 0.18, 0.3)
    heat = np.clip(F, 0, 1) * (0.65 + 0.5 * ss(V, 0.3, 0.7)) * (0.85 + 0.3 * (streak - 0.5))
    heat = heat + 0.3 * ss(np.abs(V - 0.66 - (streak - 0.5) * 0.06), 0.05, 0.015)   # hot core line
    return U, V, F, alpha, heat


def fx_fire_band():
    U, V, F, a, heat = band(seed=11)
    save(colorize(np.clip(heat, 0, 1)), a, "fx_fire_band")


def fx_fire_slash():
    W, H = 1024, 256
    U, V, F, a, heat = band(W, H, seed=21, lean=0.12)
    dis = noise(H, W, 30, 80, 23, 4)
    head = ss(U, 0.0, 0.04)                                           # pointed head
    tail = ss(U + (dis - 0.5) * 0.25, 1.0, 0.55)                       # torn, eroding tail
    width = 1 - 0.55 * U                                               # thins toward the tail
    Vw = V / np.maximum(width, 0.3)
    a = a * head * tail * ss(Vw, 1.15, 0.95)
    heat = heat * (1.15 - 0.75 * U) + 0.35 * ss(U, 0.18, 0.0) * ss(V, 0.25, 0.6)   # hottest at the head
    save(colorize(np.clip(heat, 0, 1)), a, "fx_fire_slash")


def fx_fire_ring():
    W, H = 1024, 256
    u = (np.arange(W) + 0.5) / W
    v = (np.arange(H) + 0.5) / H
    U, V = np.meshgrid(u, v)
    tong = tnoise(H, W, 26, 50, 31, 3)
    det = tnoise(H, W, 20, 30, 32, 4)
    brk = tnoise(16, W, 16, 160, 33, 2).mean(0)
    lead = ss(V, 0.02, 0.12) * ss(V, 0.75, 0.3)                       # leading (outer) edge band trailing inward
    F = lead + (tong - 0.45) * 1.2 * ss(V, 0.25, 0.0) + (det - 0.5) * 0.25
    brk = (brk - brk.min()) / (np.ptp(brk) + 1e-6)
    F = F * (0.75 + 0.4 * brk[None, :])
    a = ss(F, 0.2, 0.32)
    heat = np.clip(F, 0, 1) * (1.1 - 0.8 * V) + 0.3 * ss(np.abs(V - 0.12), 0.05, 0.01)
    save(colorize(np.clip(heat, 0, 1)), a, "fx_fire_ring")


def fx_fire_ball():
    W = H = 512
    u = (np.arange(W) + 0.5) / W
    v = (np.arange(H) + 0.5) / H
    U, V = np.meshgrid(u, v)
    lobes = tnoise(H, W, 60, 70, 41, 4)
    det = tnoise(H, W, 18, 22, 42, 4)
    pole = np.sin(np.pi * V)                                          # bright band round the middle, torn toward the poles
    F = pole * 0.9 + (lobes - 0.5) * 0.9 + (det - 0.5) * 0.3
    a = ss(F, 0.15, 0.3)
    heat = np.clip(F, 0, 1) * (0.7 + 0.5 * lobes)
    save(colorize(np.clip(heat, 0, 1)), a, "fx_fire_ball")


if __name__ == "__main__":
    fx_fire_band(); fx_fire_slash(); fx_fire_ring(); fx_fire_ball()
