"""Volt Lance (Z) - instant hitscan javelin. Signature: the lightning spear lingers impaled through the target.

Beat sheet
  0.00-0.16  javelin wind-up: arm cocked back overhead, lean back; a small spear crackles into the raised hand
             tail-to-tip and pinches thin just before release                      (anticipation, squash)
  0.16       whip-throw: arm snaps forward past release, overshoots                  (arcs, follow-through)
  0.17       STRIKE FRAME: neon bolt + full lance hand -> through the target in one frame (instant lightning)
  0.185      hit-stop 0.06; lens punch; target squashes; chest crackle; ground starburst
  0.20-0.55  the spear lingers on the line: cel shaft + solid neon head out the far side of the target,
             flickering, cooling white -> cyan -> blue; arcs hop along the shaft
  0.45-0.75  shaft dissolves from the caster end toward the head; head shatters into sparks
  0.17-1.6   burn scar under the target cools to soot; navy smoke curls off the target (dark anchor)
Run: python3 lab/thunder/moves/volt_lance.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

T = 0.17                                   # strike frame
HAND_UP = [1.5, 5.8, 0.6]                  # raised hand during the wind-up
HAND = [1.5, 4.1, -2.2]                    # hand at release (arm forward)
CHEST = [0, 3.8, -26]
TIP = [-0.2, 3.75, -31]                    # lance head comes out the far side of the target
HEAD0 = [-0.05, 3.78, -27.4]               # where the head starts (just past the chest)
KB = 1.4                                   # target knockback (studs along -Z); the impaled spear rides it


def lerp(a, b, k):
    return [a[i] + (b[i] - a[i]) * k for i in range(3)]


def build():
    L = []
    # ---- wind-up: a short spear forms in the raised hand (tail -> tip), crackling, then pinches before release
    held = {"type": "vbeam", "from": [1.5, 5.7, 2.2], "to": [1.5, 6.0, -1.6], "t0": 0.03, "life": T - 0.03,
            "reach": [[0, 0], [0.75, 1, "out"]],
            "core": {"radius": [[0, 0.04], [0.7, 0.07], [0.9, 0.09], [1, 0.02]], "color": WHITE, "material": "Neon"},
            "planes": plane_stack({"glow": [[0, [1.2, 1.6]], [0.8, [1.8, 2.4]], [0.92, [2.2, 2.8]], [1, [0.4, 0.4]]],
                                   "rim": [[0, [0.8, 1.0]], [0.8, [1.1, 1.4]], [0.92, [1.3, 1.6]], [1, [0.2, 0.2]]],
                                   "mid": [[0, [0.7, 0.9]], [0.8, [1.0, 1.3]], [0.92, [1.2, 1.5]], [1, [0.2, 0.2]]],
                                   "core": [[0, [0.4, 0.5]], [0.8, [0.6, 0.7]], [0.92, [0.7, 0.8]], [1, [0.1, 0.1]]]},
                                  count=2, colors=HOT, twist={"mid": 240, "core": -300}, speed={"mid": 3, "core": 5},
                                  tlen={"glow": 4, "rim": 4, "mid": 4, "core": 3}, bright={"glow": 0.6})}
    L.append(held)
    L += emit_stack("thunder_arc_v2", HAND_UP, 0, size=[[0, 2.2], [1, 3]], life=0.12, mode="Loop", rate=[[0.02, T, 18]], seed=101)
    L.append({"type": "emitter", "at": HAND_UP, "part": [6, 6, 6], "rate": [[0.02, T - 0.02, 50]], "seed": 102, "props": {
        "Texture": "static_sparks", "Color": [[0, BLUE], [1, WHITE]], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere",
        "ShapeInOut": "Inward", "ShapeStyle": "Surface", "Size": [[0, 0.5], [1, 1.0]], "Lifetime": [0.1, 0.14], "Speed": [24, 30],
        "Orientation": "VelocityParallel", "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [25, 25],
        "FlipbookStartRandom": True, "ZOffset": 0.3}})
    L.append(haze([0, 0.8, 0], 0.0, 0.3, 10, size=(3, 5), rise=1.2, part=[4, 1, 4]))

    # ---- the strike: neon bolt two frames + one re-strike, exactly on the lance line
    for i, (t0, life, th) in enumerate([(T, 0.05, 0.2)]):   # one 2-frame strike; the shaft snaps short right after
        L.append({"type": "bolt", "from": HAND, "to": TIP, "t0": t0, "life": life, "color": CYAN, "thickness": th, "jitter": 0.5,
                  "segments": 16, "flicker": 0.034, "branch": 0.12, "seed": 111 + i, "brightness": 2.2})

    # ---- signature: the lance lingers. Shaft: tail end retracts toward the head as it dissolves (from keys)
    fl = flicker(0.08, ((0.13, 0.75), (0.17, 0.0), (0.27, 0.6), (0.31, 0.05)), tail=0.55)
    life = 0.62
    # strike frame = the whole line; then the shaft SNAPS SHORT to a compact spear impaled through the target
    stail = lerp(CHEST, HAND, 7 / 24)
    kb = lambda p, k: [p[0], p[1], p[2] - KB * min(1, k)]            # ride the knockback
    tail = [[0, HAND], [0.085, HAND], [0.18, stail, "outExpo"], [0.5, kb(stail, 1)], [0.72, kb(stail, 1)], [1, kb(HEAD0, 1), "in"]]
    head_to = [[0, HEAD0], [0.13, HEAD0], [0.5, kb(HEAD0, 1), "out"]]
    shaft_w = {"glow": (4.2, 5.0), "rim": (2.5, 3.0), "mid": (2.2, 2.7), "core": (1.1, 1.4)}   # thickens toward the head
    wid = {k: [[0, [a * 1.25, b * 1.25]], [0.05, [a, b], "out"], [0.6, [a * 0.75, b * 0.7]], [1, [a * 0.2, b * 0.2]]] for k, (a, b) in shaft_w.items()}
    L.append({"type": "vbeam", "from": tail, "to": head_to, "t0": T, "life": life, "reach": 1,
              "core": {"radius": [[0, 0.12], [0.1, 0.1], [0.4, 0.07], [0.6, 0]], "color": [[0, WHITE], [0.4, ICE]], "material": "Neon"},
              "planes": plane_stack(wid, count=3, twist={"mid": 90, "core": -120, "glow": 30, "rim": 90}, speed={"mid": 1.5, "core": 2.5},
                                      tlen={"glow": 9, "rim": 8, "mid": 8, "core": 6}, bright={"glow": 0.6},
                                      transparency={"glow": [[0, 0.3], [0.5, 0.5], [1, 1]], "rim": [[0, 0], [0.6, 0.3], [1, 1]], "mid": fl, "core": fl})})
    # head: a crackling arrowhead (pointed vbeam) around a solid neon spike, out the far side of the target
    head_life = 0.6
    hfrom = [[0, HEAD0], [0.13, HEAD0], [0.5, kb(HEAD0, 1), "out"]]
    hto = [[0, TIP], [0.13, TIP], [0.5, kb(TIP, 1), "out"]]
    L.append({"type": "vbeam", "from": hfrom, "to": hto, "t0": T, "life": head_life, "reach": 1,
              "planes": plane_stack({k: [[0, [w * 1.3, 0.05]], [0.06, [w, 0.05], "out"], [0.75, [w * 0.8, 0.05]], [1, [0.1, 0.0]]]
                                     for k, w in {"glow": 6.5, "rim": 4.2, "mid": 3.7, "core": 1.9}.items()},
                                    count=3, twist={"mid": 160, "core": -200}, speed={"mid": 2, "core": 3}, tlen={"glow": 4, "rim": 4, "mid": 4, "core": 3},
                                    bright={"glow": 0.6}, transparency={"glow": [[0, 0.3], [1, 1]], "rim": [[0, 0], [0.7, 0.2], [1, 1]],
                                                                        "mid": fl, "core": fl})})
    mid_head = lerp(HEAD0, TIP, 0.55)
    yaw = math.degrees(math.atan2(-(TIP[0] - HAND[0]), -(TIP[2] - HAND[2])))
    L.append({"type": "shell", "mesh": "spike", "material": "Neon", "t0": T, "life": head_life, "at": mid_head, "rot": [-90, yaw, 0],
              "move": {"from": mid_head, "to": kb(mid_head, 1), "t0": T + 0.08, "t1": T + 0.3, "ease": "out"},
              "scale": [[0, [1.6, 3.0, 1.6]], [0.05, [1.25, 2.7, 1.25], "out"], [0.8, [1.1, 2.6, 1.1]], [1, [0.05, 0.8, 0.05], "in"]],
              "color": [[0, WHITE], [0.25, ICE], [0.6, CYAN], [1, BLUE]], "transparency": [[0, 0], [0.7, 0.15], [1, 1]]})
    # arcs hop along the shaft while it lingers
    L.append({"type": "emitter", "at": stail, "move": {"from": kb(stail, 1), "to": kb(HEAD0, 1), "t0": T + 0.1, "t1": T + 0.45}, "rate": [[T + 0.1, T + 0.45, 30]],
              "seed": 121, "props": {"Texture": "thunder_arc_v2_mid", "Color": [[0, WHITE], [0.4, CYAN], [1, BLUE]], "LightEmission": 0.4, "Brightness": 1.3,
                                     "Size": [[0, 1.6], [1, 2.2]], "Lifetime": [0.08, 0.12], "Speed": [0.5, 1], "Rotation": [0, 360],
                                     "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.4}})
    # head shatters into sparks as it dies
    L.append(sparks(kb(mid_head, 1), T + head_life * 0.8, 18, speed=(6, 16), life=(0.2, 0.4), seed=131))
    L += crackle(kb(mid_head, 1), T + head_life * 0.8, size=3.2, life=0.14, seed=132)

    # ---- release + impact (instant)
    L += crackle(HAND, T, size=3.2, seed=141)
    # ---- MODERN layering: big shapes -> medium -> small, then mass
    L += swirl(HAND_UP, 0.03, [[0, 1.5], [1, 3.4]], T - 0.03, seed=148, rot=30)          # charge swirl in the raised hand
    L.append(flare(HAND, T, size=12, life=0.22, seed=149))                                # release glint
    L.append(flare(CHEST, T + 0.005, size=14, life=0.28, seed=151))
    L += impact_v3(CHEST, T, size=8.5, life=0.42, seed=152)
    L += shockwave([0, 0, -26], T + 0.02, 7, life=0.45, seed=154)                         # ground shockwave under the target
    L.append(spark_burst(CHEST, T + 0.01, size=12, life=0.32, seed=155))
    L.append(streaks(CHEST, T + 0.01, 26, speed=(70, 120), length=(3, 7), spread=28, direction=[-90, 0, 0], seed=156))   # spray out the back
    L.append(streaks(CHEST, T + 0.01, 14, speed=(40, 80), length=(2, 4), seed=157))
    L += crack([0, 0, -26], T + 0.01, size=13, life=1.5, rot=-20, seed=158)
    L.append(smoke3([0, 2.0, -26.8], T + 0.04, n=5, size=(2.5, 5.5), speed=(3, 7), spread=80, seed=159, tr0=0.15))
    L.append(dust_ring([0, 0, -26], T + 0.02, n=14, speed=(20, 30), size=(2.5, 5), seed=160))
    L.append(haze([0, 1, -26], T + 0.05, T + 0.8, 18, size=(3, 8), rise=3, part=[3, 1, 3], seed=146))
    L += emit_stack("thunder_arc_v2", [0, 3.5, -25.6], T, size=[[0, 4], [1, 4.6]], life=0.16, mode="Loop", rate=[[T + 0.02, T + 0.5, 10]],
                    seed=147, colors=COOL, transparency=[[0, 0], [0.6, 0.3], [1, 1]])
    L += scar([0, 0, -26], T, size=10, rot=-20, glow_life=1.0, soot_life=3.0)

    dur = 1.6
    return {
        "name": "thunder_01_VoltLance", "title": "Volt Lance", "element": "Thunder", "archetype": "hitscan_javelin", "duration": dur,
        "layers": L,
        "hitstop": [{"t": T + 0.015, "dur": 0.06}],
        "hits": [{"t": T, "dummy": 0, "dir": [0, 0, -1], "power": KB / 3.5}],
        "numbers": [{"t": T + 0.02, "at": [0.6, 6.4, -26], "text": "88", "color": CYAN, "vel": [3, 15, 0], "size": 2.2}],
        "shakes": [{"t": T, "amp": 0.45, "dur": 0.28, "freq": 26}],
        "debris": rocks([0, 0, -26], T, radius=3.2, count=6, size=0.6, speed=24, crater=False, seed=15),
        "lights": [light(HAND_UP, [[0, 0], [0.12, 7], [T - 0.005, 9], [T, 0]], rng=9),
                   light(HAND, [[T - 0.005, 0], [T, 16], [T + 0.15, 2], [T + 0.3, 0]], rng=9),
                   light(CHEST, [[T - 0.005, 0], [T, 22], [T + 0.35, 4], [T + 0.9, 0]], rng=11)],
        "grade": [[0, 0, 0, 0, "#ffffff"], [T - 0.01, -0.06, 0.12, -0.03, "#e4ecff"], [T + 0.35, -0.02, 0.05, 0.02, "#eef3ff"], [1.2, 0, 0, 0, "#ffffff"]],
        "pose": {"lean": [[0, 0], [0.13, -16, "out"], [T - 0.005, -16], [T + 0.04, 20, "out"], [T + 0.3, 8], [T + 0.8, 0]],
                 "twist": [[0, 0], [0.13, 28, "out"], [T - 0.005, 28], [T + 0.04, -22, "out"], [T + 0.5, -6], [T + 0.9, 0]],
                 "armR": [[0, 0], [0.13, 205, "out"], [T - 0.005, 210], [T + 0.03, 70, "out"], [T + 0.12, 62], [T + 0.4, 80], [T + 1.0, 0]],
                 "armL": [[0, 0], [0.13, 60, "out"], [T - 0.005, 70], [T + 0.04, -40, "out"], [T + 0.7, 0]],
                 "scale": [[0, [1, 1, 1]], [0.13, [1.04, 0.95, 1.04], "out"], [T, [0.96, 1.06, 0.96]], [T + 0.1, [1, 1, 1]]]},
        # side-on: caster on the right, the impaled target and the spear head out its back on the left
        # wide side-on for the throw (caster left, target right), then glide in on the impaled target
        "camera": {"pos": [[0, [25, 7, -14]], [T / dur, [24.5, 6.9, -14.5]], [T / dur + 0.012, [23, 6.6, -16], "outExpo"],
                           [0.3, [21, 6.2, -18.5]], [0.55, [15, 5.4, -22.5], "out"], [1, [13.5, 5.2, -23.5]]],
                   "look": [[0, [0, 4.2, -14]], [T / dur + 0.012, [0, 4.1, -16], "outExpo"], [0.3, [0, 4, -19]], [0.55, [0, 3.8, -26], "out"], [1, [0, 3.7, -27]]],
                   "fov": [[0, 55], [T / dur, 54], [T / dur + 0.012, 49, "out"], [0.3, 53], [1, 52]]},
        "poster": T + 0.03, "dummies": [[0, 0, -26]],
    }


write(build(), os.path.join(os.path.dirname(__file__), "thunder_01_VoltLance.json"))
print("wrote thunder_01_VoltLance.json")
