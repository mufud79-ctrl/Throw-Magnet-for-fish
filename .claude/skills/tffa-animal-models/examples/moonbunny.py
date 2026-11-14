"""TFFA MoonBunny (Space) - user-picked design from 4 variations (BunnyC_Saturn in tools/blender/tffa_space_variants.py, where the
build lives with its reference notes). Previous version archived as _archive_moonbunny_v2.py / models/.../_Archive/MoonBunny_v2."""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "blender")); sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tffa-animal-models", "scripts"))
import tffa_space_variants as SV
T, V = SV.K()
out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(ROOT, "models", "TFFA", "MoonBunny")
m = T.Model("MoonBunny", out, stud=0.42, chamfer=0.17, jitter=0.05)
glow = SV.BunnyC_Saturn(m, T, V)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 30, 15, 45)], glow_color=glow)
