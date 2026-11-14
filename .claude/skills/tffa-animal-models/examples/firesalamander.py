"""TFFA FireSalamander (Volcano) - user-picked design "Magma Newt" (SalB_MagmaNewt in tools/blender/tffa_salamander_variants.py,
where the build lives): basalt rock skin cracked with glowing lava, rock plates with obsidian spikes and molten tips, a brow
crest, glowing slit eyes, magma drool, glowing toe pads. v1 archived as _archive_firesalamander_v1.py / _Archive/FireSalamander_v1."""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "blender")); sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tffa-animal-models", "scripts"))
import tffa_salamander_variants as SV
T, V = SV.K()
out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(ROOT, "models", "TFFA", "FireSalamander")
m = T.Model("FireSalamander", out, stud=0.4, chamfer=0.18, jitter=0.05)
glow = SV.SalB_MagmaNewt(m, T, V)
m.done(views=[("hero", 40, 18, 45), ("front", 0, 12, 45), ("side", 90, 8, 45), ("ref", 30, 25, 45)], glow_color=glow)
