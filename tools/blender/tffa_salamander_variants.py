"""4 FireSalamander full-body design variations for user feedback (TFFA kit, rigged). v1 was "very rough".

usage: /tmp/bpyenv/bin/python tools/blender/tffa_salamander_variants.py [Name ...]     then: python3 ... --sheet
Writes models/TFFA/SalamanderVariants/<Name>/ and Salamander_variants.png (rows = variants; hero, front, side)."""
import os, sys, subprocess, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tffa-animal-models", "scripts"))
OUT = os.path.join(ROOT, "models", "TFFA", "SalamanderVariants")
VIEWS = [("hero", 40, 18, 45), ("front", 0, 12, 45), ("side", 90, 8, 45)]
LR = lambda s: "L" if s > 0 else "R"

def K():
    import tffa_kit as T
    from mathutils import Vector
    return T, Vector

# ============================================================================ shared parts
def flame(m, T, V, name, base, d, L, w, cols, front=(1, 0, 0), flat=0.55):
    """Three-layer fanned flame: cols = (outer, mid, glowing core)."""
    d = V(d).normalized(); f = V(front); f = f - d * f.dot(d); f = f.normalized() if f.length > 1e-3 else V((0, 0, 1))
    m.spike(f"{name}R", base, base + d * L, w, cols[0], flat=flat)
    m.spike(f"{name}O", base + f * w * 0.45, base + f * w * 0.3 + d * L * 0.8, w * 0.8, cols[1], flat=flat)
    m.spike(f"{name}Y", base + f * w * 0.85, base + f * w * 0.6 + d * L * 0.55, w * 0.55, cols[2], flat=flat, glow=True)

def blob(m, T, name, p, r, col, up=(0, 0, 1), glow=False):
    """Rounded blotch: two overlapping squares (one turned 45 deg) = an octagon, never a square sticker."""
    from mathutils import Vector, Matrix
    n = Vector(up).normalized(); tx = Vector((0, 0, 1)).cross(n); tx = tx.normalized() if tx.length > 0.01 else Vector((1, 0, 0)); ty = n.cross(tx)
    R = Matrix((tx, ty, n)).transposed()
    m.box(f"{name}a", p, (r, r, 0.08), col, rot=R, studs=False, glow=glow)
    m.box(f"{name}b", p + n * 0.005, (r, r, 0.08), col, rot=R @ T.Rz(0.785), studs=False, glow=glow)

def spine_body(m, T, V, name, pts, ws, ds, col, belly=None, studs=True):
    """Smooth continuous body: overlapping tapered segs along a curving spine (+ optional belly keel)."""
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; d = (b - a).normalized()
        m.seg(f"{name}{i}", a - d * 0.25, b + d * 0.25, ws[i], ws[i + 1], col, d0=ds[i], d1=ds[i + 1], up=(0, 0, 1) if abs(d.z) > 0.9 else None, studs=studs)
        if belly:
            m.seg(f"{name}Belly{i}", a - d * 0.2 + V((0, 0, -ds[i] * 0.36)), b + d * 0.2 + V((0, 0, -ds[i + 1] * 0.36)), ws[i] * 0.84, ws[i + 1] * 0.84,
                  belly, d0=ds[i] * 0.34, d1=ds[i + 1] * 0.34, studs=False)

