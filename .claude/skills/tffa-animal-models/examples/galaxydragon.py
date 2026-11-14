"""TFFA GalaxyDragon (Space) - hero build on the approved dragon archetype (LavaDrake lineage: studded + muscular).

Reference analysis (iconic "galaxy / nebula dragon" art, most important first):
1. Silhouette: the approved upright, barrel-chested dragon with huge raised wings, long neck, spade tail.
2. Head: horned, frilled dragon head, glowing magenta eyes; a crown of glowing crystal shards between the horns.
3. Signature: the body is deep space - violet scales with glowing star specks; the wing membranes are a nebula
   (violet with cyan and magenta clouds); glowing crystal spines down the neck/back/tail; cyan belly shield.
4. Colours: deep violet, cyan belly, magenta glow (one glow colour), white stars.
Archetype dragon + bespoke extras (bones referenced explicitly)."""
import sys, os, math, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_archetypes import *

C1, C2, MEM, BEL, GL, STARW = rgb(64, 32, 116), rgb(36, 18, 72), rgb(84, 46, 160), rgb(42, 164, 206), rgb(255, 110, 225), rgb(250, 248, 255)
NEB_C, NEB_M = rgb(70, 190, 230), rgb(214, 80, 200)

def galaxy(m, c):
    rnd = np.random.default_rng(31)
    with m.bone("Body"):                      # star specks over the torso and haunches
        for k in range(16):
            s = 1 if k % 2 else -1; x = rnd.uniform(-1.6, 0.6); z = rnd.uniform(2.6, 5.4)
            m.box(f"Star{k}", (x, s * (2.05 - 0.1 * (z - 2.6) / 2.8), z), (0.16, 0.06, 0.16), STARW, studs=False)
        for k in range(4):
            s = 1 if k % 2 else -1
            m.box(f"Nebula{k}", (rnd.uniform(-1.4, 0.2), s * 2.02, rnd.uniform(3.0, 5.0)), (0.9, 0.05, 0.5), NEB_C if k < 2 else NEB_M, studs=False)
    for t, (x, z) in (("Tail1", (-3.6, 2.2)), ("Tail2", (-5.0, 1.3))):
        with m.bone(t):
            for s in (1, -1): m.box(f"TStar{t}{s}", (x, s * 0.55, z + 0.35), (0.14, 0.06, 0.14), STARW, studs=False)
    with m.bone("Head"), m.frame(pivot=(1.5, 0, 8.2), scale=1.25, move=(0, 0, 1.0)):   # crystal crown (same frame as the head)
        for k, (y, h, lean) in enumerate(((0.0, 1.4, -0.35), (0.35, 1.0, -0.45), (-0.35, 1.0, -0.45), (0.62, 0.7, -0.55), (-0.62, 0.7, -0.55))):
            b = Vector((1.75, y, 9.55))
            m.spike(f"Crown{k}", b, b + Vector((lean, y * 0.3, h)), 0.16 if k else 0.2, GL, sides=4, glow=True)
    for s in (1, -1):                          # nebula clouds stuck to the wing membranes (follow the wing bones)
        with m.bone(f"Wing_{'L' if s > 0 else 'R'}"):
            for j, (x, y, z, w, col) in enumerate(((-1.6, 3.4, 8.8, 1.3, NEB_C), (-2.2, 4.6, 9.8, 1.0, NEB_M), (-1.2, 2.6, 7.4, 0.9, NEB_M))):
                m.box(f"Cloud{s}{j}", (x, s * y, z), (w, w * 0.8, 0.12), col, rot=Rx(s * 0.5), studs=False)
                m.box(f"WingStar{s}{j}", (x + 0.3, s * (y + 0.2), z + 0.5), (0.14, 0.14, 0.1), STARW, rot=Rx(s * 0.5), studs=False)

out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "models", "TFFA", "GalaxyDragon")
build("GalaxyDragon", dragon, dict(s=0.85, studded=True, muscular=True, c1=C1, c2=C2, mem=MEM, belly=BEL, seg=rgb(30, 124, 170), knob=GL,
      horn=rgb(214, 180, 255), eye=GL, eye_glow=True, spikes=GL, spike_glow=True, glow=GL, x=[galaxy]), out,
      views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 30, 15, 45)])
