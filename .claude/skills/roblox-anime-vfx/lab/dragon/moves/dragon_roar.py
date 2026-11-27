"""Dragon Roar (full V) - exhaled blades of superheated wind (DESIGN v4: the roar's mechanic becomes a gale of
blades). Signature: RADIATING STRAIGHT BURNING SLICE LINES - a fan of 5 spinning crescent blades flies out low over
the sand, each cutting one long burning line as it passes.

Beat sheet
  0.00-0.45  the dragon rears up and inhales: heat haze and pale wind needles are drawn into the jaw, the whiskers
             whip back                                                                    (anticipation)
  0.45       ROAR / EXHALE: glint at the jaw, a heat ring, white speed lines; the head thrusts forward (squash)
  0.48-1.20  5 spinning crescent blades (anime slashes, gold body, white-hot edge, crimson rim) fan out low and fast,
             staggered 0.04 s; each draws a burning slice line on the sand behind it, needles and haze peel off it
  ~0.7       blades pass through targets: hit-stop 0.06 each, glint + ink + needles, knock-back
  1.20-2.00  the blades tear into shards far out; the slice lines burn and cool to charcoal; haze drifts; the jaw
             closes and smoke curls out
Camera: behind and above the dragon's shoulder, the fan of lines laid out ahead.
Run: python3 lab/dragon/moves/dragon_roar.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

TX = 0.45
DUR = 2.0
ORIGIN = [0, 2.2, -3]
REACH = 30.0
FAN = [-36, -18, 0, 18, 36]
TARGETS = [[-6.5, 0, -14], [1.0, 0, -17], [8.0, 0, -15]]
CAM = {"pos": [[0, [25, 15, 0]], [1, [25, 15, 0]]], "look": [[0, [-1, 5, -11]], [1, [-1, 5, -11]]], "fov": [[0, 64], [1, 64]]}

CP = [(-1.8, [-20, 8, 2]), (-0.9, [-11, 10, 8]), (0.0, [-3, 11, 8.5]), (0.3, [1, 14.5, 6.5]), (TX, [0, 15, 5.2]), (0.55, [0, 12.5, 2.8]),
      (0.9, [0, 12, 1.6]), (1.4, [-2, 12.5, 0.5]), (DUR + 0.4, [-12, 14, -2])]


def blade_dir(a):
    return [math.sin(math.radians(a)), 0, -math.cos(math.radians(a))]


def build():
    hp = cr_path(CP, -1.8, DUR + 0.4)
    head = lambda t: cr_point(CP, t)
    L = [ambience([0, 0, -12], 0, DUR, radius=16, rate=10, seed=1501)]

    # ---- inhale: haze + wind needles drawn into the jaw
    L.append({"type": "emitter", "at": head(0.2), "path": hp, "part": [9, 7, 9], "rate": [[0.05, TX - 0.03, 50]], "seed": 1502, "props": {
        "Texture": "needle_bold", "Color": "#fff8ec", "LightEmission": 0.7, "Brightness": 1.3, "Shape": "Sphere", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "Size": [[0, 3.0], [1, 0.4]], "Lifetime": [0.16, 0.22], "Speed": [32, 42], "Orientation": "VelocityParallel",
        "Transparency": [[0, 0.3], [1, 0.8]], "ZOffset": 0.4}})
    L.append({"type": "emitter", "at": head(0.2), "path": hp, "rate": [[0.05, TX, 10]], "seed": 1503, "part": [4, 3, 4], "props": {
        "Texture": "haze_soft", "Color": [[0, "#ff9a3a"], [1, "#ff5a1e"]], "LightEmission": 0.7, "Brightness": 1, "Size": [[0, 6], [1, 3]],
        "Lifetime": [0.4, 0.6], "Speed": [0.5, 1], "Rotation": [0, 360], "RotSpeed": [-10, 10], "FlipbookLayout": "None",
        "Transparency": [[0, 1], [0.3, 0.7], [1, 1]], "ZOffset": -1.0}})
    L.append(glow_orb(head(0.2), 0, 5, life=0.25, rate=[[0.1, TX + 0.1, 14]], path=hp, locked=True, tr=0.45, seed=1504))

    # ---- the exhale
    hx = head(TX + 0.03)
    L += glint(hx, TX, size=9, life=0.22, seed=1505)

    # ---- the blades: spinning anime crescents flying low and fast in a fan, each cutting a burning line
    hits, numbers, stops = [], [], []
    for b, a in enumerate(FAN):
        t0 = TX + 0.03 + 0.04 * abs(b - 2)
        t1 = t0 + 0.62
        d = blade_dir(a)
        p0 = [ORIGIN[0] + d[0] * 2, 2.2, ORIGIN[2] + d[2] * 2]
        p1 = [ORIGIN[0] + d[0] * REACH, 1.6, ORIGIN[2] + d[2] * REACH]
        mv = {"from": p0, "to": p1, "t0": t0, "t1": t1, "ease": "out"}
        for e in emit_stack("anime_slash", p0, t0, size=[[0, 9], [0.2, 12.5], [1, 13]], life=0.7, cool=False, rot=-90 + a * 0.3, seed=1511 + 4 * b,
                            z=0.5, move=mv, locked=True):
            e["props"]["RotSpeed"] = [520, 520]
            L.append(e)
        # needles + haze peeling off the blade as it flies
        ne = needles(p0, 0, 0, speed=(8, 16), size=3.5, life=(0.15, 0.25), spread=40, seed=1513 + 4 * b, rate=[[t0, t1 - 0.1, 50]])
        ne["move"] = mv
        L.append(ne)
        L.append({"type": "emitter", "at": p0, "move": mv, "rate": [[t0, t1, 12]], "seed": 1514 + 4 * b, "part": [2, 1, 2], "props": {
            "Texture": "haze_soft", "Color": [[0, "#ff9a3a"], [1, "#ff5a1e"]], "LightEmission": 0.7, "Brightness": 1, "Size": [[0, 4], [1, 8]],
            "Lifetime": [0.6, 0.9], "Speed": [1, 2], "SpreadAngle": [180, 180], "Rotation": [0, 360], "RotSpeed": [-10, 10], "FlipbookLayout": "None",
            "Transparency": [[0, 1], [0.2, 0.72], [0.7, 0.82], [1, 1]], "ZOffset": -1.0}})
        # the burning slice line laid on the sand behind it (two overlapping decals so it grows with the blade)
        for k, (f, ln) in enumerate(((0.32, 18), (0.7, 20))):
            mid = [ORIGIN[0] + d[0] * REACH * f, 0, ORIGIN[2] + d[2] * REACH * f]
            L += slice_mark(mid, t0 + (t1 - t0) * (0.12 + 0.35 * k), length=ln, rot=90 - a, glow_life=1.0, char_life=DUR - t0, seed=1531 + 3 * b + k)
        # the blade tears into shards far out
        L += ink(p1, t1 - 0.04, 6, rot=a, seed=1551 + b)
        L += glint([p1[0], 2.2, p1[2]], t1 - 0.05, size=3.0, life=0.16, seed=1561 + b)

    for i, q in enumerate(TARGETS):
        a = math.degrees(math.atan2(q[0] - ORIGIN[0], -(q[2] - ORIGIN[2])))
        b = min(range(5), key=lambda k: abs(FAN[k] - a))
        t0 = TX + 0.03 + 0.04 * abs(b - 2)
        dist = math.hypot(q[0] - ORIGIN[0], q[2] - ORIGIN[2])
        u = min(1, max(0, (dist - 2) / (REACH - 2)))
        th = t0 + 0.62 * (1 - math.sqrt(1 - u))           # inverse of the ease-out
        hp_ = [q[0], 3.0, q[2] + 0.5]
        L += glint(hp_, th, size=4.5, life=0.2, seed=1571 + i)
        L += ink(hp_, th + 0.01, 5.5, rot=30 * i, seed=1575 + i)
        L.append(needles(hp_, th + 0.02, 12, speed=(40, 70), size=3.4, spread=60, seed=1579 + i))
        d = blade_dir(FAN[b])
        hits.append({"t": th, "dummy": i, "dir": [R(d[0]), 0, R(d[2])], "power": 0.9})
        numbers.append({"t": th + 0.02, "at": [q[0] + 1, 6.4, q[2]], "text": str(144 + 11 * i), "color": GOLD, "vel": [0, 9, 0], "size": 1.7})
        stops.append({"t": th + 0.02, "dur": 0.06})

    L += aura_haze([0, 0, -14], TX + 0.1, 1.4, radius=13.0, height=6.0, strength=1.0, seed=1590, cloud=0.45)   # OUTSIDE
    L.append(smoke_wisps(head(1.3), 1.2, DUR, 6, size=2.8, part=[0.6, 0.4, 0.6], seed=1591))

    t0, life = hp[0][0], hp[-1][0] - hp[0][0]
    jaw = [[0, 6], [(0.2 - t0) / life, 14], [(TX - t0) / life, 50], [(TX + 0.6 - t0) / life, 46], [(1.3 - t0) / life, 8], [1, 6]]
    L.append(dragon(hp, t0, life, jaw=R(jaw, 3), tracks=whisker_tracks(DUR + 0.5, amp=24)))

    return {
        "name": "dragon_10_DragonRoar", "title": "Dragon Roar", "element": "Dragon", "archetype": "wind_blades", "duration": DUR,
        "caster": False, "layers": L, "dummies": TARGETS, "hits": hits, "numbers": numbers,
        "hitstop": stops,
        "shakes": [{"t": TX, "amp": 0.45, "dur": 0.35, "freq": 22}],
        "lights": [light(hx, [[0, 0], [0.3, 10], [TX, 26], [TX + 0.3, 6], [1.0, 0]], rng=24)],
        "camera": CAM,
        "poster": TX + 0.3,
    }


write(build(), out_path(os.path.dirname(__file__), "dragon_10_DragonRoar"), form="full")
print("wrote dragon_10_DragonRoar.json")
