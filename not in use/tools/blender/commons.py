"""All Common fish. Run: python commons.py [FishName ...] [--no-render]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishgen import *

def tang_extra(T, Vv, top, X, Y, col):   # black "palette" sweep
    m = smooth(0.03, -0.03, np.abs(top - 0.35 - 0.5 * np.sin(T * 5.2 - 0.6)) - 0.18 * np.sin(np.pi * np.clip(T * 1.2, 0, 1))) * smooth(0.12, 0.2, T)
    m2 = smooth(0.06, 0.0, np.hypot((T - 0.35) * 2, top - 0.25) - 0.18)
    m = np.maximum(m, m2); return col * (1 - m[..., None]) + c(16, 18, 34) * m[..., None]

def goldfish_extra(T, Vv, top, X, Y, col):
    m = smooth(0.52, 0.6, vnoise(X, Y, 2.5, 7) + 0.25 * (1 - top)) * 0.7
    return col * (1 - m[..., None]) + c(255, 236, 200) * m[..., None]

FISH = [
 dict(name="Minnow", L=1.5, R=0.22, H=1.0, w=0.75, colors=(c(110, 120, 80), c(196, 200, 180), c(236, 236, 226)),
      stripe=(c(60, 60, 50), 0.12, 0.05), dorsal=[(0.4, 0.55, 0.28, "round")], anal=(0.62, 0.72, 0.18, "round"),
      tail=("fork", 0.6, 40), fins=[[(0, c(170, 170, 140)), (1, c(220, 220, 200))], [(0, c(150, 150, 120)), (1, c(214, 214, 190))]]),
 dict(name="Goldfish", L=1.3, R=0.48, H=1.05, prof="round", w=0.75, eye=0.13, colors=(c(242, 120, 20), c(250, 150, 30), c(255, 200, 90)),
      extra=goldfish_extra, dorsal=[(0.3, 0.6, 0.45, "sail")], anal=(0.68, 0.78, 0.28, "round"), tail=("veil", 1.1, 55),
      pect=0.35, pelv=0.3, iris=c(30, 30, 30),
      fins=[[(0, c(245, 120, 20)), (0.6, c(255, 170, 60)), (1, c(255, 230, 190))], [(0, c(240, 110, 20)), (0.5, c(255, 160, 50)), (1, c(255, 236, 200))]]),
 dict(name="Bluegill", L=1.7, R=0.5, H=1.35, w=0.55, prof="round", colors=(c(56, 90, 80), c(90, 130, 120), c(240, 170, 60)),
      bars=(6, c(40, 60, 60), 0.55, 0.2, 0.85), spot=(0.2, 0.12, 0.13, c(16, 20, 60)),
      dorsal=[(0.25, 0.75, 0.4, "spiny", 0, 10)], anal=(0.6, 0.82, 0.3, "round"), tail=("fork", 0.65, 42),
      fins=[[(0, c(70, 100, 90)), (1, c(150, 180, 170))], [(0, c(70, 100, 90)), (1, c(160, 186, 176))]]),
 dict(name="Guppy", L=1.0, R=0.2, H=1.05, w=0.7, colors=(c(150, 150, 140), c(196, 196, 190), c(230, 228, 220)),
      spot=(0.62, 0.25, 0.09, c(255, 120, 40)), dorsal=[(0.5, 0.68, 0.32, "sail", 1)], tail=("fan", 0.75, 58), eye=0.085,
      fins=[[(0, c(200, 200, 196)), (1, c(230, 230, 226))], [(0, c(255, 120, 30)), (0.45, c(255, 90, 160)), (0.8, c(70, 120, 255)), (1, c(130, 210, 255))]]),
 dict(name="Perch", L=2.0, R=0.42, H=1.15, colors=(c(80, 110, 50), c(190, 190, 70), c(240, 236, 200)),
      bars=(6, c(40, 60, 30), 0.65, 0.18, 0.85),
      dorsal=[(0.22, 0.45, 0.42, "spiny", 0, 7), (0.5, 0.66, 0.34, "round")], anal=(0.66, 0.76, 0.26, "round"),
      tail=("fork", 0.7, 42), iris=c(230, 160, 40),
      fins=[[(0, c(120, 130, 70)), (1, c(200, 200, 140))], [(0, c(230, 120, 40)), (1, c(250, 170, 90))]]),
 dict(name="Carp", L=2.3, R=0.55, H=1.05, prof="round", hump=0.12, colors=(c(90, 80, 40), c(170, 140, 70), c(230, 210, 150)),
      scale=0.17, scale_k=0.55, dorsal=[(0.3, 0.62, 0.36, "long")], anal=(0.68, 0.76, 0.28, "round"), tail=("fork", 0.8, 40),
      barbels=[(0.03, -0.5, 0.18, 0.6)], iris=c(200, 160, 60),
      fins=[[(0, c(110, 90, 50)), (1, c(180, 150, 100))], [(0, c(110, 90, 50)), (1, c(190, 160, 100))]]),
 dict(name="Catfish", L=2.4, R=0.5, H=0.8, w=1.05, wt=0.5, prof="blunt", belly=0.7, eye=0.1, eye_th=0.55, eye_t=0.08,
      mouth=0.13, colors=(c(70, 70, 64), c(120, 116, 104), c(220, 216, 200)), noise=0.25, scale_k=0.0,
      dorsal=[(0.26, 0.34, 0.45, "tri"), (0.7, 0.78, 0.12, "round")], anal=(0.55, 0.85, 0.2, "long"), tail=("square", 0.7, 30),
      pect=0.45, barbels=[(0.02, -0.15, 0.9, 0.4), (0.03, -0.75, 0.4, 1.0), (0.06, 0.4, 0.3, 0.2)], barbel_c=c(60, 58, 52),
      fins=[[(0, c(80, 80, 72)), (1, c(130, 126, 114))], [(0, c(80, 80, 72)), (1, c(136, 130, 118))]]),
 dict(name="Sardine", L=1.6, R=0.24, H=1.1, w=0.7, colors=(c(40, 90, 120), c(170, 196, 210), c(236, 240, 244)),
      spots=(7, c(30, 50, 70), 0.04, 0.3), dorsal=[(0.42, 0.52, 0.26, "tri")], anal=(0.7, 0.78, 0.12, "round"), tail=("fork", 0.6, 44),
      iris=c(220, 220, 230), fins=[[(0, c(150, 170, 180)), (1, c(220, 230, 236))], [(0, c(80, 110, 130)), (1, c(200, 214, 224))]]),
 dict(name="Clownfish", L=1.2, R=0.42, H=1.05, prof="round", w=0.65, eye=0.1, colors=(c(240, 100, 20), c(250, 120, 30), c(255, 150, 60)),
      bands=[(0.14, 0.035), (0.48, 0.05), (0.88, 0.03)], scale_k=0.15,
      dorsal=[(0.25, 0.48, 0.24, "spiny", 0, 5), (0.5, 0.72, 0.3, "round")], anal=(0.62, 0.76, 0.24, "round"), tail=("round", 0.45, 45),
      pect=0.4, pelv=0.25,
      fins=[[(0, c(245, 110, 25)), (0.8, c(250, 130, 40)), (0.86, c(20, 16, 18)), (1, c(20, 16, 18))],
            [(0, c(245, 110, 25)), (0.8, c(250, 130, 40)), (0.86, c(20, 16, 18)), (1, c(20, 16, 18))]]),
 dict(name="BlueTang", L=1.5, R=0.52, H=1.35, w=0.45, prof="round", colors=(c(30, 70, 220), c(40, 100, 240), c(70, 130, 250)),
      extra=tang_extra, scale_k=0.0, dorsal=[(0.2, 0.85, 0.3, "long", 0)], anal=(0.45, 0.85, 0.25, "long"),
      tail=("fork", 0.55, 40), iris=c(30, 30, 60),
      fins=[[(0, c(30, 60, 200)), (0.85, c(40, 90, 230)), (0.9, c(16, 18, 34)), (1, c(16, 18, 34))],
            [(0, c(255, 210, 30)), (0.85, c(255, 220, 60)), (0.9, c(16, 18, 34)), (1, c(16, 18, 34))]]),
]

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for sp in FISH:
        if not want or sp["name"] in want:
            build(sp)
