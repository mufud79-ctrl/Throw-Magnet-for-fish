"""4 MoonBunny + 4 SpaceCat full-body design variations for user feedback (TFFA kit, rigged).

usage: /tmp/bpyenv/bin/python tools/blender/tffa_space_variants.py [Name ...]      (then: python3 ... --sheet)
Writes models/TFFA/SpaceVariants/<Name>/ and Bunny_variants.png / Cat_variants.png (rows: hero, front, side)."""
import os, sys, subprocess, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tffa-animal-models", "scripts"))
OUT = os.path.join(ROOT, "models", "TFFA", "SpaceVariants")
VIEWS = [("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)]
LR = lambda s: "L" if s > 0 else "R"

def K():
    import tffa_kit as T
    from mathutils import Vector
    return T, Vector

# ============================================================================ shared parts
def star(m, T, V, name, c, r, col, xaxis=(0, 1, 0), yaxis=(0, 0, 1), glow=True, n=5, thick=0.08):
    pts = []
    for k in range(n * 2):
        a = math.pi / 2 + k * math.pi / n; rr = r if k % 2 == 0 else r * 0.42
        pts.append((math.cos(a) * rr, math.sin(a) * rr))
    m.slab(name, pts, thick, col, origin=c, xaxis=xaxis, yaxis=yaxis, glow=glow)

def bunny_head(m, T, V, hc, fur, wht, browc, ears, nose=(1.0, 0.55, 0.69), eye_white=None, angry=0.05, ear_in=None, ear_glow=False):
    """Big TFFA rabbit head at hc. ears: list per side of (base_off, mid_off, tip_off) relative to hc (left side, mirrored)."""
    m.box("Head", hc, (1.45, 1.75, 1.4), fur, top=(0.86, 0.9), bot=(0.88, 0.9))
    for s in (1, -1):
        m.box(f"Cheek{s}", hc + V((0.42, s * 0.52, -0.42)), (0.7, 0.66, 0.6), wht, top=(0.85, 0.9))
    m.box("Snout", hc + V((0.76, 0, -0.32)), (0.36, 0.76, 0.46), wht, top=(0.85, 0.9))
    m.box("Nose", hc + V((0.95, 0, -0.17)), (0.08, 0.28, 0.16), nose, bot=(0.9, 0.5), studs=False)
    for s in (1, -1): m.box(f"Tooth{s}", hc + V((0.9, s * 0.075, -0.64)), (0.06, 0.13, 0.24), T.WHITE, studs=False)
    m.eyes(tuple(hc + V((0.74, 0.4, 0.14))), size=(0.58, 0.58), pupil=0.62, look=(0.3, 0.05), angry=angry, white=eye_white or T.WHITE,
           brow_col=browc, brow_h=0.3, brow_up=0.66, depth=0.13)
    for s in (1, -1): m.box(f"Glint{s}", hc + V((0.82, s * 0.32, 0.27)), (0.04, 0.1, 0.1), T.WHITE, studs=False)
    for s in (1, -1):
        b0, b1, b2 = [hc + V((o[0], s * o[1], o[2])) for o in ears]
        with m.bone(f"Ear_{LR(s)}", b0):
            m.seg(f"Ear{s}", b0, b1, 0.68, 0.62, fur, d0=0.32, d1=0.3)
            m.seg(f"EarTip{s}", b1 - (b1 - b0).normalized() * 0.12, b2, 0.62, 0.3, fur, d0=0.3, d1=0.2)
            if ear_in:
                f = V((0.16, 0, 0))
                m.seg(f"EarIn{s}", b0 + f + V((0, 0, 0.25)), b1 + f, 0.38, 0.36, ear_in, d0=0.05, d1=0.05, glow=ear_glow, studs=False)
                m.seg(f"EarInTip{s}", b1 + f, b2 + f * 0.8 - (b2 - b1).normalized() * 0.2, 0.36, 0.14, ear_in, d0=0.05, d1=0.05, glow=ear_glow, studs=False)

def bunny_legs(m, T, V, fur, wht, hind_x=-0.55, front_x=0.85, wide=1.0):
    for s in (1, -1):
        with m.bone(f"Leg_B{LR(s)}", (hind_x, s * 0.95 * wide, 1.1)):
            m.box(f"Thigh{s}", (hind_x - 0.05, s * 1.12 * wide, 0.95), (1.55, 0.6, 1.35), fur, top=(0.78, 0.84), bot=(0.88, 0.9))
            m.box(f"Foot{s}", (hind_x + 0.55, s * 1.08 * wide, 0.17), (1.8, 0.7, 0.34), fur, top=(0.9, 0.9))
            m.box(f"Toe{s}", (hind_x + 1.41, s * 1.08 * wide, 0.14), (0.18, 0.62, 0.24), wht, studs=False)
        with m.bone(f"Leg_F{LR(s)}", (front_x, s * 0.55, 1.2)):
            m.seg(f"Arm{s}", V((front_x + 0.05, s * 0.58, 1.35)), V((front_x + 0.3, s * 0.62, 0.2)), 0.5, 0.44, fur)
            m.box(f"Paw{s}", (front_x + 0.43, s * 0.62, 0.13), (0.56, 0.5, 0.26), wht, studs=False)

def cat_head(m, T, V, hc, fur, muz, nose, earc, earin, eye, browc, angry=0.25, slit=True, eye_glow=False, size=1.0):
    k = size
    m.box("Head", hc, (1.6 * k, 1.95 * k, 1.5 * k), fur, top=(0.88, 0.9), bot=(0.9, 0.92))
    for s in (1, -1):
        m.box(f"Pad{s}", hc + V((0.82, s * 0.3, -0.38)) * k, (0.55 * k, 0.62 * k, 0.5 * k), muz, top=(0.85, 0.9))
        for j in (-1, 1):
            m.box(f"Whisker{s}{j}", hc + V((0.95, s * 0.95, -0.36 + j * 0.1)) * k, (0.04, 0.9 * k, 0.04), T.WHITE, rot=T.Rx(s * j * 0.12), studs=False)
    m.box("Chin", hc + V((0.72, 0, -0.68)) * k, (0.42 * k, 0.5 * k, 0.26 * k), muz)
    m.box("Nose", hc + V((1.1, 0, -0.16)) * k, (0.1, 0.34 * k, 0.2 * k), nose, bot=(0.5, 0.45), studs=False)
    m.eyes(tuple(hc + V((0.81, 0.47, 0.2)) * 1.0 if k == 1 else hc + V((0.81 * k, 0.47 * k, 0.2 * k))), size=(0.62 * k, 0.56 * k), pupil=0.66,
           look=(0.25, 0), angry=angry, white=eye, pupil_col=eye if slit else T.PUPIL, glow_white=eye_glow, brow_col=browc, brow_h=0.36,
           brow_up=0.68, depth=0.14)
    if slit:
        for s in (1, -1): m.box(f"Slit{s}", hc + V((0.81 * k + 0.1, s * (0.47 * k - 0.04), 0.2 * k)), (0.04, 0.12 * k, 0.48 * k), T.PUPIL, studs=False)
    for s in (1, -1):
        with m.bone(f"Ear_{LR(s)}", hc + V((-0.15, s * 0.62, 0.7)) * k):
            b = hc + V((-0.15, s * 0.62, 0.72)) * k
            m.box(f"Ear{s}", b + V((0, 0, 0.36 * k)), (0.38 * k, 0.62 * k, 0.75 * k), earc, top=(0.3, 0.15), rot=T.Rx(-s * 0.18))
            m.box(f"EarIn{s}", b + V((0.15 * k, 0, 0.3 * k)), (0.06, 0.36 * k, 0.48 * k), earin, top=(0.3, 0.15), rot=T.Rx(-s * 0.18), studs=False)

def cat_body(m, T, V, L, W, H, lh, lw, fur, belly=None, legc=None, paw=None):
    z0 = lh + H / 2
    m.box("Body", (0, 0, z0), (L, W, H), fur, top=(0.9, 0.92), bot=(0.92, 0.95))
    m.box("Chest", (L * 0.32, 0, z0 + H * 0.06), (L * 0.36, W * 1.06, H * 1.08), fur, top=(0.86, 0.9))
    if belly: m.box("Belly", (L * 0.08, 0, z0 - H * 0.33), (L * 0.78, W + 0.04, H * 0.36), belly)
    for sx in (1, -1):
        for s in (1, -1):
            x = sx * (L / 2 - lw * 0.65); y = s * (W / 2 - lw * 0.55)
            with m.bone(f"Leg_{'F' if sx > 0 else 'B'}{LR(s)}", (x, y, lh + 0.1)):
                m.box(f"Leg{sx}{s}", (x, y, (lh + 0.3) / 2), (lw, lw, lh + 0.3), legc or fur)
                m.box(f"Paw{sx}{s}", (x + 0.06, y, 0.14), (lw * 1.14, lw * 1.06, 0.28), paw or legc or fur, studs=False)
    return z0

# ============================================================================ MoonBunny variations
def BunnyA_MoonRock(m, T, V):
    """The bunny's body IS a cratered moon; head, paws and big feet peek out; moon rocks orbit with glowing trails."""
    MOON, MOON_D, MOON_L, FUR, WHT, GL = T.rgb(196, 198, 212), T.rgb(104, 106, 128), T.rgb(150, 152, 172), T.rgb(236, 232, 250), T.rgb(250, 250, 255), T.rgb(255, 210, 90)
    m.gait = {"hop": True}
    body = m.bone("Body", (0, 0, 2.0)); body.__enter__()
    m.ball("Moon", (0, 0, 2.15), 2.1, MOON)
    m.box("MoonBase", (0, 0, 0.45), (2.6, 2.6, 0.9), MOON, top=(0.8, 0.8))
    craters = [(0.6, 0.9, 1.0, 0.55), (-0.3, -1.3, 2.8, 0.7), (-1.6, 0.6, 2.4, 0.6), (0.4, 1.5, 3.0, 0.45), (-0.9, -0.4, 3.9, 0.5),
               (-1.2, 1.4, 1.2, 0.5), (0.9, -1.4, 1.6, 0.48), (-1.8, -0.8, 1.6, 0.4)]
    for k, (x, y, z, r) in enumerate(craters):
        n = V((x, y, z - 2.15)).normalized(); p = V((0, 0, 2.15)) + n * 2.12
        tz = n; tx = V((0, 0, 1)).cross(tz); tx = tx.normalized() if tx.length > 0.01 else V((1, 0, 0)); ty = tz.cross(tx)
        R = T.Matrix((tx, ty, tz)).transposed()
        m.box(f"Crater{k}", p, (r * 1.25, r * 1.25, 0.2), MOON_D, rot=R, studs=False)
        m.box(f"CraterF{k}", p + n * 0.05, (r * 0.8, r * 0.8, 0.18), MOON_L, rot=R, studs=False)
    bunny_legs(m, T, V, FUR, WHT, hind_x=-0.2, front_x=1.35, wide=1.15)
    with m.bone("Tail1", (-2.1, 0, 2.0)):
        m.box("Tail", (-2.25, 0, 2.1), (0.8, 0.85, 0.8), WHT, top=(0.8, 0.8), bot=(0.8, 0.8))
    for k in range(3):             # orbiting moon rocks with glowing trails
        a = k * 2.1 + 0.4; p = V((math.cos(a) * 3.0, math.sin(a) * 3.0, 3.1 + 0.4 * math.sin(a * 2)))
        m.ball(f"Rock{k}", p, 0.32, MOON)
        tdir = V((-math.sin(a), math.cos(a), 0))
        m.seg(f"Trail{k}", p - tdir * 0.3, p - tdir * 1.3, 0.22, 0.05, GL, glow=True, studs=False)
    piv = V((0.9, 0, 3.6))
    with m.bone("Head", piv), m.frame(pivot=piv, scale=1.25):
        hc = V((1.05, 0, 4.25))
        bunny_head(m, T, V, hc, FUR, WHT, T.rgb(150, 140, 190), [(-0.2, 0.45, 0.6), (-0.35, 0.68, 1.9), (-0.3, 0.85, 2.75)], ear_in=GL, ear_glow=True)
        star(m, T, V, "BrowStar", hc + V((0.74, 0, 0.5)), 0.2, GL)
    body.__exit__(None, None, None)
    return GL

def BunnyB_Comet(m, T, V):
    """Mid-leap streak: body angled up, front paws reaching, ears streaming back; the tail becomes a long glowing comet trail."""
    FUR, FUR_D, WHT, GL = T.rgb(56, 78, 196), T.rgb(34, 46, 130), T.rgb(244, 248, 255), T.rgb(150, 232, 255)
    m.gait = {"hop": True}
    body = m.bone("Body", (0, 0, 1.9)); body.__enter__()
    with m.frame(pivot=(0, 0, 1.9), rot=T.Ry(-0.32)):
        m.box("Rump", (-0.6, 0, 1.9), (2.2, 2.1, 1.75), FUR, top=(0.8, 0.84), bot=(0.86, 0.9))
        m.box("Chest", (0.75, 0, 2.0), (1.7, 1.85, 1.8), FUR, top=(0.84, 0.86))
        m.box("Belly", (0.3, 0, 1.18), (2.4, 1.4, 0.3), WHT)
        for s in (1, -1):
            for j, (x, z) in enumerate(((-0.9, 2.4), (-0.2, 2.6), (0.6, 2.3), (-0.5, 1.6))):
                m.box(f"Speck{s}{j}", (x, s * 1.06, z), (0.12, 0.05, 0.12), GL, glow=True, studs=False)
    for s in (1, -1):
        with m.bone(f"Leg_F{LR(s)}", (1.4, s * 0.6, 2.3)):           # reaching forward
            m.seg(f"Arm{s}", V((1.4, s * 0.62, 2.2)), V((2.6, s * 0.7, 1.7)), 0.5, 0.42, FUR)
            m.box(f"Paw{s}", (2.75, s * 0.7, 1.6), (0.55, 0.5, 0.3), WHT, rot=T.Ry(0.4), studs=False)
        with m.bone(f"Leg_B{LR(s)}", (-1.1, s * 0.95, 1.6)):         # pushing off, extended back
            m.box(f"Thigh{s}", (-1.2, s * 1.08, 1.45), (1.5, 0.6, 1.3), FUR, rot=T.Ry(0.5), top=(0.78, 0.84))
            m.seg(f"Shin{s}", V((-1.6, s * 1.08, 1.0)), V((-2.4, s * 1.06, 0.3)), 0.5, 0.42, FUR)
            m.box(f"Foot{s}", (-2.65, s * 1.06, 0.17), (1.3, 0.65, 0.34), WHT, rot=T.Ry(-0.15), studs=False)
    pts = [V((-1.7, 0, 2.6)), V((-2.8, 0, 3.0)), V((-4.0, 0, 3.15)), V((-5.3, 0, 3.0)), V((-6.5, 0, 2.7))]
    m.chain("Comet", pts, [0.8, 1.05, 1.25, 1.1, 0.6], GL, studs=False, bones="Tail", glow=True)
    for k, (x, y, z, r) in enumerate(((-3.2, 0.8, 3.6, 0.2), (-4.4, -0.9, 3.7, 0.24), (-5.6, 0.7, 3.4, 0.18), (-4.8, 0.4, 2.3, 0.16), (-3.6, -0.6, 2.4, 0.14))):
        with m.bone("Tail2" if x > -4.0 else "Tail3"):
            star(m, T, V, f"Spark{k}", V((x, y, z)), r, GL, xaxis=(1, 0, 0), yaxis=(0, 0, 1))
    piv = V((1.3, 0, 2.8))
    with m.bone("Head", piv), m.frame(pivot=piv, scale=1.2):
        hc = V((1.75, 0, 3.4))
        bunny_head(m, T, V, hc, FUR, WHT, FUR_D, [(-0.25, 0.45, 0.5), (-1.3, 0.62, 1.2), (-2.2, 0.72, 1.35)], angry=0.25, ear_in=GL, ear_glow=True)
    body.__exit__(None, None, None)
    return GL

def BunnyC_Saturn(m, T, V):
    """Galaxy-furred bunny sitting tall inside a big tilted planetary ring; a tiny moon orbits its head; star-tipped ears."""
    FUR, FUR_D, WHT, NEB_M, NEB_C, GL = T.rgb(56, 44, 128), T.rgb(34, 26, 84), T.rgb(236, 230, 255), T.rgb(200, 70, 190), T.rgb(70, 170, 225), T.rgb(255, 120, 220)
    R1, R2, R3 = T.rgb(242, 196, 110), T.rgb(214, 140, 70), T.rgb(250, 226, 170)
    m.gait = {"hop": True}
    body = m.bone("Body", (0, 0, 1.6)); body.__enter__()
    m.box("Rump", (-0.4, 0, 1.4), (2.3, 2.3, 2.0), FUR, top=(0.78, 0.82), bot=(0.88, 0.9))
    m.box("Chest", (0.5, 0, 1.9), (1.5, 1.95, 2.4), FUR, top=(0.82, 0.84), rot=T.Ry(-0.08))
    m.box("Belly", (1.25, 0, 1.7), (0.24, 1.3, 1.8), WHT, top=(0.8, 0.88))
    for s in (1, -1):
        for j, (x, z, w, h, col) in enumerate(((-0.6, 1.6, 1.1, 0.5, NEB_M), (-0.2, 2.1, 0.8, 0.35, NEB_C), (-1.0, 1.0, 0.6, 0.3, NEB_C))):
            m.box(f"Neb{s}{j}", (x, s * 1.16, z), (w, 0.05, h), col, rot=T.Ry(0.3), studs=False)
        for j, (x, z) in enumerate(((-0.9, 2.0), (0.1, 1.4), (-0.3, 0.8), (-1.3, 1.5))):
            m.box(f"Spk{s}{j}", (x, s * 1.18, z), (0.12, 0.05, 0.12), T.WHITE, studs=False)
    bunny_legs(m, T, V, FUR, WHT)
    with m.bone("Tail1", (-1.6, 0, 1.3)):
        m.box("Tail", (-1.8, 0, 1.4), (0.75, 0.8, 0.75), WHT, top=(0.8, 0.8), bot=(0.8, 0.8))
    tilt = T.Rx(0.32) @ T.Ry(0.18)                  # planetary ring around the waist: three colour bands
    for band, (r, col, w) in enumerate(((2.12, R1, 0.42), (2.42, T.rgb(120, 80, 60), 0.12), (2.66, R2, 0.34), (2.9, T.rgb(120, 80, 60), 0.1), (3.12, R3, 0.28))):
        n = 24
        for k in range(n):
            a = 2 * math.pi * k / n; p = tilt @ V((math.cos(a) * r, math.sin(a) * r, 0))
            m.box(f"Ring{band}_{k}", V((0, 0, 1.75)) + p, (2 * math.pi * r / n * 1.08, w, 0.12), col, rot=tilt @ T.Rz(a + math.pi / 2), studs=False)
    piv = V((0.85, 0, 2.9))
    with m.bone("Head", piv), m.frame(pivot=piv, scale=1.25):
        hc = V((1.1, 0, 3.45))
        bunny_head(m, T, V, hc, FUR, WHT, FUR_D, [(-0.2, 0.45, 0.6), (-0.4, 0.8, 1.85), (-0.35, 1.0, 2.6)], angry=0.12, ear_in=NEB_M)
        for s in (1, -1):
            star(m, T, V, f"EarStar{s}", hc + V((-0.3, s * 1.02, 2.8)), 0.32, GL)
        otilt = T.Ry(-0.22)
        for k in range(18):                          # small smooth orbit ring + moon over the head
            a = 2 * math.pi * k / 18; p = hc + V((0, 0, 1.3)) + otilt @ V((math.cos(a) * 1.15, math.sin(a) * 1.15, 0))
            m.box(f"Orbit{k}", p, (2 * math.pi * 1.15 / 18 * 1.15, 0.09, 0.08), GL, rot=otilt @ T.Rz(a + math.pi / 2), glow=True, studs=False)
        for s in (1, -1):
            for j, (dy, dz) in enumerate(((0.38, -0.3), (0.55, -0.42), (0.42, -0.52))):
                m.box(f"Freckle{s}{j}", hc + V((0.78, s * dy, dz)), (0.04, 0.08, 0.08), GL, glow=True, studs=False)
        m.ball("TinyMoon", hc + V((0.25, 1.12, 1.35)), 0.24, T.rgb(220, 222, 236))
    body.__exit__(None, None, None)
    return GL

def BunnyD_Rocket(m, T, V):
    """Retro cosmonaut rabbit: red + white suit, helmet with ears through the top and the gold visor flipped up,
    a finned ROCKET backpack with a big flame."""
    FUR, WHT, RED, SUIT, GOLD, GL = T.rgb(236, 226, 214), T.rgb(250, 250, 255), T.rgb(220, 48, 48), T.rgb(240, 240, 246), T.rgb(250, 196, 60), T.rgb(255, 150, 40)
    m.gait = {"hop": True}
    body = m.bone("Body", (0, 0, 1.6)); body.__enter__()
    m.box("Rump", (-0.45, 0, 1.4), (2.3, 2.2, 2.0), SUIT, top=(0.8, 0.84), bot=(0.88, 0.9))
    m.box("Chest", (0.55, 0, 1.85), (1.5, 1.9, 2.2), SUIT, top=(0.84, 0.86))
    m.box("Belt", (0.1, 0, 1.35), (3.2, 2.32, 0.32), RED, studs=False)
    m.box("Panel", (1.32, 0, 2.05), (0.12, 1.0, 0.8), T.rgb(150, 154, 170), studs=False)
    for j, (y, col) in enumerate(((-0.25, RED), (0.0, GOLD), (0.25, T.rgb(80, 200, 80)))):
        m.box(f"Btn{j}", (1.4, y, 2.15), (0.06, 0.16, 0.16), col, studs=False)
    for s in (1, -1): m.box(f"Stripe{s}", (-0.2, s * 1.12, 1.9), (2.4, 0.06, 0.25), RED, studs=False)
    bunny_legs(m, T, V, SUIT, RED)
    # rocket backpack: nose cone up, fins, flame
    rb = V((-1.45, 0, 2.2))
    m.seg("Rocket", rb + V((0, 0, -1.0)), rb + V((0, 0, 1.2)), 0.95, 0.95, SUIT, studs=False)
    m.spike("RocketNose", rb + V((0, 0, 1.15)), rb + V((0, 0, 2.0)), 0.5, RED, sides=4)
    m.box("RocketBand", rb + V((0, 0, 0.6)), (1.0, 1.0, 0.22), RED, studs=False)
    m.box("Porthole", rb + V((-0.48, 0, 0.1)), (0.06, 0.4, 0.4), T.rgb(110, 200, 255), studs=False)
    for k in range(3):
        a = math.pi / 2 + k * 2 * math.pi / 3 + math.pi / 3
        d = V((math.cos(a), math.sin(a), 0))
        m.slab(f"Fin{k}", [(0, 0), (0.8, -0.2), (0.8, -0.9), (0, -0.6)], 0.1, RED, origin=rb + d * 0.45 + V((0, 0, -0.4)), xaxis=d, yaxis=(0, 0, 1))
    m.spike("Flame", rb + V((0, 0, -1.05)), rb + V((0, 0, -2.0)), 0.45, GL, sides=5, glow=True)
    with m.bone("Tail1", (-1.6, 0, 1.0)):
        m.box("Tail", (-1.8, 0, 1.0), (0.6, 0.7, 0.6), FUR, top=(0.8, 0.8), bot=(0.8, 0.8))
    piv = V((0.85, 0, 2.85))
    with m.bone("Head", piv), m.frame(pivot=piv, scale=1.2):
        hc = V((1.1, 0, 3.45))
        bunny_head(m, T, V, hc, FUR, WHT, T.rgb(150, 120, 100), [(-0.2, 0.42, 0.6), (-0.3, 0.6, 1.9), (-0.25, 0.68, 2.7)], angry=0.18, ear_in=T.rgb(255, 170, 190))
        # open helmet: shell round the back/top/sides, rim, gold visor flipped up, antenna
        m.box("HelmBack", hc + V((-0.55, 0, 0.1)), (0.5, 2.15, 1.9), SUIT, top=(0.9, 0.9))
        m.box("HelmTop", hc + V((0.0, 0, 0.82)), (1.7, 2.1, 0.32), SUIT, top=(0.85, 0.85))
        for s in (1, -1):
            m.box(f"HelmSide{s}", hc + V((0.05, s * 0.98, -0.05)), (1.65, 0.26, 1.7), SUIT)
            m.box(f"HelmRim{s}", hc + V((0.85, s * 0.98, -0.05)), (0.12, 0.3, 1.75), RED, studs=False)
        m.box("Visor", hc + V((0.45, 0, 1.05)), (1.0, 1.8, 0.18), GOLD, rot=T.Ry(-0.35), studs=False)
        m.box("HelmChin", hc + V((0.2, 0, -0.85)), (1.6, 2.1, 0.22), SUIT)
        m.seg("Antenna", hc + V((-0.5, -0.6, 0.95)), hc + V((-0.7, -0.75, 1.75)), 0.08, 0.06, T.rgb(170, 172, 180), studs=False)
        m.box("AntTip", hc + V((-0.72, -0.76, 1.8)), (0.2, 0.2, 0.2), GL, glow=True, studs=False)
    body.__exit__(None, None, None)
    return GL

# ============================================================================ SpaceCat variations
def CatA_Astronaut(m, T, V):
    """Chunky big-headed orange tabby astronaut: white + blue suit, helmet ring, gold visor up, jetpack with blue flames."""
    FUR, STRIPE, MUZ, SUIT, BLUE, GOLD, GL = T.rgb(242, 150, 60), T.rgb(196, 98, 30), T.rgb(255, 238, 214), T.rgb(240, 242, 248), T.rgb(50, 110, 220), T.rgb(250, 196, 60), T.rgb(110, 200, 255)
    body = m.bone("Body", (0, 0, 2.0)); body.__enter__()
    z0 = cat_body(m, T, V, 3.0, 2.0, 1.75, 1.1, 0.8, SUIT, legc=SUIT, paw=BLUE)
    for s in (1, -1):
        m.box(f"SuitStripe{s}", (0, s * 1.03, z0 - 0.15), (2.7, 0.06, 0.28), BLUE, studs=False)
        m.box(f"Patch{s}", (0.6, s * 1.04, z0 + 0.35), (0.42, 0.06, 0.42), BLUE, studs=False)
        star(m, T, V, f"PatchStar{s}", V((0.6, s * 1.08, z0 + 0.35)), 0.16, GOLD, xaxis=(1, 0, 0), glow=False, thick=0.04)
    m.box("Jetpack", (-0.3, 0, z0 + 1.15), (1.4, 1.5, 0.75), SUIT, top=(0.9, 0.9))
    for s in (1, -1):
        p = V((-1.0, s * 0.45, z0 + 1.05))
        m.seg(f"Thruster{s}", p + V((0.3, 0, 0)), p, 0.45, 0.55, T.rgb(170, 172, 186), studs=False)
        m.spike(f"Flame{s}", p, p + V((-1.0, 0, -0.15)), 0.24, GL, glow=True)
    with m.bone("Tail1", (-1.5, 0, z0 + 0.3)):
        pts = [V((-1.5, 0, z0 + 0.3)), V((-2.2, 0, z0 + 0.9)), V((-2.4, 0, z0 + 1.8)), V((-2.1, 0, z0 + 2.4))]
        m.chain("Tail", pts, [0.45, 0.42, 0.38, 0.32], FUR, studs=False)
        for j in range(3): m.seg(f"TailStripe{j}", pts[j].lerp(pts[j + 1], 0.5) - (pts[j + 1] - pts[j]).normalized() * 0.06,
                                 pts[j].lerp(pts[j + 1], 0.5) + (pts[j + 1] - pts[j]).normalized() * 0.06, 0.48, 0.48, STRIPE, studs=False)
    piv = V((1.2, 0, z0 + 0.6))
    with m.bone("Head", piv), m.frame(pivot=piv, scale=1.3):
        hc = V((1.75, 0, z0 + 1.0))
        cat_head(m, T, V, hc, FUR, MUZ, T.rgb(240, 120, 140), FUR, T.rgb(255, 180, 190), T.rgb(120, 220, 120), STRIPE, angry=0.1, slit=True)
        for j in range(3): m.box(f"HeadStripe{j}", hc + V((0.3 - j * 0.3, 0, 0.76)), (0.14, 1.0, 0.06), STRIPE, studs=False)
        for s in (1, -1): m.box(f"CheekStripe{s}", hc + V((0.5, s * 0.99, 0.05)), (0.5, 0.05, 0.12), STRIPE, studs=False)
        m.box("HelmRing", hc + V((-0.45, 0, -0.95)), (1.25, 1.7, 0.3), SUIT, top=(0.9, 0.9))
        m.box("HelmBand", hc + V((-0.45, 0, -0.95)), (1.27, 1.72, 0.1), BLUE, studs=False)
        m.box("Visor", hc + V((-0.25, 0, 1.05)), (1.2, 1.9, 0.2), GOLD, rot=T.Ry(-0.25), studs=False)
        for s in (1, -1): m.box(f"VisorHinge{s}", hc + V((-0.3, s * 1.0, 0.75)), (0.3, 0.12, 0.3), SUIT, studs=False)
    body.__exit__(None, None, None)
    return GL

def CatB_Bastet(m, T, V):
    """Cosmic Bastet: Egyptian-statue sitting cat, tail wrapped round the paws; black-violet body full of nebula swirls and
    stars, glowing gold slit eyes, crescent forehead mark, gold collar with a star pendant."""
    FUR, FUR_L, NEB_M, NEB_C, NEB_V, GOLD, GL = T.rgb(32, 24, 58), T.rgb(56, 44, 96), T.rgb(206, 72, 190), T.rgb(64, 176, 226), T.rgb(120, 70, 210), T.rgb(250, 196, 60), T.rgb(255, 210, 80)
    body = m.bone("Body", (0, 0, 2.0)); body.__enter__()
    m.box("Haunch", (-0.5, 0, 1.0), (2.3, 2.3, 2.0), FUR, top=(0.82, 0.86), bot=(0.92, 0.95))
    m.box("Torso", (0.05, 0, 2.55), (1.5, 1.75, 2.4), FUR, top=(0.8, 0.84), rot=T.Ry(-0.2))
    m.box("Chest", (0.55, 0, 2.2), (0.6, 1.4, 1.9), FUR_L, top=(0.8, 0.85), rot=T.Ry(-0.2))
    for s in (1, -1):        # nebula swirl bands + stars
        for j, (x, z, w, h, a, col) in enumerate(((-0.6, 1.2, 1.6, 0.36, 0.4, NEB_M), (-0.4, 0.75, 1.3, 0.26, 0.2, NEB_C), (-0.2, 2.6, 1.0, 0.3, -0.5, NEB_V),
                                                  (0.05, 3.1, 0.7, 0.22, -0.3, NEB_M), (-0.9, 1.65, 0.8, 0.22, 0.7, NEB_V))):
            m.box(f"Swirl{s}{j}", (x, s * (1.17 if z < 1.9 else 0.9), z), (w, 0.05, h), col, rot=T.Ry(a), studs=False)
        for j, (x, z) in enumerate(((-1.0, 1.5), (-0.1, 1.0), (0.2, 2.4), (-0.4, 3.2), (-1.3, 0.6), (0.3, 1.7))):
            m.box(f"Star{s}{j}", (x, s * (1.19 if z < 1.9 else 0.92), z), (0.13, 0.05, 0.13), GL, rot=T.Ry(0.785), glow=True, studs=False)
        with m.bone(f"Leg_F{LR(s)}", (0.65, s * 0.45, 2.4)):                 # straight front legs (statue pose)
            m.box(f"FrontLeg{s}", (0.8, s * 0.45, 1.2), (0.55, 0.55, 2.4), FUR)
            m.box(f"FrontPaw{s}", (0.95, s * 0.45, 0.14), (0.75, 0.62, 0.28), FUR_L, studs=False)
        with m.bone(f"Leg_B{LR(s)}", (-0.6, s * 0.9, 1.0)):
            m.box(f"HindPaw{s}", (0.05, s * 1.0, 0.15), (1.0, 0.6, 0.3), FUR_L, studs=False)
    pts = [V((-1.6, 0, 0.5)), V((-1.2, -1.3, 0.3)), V((0.0, -1.5, 0.28)), V((1.1, -1.1, 0.3)), V((1.45, -0.3, 0.42))]   # tail wraps the paws
    m.chain("Tail", pts, [0.4, 0.38, 0.36, 0.33, 0.28], FUR, bones="Tail")
    with m.bone("Tail4"): m.box("TailTip", pts[-1] + V((0.12, 0.1, 0.05)), (0.36, 0.36, 0.36), GL, glow=True, studs=False)
    for k in range(10):          # gold collar + star pendant
        a = 2 * math.pi * k / 10; p = V((0.45, 0, 3.55)) + V((math.cos(a) * 0.75, math.sin(a) * 0.85, 0.0))
        m.box(f"Collar{k}", p, (0.5, 0.36, 0.22), GOLD, rot=T.Rz(a + math.pi / 2), studs=False)
    star(m, T, V, "Pendant", V((1.27, 0, 3.25)), 0.26, GOLD, glow=False, thick=0.1)
    piv = V((0.4, 0, 3.7))
    with m.bone("Head", piv), m.frame(pivot=piv, scale=1.2):
        hc = V((0.75, 0, 4.4))
        cat_head(m, T, V, hc, FUR, FUR_L, T.rgb(200, 120, 200), FUR, NEB_M, GL, T.rgb(14, 10, 26), angry=0.3, slit=True, eye_glow=True)
        cres = [(math.cos(a) * 0.24, math.sin(a) * 0.24) for a in [0.6 + i * 0.6 for i in range(9)]] + \
               [(math.cos(a) * 0.15 + 0.08, math.sin(a) * 0.15) for a in [5.2 - i * 0.55 for i in range(7)]]
        m.slab("Crescent", cres, 0.06, GOLD, origin=hc + V((0.81, 0, 0.58)), xaxis=(0, 1, 0), yaxis=(0, 0, 1))
        for s in (1, -1): m.box(f"EarRing{s}", hc + V((-0.12, s * 0.98, 0.95)), (0.08, 0.2, 0.2), GOLD, studs=False)
    body.__exit__(None, None, None)
    return GL

def CatC_Alien(m, T, V):
    """Alien cat: teal skin with glowing spots, a glowing THIRD EYE, long antenna ear tufts, crystal growths on the back,
    three orbiting orbs, a thin tail ending in a glowing orb."""
    SKIN, SKIN_D, BELLY, CRY, GL = T.rgb(60, 176, 160), T.rgb(30, 110, 104), T.rgb(170, 236, 214), T.rgb(150, 110, 230), T.rgb(190, 255, 90)
    body = m.bone("Body", (0, 0, 2.0)); body.__enter__()
    z0 = cat_body(m, T, V, 3.2, 1.7, 1.5, 1.35, 0.66, SKIN, belly=BELLY, paw=SKIN_D)
    for s in (1, -1):
        for j, (x, z, r) in enumerate(((-0.9, 0.2, 0.32), (-0.2, 0.35, 0.24), (0.5, 0.1, 0.28), (-0.6, -0.25, 0.22), (0.9, 0.4, 0.2))):
            m.box(f"Spot{s}{j}", (x, s * 0.88, z0 + z), (r, 0.06, r), GL, glow=True, studs=False)
    for k, (x, y, h, lean) in enumerate(((-0.2, 0.0, 1.2, -0.2), (-0.6, 0.35, 0.9, -0.35), (-0.7, -0.3, 0.8, -0.3), (0.3, 0.25, 0.7, -0.1), (-1.0, 0.0, 0.6, -0.4))):
        b = V((x, y, z0 + 0.7)); t = b + V((lean, y * 0.6, h * 1.35))
        m.spike(f"Crystal{k}", b, t, 0.3, CRY, sides=5)
        m.spike(f"CrystalTip{k}", b.lerp(t, 0.6), t + (t - b).normalized() * 0.05, 0.13, GL, sides=5, glow=True)
    for k in range(3):
        a = k * 2.1; p = V((math.cos(a) * 2.3, math.sin(a) * 2.3, z0 + 1.6 + 0.3 * math.sin(a))); m.ball(f"Orb{k}", p, 0.28, GL)
    pts = [V((-1.55, 0, z0 + 0.3)), V((-2.4, 0, z0 + 0.6)), V((-3.0, 0, z0 + 1.4)), V((-3.0, 0, z0 + 2.2))]
    m.chain("Tail", pts, [0.3, 0.24, 0.2, 0.16], SKIN, studs=False, bones="Tail")
    with m.bone("Tail3"): m.ball("TailOrb", pts[-1] + V((0, 0, 0.25)), 0.32, GL)
    piv = V((1.3, 0, z0 + 0.55))
    with m.bone("Head", piv), m.frame(pivot=piv, scale=1.25):
        hc = V((1.85, 0, z0 + 0.95))
        cat_head(m, T, V, hc, SKIN, BELLY, SKIN_D, SKIN, CRY, T.rgb(20, 20, 30), SKIN_D, angry=0.2, slit=False)
        for s in (1, -1):
            m.box(f"EyeShine{s}", hc + V((0.96, s * 0.34, 0.34)), (0.04, 0.16, 0.16), T.WHITE, studs=False)
            m.box(f"EyeShine2{s}", hc + V((0.96, s * 0.55, 0.06)), (0.04, 0.08, 0.08), T.WHITE, studs=False)
        m.box("ThirdEyeRim", hc + V((0.79, 0, 0.62)), (0.14, 0.56, 0.44), SKIN_D, studs=False)
        m.box("ThirdEye", hc + V((0.86, 0, 0.62)), (0.08, 0.42, 0.32), GL, glow=True, studs=False)
        m.box("ThirdPupil", hc + V((0.9, 0, 0.62)), (0.04, 0.08, 0.28), T.PUPIL, studs=False)
        for s in (1, -1):
            b = hc + V((-0.2, s * 0.62, 1.35))
            m.seg(f"Antenna{s}", b, b + V((-0.3, s * 0.35, 1.1)), 0.08, 0.06, SKIN_D, studs=False)
            m.ball(f"AntennaTip{s}", b + V((-0.32, s * 0.38, 1.18)), 0.15, GL)
    body.__exit__(None, None, None)
    return GL

def CatD_Cyber(m, T, V):
    """Cyber space panther: sleek navy body under white sci-fi armour plates with glowing cyan seams, visor-slit face
    plate, back thrusters with flames, energy-blade tail tip. Calm, lethal (closed mouth)."""
    BODY, ARM, ARM_D, GL = T.rgb(30, 36, 70), T.rgb(232, 236, 246), T.rgb(150, 160, 186), T.rgb(80, 230, 255)
    body = m.bone("Body", (0, 0, 2.2)); body.__enter__()
    z0 = cat_body(m, T, V, 3.8, 1.6, 1.4, 1.65, 0.6, BODY, paw=ARM_D)
    m.box("BackPlate", (-0.2, 0, z0 + 0.72), (2.4, 1.4, 0.26), ARM, top=(0.8, 0.85))
    m.box("Seam", (-0.2, 0, z0 + 0.86), (2.2, 0.1, 0.05), GL, glow=True, studs=False)
    for s in (1, -1):
        m.box(f"Shoulder{s}", (1.2, s * 0.86, z0 + 0.3), (1.1, 0.28, 0.9), ARM, top=(0.8, 0.8))
        m.box(f"ShoulderSeam{s}", (1.2, s * 1.01, z0 + 0.3), (0.9, 0.04, 0.08), GL, glow=True, studs=False)
        m.box(f"Hip{s}", (-1.3, s * 0.86, z0 + 0.25), (1.0, 0.28, 0.85), ARM, top=(0.8, 0.8))
        m.box(f"HipSeam{s}", (-1.3, s * 1.01, z0 + 0.1), (0.8, 0.04, 0.08), GL, glow=True, studs=False)
        for sx in (1, -1):
            x = sx * (3.8 / 2 - 0.6 * 0.65); y = s * (1.6 / 2 - 0.6 * 0.55)
            with m.bone(f"Leg_{'F' if sx > 0 else 'B'}{LR(s)}"):
                m.box(f"Greave{sx}{s}", (x + 0.05, y, 0.75), (0.68, 0.68, 0.7), ARM, studs=False)
                m.box(f"GreaveSeam{sx}{s}", (x + 0.4, y, 0.75), (0.04, 0.4, 0.1), GL, glow=True, studs=False)
        p = V((-0.9, s * 0.45, z0 + 0.95))
        m.seg(f"Thruster{s}", p + V((0.5, 0, 0)), p, 0.38, 0.46, ARM_D, studs=False)
        m.spike(f"Flame{s}", p, p + V((-1.0, 0, -0.1)), 0.2, GL, glow=True)
    pts = [V((-1.85, 0, z0 + 0.3)), V((-2.8, 0, z0 + 0.5)), V((-3.6, 0, z0 + 1.0)), V((-4.1, 0, z0 + 1.7))]
    m.chain("Tail", pts, [0.36, 0.3, 0.25, 0.2], BODY, studs=False, bones="Tail")
    with m.bone("Tail3"): m.spike("TailBlade", pts[-1], pts[-1] + V((-0.3, 0, 1.1)), 0.22, GL, flat=0.3, glow=True)
    piv = V((1.6, 0, z0 + 0.5))
    with m.bone("Head", piv), m.frame(pivot=piv, scale=1.2):
        hc = V((2.15, 0, z0 + 0.8))
        cat_head(m, T, V, hc, BODY, T.rgb(50, 58, 100), T.rgb(20, 22, 40), BODY, GL, GL, T.rgb(10, 12, 24), angry=0.45, slit=False, eye_glow=True)
        m.box("FacePlate", hc + V((0.1, 0, 0.62)), (1.5, 1.7, 0.3), ARM, top=(0.85, 0.9))
        m.box("PlateSeam", hc + V((0.55, 0, 0.8)), (0.6, 0.08, 0.05), GL, glow=True, studs=False)
        for s in (1, -1): m.box(f"Cheekguard{s}", hc + V((0.1, s * 1.0, -0.15)), (1.2, 0.14, 0.7), ARM, studs=False)
    body.__exit__(None, None, None)
    return GL

BUNNIES = [BunnyA_MoonRock, BunnyB_Comet, BunnyC_Saturn, BunnyD_Rocket]
CATS = [CatA_Astronaut, CatB_Bastet, CatC_Alien, CatD_Cyber]

def build_one(fn):
    T, V = K()
    m = T.Model(fn.__name__, os.path.join(OUT, fn.__name__), stud=0.42, chamfer=0.17, jitter=0.05)
    glow = fn(m, T, V)
    m.done(views=VIEWS, glow_color=glow)

def sheet():
    from PIL import Image, ImageDraw
    for label, fns in (("Bunny", BUNNIES), ("Cat", CATS)):
        Tz = 380; out = Image.new("RGB", (Tz * 3, Tz * 4), "white"); d = ImageDraw.Draw(out)
        for r, fn in enumerate(fns):
            for c, (v, *_r) in enumerate(VIEWS):
                p = os.path.join(OUT, fn.__name__, "previews", f"{fn.__name__}_{v}.png")
                if os.path.exists(p): out.paste(Image.open(p).convert("RGB").resize((Tz, Tz)), (c * Tz, r * Tz))
            d.rectangle([4, r * Tz + 4, 200, r * Tz + 26], fill="white"); d.text((10, r * Tz + 9), fn.__name__, fill="black")
        out.save(os.path.join(OUT, f"{label}_variants.png")); print("SHEET", label)

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--sheet" in sys.argv: sheet(); sys.exit()
    if "--child" in sys.argv:
        build_one(next(f for f in BUNNIES + CATS if f.__name__ == want[0])); sys.exit()
    for fn in BUNNIES + CATS:
        if want and fn.__name__ not in want: continue
        print("BUILD", fn.__name__, flush=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), fn.__name__, "--child"], capture_output=True, text=True)
        tl = [l for l in r.stdout.splitlines() if l.startswith("TRIS")]
        print("  ", tl[-1] if tl else "", flush=True)
        if r.returncode: print("FAILED", fn.__name__, r.stderr[-1500:], flush=True)
