"""Dragon Koi (Divine) - style reference fish.
Run with Blender's Python (bpy):  python dragon_koi.py [out_dir] [--no-render]
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishkit import Fish, V, lerp, smooth, c, side, vnoise, scales
import numpy as np

f = Fish("DragonKoi", "Divine", L=5.0, R=0.78, H=1.08,
         PT=[0, .02, .06, .12, .22, .35, .50, .65, .80, .90, 1.0],
         PR=[0, .40, .62, .80, .94, 1.0, .93, .73, .47, .31, .25],
         zc=lambda t: 0.06 * math.sin(math.pi * t) - 0.06 * (1 - t) ** 8,
         w=lambda t: 0.80 - 0.28 * t * t)
SW = dict(iris=0, pupil=1, white=2, lip=3, rim=4, mouth=5)

f.body()

# ---- fins
def d_len(s):
    env = math.sin(math.pi * s) ** 0.55 * (1.15 - 0.55 * s)
    return 0.95 * env * (0.58 + 0.42 * ((s * 8) % 1.0) ** 1.4)
f.fin("Dorsal", lambda s: f.surf(lerp(0.13, 0.74, s), math.pi / 2, 0.93),
      lambda s: V(lerp(-0.25, -0.85, s), 0, 1), d_len,
      lambda s, r: V(0, 0.05 * r ** 1.5 * math.sin(2 * math.pi * 3 * s + 2 * r), 0), 72, 7)

te = 0.985; re = f.r_of(te)
def t_dir(s):
    a = math.radians(lerp(-62, 62, s)); return V(-math.cos(a), 0, math.sin(a))
def t_len(s):
    e = abs(2 * s - 1)
    return 2.0 * (0.5 + 0.5 * e ** 0.8) * (1 - 0.38 * e ** 6) * (1 + 0.045 * math.sin(12 * math.pi * s))
f.fin("Tail", lambda s: V(f.x_of(te), 0, f.zc(te) + lerp(-1, 1, s) * f.H * re * 0.8), t_dir, t_len,
      lambda s, r: V(0, 0.24 * r ** 1.6 * math.sin(math.pi * 1.2 * r + 2 * s), 0), 36, 11, 0.03)

for sd in (1, -1):
    nm = "L" if sd > 0 else "R"
    pn = V(-0.2, sd * 0.35, 1).normalized()
    f.fin(f"Pectoral_{nm}", lambda s, sd=sd: side(f.surf(lerp(0.19, 0.25, s), -0.75, 0.92), sd),
          lambda s, sd=sd: V(lerp(-0.35, -0.95, s), sd * lerp(0.85, 0.35, s), lerp(-0.45, -0.25, s)),
          lambda s: 1.35 * (0.45 + 0.55 * math.sin(math.pi * (0.15 + 0.85 * s)) ** 0.8) * (1 + 0.05 * math.sin(10 * math.pi * s)),
          lambda s, r, pn=pn: pn * (0.12 * r ** 1.8 * math.sin(2 * math.pi * 1.2 * s + 3 * r)), 20, 9)
    f.fin(f"Pelvic_{nm}", lambda s, sd=sd: side(f.surf(lerp(0.42, 0.48, s), -1.15, 0.92), sd),
          lambda s, sd=sd: V(-0.65, sd * lerp(0.45, 0.25, s), -0.7),
          lambda s: 0.75 * (0.4 + 0.6 * math.sin(math.pi * (0.2 + 0.8 * s)) ** 0.8),
          lambda s, r: V(0, 0, 0.05 * r * r * math.sin(5 * s + 2 * r)), 14, 8)
    f.fin(f"Frill_{nm}", lambda s, sd=sd: side(f.surf(0.15 + 0.01 * s, lerp(-0.45, 0.75, s), 0.95), sd),
          lambda s, sd=sd: V(-1, sd * 0.55, lerp(-0.1, 0.35, s)),
          lambda s: 0.55 * (0.45 + 0.55 * ((s * 3) % 1.0) ** 1.3) * (0.6 + 0.4 * math.sin(math.pi * s)),
          lambda s, r: V(0, 0, 0), 24, 4, 0.02)
f.fin("Anal", lambda s: f.surf(lerp(0.66, 0.78, s), -math.pi / 2, 0.92), lambda s: V(-0.7, 0, -1),
      lambda s: 0.5 * math.sin(math.pi * s) ** 0.6 * (1.2 - 0.5 * s),
      lambda s, r: V(0, 0.03 * r * math.sin(6 * s), 0), 16, 6)

# ---- horns, whiskers, barbels
for sd in (1, -1):
    nm = "L" if sd > 0 else "R"
    hb = side(f.surf(0.10, 1.12, 0.9), sd)
    rel = lambda x, y, z, hb=hb, sd=sd: hb + V(x, sd * y, z)
    f.tube(f"Horn_{nm}", [rel(0, 0, 0), rel(-0.12, .10, .35), rel(-0.45, .24, .62), rel(-0.95, .34, .70), rel(-1.25, .36, .62)],
           0.10, 0.012, 0, pw=0.9)
    bp = rel(-0.2, .14, .45)
    f.tube(f"HornBranch_{nm}", [bp + V(0.06, 0, -0.08), bp, bp + V(0.06, sd*.06, .22), bp + V(0.02, sd*.1, .38)], 0.06, 0.01, 0)
    wb = side(f.surf(0.035, -0.15, 0.9), sd)
    relw = lambda x, y, z, wb=wb, sd=sd: wb + V(x, sd * y, z)
    f.tube(f"Whisker_{nm}", [relw(0, 0, 0), relw(.15, .18, -.05), relw(.05, .55, -.2), relw(-.5, .85, -.35),
                             relw(-1.1, .95, -.25), relw(-1.5, .8, -.02), relw(-1.62, .62, .12)], 0.05, 0.008, 1, pw=0.7)
    bb = side(f.surf(0.02, -0.9, 0.85), sd)
    f.tube(f"Barbel_{nm}", [bb, bb + V(.06, sd*.08, -.12), bb + V(-.03, sd*.12, -.27)], 0.03, 0.008, 1)

# ---- face
from fishkit import basis
f.eyes(0.085, 0.42, 0.19, SW["iris"], SW["pupil"], SW["rim"], SW["white"])
mc = f.axis(0) + V(-0.03, 0, -0.03)
f.torus("Lips", mc, V(1, 0, 0), 0.10, 0.048, SW["lip"], 20, 8)
f.sphere("Mouth", mc + V(0.02, 0, 0), basis(V(1, 0, 0)), (0.03, 0.09, 0.08), SW["mouth"], 12, 8)

# ---- texture
PEARL, CREAM = c(247, 243, 236), c(253, 248, 236)
CRIMSON, GOLD = c(206, 30, 46), c(228, 162, 48)
def paint(T, Vv, top):
    X, Y = T * f.L, Vv * 4.6
    col = PEARL + (CREAM - PEARL) * smooth(-0.2, -0.8, top)[..., None]
    fr = 0.65 * vnoise(X, Y, 1.0, 3) + 0.35 * vnoise(X, Y, 2.2, 4) + 0.45 * top - 0.80
    dcap = np.sqrt(((X - 0.42) / 0.3) ** 2 + ((Vv - 0.5) * 4.6 / 0.62) ** 2)
    fcap = 0.3 * (1 - dcap)
    fr = np.where(T < 0.15, fcap, np.maximum(fr, fcap))
    red = smooth(-0.015, 0.015, fr)
    g = 0.7 * vnoise(X, Y, 1.6, 9) + 0.3 * vnoise(X, Y, 3.1, 11) + 0.25 * top - 0.66
    gold = smooth(-0.015, 0.015, g) * (1 - red) * smooth(0.16, 0.2, T)
    col = col * (1 - red[..., None]) + CRIMSON * red[..., None]
    col = col * (1 - gold[..., None]) + GOLD * gold[..., None]
    edge, inner = scales(X, Y, 0.15)
    st = smooth(0.13, 0.19, T)[..., None] * (1 - 0.5 * smooth(-0.3, -0.9, top))[..., None]
    ecol = c(222, 170, 80) * (1 - red - gold)[..., None] + c(150, 14, 34) * red[..., None] + c(176, 110, 28) * gold[..., None]
    e = (edge * 0.6)[..., None] * st
    col = col * (1 - e) + ecol * e
    return col * (1 + 0.06 * st * (1 - inner[..., None]))

f.texture(paint,
          fin_stops=[[(0, c(176, 18, 38)), (0.4, c(232, 74, 48)), (0.72, c(246, 186, 80)), (1.0, c(255, 243, 210))]],
          strips=[(c(196, 128, 36), c(255, 244, 214), 1.4), (c(222, 160, 50), c(255, 232, 160), 1.0)],
          swatches={SW["iris"]: c(255, 196, 40), SW["pupil"]: c(18, 10, 16), SW["white"]: c(255, 255, 255),
                    SW["lip"]: c(190, 40, 62), SW["rim"]: c(120, 14, 30), SW["mouth"]: c(60, 8, 22)})
f.finish(bend=0.5)
