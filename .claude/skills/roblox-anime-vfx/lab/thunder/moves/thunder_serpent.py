"""Thunder Serpent (B) - heavy weaving projectile. Signature: a rigged lightning serpent pours out of the palm,
swims an S-curve wrapped in chained lightning, bites, coils around the target and bursts.

Beat sheet
  0.00-0.24  arm draws back across the body; lightning gathers in the palm            (anticipation)
  0.25       the sweep releases: hand burst; the serpent POURS OUT of the palm, roaring, jaw open
  0.25-0.85  swims a 1.25-wave S-curve wrapped in 3 braided cel lightning chains; arcs crawl along it; a navy
             smear trails                                                             (arcs)
  0.72-0.86  jaw opens wide on the approach and SNAPS shut on the target; hit-stop 0.04   (timing)
  0.86-1.24  coils 1.2 turns around the target, rising and tightening                 (follow-through)
  1.25       BURST: roar, the serpent explodes into scattering bolts; starburst, crackle, debris, smoke;
             hit-stop 0.1; big shake                                                  (timing, squash)
  1.30-2.30  chains cool to indigo; static clings to the target; the scar cools       (calling card, dark anchor)
Run: python3 lab/thunder/moves/thunder_serpent.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

TB = 0.25                 # birth
TBITE = 0.86
TBURST = 1.25
HAND = [1.6, 4.0, -2.0]
SPAWN = [1.2, -1.0, -6.0]  # the serpent erupts out of the ground here (its unborn body stays below the ground)
C = [0.0, -26.0]          # target centre (x, z)
TARGET = [C[0], 0, C[1]]


def head_path():
    """S-curve swim from the palm to the front of the target, then a rising, tightening coil around it."""
    P = []
    n = 30
    end = [0.0, 3.4, C[1] + 3.6]
    for i in range(n + 1):
        u = i / n
        t = TB + (TBITE - TB) * u
        rise = min(1.0, u / 0.18)                               # bursts up out of the ground in the first stretch
        x = SPAWN[0] * (1 - u) + 5.5 * math.sin(2 * math.pi * 1.25 * u) * (1 - u ** 3) * rise
        y = SPAWN[1] + (4.2 - SPAWN[1]) * (1 - (1 - rise) ** 2) + (end[1] - 4.2) * u + 0.7 * math.sin(2 * math.pi * 2 * u) * (1 - u) * rise
        z = SPAWN[2] + (end[2] - SPAWN[2]) * u
        P.append([round(t, 4), [round(x, 3), round(y, 3), round(z, 3)]])
    m = 24
    for i in range(1, m + 1):
        u = i / m
        t = TBITE + (TBURST - TBITE) * u
        a = 2 * math.pi * 1.2 * u
        r = 3.6 - 1.0 * u
        P.append([round(t, 4), [round(math.sin(a) * r, 3), round(3.4 + 3.0 * u, 3), round(C[1] + math.cos(a) * r, 3)]])
    P.append([round(TBURST + 0.2, 4), P[-1][1]])
    return P


def build():
    P = head_path()
    L = []
    # ---- anticipation: lightning gathers in the drawn-back palm
    palm0 = [1.6, 1.8, 0.9]   # hand drawn low and back
    L += emit_stack("thunder_arc_v2", palm0, 0, size=[[0, 2.2], [1, 3.2]], life=0.12, mode="Loop", rate=[[0.02, TB, 18]], seed=501)
    L.append({"type": "emitter", "at": palm0, "part": [6, 6, 6], "rate": [[0.03, TB - 0.02, 55]], "seed": 502, "props": {
        "Texture": "static_sparks", "Color": [[0, BLUE], [1, WHITE]], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere",
        "ShapeInOut": "Inward", "ShapeStyle": "Surface", "Size": [[0, 0.5], [1, 1.0]], "Lifetime": [0.1, 0.14], "Speed": [24, 30],
        "Orientation": "VelocityParallel", "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [25, 25],
        "FlipbookStartRandom": True, "ZOffset": 0.3}})
    L += crackle(HAND, TB, size=3.5, life=0.16, seed=503)
    # the summon: ground cracks glow under the spawn point, then the serpent erupts out of the sand
    G = [SPAWN[0], 0, SPAWN[2] + 1]
    L.append({"type": "emitter", "at": [G[0], 0.3, G[2]], "part": [6, 0.1, 6], "rate": [[0.1, TB + 0.4, 34]], "seed": 508, "props": {
        "Texture": "thunder_arc_v2_mid", "Color": [[0, WHITE], [0.3, CYAN], [1, BLUE]], "LightEmission": 0.3, "Brightness": 1.3,
        "Shape": "Disc", "Orientation": "VelocityPerpendicular", "Size": [[0, 3], [1, 4]], "Lifetime": [0.1, 0.16], "Speed": [0.01, 0.01],
        "Rotation": [0, 360], "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.2}})
    L += ground_ring(G, TB, size=14, life=0.45, seed=505)
    L += crackle([G[0], 2, G[2]], TB, size=6, life=0.2, seed=506)
    L.append(dust(G, TB, n=8, size=(4, 9), seed=507))
    L.append(sparks([G[0], 1, G[2]], TB, 20, speed=(10, 24), seed=504))
    L += scar(G, TB, size=9, rot=-10, glow_life=0.9, soot_life=2.6)

    # ---- the serpent (rigged): roar on birth, jaw wide on approach, snap on the bite, roar before it bursts
    life = TBURST + 0.06 - TB
    kk = lambda t: round((t - TB) / life, 4)
    L.append({"type": "rig", "model": "thunder_serpent", "path": P, "t0": TB, "life": life, "jawBone": "jaw", "brightness": 1.2,
              "color": [[0, "#ffffff"], [kk(TBURST - 0.1), "#d8f6ff"], [kk(TBURST), "#ffffff"]],
              "jaw": [[0, -30], [kk(TB + 0.12), -30], [kk(TB + 0.2), -4], [kk(0.72), -6], [kk(0.8), -50, "out"], [kk(TBITE - 0.005), -50],
                      [kk(TBITE + 0.02), 0, "in"], [kk(TBURST - 0.14), 0], [kk(TBURST - 0.04), -55, "out"], [1, -55]],
              "transparency": [[0, 0], [kk(TBURST), 0], [1, 1]]})
    # chained lightning: three braided cel chains riding the head path (wave around it), the length of the body
    for i, ph in enumerate((0, 120, 240)):
        base = {"path": P, "wave": {"amp": [[TB, 0.4], [TB + 0.2, 1.1], [TBITE, 0.9], [TBURST, 0.7]], "freq": 3.2, "axis": [0, 1, 0], "phase": ph, "t0": TB},
                "t0": TB, "t1": TBURST, "lifetime": 0.42, "faceCamera": True, "textureMode": "Static", "textureLength": 10,
                "widthScale": [[0, 1.2], [0.15, 1.0], [0.7, 0.7], [1, 0.2]]}
        L += trail_stack(base, {"glow": 3.6, "rim": 2.1, "mid": 1.8, "core": 1.0}, layers=("rim", "mid", "core"),
                         transparency={"rim": [[0, 0], [0.7, 0.3], [1, 1]], "mid": flicker(0.2, ((0.3, 0.6), (0.36, 0.05)), tail=0.6),
                                       "core": flicker(0.2, ((0.3, 0.6), (0.36, 0.05)), tail=0.6)})
    L.append(dict(type="trail", path=P, t0=TB, t1=TBURST, lifetime=0.9, faceCamera=True, width=5.5, texture="thunder_strip_v2_2_glow",
                  textureMode="Stretch", color=NAVY, lightEmission=0, brightness=1, transparency=[[0, 0.35], [0.5, 0.55], [1, 1]],
                  widthScale=[[0, 0.6], [1, 1.4]]))
    # arcs left crawling along the body as it passes
    L.append({"type": "emitter", "at": HAND, "path": P, "rate": [[TB + 0.03, TBURST, 34]], "seed": 511, "props": {
        "Texture": "thunder_arc_v2_mid", "Color": [[0, WHITE], [0.4, CYAN], [1, BLUE]], "LightEmission": 0.35, "Brightness": 1.3,
        "Size": [[0, 2.6], [1, 3.4]], "Lifetime": [0.12, 0.2], "Speed": [0.5, 2], "SpreadAngle": [180, 180], "Rotation": [0, 360],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.3}})

    # ---- the bite (small), the burst (big)
    chest = [C[0], 3.6, C[1]]
    L += crackle([0, 3.6, C[1] + 1.2], TBITE, size=4.5, life=0.14, seed=521)
    L.append(sparks([0, 3.6, C[1] + 1.2], TBITE, 12, seed=522))
    L += emit_stack("thunder_burst_v2", [0, 4.5, C[1]], TBURST, size=[[0, 9], [0.2, 15], [1, 16]], life=0.45, seed=531,
                    squash=[[0, -0.4], [0.15, 0.3], [0.4, 0]])
    L += crackle([0, 4.5, C[1]], TBURST, size=11, life=0.24, seed=532)
    L += ground_ring(TARGET, TBURST, size=22, life=0.55, seed=533)
    L.append(sparks([0, 4.5, C[1]], TBURST, 36, speed=(16, 36), life=(0.3, 0.6), seed=534, grav=-40))
    L.append(dust(TARGET, TBURST, n=10, size=(5, 11), seed=535))
    L.append(smoke_burst([0, 4, C[1]], TBURST + 0.02, n=6, seed=536))
    # the serpent's body scatters into bolts flung outward from the coil
    for j in range(6):
        a = j / 6 * math.tau + 0.3
        tip = [round(math.sin(a) * 9, 2), round(4.5 + 3 * math.sin(a * 2), 2), round(C[1] + math.cos(a) * 9, 2)]
        L.append({"type": "bolt", "from": [0, 4.5, C[1]], "to": tip, "t0": TBURST + 0.005, "life": 0.07, "color": CYAN, "thickness": 0.16,
                  "jitter": 0.9, "segments": 9, "flicker": 0.034, "branch": 0.2, "seed": 541 + j, "brightness": 2.2})
    L += emit_stack("thunder_arc_v2", chest, TBURST, size=[[0, 4.4], [1, 5]], life=0.15, mode="Loop", rate=[[TBURST + 0.03, TBURST + 0.9, 11]],
                    seed=551, colors=COOL, transparency=[[0, 0], [0.6, 0.3], [1, 1]])
    L.append(haze([0, 1, C[1]], TBURST + 0.05, TBURST + 0.9, 22, size=(5, 11), rise=3, part=[6, 1, 6], seed=552))
    L += scar(TARGET, TBURST, size=14, rot=30, glow_life=1.1, soot_life=3.0)

    dur = 2.3
    k = lambda t: round(t / dur, 4)
    return {
        "name": "thunder_05_ThunderSerpent", "title": "Thunder Serpent", "element": "Thunder", "archetype": "rigged_serpent_projectile", "duration": dur,
        "layers": L, "dummies": [[C[0], 0, C[1]]],
        "hitstop": [{"t": TBITE + 0.012, "dur": 0.04}, {"t": TBURST + 0.015, "dur": 0.1}],
        "hits": [{"t": TBITE, "dummy": 0, "dir": [0, 0, -1], "power": 0.2}, {"t": TBURST, "dummy": 0, "dir": [0, 0, -1], "power": 0.9}],
        "numbers": [{"t": TBITE + 0.02, "at": [2.5, 6.2, C[1]], "text": "45", "color": CYAN, "vel": [5, 11, 0], "size": 2.0, "life": 0.42},
                    {"t": TBURST + 0.02, "at": [-2, 7.5, C[1]], "text": "190", "color": CYAN, "vel": [-3, 16, 0], "size": 3.0}],
        "debris": [{"kind": "fling", "at": TARGET, "t": TBURST, "count": 10, "size": 1.3, "speed": 28, "life": 1.5, "seed": 57},
                   {"kind": "fling", "at": [SPAWN[0], 0, SPAWN[2] + 1], "t": TB, "count": 8, "size": 1.0, "speed": 24, "life": 1.2, "seed": 58}],
        "shakes": [{"t": TB, "amp": 0.2, "dur": 0.15, "freq": 24}, {"t": TBITE, "amp": 0.3, "dur": 0.15, "freq": 26}, {"t": TBURST, "amp": 0.9, "dur": 0.5, "freq": 22}],
        "lights": [light(palm0, [[0, 0], [TB - 0.01, 7], [TB, 14], [TB + 0.2, 0]], rng=9),
                   {"at": HAND, "path": P, "color": CYAN, "range": 12, "brightness": [[TB - 0.001, 0], [TB, 5], [TBURST, 5], [TBURST + 0.001, 0]]},
                   light([0, 4.5, C[1]], [[TBURST - 0.005, 0], [TBURST, 26], [TBURST + 0.4, 4], [TBURST + 1.0, 0]], rng=14)],
        "grade": [[0, 0, 0, 0, "#ffffff"], [TB, -0.05, 0.1, -0.02, "#e6edff"], [TBURST, -0.08, 0.14, -0.03, "#e0e9ff"], [TBURST + 0.5, -0.03, 0.06, 0.02, "#eef3ff"], [dur, 0, 0, 0, "#ffffff"]],
        "pose": {"twist": [[0, 0], [0.2, 30, "out"], [TB, 32], [TB + 0.08, -25, "out"], [TB + 0.5, -8], [TB + 1.0, 0]],
                 "armR": [[0, 0], [0.2, -35, "out"], [TB, -40], [TB + 0.06, 120, "out"], [TB + 0.5, 105], [TB + 1.1, 0]],
                 "armL": [[0, 0], [0.2, 20, "out"], [TB + 0.06, -20, "out"], [TB + 0.8, 0]],
                 "lean": [[0, 0], [0.2, 14, "out"], [TB, 14], [TB + 0.06, -12, "out"], [TB + 0.6, 0]]},
        # follows the serpent: wide on the release, tracks the swim, settles on the coil + burst
        "camera": {"pos": [[0, [17, 9, 6]], [k(TB), [17.5, 9.5, 4]], [k(TBITE), [19, 11, -9]], [k(TBURST), [17, 10, -14], "out"], [k(TBURST) + 0.01, [16, 9.6, -15], "outExpo"], [1, [15.5, 9.4, -16]]],
                   "look": [[0, [0, 4, -6]], [k(TB), [0, 4, -8]], [k(TBITE), [0, 4, -20]], [k(TBURST), [0, 4.5, -25], "out"], [1, [0, 4, -26]]],
                   "fov": [[0, 55], [k(TBURST) - 0.004, 54], [k(TBURST) + 0.008, 48, "out"], [k(TBURST + 0.4), 54], [1, 54]]},
        "poster": TBITE,
    }


write(build(), os.path.join(os.path.dirname(__file__), "thunder_05_ThunderSerpent.json"))
print("wrote thunder_05_ThunderSerpent.json")
