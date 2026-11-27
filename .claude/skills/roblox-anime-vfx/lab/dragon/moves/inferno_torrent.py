"""Inferno Torrent (full Z) - a detonating blast breath. Signature: a THICK torrent poured in a straight line into a
ground point ~22 studs ahead that DETONATES into a mushrooming dome of fire (a crown of huge flame spikes over rolling
billows), leaving a crater.

Beat sheet (anime shape language: one lead shape per beat, hierarchy, smooth haze outside, dark accents)
  0.00-0.70  the dragon swims in and rears up; the throat glows, a flame swirl spins in the jaw, needles and embers
             are sucked into the mouth, heat haze gathers                                       (anticipation)
  0.70       release: glint at the jaw, the head recoils a little (squash), the torrent shoots out (stretch)
  0.70-1.65  the torrent: crossed flame-strip planes + glow, billow lobes rolling down it, gold needles streaming
             along it, smooth dark smoke riding its top
  0.85       DETONATION: one mono frame; hit-stop 0.16; a crown of 18 huge flame spikes + billow dome, white speed
             lines, black ink shards, a needle burst, the crater (bowl, rock rim, molten core), molten cracks, a dust
             ring, warm haze rolling out far past the blast; targets launched
  0.85-1.65  the torrent keeps pouring into the blast (splash billows); then it thins and cuts
  1.65-2.60  the jaw closes, the dragon swims off; the crater burns down (flickers), smoke rises, embers drift
Camera: full-form gameplay camera (fixed, pulled back), the dragon and the blast in one frame.
Run: python3 lab/dragon/moves/inferno_torrent.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa
from kit import _fb

TR, TD, TCUT = 0.70, 0.85, 1.65
DUR = 2.6
G = [0, 0, -22]
TARGETS = [[-3.5, 0, -21], [3.0, 0, -23.5], [0.5, 0, -18.5]]
# side-on and elevated (DESIGN): the dragon, the torrent and the blast in one fixed frame
FULL_CAM = {"pos": [[0, [27, 16, -5]], [1, [27, 16, -5]]], "look": [[0, [-1, 7, -12]], [1, [-1, 7, -12]]], "fov": [[0, 60], [1, 60]]}

# head control points (t, pos): swims in from the right, rears up, lunges a little on the breath, swims off left
CP = [(-2.4, [-12, 10, 14]), (-1.5, [-3, 11, 14]), (-0.6, [7, 11, 10]), (0.0, [8, 12, 5]), (0.35, [3, 14, 3]), (0.68, [0.4, 15.5, 1.2]), (0.78, [0, 14.6, -0.6]),
      (1.2, [-0.2, 14.0, -2.0]), (TCUT, [-0.6, 13.8, -3.0]), (2.0, [-4, 14.5, -4.5]), (DUR + 0.3, [-12, 15, -6])]


def _cr(p0, p1, p2, p3, u):
    return [0.5 * (2 * b + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (-a + 3 * b - 3 * c + d) * u ** 3)
            for a, b, c, d in zip(p0, p1, p2, p3)]


def head(t):
    ts = [c[0] for c in CP]
    i = max(0, min(len(CP) - 2, next((k for k in range(len(ts) - 1) if ts[k] <= t < ts[k + 1]), len(ts) - 2)))
    u = (t - ts[i]) / (ts[i + 1] - ts[i])
    P = [c[1] for c in CP]
    return _cr(P[max(0, i - 1)], P[i], P[i + 1], P[min(len(P) - 1, i + 2)], u)


def head_path(t0=-2.4, t1=DUR, step=1 / 60):
    n = int((t1 - t0) / step)
    return [[R(t0 + (t1 - t0) * k / n, 4), R(head(t0 + (t1 - t0) * k / n))] for k in range(n + 1)]


def mouth(t, ahead=2.2):
    a, b = head(t - 0.02), head(t + 0.02)
    d = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(x * x for x in d)) or 1
    h = head(t)
    # aim the jaw down toward the blast while breathing
    w = 1.0 if TR - 0.05 <= t <= TCUT + 0.05 else 0.0
    aim = [G[i] - h[i] for i in range(3)]
    an = math.sqrt(sum(x * x for x in aim))
    f = [(1 - w) * d[i] / n + w * aim[i] / an for i in range(3)]
    fn = math.sqrt(sum(x * x for x in f)) or 1
    return [h[i] + f[i] / fn * ahead for i in range(3)]


def keyed(fn, t0, t1, n=40, **kw):
    return [[R((k / n), 4), R(fn(t0 + (t1 - t0) * k / n, **kw))] for k in range(n + 1)]


def path(fn, t0, t1, n=60, **kw):
    return [[R(t0 + (t1 - t0) * k / n, 4), R(fn(t0 + (t1 - t0) * k / n, **kw))] for k in range(n + 1)]


def ground(t, y=0.4):
    w = 0.6 * math.sin(t * 9)
    return [G[0] + w, y, G[2] + 0.4 * math.cos(t * 7)]


def build():
    L = [ambience([0, 0, -12], 0, DUR, radius=16, rate=10, seed=1101)]
    mp = path(mouth, 0.0, DUR, n=160)

    # ---- charge: throat glow, swirl in the jaw, needles + embers sucked in, warm haze gathering round the head
    L.append(glow_orb(mp[0][1], 0, 6, life=0.25, rate=[[0.1, TR + 0.02, 16]], path=mp, locked=True, tr=0.4, seed=1102))
    L += swirl(mp[0][1], 0.2, TR + 0.02, 5.5, path=mp, seed=1103)
    L.append({"type": "emitter", "at": mouth(0.5), "path": mp, "part": [10, 8, 10], "rate": [[0.15, TR - 0.03, 50]], "seed": 1104, "props": {
        "Texture": "needle_bold", "Color": [[0, "#fff6b0"], [0.5, "#ffd21a"], [1, "#ff6a10"]], "LightEmission": 1, "Brightness": 1.4,
        "Shape": "Sphere", "ShapeInOut": "Inward", "ShapeStyle": "Surface", "Size": [[0, 3.0], [1, 0.4]], "Lifetime": [0.16, 0.22],
        "Speed": [34, 44], "Orientation": "VelocityParallel", "Transparency": [[0, 0.2], [1, 0.7]], "ZOffset": 0.4}})
    L.append(embers(mouth(0.5), 0, rate=[[0.1, TR, 40]], speed=(6, 12), life=(0.4, 0.7), grav=0, path=mp, part=[8, 6, 8], seed=1105))
    L.append({"type": "emitter", "at": mouth(0.4), "path": mp, "rate": [[0.1, TR, 10]], "seed": 1106, "part": [3, 2, 3], "props": {
        "Texture": "haze_soft", "Color": [[0, "#ff9a3a"], [1, "#ff5a1e"]], "LightEmission": 0.7, "Brightness": 1, "Size": [[0, 4], [1, 9]],
        "Lifetime": [0.6, 0.9], "Speed": [1, 2], "SpreadAngle": [180, 180], "Rotation": [0, 360], "RotSpeed": [-10, 10], "FlipbookLayout": "None",
        "Transparency": [[0, 1], [0.2, 0.7], [0.7, 0.8], [1, 1]], "ZOffset": -1.0}})

    # ---- release
    L += glint(mouth(TR), TR, size=8, life=0.2, seed=1107)

    # ---- the torrent: one fat tapered ribbon (glow + rim + mid + core flame strips) from the jaw into the blast point
    life = TCUT - TR + 0.1
    frm = keyed(mouth, TR, TR + life)
    to = keyed(ground, TR, TR + life)
    wk = [[0, [1.2, 4.0]], [0.06, [2.4, 8.5], "out"], [0.88, [2.2, 8.0]], [1, [0.5, 2.0], "in"]]
    reach = [[0, 0.1], [(TD - TR) / life, 1, "out"], [1, 1]]
    for lay, wm, sp in (("glow", 1.8, 2.6), ("rim", 1.0, 3.4), ("mid", 0.7, 4.0), ("core", 0.24, 5.0)):
        L.append({"type": "beam", "from": frm, "to": to, "t0": TR, "life": life, "textures": [f"{st}_{lay}" for st in STRIPS], "swap": 0.06,
                  "textureLength": 7, "textureSpeed": sp, "segments": 14, "color": PALS["fire"]["HOT"][lay], "lightEmission": LE[lay],
                  "brightness": BR[lay], "width": [[k, [w[0] * wm, w[1] * wm]] + e for k, w, *e in wk], "reach": reach,
                  "transparency": [[0, 0], [0.9, 0.05], [1, 0.6]]})
    # billow lobes rolling down it (at three depths), needles streaming along it, smooth dark smoke on top
    for j, (f, sz, rt) in enumerate(((0.3, 5.5, 18), (0.6, 7.5, 16), (0.85, 9.5, 14))):
        bp = [[R(TR + (TCUT - TR) * i / 40, 4), R([m + (c - m) * f for m, c in zip(mouth(TR + (TCUT - TR) * i / 40), ground(TR + (TCUT - TR) * i / 40, y=1.5))])]
              for i in range(41)]
        for e in billow(bp[0][1], TR, sz, life=0.34, seed=1111 + j * 3, grow=1.3, rot=60 * j):
            e.pop("emits", None); e["rate"] = [[TR + 0.04 + 0.03 * j, TCUT, rt]]; e["path"] = bp
            L.append(e)
    mid = [(mouth(TR + 0.3)[i] + G[i]) / 2 for i in range(3)]
    L.append({"type": "emitter", "at": mouth(TR + 0.2), "path": path(mouth, TR, TCUT), "rate": [[TR + 0.02, TCUT, 70]], "seed": 1115,
              "rot": [-128, 0, 0], "props": {
        "Texture": "needle_bold", "Color": [[0, "#fff6b0"], [0.5, "#ffd21a"], [1, "#ff6a10"]], "LightEmission": 1, "Brightness": 1.5,
        "Size": [[0, 4.5], [1, 0.4]], "Lifetime": [0.2, 0.32], "Speed": [60, 85], "SpreadAngle": [8, 8], "Drag": 2,
        "Orientation": "VelocityParallel", "ZOffset": 0.6}})
    L.append({"type": "emitter", "at": [mid[0], mid[1] + 2.5, mid[2]], "rate": [[TR + 0.1, TCUT + 0.1, 12]], "seed": 1116, "part": [3, 2, 12],
              "props": {"Texture": "haze_soft", "Color": [[0, "#4a2a22"], [1, "#6a4a3e"]], "LightEmission": 0, "Brightness": 1,
        "Size": [[0, 4], [1, 9]], "Lifetime": [0.9, 1.3], "Speed": [1, 3], "SpreadAngle": [30, 30], "Acceleration": [0, 2.5, 0], "Drag": 1.2,
        "Rotation": [0, 360], "RotSpeed": [-10, 10], "FlipbookLayout": "None", "Transparency": [[0, 1], [0.15, 0.55], [0.6, 0.7], [1, 1]],
        "ZOffset": -1.0}})

    # ---- DETONATION (BIG)
    T = TD
    # PRIMARY: a crown of huge flame spikes erupting out of the blast as a wave, over a dome of rolling billows
    for k in range(18):
        a = k / 18 * 2 * math.pi + 0.15 * math.sin(k * 2.7)
        r = 1.5 + 6.0 * ((k * 7) % 5) / 4
        h = 19 - 1.3 * r + 3.0 * ((k * 3) % 4) / 3
        p = [G[0] + math.cos(a) * r, 0, G[2] + math.sin(a) * r]
        lean = math.degrees(math.atan2(math.cos(a), 1.0)) * 0.5
        tk = T + 0.004 + 0.022 * (r - 1.5) / 6.0
        L += emit_stack("anime_flame_spike", [p[0], h * 0.42, p[2]], tk, size=[[0, h * 0.95], [1, h * 1.05]], life=0.55 + 0.35 * (r - 1.5) / 6.0,
                        cool=False, rot=-lean, seed=1121 + k, orient="FacingCameraWorldUp", z=0.04 * (k % 5))
    for j in range(7):
        a = j / 7 * 2 * math.pi
        L += billow([G[0] + math.cos(a) * 3.0, 4.0 + 2.0 * (j % 2), G[2] + math.sin(a) * 3.0], T + 0.03 + 0.02 * j, 9.0, life=0.7,
                    seed=1141 + j, grow=1.5, rot=50 * j)
    # SECONDARY: white speed lines, black ink shards, a star flash
    L.append(_fb("speed_burst", [G[0], 4, G[2]], T + 0.03, 30, 0.24, color=[[0, "#fff8e0"], [0.5, "#ffe08a"], [1, "#ffb040"]], le=1, br=1.2,
                 seed=1151, z=0.9, tr=[[0, 0.1], [0.6, 0.35], [1, 1]]))
    sh = emit_stack("ink_shards", [G[0], 4, G[2]], T + 0.03, size=[[0, 16], [1, 20]], life=0.32, cool=False, seed=1152, rot=10, layers=("rim",), z=0.7)
    for e in sh:
        e["props"]["Color"] = "#1a0806"; e["props"]["LightEmission"] = 0
    L += sh
    L += glint([G[0], 5, G[2] + 1], T + 0.02, size=14, life=0.26, seed=1153)
    # TERTIARY: gold needles flying out, scattered sparkles
    L.append({"type": "emitter", "at": [G[0], 2, G[2]], "emits": [[T + 0.03, 30]], "seed": 1154, "part": [3, 0.5, 3], "props": {
        "Texture": "needle_bold", "Color": [[0, "#fff6b0"], [0.4, "#ffd21a"], [1, "#ff6a10"]], "LightEmission": 1, "Brightness": 1.6,
        "Shape": "Cylinder", "ShapeInOut": "Outward", "ShapeStyle": "Surface", "Size": [[0, 8], [0.5, 4.5], [1, 0.5]],
        "Lifetime": [0.25, 0.45], "Speed": [80, 130], "SpreadAngle": [30, 30], "Drag": 6, "Acceleration": [0, 8, 0],
        "Orientation": "VelocityParallel", "ZOffset": 0.6}})
    for k in range(5):
        a = k * 2.4
        r = 5 + 3 * ((k * 5) % 3) / 2
        L += glint([G[0] + math.cos(a) * r, 3 + 4 * ((k * 3) % 4) / 3, G[2] + math.sin(a) * r], T + 0.07 + 0.04 * k, size=3.5 + (k % 3), life=0.2,
                   seed=1155 + k)
    # OUTSIDE: warm haze rolling out far past the blast
    L += aura_haze(G, T + 0.01, 2.0, radius=14.0, height=10.0, strength=1.3, seed=1160, cloud=0.6)
    # MASS: crater, molten cracks, dust ring, dark smoke column, rocks
    cr = crater(G, T, radius=8.0, life=DUR - T, seed=1170)
    L += [x for x in cr if "kind" not in x]
    L += molten_crack(G, T + 0.03, size=24, rot=15, glow_life=1.5, char_life=DUR - T, seed=1171, flames=False)
    dr = dust_ring(G, T + 0.02, n=18, speed=(40, 55), size=(4, 9), seed=1172)
    dr["props"]["Transparency"] = [[0, 0.35], [0.6, 0.55], [1, 1]]
    L.append(dr)
    L.append(glow_pool(G, T, 20, life=0.6, peak=0.3, seed=1173))
    L.append({"type": "emitter", "at": [G[0], 6, G[2] - 1.5], "emits": [[T + 0.12, 12]], "rate": [[T + 0.15, TCUT + 0.3, 10]], "seed": 1174,
              "part": [8, 3, 5], "props": {"Texture": "haze_soft", "Color": [[0, "#4a2a22"], [1, "#6a4a3e"]], "LightEmission": 0, "Brightness": 1,
        "Size": [[0, 7], [1, 16]], "Lifetime": [1.2, 1.7], "Speed": [3, 6], "SpreadAngle": [30, 30], "Acceleration": [0, 3, 0], "Drag": 1.2,
        "Rotation": [0, 360], "RotSpeed": [-10, 10], "FlipbookLayout": "None", "Transparency": [[0, 1], [0.15, 0.45], [0.6, 0.6], [1, 1]],
        "ZOffset": -1.5}})
    # the torrent keeps pouring into the blast: splash billows + spikes at the contact
    for e in billow([G[0], 2, G[2]], T, 8.0, life=0.45, seed=1175, grow=1.4):
        e.pop("emits", None); e["rate"] = [[T + 0.1, TCUT, 10]]
        L.append(e)
    for e in emit_stack("anime_flame_spike", [G[0], 3.5, G[2]], T + 0.12, size=[[0, 7], [1, 8]], life=0.32, rate=[[T + 0.12, TCUT - 0.05, 20]],
                        cool=False, seed=1176, orient="FacingCameraWorldUp", z=0.3, transparency=[[0, 0], [0.6, 0.1], [1, 1]]):
        e["part"] = [6, 0.5, 6]
        e["props"]["Rotation"] = [-30, 30]
        L.append(e)
    # after: flames burn down in the crater, embers drift, smoke wisps
    L += flicker([G[0], 0, G[2]], TCUT, DUR, 4.0, seed=1177)
    L.append(smoke_wisps([G[0], 0.4, G[2]], TCUT, DUR, 8, size=4, part=[10, 0.2, 10], seed=1178))

    debris = rocks(G, T + 0.01, radius=7, count=12, size=1.2, speed=36, crater=False, seed=1179) + [x for x in cr if "kind" in x]
    hits, numbers = [], []
    for i, q in enumerate(TARGETS):
        th = T + 0.02 + 0.01 * i
        d = [q[0] - G[0], 0, q[2] - G[2]]
        n = math.hypot(d[0], d[2]) or 1
        hits.append({"t": th, "dummy": i, "dir": [R(d[0] / n), 0, R(d[2] / n)], "power": 1.3})
        numbers.append({"t": th + 0.03, "at": [q[0], 7.5, q[2]], "text": str(212 + 17 * i), "color": WHITE_GOLD, "vel": [0, 11, 0], "size": 2.0})

    jaw = [[0, 6], [0.22, 12], [TR / DUR, 48], [(TCUT - 0.05) / DUR, 44], [(TCUT + 0.2) / DUR, 8], [1, 6]]
    tracks = {}
    for side in "LR":
        for i in range(3):
            tracks[f"whisker{side}_{i}"] = {"rot": [[R(t, 3), [R(-18 + 16 * math.sin(t * 6 + i), 2), 0, R((10 if side == "L" else -10) * math.sin(t * 3 + i), 2)]]
                                                    for t in [k * 0.1 for k in range(27)]]}
    L.append(dragon(head_path(), -2.4, DUR + 2.4, jaw=[[R((t * DUR + 2.4) / (DUR + 2.4), 3), v] for t, v in jaw], tracks=tracks))

    return {
        "name": "dragon_07_InfernoTorrent", "title": "Inferno Torrent", "element": "Dragon", "archetype": "blast_breath", "duration": DUR,
        "caster": False, "layers": L, "dummies": TARGETS, "hits": hits, "numbers": numbers, "debris": debris,
        "hitstop": [{"t": T + 0.03, "dur": 0.16}],
        "impact": [{"t": T + 0.025, "dur": 0.05, "mode": "mono"}],
        "shakes": [{"t": TR, "amp": 0.15, "dur": 0.2, "freq": 20}, {"t": T + 0.02, "amp": 0.7, "dur": 0.45, "freq": 18}],
        "lights": [light(mouth(TR), [[0, 0], [0.3, 10], [TR, 20], [TCUT, 20], [TCUT + 0.3, 0]], rng=24),
                   light([G[0], 4, G[2]], [[T, 0], [T + 0.02, 44], [T + 0.5, 20], [TCUT, 16], [DUR, 4]], rng=34)],
        "camera": FULL_CAM,
        "poster": T + 0.1,
    }


write(build(), out_path(os.path.dirname(__file__), "dragon_07_InfernoTorrent"), form="full")
print("wrote dragon_07_InfernoTorrent.json")