def newt_legs(m, T, V, spec, col, pad, thick=1.0, glow_pad=False):
    """spec: list of (fb, x, y_centre, fwd). Sprawling legs: out, down, rounded hand with four splayed toes."""
    for fb, x, yc, fwd in spec:
        for s in (1, -1):
            hip = V((x, yc + s * 0.75, 0.95))
            with m.bone(f"Leg_{fb}{LR(s)}", hip):
                knee = hip + V((0.2 * fwd, s * 0.95, 0.3)); foot = knee + V((0.25 * fwd, s * 0.25, -1.0))
                m.seg(f"Up{fb}{s}", hip, knee, 0.78 * thick, 0.66 * thick, col)
                m.seg(f"Lo{fb}{s}", knee, foot, 0.64 * thick, 0.54 * thick, col)
                m.box(f"Hand{fb}{s}", foot + V((0.12 * fwd, 0, 0.12)), (0.75 * thick, 0.75 * thick, 0.26), col, top=(0.8, 0.8), studs=False)
                for k, t in enumerate((-1.5, -0.5, 0.5, 1.5)):
                    ang = (0 if fwd > 0 else math.pi) + s * (0.35 + t * 0.32) * (1 if fwd > 0 else -1)
                    dd = V((math.cos(ang), math.sin(ang), 0))
                    q = foot + V((0.12 * fwd, 0, 0.1)) + dd * 0.5 * thick
                    m.box(f"Toe{fb}{s}{k}", q, (0.42 * thick, 0.16 * thick, 0.14), col, rot=T.Rz(ang), studs=False)
                    m.box(f"Pad{fb}{s}{k}", q + dd * 0.22 * thick, (0.2 * thick, 0.22 * thick, 0.16), pad, rot=T.Rz(ang), studs=False, glow=glow_pad)

def round_head(m, T, V, hc, col, size, belly=None):
    """Rounded amphibian head: core block + dome + soft snout + cheeks (no single flat brick)."""
    L, W, H = size
    m.box("HeadCore", hc, (L, W, H), col, top=(0.86, 0.88), bot=(0.9, 0.9))
    m.box("HeadDome", hc + V((-0.1, 0, H * 0.5)), (L * 0.75, W * 0.78, H * 0.35), col, top=(0.7, 0.75))
    m.box("Snout", hc + V((L * 0.5, 0, -H * 0.08)), (L * 0.3, W * 0.84, H * 0.78), col, top=(0.82, 0.86), bot=(0.9, 0.9))
    for s in (1, -1): m.box(f"Cheek{s}", hc + V((L * 0.15, s * W * 0.46, -H * 0.12)), (L * 0.6, W * 0.16, H * 0.7), col, top=(0.85, 0.85))
    if belly: m.box("Throat", hc + V((L * 0.1, 0, -H * 0.5)), (L * 0.95, W * 0.9, H * 0.18), belly, studs=False)

def smile(m, T, V, hc, L, W, H, col):
    m.box("SmileFront", hc + V((L * 0.66, 0, -H * 0.28)), (0.07, W * 0.6, 0.08), col, studs=False)
    for s in (1, -1):
        m.box(f"SmileSide{s}", hc + V((L * 0.4, s * W * 0.43, -H * 0.24)), (L * 0.6, 0.07, 0.08), col, rot=T.Rz(-s * 0.55), studs=False)
        m.box(f"SmileCurl{s}", hc + V((L * 0.1, s * W * 0.52, -H * 0.12)), (0.25, 0.07, 0.08), col, rot=T.Ry(0.7), studs=False)

