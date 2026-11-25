"""Static Field (N) - lingering zone. Signature: a crackling fence circle on the ground holds a field of crawling arcs
and floating static, and every half second a bolt jumps UP out of the ground somewhere inside.

Beat sheet
  0.00-0.12  rise onto the toes, palm raised and crackling                               (anticipation)
  0.12       PALM SLAM: crouch hard, palm to the sand; crack flash, small starburst; short hit-stop (squash, timing)
  0.15-0.38  the field spreads: a fence circle of 18 curved cel lightning segments races out to 9 studs, overshoots,
             settles; ground arcs light up behind it; big burn scar; navy ion haze pools   (stretch)
  0.40-3.00  floating static drifts up; every 0.5 s a bolt jumps UP out of the ground at a spot inside (5 strikes,
             two of them hit the enemies inside, mini scar under each); the enemy outside is untouched
  3.00-3.30  collapse: the fence shrinks into the centre and pops (crack, dust, final starburst)
Run: python3 lab/thunder/moves/static_field.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

TS = 0.12                     # slam
TC = 3.0                      # collapse
CX, CZ = 0.0, -9.0            # field centre
R = 9.0
PALM = [0.9, 0.4, -2.0]
D1, D2, D3 = [-3.5, 0, -11], [3.5, 0, -6], [12.5, 0, -14]   # two inside, one outside the fence
STRIKES = [(0.5, 4.5, -13.0), (1.0, D1[0], D1[2]), (1.5, -5.0, -5.5), (2.0, D2[0], D2[2]), (2.5, 1.0, -15.5)]
N = 18


def build():
    L = []
    # ---- anticipation + slam
    L += emit_stack("thunder_arc_v2", [1.5, 4.6, -0.6], 0, size=[[0, 2], [1, 2.8]], life=0.1, mode="Loop", rate=[[0.0, TS, 18]], seed=601)
    L += crackle(PALM, TS, size=4.5, life=0.16, seed=602)
    L += ground_ring([PALM[0], 0, PALM[2]], TS, size=9, life=0.35, seed=603)
    L.append(sparks(PALM, TS, 16, speed=(10, 22), seed=604))
    L.append(dust([PALM[0], 0, PALM[2]], TS, n=5, size=(3, 6), seed=605))

    # ---- signature 1: the fence circle (curved segments keyed on the field radius)
    life = TC + 0.3 - (TS + 0.03)
    t0 = TS + 0.03
    k = lambda t: round((t - t0) / life, 4)
    RK = [(0, 0.5, None), (k(0.32), R * 1.12, "outExpo"), (k(0.42), R * 0.97, None), (k(0.5), R, None), (k(TC), R, None), (1, 0.4, "in")]
    for j in range(N):
        a0, a1 = j / N * math.tau, (j + 1) / N * math.tau
        am = (a0 + a1) / 2
        bul = 1 - math.cos(math.pi / N)
        pt = lambda a, r: [round(CX + math.cos(a) * r, 3), 0.45, round(CZ + math.sin(a) * r, 3)]
        keys = lambda a: [[kk, pt(a, r)] + ([ez] if ez else []) for kk, r, ez in RK]
        curve = [[kk, [round(math.cos(am) * r * bul, 3), 0, round(math.sin(am) * r * bul, 3)]] + ([ez] if ez else []) for kk, r, ez in RK]
        ph = (j * 0.37) % 1 * 0.08
        tr = [[0, 0], [k(0.5), 0]]
        for p in range(10):                                    # each segment blinks on its own beat while the field holds
            tp = 0.6 + p * 0.25 + ph
            tr += [[k(tp), 0.0], [k(tp + 0.03), 0.6], [k(tp + 0.06), 0.0]]
        tr += [[k(TC), 0], [1, 0.4]]
        strips = STRIPS[j % 4:] + STRIPS[:j % 4]
        for lay, w in (("rim", 2.2), ("mid", 1.8), ("core", 0.9)):
            L.append({"type": "beam", "from": keys(a0), "to": keys(a1), "curve": curve, "t0": t0, "life": life,
                      "textures": [f"{st}_{lay}" for st in strips], "swap": 0.05, "textureLength": 4, "segments": 6,
                      "color": [[0, WHITE if lay != "rim" else BLUE], [k(0.6), HOT[lay]], [k(TC), COOL[lay][1][1] if lay != "core" else ICE], [1, WHITE]],
                      "lightEmission": LE[lay], "brightness": BR[lay], "width": [[0, w * 1.6], [k(0.45), w, "out"], [1, w * 1.4]], "transparency": tr})

    # ---- signature 2: the field itself: crawling ground arcs (+ indigo outline), floating static, pooled haze, scar
    L.append({"type": "emitter", "at": [CX, 0.3, CZ], "part": [2 * R * 0.95, 0.1, 2 * R * 0.95], "rate": [[0.3, TC, 42]], "seed": 611, "props": {
        "Texture": "thunder_arc_v2_mid", "Color": [[0, WHITE], [0.3, CYAN], [1, BLUE]], "LightEmission": 0.3, "Brightness": 1.3, "Shape": "Disc",
        "Orientation": "VelocityPerpendicular", "Size": [[0, 4.2], [1, 5.4]], "Lifetime": [0.12, 0.2], "Speed": [0.01, 0.01], "Rotation": [0, 360],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.2}})
    L.append({"type": "emitter", "at": [CX, 0.3, CZ], "part": [2 * R * 0.95, 0.1, 2 * R * 0.95], "rate": [[0.3, TC, 16]], "seed": 612, "props": {
        "Texture": "thunder_arc_v2_rim", "Color": INDIGO, "LightEmission": 0, "Brightness": 1, "Shape": "Disc", "Orientation": "VelocityPerpendicular",
        "Size": [[0, 3.6], [1, 4.6]], "Lifetime": [0.14, 0.22], "Speed": [0.01, 0.01], "Rotation": [0, 360], "FlipbookLayout": "Grid4x4",
        "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.1}})
    L.append({"type": "emitter", "at": [CX, 2.5, CZ], "part": [2 * R * 0.9, 4, 2 * R * 0.9], "rate": [[0.35, TC, 44]], "seed": 613, "props": {
        "Texture": "static_sparks", "Color": [[0, ICE], [0.5, CYAN], [1, BLUE]], "LightEmission": 1, "Brightness": 1.4, "Shape": "Cylinder",
        "Size": [[0, 0.6], [0.3, 1.7], [1, 0.4]], "Lifetime": [0.4, 0.8], "Speed": [0.8, 2.2], "SpreadAngle": [25, 25], "Rotation": [0, 360],
        "RotSpeed": [-90, 90], "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [12, 12], "FlipbookStartRandom": True, "ZOffset": 0.3}})
    L.append(haze([CX, 0.7, CZ], 0.3, TC, 26, size=(5, 10), rise=0.6, part=[2 * R * 0.9, 0.6, 2 * R * 0.9], seed=614))
    L += scar([CX, 0, CZ], TS + 0.05, size=17, rot=10, glow_life=TC - 0.2, soot_life=4.0, soot_in=TC)   # glows cyan for the whole field

    # ---- the fence is a WALL: arcs dance up along the whole circle (cel body + indigo outline, independent spawns)
    for tex, col, le, rate, sz, seed in (("thunder_arc_v2_mid", [[0, WHITE], [0.3, CYAN], [1, BLUE]], 0.3, 90, (4.0, 5.4), 615),
                                         ("thunder_arc_v2_core", WHITE, 0.35, 45, (3.4, 4.6), 616),
                                         ("thunder_arc_v2_rim", INDIGO, 0, 40, (4.4, 6.0), 617)):
        L.append({"type": "emitter", "at": [CX, 1.4, CZ], "part": [2 * R, 2.4, 2 * R], "rate": [[0.42, TC, rate]], "seed": seed, "props": {
            "Texture": tex, "Color": col, "LightEmission": le, "Brightness": 1.3 if le else 1, "Shape": "Cylinder", "ShapeStyle": "Surface",
            "Size": [[0, sz[0]], [1, sz[1]]], "Lifetime": [0.08, 0.14], "Speed": [0.01, 0.01], "Rotation": [-30, 30],
            "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [24, 24], "FlipbookStartRandom": True,
            "ZOffset": 0.3 if le else 0.2}})

    # ---- electricity JUMPS: every ~0.12 s a curved arc leaps fence -> ground, ground -> ground, or up into an enemy
    import random
    rnd = random.Random(7)
    def inside(rmax=0.8):
        a_, r_ = rnd.uniform(0, math.tau), R * math.sqrt(rnd.uniform(0.05, 1)) * rmax
        return [round(CX + math.cos(a_) * r_, 2), 0.3, round(CZ + math.sin(a_) * r_, 2)]
    t = 0.45
    j = 0
    while t < TC - 0.05:
        kind = j % 4
        if kind == 0:                                    # fence -> inside
            a_ = rnd.uniform(0, math.tau)
            p0 = [round(CX + math.cos(a_) * R, 2), rnd.uniform(0.4, 1.8), round(CZ + math.sin(a_) * R, 2)]
            p1 = inside(0.6)
        elif kind in (1, 3):                             # ground -> ground
            p0, p1 = inside(), inside()
        else:                                            # ground -> into an enemy's body
            d = (D1, D2)[(j // 4) % 2]
            p0, p1 = inside(0.9), [d[0], rnd.uniform(2.2, 4.2), d[2]]
        span = math.dist(p0, p1)
        L += arc_jump(p0, p1, round(t, 3), life=0.08, bow=[0, round(min(3.5, 0.9 + span * 0.25), 2), 0], width=1.7, seed=j)
        t += rnd.uniform(0.06, 0.1)
        j += 1

    # ---- the up-strikes: every 0.5 s a bolt jumps UP out of the ground (two of them land on the enemies)
    hits, numbers, hs = [], [], []
    for i, (ts, x, z) in enumerate(STRIKES):
        base, top = [x, 0.2, z], [x + 0.6 * math.sin(i * 2.1), 15, z + 0.6 * math.cos(i * 1.7)]
        side = [math.cos(i * 1.9) * 1.5, 0, math.sin(i * 1.9) * 1.5]
        L += arc_jump(base, top, ts, life=0.12, bow=side, width=2.0, seed=i)                       # cel column, instant
        L += arc_jump(base, [top[0] - 1, 13, top[2]], ts + 0.1, life=0.06, bow=[-side[0], 0, -side[2]], width=1.3, seed=i + 1)  # re-strike
        L += emit_stack("thunder_bolt_v2", [x, 8.5, z], ts, size=[[0, 18], [1, 18]], life=0.32, rot=180, seed=631 + i, colors=COOL)
        L += emit_stack("thunder_burst_v2", [x, 0.35, z], ts, size=[[0, 5], [0.2, 9], [1, 9.5]], life=0.3, seed=691 + i,
                        orient="VelocityPerpendicular", colors=COOL)
        L += crackle([x, 1.2, z], ts, size=4.5, life=0.16, seed=641 + i)
        L += ground_ring([x, 0, z], ts, size=7, life=0.35, seed=651 + i)
        L.append(sparks([x, 1, z], ts, 6, speed=(8, 20), seed=661 + i))
        L.append(spark_burst([x, 1.5, z], ts, size=7, life=0.24, seed=671 + i, rot=40 * i))
        L.append(streaks([x, 0.8, z], ts + 0.01, 8, speed=(50, 90), length=(2, 4), spread=50, seed=676 + i))
        L += scar([x, 0, z], ts, size=5, rot=37 * i, glow_life=0.7, soot_life=2.4, soot_in=0.6)
        hit = [d for d in (D1, D2) if d[0] == x and d[2] == z]
        if hit:
            j = [D1, D2].index(hit[0])
            hits.append({"t": ts, "dummy": j, "dir": [0, 0, 1], "power": 0.25})
            hs.append({"t": ts + 0.012, "dur": 0.05})
            numbers.append({"t": ts + 0.02, "at": [x + 1, 6.4, z], "text": "38", "color": CYAN, "vel": [3, 13, 0], "size": 2.0, "life": 0.9})
    # the two inside keep crackling while the field holds
    for j, d in enumerate((D1, D2)):
        L += emit_stack("thunder_arc_v2", [d[0], 3.4, d[2]], 0.4, size=[[0, 3.6], [1, 4.2]], life=0.14, mode="Loop", rate=[[0.42, TC, 6]],
                        seed=671 + j, colors=COOL, transparency=[[0, 0.1], [0.6, 0.35], [1, 1]])

    # ---- collapse
    L += crackle([CX, 1.5, CZ], TC + 0.28, size=9, life=0.22, seed=681)
    L.append(flare([CX, 2, CZ], TC + 0.28, size=20, life=0.3, seed=686))
    L += impact_v3([CX, 2, CZ], TC + 0.28, size=12, life=0.45, seed=687)
    L.append(streaks([CX, 1.5, CZ], TC + 0.29, 30, speed=(60, 120), length=(3, 7), spread=80, seed=688))
    L += emit_stack("thunder_burst_v2", [CX, 2, CZ], TC + 0.28, size=[[0, 6], [0.2, 11], [1, 12]], life=0.4, seed=682)
    L += ground_ring([CX, 0, CZ], TC + 0.28, size=16, life=0.5, seed=683)
    L.append(dust([CX, 0, CZ], TC + 0.28, n=10, size=(4, 10), seed=684))
    L.append(smoke_burst([CX, 1.5, CZ], TC + 0.3, n=5, seed=685))

    dur = 4.0
    kd = lambda t: round(t / dur, 4)
    return {
        "name": "thunder_06_StaticField", "title": "Static Field", "element": "Thunder", "archetype": "lingering_zone", "duration": dur,
        "layers": L, "dummies": [D1, D2, D3], "hits": hits, "numbers": numbers,
        "hitstop": [{"t": TS + 0.012, "dur": 0.05}] + hs,
        "shakes": [{"t": TS, "amp": 0.4, "dur": 0.25, "freq": 24}] + [{"t": ts, "amp": 0.18, "dur": 0.15, "freq": 28} for ts, _, _ in STRIKES]
                  + [{"t": TC + 0.28, "amp": 0.5, "dur": 0.3, "freq": 22}],
        "lights": [light(PALM, [[0, 0], [TS - 0.005, 4], [TS, 14], [TS + 0.25, 0]], rng=10),
                   light([CX, 2, CZ], [[0.2, 0], [0.4, 5]] + [[round(0.45 + i * 0.08, 3), (8 if i % 3 == 0 else 3 if i % 3 == 1 else 6)] for i in range(31)]
                         + [[TC, 5], [TC + 0.3, 14], [TC + 0.7, 0]], rng=18)]
                  + [light([x, 3, z], [[ts - 0.005, 0], [ts, 16], [ts + 0.2, 0]], rng=10) for ts, x, z in STRIKES],
        "grade": [[0, 0, 0, 0, "#ffffff"], [TS, -0.03, 0.12, 0.04, "#e6eeff"], [TC, -0.03, 0.12, 0.04, "#e6eeff"], [TC + 0.6, 0, 0, 0, "#ffffff"]],
        "pose": {"lean": [[0, 0], [0.08, -10, "out"], [TS, 38, "in"], [TS + 0.4, 30], [0.75, 0]],
                 "armR": [[0, 0], [0.08, 150, "out"], [TS, 60, "in"], [TS + 0.4, 55], [0.8, 0]],
                 "armL": [[0, 0], [0.08, -30, "out"], [TS, 20], [0.8, 0]],
                 "offset": [[0, [0, 0, 0]], [0.08, [0, 0.35, 0], "out"], [TS, [0, -0.7, 0], "in"], [TS + 0.4, [0, -0.6, 0]], [0.8, [0, 0, 0]]],
                 "scale": [[0, [1, 1, 1]], [0.08, [0.95, 1.07, 0.95]], [TS, [1.1, 0.85, 1.1]], [TS + 0.1, [1, 1, 1]]]},
        "camera": {"pos": [[0, [11, 8, 4]], [kd(TS), [11.4, 8.2, 3.6]], [kd(TS) + 0.01, [13.5, 11, 3], "outExpo"], [kd(TC), [12.5, 10.6, 4]], [1, [12.2, 10.4, 4.2]]],
                   "look": [[0, [0, 2.5, -4]], [kd(TS) + 0.01, [0, 1.6, -8.5], "outExpo"], [1, [0, 1.6, -9]]],
                   "fov": [[0, 56], [kd(TS), 55], [kd(TS) + 0.01, 58, "out"], [1, 58]]},
        "poster": 1.02,
    }


write(build(), os.path.join(os.path.dirname(__file__), "thunder_06_StaticField.json"))
print("wrote thunder_06_StaticField.json")
