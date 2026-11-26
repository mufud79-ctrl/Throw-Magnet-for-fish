"""Helpers for the dragon's base animations (idle / movement / M1), played by the rig layer v2.

Bone axes on assets/models/dragon.glb (checked with axis_test.json):
  spine_NN  local Z = yaw (side to side), local X = pitch (+X bends everything behind the bone DOWN), Y = twist.
            The chain runs head (spine_00) -> tail (spine_19), so a spine bone moves the body BEHIND it.
  orient    model root, Euler YXZ deg: +X pitches the head up, +Y turns left.
  jaw       `jaw` keys in degrees, + opens (rest pose is closed).
"""
import json
import math
import os

NB = 20
MODEL = "dragon"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))


def wave(period, amp, phase=0.0, n=24, base=(0, 0, 0)):
    """One looping sine cycle as rot keys: base + amp * sin(2pi t/period - phase), per axis amp (x, y, z)."""
    keys = []
    for i in range(n + 1):
        t = period * i / n
        s = math.sin(2 * math.pi * t / period - phase)
        keys.append([round(t, 4), [round(base[j] + amp[j] * s, 3) for j in range(3)]])
    return {"rot": keys, "loop": period}


def merge(*tracks):
    """Sum several same-length looping waves (same period and sample times) into one track."""
    out = {"rot": [], "loop": tracks[0]["loop"]}
    for ks in zip(*[t["rot"] for t in tracks]):
        out["rot"].append([ks[0][0], [round(sum(k[1][j] for k in ks), 3) for j in range(3)]])
    return out


def body_wave(period, yaw=6.0, pitch=2.0, waves=1.2, start=2, grow=0.4, yaw_base=None, pitch_waves=2.0):
    """A travelling wave down the spine: each bone a phase step behind the one before (the body ripples tailward)."""
    tr = {}
    for i in range(start, NB):
        f = (i - start) / (NB - 1 - start)
        a = 1 + grow * f
        ph = 2 * math.pi * waves * f
        base = (0, 0, yaw_base(f) if yaw_base else 0)
        php = 2 * math.pi * pitch_waves * f            # pitch ripples at a shorter wavelength so it cancels instead of
        tr[f"spine_{i:02d}"] = merge(wave(period, (0, 0, yaw * a), ph, base=base), wave(period, (pitch * a, 0, 0), php + 1.3))  # lifting the whole tail
    return tr


def keys(*pairs):
    """Hand-keyed track: keys((t, (x, y, z)), (t, (x, y, z), "out"), ...)."""
    out = []
    for p in pairs:
        k = [p[0], list(p[1])]
        if len(p) > 2:
            k.append(p[2])
        out.append(k)
    return {"rot": out}


def write(fx, name):
    fx.setdefault("caster", False)
    fx.setdefault("bloom", 0.35)
    path = os.path.join(OUT, f"{name}.json")
    json.dump(fx, open(path, "w"), indent=1)
    return path


def spline(keys, dt=1 / 60):
    """Time-keyed smooth path for path-follow rigs. keys: [(t, (x, y, z)), (t, (x, y, z), k), ...] where k scales the
    velocity through that key (1 = Catmull-Rom, 0 = a dead stop / hang, >1 = whips through). Returns path keys."""
    T = [k[0] for k in keys]
    P = [list(k[1]) for k in keys]
    K = [k[2] if len(k) > 2 else 1.0 for k in keys]
    n = len(keys)
    M = []
    for i in range(n):
        a, b = max(0, i - 1), min(n - 1, i + 1)
        M.append([(P[b][j] - P[a][j]) / ((T[b] - T[a]) or 1) * K[i] for j in range(3)])
    out = []
    t = T[0]
    while t <= T[-1] + 1e-9:
        i = max(0, min(n - 2, next((j for j in range(n - 1) if T[j + 1] >= t), n - 2)))
        h = T[i + 1] - T[i]
        u = (t - T[i]) / h
        h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
        out.append([round(t, 4), [round(h00 * P[i][j] + h10 * h * M[i][j] + h01 * P[i + 1][j] + h11 * h * M[i + 1][j], 3) for j in range(3)]])
        t += dt
    return out


def ripple(period, amp=4.0, waves=1.5, start=3, grow=0.6, axis=2):
    """Secondary travelling ripple for path-follow rigs (added on top of the path pose): small per bone, it builds
    toward the tail like a whip."""
    tr = {}
    for i in range(start, NB):
        f = (i - start) / (NB - 1 - start)
        am = [0, 0, 0]
        am[axis] = amp * (1 + grow * f)
        tr[f"spine_{i:02d}"] = wave(period, tuple(am), 2 * math.pi * waves * f)
    return tr
