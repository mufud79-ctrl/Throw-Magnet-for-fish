import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa
L = []
L += wall_beam([[0, [-7, 3.5, -8]], [1, [-7, 3.5, -8]]], [[0, [7, 3.5, -8]], [1, [7, 3.5, -8]]], 0.0, 1.5, 7)
L += ring_wall([0, 0, -14], 4.5, 0.1, 1.2, 4)
write({"name": "dragon_test_Walls", "duration": 1.5, "layers": L, "caster": False, "camera": GAMEPLAY_CAM}, os.path.join(os.path.dirname(__file__), "dragon_test_Walls.json"))
