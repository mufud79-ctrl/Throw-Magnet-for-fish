"""Talon Rend (hybrid Z) - triple claw combo. Signature: every swipe is DRAWN by the claws - three parallel flame
trails ride the three claw tips along the arm's arc - and each rake then hangs in the air at its own angle, so after
the finisher they form a burning triangle of slashes; the finisher's gouges burn into the sand under the target.

Beat sheet (fluid: spline arm arcs, the torso leads each swing, the arm overshoots and settles)
  0.00-0.16  lean back and twist away, right arm winds up high and wide; both claws ignite, embers pulled in
                                                                                       (anticipation)
  0.18       rake 1: the right claw swings down across the body on a wide arc; hit-stop 0.05
  0.24-0.34  the right arm overshoots, the torso unwinds the other way while the left arm winds up (overlap)
  0.38       rake 2: the left claw swings down the mirrored arc; hit-stop 0.05
  0.46-0.60  both arms sweep up overhead, the body stretches tall                      (anticipation, stretch)
  0.62       FINISHER: both claws come straight down; hit-stop 0.12; the target squashes and is knocked back; gouges
             ignite under it; dust kick; black smoke rises behind                     (squash, timing)
  0.70-1.70  arms overshoot low, recover in an ease; rakes cool and flake into embers; gouges cool (follow-through)
Camera: one fixed gameplay view (behind, above and right of the caster): an ability, not a cutscene.
Run: python3 lab/dragon/moves/talon_rend.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

T1, T2, T3 = 0.18, 0.38, 0.62
TARGET = [0, 0, -7.6]
CHEST = [0, 3.4, -7.6]
FRONT = [0.6, 3.5, -6.0]
DUR = 1.7

POSE = {
    "armR": smooth([[0, 0], [0.1, 120], [0.155, 158], [T1, 110], [T1 + 0.035, 38], [0.26, 22], [0.33, 40], [0.42, 70], [0.52, 150],
                    [0.585, 182], [T3, 150], [T3 + 0.035, 30], [0.72, 12], [0.85, 26], [1.2, 12], [1.5, 0], [DUR, 0]]),
    "armRz": smooth([[0, 0], [0.1, 45], [0.155, 62], [T1, 30], [T1 + 0.035, -38], [0.26, -48], [0.33, -30], [0.45, 0], [0.585, 12],
                     [T3 + 0.035, 8], [0.85, 10], [1.5, 0], [DUR, 0]]),
    "armL": smooth([[0, 0], [0.12, 25], [0.22, 30], [0.3, 120], [0.355, 158], [T2, 110], [T2 + 0.035, 38], [0.46, 40], [0.53, 150],
                    [0.585, 182], [T3, 150], [T3 + 0.035, 30], [0.72, 12], [0.85, 26], [1.2, 12], [1.5, 0], [DUR, 0]]),
    "armLz": smooth([[0, 0], [0.2, -10], [0.3, -45], [0.355, -62], [T2, -30], [T2 + 0.035, 38], [0.46, 48], [0.52, 10], [0.585, -12],
                     [T3 + 0.035, -8], [0.85, -10], [1.5, 0], [DUR, 0]]),
    "lean": smooth([[0, 0], [0.14, 12], [T1 + 0.03, -14], [0.3, -4], [0.355, 8], [T2 + 0.03, -14], [0.5, 4], [0.585, 16],
                    [T3 + 0.035, -24], [0.78, -16], [1.1, -6], [1.5, 0], [DUR, 0]]),
    "twist": smooth([[0, 0], [0.14, -32], [T1 + 0.03, 28], [0.3, 30], [0.355, 34], [T2 + 0.03, -26], [0.5, -10], [0.585, 0],
                     [T3 + 0.04, 0], [1.5, 0], [DUR, 0]]),
    "offset": smooth([[0, [0, 0, 0]], [0.14, [0, -0.2, 0.3]], [T1 + 0.04, [0, 0, -0.6]], [T2 + 0.04, [0, 0, -1.1]], [0.585, [0, 0.2, -1.2]],
                      [T3 + 0.04, [0, -0.35, -1.7]], [0.9, [0, -0.1, -1.6]], [1.4, [0, 0, -1.5]], [DUR, [0, 0, -1.5]]]),
    "scale": smooth([[0, [1, 1, 1]], [0.14, [1.04, 0.95, 1.04]], [T1 + 0.03, [0.97, 1.04, 0.97]], [0.3, [1, 1, 1]],
                     [0.585, [0.93, 1.1, 0.93]], [T3 + 0.035, [1.12, 0.86, 1.12]], [0.8, [0.98, 1.03, 0.98]], [1.0, [1, 1, 1]], [DUR, [1, 1, 1]]]),
}


def claw_trails(side, t0, t1, seed):
    """Three flame trails, one per claw tip, riding the hand's arc (they ARE the swipe), plus a soft glow ribbon."""
    out = []
    for k, lat in enumerate((-0.38, 0.0, 0.38)):
        hp = hand_path(POSE, t0, t1, side, step=1 / 120, reach=2.35, lateral=lat, fwd=-0.45)
        hot = {"rim": [[0, CRIMSON], [0.6, CRIMSON], [1, EMBER]], "mid": [[0, GOLD], [0.5, ORANGE], [1, CRIMSON]],
               "core": [[0, WHITE_GOLD], [0.4, GOLD], [1, ORANGE]]}
        for lay, w in (("rim", 0.95), ("mid", 0.62), ("core", 0.2)):
            out.append({"type": "trail", "path": hp, "at": hp[0][1], "t0": t0, "t1": t1, "lifetime": 0.26, "faceCamera": True,
                        "width": w, "textures": [f"{st}_{lay}" for st in STRIPS], "swap": 0.06, "color": hot[lay],
                        "lightEmission": LE[lay], "brightness": BR[lay], "textureMode": "Stretch",
                        "transparency": [[0, 0], [0.4, 0.05], [0.8, 0.5], [1, 1]], "widthScale": [[0, 1], [0.6, 0.75], [1, 0.2]]})
    hp = hand_path(POSE, t0, t1, side, step=1 / 120, reach=2.2)
    out += trail_stack({"path": hp, "at": hp[0][1], "t0": t0, "t1": t1, "lifetime": 0.2, "faceCamera": True,
                        "transparency": [[0, 0.45], [1, 1]], "widthScale": [[0, 1], [1, 0.3]]}, {"glow": 1.6}, layers=("glow",))
    return out