# ============================================================================ variations
def SalA_Axolotl(m, T, V):
    BLK, BLK_L, BELLY, GL = T.rgb(38, 34, 46), T.rgb(66, 60, 78), T.rgb(238, 108, 46), T.rgb(255, 188, 52)
    FL = (T.rgb(214, 52, 22), T.rgb(250, 138, 30), GL)
    m.gait = {"crawl": True}
    body = m.bone("Body", (0, 0, 1.1)); body.__enter__()
    pts = [V((2.3, 0.1, 1.2)), V((1.0, 0.55, 1.12)), V((-0.45, 0.6, 1.06)), V((-1.75, 0.15, 1.0))]
    spine_body(m, T, V, "Torso", pts, [1.9, 2.15, 2.05, 1.75], [1.35, 1.45, 1.4, 1.25], BLK, belly=BELLY)
    for k, (p, r) in enumerate(((pts[0].lerp(pts[1], 0.5) + V((0.1, -0.35, 0.7)), 0.55), (pts[1] + V((-0.1, 0.4, 0.72)), 0.48), (pts[1].lerp(pts[2], 0.5) + V((0.0, -0.5, 0.7)), 0.5),
                                (pts[2] + V((0.1, 0.45, 0.68)), 0.42), (pts[2].lerp(pts[3], 0.5) + V((0, -0.3, 0.66)), 0.46))):
        blob(m, T, f"Spot{k}", p, r, GL, glow=True)
    for s in (1, -1):
        for k, t in enumerate((0.3, 1.4, 2.4)):
            i = int(t); q = pts[i].lerp(pts[i + 1], t - i) + V((0, s * 1.06, 0.1))
            blob(m, T, f"SideSpot{s}{k}", q, 0.4, GL, up=(0, s, 0), glow=True)
    newt_legs(m, T, V, [("F", 1.6, 0.35, 1.0), ("B", -1.55, 0.3, -1.0)], BLK, BLK_L)
    tp = [pts[-1], V((-2.95, -0.35, 0.92)), V((-4.0, -0.95, 0.78)), V((-4.85, -1.05, 0.62)), V((-5.55, -0.6, 0.52))]
    m.chain("Tail", tp, [1.55, 1.2, 0.88, 0.58, 0.32], BLK, depths=[1.25, 1.05, 0.85, 0.62, 0.36], bones="Tail")
    for i in (1, 2):
        with m.bone(f"Tail{i}"): blob(m, T, f"TailSpot{i}", tp[i].lerp(tp[i + 1], 0.5) + V((0, 0, [1.2, 0.88][i - 1] * 0.42)), 0.4 - 0.08 * i, GL, glow=True)
    with m.bone("Tail4"): flame(m, T, V, "TailFire", tp[-1], (0.2, 0.5, 0.8), 1.6, 0.4, FL, front=(0, 0, 1))
    with m.bone("Head", (2.4, 0.1, 1.2)):
        hc = V((3.35, 0.0, 1.45))
        with m.frame(pivot=hc, rot=T.Rz(-0.12) @ T.Ry(-0.22)):
            round_head(m, T, V, hc, BLK, (2.0, 2.6, 1.35), belly=BELLY)
            smile(m, T, V, hc, 2.0, 2.6, 1.2, T.rgb(140, 36, 24))
            for s in (1, -1):
                m.box(f"EyeBump{s}", hc + V((0.45, s * 0.82, 0.6)), (0.95, 0.85, 0.55), BLK, top=(0.75, 0.75))
                blob(m, T, f"HeadSpot{s}", hc + V((-0.45, s * 0.5, 0.62)), 0.38, GL, glow=True)
                for g, (dz, spread, L) in enumerate(((0.45, 0.25, 1.9), (0.05, 0.6, 2.1), (-0.32, 0.35, 1.7))):
                    root = hc + V((-0.75, s * 1.25, dz))
                    m.seg(f"GillStalk{s}{g}", root - V((0, s * 0.25, 0)), root + V((-0.15, s * 0.25, 0.05)), 0.3, 0.24, BLK_L, studs=False)
                    flame(m, T, V, f"Gill{s}{g}", root + V((-0.15, s * 0.25, 0.05)), (-0.5, s * (0.5 + spread), 0.45 + dz), L, 0.55, FL, front=(0.6, 0, 1))
            m.eyes(tuple(hc + V((0.95, 0.82, 0.78))), facing=(0.85, 0.5, 0.25), size=(0.9, 0.9), pupil=0.46, look=(0.3, 0.05), angry=0.12, pupil_col=T.rgb(14, 10, 20),
                   brow_col=BLK_L, brow_h=0.25, brow_up=0.66, depth=0.17)
            pass
    body.__exit__(None, None, None)
    return GL

