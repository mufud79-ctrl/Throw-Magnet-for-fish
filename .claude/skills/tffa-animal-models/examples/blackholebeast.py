"""TFFA BlackHoleBeast (Space) - hero build on the reviewed snarling muscular quad (Panther lineage).

Reference analysis (iconic "void beast" / cosmic horror predator art, most important first):
1. Silhouette: a hulking, muscular void predator, shoulders high, head low and snarling; a black-hole orb with a
   tilted, blazing accretion ring hovers above its shoulders - the signature, read from every side.
2. Head: snarling open jaw with long fangs, glowing violet eyes under heavy brows.
3. Signature: jet-black body cracked with glowing violet veins; jagged dark crystal spines down the back glowing at the
   tips; smoky void wisps curling off the paws and tail.
4. Colours: near-black violet body, violet glow (one glow colour), pale violet-white ring highlights.
Archetype quad(snarl, muscular) + bespoke accessories."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_archetypes import *

VOID, VOID_L, GL, CRYS = rgb(30, 26, 42), rgb(52, 44, 72), rgb(196, 96, 255), rgb(70, 40, 110)

def cracks(m, c):
    L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
    for s in (1, -1):
        for j, (x, z, l, a) in enumerate(((0.25, 0.15, 0.32, 0.6), (0.05, -0.1, 0.28, -0.5), (-0.25, 0.2, 0.3, 0.35), (-0.35, -0.2, 0.22, -0.7),
                                          (0.32, -0.25, 0.18, 0.2))):
            m.box(f"Crack{s}{j}", (x * L, s * (W * 0.6 + 0.02), z0 + z * H), (l * L * 0.5, 0.06, 0.1), GL, rot=Ry(a), glow=True, studs=False)
            m.box(f"CrackB{s}{j}", (x * L + l * L * 0.18, s * (W * 0.6 + 0.02), z0 + z * H + 0.12), (l * L * 0.2, 0.06, 0.08), GL, rot=Ry(a + 1.0), glow=True, studs=False)

def crystal_spines(m, c):
    L, H, z0 = c["L"], c["H"], c["z0"]
    for k in range(7):
        x = L * 0.32 - L * 0.7 * k / 6; h = H * (0.75 - 0.05 * abs(k - 2))
        b = Vector((x, 0, z0 + H * 0.55))
        m.spike(f"Crystal{k}", b, b + Vector((-H * 0.25, 0, h)), H * 0.16, CRYS, flat=0.5)
        m.spike(f"CrystalTip{k}", b + Vector((-H * 0.16, 0, h * 0.62)), b + Vector((-H * 0.25, 0, h)), H * 0.07, GL, flat=0.5, glow=True)
        for s in (1, -1):
            if k % 2 == 0:
                m.spike(f"CrystalS{k}{s}", b + Vector((0, s * 0.35, -0.1)), b + Vector((-H * 0.2, s * 0.75, h * 0.55)), H * 0.1, CRYS, flat=0.5)

def black_hole(m, c):
    L, H, z0 = c["L"], c["H"], c["z0"]
    o = Vector((L * 0.08, 0, z0 + H * 1.55)); R = H * 0.95
    m.ball("Hole", o, H * 0.42, rgb(8, 6, 12))
    m.box("HoleRim", o, (H * 0.95, H * 0.95, 0.12), GL, rot=Ry(0.3) @ Rx(0.0), glow=True, studs=False)
    tilt = Ry(0.3) @ Rx(0.35)
    for k in range(16):       # accretion ring: blazing segments, thicker on one side
        a = 2 * math.pi * k / 16; p = tilt @ Vector((math.cos(a) * R, math.sin(a) * R, 0))
        w = 0.22 + 0.12 * (1 + math.cos(a)) / 2
        m.box(f"Ring{k}", o + p, (0.55 * R / 1.5, w, 0.16), GL if k % 2 else rgb(236, 210, 255), rot=tilt @ Rz(a + math.pi / 2), glow=(k % 2 == 1), studs=False)
    for k in range(5):        # debris orbiting the hole
        a = k * 1.3; p = tilt @ Vector((math.cos(a) * R * 1.3, math.sin(a) * R * 1.3, 0.2 * (k % 2)))
        m.box(f"Debris{k}", o + p, (0.18, 0.18, 0.18), VOID_L, rot=Rz(a) @ Rx(a), studs=False)
    m.seg("Tether", Vector((L * 0.08, 0, z0 + H * 0.62)), o + Vector((0, 0, -H * 0.42)), 0.18, 0.08, GL, glow=True, studs=False)

def wisps(m, c):
    L, W, lw = c["L"], c["W"], c["lw"]
    for sx in (1, -1):
        for s in (1, -1):
            x = sx * (L / 2 - lw * 0.62) - (L * 0.07 if sx > 0 else 0); y = s * (W / 2 - lw * 0.5 - 0.06)
            with m.bone(f"Leg_{'F' if sx > 0 else 'B'}{'L' if s > 0 else 'R'}"):
                for j in range(3):
                    a = j * 2.1 + sx
                    m.spike(f"Wisp{sx}{s}{j}", (x - 0.15 + 0.3 * math.cos(a), y + 0.3 * math.sin(a), 0.25), (x - 0.6 + 0.4 * math.cos(a), y + 0.55 * math.sin(a), 0.75),
                            0.12, VOID_L, flat=0.5)

out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "models", "TFFA", "BlackHoleBeast")
build("BlackHoleBeast", quad, dict(body=(3.8, 1.75, 1.6), legs=(1.6, 0.66), head=(1.55, 1.55, 1.0), neck=(0.6, 0.22), c1=VOID,
      snout=(1.0, 1.0, 0.72), snout_c=VOID_L, nose_c=rgb(14, 12, 20), feet=rgb(16, 14, 24), ears="cat", tail="long", tail_w=1.7,
      tail_c=VOID, angry=True, snarl=True, muscular=True, front_back=0.07, iris=GL, eye_glow=True, brow=rgb(10, 8, 14), glow=GL,
      head_scale=1.3, x=[cracks, crystal_spines, black_hole, wisps]), out,
      views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 30, 15, 45)])
