"""Flash Step (V) - teleport dash. Signature: the body becomes a bolt on a 3-kink zig-zag, leaving a flickering
ribbon and a dotted chain of burn scars along its route; it re-forms in a static burst.

Beat sheet
  0.00-0.08  crouch; arcs crackle over the body; static pulled into the chest      (anticipation, squash)
  0.08       DISSOLVE: body stretches thin and blinks out leaving a cyan afterimage; ground starburst (stretch)
  0.08-0.20  the bolt runs a 3-kink zig-zag (4 straight legs, sharp corners) leaving a flickering cel ribbon;
             each corner: a 1-frame silhouette flash, crackle, sparks, a small burn on the ground
                                                                                    (angular arcs, instant)
  0.20       RE-FORM: pops in stretched tall, squashes; zap hit-stop 0.04; starburst, white dust, chips
  0.20-0.90  ribbon flickers and cools white -> cyan -> indigo over a navy smear; arcs crawl on the body,
             static drips off                                                      (follow-through)
  0.20-2.00  ground memory: burn scars at start, corners and end cool to soot      (calling card)
Run: python3 lab/thunder/moves/flash_step.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

T0, T1 = 0.08, 0.20
P = [[0.08, [0, 3, 0]], [0.11, [-7, 3.3, -6]], [0.14, [6, 2.9, -12.5]], [0.17, [-5, 3.3, -19]], [0.20, [0, 3, -26]]]
END = P[-1][1]


def build():
    L = []
    # ---- crouch: arcs over the body, static pulled in, haze at the feet
    L += emit_stack("thunder_arc_v2", [0, 3, 0], 0, size=[[0, 4.5], [1, 5.5]], life=0.12, mode="Loop", rate=[[0.0, T0, 30]], seed=401)
    L.append({"type": "emitter", "at": [0, 3, 0], "part": [6, 7, 6], "rate": [[0.0, T0, 90]], "seed": 402, "props": {
        "Texture": "static_sparks", "Color": [[0, BLUE], [1, WHITE]], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere",
        "ShapeInOut": "Inward", "ShapeStyle": "Surface", "Size": [[0, 0.5], [1, 1.0]], "Lifetime": [0.08, 0.1], "Speed": [30, 36],
        "Orientation": "VelocityParallel", "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [25, 25],
        "FlipbookStartRandom": True, "ZOffset": 0.3}})
    L.append(haze([0, 0.6, 0], 0.0, 0.2, 24, size=(3, 6), rise=1.2, part=[4, 0.5, 4], seed=403))

    # ---- the ribbon: navy smear per leg + 4-layer cel ribbon per leg (sharp corners), pinned to the world
    base = {"faceCamera": True, "textureMode": "Static", "textureLength": 15, "lifetime": 0.65,
            "widthScale": [[0, 1.4], [0.1, 1.0], [0.6, 0.7], [1, 0.3]]}
    for (ta, pa), (tb, pb) in zip(P[:-1], P[1:]):
        L.append(dict(base, type="trail", path=[[ta, pa], [tb, pb]], t0=ta, t1=tb, lifetime=1.1, width=5.5, texture="thunder_strip_v2_2_glow",
                      color=NAVY, lightEmission=0, brightness=1, transparency=[[0, 0.2], [0.5, 0.45], [1, 1]], widthScale=[[0, 0.8], [1, 1.5]]))
    fl = flicker(0.1, ((0.15, 0.8), (0.2, 0.05), (0.31, 0.7), (0.36, 0.12)), tail=0.55)
    L += leg_trails(base, P, {"glow": 7.5, "rim": 4.4, "mid": 3.9, "core": 2.3},
                    transparency={"glow": [[0, 0.15], [0.5, 0.5], [1, 1]], "rim": [[0, 0], [0.6, 0.3], [1, 1]], "mid": fl, "core": fl})

    # ---- corners: crackle, sparks, a small burn on the ground beneath each
    ghosts = [{"t": T0 - 0.005, "at": [0, 0, 0], "color": CYAN, "life": 0.22, "lean": 18}]
    for i, (t, p) in enumerate(P[1:-1]):
        L += crackle(p, t, size=4.8, life=0.15, seed=410 + i)
        L.append(sparks(p, t, 6, seed=420 + i))
        L.append(spark_burst(p, t, size=6, life=0.22, seed=425 + i, rot=50 * i))
        L.append(flare(p, t, size=9, life=0.16, seed=428 + i))
        L += scar([p[0], 0, p[2]], t, size=8, rot=40 * i, glow_life=0.9, soot_life=2.6)
        ghosts.append({"t": t, "at": [p[0], 0, p[2]], "color": "#9fe8ff", "life": 0.07, "lean": 28})

    # ---- dissolve + re-form
    L += crackle([0, 3, 0], T0, size=5, life=0.16, seed=430)
    L += ground_ring([0, 0, 0], T0, size=10, seed=431)
    L += scar([0, 0, 0], T0, size=8, rot=20, glow_life=0.9, soot_life=2.6)
    L += emit_stack("thunder_burst_v2", [0, 3.2, -26], T1, size=[[0, 7], [0.2, 10], [1, 10.5]], life=0.36, seed=432,
                    squash=[[0, -0.35], [0.15, 0.25], [0.4, 0]])
    L += ground_ring(END, T1, size=15, life=0.5, seed=433)
    L += scar([0, 0, -26], T1, size=12, rot=-35, glow_life=1.0, soot_life=2.8)
    L.append(dust([0, 0, -26], T1, n=8, size=(4, 9), seed=434))
    L.append(sparks([0, 2.5, -26], T1, 14, speed=(12, 28), seed=435))
    L.append(flare([0, 3, -26], T1, size=16, life=0.26, seed=440))
    L += impact_v3([0, 3, -26], T1, size=9, life=0.4, seed=441)
    L.append(streaks([0, 2.5, -26], T1 + 0.01, 22, speed=(60, 110), length=(3, 6), seed=442))
    L += crack([0, 0, -26], T1 + 0.01, size=13, life=1.4, rot=-35, seed=443)
    L.append(smoke_burst([0, 1.2, -26], T1 + 0.01, n=4, seed=436))
    # residual charge on the re-formed body
    L += emit_stack("thunder_arc_v2", [0, 3, -26], T1 + 0.02, size=[[0, 4.5], [1, 5]], life=0.15, mode="Loop", rate=[[T1 + 0.02, T1 + 0.75, 10]],
                    seed=437, colors=COOL, transparency=[[0, 0], [0.6, 0.3], [1, 1]])
    L.append({"type": "emitter", "at": [0, 3, -26], "part": [2, 4, 1], "rate": [[T1 + 0.05, T1 + 0.9, 14]], "seed": 438, "props": {
        "Texture": "static_sparks", "Color": [[0, ICE], [1, BLUE]], "LightEmission": 1, "Brightness": 1.5, "Size": [[0, 0.9], [1, 0.3]],
        "Lifetime": [0.2, 0.35], "Speed": [1, 3], "SpreadAngle": [60, 60], "Acceleration": [0, -20, 0], "FlipbookLayout": "Grid4x4",
        "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.3}})
    L.append(haze([0, 0.8, -26], T1 + 0.02, T1 + 0.6, 20, size=(4, 8), rise=2.5, part=[5, 0.5, 5], seed=439))

    dur = 1.5
    k = lambda t: round(t / dur, 4)
    return {
        "name": "thunder_04_FlashStep", "title": "Flash Step", "element": "Thunder", "archetype": "zigzag_teleport", "duration": dur,
        "caster": True, "layers": L, "ghosts": ghosts,
        "hitstop": [{"t": T1 + 0.012, "dur": 0.04}],
        "debris": [{"kind": "fling", "at": [0, 0, -26], "t": T1, "count": 7, "size": 1.1, "speed": 22, "life": 1.2, "seed": 41}],
        "shakes": [{"t": T0, "amp": 0.25, "dur": 0.15, "freq": 26}, {"t": T1, "amp": 0.5, "dur": 0.3, "freq": 22}],
        "lights": [light([0, 3, 0], [[0, 2], [T0 - 0.01, 6], [T0, 14], [T0 + 0.15, 0]], rng=10),
                   {"at": [0, 3, 0], "path": P, "color": CYAN, "range": 12, "brightness": [[T0 - 0.001, 0], [T0, 5], [T1, 5], [T1 + 0.001, 0]]},
                   light(END, [[T1 - 0.005, 0], [T1, 20], [T1 + 0.4, 3], [T1 + 1.0, 0]], rng=12)],
        "grade": [[0, 0, 0, 0, "#ffffff"], [T0, -0.07, 0.14, -0.04, "#e4ecff"], [T1 + 0.2, -0.04, 0.08, 0.02, "#eef3ff"], [1.1, 0, 0, 0, "#ffffff"]],
        "pose": {"lean": [[0, 0], [0.06, 20, "out"], [T1, 20], [T1 + 0.03, -14, "out"], [T1 + 0.2, 6], [T1 + 0.5, 0]],
                 "armR": [[0, 0], [0.06, -55, "out"], [T1, -55], [T1 + 0.04, 30, "out"], [T1 + 0.5, 0]],
                 "armL": [[0, 0], [0.06, -55, "out"], [T1, -55], [T1 + 0.04, 25, "out"], [T1 + 0.5, 0]],
                 "offset": [[0, [0, 0, 0]], [0.06, [0, -0.4, 0], "out"], [T1 - 0.001, [0, -0.4, 0]], [T1, END[:1] + [0] + END[2:]]],
                 "scale": [[0, [1, 1, 1]], [0.06, [1.14, 0.82, 1.14], "out"], [T0 - 0.005, [0.5, 1.5, 0.5]], [T0 + 0.004, [0.001, 0.001, 0.001]],
                           [T1 - 0.001, [0.001, 0.001, 0.001]], [T1, [0.42, 1.6, 0.42]], [T1 + 0.06, [1.26, 0.78, 1.26], "out"], [T1 + 0.2, [0.95, 1.05, 0.95]], [T1 + 0.4, [1, 1, 1]]]},
        "camera": {"pos": [[0, [23, 17, 1]], [k(T1), [23, 17, 0]], [k(T1) + 0.008, [22, 16.2, -2], "outExpo"], [1, [21.5, 15.8, -3]]],
                   "look": [[0, [0, 1.5, -12.5]], [k(T1), [0, 1.5, -13]], [k(T1) + 0.008, [0, 1.5, -14], "outExpo"], [1, [0, 1.5, -14.5]]],
                   "fov": [[0, 54], [k(T1), 53], [k(T1) + 0.008, 50, "out"], [0.45, 53]]},
        "poster": T1 + 0.03,
    }


write(build(), os.path.join(os.path.dirname(__file__), "thunder_04_FlashStep.json"))
print("wrote thunder_04_FlashStep.json")
