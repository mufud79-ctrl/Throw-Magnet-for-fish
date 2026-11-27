"""Firestorm Coil (full C) - a coiling twister that ignites. Signature: the dragon coils round the zone and spins up a
pale WIND twister first (sand-white bands, dust pulled in), then breathes into it and the twister IGNITES FROM THE
BOTTOM UP into a banded fire tornado that bursts outward.

Beat sheet
  0.00-0.40  the dragon swoops in and starts circling the zone low                         (anticipation)
  0.40-1.20  WIND: stacked spinning bands of pale wind rise into a funnel (wider at the top), sand haze and dust are
             pulled in at the base, needles of wind streak round it; targets are dragged in
  1.20       the dragon breathes into the base: glint, a burst of flame spikes at the foot
  1.20-1.60  IGNITION climbs the funnel band by band (bottom -> top); the wind bands turn to fire bands with a white
             core; flame spikes erupt round the base; targets lifted (ticks, hit-stop 0.04)
  1.60-2.40  the fire tornado pumps on each coil pass (spike bursts at the foot), smooth dark smoke off the top,
             embers spiralling
  2.40       BURST: hit-stop 0.10; a radial star of flame spikes, speed lines, ink, needles, a scorched ring, warm
             haze rolling far out; targets flung
  2.40-3.00  embers fall, smoke drifts, the dragon swims out
Camera: wide and low, looking up the column.
Run: python3 lab/dragon/moves/firestorm_coil.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

TW, TI, TB = 0.40, 1.20, 2.40
DUR = 3.0
C = [0, 0, -10]
TARGETS = [[-3.5, 0, -8.5], [3.2, 0, -11.5], [0.4, 0, -14.0]]
CAM = {"pos": [[0, [22, 6, 14]], [1, [22, 6, 14]]], "look": [[0, [0, 9.5, -10]], [1, [0, 9.5, -10]]], "fov": [[0, 68], [1, 68]]}
LEVELS = 9          # stacked bands
TOP = 17.0


def band_r(h):
    return 2.2 + 5.2 * (h / TOP) ** 1.3


def band_path(h, t0, t1, ph, w=11.0, step=1 / 90):
    n = max(2, int((t1 - t0) / step))
    out = []
    for k in range(n + 1):
        t = t0 + (t1 - t0) * k / n
        a = ph + w * t
        r = band_r(h) * (1 + 0.06 * math.sin(t * 7 + h))
        out.append([R(t, 4), R([C[0] + math.cos(a) * r, h + 0.4 * math.sin(t * 5 + ph), C[2] + math.sin(a) * r])])
    return out


def head_path():
    P = []
    t0, t1 = -1.6, DUR + 0.4
    n = int((t1 - t0) * 60)
    for k in range(n + 1):
        t = t0 + (t1 - t0) * k / n
        if t < 0:                                   # swoop in from the left
            u = (t + 1.6) / 1.6
            P.append([R(t, 4), R([-26 + 16 * u, 5 + 2 * u, -2 - 6 * u + 4 * math.sin(u * 3)])])
            continue
        if t <= TB:
            u = t / TB
            a = math.pi + 2.2 * 2 * math.pi * u ** 0.92
            r = 11 - 2.5 * u
            y = 7 + 12 * u ** 1.1
        else:                                       # burst: swings out wide and up
            u = (t - TB) / (DUR + 0.4 - TB)
            a = math.pi + 2.2 * 2 * math.pi + 1.2 * u
            r = 8.5 + 10 * u
            y = 19 + 3 * u
        P.append([R(t, 4), R([C[0] + math.cos(a) * r, y, C[2] + math.sin(a) * r])])
    # the swoop must join the circle smoothly: blend the first circle point
    return P


def build():
    hp = head_path()
    L = [ambience(C, 0, DUR, radius=16, rate=10, seed=1401)]

    # ---- WIND twister: stacked spinning pale bands, a funnel (wider at the top)
    for lv in range(LEVELS):
        h = 0.8 + lv * (TOP - 0.8) / (LEVELS - 1)
        t_on = TW + 0.05 * lv
        t_ig = TI + 0.045 * lv                       # ignition climbs bottom -> top
        for ph in (0.0, math.pi):
            bp = band_path(h, t_on, TB + 0.02, ph + lv * 0.7)
            L.append({"type": "trail", "path": bp, "at": bp[0][1], "t0": t_on, "t1": t_ig + 0.05, "lifetime": 0.26, "faceCamera": True,
                      "width": 1.5 + 0.12 * lv, "textures": [f"{s}_rim" for s in STRIPS], "swap": 0.06, "textureMode": "Stretch",
                      "color": [[0, "#fff4e0"], [1, "#d9c49a"]], "lightEmission": 0.15, "brightness": 1.1,
                      "transparency": [[0, 0.35], [0.5, 0.55], [1, 1]], "widthScale": [[0, 1], [1, 0.25]]})
            # FIRE bands from the ignition on (one fused flame ribbon per band, glow + rim + mid + core)
            L += trail_stack({"path": bp, "at": bp[0][1], "t0": t_ig, "t1": TB + 0.02, "lifetime": 0.24, "faceCamera": True,
                              "transparency": [[0, 0], [0.5, 0.15], [1, 1]], "widthScale": [[0, 1], [1, 0.25]], "textureMode": "Stretch"},
                             {"glow": 4.5 + 0.3 * lv, "rim": 2.6 + 0.2 * lv, "mid": 1.7 + 0.12 * lv, "core": 0.5}, cool=False)
    # sand haze + dust pulled in at the base, wind needles streaking round
    L.append({"type": "emitter", "at": [C[0], 1.5, C[2]], "rate": [[TW, TB, 22]], "seed": 1402, "part": [22, 1, 22], "props": {
        "Texture": "haze_soft", "Color": "#e8d6b0", "LightEmission": 0.1, "Brightness": 1, "Shape": "Cylinder", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "Size": [[0, 7], [1, 3]], "Lifetime": [0.7, 1.0], "Speed": [10, 16], "Rotation": [0, 360], "RotSpeed": [-20, 20],
        "FlipbookLayout": "None", "Transparency": [[0, 1], [0.2, 0.55], [0.8, 0.65], [1, 1]], "ZOffset": -1.0}})
    L.append({"type": "emitter", "at": [C[0], 8, C[2]], "rate": [[TW, TI, 60]], "seed": 1403, "part": [12, 14, 12], "props": {
        "Texture": "needle_bold", "Color": "#fff8ec", "LightEmission": 0.6, "Brightness": 1.2, "Shape": "Cylinder", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "Size": [[0, 3.5], [1, 0.4]], "Lifetime": [0.16, 0.24], "Speed": [30, 40], "SpreadAngle": [60, 0],
        "Orientation": "VelocityParallel", "Transparency": [[0, 0.3], [1, 0.8]], "ZOffset": 0.4}})

    # ---- the breath into the base + IGNITION spikes climbing the funnel
    L += glint([C[0], 2.5, C[2] + 2], TI, size=8, life=0.22, seed=1404)
    for k in range(10):
        a = k / 10 * 2 * math.pi
        r = 2.4 + 0.8 * (k % 3) / 2
        p = [C[0] + math.cos(a) * r, 0, C[2] + math.sin(a) * r]
        h = 8 + 2 * ((k * 3) % 3) / 2
        L += emit_stack("anime_flame_spike", [p[0], h * 0.42, p[2]], TI + 0.01 * k, size=[[0, h * 0.95], [1, h * 1.05]], life=0.5, cool=False,
                        rot=-math.degrees(math.atan2(math.cos(a), 1.0)) * 0.4, seed=1411 + k, orient="FacingCameraWorldUp", z=0.04 * (k % 4))
    for lv in range(LEVELS):
        h = 0.8 + lv * (TOP - 0.8) / (LEVELS - 1)
        L += glint([C[0] + band_r(h) * math.cos(lv * 2.1), h, C[2] + band_r(h) * math.sin(lv * 2.1)], TI + 0.045 * lv + 0.02, size=3.0 + 0.2 * lv,
                   life=0.16, seed=1421 + lv)
    # the pump: spike bursts at the foot on each coil pass, embers spiralling, smooth dark smoke off the top
    for j, tp in enumerate((1.65, 1.95, 2.2)):
        for e in emit_stack("anime_flame_spike", [C[0], 4.5, C[2]], tp, size=[[0, 9], [1, 10]], life=0.32, rate=[[tp, tp + 0.08, 60]], cool=False,
                            seed=1431 + j, orient="FacingCameraWorldUp", z=0.3, transparency=[[0, 0], [0.6, 0.1], [1, 1]]):
            e["part"] = [6, 0.5, 6]; e["props"]["Shape"] = "Cylinder"; e["props"]["ShapeStyle"] = "Surface"; e["props"]["Rotation"] = [-25, 25]
            L.append(e)
        L.append(needles([C[0], 2, C[2]], tp, 12, speed=(50, 80), size=4.5, spread=30, seed=1441 + j, rot=[0, 0, 0], part=[5, 0.5, 5]))
    L.append(embers([C[0], 8, C[2]], 0, rate=[[TI, TB, 60]], speed=(10, 18), life=(0.5, 1.0), grav=4, part=[12, 14, 12], seed=1445))
    L.append(dark_haze([C[0], TOP + 2, C[2]], 0, n=0, rate=[[TI + 0.3, TB + 0.3, 10]], size=(6, 13), life=(1.2, 1.6), part=(12, 2, 12), tr=0.55, seed=1446))
    L += aura_haze(C, TI, TB - TI + 0.2, radius=9.0, height=12.0, strength=0.9, seed=1447, cloud=0.5)
    L.append(glow_pool(C, TI, 16, life=0.4, rate=[[TI, TB, 10]], peak=0.3, seed=1448))

    # ---- BURST (BIG)
    T = TB
    for j in range(16):
        rot = j / 16 * 360 + 6 * math.sin(j * 2.1)
        ln = 20 + 6 * ((j * 7) % 4) / 3
        L += emit_stack("anime_flame_spike", [C[0], 8, C[2]], T + 0.004 * (j % 3), size=[[0, ln * 0.6], [0.2, ln], [1, ln * 1.05]],
                        life=0.42 + 0.06 * (j % 2), cool=False, rot=rot, seed=1451 + j, z=0.5)
    L.append(speed_lines([C[0], 8, C[2]], T + 0.03, 34, seed=1471))
    L += ink([C[0], 8, C[2]], T + 0.03, 16, rot=10, seed=1472)
    L += glint([C[0], 8.5, C[2] + 1], T + 0.02, size=13, life=0.26, seed=1473)
    L.append(needles([C[0], 8, C[2]], T + 0.03, 36, speed=(80, 130), size=7, life=(0.25, 0.45), seed=1474))
    L += aura_haze(C, T + 0.01, 1.8, radius=15.0, height=11.0, strength=1.3, seed=1475, cloud=0.6)
    L.append(dark_haze([C[0], 6, C[2]], T + 0.05, n=14, size=(7, 15), life=(1.2, 1.6), part=(8, 6, 8), tr=0.5, seed=1476, outward=10))
    L.append(scorch(C, T, size=16, life=DUR - T + 0.1, seed=1477))
    L += molten_crack(C, T + 0.02, size=18, rot=60, glow_life=0.6, char_life=DUR - T, seed=1478, flames=False)
    L.append(embers([C[0], 10, C[2]], T + 0.1, n=40, speed=(8, 20), life=(0.8, 1.4), grav=-12, seed=1479))

    hits, numbers = [], []
    for i, q in enumerate(TARGETS):
        for k, tt in enumerate((1.4, 1.8, 2.15)):
            hits.append({"t": tt + 0.02 * i, "dummy": i, "dir": [R(-q[0] * 0.05), 1, R(-(q[2] - C[2]) * 0.05)], "power": 0.3})
        d = [q[0] - C[0], 0, q[2] - C[2]]
        n = math.hypot(d[0], d[2]) or 1
        hits.append({"t": T + 0.02, "dummy": i, "dir": [R(d[0] / n), 0.4, R(d[2] / n)], "power": 1.3})
        numbers.append({"t": T + 0.05, "at": [q[0], 8, q[2]], "text": str(188 + 15 * i), "color": WHITE_GOLD, "vel": [0, 11, 0], "size": 1.9})

    t0, life = hp[0][0], hp[-1][0] - hp[0][0]
    jaw = [[0, 6], [(TI - 0.15 - t0) / life, 12], [(TI - t0) / life, 44], [(TI + 0.3 - t0) / life, 40], [(TI + 0.5 - t0) / life, 10],
           [(TB - t0) / life, 46], [(TB + 0.4 - t0) / life, 8], [1, 6]]
    L.append(dragon(hp, t0, life, jaw=R(jaw, 3), tracks=whisker_tracks(DUR + 0.5)))

    return {
        "name": "dragon_09_FirestormCoil", "title": "Firestorm Coil", "element": "Dragon", "archetype": "igniting_twister", "duration": DUR,
        "caster": False, "layers": L, "dummies": TARGETS, "hits": hits, "numbers": numbers,
        "debris": rocks(C, T + 0.01, radius=6, count=12, size=1.2, speed=38, crater=False, seed=1480),
        "hitstop": [{"t": 1.42, "dur": 0.04}, {"t": 1.82, "dur": 0.04}, {"t": 2.17, "dur": 0.04}, {"t": T + 0.03, "dur": 0.10}],
        "shakes": [{"t": TI, "amp": 0.3, "dur": 0.3, "freq": 20}, {"t": T + 0.02, "amp": 0.7, "dur": 0.4, "freq": 18}],
        "lights": [light([C[0], 8, C[2]], [[TI, 0], [TI + 0.1, 24], [TB, 28], [TB + 0.05, 44], [DUR, 4]], rng=34)],
        "camera": CAM,
        "poster": 2.0,
    }


write(build(), out_path(os.path.dirname(__file__), "dragon_09_FirestormCoil"), form="full")
print("wrote dragon_09_FirestormCoil.json")
