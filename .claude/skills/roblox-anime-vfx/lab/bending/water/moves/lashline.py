"""Lashline (water) - a sweeping water ribbon with a foam edge.

Beat sheet (fill in: timings, the five animation rules, one lead shape)
  0.00-0.35  anticipation: the source gathers (stance, pull-in, glow)
  0.35       release / strike: the PRIMARY lead shape (frame 0-2)
  +1-2 frames  SECONDARY shapes; then TERTIARY sparkles
  0.35-...   OUTSIDE haze spreads past the hit; MASS (dust, marks, debris); follow-through
Camera: fixed gameplay camera (an ability, not a cutscene).
Run: python3 lab/bending/water/moves/lashline.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from elements import element_kit  # noqa: E402

K = element_kit("water")
kit = K.kit
TA = 0.35
DUR = 1.6
TARGET = [0, 0, -9]


def build():
    L = []
    hit = [TARGET[0], 3.0, TARGET[2] + 1.0]
    # ---- anticipation (replace): the element's source gathers at the caster
    L += K.glint([0.6, 3.2, -1.2], TA - 0.12, size=2.5, life=0.18, seed=1)
    # ---- PRIMARY (replace with the move's lead shape: a sweeping water ribbon with a foam edge)
    L += K.stack("anime_slash", hit, TA, size=[[0, 7], [1, 7.5]], life=0.36, rot=-30, seed=2, z=0.6)
    # ---- SECONDARY (+1-2 frames): a dark accent + a flash
    L += K.ink(hit, TA + 0.02, 5, seed=3)
    L += K.glint([hit[0], hit[1] + 0.4, hit[2] + 0.3], TA + 0.01, size=4.5, life=0.2, seed=4)
    # ---- TERTIARY: the small bright bits
    L.append(K.needles(hit, TA + 0.02, 12, speed=(40, 70), size=3.4, spread=60, seed=5))
    # ---- OUTSIDE: the smooth haze past the hit (never skip it)
    L += K.haze([TARGET[0], 0, TARGET[2]], TA, 1.2, radius=5.0, height=4.0, strength=0.9, seed=6, cloud=0.5)
    # ---- MASS: dust ring, a ground mark, a dark anchor
    L.append(kit.dust_ring([TARGET[0], 0, TARGET[2]], TA + 0.01, n=10, speed=(20, 28), size=(2.5, 5), seed=7))
    L.append(K.dark_haze([TARGET[0], 3, TARGET[2] - 1], TA + 0.08, n=4, size=(3, 7), seed=8))
    return {
        "name": "water_01_Lashline", "title": "Lashline", "element": "water", "archetype": "lashline", "duration": DUR,
        "layers": L, "dummies": [TARGET],
        "hits": [{"t": TA + 0.02, "dummy": 0, "dir": [0, 0, -1], "power": 0.6}],
        "hitstop": [{"t": TA + 0.04, "dur": 0.06}],
        "shakes": [{"t": TA + 0.02, "amp": 0.2, "dur": 0.15, "freq": 22}],
        "lights": [K.light(hit, [[TA, 0], [TA + 0.02, 24], [TA + 0.3, 0]], rng=16)],
        "camera": kit.GAMEPLAY_CAM,
        "poster": TA + 0.06,
    }


K.write(build(), os.path.join(os.path.dirname(__file__), "water_01_Lashline.json"))
print("wrote water_01_Lashline.json")
