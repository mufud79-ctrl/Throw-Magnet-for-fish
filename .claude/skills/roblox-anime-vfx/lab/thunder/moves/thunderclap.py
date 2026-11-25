"""Thunderclap (X) - close-range stun. Signature: a dome-shaped cage of lightning arcs bursts out of the caster;
arcs keep crawling over everyone it caught.

Beat sheet
  0.00-0.19  both hands rise overhead, apart; an arc crackles between the palms, brighter and tighter as they
             close                                                                   (anticipation)
  0.20       CLAP: palms slam together; white star flash overhead; hit-stop 0.05 (zap); lens punch;
             ground starburst + dust ring; caster squashes                          (timing, squash)
  0.20-0.34  the cage (25-edge geodesic dome of curved crackling arcs) bursts out, overshoots its 10-stud
             radius and settles                                                     (squash/stretch, arcs)
  0.25       the cage wall passes the 3 enemies: crackle hit + stun jolt (no knockback)
  0.30-1.20  arcs crawl over the stunned enemies, static drips off them; edges blink individually; the cage
             shrinks back as it cools white -> cyan -> indigo                       (follow-through)
  0.20-2.00  ring burn scar under the caster; navy haze pools inside the dome       (calling card, dark anchor)
Run: python3 lab/thunder/moves/thunderclap.py
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

T = 0.20
CLAP = [0, 5.45, 0]
HR0, HL0 = [2.65, 5.5, 0.1], [-2.65, 5.5, 0.1]      # hands spread at the top of the wind-up
TARGETS = [[-7.5, 0, -3.0], [5.0, 0, -6.5], [2.0, 0, 7.8]]
R = 10.0


def dome():
    """Geodesic half-icosahedron: top, an upper ring at 50 deg, a low ring at 8 deg (offset 36 deg). 25 edges."""
    def sph(el, az):
        el, az = math.radians(el), math.radians(az)
        return np.array([math.cos(el) * math.cos(az), math.sin(el), math.cos(el) * math.sin(az)])
    top = np.array([0.0, 1.0, 0.0])
    up = [sph(50, 18 + 72 * i) for i in range(5)]
    lo = [sph(8, 54 + 72 * i) for i in range(5)]
    E = [(top, u) for u in up] + [(up[i], up[(i + 1) % 5]) for i in range(5)]
    E += [(up[i], lo[i]) for i in range(5)] + [(up[(i + 1) % 5], lo[i]) for i in range(5)]
    E += [(lo[i], lo[(i + 1) % 5]) for i in range(5)]
    return E


# cage radius over the cage's life (k): bursts out, overshoots, settles, holds, shrinks back while cooling
RK = [(0.0, 0.6, None), (0.1, 11.2, "outExpo"), (0.18, 9.6, None), (0.26, 10.0, None), (0.7, 10.0, None), (1.0, 7.0, "in")]


def build():
    L = []
    rng = np.random.default_rng(9)
    # ---- wind-up: arc between the palms (shrinks to nothing as the hands meet), sparks, hands crackle
    for lay, w in (("rim", 3.0), ("mid", 2.6), ("core", 1.4)):
        L.append({"type": "beam", "from": [[0, HL0], [0.6, HL0], [1, [-0.3, 5.45, 0.1], "in"]], "to": [[0, HR0], [0.6, HR0], [1, [0.3, 5.45, 0.1], "in"]],
                  "t0": 0.05, "life": T - 0.05, "textures": [f"{st}_{lay}" for st in STRIPS], "swap": 0.04, "textureLength": 3,
                  "color": HOT[lay], "lightEmission": LE[lay], "brightness": BR[lay], "segments": 12,
                  "width": [[0, 0.4 * w], [0.7, w], [1, 1.3 * w]], "curve": [[0, [0, 0.9, 0]], [0.5, [0, -0.6, 0]], [1, [0, 0.2, 0]]],
                  "transparency": [[0, 0.35], [0.4, 0], [0.55, 0.5], [0.62, 0], [1, 0]]})
    for hx in (HR0, HL0):
        L += emit_stack("thunder_arc_v2", hx, 0, size=[[0, 1.6], [1, 2.2]], life=0.1, mode="Loop", rate=[[0.03, T, 14]], seed=201 + int(hx[0] > 0))
    L.append({"type": "emitter", "at": CLAP, "part": [7, 4, 4], "rate": [[0.03, T - 0.02, 45]], "seed": 203, "props": {
        "Texture": "static_sparks", "Color": [[0, BLUE], [1, WHITE]], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere",
        "ShapeInOut": "Inward", "ShapeStyle": "Surface", "Size": [[0, 0.5], [1, 1.0]], "Lifetime": [0.1, 0.14], "Speed": [22, 28],
        "Orientation": "VelocityParallel", "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [25, 25],
        "FlipbookStartRandom": True, "ZOffset": 0.3}})

    # ---- the clap (instant)
    L += emit_stack("thunder_burst_v2", CLAP, T, size=[[0, 6], [0.2, 8], [1, 8.5]], life=0.32, seed=211, squash=[[0, 0.35], [0.12, -0.2], [0.4, 0]])
    L += crackle(CLAP, T, size=5, life=0.18, seed=212)
    L += ground_ring([0, 0, 0], T, size=20, life=0.5, seed=213)
    L.append(dust([0, 0, 0], T, n=6, size=(3.5, 7), seed=214))
    L.append(sparks(CLAP, T, 26, speed=(14, 30), seed=215))

    # ---- signature: the cage. 25 curved crackling arcs, 3 stacked beams each, keyed by the cage radius
    life = 1.0
    for e, (a, b) in enumerate(dome()):
        m = (a + b) / 2
        bulge = m / np.linalg.norm(m) - m                     # chord midpoint -> sphere surface (unit radius)
        keys = lambda v: [[k, [round(float(x * r), 3) for x in v]] + ([ez] if ez else []) for k, r, ez in RK]
        # each edge blinks on its own pattern (crackling cage), always solid on the burst
        ph = rng.uniform(0, 0.08)
        tr = [[0, 0], [0.16, 0], [0.2 + ph, 0.7], [0.24 + ph, 0.05], [0.4 + ph, 0.55], [0.44 + ph, 0.1], [0.62, 0.2], [0.85, 0.85], [1, 1]]
        strips = STRIPS[e % 4:] + STRIPS[:e % 4]
        for lay, w in (("rim", 2.4), ("mid", 2.0), ("core", 1.0)):
            L.append({"type": "beam", "from": keys(a), "to": keys(b), "curve": keys(bulge), "t0": T, "life": life,
                      "textures": [f"{st}_{lay}" for st in strips], "swap": 0.05, "textureLength": 6, "segments": 16,
                      "color": COOL[lay], "lightEmission": LE[lay], "brightness": BR[lay],
                      "width": [[0, 1.6 * w], [0.12, w, "out"], [0.7, 0.8 * w], [1, 0.3 * w]], "transparency": tr})
    # the moment the wall sweeps outward: a fast ring of arcs low on the ground
    L += emit_stack("thunder_burst_v2", [0, 0.3, 0], T + 0.01, size=[[0, 6], [0.3, 22], [1, 24]], life=0.3, seed=216,
                    orient="VelocityPerpendicular", colors=COOL, z=-0.1)

    # ---- the stunned: hit crackle, arcs crawling over the body, static dripping off, a little jolt
    hits, numbers = [], []
    for i, p in enumerate(TARGETS):
        th = T + 0.05
        chest = [p[0], 3.6, p[2]]
        L += crackle(chest, th, size=4.5, life=0.18, seed=221 + i)
        L.append(sparks(chest, th, 12, speed=(8, 18), seed=231 + i))
        L += emit_stack("thunder_arc_v2", chest, th, size=[[0, 3.6], [1, 4.4]], life=0.14, mode="Loop", rate=[[th + 0.02, th + 0.95, 12]],
                        seed=241 + i, colors=COOL, transparency=[[0, 0], [0.6, 0.25], [1, 1]])
        L.append({"type": "emitter", "at": [p[0], 3, p[2]], "part": [2, 4, 1], "rate": [[th, th + 1.0, 12]], "seed": 251 + i, "props": {
            "Texture": "static_sparks", "Color": [[0, ICE], [1, BLUE]], "LightEmission": 1, "Brightness": 1.5, "Size": [[0, 0.9], [1, 0.3]],
            "Lifetime": [0.2, 0.35], "Speed": [1, 3], "SpreadAngle": [60, 60], "Acceleration": [0, -20, 0], "FlipbookLayout": "Grid4x4",
            "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.3}})
        d = np.array([p[0], 0, p[2]]) / np.linalg.norm([p[0], p[2]])
        hits.append({"t": th, "dummy": i, "dir": [round(float(d[0]), 3), 0, round(float(d[2]), 3)], "power": 0.12})
        numbers.append({"t": th + 0.02, "at": [p[0], 6.2, p[2]], "text": "42", "color": CYAN, "vel": [float(d[0]) * 3, 14, float(d[2]) * 3], "size": 2.0})

    # ---- ground memory + dark anchor
    L += scar([0, 0, 0], T, size=15, rot=15, glow_life=1.1, soot_life=3.0)
    L.append(haze([0, 0.8, 0], T + 0.03, T + 1.0, 30, size=(4, 9), rise=1.2, part=[14, 0.6, 14], seed=261))

    dur = 1.8
    k = lambda t: round(t / dur, 4)
    return {
        "name": "thunder_02_Thunderclap", "title": "Thunderclap", "element": "Thunder", "archetype": "close_stun_cage", "duration": dur,
        "layers": L, "dummies": TARGETS, "hits": hits, "numbers": numbers,
        "hitstop": [{"t": T + 0.015, "dur": 0.05}],
        "shakes": [{"t": T, "amp": 0.55, "dur": 0.3, "freq": 26}],
        "lights": [light(CLAP, [[0, 0], [T - 0.01, 6], [T, 22], [T + 0.25, 5], [T + 0.6, 0]], rng=12),
                   light([0, 4, 0], [[T, 0], [T + 0.08, 9], [T + 0.7, 5], [T + 1.0, 0]], rng=16)],
        "grade": [[0, 0, 0, 0, "#ffffff"], [T - 0.01, -0.07, 0.13, -0.03, "#e2eaff"], [T + 0.5, -0.03, 0.06, 0.02, "#eef3ff"], [1.4, 0, 0, 0, "#ffffff"]],
        "pose": {"armR": [[0, 0], [0.15, 180, "out"], [T, 180], [T + 0.5, 175], [T + 0.9, 0]],
                 "armL": [[0, 0], [0.15, 180, "out"], [T, 180], [T + 0.5, 175], [T + 0.9, 0]],
                 "armRz": [[0, 0], [0.15, 35, "out"], [T - 0.03, 38], [T, -42, "in"], [T + 0.06, -36], [T + 0.5, -40], [T + 0.9, 0]],
                 "armLz": [[0, 0], [0.15, -35, "out"], [T - 0.03, -38], [T, 42, "in"], [T + 0.06, 36], [T + 0.5, 40], [T + 0.9, 0]],
                 "lean": [[0, 0], [0.15, -10, "out"], [T, 6, "in"], [T + 0.2, 0]],
                 "scale": [[0, [1, 1, 1]], [0.15, [0.96, 1.06, 0.96], "out"], [T, [1.08, 0.9, 1.08]], [T + 0.08, [0.97, 1.04, 0.97]], [T + 0.25, [1, 1, 1]]]},
        "camera": {"pos": [[0, [12, 8, 13]], [k(T) - 0.003, [12.5, 8.4, 13.5]], [k(T) + 0.012, [17, 12, 17.5], "outExpo"], [1, [17.6, 12.4, 18]]],
                   "look": [[0, [0, 4, 0]], [k(T) + 0.012, [0, 3, 0], "outExpo"], [1, [0, 2.6, 0]]],
                   "fov": [[0, 54], [k(T) - 0.003, 53], [k(T) + 0.01, 48, "out"], [0.4, 53]]},
        "poster": T + 0.08,
    }


write(build(), os.path.join(os.path.dirname(__file__), "thunder_02_Thunderclap.json"))
print("wrote thunder_02_Thunderclap.json")