def SalB_MagmaNewt(m, T, V):
    ROCK, ROCK_D, BELLY, GL, OBS = T.rgb(70, 58, 56), T.rgb(40, 32, 34), T.rgb(246, 118, 40), T.rgb(255, 112, 24), T.rgb(28, 22, 28)
    m.gait = {"crawl": True}
    body = m.bone("Body", (0, 0, 1.1)); body.__enter__()
    pts = [V((2.3, 0.0, 1.2)), V((0.9, 0.35, 1.15)), V((-0.5, 0.4, 1.1)), V((-1.8, 0.1, 1.02))]
    spine_body(m, T, V, "Torso", pts, [2.0, 2.25, 2.15, 1.85], [1.4, 1.5, 1.45, 1.3], ROCK, belly=BELLY)
    for i in range(len(pts)):
        p = pts[i] + V((0, 0, 0.72))
        m.box(f"Plate{i}", p, (1.05, 1.6, 0.32), ROCK_D, top=(0.8, 0.85))
        m.spike(f"Spike{i}", p + V((0, 0, 0.12)), p + V((-0.35, 0, 1.05 - 0.1 * abs(i - 1))), 0.3, OBS, flat=0.45)
        m.spike(f"SpikeTip{i}", p + V((-0.2, 0, 0.65)), p + V((-0.35, 0, 1.05 - 0.1 * abs(i - 1))), 0.12, GL, flat=0.45, glow=True)
        if i < len(pts) - 1:
            q = pts[i].lerp(pts[i + 1], 0.5) + V((0, 0, 0.7)); m.box(f"Crack{i}", q, (0.14, 1.5, 0.08), GL, rot=T.Rz(0.3), glow=True, studs=False)
        for s in (1, -1):
            m.box(f"SideCrack{i}{s}", pts[i] + V((0.2, s * 1.12, 0.1)), (0.8, 0.06, 0.12), GL, rot=T.Ry(0.5 * s), glow=True, studs=False)
            m.box(f"SidePlate{i}{s}", pts[i] + V((-0.2, s * 0.95, 0.45)), (0.9, 0.4, 0.5), ROCK_D, rot=T.Rx(s * 0.5), top=(0.8, 0.8))
    newt_legs(m, T, V, [("F", 1.6, 0.25, 1.0), ("B", -1.6, 0.25, -1.0)], ROCK, GL, thick=1.05, glow_pad=True)
    tp = [pts[-1], V((-3.0, -0.35, 0.92)), V((-4.1, -0.9, 0.78)), V((-5.0, -0.95, 0.62)), V((-5.7, -0.5, 0.5))]
    m.chain("Tail", tp, [1.6, 1.25, 0.9, 0.6, 0.32], ROCK, depths=[1.3, 1.08, 0.86, 0.62, 0.36], bones="Tail")
    for i in (1, 2, 3):
        with m.bone(f"Tail{i}"):
            q = tp[i].lerp(tp[i + 1], 0.4); w = [1.25, 0.9, 0.6][i - 1]
            m.box(f"TailPlate{i}", q + V((0, 0, w * 0.5)), (0.7, w * 0.7, 0.26), ROCK_D, top=(0.8, 0.8))
            m.box(f"TailCrack{i}", q + V((0.4, 0, w * 0.48)), (0.12, w * 0.7, 0.06), GL, glow=True, studs=False)
    with m.bone("Tail4"): m.box("TailDrip", tp[-1] + V((-0.1, 0, -0.35)), (0.18, 0.18, 0.4), GL, glow=True, studs=False)
    with m.bone("Head", (2.4, 0.0, 1.2)):
        hc = V((3.35, -0.05, 1.45))
        with m.frame(pivot=hc, rot=T.Rz(-0.1) @ T.Ry(-0.08)):
            round_head(m, T, V, hc, ROCK, (2.0, 2.5, 1.2), belly=BELLY)
            m.box("BrowPlate", hc + V((0.25, 0, 0.72)), (1.3, 2.2, 0.32), ROCK_D, top=(0.8, 0.85))
            m.box("BrowCrack", hc + V((0.25, 0, 0.9)), (1.1, 0.12, 0.06), GL, glow=True, studs=False)
            smile(m, T, V, hc, 2.0, 2.5, 1.2, GL)
            for k, y in enumerate((-0.5, 0.35)):
                m.box(f"Drip{k}", hc + V((1.32, y, -0.62)), (0.14, 0.14, 0.45), GL, glow=True, studs=False)
                m.box(f"DripBlob{k}", hc + V((1.32, y, -0.88)), (0.22, 0.22, 0.22), GL, glow=True, studs=False)
            for s in (1, -1):
                m.box(f"EyeBump{s}", hc + V((0.45, s * 0.8, 0.6)), (0.95, 0.8, 0.55), ROCK_D, top=(0.75, 0.75))
                m.spike(f"Horn{s}", hc + V((-0.3, s * 0.85, 0.7)), hc + V((-1.1, s * 1.15, 1.1)), 0.2, OBS, flat=0.6)
            m.eyes(tuple(hc + V((0.86, 0.9, 0.72))), facing=(0.55, 0.75, 0.35), size=(0.7, 0.42), pupil=0.75, look=(0.4, 0), angry=0.45,
                   white=GL, glow_white=True, pupil_col=T.rgb(110, 20, 10), brow_col=OBS, brow_h=0.45, brow_up=0.75, depth=0.17)
    body.__exit__(None, None, None)
    return GL

