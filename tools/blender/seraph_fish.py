"""Seraph Fish (Divine) - armoured angel-shark predator.
Open jaw with teeth, horn-like brow blades, six blade wings (X front silhouette),
hooked shark dorsal, heterocercal tail. Glow: eyes, gill slits, spiked halo crown.
Run: python seraph_fish.py [out_dir] [--no-render]
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishkit import Fish, V, lerp, smooth, c, side, basis, vnoise
from mathutils import Matrix
import numpy as np

f = Fish("SeraphFish", "Divine", L=5.6, R=0.74, H=0.95, belly=0.75,
         PT=[0, .03, .08, .15, .25, .38, .52, .66, .80, .90, 1.0],
         PR=[0, .28, .48, .68, .87, 1.0, .95, .76, .48, .28, .18],
         zc=lambda t: 0.05 * math.sin(math.pi * t) + 0.05 * (1 - t) ** 5,
         w=lambda t: 1.05 - 0.5 * t, fin_styles=2)
SW = dict(pupil=1, ivory=2, gold=3, mouth=4, gum=5, glow=6, pearl=7)
BLADE, TAIL = 0, 1
f.body(N=56, M=30)

def blade(name, sd, t0, t1, th, d0, d1, l0, l1, arch, nu=14, nv=8, style=BLADE, thick=0.035, hook=0.0):
    root = lambda s: side(f.surf(lerp(t0, t1, s), th, 0.9), sd)
    direc = lambda s: V(lerp(d0[0], d1[0], s), sd * lerp(d0[1], d1[1], s), lerp(d0[2], d1[2], s))
    nrm = V(-1, 0, 0).cross(direc(0.5).normalized()).normalized() * sd
    f.fin(name, root, direc, lambda s: lerp(l0, l1, s ** 0.9),
          lambda s, r: nrm * (arch * r * r) + V(-hook * r * r * (1 - s), 0, 0), nu, nv, thick, style)

for sd in (1, -1):
    nm = "L" if sd > 0 else "R"
    blade(f"WingPec_{nm}", sd, 0.22, 0.36, -0.55, (-0.3, 1, -0.28), (-1, 0.35, -0.1), 2.5, 0.4, 0.12, hook=0.5)
    blade(f"WingUp_{nm}", sd, 0.27, 0.37, 0.95, (-0.45, 0.75, 0.8), (-1, 0.3, 0.15), 1.8, 0.3, -0.1, hook=0.4)
    blade(f"WingRear_{nm}", sd, 0.62, 0.70, -0.3, (-0.6, 0.75, -0.25), (-1, 0.2, -0.05), 0.85, 0.2, 0.05, 10, 6)
    # brow blades: horn-like armour sweeping back over the eyes
    blade(f"Brow_{nm}", sd, 0.07, 0.2, 0.62, (-0.35, 0.45, 0.55), (-1, 0.25, 0.35), 0.18, 0.75, 0.0, 10, 5, thick=0.05)

# hooked shark dorsal + second dorsal + anal
f.fin("Dorsal", lambda s: f.surf(lerp(0.30, 0.48, s), math.pi / 2, 0.9),
      lambda s: V(lerp(-0.4, -1, s), 0, lerp(1, 0.12, s)), lambda s: lerp(1.9, 0.25, s ** 0.75),
      lambda s, r: V(-0.45 * r * r * (1 - s), 0, 0), 14, 9, 0.045, BLADE)
f.fin("Dorsal2", lambda s: f.surf(lerp(0.72, 0.79, s), math.pi / 2, 0.9),
      lambda s: V(lerp(-0.6, -1, s), 0, lerp(1, 0.2, s)), lambda s: lerp(0.5, 0.1, s),
      lambda s, r: V(0, 0, 0), 8, 5, 0.035, BLADE)
f.fin("Anal", lambda s: f.surf(lerp(0.70, 0.78, s), -math.pi / 2, 0.9),
      lambda s: V(lerp(-0.6, -1, s), 0, lerp(-1, -0.2, s)), lambda s: lerp(0.5, 0.1, s),
      lambda s, r: V(0, 0, 0), 8, 5, 0.035, BLADE)

# heterocercal tail: long upper lobe
te = 0.985; rte = f.r_of(te)
def t_dir(s):
    a = math.radians(lerp(-42, 64, s)); return V(-math.cos(a), 0, math.sin(a))
def t_len(s):
    e = abs(2 * s - 1); return (1.25 if s < 0.5 else 2.5) * (0.2 + 0.8 * e ** 1.5)
f.fin("Tail", lambda s: V(f.x_of(te), 0, f.zc(te) + lerp(-1, 1, s) * f.H * rte * 0.8), t_dir, t_len,
      lambda s, r: V(0, 0.1 * r * r, 0), 30, 10, 0.045, TAIL)

# ---- open jaw: lower jaw ellipsoid hinged at the back, dark mouth, teeth rows
def bottom(t, k=1.0): return f.surf(t, -math.pi / 2, k)
hinge = bottom(0.2) + V(0, 0, 0.05)
Rj = Matrix.Rotation(math.radians(-20), 3, "Y")
Mj = Matrix.Translation(hinge) @ Rj.to_4x4() @ Matrix.Translation(-hinge)
jc = bottom(0.12) + V(0.0, 0, -0.1); ja = (0.52, 0.46, 0.15)
f.sphere("Jaw", Mj @ jc, Rj, ja, SW["pearl"], 20, 12)
f.sphere("Maw", bottom(0.12) + V(-0.03, 0, -0.03), basis(V(1, 0, 0)), (0.4, 0.34, 0.1), SW["mouth"], 18, 10)
for i, ph in enumerate(np.linspace(-1, 1, 11)):            # upper row along the U of the snout
    t = lerp(0.045, 0.18, abs(ph) ** 0.8); th = -math.pi / 2 + ph * 1.0
    p = f.surf(t, th, 0.98); ln = 0.17 - 0.05 * abs(ph)
    f.tube(f"ToothU{i}", [p, p + V(0.01, 0, -ln * 0.6), p + V(-0.02, -ph * 0.02, -ln)], 0.045, 0.004, K=6, sub=3, sw=SW["ivory"])
for i, ph in enumerate(np.linspace(-1, 1, 9)):             # lower row on the jaw's front rim
    a = ph * 1.1; el = 0.75
    p = jc + V(ja[0] * math.cos(a) * math.cos(el), ja[1] * math.sin(a) * math.cos(el), ja[2] * math.sin(el))
    ln = 0.14 - 0.04 * abs(ph)
    pts = [Mj @ q for q in (p, p + V(0.01, 0, ln * 0.6), p + V(-0.02, ph * 0.02, ln))]
    f.tube(f"ToothL{i}", pts, 0.04, 0.004, K=6, sub=3, sw=SW["ivory"])

# eyes (glowing, slit pupils) tucked under the brow blades
f.eyes(0.13, 0.32, 0.1, SW["glow"], SW["pupil"], SW["gum"], SW["ivory"],
       pupil_scale=(0.03, 0.022, 0.085), fwd=0.4, sink=0.04, rim_r=0.022, glint=0.0001)
for ob in [o for o in f.parts if o.name.startswith("Eye_")]:
    f.parts.remove(ob); f.glow.append(ob)

# ---- glow: gill slits + spiked halo crown
for sd in (1, -1):
    for i in range(5):
        t = 0.2 + i * 0.022
        pts = [side(f.surf(t + 0.012 * (1 - abs(u)) , u, 1.0), sd) for u in np.linspace(-0.55, 0.45, 5)]
        f.tube(f"Gill_{sd}_{i}", pts, 0.026, 0.02, K=6, sub=3, glow=True, sw=SW["glow"])
hc = f.surf(0.16, math.pi / 2) + V(-0.25, 0, 0.62); hn = V(-0.25, 0, 1).normalized()
f.torus("Halo", hc, hn, 0.46, 0.05, SW["glow"], 32, 8, glow=True)
Bm = basis(hn); hy, hz = Bm.col[1], Bm.col[2]
for i in range(12):
    a = 2 * math.pi * i / 12; rd = math.cos(a) * hy + math.sin(a) * hz; ln = 0.26 if i % 2 == 0 else 0.15
    f.tube(f"Spike{i}", [hc + rd * 0.45, hc + rd * (0.5 + ln * 0.4) + hn * ln * 0.3, hc + rd * (0.5 + ln) + hn * ln * 0.7],
           0.045, 0.004, K=6, sub=3, glow=True, sw=SW["glow"])

# ---- texture: midnight navy armour over pearl, gold pinstripe, darker snout
NAVY, NAVY2, PEARL = c(18, 22, 52), c(38, 50, 112), c(236, 238, 248)
def paint(T, Vv, top):
    X, Y = T * f.L, Vv * 4.0
    line = top + 0.1 - 0.15 * np.sin(T * 3.4)
    split = smooth(-0.02, 0.02, line)
    back = NAVY + (NAVY2 - NAVY) * smooth(0.95, 0.2, top)[..., None]
    back = back * (0.92 + 0.08 * vnoise(X, Y, 6, 5))[..., None]
    col = PEARL * (1 - split[..., None]) + back * split[..., None]
    col = col * (1 - 0.35 * smooth(0.12, 0.0, T) * split)[..., None]
    pin = np.exp(-(line / 0.03) ** 2) * smooth(0.06, 0.12, T)
    return col * (1 - pin[..., None]) + c(234, 182, 66) * pin[..., None]

f.texture(paint,
          fin_stops=[[(0, c(18, 22, 54)), (0.5, c(48, 70, 168)), (0.82, c(228, 234, 252)), (1, c(240, 186, 66))],
                     [(0, c(18, 22, 54)), (0.55, c(44, 64, 158)), (0.86, c(226, 232, 252)), (1, c(240, 186, 66))]],
          strips=[(c(200, 140, 40), c(255, 230, 150), 1.0)] * 2,
          swatches={SW["pupil"]: c(12, 10, 24), SW["ivory"]: c(250, 244, 226), SW["gold"]: c(232, 176, 58),
                    SW["mouth"]: c(40, 6, 18), SW["gum"]: c(14, 16, 36), SW["glow"]: c(255, 196, 64),
                    SW["pearl"]: c(228, 230, 244)},
          ray_period=16, ray_strength=0.12)
f.finish(bend=0.3, glow_color=c(255, 196, 64), cam_scale=1.12,
         views={"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50), "side": ((12.5, 0, 0.6), (0, 0, 0.2), 50),
                "front": ((1.6, 9.0, 1.2), (0, 0, 0.2), 45)})
