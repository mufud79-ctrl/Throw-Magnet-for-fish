"""Judgment Pillar (C) - placed delayed strike. Signature: a storm cloud gathers over the spot and flashes from
inside, then a colossal multi-strand column slams down, leaving a crater and the biggest burn scar in the kit.

Beat sheet
  0.00-0.15  point at a spot 22 studs ahead; fingertip crackle                          (anticipation)
  0.15-0.85  TELEGRAPH: storm cloud gathers 38 studs up with flickering inner flashes; its shadow spreads on
             the ground; a ring of crawling ground arcs marks the zone; the world dims (readable warning)
  0.75-0.97  arm raised to the sky, hauled down; stepped leaders flicker down from the cloud, streamers
             crackle up from the ground; a beat of darkness right before               (anticipation)
  1.00       STRIKE: colossal column (thick volumetric core, braided twisting strands, a giant jagged bolt);
             ONE inverted impact frame; hit-stop 0.14; big shake; lens punch            (timing)
  1.00-1.50  crater slabs + flung shards, giant ground starburst, dust ring, navy smoke columns; the column
             re-strikes twice thinner, then cools to an indigo line                    (follow-through)
  1.00-3.00  biggest Lichtenberg scar cools to soot; the cloud rumbles once more and breaks up
Run: python3 lab/thunder/moves/judgment_pillar.py
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

T = 1.00
X, Z = 0.0, -22.0                      # strike point
GROUND = [X, 0, Z]
SKY = 38.0
CLOUD = [X, SKY, Z]
FINGER = [1.5, 3.7, -2.2]


def build():
    L = []
    rng = np.random.default_rng(31)
    # ---- point: fingertip crackle
    L += crackle(FINGER, 0.08, size=2.4, life=0.14, seed=301)

    # ---- telegraph: the storm cloud (billows grow -> hold -> break up over the particle life), inner flashes
    for i in range(7):
        a = i / 7 * math.tau + rng.uniform(-0.3, 0.3)
        r = 0 if i == 0 else rng.uniform(4, 8)
        p = [X + math.cos(a) * r, SKY + rng.uniform(-1.5, 2), Z + math.sin(a) * r]
        sz = rng.uniform(16, 22) if i else 24
        L.append({"type": "emitter", "at": p, "emits": [[0.15 + 0.04 * i, 1]], "seed": 310 + i, "props": {
            "Texture": "storm_cloud", "Color": [[0, "#56628e"], [0.5, "#3c4770"], [1, "#56628e"]], "LightEmission": 0, "Brightness": 1,
            "Size": [[0, sz * 0.55], [0.3, sz], [1, sz * 1.15]], "Lifetime": [2.5, 2.5], "Speed": [0.01, 0.01], "Rotation": [rng.uniform(-20, 20)] * 2,
            "RotSpeed": [3, 3], "Transparency": [[0, 0.6], [0.2, 0.05], [0.8, 0.1], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot",
            "ZOffset": -1}})
    L.append({"type": "emitter", "at": CLOUD, "part": [20, 3, 20], "emits": [[0.2, 6], [0.4, 5]], "seed": 318, "props": {
        "Texture": "smoke_puff", "Color": "#4a557e", "LightEmission": 0, "Brightness": 1, "Shape": "Cylinder", "Size": [[0, 6], [0.4, 11], [1, 12]],
        "Lifetime": [2.2, 2.6], "Speed": [0.3, 0.8], "Rotation": [0, 360], "RotSpeed": [-6, 6], "Transparency": [[0, 1], [0.2, 0.2], [0.8, 0.3], [1, 1]],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot", "FlipbookFramerate": [1, 1], "ZOffset": -1.2}})
    # inner flashes: storm_flash played fast (its lit frames 2,3,6,9,10 flicker inside 0.12 s), lights the cloud from within
    for i, tf in enumerate([0.42, 0.6, 0.74, 0.84, 0.9, 0.95, T, T + 0.35, T + 0.6]):
        a = rng.uniform(0, math.tau)
        p = [X + math.cos(a) * rng.uniform(0, 7), SKY - 1, Z + math.sin(a) * rng.uniform(0, 7)]
        L.append({"type": "emitter", "at": p, "emits": [[tf, 1]], "seed": 320 + i, "props": {
            "Texture": "storm_flash", "Color": "#9fdcff", "LightEmission": 1, "Brightness": 0.9, "Size": 34,
            "Lifetime": [0.13, 0.13], "Speed": [0.01, 0.01], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot", "ZOffset": -3}})
    # cloud shadow spreading on the ground under the spot (dark anchor) + the warning ring of crawling ground arcs
    L.append({"type": "emitter", "at": [X, 0.08, Z], "emits": [[0.2, 3]], "seed": 330, "part": [6, 0.1, 6], "props": {
        "Texture": "ion_haze", "Color": NAVY, "LightEmission": 0, "Brightness": 1, "Shape": "Disc", "Orientation": "VelocityPerpendicular",
        "Size": [[0, 8], [0.35, 26], [1, 28]], "Lifetime": [1.6, 1.6], "Speed": [0.01, 0.01], "Rotation": [0, 360],
        "Transparency": [[0, 1], [0.3, 0.45], [0.6, 0.5], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot", "ZOffset": -1}})
    L.append({"type": "emitter", "at": [X, 0.3, Z], "part": [16, 0.1, 16], "rate": [[0.3, T, 44]], "seed": 331, "props": {
        "Texture": "thunder_arc_v2_mid", "Color": [[0, WHITE], [0.3, CYAN], [1, BLUE]], "LightEmission": 0.3, "Brightness": 1.3,
        "Shape": "Disc", "ShapeStyle": "Surface", "Orientation": "VelocityPerpendicular", "Size": [[0, 3.6], [1, 4.6]], "Lifetime": [0.1, 0.16],
        "Speed": [0.01, 0.01], "Rotation": [0, 360], "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [20, 20],
        "FlipbookStartRandom": True, "ZOffset": 0.2}})
    L.append({"type": "emitter", "at": [X, 0.3, Z], "part": [16, 0.1, 16], "rate": [[0.3, T, 18]], "seed": 332, "props": {
        "Texture": "thunder_arc_v2_rim", "Color": INDIGO, "LightEmission": 0, "Brightness": 1, "Shape": "Disc", "ShapeStyle": "Surface",
        "Orientation": "VelocityPerpendicular", "Size": [[0, 3.9], [1, 4.8]], "Lifetime": [0.12, 0.18], "Speed": [0.01, 0.01], "Rotation": [0, 360],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.1}})
    L.append(haze([X, 1, Z], 0.4, T, 20, size=(4, 8), rise=0.8, part=[16, 1, 16], seed=333))

    # ---- pre-strike: stepped leaders flicker down from the cloud; streamers crackle up from the ground
    for i in range(4):
        a = i / 4 * math.tau + 0.4
        top = [X + math.cos(a) * 3, SKY - 3, Z + math.sin(a) * 3]
        bot = [X + math.cos(a) * 1.2 + rng.uniform(-1, 1), 6, Z + math.sin(a) * 1.2]
        for lay, w in (("rim", 1.6), ("mid", 1.3), ("core", 0.6)):
            L.append({"type": "beam", "from": top, "to": bot, "t0": 0.8 + 0.03 * i, "life": T - 0.8 - 0.03 * i,
                      "reach": [[0, 0.15], [0.3, 0.35], [0.31, 0.25], [0.6, 0.55], [0.61, 0.45], [1, 0.75]],
                      "textures": [f"{st}_{lay}" for st in STRIPS[i % 4:] + STRIPS[:i % 4]], "swap": 0.04, "textureLength": 5,
                      "color": HOT[lay], "lightEmission": LE[lay], "brightness": BR[lay], "width": w, "segments": 10,
                      "transparency": [[0, 0.2], [0.45, 0.6], [0.5, 0.1], [1, 0]]})
    L.append({"type": "emitter", "at": [X, 0.5, Z], "part": [5, 0.2, 5], "rate": [[0.85, T, 40]], "seed": 334, "props": {
        "Texture": "static_sparks", "Color": [[0, WHITE], [1, CYAN]], "LightEmission": 1, "Brightness": 1.6, "Shape": "Disc",
        "Size": [[0, 1.6], [1, 0.6]], "Lifetime": [0.08, 0.14], "Speed": [14, 22], "Orientation": "VelocityParallel",
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [25, 25], "FlipbookStartRandom": True, "ZOffset": 0.3}})

    # ---- STRIKE: the column. volumetric core + plane fan, braided strands, giant jagged bolt sprite
    fl = flicker(0.06, ((0.1, 0.7), (0.13, 0.0), (0.22, 0.65), (0.26, 0.0)), tail=0.5)
    wid = {k: [[0, [a * 1.4, b * 1.4]], [0.05, [a, b], "out"], [0.35, [a * 0.7, b * 0.6]], [1, [a * 0.15, b * 0.1]]]
           for k, (a, b) in {"glow": (13, 15), "rim": (8, 9.5), "mid": (7, 8.5), "core": (3.6, 4.4)}.items()}
    L.append({"type": "vbeam", "from": [X, SKY - 2, Z], "to": [X, 0, Z], "t0": T, "life": 0.85, "reach": 1,
              "core": {"radius": [[0, 0.9], [0.05, 0.6, "out"], [0.25, 0.3], [0.4, 0]], "color": [[0, WHITE], [0.3, ICE]], "material": "Neon"},
              "planes": [{"count": 3, "width": [[0, [16, 18]], [1, [20, 22]]], "texture": "thunder_strip_v2_2_glow", "color": NAVY,
                          "lightEmission": 0, "brightness": 1, "transparency": [[0, 0.5], [0.4, 0.6], [1, 1]], "angle": 30, "textureLength": 30}]
                        + plane_stack(wid, count=4, twist={"mid": 120, "core": -150, "glow": 40, "rim": 120}, speed={"mid": 2.5, "core": 4},
                                      tlen={"glow": 20, "rim": 18, "mid": 18, "core": 14}, bright={"glow": 0.55},
                                      transparency={"glow": [[0, 0.3], [0.4, 0.55], [1, 1]], "rim": [[0, 0], [0.5, 0.3], [1, 1]], "mid": fl, "core": fl})})
    # braided strands spiralling around the column (each bows out a different way)
    for i in range(5):
        a = i / 5 * math.tau
        c = [math.cos(a) * 4.5, 0, math.sin(a) * 4.5]
        for lay, w in (("rim", 2.8), ("mid", 2.3), ("core", 1.2)):
            L.append({"type": "beam", "from": [X, SKY - 3, Z], "to": [X + math.cos(a + 1) * 1.5, 0.2, Z + math.sin(a + 1) * 1.5], "t0": T, "life": 0.45,
                      "curve": [[0, c], [0.5, [-c[0] * 0.6, 0, -c[2] * 0.6]], [1, [c[0] * 0.3, 0, c[2] * 0.3]]],
                      "textures": [f"{st}_{lay}" for st in STRIPS[i % 4:] + STRIPS[:i % 4]], "swap": 0.04, "textureLength": 9, "segments": 24,
                      "color": COOL[lay], "lightEmission": LE[lay], "brightness": BR[lay], "width": [[0, w * 1.3], [0.2, w], [1, w * 0.3]],
                      "transparency": [[0, 0], [0.12 + 0.03 * i, 0], [0.16 + 0.03 * i, 0.8], [0.22 + 0.03 * i, 0], [0.6, 0.4], [1, 1]]})
    L += emit_stack("thunder_bolt_v2", [X, SKY / 2, Z], T, size=[[0, SKY * 1.05], [1, SKY * 1.05]], life=0.42, seed=341, colors=COOL)
    # re-strikes: two thinner strikes down the same channel
    for j, (tr, w) in enumerate([(T + 0.14, 0.55), (T + 0.27, 0.35)]):
        L.append({"type": "bolt", "from": [X + 0.3, SKY - 2, Z], "to": [X, 0.2, Z], "t0": tr, "life": 0.05, "color": CYAN, "thickness": w,
                  "jitter": 1.2, "segments": 18, "flicker": 0.034, "branch": 0.15, "seed": 351 + j, "brightness": 2.2})

    # ---- impact on the ground (instant): starburst, crack flash, dust ring, smoke columns, sparks
    L += ground_ring(GROUND, T, size=30, life=0.6, seed=361)
    L += crackle([X, 2.5, Z], T, size=12, life=0.24, seed=362)
    L.append(dust(GROUND, T, n=14, size=(7, 15), seed=363))
    for i in range(3):
        a = i / 3 * math.tau + 0.5
        L.append(smoke_burst([X + math.cos(a) * 3, 2, Z + math.sin(a) * 3], T + 0.04 + 0.03 * i, n=4, seed=364 + i))
    L.append(sparks([X, 2, Z], T, 40, speed=(18, 40), life=(0.3, 0.6), seed=368, grav=-45))
    L.append(haze([X, 1, Z], T + 0.1, T + 1.4, 24, size=(6, 14), rise=4, part=[8, 1, 8], seed=369))
    L += scar(GROUND, T, size=20, rot=25, glow_life=1.3, soot_life=3.4)

    dur = 3.0
    k = lambda t: round(t / dur, 4)
    return {
        "name": "thunder_03_JudgmentPillar", "title": "Judgment Pillar", "element": "Thunder", "archetype": "placed_delayed_strike", "duration": dur,
        "layers": L, "dummies": [[X, 0, Z + 1.5]],
        "hitstop": [{"t": T + 0.016, "dur": 0.15}],
        "impact": [{"t": T + 0.016, "dur": 0.034, "mode": "invert"}],
        "hits": [{"t": T, "dummy": 0, "dir": [0, 0, 1], "power": 1.1}],
        "numbers": [{"t": T + 0.03, "at": [X + 1, 7, Z + 1.5], "text": "260", "color": CYAN, "vel": [4, 18, 0], "size": 3.2}],
        "debris": [{"kind": "crater", "at": GROUND, "t": T, "radius": 8, "count": 16, "size": 3.2, "life": 2.6, "seed": 37, "pitColor": "#1c1a22"},
                   {"kind": "fling", "at": GROUND, "t": T, "count": 14, "size": 1.6, "speed": 36, "life": 1.8, "seed": 38}],
        "shakes": [{"t": 0.85, "amp": 0.12, "dur": 0.15, "freq": 30}, {"t": T, "amp": 1.2, "dur": 0.7, "freq": 20}],
        "lights": [light(CLOUD, [[0.4, 0], [0.42, 8], [0.5, 0], [0.6, 7], [0.66, 0], [0.84, 8], [0.9, 2], [0.95, 9], [T, 0]], rng=40),
                   light([X, 8, Z], [[T - 0.01, 0], [T, 40], [T + 0.3, 12], [T + 0.9, 3], [T + 1.6, 0]], rng=30)],
        "grade": [[0, 0, 0, 0, "#ffffff"], [0.3, -0.04, 0.05, -0.04, "#e6ecfb"], [0.85, -0.14, 0.16, -0.12, "#cdd7f2"],
                  [0.97, -0.22, 0.22, -0.18, "#bfcaee"], [T + 0.05, -0.05, 0.12, 0, "#e8efff"], [T + 1.2, -0.04, 0.06, 0, "#eef3ff"], [dur, 0, 0, 0, "#ffffff"]],
        "pose": {"armR": [[0, 0], [0.12, 80, "out"], [0.62, 80], [0.8, 170, "out"], [0.93, 175], [T - 0.01, 75, "in"], [T + 0.08, 65], [T + 0.6, 70], [T + 1.2, 0]],
                 "armL": [[0, 0], [0.12, -25, "out"], [0.8, -40], [T, 20, "out"], [T + 1.0, 0]],
                 "lean": [[0, 0], [0.12, 6, "out"], [0.8, -10, "out"], [T - 0.01, 14, "in"], [T + 0.15, -8, "out"], [T + 0.8, 0]],
                 "twist": [[0, 0], [0.12, -10, "out"], [T, -16], [T + 1.0, 0]]},
        # low and wide: caster in the foreground, the spot, the column and the cloud all in frame
        # back and up: caster foreground right, the marked spot, the whole column and the cloud in frame
        "camera": {"pos": [[0, [34, 13, 16]], [k(0.95), [32, 13.5, 13]], [k(T) + 0.004, [30.5, 13, 11], "outExpo"], [1, [29.5, 12.6, 9.5]]],
                   "look": [[0, [0, 17, -16]], [k(0.95), [0, 18.5, -18]], [k(T) + 0.004, [0, 18, -19], "outExpo"], [1, [0, 16.5, -19]]],
                   "fov": [[0, 64], [k(0.97), 62], [k(T) + 0.004, 56, "out"], [k(T + 0.5), 62], [1, 63]]},
        "poster": T + 0.05, "bloom": 0.5,
    }


write(build(), os.path.join(os.path.dirname(__file__), "thunder_03_JudgmentPillar.json"))
print("wrote thunder_03_JudgmentPillar.json")
