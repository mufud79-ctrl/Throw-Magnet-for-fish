"""Tail Cyclone (hybrid V) - 360 tail sweep, close AoE with a delayed eruption. Signature: the sweep DRAWS a burning
ring on the ground (one continuous low curtain of fire); a beat later the ring ERUPTS in a crown of 8 fire pillars in
sequence around the circle (fused columns of rolling flame, each crowned by a billow).

Beat sheet (fluid: spline spin with overshoot; the arms trail the body)
  0.00-0.20  coil: crouch and twist back, heat gathers at the hips (swirl), embers pulled in   (anticipation)
  0.20-0.60  full 360 spin; the tail tip (radius 6) draws the ring of fire on the sand; a dust ring flies out
  0.60-0.75  the ring smoulders and pulses brighter (anticipation for the eruption)
  0.75-1.05  8 pillars erupt one after another, 0.04 s apart, going around; targets on the ring are launched;
             hit-stop 0.07 on the pillar that catches the first one                    (timing)
  1.05-1.80  pillars collapse into black smoke, embers rain, after-smoke rises, flickers along the ring
Stand-in: no tail mesh on the avatar yet (rig v2 `attach` - rigging session); the tail tip is computed from the spin.
Camera: gameplay view, pulled back so the whole ring around the player is in frame.
Run: python3 lab/dragon/moves/tail_cyclone.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa
from kit import _keys

TS, TE, TP = 0.20, 0.60, 0.75
RAD = 6.0
DUR = 1.8
NP = 8
TARGETS = [[-4.4, 0, -4.1], [4.8, 0, -3.6], [0.4, 0, 6.0]]

POSE = {
    "twist": smooth([[0, 0], [0.16, -70], [TS, -75], [0.32, 60], [0.46, 200], [TE, 300], [0.68, 300], [0.9, 360], [1.2, 360], [DUR, 360]]),
    "lean": smooth([[0, 0], [TS, 12], [0.4, -10], [TE, -6], [0.9, 0], [DUR, 0]]),
    "armR": smooth([[0, 0], [TS, 40], [0.4, 70], [TE, 60], [1.0, 20], [1.4, 0], [DUR, 0]]),
    "armL": smooth([[0, 0], [TS, 40], [0.4, 70], [TE, 60], [1.0, 20], [1.4, 0], [DUR, 0]]),
    "armRz": smooth([[0, 0], [TS, 60], [0.4, 85], [TE, 70], [1.0, 20], [1.4, 0], [DUR, 0]]),
    "armLz": smooth([[0, 0], [TS, -60], [0.4, -85], [TE, -70], [1.0, -20], [1.4, 0], [DUR, 0]]),
    "offset": smooth([[0, [0, 0, 0]], [TS, [0, -0.5, 0]], [0.4, [0, -0.2, 0]], [TE, [0, -0.3, 0]], [0.9, [0, 0, 0]], [DUR, [0, 0, 0]]]),
    "scale": smooth([[0, [1, 1, 1]], [TS, [1.07, 0.9, 1.07]], [0.4, [0.97, 1.05, 0.97]], [TE, [1.03, 0.96, 1.03]], [0.9, [1, 1, 1]], [DUR, [1, 1, 1]]]),
}


def tip(t, r=RAD, y=0.6):
    """The (virtual) tail tip: behind the caster, sweeping with the body twist."""
    a = math.radians(_keys(POSE["twist"], t, 0)) + math.pi / 2       # tail points backward (+Z) at twist 0
    return [math.cos(a) * r, y, math.sin(a) * r]


def build():
    L = [ambience([0, 0, 0], 0, DUR, radius=10, rate=10, seed=701)]
    # ---- coil: heat at the hips, embers pulled in, a warm pool
    L.append(glow_pool([0, 0, 0], 0, 7, life=0.25, rate=[[0.0, TE, 8]], peak=0.28, seed=703))
    L.append({"type": "emitter", "at": [0, 2.0, 0], "part": [7, 4, 7], "rate": [[0.0, TS - 0.02, 34]], "seed": 704, "props": {
        "Texture": "spark_streak", "Color": PALS["fire"]["spark"], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "Size": [[0, 1.6], [1, 0.4]], "Lifetime": [0.12, 0.16], "Speed": [20, 26], "Orientation": "VelocityParallel",
        "Transparency": [[0, 0.3], [1, 0.8]], "ZOffset": 0.3}})

    # ---- the spin: the tail tip draws the ring (one continuous low curtain), a flame ribbon at the tip, smear, dust
    n = 60
    tp = [[R(TS + (TE - TS) * i / n, 4), R(tip(TS + (TE - TS) * i / n, RAD, 1.5))] for i in range(n + 1)]
    for lay in ("rim", "mid", "core"):
        L.append({"type": "trail", "path": tp, "at": tp[0][1], "t0": TS, "t1": TE, "lifetime": 1.1 - (TE - TS) * 0.5, "width": 3.0,
                  "up": [0, 1, 0], "textures": [f"{w}_{lay}" for w in WALLS], "swap": 0.07, "textureMode": "Wrap", "textureLength": 9,
                  "color": PALS["fire"]["HOT"][lay], "lightEmission": LE[lay], "brightness": BR[lay],
                  "transparency": [[0, 0], [0.8, 0.1], [1, 1]]})
    tq = [[R(TS - 0.05 + (TE + 0.05 - TS) * i / n, 4), R(tip(TS - 0.05 + (TE + 0.05 - TS) * i / n, RAD * 0.85, 1.8))] for i in range(n + 1)]
    L += trail_stack({"path": tq, "at": tq[0][1], "t0": TS - 0.05, "t1": TE + 0.05, "lifetime": 0.18, "faceCamera": True,
                      "transparency": [[0, 0], [0.5, 0.2], [1, 1]], "widthScale": [[0, 1], [1, 0.2]], "textureMode": "Stretch"},
                     {"rim": 1.6, "mid": 1.05, "core": 0.32}, layers=("rim", "mid", "core"), cool=False)
    L += wisps(tq[0][1], TS, TE, 24, size=2.4, life=0.4, path=tq, seed=711)
    L.append(dust_ring([0, 0, 0], TS + 0.05, n=18, speed=(24, 34), size=(3, 6.5), seed=712))
    for k in range(3):
        L += smear([0, 1.6, 0], TS + 0.04 + 0.12 * k, 12, 120 * k, life=0.2, seed=713 + k)
    # smoulder + pulse before the eruption
    L.append(glow_pool([0, 0, 0], TE, 15, life=0.35, peak=0.35, seed=720, hold=0.6))
    L.append(embers([0, 0.4, 0], 0, rate=[[TE, TP + 0.05, 50]], speed=(1, 3), life=(0.6, 1.0), rise=5, grav=0, part=[13, 0.3, 13], seed=721))

    # ---- the eruption: 8 fused fire pillars in sequence around the ring
    hits, numbers, debris = [], [], []
    tang = [math.atan2(p[2], p[0]) for p in TARGETS]
    for k in range(NP):
        a = math.radians(_keys(POSE["twist"], TS, 0)) + math.pi / 2 + k / NP * 2 * math.pi
        p = [math.cos(a) * RAD, 0, math.sin(a) * RAD]
        t = TP + 0.04 * k
        # the eruption: a FAN of sharp anime flame spikes bursting out of the ring (the lead shape: a ring of spike
        # crowns going off in sequence), leaning outward, uneven heights; a glint and a few needles shooting up
        out_deg = math.degrees(math.atan2(math.cos(a), 1.0)) * 0.5
        for j2 in range(4):
            off = (j2 - 1.5) * 0.9
            q = [p[0] - math.sin(a) * off, 0, p[2] + math.cos(a) * off]
            h = 7.5 + 1.8 * ((j2 * 5 + k) % 3) / 2 - 1.2 * abs(j2 - 1.5)
            L += emit_stack("anime_flame_spike", [q[0], h * 0.42, q[2]], t + 0.012 * j2, size=[[0, h * 0.95], [1, h * 1.05]],
                            life=0.5 + 0.06 * (j2 % 2), cool=False, rot=-out_deg + (j2 - 1.5) * 8, seed=745 + 7 * k + j2,
                            orient="FacingCameraWorldUp", z=0.04 * j2)
        L += glint([p[0], 3.2, p[2]], t + 0.01, size=3.6, life=0.18, seed=748 + k)
        L.append({"type": "emitter", "at": [p[0], 1.2, p[2]], "emits": [[t + 0.02, 6]], "seed": 761 + k, "rot": [0, 0, 0], "props": {
            "Texture": "needle_bold", "Color": [[0, "#fff6b0"], [0.5, "#ffd21a"], [1, "#ff6a10"]], "LightEmission": 1, "Brightness": 1.5,
            "Size": [[0, 3.6], [1, 0.3]], "Lifetime": [0.18, 0.3], "Speed": [45, 70], "SpreadAngle": [14, 14], "Drag": 6,
            "Acceleration": [0, 0, 0], "Orientation": "VelocityParallel", "ZOffset": 0.6}})
        L.append(glow_pool(p, t, 6, life=0.4, peak=0.3, seed=751 + k))
        L.append(embers([p[0], 6.5, p[2]], t + 0.2, n=8, speed=(3, 7), life=(0.8, 1.3), grav=-10, seed=781 + k))
        L.append(scorch(p, t, size=4, life=1.6, seed=791 + k))
        L += flicker(p, t + 0.3, t + 0.9, 1.6, seed=801 + k)
    # smooth dark smoke rising off the ring after the crowns, and the warm haze spreading past it
    L.append({"type": "emitter", "at": [0, 4.0, 0], "emits": [[TP + 0.25, 10]], "rate": [[TP + 0.3, TP + 0.8, 10]], "seed": 771,
              "part": [RAD * 2, 2, RAD * 2], "props": {"Texture": "haze_soft", "Color": [[0, "#4a2a22"], [1, "#6a4a3e"]], "LightEmission": 0,
        "Brightness": 1, "Size": [[0, 4], [1, 9]], "Lifetime": [1.0, 1.4], "Speed": [1, 3], "SpreadAngle": [30, 30], "Acceleration": [0, 2.5, 0],
        "Drag": 1.2, "Rotation": [0, 360], "RotSpeed": [-10, 10], "FlipbookLayout": "None",
        "Transparency": [[0, 1], [0.15, 0.6], [0.6, 0.72], [1, 1]], "ZOffset": -1.0}})
    L += aura_haze([0, 0, 0], TP, 1.3, radius=RAD * 1.1, height=5.5, strength=1.0, seed=830, cloud=0.5)   # OUTSIDE
    # targets: each is launched by the pillar nearest to it
    first = None
    for i, q in enumerate(TARGETS):
        best = min(range(NP), key=lambda k: abs(((math.radians(_keys(POSE["twist"], TS, 0)) + math.pi / 2 + k / NP * 2 * math.pi) - tang[i] + math.pi) % (2 * math.pi) - math.pi))
        th = TP + 0.04 * best + 0.02
        first = th if first is None else min(first, th)
        sh = emit_stack("ink_shards", [q[0], 3.0, q[2]], th + 0.01, size=[[0, 4.5], [1, 6]], life=0.26, cool=False, seed=811 + i,
                        rot=40 * i, layers=("rim",), z=0.7)
        for e in sh:
            e["props"]["Color"] = "#1a0806"; e["props"]["LightEmission"] = 0
        L += sh
        L += glint([q[0], 3.4, q[2]], th, size=3.8, life=0.2, seed=815 + i)
        hits.append({"t": th, "dummy": i, "dir": [R(q[0] / RAD * 0.4), 0, R(q[2] / RAD * 0.4)], "power": 0.7})
        numbers.append({"t": th + 0.02, "at": [q[0], 6.4, q[2]], "text": str(96 + 7 * i), "color": GOLD, "vel": [0, 11, 0], "size": 1.6})
    L.append(smoke_wisps([0, 0.4, 0], 1.1, DUR, 12, size=4, part=[13, 0.2, 13], seed=821))
    debris += rocks([0, 0, 0], TP, radius=RAD, count=10, size=0.8, speed=22, crater=False, seed=823)

    return {
        "name": "dragon_04_TailCyclone", "title": "Tail Cyclone", "element": "Dragon", "archetype": "spin_ring_eruption", "duration": DUR,
        "layers": L, "dummies": TARGETS, "hits": hits, "numbers": numbers, "debris": debris,
        "hitstop": [{"t": first + 0.02, "dur": 0.07}],
        "shakes": [{"t": TS, "amp": 0.15, "dur": 0.3, "freq": 18}, {"t": TP, "amp": 0.5, "dur": 0.45, "freq": 22}],
        "lights": [light([0, 3, 0], [[0, 0], [TS, 12], [TE, 18], [TP, 24], [TP + 0.3, 40], [1.3, 10], [DUR, 0]], rng=24)],
        "pose": POSE,
        "camera": {"pos": [[0, [6.5, 9.0, 11.5]], [1, [6.5, 9.0, 11.5]]], "look": [[0, [0, 2.6, -1.5]], [1, [0, 2.6, -1.5]]], "fov": GAMEPLAY_CAM["fov"]},
        "poster": TP + 0.2,
    }


write(build(), out_path(os.path.dirname(__file__), "dragon_04_TailCyclone"), form="hybrid")
print("wrote dragon_04_TailCyclone.json")
