import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa
L = []
L += billow([-4, 3, -8], 0.1, 5, life=0.8, seed=1)                      # plain emits
for e in billow([0, 3, -8], 0.1, 5, life=0.8, seed=2):                  # rate
    e.pop("emits"); e["rate"] = [[0.1, 1.0, 6]]; L.append(e)
for e in billow([4, 3, -8], 0.1, 5, life=0.8, seed=3):                  # rate + path
    e.pop("emits"); e["rate"] = [[0.1, 1.0, 6]]; e["path"] = [[0.1, [4, 3, -8]], [1.0, [4, 3, -12]]]; L.append(e)
write({"name": "dragon_test_Billow", "duration": 1.2, "layers": L, "caster": False, "camera": GAMEPLAY_CAM}, os.path.join(os.path.dirname(__file__), "dragon_test_Billow.json"))
