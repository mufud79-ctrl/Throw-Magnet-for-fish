"""Generic spec-driven fish builder used by the rarity batch scripts (commons.py, uncommons.py, ...)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishkit import Fish, V, lerp, smooth, c, side, basis, vnoise, scales
import numpy as np

PROF = dict(
    torpedo=[0, .35, .58, .78, .93, 1.0, .94, .76, .50, .32, .24],
    round=[0, .50, .72, .88, .98, 1.0, .95, .80, .55, .35, .26],
    blunt=[0, .58, .78, .90, .97, 1.0, .93, .74, .48, .30, .22])
PT = [0, .02, .06, .12, .22, .35, .50, .65, .80, .90, 1.0]
SW = dict(iris=0, pupil=1, white=2, lip=3, rim=4, barbel=5)

def fin_len(kind, h, n=6):
    if kind == "round":  return lambda s: h * math.sin(math.pi * s) ** 0.7 * (1.1 - 0.3 * s)
    if kind == "spiny":  return lambda s: h * math.sin(math.pi * s) ** 0.5 * (0.6 + 0.4 * ((s * n) % 1.0) ** 1.3)
    if kind == "sail":   return lambda s: h * (0.35 + 0.65 * math.sin(math.pi * min(1, s * 1.4)) ** 0.6) * (1 - 0.3 * s)
    if kind == "long":   return lambda s: h * (0.3 + 0.7 * math.sin(math.pi * s) ** 0.4)
    if kind == "tri":    return lambda s: h * (1 - s) ** 0.8 * smooth(0, 0.15, s)

def tail_len(kind, Lt):
    if kind == "fork":   return lambda s: Lt * (0.42 + 0.58 * abs(2*s-1) ** 1.2)
    if kind == "round":  return lambda s: Lt * (1 - 0.3 * abs(2*s-1) ** 2)
    if kind == "square": return lambda s: Lt * (0.92 + 0.08 * abs(2*s-1))
    if kind == "fan":    return lambda s: Lt * (0.85 + 0.15 * math.sin(math.pi * s)) * (1 + 0.04 * math.sin(14 * s))
    if kind == "veil":   return lambda s: Lt * (0.55 + 0.45 * abs(2*s-1) ** 0.8) * (1 - 0.3 * abs(2*s-1) ** 6)

def build(sp):
    f = Fish(sp["name"], sp.get("rarity", "Common"), L=sp["L"], R=sp["R"], H=sp.get("H", 1.1), PT=PT, PR=PROF[sp.get("prof", "torpedo")],
             zc=lambda t: sp.get("hump", 0.04) * sp["R"] * math.sin(math.pi * t),
             w=(lambda t, a=sp.get("w", 0.8), b=sp.get("wt", 0.25): a - b * t * t),
             belly=sp.get("belly", 0.9), fin_styles=2)
    f.body(N=40, M=24)
    R, L = sp["R"], sp["L"]; th_ = 0.02 * L + 0.012
    D, T_ = 0, 1
    for k, dd in enumerate(sp.get("dorsal", [])):     # (t0, t1, height, kind, style)
        t0, t1, h, kind = dd[:4]; st = dd[4] if len(dd) > 4 else D
        f.fin(f"Dorsal{k}", lambda s, t0=t0, t1=t1: f.surf(lerp(t0, t1, s), math.pi / 2, 0.9),
              lambda s: V(lerp(-0.25, -0.75, s), 0, 1), fin_len(kind, h, dd[5] if len(dd) > 5 else 6),
              lambda s, r: V(0, 0.02 * r * math.sin(6 * s), 0), 24 if kind == "spiny" else 12, 5, th_, st)
    if "anal" in sp:
        t0, t1, h, kind = sp["anal"]
        f.fin("Anal", lambda s: f.surf(lerp(t0, t1, s), -math.pi / 2, 0.9), lambda s: V(lerp(-0.3, -0.75, s), 0, -1),
              fin_len(kind, h), lambda s, r: V(0, 0, 0), 12, 5, th_, D)
    te = 0.985; rte = f.r_of(te); kind, Lt, spread = sp["tail"]
    f.fin("Tail", lambda s: V(f.x_of(te), 0, f.zc(te) + lerp(-1, 1, s) * f.H * rte * 0.8),
          lambda s: V(-math.cos(math.radians(lerp(-spread, spread, s))), 0, math.sin(math.radians(lerp(-spread, spread, s)))),
          tail_len(kind, Lt), lambda s, r: V(0, 0.08 * Lt * r * r * math.sin(1 + 2 * s), 0), 20, 7, th_, T_)
    pl, vl = sp.get("pect", 0.28 * L), sp.get("pelv", 0.2 * L)
    for sd in (1, -1):
        nm = "L" if sd > 0 else "R"
        if pl > 0: f.fin(f"Pect_{nm}", lambda s, sd=sd: side(f.surf(lerp(0.2, 0.26, s), -0.5, 0.9), sd),
              lambda s, sd=sd: V(lerp(-0.4, -0.9, s), sd * lerp(0.8, 0.4, s), -0.3),
              lambda s: pl * (0.5 + 0.5 * math.sin(math.pi * (0.2 + 0.8 * s)) ** 0.8),
              lambda s, r, sd=sd: V(0, 0, 0.06 * pl * r * r), 10, 5, th_, D)
        if vl > 0:
            f.fin(f"Pelv_{nm}", lambda s, sd=sd: side(f.surf(lerp(0.42, 0.47, s), -1.2, 0.9), sd),
                  lambda s, sd=sd: V(-0.6, sd * 0.35, -0.75), lambda s: vl * (0.5 + 0.5 * math.sin(math.pi * s)),
                  lambda s, r: V(0, 0, 0), 8, 4, th_, D)
        for k, (t, th, ln, droop) in enumerate(sp.get("barbels", [])):
            b = side(f.surf(t, th, 0.9), sd)
            f.tube(f"Barbel_{nm}{k}", [b, b + V(0.05 * ln, sd * 0.35 * ln, -droop * 0.3 * ln),
                                        b + V(-0.4 * ln, sd * 0.7 * ln, -droop * ln)], 0.022 * L ** 0.5, 0.006, sw=SW["barbel"], K=6, sub=4)
    re = sp.get("eye", 0.075 * L)
    if sp.get("eyes", True): f.eyes(sp.get("eye_t", 0.11), sp.get("eye_th", 0.35), re, SW["iris"], SW["pupil"], SW["rim"], SW["white"],
           pupil_scale=(re * 0.3, re * 0.58, re * 0.58), fwd=0.3, sink=re * 0.4, rim_r=re * 0.13, glint=re * 0.22)
    mr = sp.get("mouth", 0.045 * L)
    mc = f.axis(0) + V(-mr * 0.3, 0, -mr * 0.3)
    if mr > 0:
        f.torus("Lips", mc, V(1, 0, 0), mr, mr * 0.45, SW["lip"], 16, 6)
        f.sphere("Mouth", mc + V(mr * 0.1, 0, 0), basis(V(1, 0, 0)), (mr * 0.3, mr * 0.85, mr * 0.75), SW["pupil"], 10, 6)
    if "hook" in sp: sp["hook"](f, sp)

    back, mid, belly = sp["colors"]
    def paint(T, Vv, top):
        X, Y = T * L, Vv * f.circ(0.35)
        col = mid + (back - mid) * smooth(0.0, 0.85, top)[..., None]
        col = col + (belly - col) * smooth(-0.1, -0.8, top)[..., None]
        if "noise" in sp: col = col * (1 + sp["noise"] * (vnoise(X, Y, 3 / L, 2) - 0.5))[..., None]
        if "bars" in sp:
            n, bc, k, t0, t1 = sp["bars"]
            b = smooth(0.25, 0.55, 0.5 + 0.5 * np.cos(2 * np.pi * n * (T - t0) / (t1 - t0))) * smooth(t0, t0 + .03, T) * (1 - smooth(t1 - .03, t1, T))
            b = b * smooth(-0.5, 0.1, top) * k; col = col * (1 - b[..., None]) + bc * b[..., None]
        if "stripe" in sp:
            sc_, wdt, at = sp["stripe"]
            m = np.exp(-((top - at) / wdt) ** 2) * smooth(0.1, 0.18, T); col = col * (1 - m[..., None]) + sc_ * m[..., None]
        if "spots" in sp:
            n, scol, rad, at = sp["spots"]
            dx = (T * n) % 1.0 - 0.5; m = (np.hypot(dx / n * L, (top - at) * 0.9) < rad) * smooth(0.18, 0.22, T) * (1 - smooth(0.75, 0.8, T))
            col = col * (1 - m[..., None]) + scol * m[..., None]
        if "bands" in sp:
            for (tc, wd) in sp["bands"]:
                d = np.abs(T - tc - 0.04 * top) / wd
                col = np.where((d < 1)[..., None], c(250, 250, 250), np.where((d < 1.3)[..., None], c(24, 18, 20), col))
        if "spot" in sp:
            tc, at, rr, scol = sp["spot"]
            m = smooth(1.05, 0.95, np.hypot((T - tc) * L, (top - at) * 0.8) / rr); col = col * (1 - m[..., None]) + scol * m[..., None]
        if "speckle" in sp:
            scol, freq, thr, tmin = sp["speckle"]
            m = smooth(thr, thr + 0.03, vnoise(X, Y, freq, 13)) * smooth(tmin, tmin + 0.2, top) * smooth(0.1, 0.16, T)
            col = col * (1 - m[..., None]) + scol * m[..., None]
        if "extra" in sp: col = sp["extra"](T, Vv, top, X, Y, col)
        edge, inner = scales(X, Y, sp.get("scale", 0.05 * L + 0.03))
        e = (edge * sp.get("scale_k", 0.35))[..., None] * smooth(0.12, 0.18, T)[..., None]
        return col * (1 - e) + col * 0.6 * e
    f.texture(paint, fin_stops=sp["fins"], strips=[(c(90, 80, 70), c(150, 140, 120), 1.0)] * 2,
              swatches={SW["iris"]: sp.get("iris", c(214, 176, 70)), SW["pupil"]: c(14, 12, 16), SW["white"]: c(255, 255, 255),
                        SW["lip"]: sp.get("lip", back * 0.8), SW["rim"]: back * 0.55, SW["barbel"]: sp.get("barbel_c", back * 1.1)})
    tot = L + sp["tail"][1]
    f.finish(bend=sp.get("bend", 0.08 * tot), bend_len=tot + 0.5, cam_scale=sp.get("cam", max(0.45, tot / 6.6)),
             roll=sp.get("roll", 0.0), glow_color=sp.get("glow"),
             views={"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50), "side": ((12.5, 0, 0.6), (0, 0, 0.2), 50)})

