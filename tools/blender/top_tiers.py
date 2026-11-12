"""Mythic, Secret and Celestial fish. Run: python top_tiers.py [FishName ...] [--no-render]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishgen import *
from epics import manta_hook, eye_pair
from legendaries import gills, cracks, shark_tail

AG = dict(brow=True, pupil=(0.3, 0.22, 0.62), eye_k=0.04)
PROF["shark"] = [0, .28, .48, .68, .87, 1.0, .95, .76, .48, .28, .18]
PROF["whale"] = [0, .55, .75, .88, .96, 1.0, .95, .80, .55, .32, .20]
FIN_PARTS = ("Dorsal", "Tail", "Pect", "Pelv", "Anal")

def aurora_hook(f, sp):
    manta_hook(f, sp)
    for sd in (1, -1):
        root = lambda s: side(f.surf(lerp(0.12, 0.62, s), 0.0, 0.92), sd)
        d = lambda s: V(lerp(0.15, -0.9, s), sd * lerp(1, 0.45, s), 0).normalized()
        ln = lambda s: 0.25 + 2.3 * min(s / 0.3, (1 - s) / 0.7) ** 1.1
        for rr in (0.35, 0.62, 0.88):
            pts = [root(s) + d(s) * ln(s) * rr + V(-0.2 * rr ** 3 * (1 - s), 0, -0.1 * rr * rr + 0.12 * rr ** 4 + 0.035)
                   for s in np.linspace(0.08, 0.9, 9)]
            glow_line(f, f"Aurora{sd}_{rr}", pts, 0.03, 0.02)
def ghost_hook(f, sp):
    for sd in (1, -1):
        for i, t in enumerate(np.linspace(0.26, 0.66, 7)):
            pts = [side(f.surf(float(t) + 0.03 * u * u, u, 1.005), sd) for u in np.linspace(-0.55, 0.75, 6)]
            glow_line(f, f"Rib{sd}_{i}", pts, 0.026, 0.018)
        glow_line(f, f"Spine{sd}", [side(f.surf(float(t), 0.85, 1.005), sd) for t in np.linspace(0.15, 0.93, 10)], 0.028, 0.012)
def ember_hook(f, sp):
    for ob in [o for o in f.parts if o.name.startswith(FIN_PARTS)]: f.parts.remove(ob); f.glow.append(ob)
    for sd in (1, -1):
        wb = side(f.surf(0.035, -0.15, 0.9), sd)
        f.tube(f"Whisker{sd}", [wb, wb + V(0.12, sd * 0.2, -0.05), wb + V(-0.3, sd * 0.6, -0.2), wb + V(-0.9, sd * 0.7, 0.05)], 0.04, 0.008, glow=True, sw=SW["glow"], K=6)
    cracks(f, 10, 21, 0.025, 0.15, 0.9, 0.035, "Ember")
def arowana_hook(f, sp):
    for sd in (1, -1):
        b = side(f.surf(0.02, -1.2, 0.95), sd)
        f.tube(f"ChinBarbel{sd}", [b, b + V(0.15, sd * 0.03, -0.04), b + V(0.4, sd * 0.06, 0.02)], 0.04, 0.01, sw=SW["x1"], K=6)
def mega_hook(f, sp): gills(f, 0.2, 5, SW["glow"], glow=True)
def hydra_hook(f, sp):
    for sd in (1, -1):
        base = side(f.surf(0.16, 0.15, 0.85), sd)
        neck = [base, base + V(0.25, sd * 0.35, 0.15), base + V(0.6, sd * 0.6, 0.32), base + V(0.95, sd * 0.68, 0.38)]
        f.tube(f"Neck{sd}", neck, 0.22, 0.17, sw=SW["x1"], K=10)
        hc = neck[-1] + V(0.22, 0, 0.02)
        f.extra_bones.append(dict(name="Neck_L" if sd > 0 else "Neck_R", head=base, tail=hc, parent="Head",
            match=lambda n, cen, sd=sd: cen.y * sd > 0.35 and n.startswith(("Neck", "Head", "HJaw", "HMaw", "HT", "HB", "HHorn", "Eye", "Pupil"))))
        f.sphere(f"Head{sd}", hc, basis(V(1, 0, 0)), (0.36, 0.2, 0.17), SW["x1"], 16, 10)
        hinge = hc + V(-0.12, 0, -0.08); Rj = Matrix.Rotation(math.radians(-24), 3, "Y")
        Mj = Matrix.Translation(hinge) @ Rj.to_4x4() @ Matrix.Translation(-hinge)
        jc = hc + V(0.06, 0, -0.14); f.sphere(f"HJaw{sd}", Mj @ jc, Rj, (0.28, 0.16, 0.06), SW["jaw"], 14, 8)
        f.sphere(f"HMaw{sd}", hc + V(0.06, 0, -0.1), basis(V(1, 0, 0)), (0.24, 0.13, 0.05), SW["maw"], 10, 6)
        for k, a in enumerate(np.linspace(-0.9, 0.9, 6)):
            p = hc + V(0.3 * math.cos(a) - 0.02, 0.16 * math.sin(a), -0.1)
            f.tube(f"HT{sd}{k}", [p, p + V(0, 0, -0.06), p + V(-0.01, 0, -0.11)], 0.028, 0.003, K=5, sub=2, sw=SW["tooth"])
            q = Mj @ (jc + V(0.26 * math.cos(a), 0.14 * math.sin(a), 0.05))
            f.tube(f"HB{sd}{k}", [q, Mj @ (jc + V(0.26 * math.cos(a), 0.14 * math.sin(a), 0.12))], 0.024, 0.003, K=5, sub=2, sw=SW["tooth"])
        eye_pair(f, [(hc + V(0.12, s2 * 0.15, 0.08), V(0.4, s2, 0.4).normalized()) for s2 in (1, -1)], 0.06, True)
        for k2, dz in enumerate((0.0, 0.08)):
            hb = hc + V(-0.15, 0, 0.12 + dz)
            f.tube(f"HHorn{sd}{k2}", [hb, hb + V(-0.12, sd * 0.06 * (k2 * 2 - 1), 0.16), hb + V(-0.34, sd * 0.1 * (k2 * 2 - 1), 0.22)], 0.05, 0.006, sw=SW["brow"], K=6)
def serpent_hook(f, sp):
    for sd in (1, -1):
        hb = side(f.surf(0.06, 1.0, 0.9), sd)
        f.tube(f"Horn{sd}", [hb, hb + V(-0.1, sd * 0.08, 0.3), hb + V(-0.5, sd * 0.2, 0.55), hb + V(-0.9, sd * 0.22, 0.5)], 0.09, 0.01, sw=SW["brow"], K=8)
        f.fin(f"Frill{sd}", lambda s, sd=sd: side(f.surf(0.1, lerp(-0.6, 0.7, s), 0.95), sd), lambda s, sd=sd: V(-1, sd * 0.7, lerp(-0.2, 0.4, s)),
              lambda s: 0.6 * (0.45 + 0.55 * ((s * 4) % 1.0) ** 1.3), lambda s, r: V(0, 0, 0), 24, 4, 0.03, 1)
def whale_hook(f, sp):
    f.sphere("WhaleMouth", f.axis(0.012) + V(0.02, 0, -0.08), basis(V(1, 0, 0)), (0.06, 0.62, 0.1), SW["maw"], 18, 8)
    rng = np.random.default_rng(9); pts = []
    for i in range(7):
        t = 0.2 + i * 0.09 + float(rng.uniform(-0.02, 0.02)); th = 0.9 + 0.4 * math.sin(i * 1.7)
        pts.append(f.surf(t, th, 1.012))
        f.sphere(f"Star{i}", pts[-1], basis((pts[-1] - f.axis(t)).normalized()), (0.08,) * 3, SW["glow"], 10, 6, glow=True)
    glow_line(f, "Constellation", pts, 0.014, 0.014)
    for sd in (1, -1):
        for k, th in enumerate((0.35, -0.1)):
            f.tube(f"Ridge{sd}{k}", [side(f.surf(float(t), th, 1.0), sd) for t in np.linspace(0.18, 0.85, 7)], 0.035, 0.015, sw=SW["x1"], K=6)

def aurora_extra(T, Vv, top, X, Y, col):
    b = 0.5 + 0.5 * np.sin(X * 3 + 2 * np.sin(Y * 2)); m = smooth(0.7, 0.95, b) * smooth(0.0, 0.6, top)
    return col * (1 - m[..., None]) + (c(80, 255, 170) * (1 - Vv[..., None]) + c(180, 90, 255) * Vv[..., None]) * m[..., None]
def ghost_extra(T, Vv, top, X, Y, col):
    return col * (0.92 + 0.12 * vnoise(X, Y, 3, 81))[..., None]
def ember_extra(T, Vv, top, X, Y, col):
    m = smooth(-0.02, 0.02, 0.6 * vnoise(X, Y, 1.4, 91) + 0.3 * top - 0.45)
    return col * (1 - m[..., None]) + c(230, 80, 20) * m[..., None]
def galaxy_extra(T, Vv, top, X, Y, col):
    n1 = vnoise(X, Y, 1.2, 101); n2 = vnoise(X, Y, 2.7, 102)
    neb = c(22, 16, 60) * (1 - n1[..., None]) + c(110, 40, 150) * n1[..., None]
    neb = neb * (1 - 0.5 * n2[..., None]) + c(40, 120, 200) * 0.5 * n2[..., None]
    stars = smooth(0.9, 0.93, vnoise(X, Y, 22, 103)); spots = smooth(0.82, 0.86, vnoise(X, Y, 5, 104)) * smooth(-0.2, 0.2, top)
    out = neb * (1 - np.maximum(stars, spots)[..., None]) + c(255, 246, 220) * np.maximum(stars, spots)[..., None]
    return out * (1 - 0.3 * smooth(-0.3, -0.9, top))[..., None] + c(120, 110, 170) * 0.3 * smooth(-0.3, -0.9, top)[..., None]

FISH = [
 dict(AG, name="AuroraRay", anims="ray", rarity="Mythic", L=2.8, R=0.5, H=0.42, w=1.25, wt=0.9, prof="blunt", belly=0.8,
      colors=(c(16, 30, 50), c(24, 44, 70), c(200, 220, 236)), extra=aurora_extra, scale_k=0.0, hook=aurora_hook, x1=c(20, 34, 56),
      glow=c(90, 255, 180), mouth=0.12, eye_th=0.15, eye_t=0.06, eye=0.08, pect=0, pelv=0, tail=(None, 0, 0), brow=False,
      dorsal=[(0.7, 0.78, 0.2, "tri")], bend=0.0, cam=0.85, fins=[[(0, c(16, 30, 50)), (0.6, c(30, 90, 110)), (1, c(120, 60, 200))]] * 2),
 dict(AG, name="GhostShark", rarity="Mythic", L=4.6, R=0.62, H=0.95, w=0.95, wt=0.5, prof="shark", belly=0.78,
      colors=(c(170, 196, 220), c(200, 220, 236), c(232, 240, 248)), extra=ghost_extra, scale_k=0.0, hook=ghost_hook, glow=c(180, 240, 255),
      glow_eyes=True, iris=c(180, 240, 255), jaw=(0.03, 0.17, 24, 13, 11, 0.09), mouth=0, brow_c=c(150, 176, 206),
      dorsal=[(0.32, 0.46, 1.3, "tri")], tail=shark_tail(1.9), pect=1.2, pelv=0.35,
      fins=[[(0, c(190, 214, 236)), (0.8, c(226, 240, 252)), (1, c(160, 230, 255))]] * 2),
 dict(AG, name="EmberKoi", rarity="Mythic", L=3.0, R=0.55, H=1.05, prof="round", hump=0.1, colors=(c(30, 24, 24), c(44, 34, 32), c(70, 50, 44)),
      extra=ember_extra, scale=0.16, scale_k=0.6, hook=ember_hook, glow=c(255, 140, 40), glow_eyes=True, iris=c(255, 140, 40), mouth=0.1,
      lip=c(60, 30, 26), dorsal=[(0.25, 0.7, 0.7, "spiny", 0, 9)], anal=(0.68, 0.78, 0.4, "spiny"), tail=("veil", 1.6, 60),
      pect=1.0, pelv=0.6, fins=[[(0, c(255, 140, 40)), (1, c(255, 220, 120))]] * 2),
 dict(AG, name="GoldenArowana", rarity="Mythic", L=3.8, R=0.48, H=1.05, w=0.6, prof="pike",
      zc_fn=lambda t: 0.06 * (1 - t) ** 6 + 0.02 * math.sin(math.pi * t), colors=(c(170, 120, 30), c(226, 176, 60), c(246, 214, 120)),
      scale=0.26, scale_k=0.75, hook=arowana_hook, x1=c(230, 180, 70), brow_c=c(200, 40, 40), mouth=0.07, iris=c(220, 40, 30),
      dorsal=[(0.66, 0.9, 0.4, "long")], anal=(0.58, 0.9, 0.4, "long"), tail=("round", 1.0, 45), pect=0.9, pelv=0.5,
      fins=[[(0, c(200, 150, 50)), (0.6, c(230, 120, 40)), (1, c(210, 40, 40))]] * 2),
 dict(AG, name="Megalodon", rarity="Secret", L=6.6, R=1.0, H=0.98, w=0.95, wt=0.5, prof="shark", belly=0.78,
      colors=(c(44, 50, 58), c(70, 76, 84), c(200, 200, 204)), noise=0.25, scale_k=0.0, hook=mega_hook, glow=c(255, 40, 40),
      glow_eyes=True, iris=c(255, 40, 40), jaw=(0.03, 0.17, 30, 17, 15, 0.16), mouth=0, eye_k=0.032,
      dorsal=[(0.3, 0.46, 2.0, "tri"), (0.76, 0.8, 0.4, "tri")], anal=(0.74, 0.79, 0.35, "tri"), tail=shark_tail(2.8),
      pect=2.0, pelv=0.5, cam=1.25, fins=[[(0, c(44, 50, 58)), (0.9, c(74, 80, 90)), (1, c(20, 22, 26))]] * 2),
 dict(AG, name="HydraEel", anims="hydra", rarity="Secret", L=5.2, R=0.36, H=1.1, w=0.85, prof="eel", colors=(c(20, 34, 24), c(34, 52, 36), c(90, 120, 60)),
      stripe=(c(150, 230, 40), 0.05, 0.3), scale=0.16, scale_k=0.5, hook=hydra_hook, x1=c(28, 44, 30), glow=c(180, 255, 60), glow_eyes=True,
      iris=c(180, 255, 60), jaw=(0.02, 0.13, 26, 13, 11, 0.1), mouth=0, eye=0.13, brow_c=c(150, 230, 40), jaw_c=c(60, 90, 50),
      dorsal=[(0.2, 0.96, 0.3, "spiny", 0, 20)], anal=(0.5, 0.97, 0.16, "long"), tail=(None, 0, 0), pect=0.5, pelv=0,
      wiggle=(0.45, 1.0), bend=0.0, cam=1.0, fins=[[(0, c(24, 40, 28)), (0.75, c(60, 110, 40)), (1, c(180, 255, 60))]] * 2),
 dict(AG, name="SeaSerpent", anims="eel", rarity="Secret", L=8.0, R=0.4, H=1.1, w=0.85, prof="eel", colors=(c(16, 70, 86), c(36, 130, 136), c(230, 190, 90)),
      scale=0.2, scale_k=0.6, hook=serpent_hook, glow=c(90, 240, 255), glow_eyes=True, iris=c(90, 240, 255), brow_c=c(230, 190, 90),
      jaw=(0.02, 0.12, 26, 15, 13, 0.12), mouth=0, eye=0.15, dorsal=[(0.12, 0.96, 0.6, "spiny", 0, 30)], anal=(0.45, 0.97, 0.2, "long"),
      tail=(None, 0, 0), pect=0.7, pelv=0, wiggle=(0.9, 1.5), bend=0.0, cam=1.35,
      fins=[[(0, c(16, 70, 86)), (0.6, c(40, 160, 160)), (1, c(230, 200, 100))]] * 2),
 dict(name="StarfallWhaleShark", rarity="Celestial", L=6.8, R=0.88, H=0.8, w=1.3, wt=0.75, prof="whale", belly=0.75,
      colors=(c(22, 16, 60),) * 3, extra=galaxy_extra, scale_k=0.0, hook=whale_hook, x1=c(70, 60, 140), glow=c(255, 240, 190),
      glow_eyes=True, iris=c(255, 240, 190), eye=0.13, eye_t=0.07, eye_th=0.0, mouth=0, brow=False,
      dorsal=[(0.38, 0.5, 1.4, "tri"), (0.76, 0.8, 0.4, "tri")], anal=(0.76, 0.8, 0.35, "tri"), tail=shark_tail(2.8),
      pect=1.8, pelv=0.5, cam=1.3, fins=[[(0, c(30, 22, 80)), (0.6, c(90, 50, 160)), (1, c(200, 180, 255))]] * 2),
]

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a.startswith("--")]
    for sp in FISH:
        if not want or sp["name"] in want: build(sp)
