"""Seraph Fish (Divine) - six feathered wing-fins, floating halo.
Glow parts (halo, forehead gem, star dots) -> SeraphFish_Glow mesh (set to Neon in Roblox).
Run with Blender's Python (bpy):  python seraph_fish.py [out_dir] [--no-render]
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishkit import Fish, V, lerp, smooth, c, side, basis, scales
import numpy as np

f = Fish("SeraphFish", "Divine", L=4.4, R=0.66, H=1.3,
         PT=[0, .02, .06, .12, .22, .35, .50, .65, .80, .90, 1.0],
         PR=[0, .42, .64, .82, .95, 1.0, .92, .72, .46, .30, .24],
         zc=lambda t: 0.05 * math.sin(math.pi * t) - 0.05 * (1 - t) ** 8,
         w=lambda t: 0.66 - 0.22 * t * t, fin_styles=2)
SW = dict(iris=0, pupil=1, white=2, lip=3, rim=4, mouth=5, glow=6)
WING, TAIL = 0, 1

f.body()

def feather(s, n):            # rounded feather tips with small notches between them
    return 0.84 + 0.16 * abs(math.sin(math.pi * n * s)) ** 0.5

def wing(name, sd, t0, t1, th, d0, d1, l0, l1, n, arch, nu=30, nv=9):
    root = lambda s: side(f.surf(lerp(t0, t1, s), th, 0.9), sd)
    direc = lambda s: V(lerp(d0[0], d1[0], s), sd * lerp(d0[1], d1[1], s), lerp(d0[2], d1[2], s))
    mid = direc(0.5).normalized()
    nrm = V(-1, 0, 0).cross(mid).normalized() * sd
    length = lambda s: lerp(l0, l1, s ** 0.8) * feather(s, n)
    wave = lambda s, r: nrm * (arch * r * r) + V(0, sd * 0.12 * r ** 3, 0)
    f.fin(name, root, direc, length, wave, nu, nv, 0.03, WING)

for sd in (1, -1):
    nm = "L" if sd > 0 else "R"
    # great wings: rise up and back from the shoulders
    wing(f"WingUpper_{nm}", sd, 0.20, 0.34, 1.0, (0.15, 0.45, 1.0), (-0.95, 0.45, 0.55), 2.0, 1.1, 6, -0.28, 36, 10)
    # lower wings: sweep down and back
    wing(f"WingLower_{nm}", sd, 0.30, 0.42, -0.9, (-0.1, 0.55, -1.0), (-0.9, 0.4, -0.5), 1.3, 0.8, 5, 0.18)
    # small rear wings
    wing(f"WingRear_{nm}", sd, 0.60, 0.68, 0.25, (-0.4, 0.8, 0.45), (-1.0, 0.5, 0.15), 0.8, 0.5, 4, -0.08, 20, 6)

# long ribbon tail
te = 0.985; rte = f.r_of(te)
def t_dir(s):
    a = math.radians(lerp(-48, 48, s)); return V(-math.cos(a), 0, math.sin(a))
def t_len(s):
    e = abs(2 * s - 1)
    return 2.7 * (0.35 + 0.65 * e ** 1.2) * (1 - 0.32 * e ** 8) * feather(s, 9)
f.fin("Tail", lambda s: V(f.x_of(te), 0, f.zc(te) + lerp(-1, 1, s) * f.H * rte * 0.8), t_dir, t_len,
      lambda s, r: V(0, 0.32 * r ** 1.7 * math.sin(math.pi * 1.1 * r + 1.5 * s), 0), 40, 12, 0.03, TAIL)
f.fin("Anal", lambda s: f.surf(lerp(0.68, 0.78, s), -math.pi / 2, 0.92), lambda s: V(-0.8, 0, -1),
      lambda s: 0.45 * math.sin(math.pi * s) ** 0.6, lambda s, r: V(0, 0, 0), 12, 5, 0.025, TAIL)

# face: big gentle eyes, small mouth
f.eyes(0.09, 0.38, 0.2, SW["iris"], SW["pupil"], SW["rim"], SW["white"],
       pupil_scale=(0.05, 0.085, 0.095), rim_r=0.022, glint=0.05)
mc = f.axis(0) + V(-0.03, 0, -0.04)
f.torus("Lips", mc, V(1, 0, 0), 0.075, 0.035, SW["lip"], 18, 6)
f.sphere("Mouth", mc + V(0.015, 0, 0), basis(V(1, 0, 0)), (0.02, 0.065, 0.05), SW["mouth"], 10, 6)

# ---- glow parts
top = f.surf(0.12, math.pi / 2)
f.torus("Halo", top + V(0.2, 0, 0.9), V(0.25, 0, 1), 0.42, 0.06, SW["glow"], 32, 8, glow=True)
gp = f.surf(0.06, 1.25, 1.0); gn = (gp - f.axis(0.06)).normalized()
f.gem("Gem", gp + gn * 0.05, basis(gn, V(1, 0, 0)), (0.11, 0.09, 0.15), SW["glow"], glow=True)
for sd in (1, -1):
    for i, t in enumerate(np.linspace(0.36, 0.78, 5)):
        p = side(f.surf(float(t), 0.0, 1.0), sd); n = side((f.surf(float(t), 0.0) - f.axis(float(t))).normalized(), sd)
        f.sphere(f"Star_{sd}_{i}", p - n * 0.01, basis(n), (0.045 - 0.004 * i,) * 3, SW["glow"], 8, 6, glow=True)

# ---- texture
def paint(T, Vv, top):
    X, Y = T * f.L, Vv * 3.6
    back, mid, belly = c(246, 230, 190), c(236, 238, 252), c(184, 190, 246)
    col = mid + (back - mid) * smooth(0.2, 0.9, top)[..., None]
    col = col + (belly - col) * smooth(-0.15, -0.85, top)[..., None]
    # soft iridescent shimmer along the body
    hue = 0.5 + 0.5 * np.sin(X * 2.2 + Y * 0.8)
    col = col * (1 - 0.06 * hue[..., None]) + (c(255, 214, 236) * hue[..., None] + c(214, 236, 255) * (1 - hue[..., None])) * 0.06
    edge, inner = scales(X, Y, 0.12)
    st = smooth(0.13, 0.19, T)[..., None]
    e = (edge * 0.5)[..., None] * st
    col = col * (1 - e) + c(214, 168, 80) * e
    # gold lateral line (the glowing star dots sit on it)
    line = np.exp(-(top / 0.07) ** 2) * smooth(0.2, 0.3, T) * (1 - smooth(0.88, 0.95, T))
    col = col * (1 - 0.75 * line[..., None]) + c(232, 184, 82) * 0.75 * line[..., None]
    return col

f.texture(paint,
          fin_stops=[[(0, c(240, 244, 255)), (0.35, c(168, 204, 255)), (0.7, c(240, 198, 104)), (1, c(255, 226, 150))],
                     [(0, c(168, 158, 245)), (0.45, c(198, 218, 255)), (0.8, c(242, 202, 116)), (1, c(255, 230, 166))]],
          strips=[(c(230, 190, 90), c(255, 245, 210), 1.0), (c(230, 190, 90), c(255, 245, 210), 1.0)],
          swatches={SW["iris"]: c(96, 170, 255), SW["pupil"]: c(22, 22, 48), SW["white"]: c(255, 255, 255),
                    SW["lip"]: c(240, 160, 180), SW["rim"]: c(214, 170, 80), SW["mouth"]: c(90, 40, 70),
                    SW["glow"]: c(255, 200, 80)},
          ray_period=10, ray_strength=0.18)
f.finish(bend=0.35, glow_color=c(255, 200, 80), cam_scale=1.1)
