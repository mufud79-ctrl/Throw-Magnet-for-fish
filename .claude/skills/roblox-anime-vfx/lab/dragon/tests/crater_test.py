import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa
cr = crater([0, 0, -10], 0.1, radius=5.5, life=2.0, seed=646)
L = [x for x in cr if "kind" not in x]
D = [x for x in cr if "kind" in x]
write({"name": "dragon_test_Crater", "duration": 1.5, "layers": L, "debris": D, "caster": False, "camera": GAMEPLAY_CAM},
      os.path.join(os.path.dirname(__file__), "dragon_test_Crater.json"))
