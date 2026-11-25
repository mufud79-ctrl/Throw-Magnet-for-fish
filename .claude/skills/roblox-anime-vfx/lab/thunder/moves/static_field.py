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
        "Orientation": "VelocityPerpendicular", "Size": [[0, 3.2], [1, 4.2]], "Lifetime": [0.12, 0.2], "Speed": [0.01, 0.01], "Rotation": [0, 360],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.2}})
    L.append({"type": "emitter", "at": [CX, 0.3, CZ], "part": [2 * R * 0.95, 0.1, 2 * R * 0.95], "rate": [[0.3, TC, 16]], "seed": 612, "props": {
        "Texture": "thunder_arc_v2_rim", "Color": INDIGO, "LightEmission": 0, "Brightness": 1, "Shape": "Disc", "Orientation": "VelocityPerpendicular",
        "Size": [[0, 3.6], [1, 4.6]], "Lifetime": [0.14, 0.22], "Speed": [0.01, 0.01], "Rotation": [0, 360], "FlipbookLayout": "Grid4x4",
        "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.1}})
    L.append({"type": "emitter", "at": [CX, 2.5, CZ], "part": [2 * R * 0.9, 4, 2 * R * 0.9], "rate": [[0.35, TC, 26]], "seed": 613, "props": {
        "Texture": "static_sparks", "Color": [[0, ICE], [0.5, CYAN], [1, BLUE]], "LightEmission": 1, "Brightness": 1.4, "Shape": "Cylinder",
        "Size": [[0, 0.4], [0.3, 1.0], [1, 0.3]], "Lifetime": [0.5, 0.9], "Speed": [0.6, 1.6], "SpreadAngle": [25, 25], "Rotation": [0, 360],
        "RotSpeed": [-90, 90], "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [12, 12], "FlipbookStartRandom": True, "ZOffset": 0.3}})
    L.append(haze([CX, 0.7, CZ], 0.3, TC, 26, size=(5, 10), rise=0.6, part=[2 * R * 0.9, 0.6, 2 * R * 0.9], seed=614))
    L += scar([CX, 0, CZ], TS + 0.05, size=17, rot=10, glow_life=1.2, soot_life=3.6)

    # ---- the up-strikes: every 0.5 s a bolt jumps UP out of the ground (two of them land on the enemies)
    hits, numbers, hs = [], [], []
    for i, (ts, x, z) in enumerate(STRIKES):
        base, top = [x, 0.2, z], [x + 0.6 * math.sin(i * 2.1), 15, z + 0.6 * math.cos(i * 1.7)]
        L.append({"type": "bolt", "from": base, "to": top, "t0": ts, "life": 0.07, "color": CYAN, "thickness": 0.28, "jitter": 1.0,
                  "segments": 12, "flicker": 0.034, "branch": 0.25, "seed": 621 + i, "brightness": 2.2})
        L += emit_stack("thunder_bolt_v2", [x, 7.5, z], ts, size=[[0, 15], [1, 15]], life=0.3, rot=180, seed=631 + i, colors=COOL)
        L += crackle([x, 1.2, z], ts, size=4.5, life=0.16, seed=641 + i)
        L += ground_ring([x, 0, z], ts, size=7, life=0.35, seed=651 + i)
        L.append(sparks([x, 1, z], ts, 12, speed=(8, 20), seed=661 + i))
        L += scar([x, 0, z], ts, size=5, rot=37 * i, glow_life=0.7, soot_life=2.0)
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
                   light([CX, 2, CZ], [[0.2, 0], [0.4, 5], [TC, 5], [TC + 0.3, 14], [TC + 0.7, 0]], rng=16)]
                  + [light([x, 3, z], [[ts - 0.005, 0], [ts, 16], [ts + 0.2, 0]], rng=10) for ts, x, z in STRIKES],
        "grade": [[0, 0, 0, 0, "#ffffff"], [TS, -0.06, 0.12, -0.03, "#e2eaff"], [TC, -0.06, 0.12, -0.03, "#e2eaff"], [TC + 0.6, 0, 0, 0, "#ffffff"]],
        "pose": {"lean": [[0, 0], [0.08, -10, "out"], [TS, 38, "in"], [TS + 0.4, 30], [0.75, 0]],
                 "armR": [[0, 0], [0.08, 150, "out"], [TS, 60, "in"], [TS + 0.4, 55], [0.8, 0]],
                 "armL": [[0, 0], [0.08, -30, "out"], [TS, 20], [0.8, 0]],
                 "offset": [[0, [0, 0, 0]], [0.08, [0, 0.35, 0], "out"], [TS, [0, -0.7, 0], "in"], [TS + 0.4, [0, -0.6, 0]], [0.8, [0, 0, 0]]],
                 "scale": [[0, [1, 1, 1]], [0.08, [0.95, 1.07, 0.95]], [TS, [1.1, 0.85, 1.1]], [TS + 0.1, [1, 1, 1]]]},
        "camera": {"pos": [[0, [14, 10, 6]], [kd(TS), [14.5, 10.3, 5.5]], [kd(TS) + 0.01, [18, 15, 7], "outExpo"], [kd(TC), [16, 15, 9]], [1, [15.5, 14.5, 9.5]]],
                   "look": [[0, [0, 2.5, -4]], [kd(TS) + 0.01, [0, 1, -8.5], "outExpo"], [1, [0, 1, -9]]],
                   "fov": [[0, 55], [kd(TS), 54], [kd(TS) + 0.01, 52, "out"], [1, 52]]},
        "poster": 1.02,
    }


write(build(), os.path.join(os.path.dirname(__file__), "thunder_06_StaticField.json"))
print("wrote thunder_06_StaticField.json")
