"""TFFA SpaceCat (Space) - hero build on the reviewed muscular cat body (Panther lineage), never a "house cat".

Reference analysis (iconic "galaxy cat" / cosmic panther art, most important first) - v2 after "looks bad":
1. Silhouette: sleek, long-legged, muscular big cat mid-stride, long thick tail curling up at the end, head low and
   forward with a fierce stare.
2. Head: broad cat head, short ears, glowing cyan eyes under heavy brows, fierce closed mouth.
3. Signature: fur is a night sky - deep violet crossed by GLOWING cyan galaxy stripes like a tiger (back, flanks,
   legs), nebula shading, glowing star specks, glowing lynx ear tufts; space gear:
   an astronaut collar ring around the neck and a jetpack on the back with glowing thruster flames; a glowing star on
   the tail tip.
4. Colours: deep violet fur, magenta + cyan nebula, white suit parts, cyan glow (one glow colour).
Archetype quad(muscular, fierce) + bespoke accessories below."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_archetypes import *

FUR, NEB_M, NEB_C, SUIT, GL = rgb(58, 42, 112), rgb(196, 70, 190), rgb(60, 170, 220), rgb(232, 234, 244), rgb(110, 236, 255)

def nebula(m, c):
    """Glowing galaxy stripes (tiger-style) wrapping over the back and down the flanks + legs; deep nebula shading."""
    L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
    for j, x in enumerate((0.3, 0.14, -0.02, -0.18, -0.33)):
        top = z0 + H * (0.6 if x > 0 else 0.55); a = 0.25 * (-1) ** j
        m.box(f"StripeTop{j}", (x * L, 0, top + 0.02), (0.16, W * 0.8, 0.06), GL, rot=Rz(a), glow=True, studs=False)
        for s in (1, -1):
            m.box(f"Stripe{s}{j}", (x * L - 0.12, s * (W * 0.56 + 0.03), z0 + H * 0.15), (0.14, 0.06, H * 0.75), GL, rot=Ry(0.35 * (-1) ** j), glow=True, studs=False)
            m.box(f"Shade{s}{j}", (x * L + 0.25, s * (W * 0.56 + 0.02), z0 - H * 0.05), (0.5, 0.05, H * 0.5), NEB_M if j % 2 else NEB_C, studs=False)
    for sx in (1, -1):        # stripes on the legs
        for s in (1, -1):
            x = sx * (L / 2 - c["lw"] * 0.62) - (L * 0.07 if sx > 0 else 0); y = s * (W / 2 - c["lw"] * 0.5 - 0.06)
            with m.bone(f"Leg_{'F' if sx > 0 else 'B'}{'L' if s > 0 else 'R'}"):
                for k, z in enumerate((c["lh"] * 0.75, c["lh"] * 0.45)):
                    m.box(f"LegStripe{sx}{s}{k}", (x, y + s * (c["lw"] * 0.62), z), (c["lw"] * 0.9, 0.05, 0.12), GL, rot=Rx(0.3 * s), glow=True, studs=False)

def ear_tufts(m, c):
    hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
    with c["head"]():
        for s in (1, -1):
            b = hc + Vector((-hl * 0.15, s * hw * 0.38, hh * 0.85))
            m.spike(f"EarTuft{s}", b, b + Vector((-0.05, s * 0.08, 0.55)), 0.09, GL, glow=True)

def star_specks(m, c):
    L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
    pts = [(-0.3, 0.3), (-0.1, -0.1), (0.15, 0.2), (0.3, -0.25), (-0.4, -0.15), (0.0, 0.38), (-0.2, 0.05)]
    for s in (1, -1):
        for j, (x, z) in enumerate(pts):
            m.box(f"Speck{s}{j}", (x * L, s * (W * 0.56 + 0.04), z0 + z * H), (0.12, 0.05, 0.12), GL, glow=True, studs=False)
    for j, x in enumerate((0.3, 0.05, -0.2, -0.38)):
        m.box(f"SpeckTop{j}", (x * L, (j % 2 - 0.5) * 0.4, z0 + H * 0.62), (0.12, 0.12, 0.05), GL, glow=True, studs=False)

def collar(m, c):
    b = c["neck_base"] + c["nd"] * 0.35; r = c["hw"] * 0.78
    for k in range(10):
        a = 2 * math.pi * k / 10; p = b + Vector((0, math.cos(a) * r, math.sin(a) * r * 0.95))
        m.box(f"Collar{k}", p, (0.42, 0.48, 0.36), SUIT, rot=Rx(a), studs=False)
    m.box("CollarLight", b + Vector((0.18, 0, -r * 0.95)), (0.12, 0.28, 0.14), GL, glow=True, studs=False)

def jetpack(m, c):
    L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]; top = z0 + H * 0.62
    m.box("Jetpack", (-L * 0.02, 0, top + 0.36), (L * 0.34, W * 0.7, 0.72), SUIT, top=(0.9, 0.9))
    m.box("JetStripe", (-L * 0.02, 0, top + 0.58), (L * 0.2, W * 0.2, 0.06), NEB_C, studs=False)
    for s in (1, -1):
        p = Vector((-L * 0.2, s * W * 0.24, top + 0.3))
        m.seg(f"Thruster{s}", p + Vector((0.35, 0, 0)), p, 0.4, 0.48, LGREY, studs=False)
        m.spike(f"Flame{s}", p + Vector((-0.02, 0, 0)), p + Vector((-1.1, 0, -0.1)), 0.22, GL, glow=True)

def tail_star(m, c):
    e = c.get("tail_end")
    if e is None: return
    with m.bone(c.get("tail_bone", "Tail3")):
        pts = []
        for k in range(10):
            a = math.pi / 2 + k * math.pi / 5; r = 0.42 if k % 2 == 0 else 0.18
            pts.append((math.cos(a) * r, math.sin(a) * r))
        m.slab("TailStar", pts, 0.12, GL, origin=e + Vector((-0.1, 0, 0.1)), xaxis=(0, 1, 0), yaxis=(0, 0, 1), glow=True)

out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "models", "TFFA", "SpaceCat")
build("SpaceCat", quad, dict(body=(3.6, 1.65, 1.5), legs=(1.55, 0.62), head=(1.55, 1.55, 1.0), neck=(0.6, 0.22), c1=FUR, snout=(1.0, 1.0, 0.72),
      snout_c=rgb(70, 54, 132), nose_c=rgb(26, 18, 48), feet=rgb(40, 30, 82), ears="cat", tail="long", tail_w=1.6, tail_c=FUR, angry=True,
      snarl=True, muscular=True, front_back=0.07, head_scale=1.3, iris=GL, eye_glow=True, brow=rgb(26, 18, 52), glow=GL,
      x=[nebula, star_specks, collar, jetpack, tail_star, ear_tufts]), out,
      views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 30, 15, 45)])
