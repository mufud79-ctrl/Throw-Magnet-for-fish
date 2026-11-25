"""Horn Rush (hybrid X) - a short horns-first charge that shoves. Signature: a WALL of flame-wind (a broad curved
flame front, 14 studs wide) that rolls forward along the ground ahead of the charge with long gust lines and embers
riding them - the only move whose shape is a wide wall moving away from you.

Beat sheet
  0.00-0.30  crouch, head lowered, horns heat up (a glow + small tongues at the head), embers and gust needles are
             pulled in toward the head, dust creeps in                                 (anticipation, squash)
  0.30       CHARGE: the caster lunges 5 studs head-first; a 1-frame flash at the horns; the wall is born at the head
  0.30-0.85  the wall rolls 0 -> 14 studs ahead and slows (ease-out): a fire_crescent front laid horizontal, a row of
             rolling billows behind it, a flame wash left on the sand, gust lines streaking past; black smoke shoved
             ahead of it
  0.46       contact: both targets slide back with the wall; hit-stop 0.06             (timing)
  0.56       a thinner second wall rides in behind the first                           (follow-through)
  0.85-1.50  the wall tears into tongues and dies; a wedge of sand dust blows forward; embers settle; the caster
             recovers from the lunge                                                    (follow-through)
Run: python3 lab/dragon/moves/horn_rush.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

TC, TH, T2 = 0.30, 0.46, 0.56
DUR = 1.5
TARGETS = [[-3.2, 0, -10.5], [3.4, 0, -11.5]]

POSE = {
    "lean": [[0, 0], [0.25, -12, "out"], [TC - 0.01, -14], [TC + 0.05, -38, "outExpo"], [0.7, -30], [1.1, -6], [1.4, 0]],
    "armR": [[0, 0], [0.25, -40, "out"], [TC + 0.05, -70, "outExpo"], [0.8, -50], [1.3, 0]],
    "armL": [[0, 0], [0.25, -40, "out"], [TC + 0.05, -70, "outExpo"], [0.8, -50], [1.3, 0]],
    "armRz": [[0, 0], [0.25, 25], [TC + 0.05, 35], [1.3, 0]],
    "armLz": [[0, 0], [0.25, -25], [TC + 0.05, -35], [1.3, 0]],
    "offset": [[0, [0, 0, 0]], [0.25, [0, -0.5, 0.4], "out"], [TC, [0, -0.5, 0.4]], [TC + 0.12, [0, 0, -5.0], "outExpo"], [0.9, [0, 0, -5.6]], [1.4, [0, 0, -5.6]]],
    "scale": [[0, [1, 1, 1]], [0.25, [1.08, 0.88, 1.08], "out"], [TC, [1.08, 0.88, 1.08]], [TC + 0.05, [0.9, 1.1, 1.0], "outExpo"],
              [0.55, [1.02, 0.98, 1.02]], [0.8, [1, 1, 1]]],
}


def head(t):
    """Head position of the avatar (FK of the upper body, like kit.hand)."""
    D = math.pi / 180
    lean = POSE_KEYS("lean", t, 0) * D
    v = [0, 2.6, -0.2]
    c, s = math.cos(lean), math.sin(lean)
    v = [v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c]
    sc = POSE_KEYS("scale", t, [1, 1, 1]); off = POSE_KEYS("offset", t, [0, 0, 0])
    return [v[0] * sc[0] + off[0], (v[1] + 2) * sc[1] + off[1], v[2] * sc[2] + off[2]]


def POSE_KEYS(k, t, d):
    from kit import _keys
    return _keys(POSE.get(k), t, d)


def head_path(t0, t1, step=1 / 60):
    n = max(2, int((t1 - t0) / step))
    return [[R(t0 + (t1 - t0) * i / n, 4), R(head(t0 + (t1 - t0) * i / n))] for i in range(n + 1)]


def build():
    L = [ambience([0, 0, -6], 0, DUR, radius=10, rate=9, seed=201)]
    hp = head_path(0.0, 1.2)
    # ---- anticipation: horns heat up, gust needles + embers pulled toward the head, dust creeping in
    L.append(glow_orb(hp[0][1], 0, 3.2, life=0.2, rate=[[0.05, 0.9, 14]], path=hp, locked=True, tr=0.45, seed=202))
    for dx, sd in ((-0.5, 203), (0.5, 205)):
        hpx = [[t, [p[0] + dx, p[1] + 0.6, p[2]]] for t, p in hp]
        for e in emit_stack("flame_tongue", hpx[0][1], 0, size=[[0, 1.3], [1, 1.6]], life=0.26, rate=[[0.08, 0.9, 18]], seed=sd,
                            layers=("rim", "mid", "core"), orient="FacingCameraWorldUp", locked=True):
            e["path"] = hpx
            L.append(e)
    L.append({"type": "emitter", "at": [0, 3.6, 0.6], "part": [8, 5, 6], "rate": [[0.02, TC - 0.03, 36]], "seed": 207, "props": {
        "Texture": "spark_streak", "Color": PALS["fire"]["spark"], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "Size": [[0, 1.8], [1, 0.4]], "Lifetime": [0.13, 0.17], "Speed": [22, 28], "Orientation": "VelocityParallel",
        "Transparency": [[0, 0.3], [1, 0.8]], "ZOffset": 0.3}})
    L.append(dust_ring([0, 0, 0.4], 0.05, n=10, speed=(-10, -6), size=(2, 4), seed=208, life=(0.4, 0.5), radius=6))

    # ---- the charge: flash at the horns, black-smoke kick behind the feet
    h0 = head(TC + 0.02)
    L.append(flare(h0, TC + 0.01, size=10, life=0.18, seed=209))
    L.append(smoke([0, 1.0, 1.2], TC, n=5, size=(3, 6), speed=(4, 8), life=(0.8, 1.2), seed=210, direction=[-60, 0, 0], spread=40))

    # ---- the wall: front crescent laid horizontal + a row of rolling billows + a flame wash on the sand
    def wall(t0, t1, z0, z1, width, seed, scale=1.0):
        out = []
        mv = {"from": [0, 2.6, z0], "to": [0, 2.4, z1], "t0": t0, "t1": t1, "ease": "out"}
        # the front: wide crescents, arc horizontal (opening toward the caster), riding the wall
        for k, dx in enumerate((-width * 0.28, width * 0.28)):
            m = dict(mv, **{"from": [dx, 2.8, z0], "to": [dx, 2.6, z1]})
            out += emit_stack("fire_crescent", m["from"], t0, size=[[0, 9 * scale], [1, 11 * scale]], life=0.32, rate=[[t0, t1 - 0.1, 9]],
                              rot=180 if k == 0 else 0, seed=seed + k, move=m, locked=True, z=0.4,
                              transparency=[[0, 0.15], [0.5, 0.2], [1, 1]])
        # rolling billows dropped along the front (they stay where they're born: the wall leaves fire behind it)
        for j in range(7):
            dx = (j - 3) / 3 * width * 0.45
            m = dict(mv, **{"from": [dx, 1.6, z0], "to": [dx, 1.6, z1]})
            out += billow(m["from"], t0, 4.2 * scale, life=0.55, seed=seed + 10 + j, move=m, rot=25 * j, grow=1.3)
            out[-4]["rate"] = [[t0, t1 - 0.05, 7]]
            for e in out[-4:]:
                e.pop("emits", None); e["rate"] = [[t0, t1 - 0.05, 7]]
        # a flame wash on the sand behind the front (flat trail along the ground)
        out += trail_stack({"move": dict(mv, **{"from": [0, 0.15, z0], "to": [0, 0.15, z1]}), "at": [0, 0.15, z0], "t0": t0, "t1": t1,
                            "lifetime": 0.5, "up": [1, 0, 0], "transparency": [[0, 0.2], [0.6, 0.5], [1, 1]], "textureMode": "Wrap", "textureLength": 8},
                           {"rim": width * 0.8, "mid": width * 0.55, "core": width * 0.12})
        out.append(glow_pool([0, 0, z0], t0, width * 0.9, life=0.35, rate=[[t0, t1, 12]], peak=0.4, seed=seed + 30,
                             path=[[t0, [0, 0, z0]], [t0 + (t1 - t0) * 0.35, [0, 0, z0 + (z1 - z0) * 0.7]], [t1, [0, 0, z1]]]))
        # gust lines: long needles streaking forward past the wall, embers riding them
        out.append({"type": "emitter", "at": [0, 2.0, z0], "part": [width, 3.5, 1], "rate": [[t0, t1, 70 * scale]], "seed": seed + 40,
                    "move": mv, "rot": [-90, 0, 0], "props": {
            "Texture": "spark_streak", "Color": PALS["fire"]["spark"], "LightEmission": 1, "Brightness": 1.6, "Size": [[0, 5], [0.7, 3], [1, 0.3]],
            "Lifetime": [0.16, 0.26], "Speed": [55, 75], "SpreadAngle": [3, 3], "Drag": 2, "Orientation": "VelocityParallel", "ZOffset": 0.6}})
        out.append(embers([0, 2.0, z0], 0, rate=[[t0, t1, 60 * scale]], speed=(22, 34), life=(0.35, 0.6), grav=-2, spread=8,
                          part=[width, 3, 1], seed=seed + 41, direction=[-90, 0, 0], move=mv))
        # black smoke shoved ahead of the front
        out.append(smoke([0, 3.0, z0], 0, rate=[[t0 + 0.04, t1, 14 * scale]], size=(3.5, 7), speed=(6, 10), life=(0.7, 1.1), seed=seed + 42,
                         part=[width * 0.8, 1.5, 1], direction=[-90, 0, 0], spread=20, move=mv))
        return out

    L += wall(TC, 0.86, -1.5, -14.0, 14.0, 221)
    L += wall(T2, 0.95, -2.5, -11.0, 10.0, 271, scale=0.6)

    # ---- contact: impacts on both targets, their slide, the wall tearing into tongues as it dies
    hits, numbers = [], []
    for i, p in enumerate(TARGETS):
        L += impact([p[0], 3.2, p[2] + 1.2], TH + 0.005 * i, size=5.5, life=0.4, seed=301 + i)
        L.append(embers([p[0], 3, p[2]], TH, n=14, speed=(10, 22), life=(0.4, 0.8), grav=-14, seed=303 + i))
        hits.append({"t": TH + 0.005 * i, "dummy": i, "dir": [0.15 * (1 if p[0] > 0 else -1), 0, -1], "power": 0.85})
        numbers.append({"t": TH + 0.02, "at": [p[0] + 1.2, 6.4, p[2]], "text": str(72 + 9 * i), "color": GOLD, "vel": [0, 9, -2], "size": 1.6})
    for j in range(9):
        x = (j - 4) * 1.6
        L += tongue([x, 0, -13.2 - 0.4 * (j % 3)], 0.84 + 0.02 * j, 3.2 + 0.5 * (j % 2), life=0.55, seed=311 + j)
    # the sand wedge blown forward
    L.append({"type": "emitter", "at": [0, 0.9, -6], "part": [12, 0.6, 8], "emits": [[0.42, 18]], "seed": 330, "rot": [-90, 0, 0], "props": {
        "Texture": "smoke_cel_v3", "Color": SAND_DUST, "LightEmission": 0, "Brightness": 1, "Size": [[0, 3], [1, 7]],
        "Lifetime": [0.8, 1.2], "Speed": [20, 30], "SpreadAngle": [12, 4], "Drag": 4, "Acceleration": [0, 1.2, 0], "Rotation": [-20, 20],
        "Transparency": [[0, 0.1], [0.7, 0.3], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot", "Orientation": "FacingCameraWorldUp", "ZOffset": -0.5}})
    # scorched lane left on the sand
    L.append(scorch([0, 0, -8], 0.6, size=13, life=2.0, seed=331, rot=90))

    return {
        "name": "dragon_02_HornRush", "title": "Horn Rush", "element": "Dragon", "archetype": "charge_wall", "duration": DUR,
        "layers": L, "dummies": TARGETS, "hits": hits, "numbers": numbers,
        "hitstop": [{"t": TH + 0.025, "dur": 0.06}],
        "shakes": [{"t": TC, "amp": 0.3, "dur": 0.25, "freq": 20}, {"t": TH, "amp": 0.35, "dur": 0.3, "freq": 22}],
        "lights": [light([0, 3, -4], [[0, 0], [TC, 10], [TC + 0.05, 36], [0.8, 18], [1.2, 0]], rng=20,
                         path=[[0, [0, 3, -1]], [0.86, [0, 3, -13]]])],
        "pose": POSE,
        "camera": {"pos": [[0, [4.0, 4.2, 9.0]], [TC / DUR, [4.2, 4.0, 8.0]], [TC / DUR + 0.06, [3.2, 3.8, 3.0], "outExpo"], [1, [3.6, 4.4, 2.0]]],
                   "look": [[0, [0, 2.8, -4]], [TC / DUR + 0.06, [0, 2.6, -9], "outExpo"], [1, [0, 2.4, -10]]],
                   "fov": [[0, 56], [TC / DUR, 54], [TC / DUR + 0.02, 62, "out"], [0.6, 57]]},
        "poster": TH + 0.03,
    }


write(build(), out_path(os.path.dirname(__file__), "dragon_02_HornRush"), form="hybrid")
print("wrote dragon_02_HornRush.json")
