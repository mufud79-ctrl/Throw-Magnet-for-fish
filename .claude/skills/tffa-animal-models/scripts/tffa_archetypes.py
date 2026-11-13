"""TFFA archetypes: parametric builders that bake in the reviewed style rules (big heads, block eyes, chunky legs,
studs on big parts) so a whole roster can be generated from short spec dicts.

    from tffa_archetypes import *
    build("Fox", quad, dict(body=(2.0, 0.9, 1.0), legs=(0.8, 0.3), head=(1.0, 1.0, 0.9), c1=rgb(230, 120, 40), ears="point",
          tail="bushy", x=[whiskers()]), out_dir)

Spec units are "design units": the builder scales everything by G (1.6) to studs. Accessories (x=[...]) are
factories returning fn(m, c); c holds anchor points (head centre, face front, back top, tail end...).
Head accessories must draw inside `with c["head"]():` so they follow the head scale."""
import os, math, shutil
from tffa_kit import *            # imports bpy first (mathutils needs it)
import numpy as np
from mathutils import Vector

# shared roster palette (sRGB, saturated TFFA brights)
GREY, DGREY, LGREY = rgb(150, 152, 160), rgb(80, 82, 90), rgb(196, 198, 204)
CREAM, TAN, TAN2, NOUGAT, SAND = rgb(244, 232, 205), rgb(200, 160, 110), rgb(206, 166, 110), rgb(214, 150, 110), rgb(232, 206, 150)
BROWN, DBROWN, PINKC = rgb(140, 96, 64), rgb(86, 58, 40), rgb(255, 176, 190)
YELLOW, ORANGE, RED, GOLD = rgb(255, 214, 50), rgb(245, 140, 40), rgb(220, 40, 40), rgb(245, 190, 50)
BLUE, LBLUE, CYAN, MAGENTA, LAVENDER = rgb(40, 110, 220), rgb(150, 205, 245), rgb(60, 220, 245), rgb(230, 70, 200), rgb(190, 150, 255)
SNOW, GREEN = rgb(250, 250, 255), rgb(80, 170, 70)

G = 1.6            # design units -> studs
HEAD_SCALE = 1.3   # TFFA heads are big
NS = dict(studs=False)

from contextlib import contextmanager, ExitStack, nullcontext
def _ctx(*factories):
    """Combine context-manager factories (e.g. a head frame + the Head bone) into one factory."""
    @contextmanager
    def f():
        with ExitStack() as st:
            for fac in factories: st.enter_context(fac())
            yield
    return f
def _in(m, name): return m.bone(name) if name in m.bones else nullcontext()
LR = lambda s: "L" if s > 0 else "R"

def _lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
def _brow(c1): return BLACK if _lum(c1) > 0.22 else lt(c1, 0.35)

# ============================================================================ face helpers
def front_eyes(m, c, P, k=1.0):
    """Big front-facing block eyes on the head front plane, above the snout."""
    hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
    e = hh * 0.36 * P.get("eye", 1.0) * k
    y = max(hw * 0.2, e * 0.62)
    m.eyes((c["xf"] + 0.01, y, hc.z + hh * 0.14), size=(e, e * 0.95), pupil=0.62, look=(0.3, -0.1),
           angry=0.3 if P.get("angry") else -0.05, white=P.get("iris", WHITE), brow_col=P.get("brow", _brow(c["C1"])),
           brow_h=0.34, brow_up=0.66, depth=max(0.12, e * 0.2), glow_pupil=P.get("eye_glow", False))

def side_eyes(m, c, P, fwd=0.15, up=0.18, k=1.0):
    hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
    e = hh * 0.4 * P.get("eye", 1.0) * k
    m.eyes((hc.x + hl * fwd, hw / 2 + 0.01, hc.z + hh * up), facing=(0.35, 1, 0), size=(e, e * 0.92), pupil=0.66,
           look=(0.35, 0), angry=0.25 if P.get("angry") else 0.0, white=P.get("iris", WHITE),
           brow_col=P.get("brow", dk(c["C1"], 0.6)), brow_h=0.3, brow_up=0.62, brow_w=1.05, brow_fwd=-0.04,
           depth=max(0.12, e * 0.2), glow_pupil=P.get("eye_glow", False))

def ears(m, c, kind, col, inner=None):
    if not kind: return
    hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
    inner = inner or lt(PINK, 0.1)
    for s in (1, -1):
      top = hc.z + hh / 2
      with m.bone(f"Ear_{LR(s)}", (hc.x - hl * 0.15, s * hw * 0.3, top)):
          if kind == "point":
              m.box(f"Ear{s}", (hc.x - hl * 0.15, s * hw * 0.3, top + hh * 0.22), (hl * 0.3, hw * 0.26, hh * 0.55), col,
                    top=(0.25, 0.3), rot=Rx(-s * 0.15), **NS)
              m.box(f"EarIn{s}", (hc.x - hl * 0.15 + hl * 0.1, s * hw * 0.3, top + hh * 0.17), (hl * 0.12, hw * 0.16, hh * 0.38), inner,
                    top=(0.3, 0.3), rot=Rx(-s * 0.15), **NS)
          elif kind == "fennec":
              m.box(f"Ear{s}", (hc.x - hl * 0.2, s * hw * 0.36, top + hh * 0.45), (hl * 0.38, hw * 0.34, hh * 1.0), col,
                    top=(0.25, 0.3), rot=Rx(-s * 0.3), **NS)
              m.box(f"EarIn{s}", (hc.x - hl * 0.2 + hl * 0.12, s * hw * 0.38, top + hh * 0.4), (hl * 0.14, hw * 0.22, hh * 0.75), inner,
                    top=(0.3, 0.3), rot=Rx(-s * 0.3), **NS)
          elif kind == "round":
              m.box(f"Ear{s}", (hc.x - hl * 0.15, s * hw * 0.36, top + hh * 0.1), (hl * 0.26, hw * 0.28, hh * 0.36), col, **NS)
              m.box(f"EarIn{s}", (hc.x - hl * 0.15 + hl * 0.12, s * hw * 0.36, top + hh * 0.08), (0.08, hw * 0.16, hh * 0.22), dk(col, 0.7), **NS)
          elif kind == "long":
              m.box(f"Ear{s}", (hc.x - hl * 0.2, s * hw * 0.24, top + hh * 0.62), (hl * 0.24, hw * 0.24, hh * 1.35), col,
                    top=(0.75, 0.8), rot=Ry(-0.12) @ Rx(-s * 0.12), **NS)
              m.box(f"EarIn{s}", (hc.x - hl * 0.2 + hl * 0.11, s * hw * 0.25, top + hh * 0.62), (0.06, hw * 0.13, hh * 1.0), inner,
                    rot=Ry(-0.12) @ Rx(-s * 0.12), **NS)
          elif kind == "floppy":
              m.box(f"Ear{s}", (hc.x - hl * 0.12, s * (hw / 2 + hw * 0.08), hc.z + hh * 0.1), (hl * 0.32, hw * 0.16, hh * 0.62), col,
                    rot=Rx(s * 0.45), **NS)
          elif kind == "big":
              m.box(f"Ear{s}", (hc.x - hl * 0.3, s * (hw / 2 + hw * 0.1), hc.z), (hl * 0.7, hw * 0.12, hh * 1.2), col, rot=Rz(s * 0.4), **NS)
          elif kind == "tiny":
              m.box(f"Ear{s}", (hc.x - hl * 0.2, s * hw * 0.34, top + hh * 0.06), (hl * 0.18, hw * 0.18, hh * 0.2), col, **NS)

def snout_block(m, c, P):
    hc, hl, hw, hh, C1 = c["hc"], c["hl"], c["hw"], c["hh"], c["C1"]
    sl, sw, sh = P.get("snout", (hl * 0.3, hw * 0.62, hh * 0.45))
    sc = Vector((c["xf"] + sl / 2 - 0.04, 0, hc.z - hh * 0.22))
    c.update(sc=sc, sl=sl, sw=sw, sh=sh)
    if sl <= 0: return
    scol = P.get("snout_c", C1)
    m.box("Snout", sc, (sl, sw, sh), scol, top=(0.92, 0.92), studs=sl > 0.5)
    ncol = P.get("nose_c", NOSE)
    if P.get("nostrils"):            # horses, camels, cattle-likes: two dark slits instead of a nose plate
        for s in (1, -1):
            m.box(f"Nostril{s}", sc + Vector((sl / 2 * 0.97, s * sw * 0.24, sh * 0.12)), (0.1, sw * 0.16, sh * 0.24), ncol, chamfer=0.1, **NS)
    else:
        m.box("Nose", sc + Vector((sl / 2, 0, sh * 0.2)), (0.1, sw * 0.42, sh * 0.32), ncol, chamfer=0.1, **NS)

