"""Talon Rend (hybrid Z) - triple claw combo. Signature: three burning claw rakes that HANG in the air at their own
angles, so after the finisher they form a burning triangle of slashes; their tails cool while the finisher's gouges
burn into the sand under the target.

Beat sheet
  0.00-0.18  lean back, right arm drawn back and up; both claws ignite (fire + a glow riding each hand, a warm pool on
             the sand), embers pulled in                                                (anticipation)
  0.18       rake 1: right claw sweeps down-right; hit-stop 0.05                        (timing)
  0.38       rake 2: left claw sweeps up-left (mirrored); hit-stop 0.05
  0.48-0.62  both arms rise overhead, the body stretches tall                           (anticipation, stretch)
  0.62       FINISHER: both claws rake straight down (the biggest rake); hit-stop 0.12; the target squashes and is
             knocked back; the gouges ignite under it; dust kick; black smoke rises behind (squash, timing)
  0.80-1.70  the rakes cool and flake into embers; gouges cool; smoke drifts; the caster settles (follow-through)
Connective layers for the whole move: flame ribbons trail both claws between strikes, ambient embers drift through
the area, light pools sit under every fire source.
Run: python3 lab/dragon/moves/talon_rend.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

T1, T2, T3 = 0.18, 0.38, 0.62
TARGET = [0, 0, -7.6]
CHEST = [0, 3.4, -7.6]
FRONT = [0.9, 3.5, -6.4]          # where the rakes hang: just in front of the target, on the camera side
DUR = 1.7

POSE = {
    "armR": [[0, 0], [0.15, -35, "out"], [T1 - 0.02, -40], [T1 + 0.03, 85, "outExpo"], [0.3, 60], [0.45, 120], [0.55, 172, "out"],
             [T3 - 0.01, 175], [T3 + 0.03, 60, "outExpo"], [0.9, 45], [1.35, 0]],
    "armRz": [[0, 0], [0.15, 70, "out"], [T1 - 0.02, 75], [T1 + 0.03, -35, "outExpo"], [0.3, -20], [0.55, 15], [T3 + 0.03, 10], [1.35, 0]],
    "armL": [[0, 0], [0.15, 25], [T2 - 0.03, -30, "out"], [T2 + 0.03, 85, "outExpo"], [0.45, 110], [0.55, 172, "out"],
             [T3 - 0.01, 175], [T3 + 0.03, 60, "outExpo"], [0.9, 45], [1.35, 0]],
    "armLz": [[0, 0], [T2 - 0.03, -70, "out"], [T2 + 0.03, 35, "outExpo"], [0.5, 20], [0.55, -15], [T3 + 0.03, -10], [1.35, 0]],
    "lean": [[0, 0], [0.15, 12, "out"], [T1 + 0.03, -14, "outExpo"], [T2 - 0.03, 6], [T2 + 0.03, -12, "outExpo"], [0.56, 16, "out"],
             [T3 + 0.03, -22, "outExpo"], [0.85, -14], [1.35, 0]],
    "twist": [[0, 0], [0.15, -25, "out"], [T1 + 0.03, 25, "outExpo"], [T2 - 0.03, 30], [T2 + 0.03, -25, "outExpo"], [0.56, 0], [1.35, 0]],
    "offset": [[0, [0, 0, 0]], [T1, [0, 0, -0.4]], [T2, [0, 0, -0.8]], [T3, [0, 0, -1.1]], [T3 + 0.05, [0, -0.3, -1.6], "outExpo"], [1.3, [0, 0, -1.5]]],
    "scale": [[0, [1, 1, 1]], [0.15, [0.96, 1.05, 0.96]], [T1 + 0.03, [1.04, 0.96, 1.04]], [0.3, [1, 1, 1]], [0.58, [0.93, 1.1, 0.93], "out"],
              [T3 + 0.03, [1.12, 0.86, 1.12], "outExpo"], [T3 + 0.2, [0.98, 1.03, 0.98]], [T3 + 0.4, [1, 1, 1]]],
}


def build():
    L = []
    # ---- ambience for the whole move: drifting embers in the air
    L.append(ambience([0, 0, -4], 0.0, DUR, radius=9, rate=9, seed=91))

    # ---- claws ignite: fire + glow riding both hands, flame ribbons trailing them between strikes, a warm pool below
    for side, seed in (("R", 101), ("L", 111)):
        hp = hand_path(POSE, 0.02, 1.05, side, reach=2.05)
        for e in emit_stack("flame_tongue", hp[0][1], 0, size=[[0, 2.2], [1, 2.6]], life=0.3, rate=[[0.02, 1.0, 24]], seed=seed,
                            orient="FacingCameraWorldUp", locked=True,
                            transparency=[[0, 0.1], [0.6, 0.2], [1, 1]]):
            e["path"] = hp
            L.append(e)
        L.append(glow_orb(hp[0][1], 0, 3.6, life=0.18, rate=[[0.02, 1.0, 14]], path=hp, locked=True, tr=0.5, seed=seed + 2))
        L.append(embers(hp[0][1], 0, rate=[[0.02, 0.95, 26]], speed=(1, 3), life=(0.35, 0.7), rise=7, grav=0, size=(0.25, 0.5),
                        seed=seed + 1, path=hp))
        L += trail_stack({"path": hp, "at": hp[0][1], "t0": 0.12, "t1": 1.0, "lifetime": 0.12, "faceCamera": True,
                          "transparency": [[0, 0.25], [0.5, 0.55], [1, 1]], "textureMode": "Stretch"},
                         {"rim": 0.55, "mid": 0.35, "core": 0.12}, cool=False)
    L.append(glow_pool([0.5, 0, -1.6], 0, 7, life=0.25, rate=[[0.02, 1.0, 8]], peak=0.25, seed=121))
    L.append({"type": "emitter", "at": [1.6, 4.2, 0.4], "part": [6, 4, 4], "rate": [[0.0, T1 - 0.02, 34]], "seed": 122, "props": {
        "Texture": "spark_streak", "Color": PALS["fire"]["spark"], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "Size": [[0, 1.6], [1, 0.4]], "Lifetime": [0.12, 0.16], "Speed": [20, 26], "Orientation": "VelocityParallel",
        "Transparency": [[0, 0.3], [1, 0.8]], "ZOffset": 0.3}})

    # ---- the three rakes hang at their own angles (a triangle once the finisher lands); fast hand swipes sell the motion
    rakes = [(T1, [FRONT[0] + 0.2, 4.0, FRONT[2]], -32, 5.8, 0.85, 131),
             (T2, [FRONT[0] - 0.2, 3.2, FRONT[2]], 212, 5.8, 0.8, 141),
             (T3, [FRONT[0], 3.4, FRONT[2] - 0.2], -92, 7.6, 0.85, 151)]
    for t, at, rot, sz, life, seed in rakes:
        L += rake(at, t, sz, life=life, rot=rot, seed=seed)
    for t, side in ((T1, "R"), (T2, "L"), (T3, "R"), (T3, "L")):
        hp = hand_path(POSE, t - 0.03, t + 0.05, side, step=1 / 120, reach=2.2)
        L += trail_stack({"path": hp, "at": hp[0][1], "t0": t - 0.03, "t1": t + 0.05, "lifetime": 0.14, "faceCamera": True,
                          "transparency": [[0, 0], [0.5, 0.25], [1, 1]], "textureMode": "Stretch"},
                         {"glow": 2.0, "rim": 1.2, "mid": 0.8, "core": 0.28}, cool=False)

    # ---- hits 1 and 2 (medium): fire impact, sparks, a light pool on the sand; smoke wisps behind
    hits, numbers = [], []
    for i, (t, side) in enumerate(((T1, 1), (T2, -1))):
        th = t + 0.01
        L += impact([CHEST[0] + 0.5 * side + 0.6, CHEST[1], CHEST[2] + 0.9], th, size=5.0, life=0.4, seed=161 + i, rot=40 * i)
        L.append(embers([0.4, 3.4, -6.8], th, n=14, speed=(10, 22), life=(0.4, 0.8), grav=-18, seed=167 + i))
        L.append(glow_pool([0.3, 0, -7.0], th, 6, life=0.35, peak=0.45, seed=169 + i))
        L.append(smoke([0, 4.6, -9.0], th + 0.06, n=3, size=(2.5, 5.5), speed=(1.5, 3), life=(0.9, 1.3), seed=165 + i))
        hits.append({"t": th, "dummy": 0, "dir": [0.25 * side, 0, -1], "power": 0.22})
        numbers.append({"t": th + 0.02, "at": [1.8 * side + 1.0, 6.4, -8.2], "text": str(48 + 7 * i), "color": GOLD, "vel": [1.5 * side, 8, 0], "size": 1.4})

    # ---- the finisher (BIG): biggest rake, gouges, flare, impact, ground shockwave, dust kick, rising smoke, rocks
    th = T3 + 0.01
    L += impact([0.6, 3.0, -7.0], th, size=8.5, life=0.55, seed=171)
    L.append(flare([0.7, 3.2, -6.6], th, size=11, life=0.2, seed=172))
    L.append(streaks([0.4, 2.0, -7.4], th + 0.005, 9, speed=(55, 90), length=(2, 4), spread=35, direction=[180, 0, 0], seed=173))
    L.append(shockwave([0, 0, -8.0], th + 0.01, 6.5, life=0.4, seed=174))
    L.append(dust_ring([0, 0, -8.2], th + 0.01, n=14, speed=(24, 34), size=(3, 6.5), seed=175))
    L.append(glow_pool([0.2, 0, -8.0], th, 11, life=0.9, peak=0.5, seed=176))
    L.append(smoke([0, 3.5, -10.0], th + 0.08, n=6, size=(4, 9), speed=(2, 5), life=(1.2, 1.8), seed=177, spread=50))
    L += gouge([0, 0, -9.4], th, size=8.5, rot=90, glow_life=1.25, char_life=3.0, seed=178)
    hits.append({"t": th, "dummy": 0, "dir": [0, 0, -1], "power": 1.0})
    numbers.append({"t": th + 0.03, "at": [1.2, 7.0, -8.6], "text": "164", "color": WHITE_GOLD, "vel": [0.5, 11, -1], "size": 1.8})
    debris = rocks([0, 0, -8.4], th, radius=3.5, count=8, size=0.9, speed=24, crater=False, seed=179)

    # ---- follow-through: the rakes flake into embers as they cool
    for t, at, rot, sz, life, seed in rakes:
        L.append(embers(at, 0, rate=[[t + life * 0.4, t + life * 0.95, 24]], speed=(1, 4), life=(0.5, 1.0), grav=-4,
                        part=[sz * 0.55, 1.2, 0.6], seed=seed + 5))

    return {
        "name": "dragon_01_TalonRend", "title": "Talon Rend", "element": "Dragon", "archetype": "claw_combo", "duration": DUR,
        "layers": L, "dummies": [TARGET], "hits": hits, "numbers": numbers, "debris": debris,
        "hitstop": [{"t": T1 + 0.03, "dur": 0.05}, {"t": T2 + 0.03, "dur": 0.05}, {"t": T3 + 0.03, "dur": 0.12}],
        "shakes": [{"t": T1, "amp": 0.15, "dur": 0.14, "freq": 24}, {"t": T2, "amp": 0.15, "dur": 0.14, "freq": 24},
                   {"t": T3, "amp": 0.5, "dur": 0.35, "freq": 22}],
        "lights": [light([0.8, 4, -1], [[0, 0], [0.1, 10], [T3, 12], [1.0, 5], [1.3, 0]], rng=16),
                   light([0.4, 3.4, -6.4], [[T1, 0], [T1 + 0.01, 30], [T1 + 0.15, 0], [T2, 0], [T2 + 0.01, 30], [T2 + 0.15, 0],
                                            [T3, 0], [T3 + 0.01, 44], [T3 + 0.35, 14], [1.3, 0]], rng=18)],
        "pose": POSE,
        "camera": {"pos": [[0, [14.5, 5.6, 0.6]], [T3 / DUR - 0.01, [13.8, 5.4, -0.6]], [T3 / DUR + 0.02, [12.6, 5.0, -1.6], "outExpo"], [1, [13.6, 5.4, -1.0]]],
                   "look": [[0, [0, 3.0, -3.8]], [T3 / DUR, [0, 3.0, -4.8]], [1, [0, 2.8, -5.0]]],
                   "fov": [[0, 55], [T3 / DUR - 0.005, 54], [T3 / DUR + 0.01, 49, "out"], [0.6, 53]]},
        "poster": T3 + 0.06,
    }


write(build(), out_path(os.path.dirname(__file__), "dragon_01_TalonRend"), form="hybrid")
print("wrote dragon_01_TalonRend.json")
