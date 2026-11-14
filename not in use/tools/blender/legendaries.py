"""All Legendary fish. Run: python legendaries.py [FishName ...] [--no-render]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishgen import *

LG = dict(rarity="Legendary", brow=True, pupil=(0.3, 0.22, 0.62), eye_k=0.04)
PROF["shark"] = [0, .28, .48, .68, .87, 1.0, .95, .76, .48, .28, .18]
def shark_tail(Lt): return ("shark", Lt, (-40, 62))

def cracks(f, n, seed, r=0.03, t0=0.12, t1=0.92, step=0.035, name="Crack"):
    rng = np.random.default_rng(seed)
    for k in range(n):
        t = float(rng.uniform(t0, t1 - 0.15)); th = float(rng.uniform(-1.2, 1.4)); sd = 1 if k % 2 == 0 else -1; pts = []
        for i in range(int(rng.integers(4, 8))):
            pts.append(side(f.surf(min(t, 0.97), th, 1.005), sd)); t += step * float(rng.uniform(0.6, 1.3)); th += float(rng.uniform(-0.45, 0.45))
        glow_line(f, f"{name}{k}", pts, r, r * 0.5)

def gills(f, t0, n, sw, glow=False):
    for sd in (1, -1):
        for i in range(n):
            pts = [side(f.surf(t0 + i * 0.02 + 0.01 * (1 - abs(u)), u, 1.0), sd) for u in np.linspace(-0.5, 0.4, 5)]
            f.tube(f"Gill{sd}_{i}", pts, 0.022, 0.018, K=6, sub=3, sw=sw, glow=glow)

def gw_hook(f, sp): gills(f, 0.2, 5, SW["x1"])
def sail_hook(f, sp):
    tip = f.axis(0)
    f.tube("Bill", [tip + V(-0.05, 0, 0), tip + V(0.5, 0, 0.0), tip + V(1.2, 0, 0.03)], 0.07, 0.008, sw=SW["x1"], K=8)
def crystal_hook(f, sp):
    rng = np.random.default_rng(5)
    for i in range(22):
        t = float(rng.uniform(0.15, 0.85)); th = float(rng.uniform(-0.3, math.pi - 0.3)); sd = 1 if i % 2 else -1
        if th > 1.4: sd = 1
        p = side(f.surf(t, th, 0.98), sd); n = side((f.surf(t, th) - f.axis(t)).normalized(), sd)
        n = (n + V(-0.5, 0, 0)).normalized(); s_ = float(rng.uniform(0.6, 1.2))
        f.gem(f"Crystal{i}", p + n * 0.08 * s_, basis(n, V(0, 0, 1)), (0.22 * s_, 0.06 * s_, 0.07 * s_), SW["x1"])
    cracks(f, 9, 3, 0.022)
def oar_hook(f, sp):
    b = f.surf(0.06, math.pi / 2, 0.9)
    for i in range(6):
        a = 0.25 + i * 0.12; ln = 0.9 + 0.3 * math.sin(i * 1.3)
        f.tube(f"Plume{i}", [b + V(-i * 0.04, 0, 0), b + V(-0.1 - i * 0.05, 0, ln * 0.5), b + V(-0.35 - a, 0, ln)], 0.035, 0.012, sw=SW["x1"], K=6)
def magma_hook(f, sp):
    cracks(f, 16, 11, 0.035, 0.1, 0.95, 0.04)
    for i, t in enumerate(np.linspace(0.12, 0.8, 9)):
        p = f.surf(float(t), math.pi / 2, 0.97)
        f.gem(f"Rock{i}", p + V(0, 0, 0.06), basis(V(-0.4, 0, 1), V(1, 0, 0)), (0.12, 0.09, 0.16 - 0.08 * float(t)), SW["x1"])
def coel_hook(f, sp):
    for nm, (t, th) in {"PecLobe": (0.24, -0.5), "PelvLobe": (0.45, -1.2), "AnalLobe": (0.72, -math.pi / 2), "D2Lobe": (0.68, math.pi / 2)}.items():
        for sd in ((1, -1) if abs(th) < 1.5 else (1,)):
            p = side(f.surf(t, th, 0.9), sd); n = side((f.surf(t, th) - f.axis(t)).normalized(), sd)
            f.tube(f"{nm}{sd}", [p, p + n * 0.15 + V(-0.08, 0, 0), p + n * 0.28 + V(-0.2, 0, 0)], 0.1, 0.06, sw=SW["x1"], K=8)

def coel_extra(T, Vv, top, X, Y, col):
    m = smooth(0.8, 0.83, vnoise(X, Y, 3.5, 51)) * smooth(0.12, 0.2, T); return col * (1 - m[..., None]) + c(236, 236, 230) * m[..., None]
def gw_extra(T, Vv, top, X, Y, col):
    m = smooth(-0.03, 0.03, top + 0.15 - 0.18 * np.sin(T * 18) * 0.3 - 0.1 * vnoise(X, Y, 4, 61))
    return c(240, 240, 244) * (1 - m[..., None]) + col * m[..., None]
def magma_extra(T, Vv, top, X, Y, col):
    n = vnoise(X, Y, 4, 71) * 0.6 + vnoise(X, Y, 9, 72) * 0.4
    return c(40, 34, 34)[None, None, :] * (0.7 + 0.6 * n)[..., None]
def sail_extra(T, Vv, top, X, Y, col):
    b = smooth(0.6, 0.85, 0.5 + 0.5 * np.cos(2 * np.pi * 9 * T)) * smooth(-0.2, 0.3, top) * smooth(0.18, 0.25, T) * (1 - smooth(0.85, 0.9, T))
    return col * (1 - 0.6 * b[..., None]) + c(120, 200, 255) * 0.6 * b[..., None]

FISH = [
 dict(LG, name="GreatWhiteShark", L=5.2, R=0.78, H=0.98, w=0.95, wt=0.5, prof="shark", belly=0.78,
      colors=(c(70, 80, 92), c(110, 118, 128), c(240, 240, 244)), extra=gw_extra, noise=0.12, scale_k=0.0, hook=gw_hook, x1=c(50, 56, 64),
      jaw=(0.03, 0.17, 26, 15, 13, 0.11), mouth=0, iris=c(20, 20, 24), pupil=(0.3, 0.58, 0.58), eye_t=0.14,
      dorsal=[(0.32, 0.46, 1.6, "tri"), (0.76, 0.8, 0.3, "tri")], anal=(0.74, 0.79, 0.28, "tri"), tail=shark_tail(2.2),
      pect=1.5, pelv=0.4, fins=[[(0, c(70, 80, 92)), (0.9, c(100, 108, 120)), (1, c(30, 34, 40))]] * 2),
 dict(LG, name="Sailfish", L=4.2, R=0.42, H=1.1, w=0.62, prof="pike", colors=(c(20, 40, 110), c(60, 110, 180), c(232, 236, 244)),
      extra=sail_extra, hook=sail_hook, x1=c(24, 40, 90), mouth=0.04, eye_t=0.06,
      dorsal=[(0.12, 0.62, 1.9, "sail", 0), (0.86, 0.9, 0.12, "round")], anal=(0.6, 0.7, 0.3, "tri"), tail=("fork", 1.6, 52),
      pect=0.6, pelv=0.8, fins=[[(0, c(20, 40, 120)), (0.5, c(40, 80, 190)), (1, c(70, 140, 230))], [(0, c(20, 40, 110)), (1, c(60, 110, 200))]]),
 dict(LG, name="CrystalPike", L=3.6, R=0.36, H=1.0, w=0.88, wt=0.3, prof="pike", colors=(c(120, 170, 210), c(170, 210, 236), c(230, 244, 252)),
      speckle=(c(240, 250, 255), 7, 0.76, -0.6), hook=crystal_hook, x1=c(190, 230, 255), glow=c(90, 230, 255), glow_eyes=True,
      iris=c(90, 230, 255), jaw=(0.02, 0.2, 20, 15, 13), mouth=0, brow_c=c(220, 244, 255), eye_t=0.15,
      dorsal=[(0.7, 0.82, 0.45, "tri")], anal=(0.72, 0.82, 0.38, "tri"), tail=("fork", 1.0, 42),
      fins=[[(0, c(150, 200, 236)), (0.7, c(220, 244, 255)), (1, c(90, 230, 255))]] * 2),
 dict(LG, name="Oarfish", anims="eel", L=7.0, R=0.26, H=1.35, w=0.35, prof="eel", colors=(c(150, 156, 170), c(206, 210, 220), c(236, 238, 244)),
      stripe=(c(80, 86, 110), 0.06, 0.4), speckle=(c(70, 76, 96), 6, 0.78, -0.4), scale_k=0.0, hook=oar_hook, x1=c(220, 40, 50),
      mouth=0.06, eye=0.12, dorsal=[(0.08, 0.99, 0.32, "long", 0)], tail=(None, 0, 0), pect=0.2, pelv=0, wiggle=(0.6, 1.4), bend=0.0, cam=1.15,
      fins=[[(0, c(220, 40, 50)), (1, c(255, 120, 110))]] * 2),
 dict(LG, name="MagmaEel", anims="eel", L=5.0, R=0.34, H=1.1, w=0.85, prof="eel", colors=(c(40, 34, 34),) * 3, extra=magma_extra, scale_k=0.0,
      hook=magma_hook, x1=c(30, 26, 26), glow=c(255, 120, 30), glow_eyes=True, iris=c(255, 120, 30), brow_c=c(30, 26, 26),
      jaw=(0.02, 0.13, 24, 13, 11, 0.09), mouth=0, eye=0.13, dorsal=[(0.15, 0.97, 0.18, "spiny", 0, 24)], anal=(0.45, 0.97, 0.14, "long"),
      tail=(None, 0, 0), pect=0.4, pelv=0, wiggle=(0.45, 1.1), bend=0.0, cam=0.9,
      fins=[[(0, c(36, 30, 30)), (0.7, c(120, 40, 20)), (1, c(255, 120, 30))]] * 2),
 dict(LG, name="Coelacanth", L=3.6, R=0.62, H=1.0, w=0.75, prof="blunt", colors=(c(40, 60, 96), c(64, 88, 128), c(110, 130, 160)),
      extra=coel_extra, scale=0.22, scale_k=0.5, hook=coel_hook, x1=c(56, 78, 116), mouth=0.08, iris=c(140, 230, 200),
      dorsal=[(0.3, 0.38, 0.6, "tri"), (0.66, 0.7, 0.4, "round")], anal=(0.7, 0.74, 0.35, "round"), tail=("round", 1.0, 50),
      pect=0.55, pelv=0.4, fins=[[(0, c(56, 78, 116)), (1, c(110, 140, 180))]] * 2),
]

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for sp in FISH:
        if not want or sp["name"] in want: build(sp)
