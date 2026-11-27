"""Revert (full F) - back to the player. Signature: the dragon COILS DOWN AROUND THE PLAYER'S SPOT AND COLLAPSES INTO
FLAME (its body heats orange and burns away into flame spikes), and the player drops out of the fire.

Beat sheet
  0.00-0.35  the dragon swoops low and coils down round the spot (a tightening spiral)     (anticipation)
  0.35-0.80  the body heats (tint -> orange) and burns away: flame spikes and wisps break off along the coil, a
             column of spikes at the centre shrinks inward, warm haze                     (follow-through)
  0.80       the player drops out at scale 1 and lands with a squash: glint, a small ring of spikes, dust, embers
  0.80-1.60  embers settle and cool, a scorch where the dragon stood, the grade returns to normal. No hit-stop.
Camera: the gameplay camera (the player is back).
Run: python3 lab/dragon/moves/revert.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

TC, TL = 0.35, 0.80
DUR = 1.6
CAM = {"pos": [[0, [11, 11, 13]], [1, [11, 11, 13]]], "look": [[0, [0, 3.5, -1]], [1, [0, 3.5, -1]]], "fov": [[0, 66], [1, 66]]}

POSE = {
    "offset": [[0, [0, 5, 0]], [TL - 0.08, [0, 5, 0]], [TL, [0, -0.4, 0], "in"], [TL + 0.12, [0, -0.2, 0]], [TL + 0.35, [0, 0, 0]], [DUR, [0, 0, 0]]],
    "scale": [[0, [0.01, 0.01, 0.01]], [TL - 0.1, [0.01, 0.01, 0.01]], [TL - 0.02, [0.9, 1.15, 0.9], "out"], [TL + 0.03, [1.22, 0.78, 1.22], "outExpo"],
              [TL + 0.2, [0.97, 1.04, 0.97]], [TL + 0.4, [1, 1, 1]], [DUR, [1, 1, 1]]],
    "armR": smooth([[0, 40], [TL, 60], [TL + 0.1, 20], [1.3, 0], [DUR, 0]]),
    "armL": smooth([[0, 40], [TL, 60], [TL + 0.1, 20], [1.3, 0], [DUR, 0]]),
    "lean": smooth([[0, 0], [TL + 0.05, 14], [1.2, 0], [DUR, 0]]),
}


def head_path():
    P = []
    t0, t1 = -1.4, 1.0
    n = int((t1 - t0) * 90)
    for k in range(n + 1):
        t = t0 + (t1 - t0) * k / n
        if t < 0:
            u = (t + 1.4) / 1.4
            P.append([R(t, 4), R([-22 + 13 * u, 14 - 6 * u, -14 + 8 * u])])
            continue
        u = min(1.0, t / TL)
        a = math.atan2(-6, -9) + 1.7 * 2 * math.pi * u ** 0.85
        r = 10.8 * (1 - 0.82 * u ** 0.9)
        y = 8 - 6.5 * u
        P.append([R(t, 4), R([math.cos(a) * r, y, math.sin(a) * r])])
    return P


def build():
    hp = head_path()
    L = [ambience([0, 0, 0], 0, DUR, radius=9, rate=8, seed=1801)]
    # the dragon: heats to orange and burns away over the coil
    t0, life = hp[0][0], hp[-1][0] - hp[0][0]
    k = lambda t: R((t - t0) / life, 3)
    L.append(dragon(hp, t0, life, jaw=[[0, 6], [1, 6]], tracks=whisker_tracks(1.2),
                    color=[[0, "#ffffff"], [k(TC), "#ffffff"], [k(0.6), "#ffb070"], [1, "#ff7a2a"]],
                    transparency=[[0, 0], [k(TC + 0.1), 0], [k(TL - 0.05), 0.85], [1, 1]]))
    # flame spikes + wisps breaking off along the coil as it burns
    for e in emit_stack("anime_flame_spike", hp[0][1], TC, size=[[0, 5], [1, 6]], life=0.3, rate=[[TC, TL, 60]], cool=False, seed=1802,
                        orient="FacingCameraWorldUp", z=0.3, transparency=[[0, 0], [0.6, 0.1], [1, 1]]):
        e["path"] = [[t, p] for t, p in hp if t >= 0]
        e["part"] = [4, 2, 4]
        e["props"]["Rotation"] = [-25, 25]
        L.append(e)
    L += wisps([0, 4, 0], TC, TL, 30, size=3.2, life=0.5, path=[[t, p] for t, p in hp if t >= 0], seed=1803)
    # the centre column of spikes shrinking inward
    for j in range(8):
        a = j / 8 * 2 * math.pi
        q = [math.cos(a) * 1.0, 0, math.sin(a) * 1.0]
        h = 8.5 - 0.8 * (j % 3)
        L += emit_stack("anime_flame_spike", [q[0], h * 0.42, q[2]], 0.42 + 0.02 * j, size=[[0, h], [0.6, h * 0.8], [1, h * 0.2]], life=TL - 0.4,
                        cool=False, rot=(j - 3.5) * 6, seed=1811 + j, orient="FacingCameraWorldUp", z=0.04 * j)
    L += aura_haze([0, 0, 0], TC, 1.1, radius=6.0, height=5.0, strength=0.8, seed=1821, cloud=0.5)
    # the player lands: glint, a small ring of spikes, dust, embers
    L += glint([0, 3.2, 0.5], TL, size=6, life=0.2, seed=1831)
    for j in range(6):
        a = j / 6 * 2 * math.pi + 0.3
        q = [math.cos(a) * 1.6, 0, math.sin(a) * 1.6]
        L += emit_stack("anime_flame_spike", [q[0], 1.4, q[2]], TL + 0.01, size=[[0, 3.4], [1, 3.6]], life=0.3, cool=False,
                        rot=-math.degrees(math.atan2(math.cos(a), 1.0)) * 0.5, seed=1841 + j, orient="FacingCameraWorldUp")
    dr = dust_ring([0, 0, 0], TL + 0.01, n=10, speed=(16, 22), size=(2, 4), seed=1851)
    dr["props"]["Transparency"] = [[0, 0.35], [0.6, 0.55], [1, 1]]
    L.append(dr)
    L.append(embers([0, 0.5, 0], TL, n=24, speed=(6, 12), life=(0.6, 1.2), grav=-6, seed=1852))
    L.append(embers([0, 0.4, 0], 0, rate=[[TL, DUR, 14]], speed=(0.5, 2), life=(0.8, 1.3), rise=2, grav=0, part=[6, 0.2, 6], seed=1853))
    L.append(scorch([0, 0, 0], TL, size=7, life=DUR - TL + 0.1, seed=1854))
    L.append(glow_pool([0, 0, 0], TC, 8, life=0.4, rate=[[TC, TL + 0.1, 10]], peak=0.3, seed=1855))
    L.append(dark_haze([0, 3, 0], TL, n=4, size=(3, 6), life=(0.8, 1.1), part=(2, 1, 2), tr=0.6, seed=1856))

    fx = {
        "name": "dragon_12_Revert", "title": "Revert", "element": "Dragon", "archetype": "revert", "duration": DUR,
        "layers": L, "pose": POSE, "camera": CAM, "_swap": TL - 0.1,
        "lights": [light([0, 3, 0], [[TC, 0], [0.5, 16], [TL, 18], [1.2, 4], [DUR, 0]], rng=18)],
        "poster": 0.6,
    }
    return fx


write(build(), out_path(os.path.dirname(__file__), "dragon_12_Revert"), form="from_full")
print("wrote dragon_12_Revert.json")
