"""Transform (hybrid F) - flame cocoon to full dragon. Signature: a FLAME COCOON (nested fused curtains of fire with
spiralling ribbons) that swells around the player, then the serpent dragon POURS OUT of it spiralling upward, coils
once, and the cocoon BURSTS on its roar.

Beat sheet
  0.00-0.40  the player crouches; a ring of fire rises from the sand around them; embers spiral inward (anticipation)
  0.40-1.20  the fire wraps up into a closed spinning cocoon (nested flame_wall curtains + spiral ribbons + billows)
             that swells from 2.5 to 4.5 studs; the silhouette swells inside it (scale 1 -> 1.6)
  1.00-1.30  HIDDEN SWAP: at the densest cocoon frames the player shrinks away inside the fire while the dragon's head
             breaks out of the top - its unborn body is still inside the cocoon / underground, so nothing pops
  1.00-1.50  the dragon pours out spiralling upward around the cocoon and coils once overhead
  1.45       the cocoon pinches inward (anticipation)
  1.50       BURST + ROAR: one inverted frame; hit-stop 0.16; the cocoon tears outward as a ring of billows + a fire ring
             + shockwave; the jaw gapes on a roar with 2 heat rings; dust ring and black smoke wall roll out; rocks;
             molten cracks under where the cocoon stood
  1.50-2.80  the roar holds then closes; embers rain; ground fire burns down; the dragon swims a slow loop overhead;
             the world settles into the deep full-form grade and stays there
Camera: gameplay camera that zooms out to the full-form distance as the dragon appears (what the game does).
Run: python3 lab/dragon/moves/transform.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

TC0, TS, TB = 0.40, 1.15, 1.50
DUR = 2.8
G = [0, 0, 0]

POSE = {
    "lean": smooth([[0, 0], [0.3, -18], [0.8, -24], [1.1, -20], [DUR, -20]]),
    "armR": smooth([[0, 0], [0.3, -30], [0.8, -40], [DUR, -40]]),
    "armL": smooth([[0, 0], [0.3, -30], [0.8, -40], [DUR, -40]]),
    "armRz": smooth([[0, 0], [0.3, 30], [DUR, 30]]),
    "armLz": smooth([[0, 0], [0.3, -30], [DUR, -30]]),
    "offset": smooth([[0, [0, 0, 0]], [0.3, [0, -0.6, 0]], [1.0, [0, -0.4, 0]], [DUR, [0, -0.4, 0]]]),
    # the silhouette swells inside the cocoon, then shrinks away at the hidden swap
    "scale": [[0, [1, 1, 1]], [0.3, [1.08, 0.85, 1.08]], [0.6, [1.12, 1.12, 1.12]], [1.0, [1.25, 1.25, 1.25]], [TS, [1.2, 1.2, 1.2]],
              [TS + 0.12, [0.01, 0.01, 0.01], "in"], [DUR, [0.01, 0.01, 0.01]]],
}


def head_path():
    """Born inside the cocoon heading straight up (the unborn body continues down into the ground), spirals up around
    the cocoon, coils once overhead, roars at the burst, then swims a slow tilted loop."""
    P = []
    t0, t1 = 0.98, TB
    n = 40
    for i in range(n + 1):
        u = i / n
        t = t0 + (t1 - t0) * u
        a = 1.6 * 2 * math.pi * u ** 0.9
        r = 0.4 + 6.5 * u ** 0.8
        P.append([round(t, 4), [round(math.cos(a) * r, 3), round(1.0 + 15.0 * u ** 0.75, 3), round(math.sin(a) * r - 1.0, 3)]])
    # after the roar: a slow tilted loop overhead (the body keeps coiling, never a straight plank)
    a0 = math.atan2(P[-1][1][2] + 1.0, P[-1][1][0])
    m = 60
    for i in range(1, m + 1):
        u = i / m
        t = t1 + (DUR - t1) * u
        a = a0 + 0.9 * 2 * math.pi * u
        r = 6.5 + 1.5 * u
        P.append([round(t, 4), [round(math.cos(a) * r, 3), round(16.0 + 2.0 * math.sin(2 * a), 3), round(math.sin(a) * r - 1.0 - 3 * u, 3)]])
    return P


def build():
    L = [ambience([0, 0, 0], 0, DUR, radius=14, rate=12, seed=1001)]
    # ---- 0.0-0.4: a ring of fire rises from the sand, embers spiral inward
    L += ring_wall(G, 3.2, 0.05, 0.6, 3.0, sweep=0.25, start=0.0, fade=[[0, 0], [0.7, 0.1], [1, 1]])
    L.append({"type": "emitter", "at": [0, 2.5, 0], "part": [10, 5, 10], "rate": [[0.0, TC0, 50]], "seed": 1002, "props": {
        "Texture": "spark_streak", "Color": PALS["fire"]["spark"], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "Size": [[0, 1.8], [1, 0.4]], "Lifetime": [0.16, 0.2], "Speed": [24, 30], "Orientation": "VelocityParallel",
        "Transparency": [[0, 0.3], [1, 0.8]], "ZOffset": 0.3}})
    L.append(glow_pool(G, 0, 8, life=0.3, rate=[[0.0, TB, 8]], peak=0.3, seed=1003))

    # ---- 0.4-1.5: the cocoon - nested fused curtains that swell and spin, spiral flame ribbons, billows
    # an egg of fire: a wide lower ring, a narrower ring above it, a small cap - each rises in turn, then the whole
    # egg swells (a second, bigger egg wraps the first)
    egg = [(TC0, 3.0, 0.0, 5.5), (TC0 + 0.12, 2.3, 3.8, 4.2), (TC0 + 0.24, 1.3, 6.6, 3.2),
           (0.86, 3.9, 0.0, 6.8), (0.94, 3.0, 4.6, 5.0), (1.02, 1.7, 8.0, 3.8)]
    for j, (t, r, b, h) in enumerate(egg):
        L += ring_wall(G, r, t, TB - t + 0.05, h, sweep=0.18, start=j * 1.3, reverse=bool(j % 2), base=b, fade=[[0, 0], [0.85, 0.05], [1, 1]])
    for k in range(3):
        sp = []
        n = 50
        for i in range(n + 1):
            u = i / n
            t = TC0 + (TB - TC0) * u
            a = k * 2.094 + u * 3.5 * 2 * math.pi
            r = 2.8 + 1.4 * u
            sp.append([round(t, 4), [round(math.cos(a) * r * (1 - 0.45 * u), 3), round(0.8 + 8.5 * u, 3), round(math.sin(a) * r * (1 - 0.45 * u), 3)]])
        L += trail_stack({"path": sp, "at": sp[0][1], "t0": TC0, "t1": TB, "lifetime": 0.22, "faceCamera": True,
                          "transparency": [[0, 0], [0.6, 0.2], [1, 1]], "widthScale": [[0, 1], [1, 0.25]], "textureMode": "Stretch"},
                         {"rim": 1.5, "mid": 1.0, "core": 0.3}, layers=("rim", "mid", "core"), cool=False)
    for j in range(6):
        a = j / 6 * 2 * math.pi
        for e in billow([math.cos(a) * 3.2, 4.5, math.sin(a) * 3.2], TC0, 4.5, life=0.5, seed=1011 + j, grow=1.3, rot=50 * j):
            e.pop("emits", None); e["rate"] = [[TC0 + 0.05 * j, TB - 0.05, 5]]
            L.append(e)
    L.append(haze([0, 8, 0], TC0, DUR, size=16, seed=1023))
    L.append(smoke([0, 10, 0], 0, rate=[[0.7, TB, 6]], size=(4, 8), speed=(2, 4), life=(1.0, 1.4), seed=1024, part=[6, 2, 6], rise=3))

    L += fire_streams(G, TC0, 0.9, r0=7.5, r1=2.8, n=7, y0=0.6, rise=3.5, turns=1.1, width=1.2, life=0.4, seed=51)
    # ---- the dragon pours out of the cocoon (the hidden swap is inside the densest fire)
    hp = head_path()
    jaw = [[0, 6], [(TB - 0.12 - 0.98) / (DUR - 0.98), 10], [(TB - 0.02 - 0.98) / (DUR - 0.98), 48], [(TB + 0.6 - 0.98) / (DUR - 0.98), 46],
           [(TB + 0.85 - 0.98) / (DUR - 0.98), 8], [1, 6]]
    tracks = {}
    for side in "LR":
        for i in range(3):
            tracks[f"whisker{side}_{i}"] = {"rot": [[round(t, 3), [round(-18 + 14 * math.sin(t * 5 + i), 2), 0, round((10 if side == "L" else -10) * math.sin(t * 2.5 + i), 2)]] for t in [k * 0.1 for k in range(19)]]}
    L.append(dragon(hp, 0.98, DUR - 0.98, jaw=jaw, tracks=tracks))
    # fire peels off the body as it emerges
    L += wisps([0, 6, 0], 1.0, 1.9, 18, size=3.0, life=0.5, path=hp, seed=1031)
    L.append(embers([0, 6, 0], 0, rate=[[1.0, 2.0, 40]], speed=(2, 6), life=(0.5, 1.0), grav=-6, path=hp, seed=1032))

    # ---- 1.45 pinch, 1.50 BURST + ROAR
    T = TB
    L += emit_stack("fire_swirl", [0, 5, 0], T - 0.12, size=[[0, 9], [1, 3]], life=0.12, cool=False, seed=1041)
    L += impact([0, 4.5, 0], T + 0.005, size=13, life=0.55, seed=1042)
    L += glint([0, 6, 0], T + 0.005, size=7, life=0.2, seed=1043)
    for j in range(10):
        a = j / 10 * 2 * math.pi
        L += billow([math.cos(a) * 3.5, 3.0, math.sin(a) * 3.5], T + 0.01, 6.0, life=0.6, seed=1051 + j, grow=1.4,
                    move={"from": [math.cos(a) * 3.5, 3.0, math.sin(a) * 3.5], "to": [math.cos(a) * 10, 2.0, math.sin(a) * 10], "t0": T, "t1": T + 0.45, "ease": "out"})
    L += fire_ring(G, T + 0.01, 13, life=0.75, seed=1061)
    L += fire_bloom(G, T + 0.01, radius=10.0, dur=1.1, height=10.0, seed=1091, arcs=4, fronds=1.0)
    L += dark_spikes([0, 5, 0], T + 0.02, size=24, life=0.35, seed=1095)
    L.append(fire_scraps([0, 4, 0], T + 0.02, n=30, speed=(20, 36), size=(1.8, 3.6), seed=1096))
    L += fire_streams(G, T + 0.01, 0.5, r0=2.0, r1=15.0, n=9, y0=0.8, rise=2.0, turns=0.8, width=1.8, life=0.45, seed=53)
    L.append(shockwave(G, T + 0.015, 16, life=0.5, seed=1062))
    L.append(dust_ring(G, T + 0.015, n=26, speed=(36, 50), size=(4, 9), seed=1063, radius=4))
    L.append(smoke([0, 2.5, 0], T + 0.03, n=16, size=(5, 11), speed=(18, 28), life=(1.2, 1.8), seed=1064, spread=90, rise=2, part=[8, 2, 8]))
    L += ember_spray([0, 5, 0], T + 0.01, size=16, life=0.7, seed=1065)
    L.append(streaks([0, 4, 0], T + 0.01, 18, speed=(70, 110), length=(3, 6), seed=1066))
    L += molten_crack(G, T + 0.01, size=16, rot=30, glow_life=1.6, char_life=3.0, seed=1067)
    L.append(scorch(G, T + 0.2, size=12, life=2.2, seed=1068))
    debris = rocks(G, T + 0.01, radius=5.5, count=14, size=1.0, speed=34, seed=1069)
    # the roar: two heat rings from the head
    head_at_burst = next(p for t, p in hp if t >= T)
    L += heat_ring(head_at_burst, T + 0.02, 12, life=0.5, seed=1071)
    L += heat_ring(head_at_burst, T + 0.22, 9, life=0.45, seed=1072)
    L.append(gusts(head_at_burst, T + 0.05, size=12, life=0.4, seed=1073))
    # after: ground fire burns down, embers rain, after-smoke, ash
    L += ring_wall(G, 7.5, T + 0.08, 1.0, 3.0, sweep=0.14, start=1.0, fade=[[0, 0], [0.6, 0.15], [1, 1]])
    L.append(embers([0, 18, 0], 0, rate=[[T + 0.2, DUR, 40]], speed=(1, 3), life=(1.2, 2.0), grav=-5, part=[24, 2, 24], seed=1081))
    L.append(smoke_wisps([0, 0.4, 0], T + 0.4, DUR, 10, size=4, part=[14, 0.2, 14], seed=1082))
    L.append(ash([0, 14, 0], T + 0.3, DUR, 14, part=(26, 3, 26), seed=1083))

    cam0, cam1 = GAMEPLAY_CAM, GAMEPLAY_CAM_FULL
    k0, k1 = (TS - 0.1) / DUR, (TB + 0.25) / DUR
    return {
        "_swap": TS, "name": "dragon_06_Transform", "title": "Transform", "element": "Dragon", "archetype": "transform", "duration": DUR,
        "layers": L, "debris": debris,
        "hitstop": [{"t": T + 0.02, "dur": 0.16}],
        "impact": [{"t": T + 0.02, "dur": 0.05, "mode": "invert"}],
        "shakes": [{"t": 0.45, "amp": 0.12, "dur": 0.9, "freq": 16}, {"t": T, "amp": 0.8, "dur": 0.5, "freq": 22}],
        "lights": [light([0, 5, 0], [[0, 0], [0.3, 14], [1.0, 30], [T, 44], [T + 0.5, 22], [DUR, 10]], rng=28)],
        "pose": POSE,
        "camera": {"pos": [[0, cam0["pos"][0][1]], [k0, cam0["pos"][0][1]], [k1, cam1["pos"][0][1], "out"], [1, cam1["pos"][0][1]]],
                   "look": [[0, cam0["look"][0][1]], [k0, cam0["look"][0][1]], [k1, cam1["look"][0][1], "out"], [1, cam1["look"][0][1]]],
                   "fov": cam0["fov"]},
        "poster": T + 0.08,
    }


write(build(), out_path(os.path.dirname(__file__), "dragon_06_Transform"), form="into_full")
print("wrote dragon_06_Transform.json")