def SalC_FlameFrill(m, T, V):
    RED, RED_D, GOLD, STR, GL = T.rgb(176, 34, 28), T.rgb(110, 20, 18), T.rgb(250, 190, 60), T.rgb(36, 22, 24), T.rgb(255, 150, 30)
    FL = (T.rgb(214, 52, 22), T.rgb(250, 138, 30), GL)
    m.gait = {"crawl": True}
    body = m.bone("Body", (-0.6, 0, 1.0)); body.__enter__()
    pts = [V((-1.6, 0.0, 0.95)), V((-0.3, 0.0, 1.15)), V((0.75, 0.0, 1.9)), V((1.3, 0.0, 2.9))]       # rearing up like a cobra
    spine_body(m, T, V, "Torso", pts, [1.75, 1.95, 1.8, 1.5], [1.25, 1.35, 1.3, 1.15], RED, belly=GOLD)
    for i in range(len(pts) - 1):
        q = pts[i].lerp(pts[i + 1], 0.5); d = (pts[i + 1] - pts[i]).normalized(); up = V((-d.z, 0, d.x))
        m.box(f"Stripe{i}", q + up * 0.68, (0.3, 1.55, 0.1), STR, rot=T.Ry(-math.atan2(d.z, d.x)), studs=False)
    newt_legs(m, T, V, [("B", -1.4, 0.0, -1.0)], RED, GOLD)
    for s in (1, -1):                           # raised front legs, claws forward
        sh = V((1.0, s * 0.7, 2.3))
        with m.bone(f"Leg_F{LR(s)}", sh):
            el = sh + V((0.5, s * 0.55, -0.3)); hd = el + V((0.55, s * 0.1, -0.35))
            m.seg(f"FArmU{s}", sh, el, 0.62, 0.52, RED); m.seg(f"FArmL{s}", el, hd, 0.52, 0.44, RED)
            for t in (-1, 0, 1): m.spike(f"FClaw{s}{t}", hd + V((0.1, t * 0.16, 0)), hd + V((0.45, t * 0.2, -0.15)), 0.07, GOLD, flat=0.4)
    tp = [pts[0], V((-2.8, -0.5, 0.75)), V((-3.8, -1.3, 0.6)), V((-4.3, -2.2, 0.5)), V((-3.9, -2.9, 0.45))]
    m.chain("Tail", tp, [1.45, 1.1, 0.8, 0.55, 0.3], RED, depths=[1.15, 0.95, 0.75, 0.55, 0.32], bones="Tail")
    for i in (1, 2, 3):
        with m.bone(f"Tail{i}"):
            q = tp[i].lerp(tp[i + 1], 0.5); m.box(f"TailStripe{i}", q + V((0, 0, [1.0, 0.75, 0.52][i - 1] * 0.48)), (0.28, 0.9 - 0.15 * i, 0.08), STR, studs=False)
            flame(m, T, V, f"TailFlame{i}", q + V((0, 0, 0.35)), (-0.3, 0, 1), 1.0 - 0.15 * i, 0.3, FL)
    with m.bone("Tail4"): flame(m, T, V, "TailTip", tp[-1], (0.4, -0.4, 0.8), 1.4, 0.38, FL, front=(0, 0, 1))
    with m.bone("Head", (1.4, 0, 3.3)):
        hc = V((2.0, 0, 3.75))
        for k in range(11):                     # frilled-lizard collar of flame behind the head
            a = math.pi * (k / 10) - math.pi / 2 + math.pi / 2 * 0.0
            ang = -math.pi * 0.95 / 2 + math.pi * 0.95 * k / 10
            d = V((-0.45, math.sin(ang), math.cos(ang)))
            flame(m, T, V, f"Frill{k}", hc + V((-0.55, 0, 0)) + V((0, math.sin(ang), math.cos(ang))) * 0.55, d, 1.9 - 0.25 * abs(k - 5) / 5, 0.5, FL, front=(1, 0, 0))
        m.box("FrillBack", hc + V((-0.75, 0, 0.1)), (0.2, 2.6, 2.2), RED_D, top=(0.6, 0.85), studs=False)
        round_head(m, T, V, hc, RED, (1.7, 1.9, 1.05), belly=GOLD)
        smile(m, T, V, hc, 1.7, 1.9, 1.05, STR)
        for t in (1, -1): m.spike(f"Fang{t}", hc + V((1.08, t * 0.4, -0.32)), hc + V((1.1, t * 0.4, -0.62)), 0.07, T.TOOTH, flat=0.35)
        m.eyes(tuple(hc + V((0.75, 0.68, 0.32))), facing=(0.65, 0.7, 0.2), size=(0.6, 0.45), pupil=0.7, look=(0.4, 0), angry=0.45,
               white=GOLD, brow_col=STR, brow_h=0.45, brow_up=0.72, depth=0.15)
    body.__exit__(None, None, None)
    return GL

