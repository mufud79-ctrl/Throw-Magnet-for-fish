"""Seraph Fish (Divine) - aggressive 'avenging angel' predator.
Six swept blade-wings, spiked halo crown, glowing slit eyes and LED side lines.
Glow parts -> SeraphFish_Glow (Neon). Run: python seraph_fish.py [out_dir] [--no-render]
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishkit import Fish, V, lerp, smooth, c, side, basis, scales
import numpy as np

f = Fish("SeraphFish", "Divine", L=5.4, R=0.68, H=1.0,
         PT=[0, .03, .08, .15, .25, .38, .52, .66, .80, .90, 1.0],
         PR=[0, .20, .40, .62, .84, 1.0, .96, .78, .50, .30, .21],
         zc=lambda t: 0.04 * math.sin(math.pi * t) - 0.08 * (1 - t) ** 6,
         w=lambda t: 0.72 - 0.25 * t * t, fin_styles=2)
SW = dict(pupil=1, ivory=2, gold=3, rim=4, mouth=5, glow=6)
BLADE, TAIL = 0, 1

f.body(N=54)

def blade(name, sd, t0, t1, th, d0, d1, l0, l1, arch, nu=14, nv=8, style=BLADE, thick=0.03):
    root = lambda s: side(f.surf(lerp(t0, t1, s), th, 0.9), sd)
    direc = lambda s: V(lerp(d0[0], d1[0], s), sd * lerp(d0[1], d1[1], s), lerp(d0[2], d1[2], s))
    nrm = V(-1, 0, 0).cross(direc(0.5).normalized()).normalized() * sd
    f.fin(name, root, direc, lambda s: lerp(l0, l1, s ** 0.9),
          lambda s, r: nrm * (arch * r * r), nu, nv, thick, style)

for sd in (1, -1):
    nm = "L" if sd > 0 else "R"
    blade(f"WingMain_{nm}", sd, 0.20, 0.36, 0.85, (-0.45, 0.9, 0.3), (-1, 0.3, 0.06), 2.3, 0.45, -0.15)
    blade(f"WingLow_{nm}", sd, 0.32, 0.44, -0.85, (-0.55, 0.8, -0.4), (-1, 0.25, -0.06), 1.5, 0.35, 0.1)
    blade(f"WingRear_{nm}", sd, 0.60, 0.68, 0.25, (-0.7, 0.65, 0.2), (-1, 0.2, 0.04), 0.95, 0.25, -0.05, 10, 6)

# swept dorsal blade + anal finlet
f.fin("Dorsal", lambda s: f.surf(lerp(0.30, 0.50, s), math.pi / 2, 0.9),
      lambda s: V(lerp(-0.8, -1, s), 0, lerp(1, 0.18, s)), lambda s: lerp(1.25, 0.2, s ** 0.8),
      lambda s, r: V(0, 0, 0), 14, 8, 0.035, BLADE)
f.fin("Anal", lambda s: f.surf(lerp(0.62, 0.72, s), -math.pi / 2, 0.9),
      lambda s: V(lerp(-0.8, -1, s), 0, lerp(-1, -0.2, s)), lambda s: lerp(0.6, 0.12, s),
      lambda s, r: V(0, 0, 0), 10, 6, 0.03, BLADE)

# forked lunate tail, razor tips
te = 0.985; rte = f.r_of(te)
def t_dir(s):
    a = math.radians(lerp(-58, 58, s)); return V(-math.cos(a), 0, math.sin(a))
f.fin("Tail", lambda s: V(f.x_of(te), 0, f.zc(te) + lerp(-1, 1, s) * f.H * rte * 0.8), t_dir,
      lambda s: 2.1 * (0.22 + 0.78 * abs(2 * s - 1) ** 1.6),
      lambda s, r: V(0, 0.12 * r ** 2 * math.sin(1.5 * s), 0), 30, 10, 0.035, TAIL)

# face: glowing slit eyes under angry gold brows, fangs, mouth line
f.eyes(0.1, 0.32, 0.14, SW["glow"], SW["pupil"], SW["rim"], SW["ivory"],
       pupil_scale=(0.04, 0.03, 0.12), fwd=0.5, sink=0.06, rim_r=0.026, glint=0.0001)
for ob in [o for o in f.parts if o.name.startswith("Eye_")]:   # eyeballs glow
    f.parts.remove(ob); f.glow.append(ob)
for sd in (1, -1):
    nm = "L" if sd > 0 else "R"
    p = lambda t, th, k, sd=sd: side(f.surf(t, th, k), sd)
    f.tube(f"Brow_{nm}", [p(0.045, 0.30, 1.0), p(0.075, 0.50, 1.07), p(0.115, 0.70, 1.1), p(0.16, 0.86, 1.08)],
           0.06, 0.025, sw=SW["gold"])
    f.tube(f"MouthLine_{nm}", [p(0.003, -0.3, 1.0), p(0.03, -0.45, 1.0), p(0.065, -0.5, 1.0)], 0.022, 0.016, sw=SW["mouth"])
    for i, (t, ln) in enumerate([(0.012, 0.16), (0.04, 0.11)]):
        b = p(t, -0.62, 0.97)
        f.tube(f"Fang_{nm}{i}", [b, b + V(-0.01, sd * 0.02, -ln * 0.6), b + V(-0.04, sd * 0.03, -ln)], 0.035, 0.004, sw=SW["ivory"])

# glow: spiked halo crown + LED side lines
hc = f.surf(0.14, math.pi / 2) + V(-0.15, 0, 0.5); hn = V(0.25, 0, 1).normalized()
f.torus("Halo", hc, hn, 0.4, 0.045, SW["glow"], 32, 8, glow=True)
Bm = basis(hn); hy, hz = Bm.col[1], Bm.col[2]
for i in range(10):
    a = 2 * math.pi * i / 10; rd = math.cos(a) * hy + math.sin(a) * hz
    f.tube(f"Spike{i}", [hc + rd * 0.4, hc + rd * 0.47 + hn * 0.05, hc + rd * 0.56 + hn * 0.13], 0.04, 0.004,
           K=6, sub=3, glow=True, sw=SW["glow"])
for sd in (1, -1):
    pts = [side(f.surf(float(t), 0.12, 1.005), sd) for t in np.linspace(0.16, 0.88, 9)]
    f.tube(f"LED_{sd}", pts, 0.022, 0.012, K=6, sub=4, glow=True, sw=SW["glow"])

# ---- texture: midnight navy over pearl, gold pinstripe at the split
NAVY, NAVY2, PEARL = c(22, 28, 64), c(40, 52, 110), c(236, 238, 248)
def paint(T, Vv, top):
    X, Y = T * f.L, Vv * 3.6
    line = top - 0.18 - 0.12 * np.sin(T * 3.0)
    split = smooth(-0.02, 0.02, line)
    back = NAVY + (NAVY2 - NAVY) * smooth(0.95, 0.3, top)[..., None]
    col = PEARL * (1 - split[..., None]) + back * split[..., None]
    edge, inner = scales(X, Y, 0.13)
    e = (edge * 0.5)[..., None] * smooth(0.13, 0.19, T)[..., None]
    col = col * (1 - e) + (c(70, 96, 190) * split[..., None] + c(196, 200, 222) * (1 - split[..., None])) * e
    pin = np.exp(-(line / 0.035) ** 2) * smooth(0.08, 0.14, T)
    return col * (1 - pin[..., None]) + c(234, 182, 66) * pin[..., None]

f.texture(paint,
          fin_stops=[[(0, c(22, 28, 66)), (0.45, c(52, 74, 170)), (0.8, c(230, 236, 252)), (1, c(240, 188, 72))],
                     [(0, c(22, 28, 66)), (0.5, c(46, 66, 160)), (0.85, c(226, 232, 252)), (1, c(240, 188, 72))]],
          strips=[(c(200, 140, 40), c(255, 230, 150), 1.0), (c(200, 140, 40), c(255, 230, 150), 1.0)],
          swatches={SW["pupil"]: c(12, 10, 24), SW["ivory"]: c(250, 244, 226), SW["gold"]: c(232, 176, 58),
                    SW["rim"]: c(14, 16, 36), SW["mouth"]: c(10, 10, 24), SW["glow"]: c(255, 196, 64)},
          ray_period=16, ray_strength=0.15)
f.finish(bend=0.3, glow_color=c(255, 196, 64), cam_scale=1.1,
         views={"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50), "side": ((12.5, 0, 0.6), (0, 0, 0.2), 50)})
