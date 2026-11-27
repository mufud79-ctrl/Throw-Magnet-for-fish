"""Horn Rush (hybrid X) - a short horns-first charge that shoves. Signature: a WALL of flame-wind (a broad arch of
fire 14 studs wide with tongues standing on its front) that rolls forward along the ground ahead of the charge, gust
lines and embers streaming past it - the only move whose shape is a wide wall moving away from you.

Beat sheet (fluid: spline poses, the head leads, the body follows, the arms trail)
  0.00-0.30  crouch, head lowered, horns heat up (a swirl + wisps at the head), gust needles and embers are pulled
             in, dust creeps in                                                         (anticipation, squash)
  0.30       CHARGE: the caster lunges 5 studs head-first (stretch); a glint flashes at the horns; the wall is born
  0.30-0.86  the wall rolls 0 -> 14 studs ahead and slows (ease-out): flame arch front + standing tongues, a row of
             rolling billows behind it, a flame wash on the sand, gust lines streaming forward, black smoke shoved
             ahead of it
  0.46       contact: both targets slide back with the wall; hit-stop 0.06; ember sprays + glints on them
  0.56       a thinner second wall rides in behind the first                            (follow-through)
  0.86-1.50  the wall tears into tongues and dies; a wedge of sand dust blows forward; flickers burn on the scorched
             lane; after-smoke rises; the caster settles out of the lunge               (follow-through)
Camera: fixed gameplay view (behind / above / right).
Run: python3 lab/dragon/moves/horn_rush.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa
from kit import _keys, _fb

TC, TH, T2 = 0.30, 0.46, 0.56
DUR = 1.5
TARGETS = [[-3.2, 0, -11.0], [3.2, 0, -12.0]]

POSE = {
    "lean": smooth([[0, 0], [0.18, -10], [0.28, -16], [TC, -14], [TC + 0.06, -40], [0.5, -34], [0.75, -26], [1.05, -8], [1.35, 0], [DUR, 0]]),
    "armR": smooth([[0, 0], [0.2, -35], [TC, -45], [TC + 0.07, -80], [0.55, -70], [0.85, -40], [1.3, 0], [DUR, 0]]),
    "armL": smooth([[0, 0], [0.2, -35], [TC, -45], [TC + 0.07, -80], [0.55, -70], [0.85, -40], [1.3, 0], [DUR, 0]]),
    "armRz": smooth([[0, 0], [0.2, 22], [TC + 0.07, 34], [0.85, 20], [1.3, 0], [DUR, 0]]),
    "armLz": smooth([[0, 0], [0.2, -22], [TC + 0.07, -34], [0.85, -20], [1.3, 0], [DUR, 0]]),
    "offset": smooth([[0, [0, 0, 0]], [0.2, [0, -0.45, 0.35]], [TC, [0, -0.55, 0.45]], [TC + 0.1, [0, 0.1, -4.4]], [0.5, [0, -0.1, -5.4]],
                      [0.75, [0, 0, -5.6]], [1.2, [0, 0, -5.5]], [DUR, [0, 0, -5.5]]]),
    "scale": smooth([[0, [1, 1, 1]], [0.2, [1.06, 0.9, 1.06]], [TC, [1.09, 0.87, 1.09]], [TC + 0.06, [0.9, 1.1, 0.95]],
                     [0.52, [1.03, 0.97, 1.03]], [0.75, [1, 1, 1]], [DUR, [1, 1, 1]]]),
}


def head(t):
    """Head position of the previewer avatar (FK of the upper body, like kit.hand)."""
    lean = _keys(POSE["lean"], t, 0) * math.pi / 180
    v = [0, 2.6, -0.2]
    c, s = math.cos(lean), math.sin(lean)
    v = [v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c]
    sc = _keys(POSE["scale"], t, [1, 1, 1]); off = _keys(POSE["offset"], t, [0, 0, 0])
    return [v[0] * sc[0] + off[0], (v[1] + 2) * sc[1] + off[1], v[2] * sc[2] + off[2]]


def head_path(t0, t1, step=1 / 60, dx=0.0, dy=0.0):
    n = max(2, int((t1 - t0) / step))
    out = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        p = head(t)
        out.append([R(t, 4), R([p[0] + dx, p[1] + dy, p[2]])])
    return out


def wall(t0, t1, z0, z1, width, seed, scale=1.0):
    out = []
    mv = lambda y, dx=0.0: {"from": [dx, y, z0], "to": [dx, y, z1], "t0": t0, "t1": t1, "ease": "out"}
    # the front: one big flame arch (fire_crescent turned to open toward the caster), re-born every few frames
    # the front on the ground: a wide flame arc laid flat, bowing forward (seen from behind/above it reads as a curved
    # wave front rolling away)
    out += emit_stack("fire_crescent", [0, 0.35, z0], t0, size=[[0, width * 1.25], [1, width * 1.4]], life=0.26, rate=[[t0, t1 - 0.1, 12]],
                      rot=90, seed=seed, move=mv(0.35), locked=True, z=0.1, orient="VelocityPerpendicular",
                      transparency=[[0, 0.05], [0.6, 0.15], [1, 1]])
    # tongues standing on the front, riding it
    # the wall itself: ONE fused curtain of fire (flame_wall Beams), bowing forward, growing up on the charge and
    # dying down at the end; it rides the front
    life = t1 - t0 + 0.12
    k1 = (t1 - t0) / life
    zk = lambda z: [[0, z], [k1 * 0.35, z + (z1 - z0) * 0.7], [k1, z1 + (z1 - z0) * 0.0], [1, z1 - 0.6]]
    hmax = 7.0 * scale
    frm = [[k, [-width * 0.5, hmax * 0.5, z]] for k, z in zk(z0)]
    to = [[k, [width * 0.5, hmax * 0.5, z]] for k, z in zk(z0)]
    hk = [[0, hmax * 0.25], [0.12, hmax, "out"], [k1 * 0.8, hmax], [1, hmax * 0.15, "in"]]
    out += wall_beam(frm, to, t0, life, hk, bow=[0, 0, -1.6 * scale], tlen=12 * scale)
    # ANIME CREST: sharp flame spikes erupting along the wall's front edge as it rolls (the lead shape: a charging wall
    # of spikes), plus warm translucent haze pushed ahead of it
    for e in emit_stack("anime_flame_spike", [0, hmax * 0.42, z0], t0 + 0.02, size=[[0, hmax * 0.9], [1, hmax * 1.05]], life=0.3,
                        rate=[[t0 + 0.02, t1 - 0.12, 34 * scale]], cool=False, seed=seed + 60, orient="FacingCameraWorldUp", z=0.2, locked=True,
                        transparency=[[0, 0], [0.6, 0.1], [1, 1]]):
        e["move"] = mv(hmax * 0.42)
        e["part"] = [width * 0.9, 0.5, 0.6]
        e["props"]["Rotation"] = [-12, 12]
        out.append(e)
    out.append({"type": "emitter", "at": [0, 2.5, z0], "rate": [[t0, t1, 16 * scale]], "seed": seed + 61, "part": [width * 0.9, 1.5, 1],
                "move": mv(2.5), "props": {"Texture": "haze_soft", "Color": [[0, "#ff9a3a"], [1, "#ff5a1e"]], "LightEmission": 0.7,
        "Brightness": 1, "Size": [[0, 5 * scale], [1, 10 * scale]], "Lifetime": [0.7, 1.0], "Speed": [3, 6], "SpreadAngle": [40, 40],
        "Drag": 1.5, "Rotation": [0, 360], "RotSpeed": [-8, 8], "FlipbookLayout": "None",
        "Transparency": [[0, 1], [0.15, 0.68], [0.6, 0.78], [1, 1]], "ZOffset": -1.0}})
    # rolling billows dropped behind the front (they stay where they're born: the wall leaves fire behind it)
    for j in range(5):
        dx = (j - 2) / 2 * width * 0.38
        for e in billow([dx, 1.4, z0], t0, 3.6 * scale, life=0.5, seed=seed + 20 + j, move=mv(1.4, dx), rot=40 * j, grow=1.3):
            e.pop("emits", None); e["rate"] = [[t0, t1 - 0.05, 6]]
            out.append(e)
    # flame wash on the sand behind the front
    out += trail_stack({"move": mv(0.15), "at": [0, 0.15, z0], "t0": t0 + 0.07, "t1": t1, "lifetime": 0.3, "up": [1, 0, 0],
                        "transparency": [[0, 0.35], [0.5, 0.6], [1, 1]], "widthScale": [[0, 1], [1, 0.4]], "textureMode": "Wrap", "textureLength": 8},
                       {"rim": width * 0.55, "mid": width * 0.36, "core": width * 0.06}, layers=("rim", "mid", "core"))
    out.append(glow_pool([0, 0, z0], t0, width * 0.9, life=0.35, rate=[[t0, t1, 12]], peak=0.4, seed=seed + 30,
                         path=[[t0, [0, 0, z0]], [t0 + (t1 - t0) * 0.35, [0, 0, z0 + (z1 - z0) * 0.7]], [t1, [0, 0, z1]]]))
    # gust lines + needles + embers streaming forward past the front
    out.append({"type": "emitter", "at": [0, 2.0, z0], "part": [width, 3.5, 1], "rate": [[t0, t1, 60 * scale]], "seed": seed + 40,
                "move": mv(2.0), "rot": [-90, 0, 0], "props": {
        "Texture": "spark_streak", "Color": PALS["fire"]["spark"], "LightEmission": 1, "Brightness": 1.6, "Size": [[0, 5], [0.7, 3], [1, 0.3]],
        "Lifetime": [0.16, 0.26], "Speed": [55, 75], "SpreadAngle": [3, 3], "Drag": 2, "Orientation": "VelocityParallel", "ZOffset": 0.6}})
    out.append(embers([0, 2.0, z0], 0, rate=[[t0, t1, 60 * scale]], speed=(22, 34), life=(0.35, 0.6), grav=-2, spread=8,
                      part=[width, 3, 1], seed=seed + 41, direction=[-90, 0, 0], move=mv(2.0)))
    out += wisps([0, 3.0, z0], t0, t1, 14 * scale, size=2.6, life=0.45, seed=seed + 43, rots=(-30, 30))
    for e in out[-6:]:
        e["move"] = mv(3.0)
        e["part"] = [width * 0.8, 1.5, 1]
    out.append({"type": "emitter", "at": [0, 3.6, z0 + 1.0], "rate": [[t0 + 0.04, t1, 10 * scale]], "seed": seed + 42, "part": [width * 0.8, 1.5, 1],
                "move": mv(3.6), "props": {"Texture": "haze_soft", "Color": [[0, "#4a2a22"], [1, "#6a4a3e"]], "LightEmission": 0, "Brightness": 1,
        "Size": [[0, 4 * scale], [1, 9 * scale]], "Lifetime": [0.8, 1.2], "Speed": [2, 4], "SpreadAngle": [30, 30], "Acceleration": [0, 2.5, 0],
        "Drag": 1.2, "Rotation": [0, 360], "RotSpeed": [-10, 10], "FlipbookLayout": "None",
        "Transparency": [[0, 1], [0.15, 0.55], [0.6, 0.7], [1, 1]], "ZOffset": -1.2}})
    return out


def build():
    L = [ambience([0, 0, -7], 0, DUR, radius=10, rate=9, seed=201)]
    hp = head_path(0.0, 1.2)
    # ---- anticipation: horns heat up (swirl + glow + small flames + wisps), needles + embers pulled in, dust creeps in
    L.append(glow_orb(hp[0][1], 0, 3.4, life=0.2, rate=[[0.05, 1.0, 14]], path=hp, locked=True, tr=0.45, seed=203))
    for dx, sd in ((-0.5, 204), (0.5, 206)):
        hpx = head_path(0.0, 1.2, dx=dx, dy=0.6)
        L += flicker(hpx[0][1], 0.06, 1.0, 1.5, path=hpx, seed=sd)
    L += wisps(hp[0][1], 0.05, 1.1, 14, size=2.0, life=0.4, path=hp, seed=208)
    L.append({"type": "emitter", "at": [0, 3.4, 0.6], "part": [8, 5, 6], "rate": [[0.02, TC - 0.03, 36]], "seed": 210, "props": {
        "Texture": "spark_streak", "Color": PALS["fire"]["spark"], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "Size": [[0, 1.8], [1, 0.4]], "Lifetime": [0.13, 0.17], "Speed": [22, 28], "Orientation": "VelocityParallel",
        "Transparency": [[0, 0.3], [1, 0.8]], "ZOffset": 0.3}})
    L.append(glow_pool([0, 0, 0], 0, 6, life=0.3, rate=[[0.02, TC, 8]], peak=0.25, seed=211))

    # ---- the charge: glint + flare at the horns, a smear of the lunge, black smoke and dust kicked up behind
    h0 = head(TC + 0.03)
    L.append(flare(h0, TC + 0.01, size=10, life=0.18, seed=213))
    L += smear([0, 3.2, -1.6], TC + 0.01, 8, 90, life=0.2, seed=214)
    L.append(dust_ring([0, 0, 0.6], TC + 0.01, n=7, speed=(14, 20), size=(1.6, 3.2), seed=216, life=(0.35, 0.5)))

    # ---- the walls
    L += wall(TC, 0.86, -1.8, -14.5, 14.0, 221)
    L += wall(T2, 0.95, -2.8, -11.5, 10.0, 271, scale=0.65)

    # ---- contact: impacts, sprays and glints on both targets
    hits, numbers = [], []
    for i, p in enumerate(TARGETS):
        th = TH + 0.006 * i
        hp_ = [p[0], 3.2, p[2] + 1.2]
        L += glint([hp_[0], hp_[1] + 0.4, hp_[2] + 0.3], th, size=4.5, life=0.2, seed=301 + i)
        sh = emit_stack("ink_shards", hp_, th + 0.015, size=[[0, 5], [1, 6.5]], life=0.26, cool=False, seed=303 + i, rot=30 * i, layers=("rim",), z=0.7)
        for e in sh:
            e["props"]["Color"] = "#1a0806"; e["props"]["LightEmission"] = 0
        L += sh
        L.append({"type": "emitter", "at": hp_, "emits": [[th + 0.02, 12]], "seed": 309 + i, "props": {
            "Texture": "needle_bold", "Color": [[0, "#fff6b0"], [0.5, "#ffd21a"], [1, "#ff6a10"]], "LightEmission": 1, "Brightness": 1.5,
            "Size": [[0, 3.2], [1, 0.3]], "Lifetime": [0.14, 0.24], "Speed": [40, 70], "SpreadAngle": [60, 60], "Drag": 7,
            "Orientation": "VelocityParallel", "ZOffset": 0.6}})
        L.append(glow_pool([p[0], 0, p[2]], th, 6, life=0.4, peak=0.45, seed=307 + i))
        hits.append({"t": th, "dummy": i, "dir": [0.15 * (1 if p[0] > 0 else -1), 0, -1], "power": 0.85})
        numbers.append({"t": th + 0.02, "at": [p[0] + 1.2, 6.4, p[2]], "text": str(72 + 9 * i), "color": GOLD, "vel": [0, 9, -2], "size": 1.6})
    L += aura_haze([0, 0, -10.5], TH, 1.2, radius=7.0, height=5.0, strength=0.9, seed=360, cloud=0.5)   # OUTSIDE
    # the wall tears into tongues as it dies
    for j in range(9):
        L += tongue([(j - 4) * 1.6, 0, -13.8 - 0.4 * (j % 3)], 0.84 + 0.02 * j, 3.2 + 0.5 * (j % 2), life=0.55, seed=311 + j)
    # the sand wedge blown forward
    L.append({"type": "emitter", "at": [0, 0.9, -6], "part": [12, 0.6, 8], "emits": [[0.42, 18]], "seed": 330, "rot": [-90, 0, 0], "props": {
        "Texture": "smoke_cel_v3", "Color": SAND_DUST, "LightEmission": 0, "Brightness": 1, "Size": [[0, 3], [1, 7]],
        "Lifetime": [0.8, 1.2], "Speed": [20, 30], "SpreadAngle": [12, 4], "Drag": 4, "Acceleration": [0, 1.2, 0], "Rotation": [-20, 20],
        "Transparency": [[0, 0.35], [0.7, 0.55], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot", "Orientation": "FacingCameraWorldUp", "ZOffset": -0.5}})
    # the scorched lane: char decal, flickers along it, after-smoke, shimmer
    L.append(scorch([0, 0, -8.5], 0.55, size=13, life=2.0, seed=331, rot=90))
    for k in range(5):
        L += flicker([(k % 2 - 0.5) * 2.4, 0, -4.5 - 2.2 * k], 0.5 + 0.06 * k, 1.35, 1.3 + 0.3 * (k % 2), seed=341 + k)
    L.append(smoke_wisps([0, 0.4, -8.5], 0.8, DUR, 8, size=3.5, part=[4, 0.2, 10], seed=350))

    return {
        "name": "dragon_02_HornRush", "title": "Horn Rush", "element": "Dragon", "archetype": "charge_wall", "duration": DUR,
        "layers": L, "dummies": TARGETS, "hits": hits, "numbers": numbers,
        "hitstop": [{"t": TH + 0.025, "dur": 0.06}],
        "shakes": [{"t": TC, "amp": 0.2, "dur": 0.2, "freq": 20}, {"t": TH, "amp": 0.3, "dur": 0.25, "freq": 22}],
        "lights": [light([0, 3, -4], [[0, 0], [TC, 10], [TC + 0.05, 36], [0.8, 18], [1.2, 0]], rng=20,
                         path=[[0, [0, 3, -1]], [0.86, [0, 3, -13]]])],
        "pose": POSE,
        "camera": follow_cam(POSE, DUR),
        "poster": TH + 0.03,
    }


write(build(), out_path(os.path.dirname(__file__), "dragon_02_HornRush"), form="hybrid")
print("wrote dragon_02_HornRush.json")