# ============================================================================ tails / patterns
def tail(m, c, kind, col, tip=None):
    if not kind: return
    L, H, z0, W = c["L"], c["H"], c["z0"], c["W"]
    tb = Vector((-L / 2 + 0.15, 0, z0 + H * 0.18)); k = max(0.5, H / 1.6)
    end = tb
    if kind in ("short", "curly", "bushy", "tuft", "flat"):
        with m.bone("Tail1", tb):
            _tail_simple(m, kind, tb, k, col, tip, c)
        c["tail_bone"] = "Tail1"; return
    c["tail_bone"] = {"long": "Tail3", "up": "Tail3"}.get(kind, "Tail4")
    if False:
        pass
    elif kind == "short":
        m.box("Tail", tb + Vector((-0.2 * k, 0, 0.05)), (0.5 * k, 0.5 * k, 0.45 * k), col)
    elif kind == "curly":
        m.box("Tail", tb + Vector((-0.15 * k, 0, 0.1)), (0.35 * k, 0.25 * k, 0.35 * k), col, rot=Ry(0.6), **NS)
    elif kind == "long":
        pts = [tb, tb + Vector((-1.0, 0, -0.25)) * k, tb + Vector((-1.9, 0, -0.1)) * k, tb + Vector((-2.6, 0, 0.35)) * k]
        m.chain("Tail", pts, [0.38 * k, 0.3 * k, 0.24 * k, 0.16 * k], col, studs=False, bones="Tail"); end = pts[-1]
    elif kind == "bushy":
        m.box("Tail", tb + Vector((-0.75, 0, 0.35)) * k, (1.5 * k, 0.85 * k, 0.85 * k), col, rot=Ry(0.55), top=(0.8, 0.85))
        m.box("TailTip", tb + Vector((-1.55, 0, 0.92)) * k, (0.6 * k, 0.75 * k, 0.75 * k), tip or WHITE, rot=Ry(0.55), top=(0.6, 0.65)); end = tb + Vector((-1.7, 0, 1.0)) * k
    elif kind == "up":
        pts = [tb, tb + Vector((-0.5, 0, 0.6)) * k, tb + Vector((-0.75, 0, 1.6)) * k, tb + Vector((-0.4, 0, 2.3)) * k]
        m.chain("Tail", pts, [0.6 * k, 0.95 * k, 0.95 * k, 0.6 * k], col, bones="Tail"); end = pts[-1]
    elif kind == "tuft":
        a = tb + Vector((-0.1, 0, 0)); b = tb + Vector((-0.45, 0, -0.9)) * k
        m.seg("Tail", a, b, 0.2 * k, 0.16 * k, col, **NS)
        m.box("Tuft", b + Vector((-0.05, 0, -0.2 * k)), (0.38 * k, 0.38 * k, 0.55 * k), tip or dk(col, 0.6), top=(0.6, 0.6), **NS); end = b
    elif kind == "flat":
        m.box("Tail", tb + Vector((-0.9, 0, -0.45)) * k, (1.6 * k, 1.0 * k, 0.22 * k), tip or dk(col), **NS); end = tb + Vector((-1.7, 0, -0.45)) * k
    elif kind in ("thick", "dragon"):
        w = W * 0.55
        pts = [tb + Vector((0.3, 0, -0.1)), tb + Vector((-1.4, 0, -0.35)) * 1, tb + Vector((-2.8, 0, -0.45)), tb + Vector((-4.0, 0, -0.35)),
               tb + Vector((-5.0, 0, -0.1))]
        pts = [tb + (p - tb) * (k * 0.9) for p in pts]
        m.chain("Tail", pts, [w, w * 0.78, w * 0.55, w * 0.35, w * 0.16], col, bones="Tail"); end = pts[-1]
        if kind == "dragon":
          d = (pts[-1] - pts[-2]).normalized()
          with m.bone("Tail4"):
            m.slab("TailSpade", [(0, 0), (0.55 * k, 0.45 * k), (1.1 * k, 0), (0.55 * k, -0.45 * k)], 0.18 * k, tip or dk(col),
                   origin=end, xaxis=d, yaxis=(0, 1, 0))
    c["tail_end"] = end; c["tail_base"] = tb

def _tail_simple(m, kind, tb, k, col, tip, c):
    end = tb
    if kind == "short":
        m.box("Tail", tb + Vector((-0.2 * k, 0, 0.05)), (0.5 * k, 0.5 * k, 0.45 * k), col)
    elif kind == "curly":
        m.box("Tail", tb + Vector((-0.15 * k, 0, 0.1)), (0.35 * k, 0.25 * k, 0.35 * k), col, rot=Ry(0.6), **NS)
    elif kind == "bushy":
        m.box("Tail", tb + Vector((-0.75, 0, 0.35)) * k, (1.5 * k, 0.85 * k, 0.85 * k), col, rot=Ry(0.55), top=(0.8, 0.85))
        m.box("TailTip", tb + Vector((-1.55, 0, 0.92)) * k, (0.6 * k, 0.75 * k, 0.75 * k), tip or WHITE, rot=Ry(0.55), top=(0.6, 0.65)); end = tb + Vector((-1.7, 0, 1.0)) * k
    elif kind == "tuft":
        a = tb + Vector((-0.1, 0, 0)); b = tb + Vector((-0.45, 0, -0.9)) * k
        m.seg("Tail", a, b, 0.2 * k, 0.16 * k, col, **NS)
        m.box("Tuft", b + Vector((-0.05, 0, -0.2 * k)), (0.38 * k, 0.38 * k, 0.55 * k), tip or dk(col, 0.6), top=(0.6, 0.6), **NS); end = b
    elif kind == "flat":
        m.box("Tail", tb + Vector((-0.9, 0, -0.45)) * k, (1.6 * k, 1.0 * k, 0.22 * k), tip or dk(col), **NS); end = tb + Vector((-1.7, 0, -0.45)) * k
    c["tail_end"] = end; c["tail_base"] = tb

