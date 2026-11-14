"""All Epic fish. Run: python epics.py [FishName ...] [--no-render]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishgen import *

EP = dict(rarity="Epic", brow=True, pupil=(0.3, 0.22, 0.62), eye_k=0.045)
PROF["gar"] = [0, .12, .22, .40, .75, 1.0, .98, .88, .62, .40, .26]
PROF["shark"] = [0, .28, .48, .68, .87, 1.0, .95, .76, .48, .28, .18]
PROF["blob"] = [0, .62, .82, .94, 1.0, 1.0, .9, .7, .45, .3, .22]
SHARK_TAIL = ("shark", None, (-40, 62))
def shark_tail(Lt): return ("shark", Lt, (-40, 62))

def eye_pair(f, pts, re, iris_glow=False):
    for k, (C, n) in enumerate(pts):
        Bm = basis(n)
        f.sphere(f"Eye{k}", C, Bm, (re,) * 3, SW["iris"], glow=iris_glow)
        f.sphere(f"Pupil{k}", C + n * re * 0.8, Bm, (re * 0.3, re * 0.22, re * 0.62), SW["pupil"], 10, 6)

def manta_hook(f, sp):
    for sd in (1, -1):
        f.fin(f"Wing{sd}", lambda s, sd=sd: side(f.surf(lerp(0.12, 0.62, s), 0.0, 0.92), sd),
              lambda s, sd=sd: V(lerp(0.15, -0.9, s), sd * lerp(1, 0.45, s), 0),
              lambda s: 0.25 + 2.3 * min(s / 0.3, (1 - s) / 0.7) ** 1.1,
              lambda s, r: V(-0.2 * r ** 3 * (1 - s), 0, -0.1 * r * r + 0.12 * r ** 4), 20, 10, 0.05, 0)
        f.fin(f"Horn{sd}", lambda s, sd=sd: side(f.surf(0.03, lerp(-0.3, 0.3, s), 0.9), sd) + V(0, sd * 0.25, 0),
              lambda s, sd=sd: V(1, sd * 0.25, -0.15), lambda s: 0.55 * (0.6 + 0.4 * math.sin(math.pi * s)),
              lambda s, r: V(0, -sd * 0.25 * r ** 2, 0.15 * r * r), 8, 6, 0.05, 0)
    e = f.axis(1)
    f.tube("Whip", [e + V(0.1, 0, 0), e + V(-0.6, 0.05, 0.02), e + V(-1.4, 0.15, -0.05), e + V(-2.0, 0.1, 0.05)], 0.06, 0.008, sw=SW["x1"], K=6)
def hammer_hook(f, sp):
    hc = f.surf(0.035, 0.0, 0.0) + V(0, 0, 0.04)
    f.sphere("Hammer", hc, basis(V(1, 0, 0)), (0.2, 0.95, 0.11), SW["x1"], 20, 10)
    eye_pair(f, [(hc + V(0.02, sd * 0.93, 0.0), V(0.3, sd, 0.15).normalized()) for sd in (1, -1)], 0.085)
def greenland_hook(f, sp):
    eye_pair(f, [(side(f.surf(0.12, 0.3, 0.97), sd), side(V(0.3, 1, 0.25).normalized(), sd)) for sd in (1, -1)], 0.08, True)
def angler_hook(f, sp):
    b = f.surf(0.08, math.pi / 2, 0.95)
    f.tube("Illicium", [b, b + V(-0.05, 0, 0.45), b + V(0.35, 0, 0.75), b + V(0.75, 0, 0.6), b + V(0.85, 0, 0.42)], 0.04, 0.02, sw=SW["x1"], K=6)
    f.extra_bones.append(dict(name="Lure", head=b, tail=b + V(0.86, 0, 0.32), parent="Head", match=lambda n, cen: n in ("Illicium", "Lure")))
    f.sphere("Lure", b + V(0.86, 0, 0.32), basis(V(1, 0, 0)), (0.13, 0.13, 0.15), SW["glow"], 14, 10, glow=True)
def blob_hook(f, sp):
    f.sphere("Nose", f.axis(0.04) + V(0.05, 0, -0.08), basis(V(1, 0, 0)), (0.18, 0.2, 0.26), SW["x1"], 16, 10)
    for sd in (1, -1):                                       # droopy frown corners
        p = side(f.surf(0.06, -0.85, 1.0), sd)
        f.tube(f"Frown{sd}", [p + V(0.03, -sd * 0.1, 0.02), p, p + V(-0.06, sd * 0.02, -0.08)], 0.025, 0.02, sw=SW["maw"], K=6)
def arapaima_extra(T, Vv, top, X, Y, col):
    m = smooth(0.45, 0.75, T + 0.1 * (vnoise(X, Y, 3, 41) - 0.5)) * smooth(0.6, -0.2, top)
    return col * (1 - m[..., None]) + c(190, 40, 30) * m[..., None]
def greenland_extra(T, Vv, top, X, Y, col):
    sc = 0
    for k, (a, b, w) in enumerate(((0.3, 0.2, 2.5), (0.5, -0.1, -3.0), (0.65, 0.35, 1.8), (0.42, 0.5, -2.2))):
        sc += np.exp(-((top - b - w * (T - a)) / 0.025) ** 2) * (np.abs(T - a) < 0.06)
    sc = np.clip(sc, 0, 1); return col * (1 - 0.7 * sc[..., None]) + c(196, 196, 200) * 0.7 * sc[..., None]

SHARK_FINS = [[(0, c(70, 76, 86)), (0.85, c(120, 126, 136)), (1, c(40, 44, 52))]] * 2
FISH = [
 dict(EP, name="AlligatorGar", L=3.8, R=0.38, H=1.0, w=0.85, prof="gar", colors=(c(70, 72, 50), c(120, 120, 80), c(226, 220, 190)),
      scale=0.2, scale_k=0.7, speckle=(c(40, 40, 30), 6, 0.78, -0.5), jaw=(0.01, 0.2, 14, 19, 17, 0.07), mouth=0, eye_t=0.22,
      iris=c(230, 160, 40), dorsal=[(0.78, 0.86, 0.36, "round")], anal=(0.76, 0.86, 0.32, "round"), tail=("round", 0.9, 40),
      fins=[[(0, c(90, 80, 50)), (0.6, c(160, 120, 70)), (1, c(200, 150, 90))]] * 2),
 dict(EP, name="Arapaima", L=4.0, R=0.55, H=1.0, w=0.8, prof="blunt", colors=(c(50, 64, 56), c(100, 110, 96), c(200, 196, 180)),
      extra=arapaima_extra, scale=0.24, scale_k=0.6, mouth=0.07, eye_t=0.1, iris=c(220, 200, 120),
      dorsal=[(0.66, 0.86, 0.4, "long")], anal=(0.66, 0.86, 0.36, "long"), tail=("round", 0.9, 40), pect=0.8,
      fins=[[(0, c(60, 64, 56)), (0.6, c(150, 50, 40)), (1, c(200, 60, 40))]] * 2),
 dict(EP, name="MantaRay", anims="ray", L=2.6, R=0.5, H=0.42, w=1.25, wt=0.9, prof="blunt", belly=0.8,
      colors=(c(22, 24, 34), c(40, 44, 58), c(236, 236, 240)), speckle=(c(40, 40, 50), 5, 0.75, -1.2), scale_k=0.0,
      hook=manta_hook, x1=c(30, 32, 44), mouth=0.12, eye_th=0.15, eye_t=0.06, eye=0.08, pect=0, pelv=0, tail=(None, 0, 0),
      dorsal=[(0.7, 0.78, 0.2, "tri")], bend=0.0, cam=0.8,
      fins=[[(0, c(24, 26, 36)), (0.94, c(46, 50, 66)), (1, c(200, 204, 216))]] * 2),
 dict(EP, name="HammerheadShark", L=4.6, R=0.55, H=0.95, w=0.95, wt=0.5, prof="shark", belly=0.75,
      colors=(c(90, 100, 112), c(130, 140, 150), c(236, 236, 240)), scale_k=0.0, eyes=False, hook=hammer_hook, x1=c(96, 106, 118),
      jaw=(0.06, 0.17, 18, 13, 11, 0.07), mouth=0, dorsal=[(0.3, 0.44, 1.5, "tri"), (0.76, 0.81, 0.3, "tri")],
      anal=(0.74, 0.8, 0.28, "tri"), tail=shark_tail(2.0), pect=1.2, pelv=0.3, fins=SHARK_FINS),
 dict(EP, name="GreenlandShark", L=4.4, R=0.66, H=0.95, w=0.95, wt=0.4, prof="shark", belly=0.8,
      colors=(c(64, 66, 64), c(96, 98, 94), c(150, 150, 146)), noise=0.3, scale_k=0.0, extra=greenland_extra, eyes=False,
      hook=greenland_hook, glow=c(200, 255, 220), iris=c(200, 255, 220), jaw=(0.04, 0.16, 14, 13, 11, 0.06), mouth=0,
      dorsal=[(0.42, 0.5, 0.4, "tri"), (0.62, 0.68, 0.3, "tri")], tail=shark_tail(1.4), pect=0.8, pelv=0.3,
      fins=[[(0, c(60, 62, 60)), (1, c(110, 110, 106))]] * 2),
 dict(EP, name="Anglerfish", anims="angler", L=1.9, R=0.8, H=0.95, w=0.9, prof="blunt", colors=(c(40, 30, 34), c(66, 50, 52), c(90, 70, 70)),
      noise=0.35, scale_k=0.0, jaw=(0.0, 0.22, 34, 15, 13, 0.16), mouth=0, hook=angler_hook, x1=c(70, 54, 56), glow=c(180, 255, 200),
      eye_t=0.2, eye_th=0.6, iris=c(180, 255, 200), glow_eyes=True, dorsal=[(0.6, 0.78, 0.3, "round")], anal=(0.66, 0.8, 0.26, "round"),
      tail=("round", 0.6, 40), pect=0.4, pelv=0, fins=[[(0, c(50, 38, 40)), (1, c(110, 90, 90))]] * 2),
 dict(name="Blobfish", rarity="Epic", L=1.5, R=0.62, H=0.9, w=1.0, wt=0.5, prof="blob", belly=1.05, colors=(c(236, 170, 170), c(240, 184, 182), c(246, 206, 200)),
      noise=0.15, scale_k=0.0, hook=blob_hook, x1=c(232, 150, 156), mouth=0, eye=0.07, eye_t=0.14, eye_th=0.45, iris=c(30, 26, 30),
      dorsal=[], tail=("round", 0.4, 35), pect=0.3, pelv=0, bend=0.0,
      fins=[[(0, c(236, 170, 170)), (1, c(250, 214, 210))]] * 2),
]

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for sp in FISH:
        if not want or sp["name"] in want: build(sp)
