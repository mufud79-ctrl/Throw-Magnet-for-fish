"""TFFA AstroDog (Space) - hero build on the quad body.

Reference analysis (iconic dog astronaut, Laika-style mission art, most important first):
1. Silhouette: a brave, sturdy dog standing proud in a chunky space suit, chest out, head up, tail up.
2. Head: beagle head (tan with a white muzzle/blaze), long floppy brown ears, determined friendly eyes; an open-face
   helmet ring around the head with an antenna and a glowing tip.
3. Signature: white suit with orange stripes and a mission patch; chest control panel with coloured buttons; oxygen
   backpack with twin tanks and a light; chunky boots.
4. Colours: white suit, orange accents, tan + brown dog, cyan lights (one glow colour).
Archetype quad + bespoke accessories."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_archetypes import *

SUIT, ORNG, TANC, EARC, GL, BOOT = rgb(236, 238, 246), rgb(246, 132, 36), rgb(214, 150, 92), rgb(120, 72, 40), rgb(110, 230, 255), rgb(120, 124, 138)

def suit(m, c):
    L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
    for s in (1, -1):
        m.box(f"Stripe{s}", (0, s * (W / 2 + 0.02), z0 - H * 0.05), (L * 0.85, 0.06, H * 0.14), ORNG, studs=False)
        m.box(f"Patch{s}", (L * 0.18, s * (W / 2 + 0.04), z0 + H * 0.22), (0.4, 0.06, 0.4), ORNG, studs=False)
        m.box(f"PatchIn{s}", (L * 0.18, s * (W / 2 + 0.07), z0 + H * 0.22), (0.24, 0.04, 0.24), rgb(40, 90, 200), studs=False)
    # chest control panel with buttons
    px = L / 2 + 0.02
    m.box("Panel", (px, 0, z0 + H * 0.05), (0.14, W * 0.5, H * 0.42), LGREY, studs=False)
    for j, (y, z, col) in enumerate(((-0.18, 0.12, RED), (0.0, 0.12, YELLOW), (0.18, 0.12, rgb(80, 200, 80)), (0.0, -0.08, GL))):
        m.box(f"Button{j}", (px + 0.08, y * W * 1.4, z0 + H * z), (0.08, 0.14, 0.14), col, studs=False, glow=(col == GL))

def backpack(m, c):
    L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]; top = z0 + H / 2
    m.box("Pack", (-L * 0.05, 0, top + 0.3), (L * 0.42, W * 0.72, 0.6), SUIT, top=(0.92, 0.92))
    for s in (1, -1):
        m.seg(f"Tank{s}", (-L * 0.24, s * W * 0.22, top + 0.62), (L * 0.14, s * W * 0.22, top + 0.62), 0.42, 0.42, ORNG, studs=False)
        m.box(f"TankCap{s}", (L * 0.17, s * W * 0.22, top + 0.62), (0.14, 0.3, 0.3), LGREY, studs=False)
    m.box("PackLight", (-L * 0.27, 0, top + 0.35), (0.08, W * 0.3, 0.16), GL, glow=True, studs=False)

def helmet(m, c):
    hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
    with c["head"]():
        # open-face helmet: a ring framing the face (top, sides, chin) set behind the eyes
        m.box("HelmTop", hc + Vector((-hl * 0.05, 0, hh * 0.62)), (hl * 1.15, hw * 1.25, hh * 0.22), SUIT, top=(0.9, 0.9))
        for s in (1, -1):
            m.box(f"HelmSide{s}", hc + Vector((-hl * 0.05, s * hw * 0.62, 0)), (hl * 1.15, hw * 0.12, hh * 1.3), SUIT)
            m.box(f"HelmStripe{s}", hc + Vector((-hl * 0.05, s * hw * 0.69, hh * 0.2)), (hl * 0.9, 0.05, hh * 0.12), ORNG, studs=False)
        m.box("HelmChin", hc + Vector((-hl * 0.05, 0, -hh * 0.62)), (hl * 1.15, hw * 1.25, hh * 0.18), SUIT)
        m.seg("Antenna", hc + Vector((-hl * 0.3, hw * 0.35, hh * 0.7)), hc + Vector((-hl * 0.45, hw * 0.42, hh * 1.5)), 0.09, 0.07, LGREY, studs=False)
        m.box("AntennaTip", hc + Vector((-hl * 0.46, hw * 0.42, hh * 1.56)), (0.24, 0.24, 0.24), GL, glow=True, studs=False)
        m.box("Blaze", hc + Vector((hl * 0.5 + 0.01, 0, hh * 0.25)), (0.06, hw * 0.18, hh * 0.5), WHITE, studs=False)

out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "models", "TFFA", "AstroDog")
build("AstroDog", quad, dict(body=(2.5, 1.5, 1.5), legs=(0.95, 0.58), head=(1.25, 1.25, 1.1), neck=(0.3, 0.7), c1=SUIT, head_c=TANC,
      snout=(0.55, 0.75, 0.55), snout_c=WHITE, nose_c=rgb(40, 30, 30), ears="floppy", ear_c=EARC, tail="short", tail_c=TANC,
      leg_c=SUIT, feet=BOOT, brow=rgb(90, 56, 32), glow=GL, x=[suit, backpack, helmet]), out,
      views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 30, 15, 45)])
