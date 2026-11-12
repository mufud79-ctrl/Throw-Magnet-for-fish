"""All Rare fish (aggressive tier starts here). Run: python rares.py [FishName ...] [--no-render]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishgen import *

RA = dict(rarity="Rare", brow=True, pupil=(0.3, 0.22, 0.62), eye_k=0.048)
SLIT_IRIS = c(236, 190, 50)

def scutes_hook(f, sp):
    for th in (math.pi / 2, 0.3, -0.4):
        for sd in ((1,) if th == math.pi / 2 else (1, -1)):
            for i, t in enumerate(np.linspace(0.16, 0.84, 11)):
                p = side(f.surf(float(t), th, 1.0), sd); n = side((f.surf(float(t), th) - f.axis(float(t))).normalized(), sd)
                k = 1 - 0.4 * float(t)
                f.gem(f"Scute{th:.1f}_{sd}_{i}", p + n * 0.01, basis(n, V(1, 0, 0)), (0.06 * k, 0.09 * k, 0.07 * k), SW["x1"])
def lightning_hook(f, sp):
    for sd in (1, -1):
        for row, (a, b) in enumerate(((0.35, 0.05), (-0.2, -0.5))):
            pts = [side(f.surf(lerp(0.18, 0.93, i / 13), a if i % 2 else b, 1.01), sd) for i in range(14)]
            glow_line(f, f"Bolt{sd}_{row}", pts, 0.028, 0.012)
def lion_hook(f, sp):
    for i in range(13):
        k = i / 12; b = f.surf(lerp(0.17, 0.6, k), math.pi / 2, 0.9); h = 1.0 * (1 - 0.35 * k)
        f.tube(f"Spine{i}", [b, b + V(-0.1 - 0.1 * k, 0.02 * math.sin(i), h * 0.5), b + V(-0.25 - 0.25 * k, 0, h)], 0.04, 0.006, K=6, sub=3)
    for sd in (1, -1):                                   # brow tentacles
        b = side(f.surf(0.1, 0.9, 1.0), sd)
        f.tube(f"Tentacle{sd}", [b, b + V(0.02, sd * 0.05, 0.12), b + V(-0.06, sd * 0.08, 0.24)], 0.03, 0.006, K=6, sub=3)
def icy_hook(f, sp):
    for i, t in enumerate(np.linspace(0.3, 0.7, 4)):
        b = f.surf(float(t), math.pi / 2, 0.95)
        f.gem(f"Shard{i}", b + V(0, 0, 0.12), basis(V(0, 0, 1), V(1, 0, 0)), (0.07, 0.05, 0.2 - 0.03 * i), SW["glow"], glow=True)

FISH = [
 dict(RA, name="Pike", L=3.0, R=0.32, H=1.0, w=0.88, wt=0.3, prof="pike", colors=(c(46, 74, 38), c(110, 140, 64), c(236, 232, 200)),
      speckle=(c(214, 214, 140), 6, 0.74, -0.45), jaw=(0.02, 0.2, 18, 15, 13), mouth=0, iris=SLIT_IRIS, eye_t=0.15,
      dorsal=[(0.72, 0.82, 0.34, "round")], anal=(0.72, 0.82, 0.3, "round"), tail=("fork", 0.85, 38),
      fins=[[(0, c(90, 100, 50)), (0.7, c(190, 150, 70)), (1, c(220, 120, 60))], [(0, c(80, 100, 50)), (1, c(200, 140, 70))]]),
 dict(RA, name="Sturgeon", L=3.3, R=0.38, H=0.82, w=1.0, wt=0.45, prof="pike", belly=0.7,
      zc_fn=lambda t: 0.14 * 0.38 * (1 - t) ** 8 + 0.02 * math.sin(math.pi * t),
      colors=(c(70, 66, 58), c(110, 104, 92), c(226, 220, 204)), noise=0.2, scale_k=0.0, hook=scutes_hook, x1=c(232, 222, 196),
      barbels=[(0.04, -1.25, 0.16, 1.0), (0.045, -1.5, 0.16, 1.0)], barbel_c=c(220, 210, 190), mouth=0.05, eye_t=0.13,
      dorsal=[(0.74, 0.82, 0.3, "tri")], anal=(0.74, 0.82, 0.24, "round"), tail=("shark", 1.2, (-32, 60)), pect=0.7,
      fins=[[(0, c(70, 66, 58)), (1, c(150, 140, 120))], [(0, c(70, 66, 58)), (1, c(140, 132, 114))]]),
 dict(RA, name="Piranha", L=1.7, R=0.6, H=1.2, w=0.55, prof="deep", colors=(c(84, 96, 108), c(168, 174, 184), c(214, 48, 36)),
      speckle=(c(226, 230, 236), 9, 0.78, -0.3), jaw=(0.02, 0.17, 22, 9, 9, 0.07 * 1.7), jaw_c=c(214, 60, 44), mouth=0,
      iris=c(230, 40, 30), dorsal=[(0.42, 0.58, 0.42, "round"), (0.78, 0.82, 0.1, "round")], anal=(0.58, 0.8, 0.32, "long"),
      tail=("fork", 0.7, 40), pelv=0.25,
      fins=[[(0, c(90, 96, 104)), (1, c(200, 60, 40))], [(0, c(60, 64, 70)), (0.75, c(90, 96, 104)), (0.8, c(20, 20, 24)), (1, c(20, 20, 24))]]),
 dict(RA, name="ElectricEel", anims="eel", L=4.4, R=0.24, H=1.1, w=0.8, prof="eel", colors=(c(36, 40, 36), c(64, 68, 56), c(224, 120, 50)),
      noise=0.15, scale_k=0.0, mouth=0, jaw=(0.02, 0.12, 20, 9, 7, 0.1), eye=0.1, hook=lightning_hook, glow=c(120, 230, 255), glow_eyes=True,
      anal=(0.22, 0.98, 0.22, "long"), tail=(None, 0, 0), pelv=0, pect=0.3, wiggle=(0.35, 1.0), bend=0.0,
      fins=[[(0, c(50, 54, 46)), (1, c(120, 110, 80))], [(0, c(50, 54, 46)), (1, c(120, 110, 80))]]),
 dict(RA, name="Lionfish", L=1.7, R=0.45, H=1.25, w=0.6, prof="round", colors=(c(150, 46, 36), c(190, 70, 50), c(240, 220, 210)),
      bars=(9, c(250, 240, 230), 0.9, 0.12, 0.92), hook=lion_hook, iris=c(220, 50, 40), mouth=0.06,
      strips=[(c(160, 40, 30), c(250, 240, 230), 1.0)] * 2, dorsal=[(0.62, 0.8, 0.36, "round")], anal=(0.62, 0.8, 0.32, "round"),
      pect=0.95, pelv=0.4, tail=("round", 0.55, 45),
      fins=[[(0, c(170, 40, 30)), (0.18, c(250, 240, 230)), (0.34, c(170, 40, 30)), (0.5, c(250, 240, 230)), (0.66, c(170, 40, 30)), (0.82, c(250, 240, 230)), (1, c(170, 40, 30))]] * 2),
 dict(RA, name="MorayEel", anims="eel", L=3.6, R=0.3, H=1.2, w=0.7, prof="eel", colors=(c(150, 150, 50), c(170, 170, 70), c(196, 196, 110)),
      speckle=(c(30, 28, 20), 5, 0.66, -1.2), scale_k=0.0, jaw=(0.02, 0.14, 26, 13, 11, 0.05 * 3.6), mouth=0, eye=0.05 * 3.6 * 0.6,
      iris=SLIT_IRIS, dorsal=[(0.12, 0.97, 0.2, "long")], anal=(0.4, 0.97, 0.15, "long"), tail=(None, 0, 0), pect=0, pelv=0,
      wiggle=(0.3, 1.1), bend=0.0, fins=[[(0, c(150, 150, 50)), (1, c(110, 110, 40))]] * 2),
 dict(RA, name="Icefish", L=2.4, R=0.36, H=1.0, w=0.86, wt=0.35, prof="pike", colors=(c(186, 208, 224), c(218, 232, 242), c(240, 246, 250)),
      bars=(12, c(160, 186, 206), 0.45, 0.2, 0.9), jaw=(0.02, 0.2, 18, 15, 13), mouth=0, iris=c(120, 210, 255), glow_eyes=True,
      glow=c(140, 230, 255), hook=icy_hook, brow_c=c(150, 190, 220), dorsal=[(0.5, 0.82, 0.24, "long")], anal=(0.5, 0.86, 0.22, "long"),
      tail=("fork", 0.6, 36), pect=0.7,
      fins=[[(0, c(200, 220, 236)), (0.8, c(236, 244, 252)), (1, c(120, 190, 240))]] * 2),
 dict(RA, name="Lanternfish", L=1.5, R=0.3, H=1.1, w=0.7, colors=(c(18, 22, 40), c(56, 66, 90), c(196, 204, 218)),
      jaw=(0.02, 0.15, 20, 11, 9, 0.035 * 1.5), mouth=0, eye=0.12, glow=c(120, 210, 255), glow_eyes=True, iris=c(120, 210, 255),
      dots=[(-0.55, 0.2, 0.86, 9, 0.035), (-0.95, 0.16, 0.8, 8, 0.03), (0.1, 0.3, 0.8, 5, 0.028)],
      dorsal=[(0.42, 0.56, 0.3, "round"), (0.78, 0.82, 0.08, "round")], anal=(0.6, 0.8, 0.22, "round"), tail=("fork", 0.6, 40),
      fins=[[(0, c(30, 36, 60)), (1, c(90, 110, 150))]] * 2),
]

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for sp in FISH:
        if not want or sp["name"] in want: build(sp)
