"""Palette proof: the same neutral anime primitives (slash, glint, needles, ink, haze) in each element's look, side by
side on the sand, so the colour scripts can be judged together (value test: each must still read on sand)."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from elements import element_kit, kit  # noqa: E402

ROWS = [["water", "earth", "fire", "air"], ["ice", "metal", "lightning", "flight"], ["healing", "lava", "combustion", "projection"],
        ["plant", "sand", "dragonfire", "energy"], ["blood", "seismic", "spirit"]]
L = []
for r, row in enumerate(ROWS):
    for c, el in enumerate(row):
        K = element_kit(el)
        p = [(c - 1.5) * 9, 3.5, -6 - r * 9]
        t = 0.15 + 0.05 * c + 0.08 * r
        L += K.stack("anime_slash", p, t, size=[[0, 6], [1, 6.5]], life=0.9, rot=-30, seed=10 + 10 * r + c)
        L += K.glint([p[0] + 0.5, p[1] + 0.5, p[2] + 0.3], t + 0.02, size=3.5, life=0.5, seed=50 + 10 * r + c)
        L.append(K.needles(p, t + 0.02, 10, speed=(10, 20), size=2.5, life=(0.5, 0.8), seed=90 + 10 * r + c))
        L += K.ink(p, t + 0.03, 3.0, life=0.6, seed=130 + 10 * r + c)
        L += K.haze([p[0], 0, p[2]], t, 1.2, radius=3.0, height=3.0, strength=0.8, seed=170 + 10 * r + c, cloud=0.5)
kit.write({"name": "bending_test_Palettes", "duration": 1.4, "layers": L, "caster": False,
           "camera": {"pos": [[0, [0, 21, 8]], [1, [0, 21, 8]]], "look": [[0, [0, 0, -21]], [1, [0, 0, -21]]], "fov": [[0, 60], [1, 60]]}},
          os.path.join(os.path.dirname(__file__), "bending_test_Palettes.json"), form="full")
