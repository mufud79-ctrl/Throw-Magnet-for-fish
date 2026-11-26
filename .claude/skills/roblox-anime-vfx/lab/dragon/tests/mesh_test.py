"""Mesh-led fire impact test (the rework): swirl vortex + whirling crescents + ring + dome + tube wall."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa
T = 0.2
G = [0, 0, -8]
def shell(mesh, tex, t0, life, scale, at, rot=(0, 0, 0), spin=0, scroll=(0, 0), tr=None, axis=(0, 1, 0), bright=1.15, tile=(1, 1)):
    return {"type": "shell", "mesh": mesh, "material": "Textured", "texture": tex, "t0": t0, "life": life, "scale": scale, "at": R(at),
            "rot": list(rot), "spin": spin, "spinAxis": list(axis), "scroll": list(scroll), "color": "#ffffff", "brightness": bright,
            "transparency": tr or [[0, 0], [0.7, 0.1], [1, 1]], "tile": list(tile)}
L = []
# primary: a flattened swirl vortex spinning fast, scrolling (two, counter-turning)
L.append(shell("swirl", "fx_fire_band", T, 0.75, [[0, [2, 0.3, 2]], [0.2, [8, 0.9, 8], "out"], [1, [10, 0.5, 10]]], [G[0], 0.5, G[2]], spin=720, scroll=(-2.5, 0)))
L.append(shell("swirl", "fx_fire_band", T + 0.03, 0.7, [[0, [1.5, 0.6, 1.5]], [0.2, [6, 1.6, 6], "out"], [1, [7, 0.8, 7]]], [G[0], 1.0, G[2]], spin=-540, scroll=(-3, 0)))
# secondaries: whirling crescent slashes around the impact
for k in range(3):
    L.append(shell("crescent_full", "fx_fire_slash", T + 0.04 + 0.03 * k, 0.45, [[0, 3], [0.25, 9 - k, "out"], [1, 10 - k]], [G[0], 1.2 + 1.2 * k, G[2]],
                   rot=(8 * (k - 1), 120 * k, 0), spin=600 - 180 * k, tr=[[0, 0], [0.6, 0.1], [1, 1]]))
L.append(shell("ring_flat", "fx_fire_ring", T + 0.02, 0.5, [[0, 2], [1, 15, "out"]], [G[0], 0.25, G[2]], spin=90, tr=[[0, 0], [0.5, 0.15], [1, 1]]))
L.append(shell("dome", "fx_fire_ball", T, 0.35, [[0, [1, 1, 1]], [0.4, [5, 4, 5], "out"], [1, [6, 3, 6]]], G, spin=300, scroll=(0.5, -0.8), tr=[[0, 0], [0.4, 0.2], [1, 1]]))
L.append(shell("tube", "fx_fire_band", T + 0.06, 0.9, [[0, [6, 0.2, 6]], [0.15, [8.5, 1.4, 8.5], "out"], [0.8, [8.7, 1.2, 8.7]], [1, [8.8, 0.3, 8.8]]], [G[0], 1.4, G[2]],
               rot=(180, 0, 0), spin=60, scroll=(1.2, 0), tile=(4, 1)))
fx = {"name": "dragon_test_Mesh", "duration": 1.3, "layers": L, "dummies": [[-4, 0, -10], [4, 0, -11]], "camera": GAMEPLAY_CAM}
write(fx, os.path.join(os.path.dirname(__file__), "dragon_test_Mesh.json"))