def build():
    L = [ambience([0, 0, -4], 0.0, DUR, radius=9, rate=9, seed=91)]

    # ---- claws on fire for the whole combo: tongues + glow riding each hand, claw-tip trails, embers shed off them
    for side, seed in (("R", 101), ("L", 111)):
        hp = hand_path(POSE, 0.02, 1.2, side, reach=2.05)
        for e in emit_stack("flame_tongue", hp[0][1], 0, size=[[0, 2.0], [1, 2.4]], life=0.28, rate=[[0.02, 1.15, 24]], seed=seed,
                            orient="FacingCameraWorldUp", locked=True, transparency=[[0, 0.1], [0.6, 0.2], [1, 1]]):
            e["path"] = hp
            L.append(e)
        L.append(glow_orb(hp[0][1], 0, 3.4, life=0.18, rate=[[0.02, 1.15, 14]], path=hp, locked=True, tr=0.5, seed=seed + 2))
        L.append(embers(hp[0][1], 0, rate=[[0.02, 1.1, 30]], speed=(1, 4), life=(0.35, 0.8), rise=6, grav=0, size=(0.25, 0.5),
                        seed=seed + 1, path=hp))
        L += claw_trails(side, 0.06, 1.15, seed + 5)
    L.append(glow_pool([0.4, 0, -1.4], 0, 7, life=0.25, rate=[[0.02, 1.1, 8]], peak=0.22, seed=121))
    L.append({"type": "emitter", "at": [1.4, 4.2, 0.4], "part": [6, 4, 4], "rate": [[0.0, T1 - 0.03, 34]], "seed": 122, "props": {
        "Texture": "spark_streak", "Color": PALS["fire"]["spark"], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "Size": [[0, 1.6], [1, 0.4]], "Lifetime": [0.12, 0.16], "Speed": [20, 26], "Orientation": "VelocityParallel",
        "Transparency": [[0, 0.3], [1, 0.8]], "ZOffset": 0.3}})

    # ---- the rakes: each hangs where its swipe passed, at the swipe's angle
    rakes = [(T1 + 0.02, [FRONT[0] + 0.3, 3.9, FRONT[2]], -40, 5.6, 0.8, 131),
             (T2 + 0.02, [FRONT[0] - 0.5, 3.6, FRONT[2]], 220, 5.6, 0.75, 141),
             (T3 + 0.02, [FRONT[0] - 0.1, 3.4, FRONT[2] - 0.2], -90, 7.4, 0.85, 151)]
    for t, at, rot, sz, life, seed in rakes:
        L += rake(at, t, sz, life=life, rot=rot, seed=seed)

    # ---- hits 1 and 2 (medium)
    hits, numbers = [], []
    for i, (t, side) in enumerate(((T1, 1), (T2, -1))):
        th = t + 0.02
        L += impact([CHEST[0] + 0.5 * side, CHEST[1], CHEST[2] + 1.0], th, size=5.0, life=0.4, seed=161 + i, rot=40 * i)
        L.append(embers([0.3, 3.4, -6.8], th, n=14, speed=(10, 22), life=(0.4, 0.8), grav=-18, seed=167 + i))
        L.append(glow_pool([0.2, 0, -7.0], th, 6, life=0.35, peak=0.45, seed=169 + i))
        L.append(smoke([0, 4.6, -9.2], th + 0.06, n=3, size=(2.5, 5.5), speed=(1.5, 3), life=(0.9, 1.3), seed=165 + i))
        hits.append({"t": th, "dummy": 0, "dir": [0.25 * side, 0, -1], "power": 0.22})
        numbers.append({"t": th + 0.02, "at": [1.8 * side, 6.4, -8.4], "text": str(48 + 7 * i), "color": GOLD, "vel": [1.5 * side, 8, 0], "size": 1.4})

    # ---- the finisher (BIG)
    th = T3 + 0.02
    L += impact([0.3, 3.0, -7.0], th, size=8.5, life=0.55, seed=171)
    L.append(flare([0.3, 3.2, -6.6], th, size=11, life=0.2, seed=172))
    L.append(streaks([0.2, 2.0, -7.4], th + 0.005, 9, speed=(55, 90), length=(2, 4), spread=35, direction=[180, 0, 0], seed=173))
    L.append(shockwave([0, 0, -8.0], th + 0.01, 6.5, life=0.4, seed=174))
    L.append(dust_ring([0, 0, -8.2], th + 0.01, n=14, speed=(24, 34), size=(3, 6.5), seed=175))
    L.append(glow_pool([0.1, 0, -8.0], th, 11, life=0.9, peak=0.5, seed=176))
    L.append(smoke([0, 3.5, -10.2], th + 0.08, n=6, size=(4, 9), speed=(2, 5), life=(1.2, 1.8), seed=177, spread=50))
    L += fire_streams([0, 0, -7.8], th, 0.4, r0=0.8, r1=6.0, n=6, y0=0.6, rise=3.0, turns=0.9, width=1.2, life=0.38, seed=11)
    L += gouge([0, 0, -9.4], th, size=8.5, rot=90, glow_life=1.25, char_life=3.0, seed=178)
    hits.append({"t": th, "dummy": 0, "dir": [0, 0, -1], "power": 1.0})
    numbers.append({"t": th + 0.03, "at": [1.4, 7.0, -8.8], "text": "164", "color": WHITE_GOLD, "vel": [0.5, 10, -1], "size": 1.8})
    debris = rocks([0, 0, -8.4], th, radius=3.5, count=8, size=0.9, speed=24, crater=False, seed=179)
    for t, at, rot, sz, life, seed in rakes:
        L.append(embers(at, 0, rate=[[t + life * 0.4, t + life * 0.95, 24]], speed=(1, 4), life=(0.5, 1.0), grav=-4,
                        part=[sz * 0.55, 1.2, 0.6], seed=seed + 5))

    # ---- FILLER (fluidity): swirls winding up each claw, wisps shed off the hands, a motion smear on every swing,
    # ember sprays on every hit, heat shimmer over the fight, after-smoke and small flames on the gouges
    hpR = hand_path(POSE, 0.0, 1.2, "R", reach=2.05)
    hpL = hand_path(POSE, 0.0, 1.2, "L", reach=2.05)
    L += swirl(hpR[0][1], 0.0, T1 + 0.02, 3.4, path=hpR, seed=401)
    L += swirl(hpL[0][1], 0.2, T2 + 0.02, 3.4, path=hpL, seed=405)
    L += swirl(hpR[0][1], 0.46, T3 + 0.02, 3.0, path=hpR, seed=409, rot=60)
    L += swirl(hpL[0][1], 0.46, T3 + 0.02, 3.0, path=hpL, seed=413, rot=-60)
    L += wisps(hpR[0][1], 0.05, 1.15, 12, size=2.0, life=0.4, path=hpR, seed=421)
    L += wisps(hpL[0][1], 0.05, 1.15, 12, size=2.0, life=0.4, path=hpL, seed=425)
    for t, at, rot, sz in ((T1 - 0.005, [0.8, 4.0, -3.4], -40, 7.5), (T2 - 0.005, [-0.6, 3.8, -3.4], 220, 7.5),
                           (T3 - 0.005, [1.2, 4.2, -3.6], -95, 8.5), (T3 - 0.005, [-1.2, 4.2, -3.6], -85, 8.5)):
        L += smear(at, t, sz, rot, life=0.2, seed=431 + int(t * 100))
    for i, (t, sz) in enumerate(((T1, 5.0), (T2, 5.0), (T3, 8.5))):
        L += ember_spray([0.3, 3.4, -6.7], t + 0.02, size=sz, life=0.55, seed=441 + i, rot=30 * i)
        L += glint([0.5 - 0.3 * i, 3.6 + 0.2 * i, -6.2], t + 0.02, size=3.5 + 1.5 * (i == 2), life=0.2, seed=471 + i, rot=15 * i)
    L.append(haze([0, 5.5, -6.5], 0.15, DUR, size=10, seed=451))
    L.append(smoke_wisps([0, 0.4, -9.4], T3 + 0.25, DUR, 7, size=3.5, part=[6, 0.2, 2], seed=452))
    L.append(smoke_wisps([0, 3.5, -8.4], T3 + 0.1, DUR - 0.2, 4, size=4.0, part=[1.5, 2, 1.5], seed=453))
    for k, x in enumerate((-1.6, 0.0, 1.6)):
        L += flicker([x, 0, -9.4 + 0.6 * (k - 1)], T3 + 0.06 + 0.04 * k, T3 + 0.95, 1.6 - 0.2 * abs(k - 1), seed=461 + k)

    return {
        "name": "dragon_01_TalonRend", "title": "Talon Rend", "element": "Dragon", "archetype": "claw_combo", "duration": DUR,
        "layers": L, "dummies": [TARGET], "hits": hits, "numbers": numbers, "debris": debris,
        "hitstop": [{"t": T1 + 0.045, "dur": 0.05}, {"t": T2 + 0.045, "dur": 0.05}, {"t": T3 + 0.045, "dur": 0.12}],
        "shakes": [{"t": T1 + 0.02, "amp": 0.12, "dur": 0.12, "freq": 24}, {"t": T2 + 0.02, "amp": 0.12, "dur": 0.12, "freq": 24},
                   {"t": T3 + 0.02, "amp": 0.4, "dur": 0.3, "freq": 22}],
        "lights": [light([0.8, 4, -1], [[0, 0], [0.1, 10], [T3, 12], [1.0, 5], [1.3, 0]], rng=16),
                   light([0.3, 3.4, -6.4], [[T1, 0], [T1 + 0.02, 30], [T1 + 0.17, 0], [T2, 0], [T2 + 0.02, 30], [T2 + 0.17, 0],
                                            [T3, 0], [T3 + 0.02, 44], [T3 + 0.37, 14], [1.3, 0]], rng=18)],
        "pose": POSE,
        "camera": GAMEPLAY_CAM,
        "poster": T3 + 0.08,
    }


write(build(), out_path(os.path.dirname(__file__), "dragon_01_TalonRend"), form="hybrid")
print("wrote dragon_01_TalonRend.json")
