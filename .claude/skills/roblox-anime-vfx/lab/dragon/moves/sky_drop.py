"""Sky Drop (hybrid C) - leap and claw dive (gap-closer + AoE slam). Signature: a RING OF STANDING FLAMES around a
crater with radial molten cracks (the slam calling card).

Beat sheet (fluid: spline arc for the leap, eased dive, squash on landing)
  0.00-0.15  crouch (squash), heat gathers at the feet, sand creeps in                  (anticipation)
  0.15       LEAP: a flame burst + dust ring under the feet; the body stretches; two flame ribbons spiral up around
             the rising body (it rides a spiral of flame); a second burst at 0.35 (a mid-air boost)    (arcs)
  0.75-0.90  apex hang 16 studs up / 10 ahead: arms rise, body tips forward, claws ignite (swirls + flames) (anticipation)
  0.90-1.05  DIVE: stretched, a fire trail and streaks behind, a vertical smear           (squash & stretch)
  1.05       IMPACT: one mono frame; hit-stop 0.15; crater + molten cracks; a fire ring races out to 9 studs; a
             ring of flame tongues stands up all around it; black smoke column; three targets launched
  1.05-2.20  the caster rises out of the crouch; the flame ring burns down; cracks cool; smoke rolls up; after-smoke,
             flickers, ash                                                            (follow-through)
Camera: gameplay follow camera (tracks the player, half the height of the jump).
Run: python3 lab/dragon/moves/sky_drop.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa
from kit import _keys

TL, TB2, TA, TD, TI = 0.15, 0.35, 0.75, 0.90, 1.05
LAND = [0, 0, -10]
DUR = 2.2
TARGETS = [[-4.5, 0, -12.5], [4.6, 0, -11.5], [0.6, 0, -15.6]]

_rise = smooth([[0, [0, 0, 0]], [0.1, [0, -0.45, 0.2]], [TL, [0, -0.5, 0.2]], [0.32, [0, 7.5, -3.2]], [0.5, [0, 12.5, -6.2]],
                [TA, [0, 16.0, -9.2]], [TD, [0, 16.6, -10.0]]])
OFFSET = _rise + [[0.97, [0, 9.0, -10.0]], [TI, [0, -0.35, -10.0]], [TI + 0.1, [0, -0.6, -10.0]], [1.5, [0, -0.1, -10.0]],
                  [1.8, [0, 0, -10.0]], [DUR, [0, 0, -10.0]]]
POSE = {
    "offset": OFFSET,
    "lean": smooth([[0, 0], [TL, -18], [0.3, 8], [0.6, 4], [TA, -20], [TD, -48], [TI, -55], [TI + 0.12, -30], [1.5, -8], [1.9, 0], [DUR, 0]]),
    "armR": smooth([[0, 0], [TL, -40], [0.3, 30], [0.6, 60], [TA, 175], [TD, 185], [TI, 95], [TI + 0.15, 70], [1.6, 20], [2.0, 0], [DUR, 0]]),
    "armL": smooth([[0, 0], [TL, -40], [0.3, 30], [0.6, 60], [TA, 175], [TD, 185], [TI, 95], [TI + 0.15, 70], [1.6, 20], [2.0, 0], [DUR, 0]]),
    "armRz": smooth([[0, 0], [TL, 30], [0.4, 40], [TA, 25], [TI, 18], [1.6, 8], [DUR, 0]]),
    "armLz": smooth([[0, 0], [TL, -30], [0.4, -40], [TA, -25], [TI, -18], [1.6, -8], [DUR, 0]]),
    "scale": [[0, [1, 1, 1]], [0.12, [1.1, 0.86, 1.1]], [TL, [1.1, 0.86, 1.1]], [TL + 0.06, [0.88, 1.18, 0.88], "out"], [0.45, [1, 1, 1]],
              [TD, [1, 1, 1]], [TD + 0.05, [0.85, 1.25, 0.85], "out"], [TI, [0.86, 1.22, 0.86]], [TI + 0.03, [1.22, 0.78, 1.22], "outExpo"],
              [TI + 0.2, [0.97, 1.04, 0.97]], [TI + 0.4, [1, 1, 1]], [DUR, [1, 1, 1]]],
}


def body(t, y=2.6):
    o = _keys(OFFSET, t, [0, 0, 0])
    return [o[0], o[1] + y, o[2]]


def body_path(t0, t1, y=2.6, step=1 / 60):
    n = max(2, int((t1 - t0) / step))
    return [[R(t0 + (t1 - t0) * i / n, 4), R(body(t0 + (t1 - t0) * i / n, y))] for i in range(n + 1)]


def build():
    L = [ambience([0, 0, -7], 0, DUR, radius=11, rate=9, seed=501)]
    # ---- crouch: heat at the feet, sand pulled in
    L.append(glow_pool([0, 0, 0], 0, 6, life=0.2, rate=[[0.0, TL, 10]], peak=0.3, seed=502))
    L.append({"type": "emitter", "at": [0, 0.6, 0], "part": [7, 0.4, 7], "rate": [[0.0, TL - 0.02, 30]], "seed": 503, "props": {
        "Texture": "spark_streak", "Color": PALS["fire"]["spark"], "LightEmission": 1, "Brightness": 1.4, "Shape": "Cylinder", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "Size": [[0, 1.4], [1, 0.4]], "Lifetime": [0.12, 0.16], "Speed": [18, 22], "Orientation": "VelocityParallel",
        "Transparency": [[0, 0.3], [1, 0.8]], "ZOffset": 0.3}})

    # ---- the leap: two flame bursts under the feet, dust ring, spiral flame ribbons around the rising body
    for t, seed in ((TL, 511), (TB2, 515)):
        f = body(t, 0.2)
        L += billow([f[0], f[1] + 0.8, f[2]], t, 5.0, life=0.5, seed=seed, grow=1.4)
        L += ember_spray([f[0], f[1] + 0.5, f[2]], t, size=6, life=0.45, seed=seed + 1)
        L += glint([f[0], f[1] + 0.6, f[2]], t, size=4, life=0.18, seed=seed + 2)
    L.append(dust_ring([0, 0, 0], TL + 0.01, n=10, speed=(22, 30), size=(2.5, 5.5), seed=518))
    L.append(dust_rollout([0, 0, 0], TL + 0.01, n=6, size=(8, 13), speed=(9, 14), seed=517))
    L.append(scorch([0, 0, 0], TL, size=6, life=2.0, seed=519))
    L.append(smoke([0, 0.6, 0], TL + 0.04, n=4, size=(3, 6), speed=(2, 5), life=(0.9, 1.3), seed=520))
    for k, ph in enumerate((0.0, math.pi)):
        sp = []
        n = 36
        for i in range(n + 1):
            u = i / n
            t = TL + (TA - TL) * u
            c = body(t, 1.8)
            a = ph + u * 2.2 * 2 * math.pi
            r = 1.6 + 0.8 * math.sin(u * math.pi)
            sp.append([R(t, 4), R([c[0] + math.cos(a) * r, c[1] - 0.8 * (1 - u), c[2] + math.sin(a) * r])])
        hot = {"rim": [[0, CRIMSON], [0.6, CRIMSON], [1, EMBER]], "mid": [[0, GOLD], [0.5, ORANGE], [1, CRIMSON]], "core": [[0, WHITE_GOLD], [0.4, GOLD], [1, ORANGE]]}
        for lay, w in (("rim", 1.3), ("mid", 0.85), ("core", 0.26)):
            L.append({"type": "trail", "path": sp, "at": sp[0][1], "t0": TL, "t1": TA, "lifetime": 0.32, "faceCamera": True, "width": w,
                      "textures": [f"{s}_{lay}" for s in STRIPS], "swap": 0.06, "color": hot[lay], "lightEmission": LE[lay], "brightness": BR[lay],
                      "textureMode": "Stretch", "transparency": [[0, 0], [0.5, 0.1], [1, 1]], "widthScale": [[0, 1], [1, 0.2]]})
        L += wisps(sp[0][1], TL, TA, 14, size=2.2, life=0.4, path=sp, seed=531 + k * 3)
    # body fire riding the leap
    bp = body_path(0.1, TI + 0.02, 2.6)
    L.append(glow_orb(bp[0][1], 0, 5, life=0.2, rate=[[TL, TI, 14]], path=bp, locked=True, tr=0.55, seed=540))

    # ---- apex: claws ignite (swirls + flickers on both hands), embers pulled in
    for side, seed in (("R", 551), ("L", 561)):
        hp = hand_path(POSE, 0.5, TI + 0.03, side, reach=2.05)
        L += swirl(hp[0][1], TA - 0.12, TD + 0.02, 3.4, path=hp, seed=seed)
        L += flicker(hp[0][1], TA - 0.1, TI + 0.02, 2.2, path=hp, seed=seed + 4)
        hpc = hand_path(POSE, TA - 0.05, TI + 0.02, side, step=1 / 120, reach=2.3)
        L += trail_stack({"path": hpc, "at": hpc[0][1], "t0": TA - 0.05, "t1": TI - 0.03, "lifetime": 0.1, "faceCamera": True,
                          "transparency": [[0, 0], [0.5, 0.2], [1, 1]], "widthScale": [[0, 1], [1, 0.2]], "textureMode": "Stretch"},
                         {"rim": 1.0, "mid": 0.65, "core": 0.2}, layers=("rim", "mid", "core"), cool=False)

    # ---- the dive: fire trail behind the body, streaks, a vertical smear
    dp = body_path(TD, TI, 3.0, step=1 / 120)
    L += trail_stack({"path": dp, "at": dp[0][1], "t0": TD, "t1": TI, "lifetime": 0.11, "faceCamera": True,
                      "transparency": [[0, 0], [0.5, 0.2], [1, 1]], "widthScale": [[0, 1], [1, 0.3]], "textureMode": "Stretch"},
                     {"glow": 4.0, "rim": 2.6, "mid": 1.7, "core": 0.5}, cool=False)
    L.append({"type": "emitter", "at": body(TD, 3), "rate": [[TD, TI, 80]], "seed": 571, "path": dp, "rot": [180, 0, 0], "props": {
        "Texture": "spark_streak", "Color": PALS["fire"]["spark"], "LightEmission": 1, "Brightness": 1.6, "Size": [[0, 4.5], [1, 0.4]],
        "Lifetime": [0.12, 0.2], "Speed": [8, 14], "SpreadAngle": [12, 12], "Drag": 3, "Orientation": "VelocityParallel", "ZOffset": 0.5}})
    L += smear(body(0.97, 3.5), TD + 0.04, 9, -90, life=0.16, seed=572)

    # ---- IMPACT (BIG): crater + molten cracks, fire ring, standing flame ring, smoke column, mass, fillers
    T = TI
    g = [LAND[0], 0, LAND[2]]
    L += impact([g[0], 2.0, g[2]], T + 0.005, size=11, life=0.55, seed=581)
    L.append(flare([g[0], 1.8, g[2]], T + 0.005, size=16, life=0.22, seed=582))
    L.append(streaks([g[0], 1.0, g[2]], T + 0.01, 14, speed=(60, 100), length=(2.5, 5), spread=60, seed=585))
    L.append(dust_ring(g, T + 0.015, n=16, speed=(32, 44), size=(3.5, 8), seed=588))
    L.append(dust_rollout(g, T + 0.02, radius=4, n=12, size=(12, 20), speed=(14, 22), seed=592))
    L += dark_spikes([g[0], 2.2, g[2]], T + 0.02, size=16, life=0.32, seed=597)
    L.append(fire_scraps([g[0], 2.0, g[2]], T + 0.02, n=22, speed=(16, 30), seed=598))
    # the flow shape (reference): big flame streams whirl out of the landing and wrap the crater
    # thin hot swirl lines over the red streams (crisp yellow lines on red haze, as in the references)
    for k in range(6):
        ph = k / 6 * 2 * math.pi + 0.4
        sp = []
        for i in range(41):
            u = i / 40
            aa = ph + 1.1 * 2 * math.pi * u ** 0.8
            r = 1.2 + 8.0 * (1 - (1 - u) ** 2)
            sp.append([R(T + 0.02 + 0.4 * u, 4), R([g[0] + math.cos(aa) * r, 0.35 + 0.6 * u, g[2] + math.sin(aa) * r])])
        for lay, w, col in (("mid", 0.32, [[0, "#fff2a0"], [0.5, "#ffc81e"], [1, "#ff7a10"]]), ("core", 0.12, [[0, "#ffffff"], [0.5, "#fff2a0"], [1, "#ffc81e"]])):
            L.append({"type": "trail", "path": sp, "at": sp[0][1], "t0": T + 0.02, "t1": T + 0.42, "lifetime": 0.32, "faceCamera": True,
                      "width": w, "textures": [f"{st}_{lay}" for st in STRIPS], "swap": 0.06, "color": col, "lightEmission": 1,
                      "brightness": 1.4, "textureMode": "Stretch", "transparency": [[0, 0], [0.6, 0.2], [1, 1]], "widthScale": [[0, 1], [1, 0.2]]})
    # a brief hot heart at the centre of the impact
    L.append(glow_orb([g[0], 1.6, g[2]], T + 0.01, 7, life=0.45, tr=0.15, seed=596))
    L[-1]["props"]["Color"] = "#ffe070"; L[-1]["props"]["LightEmission"] = 1
    # the flow shape: a spiral of fire whirling out on the ground from the landing (flat fire_swirl, two counter-turning)
    for j, (sz, rot) in enumerate(((24, 0), (16, 70))):
        for e in emit_stack("fire_swirl", [g[0], 0.3 + 0.05 * j, g[2]], T + 0.01, size=[[0, sz * 0.5], [0.25, sz], [1, sz * 1.15]], life=0.75,
                            cool=False, mode="Loop", fps=26, seed=593 + j, rot=rot, orient="VelocityPerpendicular",
                            transparency=[[0, 0], [0.6, 0.15], [1, 1]]):
            L.append(e)
    L.append(glow_pool(g, T, 18, life=1.2, peak=0.5, seed=589))
    L += molten_crack(g, T + 0.01, size=17, rot=20, glow_life=1.6, char_life=3.2, seed=590)
    L.append(scorch(g, T + 0.3, size=12, life=2.2, seed=591))
    # the ring of standing flames (signature): tongues stand up all around the ring for ~1 s, then burn down
    # the ring of fire (signature): ONE continuous curtain drawn around the crater in 0.12 s, then a lower ring as it
    # burns down - fused fire, never separate tongues
    L += ring_wall(g, 8.4, T + 0.05, 0.95, 5.2, sweep=0.12, start=0.3, fade=[[0, 0], [0.75, 0.05], [1, 1]])
    L += ring_wall(g, 8.6, T + 0.72, 0.6, 2.6, sweep=0.1, start=2.0, reverse=True, fade=[[0, 0.1], [0.6, 0.3], [1, 1]])
    L.append(glow_pool(g, T + 0.1, 20, life=0.6, rate=[[T + 0.1, T + 1.0, 4]], peak=0.25, seed=661, hold=0.4))
    # black smoke column rolling up, after-smoke, shimmer, ash
    L.append(smoke([g[0], 1.5, g[2]], 0, rate=[[T + 0.06, T + 0.5, 22]], size=(5, 11), speed=(6, 11), life=(1.2, 1.8), seed=662,
                   part=[5, 1, 5], spread=25, rise=4))
    L.append(smoke_wisps([g[0], 0.4, g[2]], T + 0.4, DUR, 10, size=4, part=[16, 0.2, 16], seed=663))
    L.append(haze([g[0], 5.0, g[2]], T, DUR, size=18, seed=664))
    L.append(ash([g[0], 9, g[2]], T + 0.2, DUR, 16, part=(18, 3, 18), seed=665))
    debris = rocks(g, T + 0.01, radius=6.0, count=9, size=0.9, speed=28, seed=666)

    hits, numbers = [], []
    for i, p in enumerate(TARGETS):
        th = T + 0.03 + 0.01 * i
        d = [p[0] - g[0], 0, p[2] - g[2]]
        n = math.hypot(d[0], d[2]) or 1
        L += impact([p[0], 3.0, p[2]], th, size=5, life=0.4, seed=671 + i)
        L += wisps([p[0], 3.0, p[2]], th, th + 0.7, 10, size=2.2, life=0.45, seed=681 + 3 * i)
        hits.append({"t": th, "dummy": i, "dir": [R(d[0] / n), 0, R(d[2] / n)], "power": 1.1})
        numbers.append({"t": th + 0.02, "at": [p[0] + 1.0, 6.6, p[2]], "text": str(118 + 11 * i), "color": WHITE_GOLD, "vel": [R(d[0] / n * 2), 10, R(d[2] / n * 2)], "size": 1.8})

    fx = {
        "name": "dragon_03_SkyDrop", "title": "Sky Drop", "element": "Dragon", "archetype": "leap_slam", "duration": DUR,
        "layers": L, "dummies": TARGETS, "hits": hits, "numbers": numbers, "debris": debris,
        "hitstop": [{"t": T + 0.025, "dur": 0.15}],
        "impact": [{"t": T + 0.025, "dur": 0.05, "mode": "mono"}],
        "shakes": [{"t": TL, "amp": 0.15, "dur": 0.15, "freq": 20}, {"t": T, "amp": 0.75, "dur": 0.45, "freq": 22}],
        "lights": [light([0, 2, 0], [[0, 0], [TL, 20], [TA, 10], [TI, 14]], rng=16, path=body_path(0, TI, 2.6, step=0.05)),
                   light([g[0], 3, g[2]], [[T, 0], [T + 0.01, 44], [T + 0.4, 24], [T + 1.0, 8], [DUR, 0]], rng=24)],
        "pose": POSE,
        "camera": follow_cam(POSE, DUR, y_follow=0.8, base={"pos": [[0, [8.5, 9.0, 11.0]]], "look": [[0, [-1.0, 2.6, -7.0]]], "fov": GAMEPLAY_CAM["fov"]}),
        "poster": T + 0.06,
    }
    return fx


write(build(), out_path(os.path.dirname(__file__), "dragon_03_SkyDrop"), form="hybrid")
print("wrote dragon_03_SkyDrop.json")
