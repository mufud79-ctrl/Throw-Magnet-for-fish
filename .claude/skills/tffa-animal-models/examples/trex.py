"""TFFA T-Rex (Prehistoric). Reference: the game icon. Golden studded blocks, huge head with the mouth wide open,
big white blade teeth, red mouth + pink tongue, white throat/jaw underside, ridge bumps on the snout,
square side eye with a heavy brow. Tiny arms, thick legs, long stepped tail.
Built by the `theropod` archetype (scripts/tffa_archetypes.py), which is this reviewed model made scalable + rigged."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_archetypes import *

out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "models", "TFFA", "TRex")
m = Model("TRex", out, stud=0.7, chamfer=0.14, jitter=0.09)
theropod(m, dict(s=1.0, c1=rgb(222, 150, 40), c2=rgb(160, 96, 30)))
m.done(views=[("hero", 40, 10, 45), ("side", 90, 4, 50), ("icon", 35, -6, 50, "plain", (5.0, 0, 7.9, 3.4))])
