"""Generic spec-driven fish builder used by the rarity batch scripts (commons.py, uncommons.py, ...)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishkit import Fish, V, lerp, smooth, c, side, basis, vnoise, scales
import numpy as np
from mathutils import Matrix

PROF = dict(
    torpedo=[0, .35, .58, .78, .93, 1.0, .94, .76, .50, .32, .24],
    round=[0, .50, .72, .88, .98, 1.0, .95, .80, .55, .35, .26],
    blunt=[0, .58, .78, .90, .97, 1.0, .93, .74, .48, .30, .22],
    pike=[0, .22, .40, .60, .84, 1.0, .98, .86, .62, .40, .26],
    deep=[0, .50, .74, .90, .98, 1.0, .94, .78, .52, .32, .22],
    eel=[0, .55, .78, .92, .98, 1.0, .98, .92, .78, .50, .10])
PT = [0, .02, .06, .12, .22, .35, .50, .65, .80, .90, 1.0]
SW = dict(iris=0, pupil=1, white=2, lip=3, rim=4, barbel=5, tooth=6, maw=7, jaw=8, glow=9, brow=10, x1=11, x2=12)

def fin_len(kind, h, n=6):
    if kind == "round":  return lambda s: h * math.sin(math.pi * s) ** 0.7 * (1.1 - 0.3 * s)
    if kind == "spiny":  return lambda s: h * math.sin(math.pi * s) ** 0.5 * (0.6 + 0.4 * ((s * n) % 1.0) ** 1.3)
    if kind == "sail":   return lambda s: h * (0.35 + 0.65 * math.sin(math.pi * min(1, s * 1.4)) ** 0.6) * (1 - 0.3 * s)
    if kind == "long":   return lambda s: h * (0.3 + 0.7 * math.sin(math.pi * s) ** 0.4)
    if kind == "tri":    return lambda s: h * (1 - s) ** 0.8 * smooth(0, 0.15, s)

def tail_len(kind, Lt):
    if kind == "shark":  return lambda s: Lt * (0.55 if s < 0.5 else 1.0) * (0.25 + 0.75 * abs(2*s-1) ** 1.4)
    if kind == "fork":   return lambda s: Lt * (0.42 + 0.58 * abs(2*s-1) ** 1.2)
    if kind == "round":  return lambda s: Lt * (1 - 0.3 * abs(2*s-1) ** 2)
    if kind == "square": return lambda s: Lt * (0.92 + 0.08 * abs(2*s-1))
    if kind == "fan":    return lambda s: Lt * (0.85 + 0.15 * math.sin(math.pi * s)) * (1 + 0.04 * math.sin(14 * s))
    if kind == "veil":   return lambda s: Lt * (0.55 + 0.45 * abs(2*s-1) ** 0.8) * (1 - 0.3 * abs(2*s-1) ** 6)

def open_jaw(f, sp, t_tip=0.03, t_hinge=0.16, angle=22, nu=11, nl=9, ln=None):
    """Hinged lower jaw (opened by `angle` deg), dark maw and upper/lower tooth rows."""
    L = f.L; ln = ln or 0.035 * L
    bottom = lambda t: f.surf(t, -math.pi / 2)
    tm = (t_tip + t_hinge) / 2; rm = f.r_of(tm)
    hinge = bottom(t_hinge) + V(0, 0, 0.1 * rm)
    Rj = Matrix.Rotation(math.radians(-angle), 3, "Y")
    Mj = Matrix.Translation(hinge) @ Rj.to_4x4() @ Matrix.Translation(-hinge)
    ja = ((t_hinge - t_tip) * L * 0.62, f.w(tm) * rm * 0.9, 0.22 * rm); jc = bottom(tm) + V(0, 0, -0.55 * ja[2])
    f.sphere("Jaw", Mj @ jc, Rj, ja, SW["jaw"], 18, 10)
    f.sphere("Maw", bottom(tm) + V(0, 0, 0.05 * rm), basis(V(1, 0, 0)), (ja[0] * 0.85, ja[1] * 0.8, ja[2] * 0.7), SW["maw"], 14, 8)
    for i, ph in enumerate(np.linspace(-1, 1, nu)):
        t = lerp(t_tip + 0.01, t_hinge - 0.015, abs(ph) ** 0.8); p = f.surf(t, -math.pi / 2 + ph * 0.95, 0.97)
        l = ln * (1 - 0.3 * abs(ph)) * (1.4 if i in (1, nu - 2) else 1)
        f.tube(f"ToothU{i}", [p, p + V(0.005, 0, -l * 0.6), p + V(-0.01, -ph * 0.01, -l)], l * 0.28, 0.003, K=5, sub=2, sw=SW["tooth"])
    for i, ph in enumerate(np.linspace(-1, 1, nl)):
        a = ph * 1.15; el = 0.8; l = ln * 0.85 * (1 - 0.3 * abs(ph))
        p = jc + V(ja[0] * math.cos(a) * math.cos(el), ja[1] * math.sin(a) * math.cos(el), ja[2] * math.sin(el))
        f.tube(f"ToothL{i}", [Mj @ q for q in (p, p + V(0.005, 0, l * 0.6), p + V(-0.01, ph * 0.01, l))], l * 0.28, 0.003,
               K=5, sub=2, sw=SW["tooth"])

def glow_line(f, name, pts, r0, r1=None):
    f.tube(name, pts, r0, r1 or r0 * 0.7, K=6, sub=4, glow=True, sw=SW["glow"])

def build(sp):
    f = Fish(sp["name"], sp.get("rarity", "Common"), L=sp["L"], R=sp["R"], H=sp.get("H", 1.1), PT=PT, PR=PROF[sp.get("prof", "torpedo")],
             zc=sp.get("zc_fn") or (lambda t: sp.get("hump", 0.04) * sp["R"] * math.sin(math.pi * t)),
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
    lo, hi = spread if isinstance(spread, tuple) else (-spread, spread)
    if kind:
        f.fin("Tail", lambda s: V(f.x_of(te), 0, f.zc(te) + lerp(-1, 1, s) * f.H * rte * 0.8),
              lambda s: V(-math.cos(math.radians(lerp(lo, hi, s))), 0, math.sin(math.radians(lerp(lo, hi, s)))),
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
    re = sp.get("eye", sp.get("eye_k", 0.075) * L)
    if sp.get("eyes", True): f.eyes(sp.get("eye_t", 0.11), sp.get("eye_th", 0.35), re, SW["iris"], SW["pupil"], SW["rim"], SW["white"],
           pupil_scale=tuple(re * k for k in sp.get("pupil", (0.3, 0.58, 0.58))), fwd=0.3, sink=re * 0.4, rim_r=re * 0.13, glint=re * 0.22)
    if sp.get("glow_eyes"):
        for ob in [o for o in f.parts if o.name.startswith("Eye_")]: f.parts.remove(ob); f.glow.append(ob)
    mr = sp.get("mouth", 0.045 * L)
    mc = f.axis(0) + V(-mr * 0.3, 0, -mr * 0.3)
    if mr > 0:
        f.torus("Lips", mc, V(1, 0, 0), mr, mr * 0.45, SW["lip"], 16, 6)
        f.sphere("Mouth", mc + V(mr * 0.1, 0, 0), basis(V(1, 0, 0)), (mr * 0.3, mr * 0.85, mr * 0.75), SW["pupil"], 10, 6)
    if sp.get("brow"):
        et, eth = sp.get("eye_t", 0.11), sp.get("eye_th", 0.35)
        for sd in (1, -1):
            pts = [side(f.surf(et - 0.045, eth + 0.1, 1.0), sd), side(f.surf(et, eth + re / f.r_of(et) * 1.0, 1.06), sd),
                   side(f.surf(et + 0.06, eth + re / f.r_of(et) * 1.6, 1.04), sd)]
            f.tube(f"Brow{sd}", pts, re * 0.32, re * 0.12, sw=SW["brow"], K=6, sub=4)
    if "jaw" in sp: open_jaw(f, sp, *sp["jaw"])
    for (th, t0, t1, n, rr) in sp.get("dots", []):
        for sd in (1, -1):
            for i, t in enumerate(np.linspace(t0, t1, n)):
                p = side(f.surf(float(t), th, 1.0), sd); nn = side((f.surf(float(t), th) - f.axis(float(t))).normalized(), sd)
                f.sphere(f"Dot{th}_{sd}_{i}", p - nn * rr * 0.3, basis(nn), (rr,) * 3, SW["glow"], 8, 6, glow=True)
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
    f.texture(paint, fin_stops=sp["fins"], **({} if "strips" in sp else {"strips": [(c(90, 80, 70), c(150, 140, 120), 1.0)] * 2}),
              swatches={SW["iris"]: sp.get("iris", c(214, 176, 70)), SW["pupil"]: c(14, 12, 16), SW["white"]: c(255, 255, 255),
                        SW["lip"]: sp.get("lip", back * 0.8), SW["rim"]: back * 0.55, SW["barbel"]: sp.get("barbel_c", back * 1.1),
                        SW["tooth"]: c(250, 246, 230), SW["maw"]: c(70, 12, 22), SW["jaw"]: sp.get("jaw_c", belly),
                        SW["glow"]: sp.get("glow", c(255, 255, 255)), SW["brow"]: sp.get("brow_c", back * 0.6),
                        SW["x1"]: sp.get("x1", c(128, 128, 128)), SW["x2"]: sp.get("x2", c(128, 128, 128))},
              **({"strips": sp["strips"]} if "strips" in sp else {}))
    tot = L + sp["tail"][1]
    f.finish(bend=sp.get("bend", 0.08 * tot), bend_len=tot + 0.5, cam_scale=sp.get("cam", max(0.45, tot / 6.6)),
             roll=sp.get("roll", 0.0), glow_color=sp.get("glow"), wiggle=sp.get("wiggle", (0, 0)),
             views=sp.get("views", {"hero": ((7.0, 7.5, 3.2), (0, 0.4, 0), 50), "side": ((12.5, 0, 0.6), (0, 0, 0.2), 50)}))

