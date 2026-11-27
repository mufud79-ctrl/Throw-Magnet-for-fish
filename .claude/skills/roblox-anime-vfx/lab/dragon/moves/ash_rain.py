"""Ash Rain (full B) - fireball barrage from above (zone denial). Signature: a SPIRAL OF SMALL CRATERS burned into the
ground while ash drifts over the zone.

Beat sheet
  0.00-0.50  the dragon climbs into a wide circle overhead (radius 12, ~18 up)             (anticipation)
  0.50-2.40  a fireball drops from the jaw every 0.19 s (10): a hot core wrapped in flame spikes with a short trail,
             falling on an arc to points along a spiral; each lands as a small anime pop - a small spike crown, a
             glint, black ink, needles - and leaves a mini crater (bowl + molten core) and a scorch; hit-stop 0.04 on
             the ones that hit targets. Grey ash and embers drift down over the zone the whole time; warm haze
             builds over it
  2.40-3.20  the dragon pulls out of the circle; the craters smoulder and cool one by one in drop order
Camera: high and wide over the zone.
Run: python3 lab/dragon/moves/ash_rain.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

DUR = 3.2
C = [0, 0, -12]
N = 10
T0, DT, FALL = 0.5, 0.19, 0.42
TARGETS = [[-5.5, 0, -9.5], [5.0, 0, -15.5], [1.5, 0, -6.0]]
CAM = {"pos": [[0, [17, 21, 9]], [1, [17, 21, 9]]], "look": [[0, [-1, 6, -13]], [1, [-1, 6, -13]]], "fov": [[0, 64], [1, 64]]}


def head_path():
    P = []
    t0, t1 = -1.6, DUR + 0.4
    n = int((t1 - t0) * 60)
    for k in range(n + 1):
        t = t0 + (t1 - t0) * k / n
        if t < 0.5:
            u = (t + 1.6) / 2.1
            a = -0.4 + 1.2 * u
            r = 26 - 14 * u
            y = 8 + 10 * u
        elif t < 2.4:
            u = (t - 0.5) / 1.9
            a = 0.8 + 1.6 * 2 * math.pi * u
            r = 12
            y = 18 + 1.0 * math.sin(u * 9)
        else:
            u = (t - 2.4) / (t1 - 2.4)
            a = 0.8 + 1.6 * 2 * math.pi + 1.1 * u
            r = 12 + 14 * u
            y = 18 + 4 * u
        P.append([R(t, 4), R([C[0] + math.cos(a) * r, y, C[2] + math.sin(a) * r])])
    return P


def spiral(k):
    a = k * 1.05 + 0.3
    r = 1.5 + 1.15 * k
    return [C[0] + math.cos(a) * r, 0, C[2] + math.sin(a) * r]


def build():
    hp = head_path()
    hat = lambda t: min(hp, key=lambda q: abs(q[0] - t))[1]
    L = [ambience(C, 0, DUR, radius=16, rate=10, seed=1601)]
    # ash + embers drifting down over the whole zone, warm haze building over it
    L.append(ash([C[0], 14, C[2]], 0.3, DUR, 26, part=(26, 2, 26), seed=1602))
    L.append(embers([C[0], 14, C[2]], 0, rate=[[0.5, DUR - 0.3, 30]], speed=(1, 3), life=(1.5, 2.2), grav=-3, part=[24, 2, 24], seed=1603))
    L += aura_haze(C, 0.9, 2.2, radius=11.0, height=5.0, strength=0.8, seed=1604, cloud=0.4)

    hits, numbers, stops, debris = [], [], [], []
    for k in range(N):
        td = T0 + DT * k
        tl = td + FALL
        m = hat(td)
        g = spiral(k)
        # the fireball: hot core in flame spikes, falling on an arc, a short trail and needles behind
        arc = [[R(td + FALL * i / 20, 4), R([m[0] + (g[0] - m[0]) * (i / 20), m[1] + (1.0 - m[1]) * (i / 20) ** 1.6 + 2.5 * math.sin(math.pi * i / 20),
                                            m[2] + (g[2] - m[2]) * (i / 20)])] for i in range(21)]
        L.append(glow_orb(arc[0][1], td, 3.4, life=0.12, rate=[[td, tl, 40]], path=arc, locked=True, tr=0.2, seed=1611 + k))
        for e in emit_stack("anime_flame_spike", arc[0][1], td, size=[[0, 3.6], [1, 2.4]], life=0.12, rate=[[td, tl, 36]], cool=False,
                            seed=1621 + k, orient="FacingCameraWorldUp", z=0.4):
            e["path"] = [[t, [p[0], p[1] + 1.2, p[2]]] for t, p in arc]
            e["props"]["Rotation"] = [-30, 30]
            L.append(e)
        L += trail_stack({"path": arc, "at": arc[0][1], "t0": td, "t1": tl, "lifetime": 0.16, "faceCamera": True,
                          "transparency": [[0, 0], [0.5, 0.2], [1, 1]], "widthScale": [[0, 1], [1, 0.2]], "textureMode": "Stretch"},
                         {"glow": 3.0, "rim": 1.8, "mid": 1.2, "core": 0.35}, cool=False)
        # the landing: a small anime pop + mini crater
        for j in range(5):
            a = j / 5 * 2 * math.pi + k
            q = [g[0] + math.cos(a) * 1.2, 0, g[2] + math.sin(a) * 1.2]
            h = 6.0 + 1.6 * ((j + k) % 3) / 2
            L += emit_stack("anime_flame_spike", [q[0], h * 0.42, q[2]], tl + 0.008 * j, size=[[0, h * 0.95], [1, h * 1.05]], life=0.38, cool=False,
                            rot=-math.degrees(math.atan2(math.cos(a), 1.0)) * 0.5, seed=1631 + 7 * k + j, orient="FacingCameraWorldUp", z=0.04 * j)
        L += glint([g[0], 2.0, g[2]], tl, size=5.5, life=0.18, seed=1701 + k)
        L += ink([g[0], 1.8, g[2]], tl + 0.01, 4.0, rot=36 * k, life=0.24, seed=1711 + k)
        L.append(needles([g[0], 1.0, g[2]], tl + 0.01, 8, speed=(30, 55), size=3.0, spread=60, seed=1721 + k))
        cr = crater(g, tl, radius=2.6, life=DUR - tl + 0.05, slabs=8, seed=1731 + k)
        L += [x for x in cr if "kind" not in x]
        debris += [x for x in cr if "kind" in x]
        L.append(dark_haze([g[0], 2.5, g[2]], tl + 0.06, n=3, size=(3, 6), life=(0.8, 1.1), part=(1.5, 1, 1.5), tr=0.55, seed=1741 + k))
        L.append(glow_pool(g, tl, 5, life=0.4, peak=0.3, seed=1751 + k))
        L += flicker(g, tl + 0.15, min(DUR, tl + 1.0), 1.4, seed=1761 + k)
        for i, q in enumerate(TARGETS):
            if math.hypot(q[0] - g[0], q[2] - g[2]) < 2.6:
                hits.append({"t": tl + 0.01, "dummy": i, "dir": [R((q[0] - g[0]) * 0.3), 0.3, R((q[2] - g[2]) * 0.3)], "power": 0.5})
                numbers.append({"t": tl + 0.03, "at": [q[0], 6, q[2]], "text": str(58 + 6 * k), "color": GOLD, "vel": [0, 9, 0], "size": 1.5})
                stops.append({"t": tl + 0.02, "dur": 0.04})

    t0, life = hp[0][0], hp[-1][0] - hp[0][0]
    jaw = [[0, 6], [(T0 - 0.1 - t0) / life, 30], [(T0 + DT * N - t0) / life, 30], [(2.6 - t0) / life, 6], [1, 6]]
    L.append(dragon(hp, t0, life, jaw=R(jaw, 3), tracks=whisker_tracks(DUR + 0.5)))

    return {
        "name": "dragon_11_AshRain", "title": "Ash Rain", "element": "Dragon", "archetype": "fireball_barrage", "duration": DUR,
        "caster": False, "layers": L, "dummies": TARGETS, "hits": hits, "numbers": numbers, "debris": debris,
        "hitstop": stops,
        "shakes": [{"t": T0 + DT * k + FALL, "amp": 0.15, "dur": 0.12, "freq": 22} for k in range(N)],
        "lights": [light(C, [[0.8, 0], [1.0, 14], [2.6, 14], [3.0, 2]], rng=26)],
        "camera": CAM,
        "poster": 2.0,
    }


write(build(), out_path(os.path.dirname(__file__), "dragon_11_AshRain"), form="full")
print("wrote dragon_11_AshRain.json")
