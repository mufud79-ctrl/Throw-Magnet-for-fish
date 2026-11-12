"""All Uncommon fish. Run: python uncommons.py [FishName ...] [--no-render]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishgen import *
from fishkit import pchip

U = dict(rarity="Uncommon")

def koi_extra(T, Vv, top, X, Y, col):
    f = 0.6 * vnoise(X, Y, 1.5, 21) + 0.4 * vnoise(X, Y, 3.0, 22) + 0.35 * top - 0.62
    f = np.maximum(f, 0.3 - np.hypot((T - 0.07) * 6, top - 0.9))
    m = smooth(-0.015, 0.015, f) * smooth(0.02, 0.05, T); return col * (1 - m[..., None]) + c(222, 52, 34) * m[..., None]
def salmon_extra(T, Vv, top, X, Y, col):
    m = smooth(0.22, 0.17, T); return col * (1 - m[..., None]) + c(70, 104, 60) * m[..., None]
def flounder_extra(T, Vv, top, X, Y, col):
    ys = np.cos(2 * np.pi * (Vv - 0.25))              # +1 on the eyed (upper) side
    mott = c(150, 120, 80) * (0.8 + 0.4 * vnoise(X, Y, 3, 31))[..., None]
    sp_ = smooth(0.7, 0.73, vnoise(X, Y, 6, 32)); mott = mott * (1 - 0.5 * sp_)[..., None]
    ring = smooth(0.74, 0.77, vnoise(X, Y, 4, 33)) * (1 - smooth(0.8, 0.83, vnoise(X, Y, 4, 33)))
    mott = mott * (1 - ring[..., None]) + c(230, 140, 60) * ring[..., None]
    m = smooth(-0.15, 0.1, ys); return c(244, 240, 232) * (1 - m[..., None]) + mott * m[..., None]

def spikes_hook(f, sp):
    for i, t in enumerate(np.linspace(0.14, 0.86, 7)):
        for j in range(10):
            th = 2 * math.pi * (j + 0.5 * (i % 2)) / 10
            p = f.surf(float(t), th); n = (p - f.axis(float(t))).normalized()
            f.tube(f"Spike{i}_{j}", [p - n * 0.02, p + n * 0.07 + V(-0.03, 0, 0), p + n * 0.14 + V(-0.06, 0, 0)], 0.03, 0.003,
                   K=5, sub=2, sw=SW["barbel"])
def kype_hook(f, sp):
    b = f.surf(0.03, -math.pi / 2, 0.95); f.jaw_hinge = b + V(-0.15, 0, 0.02)
    f.tube("Kype", [b + V(-0.15, 0, 0.02), b + V(0.1, 0, -0.06), b + V(0.22, 0, 0.04), b + V(0.24, 0, 0.12)], 0.07, 0.03, sw=SW["lip"])
def arms_hook(f, sp):
    for sd in (1, -1):
        f.fin(f"Arm_{sd}", lambda s, sd=sd: side(f.surf(lerp(0.17, 0.23, s), -0.9, 0.9), sd),
              lambda s, sd=sd: V(lerp(0.3, -0.2, s), sd * 0.45, -1), lambda s: 0.36 * (0.6 + 0.4 * math.sin(math.pi * s)),
              lambda s, r: V(0.06 * r * r, 0, 0), 8, 5, 0.03, 0)
def streamers_hook(f, sp):
    for sd in (1, -1):
        b = side(f.surf(0.3, -1.3, 0.9), sd)
        f.tube(f"Streamer_{sd}", [b, b + V(-0.1, sd * 0.05, -0.4), b + V(-0.3, sd * 0.08, -0.85), b + V(-0.45, sd * 0.06, -1.1)],
               0.03, 0.005, sw=SW["barbel"], K=6)
def flounder_hook(f, sp):
    for k, (t, th) in enumerate([(0.13, 0.25), (0.19, 0.62)]):
        S = f.surf(t, th); n = (S - f.axis(t)).normalized(); Bm = basis(n, V(1, 0, 0)); re = 0.1
        C = S - n * 0.03
        f.sphere(f"Eye{k}", C, Bm, (re, re, re), SW["iris"])
        f.sphere(f"Pupil{k}", C + n * (re * 0.8), Bm, (re * 0.3, re * 0.58, re * 0.58), SW["pupil"], 12, 8)
        f.sphere(f"Glint{k}", C + (n + Bm.col[2] * 0.5).normalized() * re, Bm, (re * 0.22,) * 3, SW["white"], 8, 6)

FISH = [
 dict(U, name="Koi", L=2.2, R=0.5, H=1.05, prof="round", hump=0.1, colors=(c(250, 246, 238), c(250, 246, 238), c(253, 250, 244)),
      extra=koi_extra, scale=0.13, scale_k=0.4, barbels=[(0.03, -0.5, 0.15, 0.6)], dorsal=[(0.3, 0.62, 0.34, "long")],
      anal=(0.68, 0.76, 0.24, "round"), tail=("fork", 0.85, 42), iris=c(40, 34, 30), lip=c(232, 150, 140),
      fins=[[(0, c(250, 240, 230)), (1, c(255, 252, 248))], [(0, c(240, 120, 90)), (0.6, c(250, 236, 226)), (1, c(255, 252, 248))]]),
 dict(U, name="LargemouthBass", L=2.4, R=0.55, H=1.05, w=0.7, colors=(c(60, 90, 40), c(140, 160, 80), c(236, 232, 200)),
      stripe=(c(36, 52, 28), 0.16, 0.05), noise=0.2, mouth=0.12, eye_t=0.14,
      dorsal=[(0.25, 0.45, 0.38, "spiny", 0, 7), (0.5, 0.68, 0.36, "round")], anal=(0.66, 0.78, 0.28, "round"),
      tail=("fork", 0.8, 38), iris=c(200, 90, 30), fins=[[(0, c(90, 110, 60)), (1, c(170, 180, 130))], [(0, c(80, 100, 50)), (1, c(160, 170, 120))]]),
 dict(U, name="RainbowTrout", L=2.4, R=0.42, H=1.1, w=0.7, colors=(c(70, 92, 62), c(196, 196, 176), c(242, 238, 232)),
      stripe=(c(232, 110, 130), 0.15, 0.02), speckle=(c(30, 30, 30), 9, 0.78, -0.25),
      dorsal=[(0.4, 0.53, 0.32, "round"), (0.76, 0.8, 0.1, "round")], anal=(0.68, 0.76, 0.22, "round"), tail=("fork", 0.75, 36),
      fins=[[(0, c(150, 150, 120)), (1, c(220, 214, 190))], [(0, c(110, 120, 90)), (1, c(200, 196, 170))]]),
 dict(U, name="Salmon", L=2.7, R=0.5, H=1.15, w=0.7, hump=0.22, colors=(c(176, 30, 34), c(214, 50, 44), c(226, 90, 76)),
      extra=salmon_extra, hook=kype_hook, lip=c(70, 104, 60), dorsal=[(0.4, 0.52, 0.32, "round"), (0.76, 0.8, 0.1, "round")],
      anal=(0.68, 0.78, 0.24, "round"), tail=("fork", 0.85, 38), iris=c(220, 190, 80),
      fins=[[(0, c(70, 100, 60)), (1, c(150, 160, 120))], [(0, c(150, 40, 40)), (1, c(110, 120, 80))]]),
 dict(U, name="Mudskipper", L=1.7, R=0.26, H=1.0, w=0.85, prof="blunt", colors=(c(110, 95, 70), c(150, 130, 95), c(205, 195, 165)),
      speckle=(c(90, 170, 240), 7, 0.8, -0.3), eye=0.11, eye_t=0.07, eye_th=1.15, pect=0, pelv=0, hook=arms_hook,
      dorsal=[(0.3, 0.42, 0.5, "sail", 1), (0.55, 0.86, 0.2, "long")], anal=(0.55, 0.86, 0.14, "long"), tail=("round", 0.45, 40),
      fins=[[(0, c(130, 115, 85)), (1, c(190, 175, 140))], [(0, c(120, 100, 70)), (0.7, c(90, 160, 230)), (1, c(240, 120, 80))]]),
 dict(U, name="Pufferfish", L=1.3, R=0.62, H=1.0, w=0.95, prof="round", colors=(c(190, 170, 90), c(225, 205, 130), c(246, 242, 228)),
      speckle=(c(90, 66, 38), 5, 0.72, -0.2), eye=0.14, mouth=0.05, hook=spikes_hook, barbel_c=c(240, 232, 200), scale_k=0.0,
      dorsal=[(0.72, 0.82, 0.22, "round")], anal=(0.72, 0.82, 0.18, "round"), tail=("round", 0.38, 40), pect=0.3, pelv=0,
      fins=[[(0, c(200, 180, 100)), (1, c(240, 228, 180))], [(0, c(190, 170, 90)), (1, c(240, 228, 180))]]),
 dict(U, name="Angelfish", L=1.4, R=0.55, H=1.45, w=0.4, prof="round", colors=(c(170, 170, 160), c(222, 222, 212), c(240, 240, 234)),
      bars=(3, c(30, 30, 34), 0.85, 0.1, 0.9), hook=streamers_hook, pelv=0, cam=0.62, barbel_c=c(220, 220, 212),
      dorsal=[(0.25, 0.62, 1.3, "tri")], anal=(0.42, 0.72, 1.1, "tri"), tail=("fork", 0.5, 40),
      fins=[[(0, c(60, 60, 64)), (0.5, c(200, 200, 196)), (1, c(240, 240, 236))], [(0, c(190, 190, 184)), (1, c(240, 240, 236))]]),
 dict(U, name="Flounder", L=2.0, R=0.8, H=1.0, w=0.22, wt=0.0, prof="round", colors=(c(150, 120, 80),) * 3, extra=flounder_extra,
      eyes=False, hook=flounder_hook, roll=math.pi / 2, bend=0.0, scale_k=0.0, pelv=0, pect=0.3, iris=c(220, 190, 90),
      dorsal=[(0.1, 0.92, 0.22, "long")], anal=(0.28, 0.92, 0.2, "long"), tail=("round", 0.5, 45),
      fins=[[(0, c(140, 110, 72)), (1, c(200, 176, 130))], [(0, c(140, 110, 72)), (1, c(200, 176, 130))]]),
]

def build_seahorse():
    f = Fish("Seahorse", "Uncommon", L=1.0, R=0.3, H=1.0, PT=PT, PR=PROF["round"], fin_styles=2); f.rig_vertical = True
    body_sw, dark = 6, 7
    trunk = [V(-0.12, 0, 1.0), V(-0.16, 0, 0.82), V(-0.02, 0, 0.55), V(0.02, 0, 0.25), V(-0.06, 0, -0.05),
             V(-0.02, 0, -0.35), V(0.14, 0, -0.55), V(0.3, 0, -0.5), V(0.32, 0, -0.36), V(0.22, 0, -0.3)]
    base = lambda s: float(pchip([0, .1, .3, .5, .7, .85, 1], [.14, .16, .25, .19, .1, .06, .02], s))
    f.tube("Trunk", trunk, 0, 0, strip=0, K=12, sub=8, rfn=lambda s: base(s) * (1 + 0.1 * max(0.0, math.sin(s * 95))))
    f.sphere("Head", V(-0.04, 0, 1.12), basis(V(1, 0, 0.3)), (0.2, 0.15, 0.16), body_sw, 16, 10)
    f.tube("Snout", [V(0.1, 0, 1.12), V(0.3, 0, 1.06), V(0.46, 0, 1.0)], 0.075, 0.05, sw=body_sw)
    f.sphere("Mouth", V(0.47, 0, 1.0), basis(V(1, 0, -0.2)), (0.02, 0.045, 0.04), dark, 8, 6)
    for i, dx in enumerate((-0.14, -0.05, 0.04)):
        p = V(dx, 0, 1.24)
        f.tube(f"Crown{i}", [p, p + V(-0.02, 0, 0.08), p + V(-0.05, 0, 0.15)], 0.035, 0.005, sw=body_sw, K=6, sub=3)
    for sd in (1, -1):
        n = V(0.45, sd, 0.15).normalized(); C = V(0.0, sd * 0.11, 1.15); Bm = basis(n); re = 0.075
        f.sphere(f"Eye{sd}", C, Bm, (re,) * 3, 0)
        f.sphere(f"Pupil{sd}", C + n * re * 0.8, Bm, (re * 0.3, re * 0.58, re * 0.58), 1, 10, 6)
        f.sphere(f"Glint{sd}", C + (n + Bm.col[2] * 0.5).normalized() * re, Bm, (re * 0.22,) * 3, 2, 6, 4)
        f.fin(f"Pect{sd}", lambda s, sd=sd: V(-0.1, sd * 0.1, lerp(0.98, 0.9, s)), lambda s, sd=sd: V(-0.4, sd * 1, 0),
              lambda s: 0.16 * math.sin(math.pi * s) ** 0.5, lambda s, r: V(0, 0, 0), 6, 4, 0.02, 0)
    f.fin("Dorsal", lambda s: V(lerp(-0.2, -0.18, s), 0, lerp(0.55, 0.15, s)), lambda s: V(-1, 0, 0.15),
          lambda s: 0.24 * math.sin(math.pi * s) ** 0.5, lambda s, r: V(0, 0.02 * r * math.sin(10 * s), 0), 12, 5, 0.02, 1)
    f.texture(lambda T, Vv, top: np.zeros(T.shape + (3,)) + c(250, 170, 40),
              fin_stops=[[(0, c(250, 170, 40)), (1, c(255, 230, 160))], [(0, c(250, 160, 40)), (0.7, c(255, 220, 140)), (1, c(255, 248, 230))]],
              strips=[(c(240, 150, 30), c(255, 196, 60), 1.0)] * 2,
              swatches={0: c(40, 30, 20), 1: c(14, 12, 16), 2: c(255, 255, 255), body_sw: c(244, 156, 34), dark: c(60, 30, 20)})
    f.finish(bend=0.0, cam_scale=0.42, views={"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50), "side": ((12.5, 0, 0.6), (0, 0, 0.2), 50)})

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for sp in FISH:
        if not want or sp["name"] in want: build(sp)
    if not want or "Seahorse" in want: build_seahorse()
