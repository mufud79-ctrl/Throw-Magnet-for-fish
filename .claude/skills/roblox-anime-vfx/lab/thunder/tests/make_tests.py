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


def crackle(at, t, size=4.0, life=0.16, seed=50):
    """Instant arc flash (thunder_arc played once): the angular replacement for camera-facing ring bursts."""
    return emit_stack("thunder_arc_v2", at, t, size=[[0, size * 0.8], [0.2, size], [1, size * 1.1]], life=life, seed=seed,
                      colors=COOL, transparency=[[0, 0], [0.5, 0.2], [1, 1]])


def ground_ring(at, t, size=12.0, life=0.45, seed=55):
    """thunder_burst laid flat on the ground: its shock ring becomes a shockwave in perspective, its bolts rake the sand."""
    return emit_stack("thunder_burst_v2", [at[0], 0.25, at[2]], t, size=[[0, size * 0.7], [0.15, size], [1, size * 1.08]], life=life,
                      seed=seed, orient="VelocityPerpendicular", colors=COOL, z=-0.2)


def dust(at, t, n=9, size=(5, 11), seed=61):
    """White anime dust thrown out low and sideways from a landing (RELL impact)."""
    return {"type": "emitter", "at": [at[0], 0.6, at[2]], "emits": [[t, n]], "seed": seed, "part": [5, 0.2, 5], "props": {
        "Texture": "dust_burst", "Color": "#d9d3c6", "LightEmission": 0, "Brightness": 1.0, "Shape": "Disc",
        "Size": [[0, size[0]], [1, size[1]]], "Lifetime": [0.6, 0.9], "Speed": [18, 26], "SpreadAngle": [8, 8],
        "EmissionDirection": "Top", "ShapeInOut": "Outward", "Drag": 4, "Acceleration": [0, 2, 0], "Rotation": [-15, 15],
        "Transparency": [[0, 0.05], [0.6, 0.3], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot",
        "Orientation": "FacingCameraWorldUp", "ZOffset": -0.6}}


def smoke_burst(at, t, n=6, seed=63):
    """Dark storm smoke kicked up by the strike (the dark anchor at the hit)."""
    return {"type": "emitter", "at": at, "emits": [[t, n]], "seed": seed, "props": {
        "Texture": "smoke_puff", "Color": [[0, "#3a4570"], [1, NAVY]], "LightEmission": 0, "Brightness": 1,
        "Size": [[0, 3], [1, 7.5]], "Lifetime": [0.8, 1.2], "Speed": [4, 9], "SpreadAngle": [70, 70], "Drag": 3,
        "Acceleration": [0, 3, 0], "Rotation": [0, 360], "RotSpeed": [-30, 30], "Transparency": [[0, 0.15], [0.7, 0.5], [1, 1]],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot", "ZOffset": -0.4}}


def light(at, keys, color=CYAN, rng=14):
    # Roblox PointLight brightness ~1-8; anything hotter floods the sand white
    return {"at": at, "color": color, "range": rng, "brightness": [[t, round(v * 0.18, 2)] + k[2:] for t, v, *k in [list(x) for x in keys]]}


# ------------------------------------------------------------------ trail showcase: bolt ribbon on a 3-kink path
def trail_showcase():
    P = [[0.24, [0, 3, 0]], [0.28, [-7, 3.4, -6]], [0.32, [6, 2.9, -12]], [0.36, [-5, 3.4, -18.5]], [0.40, [0, 3, -25]]]
    kinks = [p for _, p in P[1:-1]]
    L = []
    # anticipation: arcs crackle over the crouched body, ion haze pools at the feet (dark anchor)
    L += emit_stack("thunder_arc_v2", [0, 3, 0], 0, size=[[0, 5], [1, 6]], life=0.2, mode="Loop", rate=[[0.02, 0.24, 14]], layers=("glow", "rim", "mid", "core"))
    L.append(haze([0, 0.6, 0], 0.0, 0.3, 18, size=(3, 6), rise=1.5, part=[4, 0.5, 4]))
    L.append(sparks([0, 3, 0], 0.12, 10, speed=(4, 9), life=(0.15, 0.3), seed=3))
    # the ribbon: dark smear first, then the four layers, pinned to the world (Static) so the bolt stays on its line
    base = {"path": P, "t0": 0.24, "t1": 0.40, "lifetime": 0.7, "faceCamera": True, "textureMode": "Static", "textureLength": 16,
            "widthScale": [[0, 1.35], [0.12, 1.0], [0.6, 0.7], [1, 0.35]]}
    for (ta, pa), (tb, pb) in zip(P[:-1], P[1:]):
        L.append(dict(base, type="trail", path=[[ta, pa], [tb, pb]], t0=ta, t1=tb, lifetime=1.1, width=5, texture="thunder_strip_v2_2_glow",
                      color=NAVY, lightEmission=0, brightness=1, transparency=[[0, 0.2], [0.5, 0.45], [1, 1]], widthScale=[[0, 0.8], [1, 1.5]]))
    fl = flicker(0.12, ((0.17, 0.8), (0.22, 0.05), (0.33, 0.7), (0.38, 0.15)), tail=0.55)
    L += leg_trails(base, P, {"glow": 6.5, "rim": 3.8, "mid": 3.4, "core": 2.0},
                     transparency={"glow": [[0, 0.1], [0.5, 0.5], [1, 1]], "rim": [[0, 0], [0.6, 0.3], [1, 1]], "mid": fl, "core": fl})
    # kinks: each corner cracks with an instant arc flash and spits sparks (no camera-facing rings)
    for i, (t, p) in enumerate(P[1:-1]):
        L.append(sparks(p, t, 10, seed=20 + i))
        L += crackle(p, t, size=4.5, seed=60 + i)
    # dissolve: the body flashes out as a cyan afterimage, the ground cracks with a flat shock ring
    L += crackle([0, 3, 0], 0.24, size=5, life=0.18, seed=70)
    L += ground_ring([0, 0, 0], 0.24, size=10, seed=71)
    # re-form (the landing): flat shockwave, arc flash, white dust, chips of ground, dark smoke, sparks
    L += crackle([0, 3.2, -25], 0.40, size=8, life=0.22, seed=73)
    L += ground_ring([0, 0, -25], 0.40, size=16, life=0.5, seed=72)
    L.append(dust([0, 0, -25], 0.40, seed=64))
    L.append(smoke_burst([0, 1.2, -25], 0.41, seed=65))
    L.append(sparks([0, 2.5, -25], 0.40, 24, speed=(12, 28), seed=31))
    L.append(haze([0, 0.8, -25], 0.42, 0.9, 22, size=(4, 9), rise=3, part=[5, 0.5, 5], seed=12))
    # residual charge: arcs keep crawling over the re-formed body and static drips off it
    L += emit_stack("thunder_arc_v2", [0, 3, -25], 0.42, size=[[0, 4.5], [1, 5]], life=0.16, mode="Loop", rate=[[0.42, 1.15, 9]], seed=91,
                    colors=COOL, transparency=[[0, 0], [0.6, 0.3], [1, 1]])
    L.append({"type": "emitter", "at": [0, 3, -25], "part": [2, 4, 1], "rate": [[0.45, 1.3, 14]], "seed": 33, "props": {
        "Texture": "static_sparks", "Color": [[0, ICE], [1, BLUE]], "LightEmission": 1, "Brightness": 1.5, "Size": [[0, 0.9], [1, 0.3]],
        "Lifetime": [0.2, 0.35], "Speed": [1, 3], "SpreadAngle": [60, 60], "Acceleration": [0, -20, 0], "FlipbookLayout": "Grid4x4",
        "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.3}})
    L += scar([0, 0, 0], 0.24, size=9, rot=20)
    L += scar([0, 0, -25], 0.40, size=13, rot=-35)
    return {
        "name": "test_trail", "title": "Trail showcase: bolt ribbon", "element": "Thunder", "archetype": "test", "duration": 1.7,
        "caster": True, "layers": L, "hitstop": [{"t": 0.425, "dur": 0.06}],
        "ghosts": [{"t": 0.235, "at": [0, 0, 0], "color": CYAN, "life": 0.22, "lean": 18}],
        "debris": [{"kind": "fling", "at": [0, 0, -25], "t": 0.40, "count": 9, "size": 1.3, "speed": 26, "life": 1.4, "seed": 5}],  # freeze one frame after the strike so the bolt is on screen
        "shakes": [{"t": 0.24, "amp": 0.25, "dur": 0.2, "freq": 24}, {"t": 0.40, "amp": 0.55, "dur": 0.35, "freq": 22}],
        "lights": [light([0, 3, 0], [[0, 0], [0.2, 6], [0.24, 14], [0.4, 0]]), light([0, 3, -25], [[0.39, 0], [0.4, 24], [0.8, 4], [1.4, 0]], rng=12),
                   {"at": [0, 3, 0], "path": P, "color": CYAN, "range": 12, "brightness": [[0.23, 0], [0.24, 5], [0.4, 5], [0.41, 0]]}],
        "grade": [[0, 0, 0, 0, "#ffffff"], [0.2, -0.07, 0.14, -0.04, "#e4ecff"], [0.42, -0.04, 0.1, 0.02, "#eef3ff"], [1.2, 0, 0, 0, "#ffffff"]],  # storm dim so the bolt pops
        "pose": {"lean": [[0, 0], [0.18, 18, "out"], [0.40, 18], [0.43, -14, "out"], [0.6, 6], [0.85, 0]],
                 "armR": [[0, 0], [0.18, -50, "out"], [0.40, -50], [0.44, 30, "out"], [0.8, 0]],
                 "armL": [[0, 0], [0.18, -50, "out"], [0.40, -50], [0.44, 25, "out"], [0.8, 0]],
                 "offset": [[0, [0, 0, 0]], [0.18, [0, -0.35, 0], "out"], [0.399, [0, -0.35, 0]], [0.4, [0, 0, -25]]],
                 "scale": [[0, [1, 1, 1]], [0.18, [1.12, 0.84, 1.12], "out"], [0.23, [0.55, 1.45, 0.55]], [0.245, [0.001, 0.001, 0.001]],
                           [0.399, [0.001, 0.001, 0.001]], [0.4, [0.45, 1.55, 0.45]], [0.47, [1.25, 0.8, 1.25], "out"], [0.62, [0.95, 1.05, 0.95]], [0.8, [1, 1, 1]]]},
        "camera": {"pos": [[0, [21, 16, 1]], [0.2, [21, 16, 0]], [0.215, [20, 15.2, -2], "outExpo"], [1, [19.5, 14.8, -3]]],
                   "look": [[0, [0, 1.5, -12]], [0.2, [0, 1.5, -12.5]], [0.215, [0, 1.5, -13.5], "outExpo"], [1, [0, 1.5, -14]]],
                   "fov": [[0, 55], [0.2, 54], [0.212, 50, "out"], [0.45, 54]]}, "poster": 0.43,
    }


# ------------------------------------------------------------------ vbeam showcase: arc cannon from the hand
def vbeam_showcase():
    hand, hit = [1.5, 4.1, -2.2], [0, 3.6, -24]
    T = 0.32
    L = []
    # anticipation: arcs gather at the cocked hand, sparks pulled inward, haze darkens around the caster
    L += emit_stack("thunder_arc_v2", hand, 0, size=[[0, 2.5], [1, 4]], life=0.16, mode="Loop", rate=[[0.03, T, 16]])
    L.append({"type": "emitter", "at": hand, "part": [7, 7, 7], "rate": [[0.04, T - 0.03, 60]], "seed": 5, "props": {
        "Texture": "static_sparks", "Color": [[0, BLUE], [1, WHITE]], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere",
        "ShapeInOut": "Inward", "ShapeStyle": "Surface", "Size": [[0, 0.6], [1, 1.2]], "Lifetime": [0.12, 0.16], "Speed": [22, 28],
        "Orientation": "VelocityParallel", "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [25, 25],
        "FlipbookStartRandom": True, "ZOffset": 0.3}})
    L.append(haze([0, 1, 0], 0.0, 0.5, 14, size=(3, 6), rise=1.2, part=[5, 1, 5]))
    # the beam: thin hot core that strikes and dies fast; strands fan around the axis, flicker, then cool to indigo
    fl = flicker(0.1, ((0.14, 0.8), (0.18, 0.0), (0.27, 0.65), (0.31, 0.1)), tail=0.5)
    wid = {L_: [[0, [a * 1.15, b * 1.15]], [0.04, [a, b], "out"], [0.6, [a * 0.7, b * 0.6]], [1, [a * 0.3, b * 0.2]]]
           for L_, (a, b) in {"glow": (4.6, 3.8), "rim": (3.4, 2.8), "mid": (3.2, 2.6), "core": (1.7, 1.4)}.items()}
    L.append({"type": "vbeam", "from": hand, "to": hit, "t0": T, "life": 1.0, "reach": 1,
              "core": {"radius": [[0, 0.14], [0.06, 0.1], [0.25, 0.05], [0.34, 0]], "color": [[0, WHITE], [0.3, ICE]], "material": "Neon"},
              "planes": [{"count": 2, "width": [[0, [4, 3]], [1, [6, 5]]], "texture": "thunder_strip_v2_3_glow", "color": NAVY, "lightEmission": 0,
                          "brightness": 1, "transparency": [[0, 0.35], [0.5, 0.5], [1, 1]], "angle": 45, "textureLength": 14, "textureSpeed": -0.5}]
                        + plane_stack(wid, count=3, twist={"mid": 120, "core": -160, "glow": 40, "rim": 120}, speed={"mid": 2, "core": 3.5},
                                      tlen={"glow": 10, "rim": 9, "mid": 9, "core": 7}, bright={"glow": 0.6},
                                      transparency={"glow": [[0, 0.35], [0.5, 0.55], [1, 1]], "rim": [[0, 0], [0.6, 0.3], [1, 1]], "mid": fl, "core": fl})})
    # the strike itself: two angular neon bolts, two frames on, a frame off, one re-strike (instant lightning)
    for i, (t0, life, th) in enumerate([(T, 0.07, 0.2), (T + 0.1, 0.05, 0.13)]):
        L.append({"type": "bolt", "from": hand, "to": hit, "t0": t0, "life": life, "color": CYAN, "thickness": th, "jitter": 0.6,
                  "segments": 14, "flicker": 0.034, "branch": 0.12, "seed": 17 + i, "brightness": 2.2})
    # muzzle + impact (instant), arcs crawl over the target, scar under it, dark smoke rises off the burn
    L += crackle(hand, T, size=4, seed=81)
    L += crackle(hit, T, size=9, life=0.22, seed=82)
    L += ground_ring([0, 0, -24], T, size=13, seed=83)
    L.append(dust([0, 0, -24], T, n=8, size=(4.5, 10), seed=66))
    L.append(smoke_burst([0, 2.5, -24], T + 0.01, seed=67))
    L.append(sparks(hit, T, 26, speed=(14, 30), seed=41))
    L += emit_stack("thunder_arc_v2", [0, 3, -24.5], T, size=[[0, 4.5], [1, 5.5]], life=0.18, mode="Loop", rate=[[T + 0.02, T + 0.9, 12]], seed=90)
    L.append(haze([0, 1, -24], T + 0.05, T + 0.9, 24, size=(4, 10), rise=3.5, part=[4, 1, 4], seed=13))
    L += scar([0, 0, -24], T, size=11, rot=10)
    return {
        "name": "test_vbeam", "title": "Volumetric beam showcase: arc cannon", "element": "Thunder", "archetype": "test", "duration": 1.6,
        "layers": L, "hitstop": [{"t": T + 0.025, "dur": 0.07}], "hits": [{"t": T, "dummy": 0, "dir": [0, 0, -1], "power": 0.7}],
        "debris": [{"kind": "fling", "at": [0, 0, -24], "t": T, "count": 7, "size": 1.1, "speed": 24, "life": 1.3, "seed": 9}],
        "shakes": [{"t": T, "amp": 0.6, "dur": 0.35, "freq": 24}],
        "lights": [light(hand, [[0, 0], [T - 0.01, 6], [T, 18], [T + 0.2, 3], [T + 0.5, 0]], rng=9), light(hit, [[T - 0.01, 0], [T, 24], [T + 0.4, 4], [T + 1.0, 0]], rng=11)],
        "grade": [[0, 0, 0, 0, "#ffffff"], [T - 0.02, -0.07, 0.14, -0.04, "#e2eaff"], [T + 0.3, -0.03, 0.07, 0.02, "#eef3ff"], [1.4, 0, 0, 0, "#ffffff"]],
        "pose": {"lean": [[0, 0], [T - 0.04, -14, "out"], [T, 12, "out"], [T + 0.25, 4], [T + 0.7, 0]],
                 "twist": [[0, 0], [T - 0.04, 20, "out"], [T, -8, "out"], [T + 0.6, 0]],
                 "armR": [[0, 0], [T - 0.04, 125, "out"], [T, 88, "out"], [T + 0.5, 90], [T + 1.0, 0]],
                 "armL": [[0, 0], [T - 0.04, -30], [T + 0.2, 20], [T + 0.9, 0]]},
        "camera": {"pos": [[0, [17, 7.8, 5]], [0.16, [16.6, 7.6, 4.3]], [0.175, [16, 7.3, 3.2], "outExpo"], [1, [15.7, 7.2, 2.6]]],
                   "look": [[0, [-1, 3.3, -10.5]], [0.175, [-1, 3.4, -11.3], "outExpo"], [1, [-1, 3.4, -11.8]]],
                   "fov": [[0, 54], [0.165, 53], [0.178, 48, "out"], [0.4, 53]]}, "poster": 0.37, "dummies": [[0, 0, -24]],
    }


write(trail_showcase(), os.path.join(HERE, "test_trail.json"))
write(vbeam_showcase(), os.path.join(HERE, "test_vbeam.json"))
print("wrote test_trail.json, test_vbeam.json")