def SalD_EmberGecko(m, T, V):
    BLK, BLK_L, YEL, GL, PINKT = T.rgb(40, 36, 50), T.rgb(70, 64, 84), T.rgb(255, 202, 52), T.rgb(255, 150, 40), T.rgb(255, 120, 140)
    FL = (T.rgb(214, 52, 22), T.rgb(250, 138, 30), GL)
    m.gait = {"crawl": True}
    body = m.bone("Body", (0, 0, 1.0)); body.__enter__()
    pts = [V((1.2, 0.0, 1.05)), V((0.0, 0.1, 1.05)), V((-1.1, 0.0, 1.0))]
    spine_body(m, T, V, "Torso", pts, [2.0, 2.2, 1.9], [1.45, 1.5, 1.35], BLK, belly=T.rgb(250, 230, 200))
    for k, (p, r) in enumerate(((V((0.7, 0.4, 1.8)), 0.62), (V((-0.4, -0.45, 1.8)), 0.58), (V((-0.2, 0.55, 1.76)), 0.36), (V((0.9, -0.5, 1.76)), 0.34))):
        blob(m, T, f"Spot{k}", p, r, YEL)
    for s in (1, -1):
        for k, (x, z, r) in enumerate(((0.6, 1.2, 0.5), (-0.6, 1.05, 0.46))): blob(m, T, f"SideSpot{s}{k}", V((x, s * 1.12, z)), r, YEL, up=(0, s, 0))
    newt_legs(m, T, V, [("F", 1.1, 0.0, 1.0), ("B", -1.0, 0.0, -1.0)], BLK, GL, thick=1.1, glow_pad=True)
    tp = [pts[-1]]                               # spiral-curled tail on the ground
    for k in range(1, 7):
        a = math.pi * 0.5 + k * 0.62; r = 1.7 - k * 0.2
        tp.append(V((-2.4 + math.cos(a) * r, -0.3 + math.sin(a) * r * 0.9 - 0.4, 0.62 - 0.03 * k)))
    tp[1] = V((-2.0, 0.1, 0.85))
    m.chain("Tail", tp, [1.4, 1.15, 0.95, 0.78, 0.62, 0.48, 0.34], BLK, depths=[1.2, 1.0, 0.85, 0.7, 0.56, 0.44, 0.32], bones="Tail")
    for i in (1, 3):
        with m.bone(f"Tail{i}"): blob(m, T, f"TailSpot{i}", tp[i].lerp(tp[i + 1], 0.5) + V((0, 0, [1.0, 0.7][i // 2] * 0.5)), 0.42 - 0.08 * i, YEL)
    piv = V((1.6, 0, 1.2))
    with m.bone("Head", piv), m.frame(pivot=piv, scale=1.4, rot=T.Ry(-0.18)):
        hc = V((2.4, 0, 1.45))
        round_head(m, T, V, hc, BLK, (1.6, 2.0, 1.15), belly=T.rgb(250, 230, 200))
        smile(m, T, V, hc, 1.6, 2.0, 1.15, T.rgb(150, 40, 40))
        m.box("Tongue", hc + V((1.08, 0.15, -0.42)), (0.24, 0.3, 0.08), PINKT, studs=False)
        for s in (1, -1):
            blob(m, T, f"HeadSpot{s}", hc + V((-0.35, s * 0.45, 0.78)), 0.36, YEL)
        m.eyes(tuple(hc + V((0.72, 0.68, 0.46))), facing=(0.85, 0.5, 0.15), size=(0.82, 0.82), pupil=0.46, look=(0.3, 0.05), angry=0.0, pupil_col=T.rgb(14, 10, 20),
               brow_col=BLK_L, brow_h=0.22, brow_up=0.66, depth=0.17)
        pass
        m.seg("Wick", hc + V((-0.1, 0, 0.75)), hc + V((-0.05, 0, 1.15)), 0.12, 0.1, BLK_L, studs=False)
        flame(m, T, V, "Candle", hc + V((-0.05, 0, 1.12)), (0, 0, 1), 0.95, 0.38, FL)
    body.__exit__(None, None, None)
    return GL

VARIANTS = [SalA_Axolotl, SalB_MagmaNewt, SalC_FlameFrill, SalD_EmberGecko]

def build_one(fn):
    T, V = K()
    m = T.Model(fn.__name__, os.path.join(OUT, fn.__name__), stud=0.4, chamfer=0.18, jitter=0.05)
    glow = fn(m, T, V)
    m.done(views=VIEWS, glow_color=glow)

def sheet():
    from PIL import Image, ImageDraw
    Tz = 380; out = Image.new("RGB", (Tz * 3, Tz * len(VARIANTS)), "white"); d = ImageDraw.Draw(out)
    for r, fn in enumerate(VARIANTS):
        for c, (v, *_r) in enumerate(VIEWS):
            p = os.path.join(OUT, fn.__name__, "previews", f"{fn.__name__}_{v}.png")
            if os.path.exists(p): out.paste(Image.open(p).convert("RGB").resize((Tz, Tz)), (c * Tz, r * Tz))
        d.rectangle([4, r * Tz + 4, 220, r * Tz + 26], fill="white"); d.text((10, r * Tz + 9), fn.__name__, fill="black")
    out.save(os.path.join(OUT, "Salamander_variants.png")); print("SHEET")

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--sheet" in sys.argv: sheet(); sys.exit()
    if "--child" in sys.argv:
        build_one(next(f for f in VARIANTS if f.__name__ == want[0])); sys.exit()
    for fn in VARIANTS:
        if want and fn.__name__ not in want: continue
        print("BUILD", fn.__name__, flush=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), fn.__name__, "--child"], capture_output=True, text=True)
        tl = [l for l in r.stdout.splitlines() if l.startswith("TRIS")]
        print("  ", tl[-1] if tl else "", flush=True)
        if r.returncode: print("FAILED", fn.__name__, r.stderr[-1500:], flush=True)
