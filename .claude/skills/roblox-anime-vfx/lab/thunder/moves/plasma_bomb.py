"""Plasma Bomb (M) - hold-charge lob. Signature: chain lightning; after the blast, arcs hop from target to target.

Beat sheet
  0.00-0.68  HOLD: a plasma orb grows in the forward palm; arcs crackle round it, sparks pulled in, radiating rays
             pulse (the anime charge star); the caster leans back                        (anticipation)
  0.66-0.70  the orb pinches small, then swells, right before release                   (squash)
  0.70       LOB: arm snaps with overshoot; the orb flies a high parabola, stretched along its flight, dragging a
             cel lightning ribbon and dripping arcs                                      (arcs, stretch)
  1.20       DETONATION at enemy A: plasma burst, crackle, ground starburst, dust, smoke; hit-stop 0.08
  1.32/1.44  CHAIN: doubled curved arcs hop A -> B -> C; crackle + hit-stop 0.04 + number on each
  1.40-2.40  chain arcs flicker and cool; static crawls on all three; scars under each; settle
Run: python3 lab/thunder/moves/plasma_bomb.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

TR = 0.70                 # release
TD = 1.20                 # detonation
HOPS = [1.32, 1.44]
HAND = [1.4, 4.4, -2.0]
A, B, Cc = [0, 0, -20], [-8, 0, -27], [7, 0, -31]
IMPACT = [0, 1.3, -19.2]
chest = lambda d: [d[0], 3.4, d[2]]


def orb_path():
    P = [[0.0, HAND], [TR, HAND]]
    n = 16
    for i in range(1, n + 1):
        u = i / n
        p = [HAND[j] + (IMPACT[j] - HAND[j]) * u for j in range(3)]
        p[1] += 7.0 * math.sin(math.pi * u) - 1.2 * u * u    # high lob, dropping in
        P.append([round(TR + (TD - TR) * u, 4), [round(v, 3) for v in p]])
    return P


def build():
    P = orb_path()
    L = []
    # ---- the orb: plasma_orb stack locked to the path (one particle each layer, alive through hold + flight)
    k = lambda t: round(t / TD, 4)
    size = [[0, 0.5], [k(0.45), 3.4], [k(0.62), 4.0], [k(0.68), 2.7], [k(TR), 4.6], [k(TR + 0.1), 5.2], [1, 5.6]]   # heavier in flight
    for e in emit_stack("plasma_orb", HAND, 0.0, size=size, life=TD, mode="Loop", seed=701):
        e["path"] = P
        e["props"].update({"LockedToPart": True, "FlipbookFramerate": [24, 24],
                           "Squash": [[0, 0], [k(TR), 0], [k(TR + 0.05), 0.55], [k(TD - 0.05), 0.4], [1, 0.2]]})
        if e["props"]["Texture"].endswith("_rim"):
            e["props"]["Color"] = INDIGO
        L.append(e)
    L.append({"type": "emitter", "at": HAND, "path": P, "emits": [[0.0, 1]], "seed": 704, "props": {
        "Texture": "plasma_orb_glow", "Color": [[0, CYAN], [1, BLUE]], "LightEmission": 1, "Brightness": 1.2, "LockedToPart": True,
        "Size": [[0, 1.5], [k(0.6), 7], [k(0.68), 5], [k(TR), 8.5], [1, 9.5]], "Lifetime": [TD, TD], "Speed": [0.01, 0.01],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "Loop", "FlipbookFramerate": [20, 20], "Transparency": 0.35, "ZOffset": -0.2}})
    # hold: arcs round the orb, sparks pulled in, pulsing charge rays (god_rays), haze
    L += emit_stack("thunder_arc_v2", HAND, 0.02, size=[[0, 3], [1, 4.4]], life=0.12, mode="Loop", rate=[[0.05, TR, 20]], seed=702)
    L.append({"type": "emitter", "at": HAND, "part": [8, 8, 8], "rate": [[0.05, TR - 0.03, 70]], "seed": 703, "props": {
        "Texture": "static_sparks", "Color": [[0, BLUE], [1, WHITE]], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere",
        "ShapeInOut": "Inward", "ShapeStyle": "Surface", "Size": [[0, 0.5], [1, 1.1]], "Lifetime": [0.12, 0.16], "Speed": [26, 32],
        "Orientation": "VelocityParallel", "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [25, 25],
        "FlipbookStartRandom": True, "ZOffset": 0.3}})
    for i, tr in enumerate([0.2, 0.34, 0.46, 0.56, 0.64]):
        L += emit_stack("god_rays", HAND, tr, size=[[0, 5 + i], [1, 8 + i * 1.4]], life=0.16, colors={"glow": BLUE, "rim": INDIGO, "mid": CYAN, "core": WHITE},
                        rot=23 * i, seed=711 + i, layers=("glow", "mid", "core"))
    L.append(haze([0, 1, 0], 0.1, TR, 14, size=(3, 6), rise=1.2, part=[5, 1, 5], seed=716))

    # ---- release + flight: snap crackle, ribbon trail behind the orb, arcs dripping off it
    L += crackle(HAND, TR, size=4.5, life=0.16, seed=721)
    base = {"path": P, "t0": TR, "t1": TD, "lifetime": 0.3, "faceCamera": True, "textureMode": "Static", "textureLength": 8,
            "widthScale": [[0, 1.2], [0.2, 1.0], [1, 0.2]]}
    L += trail_stack(base, {"glow": 4.2, "rim": 2.6, "mid": 2.3, "core": 1.2},
                     transparency={"glow": [[0, 0.3], [1, 1]], "rim": [[0, 0], [1, 1]], "mid": [[0, 0], [0.6, 0.3], [1, 1]], "core": [[0, 0], [0.5, 0.3], [1, 1]]})
    L.append({"type": "emitter", "at": HAND, "path": P, "rate": [[TR, TD, 40]], "seed": 722, "props": {
        "Texture": "thunder_arc_v2_mid", "Color": [[0, WHITE], [0.4, CYAN], [1, BLUE]], "LightEmission": 0.35, "Brightness": 1.3,
        "Size": [[0, 2.2], [1, 2.8]], "Lifetime": [0.1, 0.16], "Speed": [1, 4], "SpreadAngle": [180, 180], "Acceleration": [0, -18, 0],
        "Rotation": [0, 360], "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.3}})

    # ---- detonation
    L += emit_stack("plasma_orb", IMPACT, TD, size=[[0, 4], [0.25, 11], [1, 13]], life=0.32, seed=731,
                    transparency=[[0, 0], [0.4, 0.2], [1, 1]], squash=[[0, -0.35], [0.2, 0.2], [0.5, 0]])
    L += emit_stack("thunder_burst_v2", IMPACT, TD, size=[[0, 8], [0.2, 14], [1, 15]], life=0.42, seed=732)
    L += crackle(IMPACT, TD, size=9, life=0.22, seed=733)
    L += ground_ring(A, TD, size=18, life=0.5, seed=734)
    L.append(dust(A, TD, n=9, size=(4, 10), seed=735))
    L.append(smoke_burst([0, 2, -19.5], TD + 0.02, n=5, seed=736))
    L.append(sparks(IMPACT, TD, 30, speed=(14, 32), seed=737))
    L += scar(A, TD, size=12, rot=15, glow_life=1.0, soot_life=3.0, soot_in=0.8)

    # ---- signature: chain lightning hops A -> B -> C (doubled curved arcs that linger, flicker and cool)
    hits = [{"t": TD, "dummy": 0, "dir": [0, 0, -1], "power": 0.6}]
    hs = [{"t": TD + 0.015, "dur": 0.08}]
    numbers = [{"t": TD + 0.02, "at": [2.5, 6.0, -19], "text": "120", "color": CYAN, "vel": [6, 12, 2], "size": 2.6, "life": 0.3}]
    links = [(A, B, HOPS[0], 1), (B, Cc, HOPS[1], 2)]
    for n, (p, q, th, di) in enumerate(links):
        a, b = chest(p), chest(q)
        for s_, (bow, w, life) in enumerate([((0, 3.0, 0), 2.8, 0.42), ((0, -1.2, 0), 1.8, 0.3), ((0, 1.2, 1.5), 1.3, 0.24)]):
            for e in arc_jump(a, b, th, life=life, bow=bow, width=w, seed=n * 2 + s_):
                e["transparency"] = [[0, 0], [0.18, 0], [0.24, 0.75], [0.3, 0], [0.48, 0.6], [0.54, 0.05], [1, 1]]
                e["color"] = COOL[[x for x in ("rim", "mid", "core") if e["textures"][0].endswith(x)][0]]
                L.append(e)
        L += crackle(b, th, size=5.5, life=0.18, seed=741 + n)
        L.append(sparks(b, th, 14, speed=(10, 22), seed=751 + n))
        L += scar([q[0], 0, q[2]], th, size=7, rot=50 * n, glow_life=0.8, soot_life=2.4, soot_in=0.6)
        hits.append({"t": th, "dummy": di, "dir": [round((q[0] - p[0]) / 12, 2), 0, -0.6], "power": 0.35})
        hs.append({"t": th + 0.012, "dur": 0.04})
        numbers.append({"t": th + 0.02, "at": [q[0] + 1, 6, q[2]], "text": "70", "color": CYAN, "vel": [2, 13, 0], "size": 2.2})
    # static clings to all three
    for j, d in enumerate((A, B, Cc)):
        t0 = TD if j == 0 else HOPS[j - 1]
        L += emit_stack("thunder_arc_v2", chest(d), t0, size=[[0, 3.8], [1, 4.4]], life=0.14, mode="Loop", rate=[[t0 + 0.02, t0 + 0.8, 9]],
                        seed=761 + j, colors=COOL, transparency=[[0, 0], [0.6, 0.3], [1, 1]])
    L.append(haze([0, 1, -25], TD + 0.1, TD + 1.0, 18, size=(5, 10), rise=2.5, part=[16, 1, 12], seed=771))

    dur = 2.5
    kd = lambda t: round(t / dur, 4)
    return {
        "name": "thunder_07_PlasmaBomb", "title": "Plasma Bomb", "element": "Thunder", "archetype": "charged_lob_chain", "duration": dur,
        "layers": L, "dummies": [A, B, Cc], "hits": hits, "numbers": numbers, "hitstop": hs,
        "debris": [{"kind": "fling", "at": A, "t": TD, "count": 9, "size": 1.2, "speed": 26, "life": 1.4, "seed": 77}],
        "shakes": [{"t": TR, "amp": 0.2, "dur": 0.12, "freq": 26}, {"t": TD, "amp": 0.7, "dur": 0.4, "freq": 22}]
                  + [{"t": t, "amp": 0.25, "dur": 0.15, "freq": 28} for t in HOPS],
        "lights": [{"at": HAND, "path": P, "color": CYAN, "range": 12, "brightness": [[0, 0], [0.5, 6], [TR, 8], [TD, 6], [TD + 0.001, 0]]},
                   light(IMPACT, [[TD - 0.005, 0], [TD, 22], [TD + 0.4, 4], [TD + 1.0, 0]], rng=14)]
                  + [light(chest(q), [[t - 0.005, 0], [t, 12], [t + 0.3, 0]], rng=10) for (_, q, t, _) in links],
        "grade": [[0, 0, 0, 0, "#ffffff"], [TR - 0.05, -0.07, 0.14, -0.03, "#e2eaff"], [TD + 0.3, -0.05, 0.1, 0, "#e8efff"], [dur, 0, 0, 0, "#ffffff"]],
        "pose": {"armR": [[0, 0], [0.15, 85, "out"], [TR - 0.05, 95], [TR, 150, "out"], [TR + 0.12, 125], [TR + 0.8, 0]],
                 "armRz": [[0, 0], [0.15, -10], [TR, 10], [TR + 0.8, 0]],
                 "armL": [[0, 0], [0.15, 40, "out"], [TR, -20, "out"], [TR + 0.8, 0]],
                 "lean": [[0, 0], [0.3, -10, "out"], [TR - 0.03, -14], [TR + 0.05, 14, "out"], [TR + 0.4, 4], [TR + 0.9, 0]],
                 "scale": [[0, [1, 1, 1]], [TR - 0.03, [1.04, 0.95, 1.04]], [TR + 0.05, [0.96, 1.05, 0.96]], [TR + 0.2, [1, 1, 1]]]},
        # close on the charge, pulls up and wide for the lob, settles framing all three targets for the chain
        # over the shoulder on the charge, then high behind the caster so A (centre), B (left), C (right) spread out
        "camera": {"pos": [[0, [5.5, 6, 4.5]], [kd(TR), [6, 6.4, 4]], [kd(TR + 0.3), [5, 12, 4]], [kd(TD), [3.5, 11.5, -5]], [1, [3.5, 11.2, -6]]],
                   "look": [[0, [1.2, 4.3, -3]], [kd(TR), [1, 4.4, -4]], [kd(TR + 0.3), [0, 3, -16]], [kd(TD), [0, 2.5, -25]], [1, [0, 2.5, -26]]],
                   "fov": [[0, 50], [kd(TR), 50], [kd(TD) - 0.004, 56], [kd(TD) + 0.008, 51, "out"], [kd(TD + 0.4), 56], [1, 56]]},
        "poster": HOPS[0] + 0.03,
    }


write(build(), os.path.join(os.path.dirname(__file__), "thunder_07_PlasmaBomb.json"))
print("wrote thunder_07_PlasmaBomb.json")
