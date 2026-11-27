"""Comet Dive (full X) - a burning comet dive. Signature: the COMET - the dragon dives head-first wrapped in a fire mass
with a long straight tail of flame spikes - then a huge crater blast and a MOLTEN ROCK RAIN.

Beat sheet
  0.00-0.65  the dragon climbs in a tight helix (whiskers whip), embers peel off           (anticipation: wind-up)
  0.65-0.82  apex: it tightens into a coil and hangs, nose rolls down, a glint at the head  (anticipation: hang)
  0.82-1.22  DIVE: a fire mass on the head (billows + backward flame spikes + glow) stretched along the dive, a long
             straight trail and gold needles streaming up behind it                       (squash & stretch)
  1.22       IMPACT: one mono frame; hit-stop 0.18; a radial star of huge spikes + a spike crown, white speed lines,
             black ink, needle burst, the big crater (radius 10) with molten cracks, warm haze rolling far out
  1.25-2.30  molten rock rain: glowing lava drops flung up on arcs, each landing in a small ember splash
  1.55       the dragon bursts back up out of the smoke on the far side and swims up to a hover
Camera: wide and low near the impact, so the comet comes in from the top of the frame.
Run: python3 lab/dragon/moves/comet_dive.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

TA, TD, TI, TU = 0.65, 0.82, 1.22, 1.55
DUR = 2.6
G = [0, 0, -14]
TARGETS = [[-4.0, 0, -12.5], [4.2, 0, -15.0], [0.6, 0, -18.5]]
CAM = {"pos": [[0, [26, 9, 10]], [1, [26, 9, 10]]], "look": [[0, [0, 13, -12]], [1, [0, 13, -12]]], "fov": [[0, 66], [1, 66]]}

# head flight: comes in low from the left, climbs a helix, coils at the apex, dives straight down into G, runs on
# underground (hidden by the floor), bursts back up on the far side and swims up to a hover
CP = [(-2.0, [-20, 6, -4]), (-1.0, [-10, 8, -10]), (0.0, [-2, 9, -12]), (0.2, [3, 13, -14]), (0.4, [0, 19, -18]),
      (0.55, [-4, 24, -14]), (TA, [0, 27, -10]), (0.74, [4, 29, -13]), (TD, [0.5, 30, -15]), (0.9, [0, 25, -14.2]),
      (TI, [0, 0.5, -14]), (1.32, [0, -6, -14]), (1.45, [5, -6, -18]), (TU, [8, 1, -20]), (1.8, [9, 10, -21]),
      (2.2, [5, 15, -24]), (DUR + 0.4, [-4, 16, -26])]


def head(t):
    return cr_point(CP, t)


def build():
    hp = cr_path(CP, -2.0, DUR + 0.4)
    L = [ambience([0, 0, -12], 0, DUR, radius=16, rate=10, seed=1201)]

    # ---- climb: embers + wisps peel off the body, a glow riding the head
    L.append(glow_orb(head(0), 0, 6, life=0.25, rate=[[0.0, TI, 14]], path=hp, locked=True, tr=0.45, seed=1202))
    L += wisps(head(0), 0.0, TD, 20, size=3.2, life=0.5, path=hp, seed=1203)
    L.append(embers(head(0), 0, rate=[[0.0, TD, 40]], speed=(2, 6), life=(0.5, 1.0), grav=-6, path=hp, seed=1204))
    # ---- apex: glint + swirl as it hangs
    L += glint(head(TA + 0.08), TA + 0.08, size=7, life=0.22, seed=1205)
    L += swirl(head(TA), TA - 0.05, TD + 0.02, 7, path=hp, seed=1206)

    # ---- the COMET: a fire mass on the head, flame spikes pointing back up the dive, a long trail, needles
    dp = cr_path(CP, TD, TI + 0.01, step=1 / 120)
    for e in billow(head(TD), TD, 7.5, life=0.22, seed=1211, grow=1.25):
        e.pop("emits", None); e["rate"] = [[TD + 0.02, TI, 40]]; e["path"] = dp
        L.append(e)
    for e in emit_stack("anime_flame_spike", head(TD), TD + 0.03, size=[[0, 10], [1, 12]], life=0.2, rate=[[TD + 0.03, TI - 0.01, 45]],
                        cool=False, seed=1212, orient="FacingCameraWorldUp", z=0.4, transparency=[[0, 0], [0.6, 0.1], [1, 1]]):
        e["path"] = [[t, [p[0], p[1] + 4.5, p[2]]] for t, p in dp]
        e["part"] = [2.5, 1.0, 2.5]
        e["props"]["Rotation"] = [-14, 14]
        L.append(e)
    L += trail_stack({"path": dp, "at": dp[0][1], "t0": TD, "t1": TI, "lifetime": 0.3, "faceCamera": True,
                      "transparency": [[0, 0], [0.5, 0.2], [1, 1]], "widthScale": [[0, 1], [1, 0.35]], "textureMode": "Stretch"},
                     {"glow": 9.0, "rim": 5.5, "mid": 3.6, "core": 1.0}, cool=False)
    L.append(needles(head(TD), 0, 0, speed=(30, 50), size=6, life=(0.15, 0.25), spread=10, seed=1213, rot=[0, 0, 0],
                     rate=[[TD + 0.02, TI, 90]], part=[3, 1, 3], path=dp))
    L.append(dark_haze(head(TD), 0, n=0, rate=[[TD + 0.05, TI, 14]], size=(4, 9), part=(3, 2, 3), tr=0.6, seed=1214))
    L[-1]["path"] = [[t, [p[0], p[1] + 6, p[2]]] for t, p in dp]

    # ---- IMPACT (BIG)
    T = TI
    for j in range(16):                                         # PRIMARY: a radial star of huge spikes
        rot = j / 16 * 360 + 6 * math.sin(j * 2.1)
        ln = 20 + 7 * ((j * 7) % 4) / 3
        L += emit_stack("anime_flame_spike", [G[0], 3.5, G[2]], T + 0.004 * (j % 3), size=[[0, ln * 0.6], [0.2, ln], [1, ln * 1.05]],
                        life=0.42 + 0.06 * (j % 2), cool=False, rot=rot, seed=1221 + j, z=0.5)
    for k in range(14):                                         # ... and a crown standing round the crater
        a = k / 14 * 2 * math.pi + 0.2 * math.sin(k * 3.1)
        r = 4 + 5 * ((k * 7) % 5) / 4
        h = 15 - 0.9 * r + 2.5 * ((k * 3) % 4) / 3
        p = [G[0] + math.cos(a) * r, 0, G[2] + math.sin(a) * r]
        L += emit_stack("anime_flame_spike", [p[0], h * 0.42, p[2]], T + 0.02 + 0.02 * (r - 4) / 5, size=[[0, h * 0.95], [1, h * 1.05]],
                        life=0.6 + 0.3 * (r - 4) / 5, cool=False, rot=-math.degrees(math.atan2(math.cos(a), 1.0)) * 0.5, seed=1241 + k,
                        orient="FacingCameraWorldUp", z=0.04 * (k % 5))
    L.append(speed_lines([G[0], 4, G[2]], T + 0.03, 34, life=0.26, seed=1251))     # SECONDARY
    L += ink([G[0], 4, G[2]], T + 0.03, 18, rot=25, life=0.32, seed=1252)
    L += glint([G[0], 5, G[2] + 1], T + 0.02, size=15, life=0.26, seed=1253)
    L.append(needles([G[0], 2, G[2]], T + 0.03, 34, speed=(80, 140), size=8, life=(0.25, 0.45), seed=1254))   # TERTIARY
    for k in range(5):
        a = k * 2.4
        r = 6 + 3 * ((k * 5) % 3) / 2
        L += glint([G[0] + math.cos(a) * r, 3 + 4 * ((k * 3) % 4) / 3, G[2] + math.sin(a) * r], T + 0.07 + 0.04 * k, size=3.5 + (k % 3),
                   life=0.2, seed=1255 + k)
    L += aura_haze(G, T + 0.01, 2.2, radius=16.0, height=11.0, strength=1.3, seed=1260, cloud=0.6)   # OUTSIDE
    cr = crater(G, T, radius=10.0, life=DUR - T, slabs=20, seed=1270)                                  # MASS
    L += [x for x in cr if "kind" not in x]
    L += molten_crack(G, T + 0.03, size=30, rot=40, glow_life=1.6, char_life=DUR - T, seed=1271, flames=False)
    dr = dust_ring(G, T + 0.02, n=22, speed=(45, 60), size=(5, 10), seed=1272)
    dr["props"]["Transparency"] = [[0, 0.35], [0.6, 0.55], [1, 1]]
    L.append(dr)
    L.append(glow_pool(G, T, 24, life=0.6, peak=0.3, seed=1273))
    L.append(dark_haze([G[0], 6, G[2]], T + 0.1, n=14, rate=[[T + 0.15, T + 0.9, 10]], size=(7, 16), life=(1.2, 1.7), part=(8, 3, 8), tr=0.45,
                       seed=1274, outward=6))

    # ---- molten rock rain: glowing drops flung up on arcs, landing in small ember splashes
    L.append({"type": "emitter", "at": [G[0], 2, G[2]], "emits": [[T + 0.04, 26]], "rate": [[T + 0.1, T + 0.6, 20]], "seed": 1281, "part": [4, 1, 4],
              "props": {"Texture": "lava_drops", "Color": [[0, "#fff6b0"], [0.3, "#ffb02a"], [0.7, "#e0401a"], [1, "#6a100a"]], "LightEmission": 0.9,
        "Brightness": 1.5, "Size": [[0, 1.4], [1, 0.9]], "Lifetime": [1.0, 1.4], "Speed": [30, 48], "SpreadAngle": [40, 40],
        "Acceleration": [0, -55, 0], "Drag": 0.3, "Rotation": [0, 360], "RotSpeed": [-200, 200], "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random",
        "FlipbookFramerate": [0.01, 0.01], "FlipbookStartRandom": True, "ZOffset": 0.4}})
    for k in range(10):
        a = k * 2.39 + 0.4
        r = 9 + 6 * ((k * 3) % 5) / 4
        p = [G[0] + math.cos(a) * r, 0, G[2] + math.sin(a) * r]
        tl = T + 0.9 + 0.06 * k
        L.append(embers([p[0], 0.4, p[2]], tl, n=10, speed=(6, 12), life=(0.3, 0.6), grav=-20, spread=50, seed=1291 + k))
        L += glint([p[0], 0.8, p[2]], tl, size=2.0, life=0.16, seed=1301 + k)
        L.append(scorch(p, tl, size=2.4, life=DUR - tl + 0.1, seed=1311 + k))

    # ---- the dragon bursts back up out of the smoke
    up = head(TU)
    L += emit_stack("anime_flame_spike", [up[0], 3, up[2]], TU - 0.02, size=[[0, 8], [1, 9]], life=0.35, cool=False, seed=1321,
                    orient="FacingCameraWorldUp", z=0.3)
    L.append(dust_ring([up[0], 0, up[2]], TU - 0.02, n=10, speed=(20, 28), size=(3, 6), seed=1322))
    L += wisps(head(TU), TU, 2.2, 18, size=3.0, life=0.5, path=hp, seed=1323)
    L += flicker([G[0], 0, G[2]], T + 0.4, DUR, 4.5, seed=1324)

    debris = rocks(G, T + 0.01, radius=8, count=14, size=1.4, speed=42, crater=False, seed=1329) + [x for x in cr if "kind" in x]
    hits, numbers = [], []
    for i, q in enumerate(TARGETS):
        th = T + 0.02 + 0.01 * i
        d = [q[0] - G[0], 0, q[2] - G[2]]
        n = math.hypot(d[0], d[2]) or 1
        hits.append({"t": th, "dummy": i, "dir": [R(d[0] / n), 0, R(d[2] / n)], "power": 1.5})
        numbers.append({"t": th + 0.03, "at": [q[0], 7.5, q[2]], "text": str(268 + 19 * i), "color": WHITE_GOLD, "vel": [0, 11, 0], "size": 2.1})

    t0 = -2.0
    life = DUR + 0.4 - t0
    jaw = [[0, 6], [(TA - t0) / life, 10], [(TD - t0) / life, 40], [(TI + 0.05 - t0) / life, 40], [(TI + 0.4 - t0) / life, 8], [1, 6]]
    L.append(dragon(hp, t0, life, jaw=R(jaw, 3), tracks=whisker_tracks(DUR + 0.5)))

    return {
        "name": "dragon_08_CometDive", "title": "Comet Dive", "element": "Dragon", "archetype": "comet_dive", "duration": DUR,
        "caster": False, "layers": L, "dummies": TARGETS, "hits": hits, "numbers": numbers, "debris": debris,
        "hitstop": [{"t": T + 0.03, "dur": 0.18}],
        "impact": [{"t": T + 0.025, "dur": 0.05, "mode": "mono"}],
        "shakes": [{"t": T + 0.02, "amp": 0.9, "dur": 0.5, "freq": 18}],
        "lights": [light(head(TD), [[TD, 0], [TD + 0.1, 24], [TI, 30], [TI + 0.1, 0]], rng=26, path=dp),
                   light([G[0], 4, G[2]], [[T, 0], [T + 0.02, 44], [T + 0.6, 18], [DUR, 4]], rng=36)],
        "camera": CAM,
        "poster": T + 0.08,
    }


write(build(), out_path(os.path.dirname(__file__), "dragon_08_CometDive"), form="full")
print("wrote dragon_08_CometDive.json")
