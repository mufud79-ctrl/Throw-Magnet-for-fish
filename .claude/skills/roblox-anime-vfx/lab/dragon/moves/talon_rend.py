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
from kit import _fb
import math

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
        for lay, w in (("rim", 1.5), ("mid", 1.0), ("core", 0.32)):
            out.append({"type": "trail", "path": hp, "at": hp[0][1], "t0": t0, "t1": t1, "lifetime": 0.26, "faceCamera": True,
                        "width": w, "textures": [f"{st}_{lay}" for st in STRIPS], "swap": 0.06, "color": hot[lay],
                        "lightEmission": LE[lay], "brightness": BR[lay], "textureMode": "Stretch",
                        "transparency": [[0, 0], [0.4, 0.05], [0.8, 0.5], [1, 1]], "widthScale": [[0, 1], [0.6, 0.75], [1, 0.2]]})
    hp = hand_path(POSE, t0, t1, side, step=1 / 120, reach=2.2)
    out += trail_stack({"path": hp, "at": hp[0][1], "t0": t0, "t1": t1, "lifetime": 0.2, "faceCamera": True,
                        "transparency": [[0, 0.35], [1, 1]], "widthScale": [[0, 1], [1, 0.3]]}, {"glow": 3.2}, layers=("glow",))
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

    # ---- the rakes: three parallel ANIME SLASHES per swipe (hard-edged crescents, knife tips, white-hot inner line),
    # cut across the target at the swipe's angle - the lead shape of this move
    def claw_slash(at, t, size, rot, seed, life=0.34):
        out = []
        nx, ny = math.cos(math.radians(rot + 90)), math.sin(math.radians(rot + 90))
        for k, off in enumerate((-1, 0, 1)):
            d = off * size * 0.13
            out += emit_stack("anime_slash", [at[0] + nx * d, at[1] + ny * d, at[2] + 0.05 * k], t + 0.012 * k,
                              size=[[0, size * (1 - 0.08 * abs(off))], [1, size * 1.06]], life=life, cool=False, rot=rot,
                              seed=seed + k, z=0.6 + 0.02 * k)
        return out

    hits, numbers = [], []
    for i, (t, side, rot) in enumerate(((T1, 1, -35), (T2, -1, 215))):
        th = t + 0.02
        hp = [CHEST[0] + 0.3 * side, CHEST[1] + 0.3, CHEST[2] + 1.2]
        L += claw_slash(hp, th - 0.01, 7.0, rot, 131 + 10 * i)                      # PRIMARY
        L += glint([hp[0] - 0.4 * side, hp[1] + 0.5, hp[2] + 0.3], th, size=4.2, life=0.2, seed=161 + i)
        sh = emit_stack("ink_shards", hp, th + 0.02, size=[[0, 4.5], [1, 6]], life=0.26, cool=False, seed=163 + i, rot=rot, layers=("rim",), z=0.7)
        for e in sh:
            e["props"]["Color"] = "#1a0806"; e["props"]["LightEmission"] = 0
        L += sh                                                                     # SECONDARY (dark accent)
        L.append({"type": "emitter", "at": hp, "emits": [[th + 0.02, 10]], "seed": 165 + i, "props": {
            "Texture": "needle_bold", "Color": [[0, "#fff6b0"], [0.5, "#ffd21a"], [1, "#ff6a10"]], "LightEmission": 1, "Brightness": 1.5,
            "Size": [[0, 3.2], [1, 0.3]], "Lifetime": [0.14, 0.24], "Speed": [40, 70], "SpreadAngle": [40, 40], "Drag": 7,
            "Orientation": "VelocityParallel", "ZOffset": 0.6}})   # TERTIARY
        L.append(glow_pool([0.2, 0, -7.0], th, 6, life=0.3, peak=0.35, seed=169 + i))
        hits.append({"t": th, "dummy": 0, "dir": [0.25 * side, 0, -1], "power": 0.22})
        numbers.append({"t": th + 0.02, "at": [1.8 * side, 6.4, -8.4], "text": str(48 + 7 * i), "color": GOLD, "vel": [1.5 * side, 8, 0], "size": 1.4})

    # ---- the finisher (BIG): both claws down -> an X of two triple slashes, white speed lines, a burst of needles,
    # haze rolling out, gouges burned into the sand
    th = T3 + 0.02
    fp = [0.2, 3.4, -6.4]
    L += claw_slash([fp[0] - 0.6, fp[1], fp[2]], th - 0.01, 10.5, -70, 151, life=0.42)
    L += claw_slash([fp[0] + 0.6, fp[1], fp[2]], th + 0.015, 10.5, -110, 155, life=0.42)
    sh = emit_stack("ink_shards", fp, th + 0.03, size=[[0, 8], [1, 10]], life=0.3, cool=False, seed=159, rot=20, layers=("rim",), z=0.7)
    for e in sh:
        e["props"]["Color"] = "#1a0806"; e["props"]["LightEmission"] = 0
    L += sh
    L += glint([fp[0], fp[1] + 0.4, fp[2] + 0.4], th + 0.01, size=7, life=0.24, seed=172)
    L.append({"type": "emitter", "at": fp, "emits": [[th + 0.03, 22]], "seed": 173, "props": {
        "Texture": "needle_bold", "Color": [[0, "#fff6b0"], [0.4, "#ffd21a"], [1, "#ff6a10"]], "LightEmission": 1, "Brightness": 1.6,
        "Size": [[0, 4.5], [0.5, 2.5], [1, 0.3]], "Lifetime": [0.18, 0.32], "Speed": [55, 95], "SpreadAngle": [180, 180], "Drag": 7,
        "Orientation": "VelocityParallel", "ZOffset": 0.6}})
    for k in range(4):
        a = k * 2.3
        L += glint([fp[0] + math.cos(a) * 3.2, fp[1] + math.sin(a) * 2.2, fp[2]], th + 0.06 + 0.04 * k, size=2.2 + 0.6 * (k % 2), life=0.18, seed=176 + k)
    L += aura_haze([0, 0, -8.4], th, 1.3, radius=5.5, height=5.0, strength=1.0, seed=180, cloud=0.6)   # OUTSIDE
    L.append(dust_ring([0, 0, -8.2], th + 0.01, n=12, speed=(24, 34), size=(3, 6), seed=175))
    L.append(glow_pool([0.1, 0, -8.0], th, 10, life=0.6, peak=0.35, seed=176))
    L.append({"type": "emitter", "at": [0, 3.5, -10.0], "emits": [[th + 0.08, 6]], "rate": [[th + 0.1, th + 0.6, 6]], "seed": 177,
              "part": [4, 1.5, 2], "props": {"Texture": "haze_soft", "Color": [[0, "#4a2a22"], [1, "#6a4a3e"]], "LightEmission": 0,
        "Brightness": 1, "Size": [[0, 4], [1, 9]], "Lifetime": [0.9, 1.3], "Speed": [2, 4], "SpreadAngle": [30, 30], "Acceleration": [0, 2.5, 0],
        "Drag": 1.2, "Rotation": [0, 360], "RotSpeed": [-10, 10], "FlipbookLayout": "None",
        "Transparency": [[0, 1], [0.15, 0.5], [0.6, 0.65], [1, 1]], "ZOffset": -0.8}})
    L += gouge([0, 0, -9.4], th, size=8.5, rot=90, glow_life=1.25, char_life=3.0, seed=178)
    hits.append({"t": th, "dummy": 0, "dir": [0, 0, -1], "power": 1.0})
    numbers.append({"t": th + 0.03, "at": [1.4, 7.0, -8.8], "text": "164", "color": WHITE_GOLD, "vel": [0.5, 10, -1], "size": 1.8})
    debris = rocks([0, 0, -8.4], th, radius=3.5, count=8, size=0.9, speed=24, crater=False, seed=179)

    # ---- FILLER (fluidity): swirls winding up each claw, wisps shed off the hands, a motion smear on every swing,
    # ember sprays on every hit, heat shimmer over the fight, after-smoke and small flames on the gouges
    hpR = hand_path(POSE, 0.0, 1.2, "R", reach=2.05)
    hpL = hand_path(POSE, 0.0, 1.2, "L", reach=2.05)
    L += wisps(hpR[0][1], 0.05, 1.15, 12, size=2.0, life=0.4, path=hpR, seed=421)
    L += wisps(hpL[0][1], 0.05, 1.15, 12, size=2.0, life=0.4, path=hpL, seed=425)
    for t, at, rot, sz in ((T1 - 0.005, [0.8, 4.0, -3.4], -40, 7.5), (T2 - 0.005, [-0.6, 3.8, -3.4], 220, 7.5),
                           (T3 - 0.005, [1.2, 4.2, -3.6], -95, 8.5), (T3 - 0.005, [-1.2, 4.2, -3.6], -85, 8.5)):
        L += smear(at, t, sz, rot, life=0.2, seed=431 + int(t * 100))
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
