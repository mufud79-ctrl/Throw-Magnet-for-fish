"""Showcase specs for the two new layer types (trail, vbeam). Run: python3 lab/thunder/tests/make_tests.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

HERE = os.path.dirname(__file__)


def sparks(at, t, n, speed=(8, 18), life=(0.25, 0.45), size=(0.8, 1.4), seed=7, color=CYAN, grav=-35):
    return {"type": "emitter", "at": at, "emits": [[t, n]], "seed": seed, "props": {
        "Texture": "static_sparks", "Color": [[0, WHITE], [0.3, color], [1, BLUE]], "LightEmission": 1, "Brightness": 1.6,
        "Size": [[0, size[1]], [1, size[0] * 0.4]], "Lifetime": list(life), "Speed": list(speed), "SpreadAngle": [180, 180],
        "Acceleration": [0, grav, 0], "Drag": 3, "Rotation": [0, 360], "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random",
        "FlipbookFramerate": [20, 30], "FlipbookStartRandom": True, "ZOffset": 0.4}}


def haze(at, t0, t1, rate, size=(4, 8), rise=2.5, seed=11, part=None, color=NAVY, tr=0.45):
    e = {"type": "emitter", "at": at, "rate": [[t0, t1, rate]], "seed": seed, "props": {
        "Texture": "ion_haze", "Color": color, "LightEmission": 0, "Brightness": 1,
        "Size": [[0, size[0]], [1, size[1]]], "Lifetime": [0.9, 1.4], "Speed": [0.5, rise], "SpreadAngle": [40, 40],
        "Rotation": [0, 360], "RotSpeed": [-20, 20], "Transparency": [[0, 1], [0.2, tr], [1, 1]],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot", "ZOffset": -0.3}}
    if part:
        e["part"] = part
        e["props"]["Shape"] = "Cylinder"
    return e


def light(at, keys, color=CYAN, rng=14):
    # Roblox PointLight brightness ~1-8; anything hotter floods the sand white
    return {"at": at, "color": color, "range": rng, "brightness": [[t, round(v * 0.18, 2)] + k[2:] for t, v, *k in [list(x) for x in keys]]}


# ------------------------------------------------------------------ trail showcase: bolt ribbon on a 3-kink path
def trail_showcase():
    P = [[0.24, [0, 3, 0]], [0.28, [-7, 3.4, -6]], [0.32, [6, 2.9, -12]], [0.36, [-5, 3.4, -18.5]], [0.40, [0, 3, -25]]]
    kinks = [p for _, p in P[1:-1]]
    L = []
    # anticipation: arcs crackle over the crouched body, ion haze pools at the feet (dark anchor)
    L += emit_stack("thunder_arc", [0, 3, 0], 0, size=[[0, 5], [1, 6]], life=0.2, mode="Loop", rate=[[0.02, 0.24, 14]], layers=("glow", "rim", "mid", "core"))
    L.append(haze([0, 0.6, 0], 0.0, 0.3, 18, size=(3, 6), rise=1.5, part=[4, 0.5, 4]))
    L.append(sparks([0, 3, 0], 0.12, 10, speed=(4, 9), life=(0.15, 0.3), seed=3))
    # the ribbon: dark smear first, then the four layers, pinned to the world (Static) so the bolt stays on its line
    base = {"path": P, "t0": 0.24, "t1": 0.40, "lifetime": 0.7, "faceCamera": True, "textureMode": "Static", "textureLength": 16,
            "widthScale": [[0, 1.35], [0.12, 1.0], [0.6, 0.7], [1, 0.35]]}
    for (ta, pa), (tb, pb) in zip(P[:-1], P[1:]):
        L.append(dict(base, type="trail", path=[[ta, pa], [tb, pb]], t0=ta, t1=tb, lifetime=1.1, width=5, texture="thunder_strip_2_glow",
                      color=NAVY, lightEmission=0, brightness=1, transparency=[[0, 0.2], [0.5, 0.45], [1, 1]], widthScale=[[0, 0.8], [1, 1.5]]))
    fl = flicker(0.12, ((0.17, 0.8), (0.22, 0.05), (0.33, 0.7), (0.38, 0.15)), tail=0.55)
    L += leg_trails(base, P, {"glow": 6.5, "rim": 3.8, "mid": 3.4, "core": 2.0},
                     transparency={"glow": [[0, 0.1], [0.5, 0.5], [1, 1]], "rim": [[0, 0], [0.6, 0.3], [1, 1]], "mid": fl, "core": fl})
    # kinks: each corner spits sparks and flashes (angular, instant)
    for i, (t, p) in enumerate(P[1:-1]):
        L.append(sparks(p, t, 9, seed=20 + i))
        L += emit_stack("thunder_burst", p, t, size=3.5, life=0.22, seed=60 + i)
    # dissolve and re-form bursts + burn scars at both ends
    L += emit_stack("thunder_burst", [0, 3, 0], 0.24, size=7, life=0.35, seed=71)
    L += emit_stack("thunder_burst", [0, 3, -25], 0.40, size=11, life=0.45, seed=72, squash=[[0, -0.4], [0.15, 0.25], [0.4, 0]])
    L.append(sparks([0, 2.5, -25], 0.40, 22, speed=(12, 26), seed=31))
    L.append(haze([0, 0.8, -25], 0.42, 0.9, 22, size=(4, 9), rise=3, part=[5, 0.5, 5], seed=12))
    L += scar([0, 0, 0], 0.24, size=8, rot=20)
    L += scar([0, 0, -25], 0.40, size=12, rot=-35)
    return {
        "name": "test_trail", "title": "Trail showcase: bolt ribbon", "element": "Thunder", "archetype": "test", "duration": 2.0,
        "caster": True, "layers": L, "hitstop": [{"t": 0.425, "dur": 0.06}],  # freeze one frame after the strike so the bolt is on screen
        "shakes": [{"t": 0.24, "amp": 0.25, "dur": 0.2, "freq": 24}, {"t": 0.40, "amp": 0.55, "dur": 0.35, "freq": 22}],
        "lights": [light([0, 3, 0], [[0, 0], [0.2, 6], [0.24, 30], [0.4, 0]]), light([0, 3, -25], [[0.39, 0], [0.4, 40], [0.9, 4], [1.6, 0]]),
                   {"at": [0, 3, 0], "path": P, "color": CYAN, "range": 12, "brightness": [[0.23, 0], [0.24, 5], [0.4, 5], [0.41, 0]]}],
        "grade": [[0, 0, 0, 0, "#ffffff"], [0.22, -0.04, 0.08, -0.1, "#e6efff"], [0.45, 0, 0.05, 0, "#f2f7ff"], [1.2, 0, 0, 0, "#ffffff"]],
        "pose": {"lean": [[0, 0], [0.18, 18, "out"], [0.40, 18], [0.43, -14, "out"], [0.6, 6], [0.85, 0]],
                 "armR": [[0, 0], [0.18, -50, "out"], [0.40, -50], [0.44, 30, "out"], [0.8, 0]],
                 "armL": [[0, 0], [0.18, -50, "out"], [0.40, -50], [0.44, 25, "out"], [0.8, 0]],
                 "offset": [[0, [0, 0, 0]], [0.18, [0, -0.35, 0], "out"], [0.399, [0, -0.35, 0]], [0.4, [0, 0, -25]]],
                 "scale": [[0, [1, 1, 1]], [0.18, [1.12, 0.84, 1.12], "out"], [0.23, [0.55, 1.45, 0.55]], [0.245, [0.001, 0.001, 0.001]],
                           [0.399, [0.001, 0.001, 0.001]], [0.4, [0.45, 1.55, 0.45]], [0.47, [1.25, 0.8, 1.25], "out"], [0.62, [0.95, 1.05, 0.95]], [0.8, [1, 1, 1]]]},
        "camera": {"pos": [18, 14, 2], "look": [0, 2, -12.5], "fov": 52}, "poster": 0.42,
    }


# ------------------------------------------------------------------ vbeam showcase: arc cannon from the hand
def vbeam_showcase():
    hand, hit = [1.5, 4.1, -2.2], [0, 3.6, -24]
    T = 0.32
    L = []
    # anticipation: arcs gather at the cocked hand, sparks pulled inward, haze darkens around the caster
    L += emit_stack("thunder_arc", hand, 0, size=[[0, 2.5], [1, 4]], life=0.16, mode="Loop", rate=[[0.03, T, 16]])
    L.append({"type": "emitter", "at": hand, "part": [7, 7, 7], "rate": [[0.04, T - 0.03, 60]], "seed": 5, "props": {
        "Texture": "static_sparks", "Color": [[0, BLUE], [1, WHITE]], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere",
        "ShapeInOut": "Inward", "ShapeStyle": "Surface", "Size": [[0, 0.6], [1, 1.2]], "Lifetime": [0.12, 0.16], "Speed": [22, 28],
        "Orientation": "VelocityParallel", "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [25, 25],
        "FlipbookStartRandom": True, "ZOffset": 0.3}})
    L.append(haze([0, 1, 0], 0.0, 0.5, 14, size=(3, 6), rise=1.2, part=[5, 1, 5]))
    # the beam: thin hot core that strikes and dies fast; strands fan around the axis, flicker, then cool to indigo
    fl = flicker(0.1, ((0.14, 0.8), (0.18, 0.0), (0.27, 0.65), (0.31, 0.1)), tail=0.5)
    wid = {L_: [[0, [a * 1.35, b * 1.35]], [0.04, [a, b], "out"], [0.6, [a * 0.7, b * 0.6]], [1, [a * 0.3, b * 0.2]]]
           for L_, (a, b) in {"glow": (7.5, 6.0), "rim": (3.6, 3.0), "mid": (3.4, 2.8), "core": (1.8, 1.5)}.items()}
    L.append({"type": "vbeam", "from": hand, "to": hit, "t0": T, "life": 1.0, "reach": 1,
              "core": {"radius": [[0, 0.32], [0.06, 0.2], [0.25, 0.1], [0.34, 0]], "color": [[0, WHITE], [0.3, ICE]], "material": "Neon"},
              "planes": [{"count": 2, "width": [[0, [4, 3]], [1, [6, 5]]], "texture": "thunder_strip_3_glow", "color": NAVY, "lightEmission": 0,
                          "brightness": 1, "transparency": [[0, 0.35], [0.5, 0.5], [1, 1]], "angle": 45, "textureLength": 14, "textureSpeed": -0.5}]
                        + plane_stack(wid, count=3, twist={"mid": 120, "core": -160, "glow": 40, "rim": 120}, speed={"mid": 2, "core": 3.5},
                                      tlen={"glow": 10, "rim": 9, "mid": 9, "core": 7},
                                      transparency={"glow": [[0, 0], [0.5, 0.35], [1, 1]], "rim": [[0, 0], [0.6, 0.3], [1, 1]], "mid": fl, "core": fl})})
    # muzzle + impact (instant), arcs crawl over the target, scar under it, dark smoke rises off the burn
    L += emit_stack("thunder_burst", hand, T, size=5, life=0.3, seed=81)
    L += emit_stack("thunder_burst", hit, T, size=12, life=0.5, seed=82, squash=[[0, -0.45], [0.12, 0.3], [0.4, 0]])
    L.append(sparks(hit, T, 26, speed=(14, 30), seed=41))
    L += emit_stack("thunder_arc", [0, 3, -24.5], T, size=[[0, 4.5], [1, 5.5]], life=0.18, mode="Loop", rate=[[T + 0.02, T + 0.9, 12]], seed=90)
    L.append(haze([0, 1, -24], T + 0.05, T + 0.9, 24, size=(4, 10), rise=3.5, part=[4, 1, 4], seed=13))
    L += scar([0, 0, -24], T, size=11, rot=10)
    return {
        "name": "test_vbeam", "title": "Volumetric beam showcase: arc cannon", "element": "Thunder", "archetype": "test", "duration": 1.9,
        "layers": L, "hitstop": [{"t": T + 0.025, "dur": 0.07}], "hits": [{"t": T, "dummy": 0, "dir": [0, 0, -1], "power": 0.7}],
        "shakes": [{"t": T, "amp": 0.6, "dur": 0.35, "freq": 24}],
        "lights": [light(hand, [[0, 0], [T - 0.01, 6], [T, 18], [T + 0.2, 3], [T + 0.5, 0]], rng=9), light(hit, [[T - 0.01, 0], [T, 45], [T + 0.5, 6], [T + 1.2, 0]])],
        "grade": [[0, 0, 0, 0, "#ffffff"], [T - 0.02, -0.05, 0.1, -0.12, "#e3ecff"], [T + 0.3, 0, 0.04, 0, "#f2f7ff"], [1.4, 0, 0, 0, "#ffffff"]],
        "pose": {"lean": [[0, 0], [T - 0.04, -14, "out"], [T, 12, "out"], [T + 0.25, 4], [T + 0.7, 0]],
                 "twist": [[0, 0], [T - 0.04, 20, "out"], [T, -8, "out"], [T + 0.6, 0]],
                 "armR": [[0, 0], [T - 0.04, 125, "out"], [T, 88, "out"], [T + 0.5, 90], [T + 1.0, 0]],
                 "armL": [[0, 0], [T - 0.04, -30], [T + 0.2, 20], [T + 0.9, 0]]},
        "camera": {"pos": [16, 7.5, 3], "look": [-0.5, 3.4, -12], "fov": 52}, "poster": 0.36, "dummies": [[0, 0, -24]],
    }


write(trail_showcase(), os.path.join(HERE, "test_trail.json"))
write(vbeam_showcase(), os.path.join(HERE, "test_vbeam.json"))
print("wrote test_trail.json, test_vbeam.json")