def pattern(m, c, kind, col, n=5, seed=1):
    if not kind: return
    L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]; rng = np.random.default_rng(seed)
    if kind == "stripes":
        for k in range(n):
            x = -L / 2 + L * (k + 0.75) / (n + 0.5)
            m.box(f"Stripe{k}", (x, 0, z0 + H * 0.1), (L * 0.06 + 0.12, W + 0.1, H * 0.86), col, rot=Ry(0.15 * (-1) ** k), **NS)
    elif kind in ("spots", "patches"):
        # chunky square-ish patches kept on the flat middle of the body sides + a few on the back (TFFA giraffe/cow)
        big = kind == "patches"; xs = np.linspace(-L * 0.3, L * 0.3, 3 if big else max(3, n // 2 + 1))
        k = 0
        for s in (1, -1):
            for i, x in enumerate(xs):
                w = L * (0.26 if big else 0.16) * rng.uniform(0.8, 1.15); h = H * (0.5 if big else 0.3) * rng.uniform(0.8, 1.15)
                z = z0 + H * (0.08 if (i + (s > 0)) % 2 else -0.15) * (0 if big else 1)
                m.box(f"Spot{k}", (x + rng.uniform(-0.1, 0.1) * L / 3, s * (W / 2 + 0.03), z), (w, 0.14, h), col, **NS); k += 1
        for i, x in enumerate(xs[::2] if not big else xs[1:2]):
            m.box(f"SpotT{i}", (x, rng.uniform(-W / 5, W / 5), z0 + H / 2 + 0.03), (L * (0.3 if big else 0.16), W * 0.32, 0.14), col, **NS)
    elif kind == "saddle":
        m.box("Saddle", (0, 0, z0 + H / 2 + 0.03), (L * 0.6, W * 0.8, 0.14), col, **NS)

# ============================================================================ archetypes
def quad(m, P):
    """Four-legged animal (cow template generalised). Bones: Body, Leg_FL/FR/BL/BR, Neck, Head, Ear_L/R, Tail1..n."""
    L, W, H = P["body"]; lh, lw = P["legs"]; lw *= 1.2
    C1 = P["c1"]; C2 = P.get("c2", dk(C1)); BEL = P.get("belly"); sprawl = P.get("sprawl", 0.0)
    z0 = lh + H / 2
    m.gait = dict(P.get("gait", {}))
    body = m.bone("Body", (0, 0, z0)); body.__enter__()
    m.box("Body", (0, 0, z0), (L, W, H), C1, top=(0.92, 1.0), bot=(0.96, 1.0))
    if BEL: m.box("Belly", (L * 0.04, 0, z0 - H * 0.3), (L * 0.84, W + 0.06, H * 0.42), BEL)
    legc = P.get("leg_c", C1); feet = P.get("feet")
    for sx in (1, -1):
        for s in (1, -1):
            x = sx * (L / 2 - lw * 0.62); y = s * (W / 2 - lw * 0.5)
            with m.bone(f"Leg_{'F' if sx > 0 else 'B'}{LR(s)}", (x, y, lh + 0.15)):
                if sprawl:
                    a = Vector((x, y, z0 - H * 0.15)); b = Vector((x + sx * 0.1, s * (W / 2 + sprawl * 1.6), 0.25))
                    m.seg(f"Leg{sx}{s}", a, b, lw, lw * 0.9, legc)
                    m.box(f"Foot{sx}{s}", (b.x + 0.15, b.y, 0.15), (lw * 1.4, lw * 1.2, 0.3), feet or legc, **NS)
                    for t in (-1, 0, 1): m.spike(f"Claw{sx}{s}{t}", (b.x + lw * 0.65, b.y + t * lw * 0.35, 0.12), (b.x + lw * 0.95, b.y + t * lw * 0.42, 0.05), lw * 0.12, CLAW)
                else:
                    m.box(f"Leg{sx}{s}", (x, y, (lh + 0.4) / 2), (lw, lw, lh + 0.4), legc)
                    if feet:
                        fh = min(0.4, lh * 0.28); m.box(f"Foot{sx}{s}", (x + 0.04, y, fh / 2), (lw * 1.1, lw * 1.1, fh), feet, **NS)
    # neck + head
    hl, hw, hh = P["head"]; nl, nt = P.get("neck", (0.2, 0.6))
    base = Vector((L / 2 - min(0.5, L * 0.15), 0, z0 + H * 0.15)); d = Vector((math.cos(nt), 0, math.sin(nt)))
    tipn = base + d * nl
    if nl > 0.15:
        with m.bone("Neck", base):
            m.seg("Neck", base - d * 0.45, tipn + d * 0.15, hw * 0.82, hw * 0.74, P.get("neck_c", C1), d0=hh * 1.05, d1=hh * 0.9)
    hc = tipn + Vector((hl * 0.28, 0, hh * 0.12))
    hscale = P.get("head_scale", HEAD_SCALE)
    m.bone("Head", tipn, "Neck" if nl > 0.15 else "Body")
    head = _ctx(lambda: m.frame(pivot=tipn, scale=hscale), lambda: m.bone("Head"))
    c = dict(L=L, W=W, H=H, lh=lh, lw=lw, z0=z0, hc=hc, hl=hl, hw=hw, hh=hh, xf=hc.x + hl / 2, C1=C1, C2=C2,
             head=head, back=Vector((0, 0, z0 + H / 2)), neck_base=base, neck_tip=tipn, nd=d)
    with head():
        m.box("Head", hc, (hl, hw, hh), P.get("head_c", C1), top=(0.92, 0.92))
        snout_block(m, c, P)
        long_face = c["sl"] > hl * 0.45 or P.get("side_eyes")
        (side_eyes if long_face else front_eyes)(m, c, P)
        ears(m, c, P.get("ears"), P.get("ear_c", P.get("head_c", C1)))
        if P.get("mane"):
            m.box("Mane", hc + Vector((-hl * 0.3, 0, 0.05)), (hl * 0.7, hw * 1.55, hh * 1.5), P["mane"], top=(0.8, 0.85))
    tail(m, c, P.get("tail"), P.get("tail_c", C1), P.get("tail_tip"))
    pattern(m, c, P.get("pattern"), P.get("pat_c", C2), P.get("pat_n", 5))
    for fn in P.get("x", []): fn(m, c)
    body.__exit__(None, None, None)
    return c

def bird(m, P):
    """Bird. Bones: Body, Neck, Head, Wing_L/R, Tail1, Leg_L/R. P['fly']=False for flightless birds."""
    L, W, H = P["body"]; lh = P.get("leg", 0.6); C1 = P["c1"]; up = P.get("upright", False)
    z0 = lh + H / 2
    m.gait = dict(P.get("gait", {}), fly=P.get("fly", True))
    body = m.bone("Body", (0, 0, z0)); body.__enter__()
    m.box("Body", (0, 0, z0), (L, W, H), C1, top=(0.78, 0.82), bot=(0.85, 0.88), rot=None if up else Ry(-0.12))
    if P.get("belly"):
        m.box("Belly", (L * 0.16, 0, z0 - H * 0.08), (L * 0.75, W * 0.86, H * 0.78), P["belly"], top=(0.8, 0.85), bot=(0.85, 0.9))
    hs = P["head"]; nk = P.get("neck", 0)
    hc = Vector((L * (0.12 if up else 0.36), 0, z0 + H / 2 + hs * 0.32 + nk))
    pivot = hc - Vector((0, 0, hs * 0.4))
    if nk > 0:
        with m.bone("Neck", (L * 0.32, 0, z0 + H * 0.2)):
            m.seg("Neck", (L * 0.32, 0, z0 + H * 0.2), hc - Vector((0, 0, hs * 0.3)), hs * 0.55, hs * 0.5, P.get("neck_c", C1))
    m.bone("Head", pivot, "Neck" if nk > 0 else "Body")
    head = _ctx(lambda: m.frame(pivot=pivot, scale=1.2), lambda: m.bone("Head"))
    c = dict(L=L, W=W, H=H, z0=z0, hc=hc, hl=hs, hw=hs * 0.95, hh=hs, xf=hc.x + hs / 2, C1=C1, C2=P.get("c2", dk(C1)),
             head=head, lh=lh, back=Vector((0, 0, z0 + H / 2)))
    with head():
        m.box("Head", hc, (hs, hs * 0.95, hs), P.get("head_c", C1), top=(0.88, 0.88))
        bl, bw, bh = P.get("beak", (hs * 0.42, hs * 0.36, hs * 0.26))
        bc = Vector((c["xf"] + bl / 2 - 0.03, 0, hc.z - hs * 0.12))
        m.box("Beak", bc, (bl, bw, bh), P.get("beak_c", ORANGE), top=P.get("beak_top", (0.55, 0.6)), bot=(1, 1), shift=(bl * 0.12 if P.get("beak_top") is None else 0, 0), **NS)
        if bl > hs * 0.8: m.box("BeakLow", bc + Vector((-bl * 0.1, 0, -bh * 0.45)), (bl * 0.75, bw * 0.85, bh * 0.4), dk(P.get("beak_c", ORANGE), 0.85), **NS)
        c.update(sc=bc, sl=bl, sw=bw, sh=bh)
        e = hs * 0.3 * P.get("eye", 1.0)
        m.eyes((c["xf"] + 0.01, max(hs * 0.2, e * 0.6), hc.z + hs * 0.16), size=(e, e), pupil=0.62, look=(0.3, -0.1),
               angry=0.32 if P.get("angry") else -0.05, white=P.get("iris", WHITE), brow_col=P.get("brow", _brow(P.get("head_c", C1))),
               brow_h=0.32, brow_up=0.66, depth=max(0.1, e * 0.2))
    wc = P.get("wing_c", P.get("c2", dk(C1, 0.85)))
    if P.get("spread"):
        feather_wings(m, c, wc, P.get("wing_c2", YELLOW), span=P.get("span", 1.0), glow=P.get("wing_glow", False))
    else:
        wl = P.get("wing", 0.75)
        for s in (1, -1):
            with m.bone(f"Wing_{LR(s)}", (L * 0.1, s * W * 0.42, z0 + H * 0.3)):
                m.box(f"Wing{s}", (-L * 0.06, s * (W / 2 * 0.9 + 0.08), z0 + H * 0.05), (L * wl, 0.22, H * 0.62), wc, top=(0.85, 1), bot=(0.6, 1),
                      rot=Rx(s * 0.06) @ Ry(0.12), **NS)
    tc = P.get("tail_c", wc)
    with m.bone("Tail1", (-L / 2 + 0.2, 0, z0 + H * 0.1)):
        for k in (-1, 0, 1):
            a = Vector((-L / 2 + 0.1, k * W * 0.18, z0 + H * (0.05 if up else 0.15)))
            dd = Vector((-1, k * 0.35, -0.5 if up else 0.35)).normalized()
            feather(m, f"TailF{k}", a, dd, L * 0.5, W * 0.28, (tc, tc, lt(tc, 0.15)) if not P.get("tail_glow") else (tc, tc, YELLOW), side=(0, 1, 0), glow=P.get("tail_glow", False))
    lc = P.get("leg_c", ORANGE)
    for s in (1, -1):
        y = s * W * 0.22
        with m.bone(f"Leg_{LR(s)}", (0.05, y, z0 - H * 0.3)):
            m.seg(f"Leg{s}", (0.05, y, z0 - H * 0.3), (0.12, y, 0.12), max(0.22, W * 0.13), max(0.18, W * 0.11), lc, **NS)
            for t in (-1, 0, 1):
                m.spike(f"Toe{s}{t}", (0.15, y + t * 0.12, 0.1), (0.15 + max(0.45, L * 0.22), y + t * 0.22, 0.05), max(0.09, W * 0.06), lc)
    for fn in P.get("x", []): fn(m, c)
    body.__exit__(None, None, None)
    return c

def ape(m, P):
    """Upright little biped (meerkat, monkey, sloth). Bones: Body, Head, Arm_L/R, Leg_L/R, Tail."""
    W, D, H = P["torso"]; lh = P.get("leg", 0.6); C1 = P["c1"]; lean = P.get("lean", 0.1)
    z0 = lh + H / 2; m.gait = dict(P.get("gait", {}))
    body = m.bone("Body", (0, 0, lh + H * 0.2)); body.__enter__()
    m.box("Torso", (0, 0, z0), (D, W, H), C1, top=(0.8, 0.85), rot=Ry(-lean))
    m.box("Tummy", (D * 0.42, 0, z0 - H * 0.08), (0.2, W * 0.62, H * 0.6), P.get("face_c", lt(C1, 0.35)), rot=Ry(-lean), **NS)
    hs = P["head"]; hc = Vector((D * 0.15 + math.sin(lean) * H * 0.5, 0, z0 + H / 2 + hs * 0.42))
    pivot = hc - Vector((0, 0, hs * 0.45)); m.bone("Head", pivot)
    head = _ctx(lambda: m.frame(pivot=pivot, scale=1.25), lambda: m.bone("Head"))
    c = dict(W=W, D=D, H=H, z0=z0, hc=hc, hl=hs, hw=hs, hh=hs * 0.95, xf=hc.x + hs / 2, C1=C1, C2=P.get("c2", dk(C1)), head=head,
             L=D, back=Vector((0, 0, z0 + H / 2)), lh=lh)
    with head():
        m.box("Head", hc, (hs, hs, hs * 0.95), P.get("head_c", C1), top=(0.9, 0.9))
        P2 = dict(P); P2.setdefault("snout", (hs * 0.28, hs * 0.6, hs * 0.38)); P2.setdefault("snout_c", P.get("face_c", lt(C1, 0.35)))
        snout_block(m, c, P2); front_eyes(m, c, P2, 1.05)
        ears(m, c, P.get("ears"), P.get("ear_c", C1))
    aw = P.get("arm_w", W * 0.28) * 1.2; al = P.get("arm", H * 0.9)
    for s in (1, -1):
        sh = Vector((D * 0.1, s * (W / 2 + aw * 0.35), z0 + H * 0.32)); hand = sh + Vector((al * 0.25, s * 0.1, -al))
        with m.bone(f"Arm_{LR(s)}", sh):
            m.seg(f"Arm{s}", sh, hand, aw, aw * 0.9, C1)
            m.box(f"Hand{s}", hand + Vector((0.05, 0, -aw * 0.2)), (aw * 1.25, aw * 1.1, aw * 0.8), P.get("face_c", lt(C1, 0.35)), **NS)
        with m.bone(f"Leg_{LR(s)}", (0, s * W * 0.26, lh + 0.1)):
            m.box(f"Leg{s}", (0, s * W * 0.26, (lh + 0.3) / 2), (aw * 1.15, aw * 1.15, lh + 0.3), C1)
            m.box(f"Foot{s}", (aw * 0.35, s * W * 0.26, 0.12), (aw * 1.7, aw * 1.15, 0.24), P.get("face_c", lt(C1, 0.35)), **NS)
    c["tail_end"] = None
    if P.get("tail"):
        c2 = dict(c, L=D, H=H * 0.6, z0=lh + H * 0.1, W=W); tail(m, c2, P["tail"], C1, P.get("tail_tip")); c["tail_end"] = c2.get("tail_end")
    for fn in P.get("x", []): fn(m, c)
    body.__exit__(None, None, None)
    return c

def theropod(m, P):
    """T-Rex family (the reviewed TRex example, scalable). Bones: Body, Neck, Head, Jaw, Tail1-4, Leg_L/R, Arm_L/R.
    P: s (scale, 1 = 17-stud TRex), snout (length factor), c1, c2, belly, iris, eye_glow."""
    s = P.get("s", 1.0); sn = P.get("snout", 1.0); m.gait = dict(P.get("gait", {}))
    G1, G2, BEL = P["c1"], P.get("c2", dk(P["c1"], 0.72)), P.get("belly", rgb(244, 240, 230))
    S = lambda x, y, z: Vector((x * s, y * s, z * s)); Z = lambda *a: tuple(v * s for v in a)
    body = m.bone("Body", S(0, 0, 5.0)); body.__enter__()
    m.box("Body", S(0, 0, 5.0), Z(5.4, 3.8, 3.8), G1, rot=Ry(-0.35), top=(0.85, 0.85))
    m.box("Belly", S(0.8, 0, 4.2), Z(3.6, 3.0, 2.6), BEL, rot=Ry(-0.45), **NS)
    m.chain("Tail", [S(-2.3, 0, 5.3), S(-4.4, 0, 5.4), S(-6.3, 0, 5.6), S(-8.0, 0, 6.0), S(-9.3, 0, 6.5)], [v * s for v in (3.0, 2.4, 1.8, 1.2, 0.6)], G1, bones="Tail")
    for t in (1, -1):
        with m.bone(f"Leg_{LR(t)}", S(-0.6, t * 1.9, 4.8)):
            m.box(f"Thigh{t}", S(-0.6, t * 1.9, 4.0), Z(2.8, 1.5, 3.4), G1, rot=Ry(0.25), top=(0.85, 0.9))
            m.seg(f"Shin{t}", S(-0.9, t * 2.0, 2.6), S(-0.3, t * 2.0, 0.7), 1.3 * s, 1.1 * s, G1)
            m.box(f"Foot{t}", S(0.3, t * 2.0, 0.4), Z(2.4, 1.6, 0.8), G2)
            for k in (-1, 0, 1): m.spike(f"Toe{t}{k}", S(1.4, t * 2.0 + k * 0.5, 0.3), S(1.9, t * 2.0 + k * 0.6, 0.12), 0.18 * s, CLAW)
        with m.bone(f"Arm_{LR(t)}", S(2.4, t * 1.5, 5.1)):
            m.seg(f"Arm{t}", S(2.4, t * 1.5, 5.1), S(3.0, t * 1.6, 4.3), 0.6 * s, 0.5 * s, G1, **NS)
            for k in (-1, 1): m.spike(f"ArmClaw{t}{k}", S(3.05, t * 1.6 + k * 0.15, 4.2), S(3.35, t * 1.6 + k * 0.18, 3.85), 0.1 * s, CLAW)
    H_ = S(3.2, 0, 7.5); ext = (sn - 1) * 3.0
    with m.bone("Neck", S(1.8, 0, 6.0)):
        m.seg("Neck", S(1.8, 0, 6.0), S(3.0, 0, 7.6), 3.0 * s, 2.6 * s, G1, d0=3.2 * s, d1=2.8 * s)
        m.box("Throat", S(3.4, 0, 6.5), Z(2.0, 2.6, 2.0), BEL, rot=Ry(0.2))
        m.box("MouthBack", S(3.9, 0, 7.5), Z(1.0, 2.0, 1.4), MOUTH, **NS)
    m.bone("Head", H_, "Neck")
    with m.bone("Head"), m.frame(pivot=H_, rot=Ry(-0.22)):
        m.box("Skull", S(3.9, 0, 8.6), Z(2.8, 3.0, 2.4), G1, top=(0.9, 0.9))
        m.box("Snout", S(6.2 + ext / 2, 0, 8.45), Z(3.6 + ext, 2.5, 1.8), G1, top=(0.92, 0.9))
        m.box("UpperGum", S(6.0 + ext / 2, 0, 7.5), Z(3.8 + ext, 2.2, 0.3), MOUTH, **NS)
        for k, x in enumerate((5.0, 6.0, 7.0)): m.box(f"Ridge{k}", S(x + ext * 0.5, 0, 9.45), Z(0.75, 1.7, 0.55), G1, **NS)
        xs = np.linspace(4.6, 7.7 + ext, int(5 + ext))
        for t in (1, -1):
            for k, x in enumerate(xs):
                L_ = 1.2 if k % 3 == 1 else 0.95
                m.spike(f"ToothU{t}{k}", S(x, t * 1.02, 7.45), S(x + 0.04, t * 0.98, 7.45 - L_), 0.42 * s, TOOTH, flat=0.3)
        m.box("EyeBase", S(4.2, 0, 9.0), Z(1.6, 3.4, 1.5), G1, **NS)
        m.eyes(S(4.3, 1.72, 9.0), facing=(0.25, 1, 0), size=Z(1.35, 1.25), pupil=0.72, look=(0, 0), angry=0.0,
               white=P.get("iris", WHITE), brow_col=G1, brow_h=0.42, brow_up=0.66, brow_w=1.3, depth=0.36 * s, glow_white=P.get("eye_glow", False))
        m.bone("Jaw", H_, "Head")
    with m.bone("Jaw"), m.frame(pivot=H_, rot=Ry(0.55)):
        m.box("Jaw", S(5.4 + ext / 2, 0, 6.75), Z(4.4 + ext, 2.3, 1.1), BEL, bot=(0.95, 0.9))
        m.box("Tongue", S(5.2, 0, 7.42), Z(3.6, 1.4, 0.3), TONGUE, **NS)
        m.box("LowerGum", S(5.4 + ext / 2, 0, 7.3), Z(4.2 + ext, 2.0, 0.2), MOUTH, **NS)
        for t in (1, -1):
            for k, x in enumerate(np.linspace(4.0, 7.2 + ext, int(6 + ext))):
                m.spike(f"ToothL{t}{k}", S(x, t * 0.95, 7.3), S(x - 0.04, t * 0.92, 7.95), 0.3 * s, TOOTH, flat=0.3)
    c = dict(s=s, S=S, Z=Z, G1=G1, G2=G2, C1=G1, back=S(0, 0, 7.0))
    for fn in P.get("x", []): fn(m, c)
    body.__exit__(None, None, None)
    return c

# ---------------------------------------------------------------------------- special bodies
def frog(m, P):
    C1, BEL = P["c1"], P.get("belly", rgb(240, 230, 120)); m.gait = {"hop": True}
    with m.bone("Body", (0, 0, 0.75)):
        m.box("Body", (0, 0, 0.75), (2.0, 1.9, 1.3), C1, top=(0.75, 0.8))
        m.box("Belly", (0.45, 0, 0.55), (1.3, 1.7, 0.9), BEL, **NS)
        m.box("Mouth", (1.0, 0, 0.72), (0.08, 1.4, 0.07), dk(C1, 0.45), **NS)
        for s in (1, -1):
            m.box(f"EyeBump{s}", (0.45, s * 0.55, 1.45), (0.75, 0.7, 0.6), C1)
            m.box(f"EyeW{s}", (0.83, s * 0.55, 1.5), (0.1, 0.55, 0.5), WHITE, **NS)
            m.box(f"Pupil{s}", (0.89, s * 0.5, 1.47), (0.08, 0.32, 0.32), PUPIL, **NS)
            with m.bone(f"Leg_B{LR(s)}", (-0.4, s * 0.9, 0.7)):
                m.box(f"Thigh{s}", (-0.55, s * 1.0, 0.45), (1.1, 0.55, 0.8), C1, top=(0.8, 0.9))
                m.box(f"BackFoot{s}", (-0.05, s * 1.1, 0.1), (1.0, 0.6, 0.2), dk(C1, 0.8), **NS)
            with m.bone(f"Leg_F{LR(s)}", (0.7, s * 0.7, 0.55)):
                m.box(f"FrontLeg{s}", (0.7, s * 0.7, 0.3), (0.3, 0.3, 0.6), C1, **NS)
                m.box(f"Hand{s}", (0.85, s * 0.75, 0.06), (0.5, 0.45, 0.12), dk(C1, 0.8), **NS)
    return dict(C1=C1, L=2.0, W=1.9, H=1.3, z0=0.75, back=Vector((0, 0, 1.4)))

def seal(m, P):
    C1, C2 = P["c1"], P.get("c2", dk(P["c1"])); s = P.get("s", 1.0)
    S = lambda x, y, z: Vector((x * s, y * s, z * s)); Z = lambda *a: tuple(v * s for v in a)
    body = m.bone("Body", S(0.8, 0, 0.75)); body.__enter__()
    segs = [(0.8, 1.7, 1.5), (-0.5, 1.5, 1.15), (-1.6, 1.05, 0.8), (-2.4, 0.65, 0.5)]
    for k, (x, w, h) in enumerate(segs):
        ctx = m.bone(f"Tail{k}", S(x + 0.65, 0, h / 2), "Body" if k == 1 else f"Tail{k - 1}") if k else nullcontext()
        with ctx:
            m.box(f"Body{k}", S(x, 0, h / 2), Z(1.5, w, h), C1, top=(0.85, 0.85))
            if k == 3:
                for t in (1, -1): m.box(f"TailFlip{t}", S(-3.0, t * 0.38, 0.14), Z(0.7, 0.6, 0.14), C2, rot=Rz(t * 0.6), **NS)
    hc = S(1.8, 0, 1.75); hl, hw, hh = 1.2 * s, 1.15 * s, 1.0 * s
    m.bone("Head", S(1.4, 0, 1.3))
    c = dict(hc=hc, hl=hl, hw=hw, hh=hh, xf=hc.x + hl / 2, C1=C1, C2=C2, head=lambda: m.bone("Head"), L=3.5 * s, W=1.7 * s, H=1.5 * s,
             z0=0.75 * s, back=S(0, 0, 1.5))
    with m.bone("Head"):
        m.box("Head", hc, (hl, hw, hh), C1, top=(0.88, 0.9))
        P2 = dict(P); P2.setdefault("snout", (0.4 * s, 0.85 * s, 0.5 * s)); P2.setdefault("snout_c", lt(C1, 0.35))
        snout_block(m, c, P2); front_eyes(m, c, P2, 1.1)
    for t in (1, -1):
        with m.bone(f"Fin_{LR(t)}", S(1.0, t * 0.7, 0.3)):
            m.box(f"Flipper{t}", S(1.0, t * 1.0, 0.18), Z(1.0, 0.6, 0.18), C2, rot=Rz(t * 0.45), **NS)
    for fn in P.get("x", []): fn(m, c)
    body.__exit__(None, None, None)
    return c

def snake(m, P):
    C1, C2 = P["c1"], P.get("c2", dk(P["c1"]))
    body = m.bone("Body", (0, 0, 0.4)); body.__enter__()
    for k in range(10):
        a = 2 * math.pi * k / 10; r = 1.35
        m.box(f"Coil{k}", (r * math.cos(a), r * math.sin(a), 0.4), (1.0, 0.85, 0.8), C1, rot=Rz(a + math.pi / 2))
        if k % 2 == 0: m.box(f"Diamond{k}", (r * math.cos(a), r * math.sin(a), 0.82), (0.5, 0.5, 0.1), C2, rot=Rz(a + math.pi / 4), **NS)
    for k in range(3): m.box(f"Rattle{k}", (-1.1 - 0.28 * k, -0.95, 0.6 + 0.32 * k), (0.32, 0.36, 0.28), rgb(220, 200, 150), **NS)
    m.chain("Neck", [(1.35, 0, 0.6), (0.9, 0.15, 1.5), (0.7, 0.05, 2.4), (0.95, 0, 2.9)], [0.85, 0.75, 0.7, 0.65], C1, bones="Neck")
    hc = Vector((1.35, 0, 3.05)); hl, hw, hh = 1.2, 1.0, 0.65
    m.bone("Head", (0.95, 0, 2.9), "Neck3")
    c = dict(hc=hc, hl=hl, hw=hw, hh=hh, xf=hc.x + hl / 2, C1=C1, C2=C2, head=lambda: m.bone("Head"), back=Vector((0, 0, 1.0)))
    with m.bone("Head"):
        m.box("Head", hc, (hl, hw, hh), C1, top=(0.85, 0.85))
        side_eyes(m, c, dict(P, angry=True, eye=1.25), fwd=0.2, up=0.3)
        m.box("Tongue", hc + Vector((hl / 2 + 0.25, 0, -0.1)), (0.5, 0.1, 0.05), MOUTH, **NS)
    for fn in P.get("x", []): fn(m, c)
    body.__exit__(None, None, None)
    return c

def scorpion(m, P):
    C1, C2 = P["c1"], P.get("c2", dk(P["c1"]))
    body = m.bone("Body", (0, 0, 0.7)); body.__enter__()
    m.box("Body", (0, 0, 0.7), (2.2, 1.6, 0.7), C1, top=(0.85, 0.8))
    m.bone("Head", (1.0, 0, 0.7))
    c = dict(hc=Vector((1.3, 0, 0.75)), hl=0.8, hw=1.3, hh=0.65, xf=1.7, C1=C1, C2=C2, head=lambda: m.bone("Head"), back=Vector((0, 0, 1.05)))
    with m.bone("Head"):
        m.box("Head", (1.3, 0, 0.75), (0.8, 1.3, 0.65), C1, top=(0.8, 0.85))
        front_eyes(m, c, dict(P, angry=True, eye=1.3))
    for s in (1, -1):
        for k in range(4):
            a = Vector((0.6 - 0.5 * k, s * 0.7, 0.6)); b = Vector((0.75 - 0.55 * k, s * 1.55, 0.05))
            with m.bone(f"Leg_{'F' if k < 2 else 'B'}{LR(s)}", (0.35 - 1.0 * (k >= 2), s * 0.7, 0.6)):
                m.seg(f"Leg{s}{k}", a, b, 0.18, 0.12, C2, **NS)
        with m.bone(f"Arm_{LR(s)}", (1.4, s * 0.6, 0.7)):
            m.seg(f"Arm{s}", (1.4, s * 0.6, 0.7), (2.2, s * 1.05, 0.75), 0.32, 0.28, C1, **NS)
            m.box(f"ClawA{s}", (2.55, s * 1.12, 0.78), (0.8, 0.42, 0.42), C1, top=(0.8, 0.8), **NS)
            m.spike(f"ClawB{s}", (2.5, s * 0.85, 0.75), (3.0, s * 0.78, 0.75), 0.15, C2)
    m.chain("Tail", [(-1.0, 0, 0.8), (-1.85, 0, 1.3), (-2.05, 0, 2.15), (-1.6, 0, 2.85), (-0.9, 0, 3.0)], [0.6, 0.55, 0.5, 0.45, 0.4], C1, bones="Tail")
    with m.bone("Tail4"): m.spike("Stinger", (-0.9, 0, 3.0), (-0.4, 0, 2.5), 0.22, BLACK)
    body.__exit__(None, None, None)
    return c

def blob(m, P):
    C1 = P["c1"]; L, W, H = P.get("size", (2.6, 2.0, 1.6)); m.gait = {"crawl": True}
    body = m.bone("Body", (0, 0, H * 0.3)); body.__enter__()
    m.box("Blob", (0, 0, H * 0.45), (L, W, H * 0.9), C1, top=(0.6, 0.7), bot=(1, 1), chamfer=0.25)
    m.box("Base", (0, 0, 0.12), (L * 1.05, W * 1.05, 0.24), dk(C1, 0.8), **NS)
    hc = Vector((L * 0.25, 0, H * 0.6))
    with m.bone("Head", hc):
        for k, y in enumerate(P.get("eye_y", (0.4, -0.4))):
            st = P.get("stalks", False); p = hc + Vector((L * 0.2, y * W / 2, 0.2 + (0.7 if st else 0)))
            if st: m.seg(f"Stalk{k}", hc + Vector((L * 0.15, y * W / 2, 0)), p, 0.18, 0.14, C1, **NS)
            m.box(f"EyeW{k}", p, (0.3, 0.5, 0.5), WHITE, **NS)
            m.box(f"Pupil{k}", p + Vector((0.12, 0, -0.03)), (0.1, 0.28, 0.3), PUPIL, **NS)
    c = dict(L=L, W=W, H=H, z0=H * 0.45, C1=C1, back=Vector((0, 0, H * 0.9)))
    for fn in P.get("x", []): fn(m, c)
    body.__exit__(None, None, None)
    return c

def golem(m, P):
    C1, C2, GL = P["c1"], P.get("c2", dk(P["c1"])), P.get("glowc", ORANGE)
    body = m.bone("Body", (0, 0, 2.6)); body.__enter__()
    m.box("Torso", (0, 0, 3.6), (2.0, 3.2, 2.8), C1, top=(0.85, 0.9), rot=Ry(-0.15))
    for k, (y, z, a) in enumerate([(0.6, 3.8, 0.4), (-0.5, 3.2, -0.6), (0.1, 4.4, 0.0), (-0.2, 2.6, 0.8)]):
        m.box(f"Crack{k}", (1.0, y, z), (0.1, 0.9, 0.16), GL, rot=Rx(a), glow=True, **NS)
    with m.bone("Head", (0.6, 0, 4.9)):
        m.box("Head", (0.7, 0, 5.4), (1.4, 1.5, 1.2), C2, top=(0.85, 0.85))
        m.box("Brow", (1.35, 0, 5.75), (0.3, 1.5, 0.35), C1, **NS)
        for s in (1, -1): m.box(f"Eye{s}", (1.42, s * 0.35, 5.45), (0.1, 0.38, 0.22), GL, glow=True, **NS)
    for s in (1, -1):
        with m.bone(f"Arm_{LR(s)}", (0.1, s * 2.0, 4.5)):
            m.box(f"Shoulder{s}", (0.1, s * 2.0, 4.5), (1.6, 1.4, 1.4), C2, top=(0.8, 0.85))
            m.seg(f"Arm{s}", (0.2, s * 2.1, 4.0), (0.9, s * 2.15, 1.6), 1.1, 1.2, C1)
            m.box(f"Fist{s}", (1.0, s * 2.15, 0.9), (1.5, 1.5, 1.4), C2)
        with m.bone(f"Leg_{LR(s)}", (-0.2, s * 0.9, 2.4)):
            m.box(f"Leg{s}", (-0.2, s * 0.9, 1.25), (1.2, 1.2, 2.5), C1)
            m.box(f"Foot{s}", (0.15, s * 0.9, 0.22), (1.7, 1.4, 0.44), C2, **NS)
    body.__exit__(None, None, None)
    return dict(C1=C1, back=Vector((0, 0, 5.0)))

def whale(m, P):
    C1, BEL = P["c1"], P.get("belly", lt(P["c1"], 0.5)); m.gait = {"crawl": True}
    body = m.bone("Body", (0.5, 0, 2.3)); body.__enter__()
    m.box("Body", (0, 0, 2.3), (7.0, 3.6, 3.4), C1, top=(0.85, 0.85))
    m.box("Belly", (1.0, 0, 1.0), (7.6, 3.2, 1.0), BEL)
    m.bone("Head", (3.2, 0, 2.2))
    c = dict(hc=Vector((4.0, 0, 2.6)), hl=1.8, hw=3.2, hh=2.6, xf=4.9, C1=C1, head=lambda: m.bone("Head"), back=Vector((0, 0, 4.0)), L=7, W=3.6, H=3.4, z0=2.3)
    with m.bone("Head"):
        m.box("Head", (4.0, 0, 2.2), (1.8, 3.2, 2.9), C1, top=(0.8, 0.85))
        side_eyes(m, c, dict(P, eye=0.7), fwd=0.0, up=0.0)
    with m.bone("Tail1", (-3.4, 0, 2.6)):
        m.box("TailStock", (-4.4, 0, 2.7), (2.0, 1.6, 1.4), C1)
        for s in (1, -1): m.box(f"Fluke{s}", (-5.6, s * 1.0, 2.9), (1.4, 2.0, 0.3), C1, rot=Rz(s * 0.35), top=(0.6, 1), **NS)
    for s in (1, -1):
        with m.bone(f"Fin_{LR(s)}", (2.0, s * 1.7, 1.3)):
            m.box(f"Fin{s}", (1.8, s * 2.3, 1.1), (1.7, 1.5, 0.28), C1, rot=Rx(s * 0.4), **NS)
    for fn in P.get("x", []): fn(m, c)
    body.__exit__(None, None, None)
    return c

def kraken(m, P):
    C1, C2 = P["c1"], P.get("c2", dk(P["c1"]))
    body = m.bone("Body", (0.3, 0, 2.5)); body.__enter__()
    m.box("Mantle", (-0.6, 0, 4.4), (2.6, 2.6, 3.4), C1, top=(0.45, 0.5), rot=Ry(0.3))
    m.box("Head", (0.5, 0, 2.5), (2.4, 2.8, 2.0), C1, top=(0.9, 0.9))
    c = dict(hc=Vector((0.5, 0, 2.5)), hl=2.4, hw=2.8, hh=2.0, xf=1.7, C1=C1, C2=C2, head=lambda: nullcontext(), back=Vector((0, 0, 5)))
    front_eyes(m, c, dict(P, angry=True, iris=rgb(255, 214, 60)))
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8; o = Vector((math.cos(a), math.sin(a), 0)); b = Vector((0.5, 0, 1.6)) + o * 0.9
        pts = [b, b + o * 1.0 + Vector((0, 0, -1.1)), b + o * 2.2 + Vector((0, 0, -1.4)), b + o * 3.0 + Vector((0, 0, -0.9)), b + o * 3.3 + Vector((0, 0, 0.0))]
        m.chain(f"Tent{k}", pts, [0.75, 0.6, 0.45, 0.32, 0.18], C1, bones=[f"Tent{k}_{j}" for j in range(4)])
        with m.bone(f"Tent{k}_1"): m.box(f"Sucker{k}", b + o * 2.2 + Vector((0, 0, -1.75)), (0.32, 0.32, 0.12), C2, **NS)
    body.__exit__(None, None, None)
    return c

# ============================================================================ accessories (factories -> fn(m, c))
def feather(m, name, root, direction, length, width, grad, side=(0, 1, 0), glow=False):
    d = Vector(direction).normalized(); sd = Vector(side); sd = (sd - d * sd.dot(d)).normalized()
    pts = [(0, 0), (width / 2, length * 0.18), (width * 0.42, length * 0.8), (0, length), (-width * 0.42, length * 0.8), (-width / 2, length * 0.18)]
    m.slab(name, pts, max(0.1, width * 0.2), grad[0], origin=root, xaxis=sd, yaxis=d, grad=grad, chamfer=0.3, glow=glow)

def feather_wings(m, c, col, tipc=None, span=1.0, glow=False, n=8):
    """Raised fan wings of blade feathers (phoenix/griffin/pegasus). Spread sideways + swept back so they read front and side."""
    W, H, z0, L = c["W"], c["H"], c["z0"], c["L"]; k = H * span; tipc = tipc or lt(col, 0.4)
    for s in (1, -1):
        sh = Vector((L * 0.1, s * W * 0.42, z0 + H * 0.3)); el = sh + Vector((-0.4, s * 0.55, 0.9)) * k; tp = el + Vector((-0.3, s * 0.3, 1.0)) * k
        wb = m.bone(f"Wing_{LR(s)}", sh, "Body"); wb.__enter__()
        m.seg(f"WingArm{s}", sh, el, 0.45 * k, 0.35 * k, col, studs=False)
        m.seg(f"WingHand{s}", el, tp, 0.35 * k, 0.2 * k, col, studs=False)
        for j in range(n):
            t = j / (n - 1); root = sh.lerp(el, t * 2) if t < 0.5 else el.lerp(tp, (t - 0.5) * 2)
            ang = 0.25 + t * 1.15
            d = (-0.8 * math.cos(ang), s * 0.6 * math.cos(ang), math.sin(ang))
            feather(m, f"Feather{s}{j}", root, d, (1.2 + 1.9 * t ** 0.8) * k, 0.38 * k, (dk(col, 0.9), col, tipc), side=(-0.8, s * 0.6, 0), glow=glow)
        wb.__exit__(None, None, None)

def wings(col, span=1.0, glow=False, membrane=None, kind="bat"):
    def fn(m, c):
        if kind == "feather": return feather_wings(m, c, col, membrane, span, glow)
        W, H, z0, L = c["W"], c["H"], c["z0"], c["L"]; k = H * span * 1.1; mem = membrane or dk(col, 0.65)
        for s in (1, -1):
            sh = Vector((L * 0.12, s * W * 0.42, z0 + H * 0.35)); wr = sh + Vector((-0.2, s * 0.6, 1.9)) * k
            tp = sh + Vector((-0.6, s * 2.0, 3.0)) * k
            wb = m.bone(f"Wing_{LR(s)}", sh, "Body"); wb.__enter__()
            m.seg(f"WingArm{s}", sh, wr, 0.32 * k, 0.26 * k, col, studs=False)
            m.seg(f"WingFinger{s}", wr, tp, 0.24 * k, 0.1 * k, col, studs=False)
            m.ball(f"WingKnob{s}", wr, 0.2 * k, lt(col, 0.3))
            pts = [sh, wr, tp, sh + Vector((-0.75, s * 2.4, 1.9)) * k, sh + Vector((-0.7, s * 2.1, 0.9)) * k, sh + Vector((-0.5, s * 1.2, 0.3)) * k,
                   sh + Vector((-0.4, s * 0.4, -0.1)) * k]
            pts = [sh] + [p for p in pts[1:]]
            m.poly(f"Wing{s}", pts, 0.12 * k, mem, glow=glow)
            for j, q in enumerate((sh + Vector((-0.73, s * 2.3, 1.4)) * k, sh + Vector((-0.6, s * 1.6, 0.6)) * k)):
                m.seg(f"WingBone{s}{j}", wr, q, 0.14 * k, 0.07 * k, col, studs=False)
            wb.__exit__(None, None, None)
    return fn

def horns(kind, col=HORN, glow=False):
    def fn(m, c):
        hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]; top = hc.z + hh / 2
        with c["head"]():
            for s in (1, -1):
                if kind == "cow": m.spike(f"Horn{s}", (hc.x - hl * 0.1, s * hw * 0.32, top - 0.05), (hc.x - hl * 0.15, s * hw * 0.62, top + hh * 0.45), hh * 0.12, col, sides=5)
                elif kind == "goat":
                    a = Vector((hc.x - hl * 0.05, s * hw * 0.25, top - 0.05)); b = a + Vector((-hl * 0.45, s * 0.08, hh * 0.5)); e = b + Vector((-hl * 0.35, s * 0.1, -hh * 0.15))
                    m.seg(f"Horn{s}", a, b, hh * 0.22, hh * 0.16, col, studs=False); m.spike(f"HornTip{s}", b, e, hh * 0.09, col)
                elif kind == "ossicone":
                    m.seg(f"Horn{s}", (hc.x - hl * 0.15, s * hw * 0.22, top - 0.05), (hc.x - hl * 0.2, s * hw * 0.25, top + hh * 0.45), hh * 0.14, hh * 0.12, col, studs=False)
                    m.box(f"HornKnob{s}", (hc.x - hl * 0.2, s * hw * 0.25, top + hh * 0.5), (hh * 0.24,) * 3, dk(col, 0.6), **NS)
                elif kind == "antler":
                    b = Vector((hc.x - hl * 0.15, s * hw * 0.25, top)); t1 = b + Vector((-0.1, s * 0.25, 0.9)) * hh
                    m.seg(f"Antler{s}", b, t1, hh * 0.13, hh * 0.1, col, studs=False)
                    for j, f_ in enumerate((0.45, 0.8)):
                        p = b.lerp(t1, f_); m.seg(f"Tine{s}{j}", p, p + Vector((0.28, s * 0.18, 0.32)) * hh, hh * 0.09, hh * 0.06, col, studs=False)
            if kind == "rhino":
                sc, sl, sh = c["sc"], c["sl"], c["sh"]
                m.spike("Horn", sc + Vector((sl * 0.25, 0, sh / 2 - 0.05)), sc + Vector((sl * 0.55, 0, sh / 2 + hh * 0.85)), hh * 0.22, col, sides=5)
                m.spike("Horn2", sc + Vector((-sl * 0.35, 0, sh / 2 + 0.05)), sc + Vector((-sl * 0.3, 0, sh / 2 + hh * 0.42)), hh * 0.13, col, sides=5)
            if kind == "unicorn":
                m.spike("Horn", (c["xf"] - hl * 0.15, 0, top - 0.05), (c["xf"] + hl * 0.1, 0, top + hh * 1.2), hh * 0.14, col, sides=6, glow=glow)
    return fn

def tusks(kind="walrus", col=HORN):
    def fn(m, c):
        sc, sl, sw, sh = c["sc"], c["sl"], c["sw"], c["sh"]
        with c["head"]():
            for s in (1, -1):
                if kind == "walrus": m.spike(f"Tusk{s}", sc + Vector((sl * 0.3, s * sw * 0.25, -sh * 0.3)), sc + Vector((sl * 0.25, s * sw * 0.28, -sh * 0.3 - c["hh"] * 0.9)), sw * 0.08, col, sides=5)
                elif kind == "up": m.spike(f"Tusk{s}", sc + Vector((sl * 0.3, s * sw * 0.48, -sh * 0.2)), sc + Vector((sl * 0.25, s * sw * 0.62, sh * 0.85)), sw * 0.08, col, sides=5)
                elif kind == "mammoth":
                    a = sc + Vector((0, s * sw * 0.42, -sh * 0.3)); b = a + Vector((c["hl"] * 0.7, s * 0.2, -c["hh"] * 0.45)); e = b + Vector((c["hl"] * 0.5, -s * 0.1, c["hh"] * 0.55))
                    m.seg(f"Tusk{s}", a, b, sw * 0.16, sw * 0.13, col, studs=False); m.spike(f"TuskTip{s}", b, e, sw * 0.07, col, sides=5)
    return fn

def trunk(col):
    def fn(m, c):
        sc, sl, sw, sh = c["sc"], c["sl"], c["sw"], c["sh"]
        with c["head"]():
            a = sc + Vector((sl / 2, 0, 0)); pts = [a, a + Vector((0.3, 0, -0.7)) * c["hh"], a + Vector((0.4, 0, -1.4)) * c["hh"], a + Vector((0.65, 0, -1.75)) * c["hh"]]
            m.chain("Trunk", pts, [sw * 0.5, sw * 0.42, sw * 0.34, sw * 0.28], col)
    return fn

def mane_back(col, n=5):
    def fn(m, c):
        if "neck_tip" not in c: return
        a, b = c["neck_base"], c["neck_tip"]; d = c["nd"]; up = Vector((-d.z, 0, d.x))
        with _in(m, "Neck"):
          for k in range(n):
            p = a.lerp(b, k / max(1, n - 1)) + up * c["hh"] * 0.55
            m.box(f"Mane{k}", p, (c["hl"] * 0.42, c["hw"] * 0.42, c["hh"] * 0.8), col, rot=Ry(-0.5), top=(0.55, 0.8), **NS)
        with c["head"]():                                  # forelock tuft on top of the head
            m.box("Forelock", c["hc"] + Vector((-c["hl"] * 0.2, 0, c["hh"] * 0.55)), (c["hl"] * 0.45, c["hw"] * 0.42, c["hh"] * 0.4), col, top=(0.6, 0.8), **NS)
    return fn

def beard(col):
    def fn(m, c):
        with c["head"](): m.box("Beard", c["sc"] + Vector((-c["sl"] * 0.05, 0, -c["sh"] * 0.5 - c["hh"] * 0.2)), (max(c["sl"], c["hl"] * 0.3) * 0.7, c["sw"] * 0.4, c["hh"] * 0.45), col, top=(1, 1), bot=(0.35, 0.4), **NS)
    return fn

def wool(col=WHITE):
    def fn(m, c):
        L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
        for k, (x, z) in enumerate([(-0.3, 0.25), (0.3, 0.2), (0, 0.4), (-0.35, -0.1), (0.35, -0.1)]):
            m.box(f"Wool{k}", (x * L, 0, z0 + z * H), (L * 0.55, W * 1.12, H * 0.75), col, top=(0.85, 0.9))
    return fn

def mask(col=BLACK):
    def fn(m, c):
        with c["head"](): m.box("Mask", (c["xf"] - 0.02, 0, c["hc"].z + c["hh"] * 0.12), (0.12, c["hw"] * 1.02, c["hh"] * 0.42), col, **NS)
    return fn

def eye_patches(col):
    def fn(m, c):
        with c["head"]():
            for s in (1, -1):
                m.box(f"EyePatch{s}", (c["xf"] - 0.02, s * c["hw"] * 0.24, c["hc"].z + c["hh"] * 0.08), (0.1, c["hw"] * 0.36, c["hh"] * 0.5), col, rot=Rx(-s * 0.3), **NS)
    return fn

def hump(n=1, col=None):
    def fn(m, c):
        L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
        for k in range(n):
            x = 0 if n == 1 else (-0.2 + 0.4 * k) * L
            m.box(f"Hump{k}", (x, 0, z0 + H / 2 + H * 0.22), (L * 0.32, W * 0.7, H * 0.6), col or c["C1"], top=(0.5, 0.6))
    return fn

def shell(col, spot=None, spikes=False):
    def fn(m, c):
        L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
        m.box("Shell", (0, 0, z0 + H * 0.25), (L * 1.08, W * 1.1, H * 1.0), col, top=(0.72, 0.72))
        if spot:
            for k, (x, y) in enumerate([(-0.25, 0), (0.15, 0), (0, 0.25), (0, -0.25), (-0.1, 0.0)][:4]):
                m.box(f"ShellSpot{k}", (x * L, y * W, z0 + H * 0.77), (L * 0.18, W * 0.18, 0.12), spot, **NS)
        if spikes:
            for k in range(5):
                for s in (1, -1):
                    x = -L * 0.4 + L * 0.2 * k
                    m.spike(f"ShellSpike{k}{s}", (x, s * W * 0.5, z0 + H * 0.35), (x, s * W * 0.82, z0 + H * 0.5), H * 0.14, lt(col, 0.4))
    return fn

def club_tail(col):
    def fn(m, c):
        e = c.get("tail_end")
        if e is not None:
            with _in(m, c.get("tail_bone", "Tail4")): m.box("Club", e + Vector((-0.3, 0, 0)), (1.0, 1.1, 0.75), col, top=(0.7, 0.75))
    return fn

def plates(col, n=7):
    def fn(m, c):
        L, H, z0 = c["L"], c["H"], c["z0"]
        for k in range(n):
            x = L * 0.4 - L * 1.0 * k / (n - 1); h = H * (0.55 + 0.5 * math.sin(math.pi * (k + 0.5) / n))
            for s in (1, -1):
                m.slab(f"Plate{k}{s}", [(0, 0), (h * 0.45, h * 0.5), (0, h), (-h * 0.45, h * 0.5)], 0.18, col,
                       origin=(x + s * 0.18, s * 0.22, z0 + H * 0.38), xaxis=(1, 0, 0), yaxis=(0, s * 0.25, 1))
    return fn

def frill(col, hcol=HORN):
    def fn(m, c):
        hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
        with c["head"]():
            r = hh * 1.05
            pts = [(r * math.cos(a), r * math.sin(a) * 0.95) for a in np.linspace(-0.25, math.pi + 0.25, 9)] + [(-r * 0.7, -r * 0.3), (r * 0.7, -r * 0.3)]
            pts = pts[:9] + [(-r * 0.75, -r * 0.35), (r * 0.75, -r * 0.35)][::-1]
            m.slab("Frill", pts, 0.25, col, origin=hc + Vector((-hl * 0.45, 0, hh * 0.35)), xaxis=(0, 1, 0), yaxis=(-0.35, 0, 1))
            for s in (1, -1):
                m.spike(f"BrowHorn{s}", hc + Vector((hl * 0.05, s * hw * 0.28, hh * 0.45)), hc + Vector((hl * 0.9, s * hw * 0.35, hh * 1.25)), hh * 0.14, hcol, sides=5)
            m.spike("NoseHorn", c["sc"] + Vector((c["sl"] * 0.2, 0, c["sh"] / 2 - 0.05)), c["sc"] + Vector((c["sl"] * 0.45, 0, c["sh"] / 2 + hh * 0.45)), hh * 0.12, hcol, sides=5)
    return fn

def crest(col):
    def fn(m, c):
        hc, hl, hh = c["hc"], c["hl"], c["hh"]
        with c["head"](): m.seg("Crest", hc + Vector((0, 0, hh * 0.3)), hc + Vector((-hl * 1.6, 0, hh * 1.2)), hh * 0.38, hh * 0.25, col, studs=False)
    return fn

def sail(col, glow=False):
    def fn(m, c):
        b = c["back"]; S = c.get("s", 1.0) * 1.0
        pts = [(-4.2, 0), (-3.4, 2.2), (-2.4, 3.0), (-1.2, 3.4), (0.0, 3.2), (1.0, 2.6), (1.8, 1.2), (2.2, 0)]
        k = c["s"] * 1.0 if "s" in c else 1.0
        m.slab("Sail", [(x * k, y * k) for x, y in pts], 0.22 * k, col, origin=b + Vector((0.6, 0, -0.6)) * 1, xaxis=(1, 0, -0.15), yaxis=(0, 0, 1), glow=glow)
    return fn

def spine_spikes(col, n=6, glow=False):
    def fn(m, c):
        if "L" not in c: return
        L, H, z0 = c["L"], c["H"], c["z0"]
        for k in range(n):
            x = L * 0.35 - L * 0.9 * k / max(1, n - 1)
            m.spike(f"Spine{k}", (x, 0, z0 + H / 2 - 0.05), (x - H * 0.15, 0, z0 + H / 2 + H * 0.42), H * 0.13, col, flat=0.45, glow=glow)
    return fn

def hedgehog_spikes(col):
    def fn(m, c):
        L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
        m.box("Quills", (-L * 0.08, 0, z0 + H * 0.2), (L * 0.95, W * 1.12, H * 1.0), col, top=(0.7, 0.75))
        for i in range(5):
            for j in range(-2, 3):
                x = L * 0.3 - i * L * 0.18; y = j * W * 0.22
                m.spike(f"Quill{i}{j}", (x, y, z0 + H * 0.65 - abs(j) * 0.1), (x - 0.35, y * 1.5, z0 + H * 1.1 - abs(j) * 0.2), 0.14, lt(col, 0.25))
    return fn

def fangs(col=TOOTH):
    def fn(m, c):
        sc, sl, sw, sh = c["sc"], c["sl"], c["sw"], c["sh"]
        with c["head"]():
            for s in (1, -1): m.spike(f"Fang{s}", sc + Vector((sl * 0.35, s * sw * 0.3, -sh * 0.4)), sc + Vector((sl * 0.38, s * sw * 0.3, -sh * 0.4 - c["hh"] * 0.45)), sw * 0.1, col, flat=0.5)
    return fn

def buck_teeth(col=WHITE):
    def fn(m, c):
        sc, sl, sw, sh = c["sc"], c["sl"], c["sw"], c["sh"]
        with c["head"]():
            for s in (1, -1): m.box(f"Tooth{s}", sc + Vector((sl / 2 - 0.02, s * sw * 0.11, -sh * 0.62)), (0.08, sw * 0.2, sh * 0.5), col, **NS)
    return fn

def fur_coat(col, n=6):
    def fn(m, c):
        L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
        for k in range(n):
            x = L * 0.42 - L * 0.84 * k / (n - 1)
            for s in (1, -1): m.box(f"Fur{k}{s}", (x, s * (W / 2 + 0.05), z0 - H * 0.35), (L / n * 1.1, 0.3, H * 0.55), col, top=(1, 1), bot=(0.6, 1))
    return fn

def glow_bits(col, n=8, seed=3, where="body", size=0.35):
    def fn(m, c):
        rng = np.random.default_rng(seed)
        L, W, H, z0 = c.get("L", 2), c.get("W", 1.5), c.get("H", 1.5), c.get("z0", 1)
        for k in range(n):
            if where == "top":
                m.box(f"Glow{k}", (rng.uniform(-L / 3, L / 3), rng.uniform(-W / 3, W / 3), z0 + H / 2 + 0.03), (size, size, 0.1), col, glow=True, **NS)
            else:
                s = 1 if k % 2 else -1
                m.box(f"Glow{k}", (rng.uniform(-L / 2.6, L / 2.6), s * (W / 2 + 0.03), z0 + rng.uniform(-H / 4, H / 3)), (size, 0.1, size), col, glow=True, **NS)
    return fn

def flame_mane(col):
    def fn(m, c):
        a, b = c["neck_base"], c["neck_tip"]
        with _in(m, "Neck"):
          for k in range(6):
            p = a.lerp(b, k / 5) + Vector((-0.2, 0, c["hh"] * 0.45))
            m.spike(f"Flame{k}", p, p + Vector((-0.6, 0, 0.9 + 0.3 * (k % 2))), 0.28, col, glow=True)
        for k in range(4):
            p = Vector((c["L"] * (0.3 - 0.22 * k), 0, c["z0"] + c["H"] / 2))
            m.spike(f"BackFlame{k}", p, p + Vector((-0.5, 0, 0.7)), 0.22, col, glow=True)
    return fn

def headdress(gold=GOLD, blue=BLUE):
    def fn(m, c):
        hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
        with c["head"]():
            m.box("Nemes", hc + Vector((-hl * 0.08, 0, hh * 0.32)), (hl * 1.05, hw * 1.12, hh * 0.45), gold, **NS)
            for k in range(3): m.box(f"NemesStripe{k}", hc + Vector((-hl * 0.08, 0, hh * (0.18 + 0.15 * k))), (hl * 1.08, hw * 1.15, hh * 0.06), blue, **NS)
            for s in (1, -1): m.box(f"Lappet{s}", hc + Vector((-hl * 0.1, s * hw * 0.58, -hh * 0.3)), (hl * 0.5, 0.18, hh * 1.0), gold, **NS)
            m.box("Uraeus", (c["xf"], 0, hc.z + hh * 0.62), (0.18, 0.22, 0.35), blue, **NS)
    return fn

def astro(suit=WHITE, accent=ORANGE):
    def fn(m, c):
        hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
        with c["head"]():
            m.box("HelmetRing", hc + Vector((-hl * 0.1, 0, -hh * 0.5)), (hl * 1.25, hw * 1.25, hh * 0.25), suit)
            m.seg("Antenna", hc + Vector((-hl * 0.2, hw * 0.25, hh * 0.5)), hc + Vector((-hl * 0.3, hw * 0.3, hh * 1.2)), 0.1, 0.08, LGREY, studs=False)
            m.box("AntennaTip", hc + Vector((-hl * 0.3, hw * 0.3, hh * 1.25)), (0.25, 0.25, 0.25), accent, glow=True, **NS)
        L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
        m.box("Pack", (-L * 0.05, 0, z0 + H / 2 + 0.3), (L * 0.42, W * 0.7, 0.6), suit)
        m.box("PackLight", (-L * 0.05 + L * 0.21, 0, z0 + H / 2 + 0.35), (0.1, W * 0.4, 0.2), accent, glow=True, **NS)
    return fn

def hole_ring(col):
    def fn(m, c):
        b = Vector((-c["L"] * 0.1, 0, c["z0"] + c["H"] * 0.9)); R = c["H"] * 0.9
        for k in range(12):
            a = 2 * math.pi * k / 12; p = b + Vector((0, R * math.cos(a), R * math.sin(a) * 0.5 + R * 0.6))
            m.box(f"Ring{k}", p, (0.3, 0.55, 0.3), col, rot=Rx(a), glow=True, **NS)
    return fn

def chimera_bits(goat=rgb(236, 228, 210), snake_c=rgb(80, 170, 70)):
    def fn(m, c):
        L, W, H, z0 = c["L"], c["W"], c["H"], c["z0"]
        p = Vector((-L * 0.05, 0, z0 + H / 2))
        m.seg("GoatNeck", p, p + Vector((0.2, 0, 1.0)), 0.6, 0.55, goat)
        gh = p + Vector((0.4, 0, 1.4)); m.box("GoatHead", gh, (0.9, 0.75, 0.75), goat)
        for s in (1, -1):
            m.seg(f"GoatHorn{s}", gh + Vector((-0.1, s * 0.2, 0.35)), gh + Vector((-0.6, s * 0.3, 0.9)), 0.18, 0.1, HORN, studs=False)
            m.box(f"GoatEye{s}", gh + Vector((0.2, s * 0.38, 0.1)), (0.22, 0.05, 0.18), WHITE, **NS)
        e = c.get("tail_end")
        if e is not None:
          with _in(m, c.get("tail_bone", "Tail3")):
            m.box("SnakeHead", e + Vector((-0.25, 0, 0.25)), (0.7, 0.5, 0.4), snake_c)
            for s in (1, -1): m.box(f"SnakeEye{s}", e + Vector((-0.1, s * 0.26, 0.32)), (0.18, 0.05, 0.14), rgb(255, 214, 60), **NS)
    return fn

def whiskers(col=rgb(240, 236, 220)):
    def fn(m, c):
        sc, sl, sw, sh = c["sc"], c["sl"], c["sw"], c["sh"]
        with c["head"]():
            for s in (1, -1):
                for k in (-1, 1):
                    m.box(f"Whisker{s}{k}", sc + Vector((sl * 0.2, s * (sw / 2 + 0.35), k * sh * 0.15)), (0.06, 0.8, 0.06), col, rot=Rx(s * k * 0.15), **NS)
    return fn

def crescent(col):
    def fn(m, c):
        hc, hh = c["hc"], c["hh"]
        with c["head"]():
            pts = [(math.cos(a) * 0.45, math.sin(a) * 0.45) for a in np.linspace(0.5, 5.8, 9)] + [(math.cos(a) * 0.28 + 0.12, math.sin(a) * 0.28) for a in np.linspace(5.4, 0.9, 7)]
            m.slab("Crescent", pts, 0.1, col, origin=(c["xf"] + 0.06, 0, hc.z + hh * 0.42), xaxis=(0, 1, 0), yaxis=(0, 0, 1), glow=True)
    return fn

def talons(col=rgb(250, 210, 60)):
    def fn(m, c):
        for sx in (1, -1):
            for s in (1, -1):
                x = sx * (c["L"] / 2 - c["lw"] * 0.62); y = s * (c["W"] / 2 - c["lw"] * 0.5)
                with _in(m, f"Leg_{'F' if sx > 0 else 'B'}{LR(s)}"):
                  for t in (-1, 0, 1): m.spike(f"Talon{sx}{s}{t}", (x + c["lw"] * 0.45, y + t * c["lw"] * 0.3, 0.12), (x + c["lw"] * 0.85, y + t * c["lw"] * 0.38, 0.03), c["lw"] * 0.12, CLAW)
    return fn

def beak_head(col=rgb(250, 200, 50)):
    def fn(m, c):
        sc, sl, sw, sh = c["sc"], c["sl"], c["sw"], c["sh"]
        with c["head"](): m.spike("BeakHook", sc + Vector((sl * 0.35, 0, sh * 0.2)), sc + Vector((sl * 0.75, 0, -sh * 0.65)), sw * 0.3, col, flat=0.6)
    return fn

def comb(col=RED):
    def fn(m, c):
        hc, hl, hh = c["hc"], c["hl"], c["hh"]
        with c["head"]():
            for k in range(3): m.box(f"Comb{k}", hc + Vector((hl * (0.25 - 0.22 * k), 0, hh * 0.55 + 0.1 * (k == 1))), (hl * 0.2, hl * 0.12, hh * 0.32), col, **NS)
            m.box("Wattle", c["sc"] + Vector((-0.05, 0, -c["sh"] * 0.75)), (c["sl"] * 0.4, c["sw"] * 0.35, hh * 0.25), col, **NS)
    return fn

def tufts(col):
    def fn(m, c):
        hc, hl, hw, hh = c["hc"], c["hl"], c["hw"], c["hh"]
        with c["head"]():
            for s in (1, -1): m.box(f"Tuft{s}", hc + Vector((0, s * hw * 0.36, hh * 0.62)), (hl * 0.3, hw * 0.2, hh * 0.45), col, top=(0.3, 0.4), rot=Rx(-s * 0.25), **NS)
    return fn

def bill_tip(col=BLACK):
    def fn(m, c):
        with c["head"](): m.box("BillTip", c["sc"] + Vector((c["sl"] * 0.4, 0, 0)), (c["sl"] * 0.2, c["sw"] * 0.75, c["sh"] * 0.95), col, **NS)
    return fn

def ruff(col=WHITE):
    def fn(m, c):
        hc, hs = c["hc"], c["hh"]
        m.box("Ruff", hc + Vector((-hs * 0.3, 0, -hs * 0.75)), (hs * 1.2, hs * 1.3, hs * 0.5), col, top=(0.8, 0.85))
    return fn

def rex_cracks(col):
    def fn(m, c):
        S = c["S"]; s = c["s"]
        for k, (x, z, a) in enumerate([(1.0, 4.6, 0.5), (-0.4, 4.4, -0.4), (-2.6, 4.9, 0.3), (-4.6, 5.0, -0.5), (0.4, 5.8, 0.1)]):
            for t in (1, -1): m.box(f"Crack{k}{t}", S(x, t * 1.95, z), (1.3 * s, 0.1, 0.2 * s), col, rot=Ry(a), glow=True, **NS)
    return fn

# ============================================================================ build driver
def build(name, arch, P, out, views=None):
    """Build one animal from an archetype + spec into folder `out` (old contents are replaced)."""
    if os.path.isdir(out): shutil.rmtree(out)
    size = max(P.get("body", P.get("torso", P.get("size", (3, 2, 2))))) if P else 3
    if arch is theropod: size = 9 * P.get("s", 1.0) / G
    if arch in (whale, golem, kraken): size = 5
    stud = float(np.clip(size * G / 12, 0.26, 0.6))
    m = Model(name, out, stud=stud, chamfer=0.16, jitter=P.get("jitter", 0.05))
    with m.frame(scale=1.0 if arch is theropod else G):
        c = arch(m, P)
    m.done(glow_color=P.get("glow"), views=views or [("hero", 40, 12, 45)])
    return m
