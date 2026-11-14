"""TFFA Kraken (Mythic Isles) - custom hero build from the user's reference painting (giant octopus vs submarine).

Reference analysis (most important first):
1. Silhouette: a gigantic bulbous, wrinkled mantle is the dominant mass, rising above everything, face looming forward;
   a mass of huge tentacles radiates everywhere - several arch in big loops higher than the head, some reach forward.
2. Head: no visible mouth; small slit-like glowing orange eyes on the sides of the bulb under heavy wrinkled brow
   ridges; warty, bumpy skin (studs + wart blocks).
3. Tentacles: enormously thick at the base, smooth curves, tips curling into spirals; big pale teal suckers with dark
   centres along the inner/under side of every curl.
4. Colours: slate blue-grey, darker shading, pale teal suckers, glowing orange eyes.
Bones: Body, Tent<k>_<j>. Studded."""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from tffa_kit import *
from mathutils import Vector, Matrix

SKIN, SKIN_D, SKIN_L = rgb(70, 92, 112), rgb(46, 62, 78), rgb(98, 124, 146)
SUC, SUC_D, EYE = rgb(130, 186, 196), rgb(40, 70, 82), rgb(255, 146, 36)
V = lambda *a: Vector(a)

m = Model("Kraken", sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None, stud=0.75, chamfer=0.16, jitter=0.07)
m.gait = {"amp": 0.7}
body = m.bone("Body", (0, 0, 4.0)); body.__enter__()

# ---------------------------------------------------------------- mantle: a smooth egg LEANING BACK (two long tilted tapered blocks)
BASE, MID, TOP = V(0.9, 0, 2.9), V(-0.5, 0, 6.9), V(-2.9, 0, 10.6)
HF = m.frame(pivot=(0.6, 0, 2.2), scale=1.35); HF.__enter__()      # the head is the colossal focal mass
m.box("Skirt", (0.6, 0, 2.55), (4.4, 5.2, 1.5), SKIN, top=(0.95, 0.95), bot=(0.8, 0.8))
m.seg("MantleLow", BASE, MID, 5.0, 5.9, SKIN, d0=4.4, d1=5.4)
m.seg("MantleHigh", MID - (MID - BASE).normalized() * 0.3, TOP, 5.9, 2.4, SKIN, d0=5.4, d1=2.0)
m.seg("MantleTip", TOP - (TOP - MID).normalized() * 0.4, TOP + (TOP - MID).normalized() * 0.5, 2.2, 1.0, SKIN, d0=1.9, d1=0.8)
def egg(t, a, rad=1.0):
    """Point on the egg surface: t 0..1 along base->top, a = angle round the axis (0 = front)."""
    if t < 0.5: c = BASE.lerp(MID, t * 2); w, d = 5.0 + 0.9 * t * 2, 4.4 + 1.0 * t * 2
    else: c = MID.lerp(TOP, (t - 0.5) * 2); w, d = 5.9 - 3.5 * (t - 0.5) * 2, 5.4 - 3.4 * (t - 0.5) * 2
    ax = (TOP - BASE).normalized(); fw = V(ax.z, 0, -ax.x)
    return c + fw * math.cos(a) * d / 2 * rad + V(0, 1, 0) * math.sin(a) * w / 2 * rad
# warts scattered over the egg, a darker crest of bumps down the back
rnd = random.Random(7)
for k in range(12):
    q = egg(rnd.uniform(0.35, 0.92), rnd.uniform(-2.6, 2.6), 0.98); ww = rnd.uniform(0.3, 0.5)
    m.box(f"Wart{k}", q, (ww, ww, ww * 0.8), SKIN_L if k % 3 else SKIN_D, studs=False)

# ---------------------------------------------------------------- face on the front slope: eye bulges, glowing eyes, angry V creases
for s in (1, -1):
    m.box(f"EyeBulge{s}", (2.0, s * 1.85, 5.45), (1.6, 1.5, 1.45), SKIN, top=(0.8, 0.85), rot=Ry(-0.3))
    for j in range(3):          # angry creases rising from between the eyes up the forehead
        m.box(f"Crease{s}{j}", (1.95 - j * 0.45, s * (0.55 + j * 0.35), 6.6 + j * 0.55), (0.3, 1.5, 0.24), SKIN_D, rot=Rx(-s * 0.5) @ Ry(-0.45), studs=False)
m.eyes((2.62, 1.95, 5.5), facing=(0.88, 0.42, 0.2), size=(1.35, 0.68), pupil=0.72, look=(0.45, 0), angry=0.45, white=EYE, glow_white=True,
       brow_col=SKIN_D, brow_h=0.45, brow_up=0.72, brow_w=1.2, depth=0.22)
m.seg("Siphon", V(0.4, 2.45, 3.6), V(1.2, 3.0, 3.0), 0.6, 0.46, SKIN_D)
m.box("SiphonEnd", (1.32, 3.07, 2.95), (0.22, 0.55, 0.55), SKIN_D, studs=False)
HF.__exit__(None, None, None)

# ---------------------------------------------------------------- tentacles
def catmull(ctrl, n):
    pts = [ctrl[0]] + list(ctrl) + [ctrl[-1]]; out = []
    for i in range(n):
        u = i / (n - 1) * (len(ctrl) - 1); j = min(int(u), len(ctrl) - 2); t = u - j
        p0, p1, p2, p3 = pts[j], pts[j + 1], pts[j + 2], pts[j + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return out

UP = V(0, 0, 1)
def tentacle_ctrl(kind, o, f):
    """Control points relative to the base, in (outward o, up z) plus a forward bias f."""
    if kind == "reach":    # forward along the ground toward the viewer, then up into an inward spiral
        return [V(0, 0, 0), o * 1.6 - UP * 1.6, o * 3.4 - UP * 2.0 + f * 0.8, o * 5.0 - UP * 1.5 + f * 1.6, o * 5.8 + UP * 0.2 + f * 2.0,
                o * 5.1 + UP * 1.5 + f * 1.8, o * 4.2 + UP * 1.0 + f * 1.3, o * 4.4 + UP * 0.2 + f * 1.1]
    if kind == "arch":     # out of the side, a huge loop above head height, tip curling down
        return [V(0, 0, 0), o * 1.6 - UP * 1.0, o * 3.3 + UP * 0.2, o * 4.1 + UP * 2.3, o * 3.8 + UP * 4.4, o * 2.8 + UP * 5.2,
                o * 2.0 + UP * 4.6, o * 2.3 + UP * 3.9]
    if kind == "plant":    # wide on the ground, tip curls up and back in a spiral
        return [V(0, 0, 0), o * 1.7 - UP * 1.7, o * 3.6 - UP * 2.1, o * 5.4 - UP * 2.0, o * 6.6 - UP * 1.3, o * 6.7 - UP * 0.1,
                o * 6.0 + UP * 0.3, o * 5.7 - UP * 0.4]
    # "rear": rises behind in an S, visible past the mantle
    return [V(0, 0, 0), o * 1.5 - UP * 1.2, o * 2.9 + UP * 0.3, o * 3.3 + UP * 2.6, o * 4.4 + UP * 4.4, o * 5.4 + UP * 5.0,
            o * 5.8 + UP * 4.2, o * 5.3 + UP * 3.7]

LAYOUT = [(44, "reach"), (-44, "reach"), (84, "arch"), (-84, "arch"), (126, "plant"), (-126, "plant"), (166, "rear"), (-166, "rear")]
WS = [1.75, 1.55, 1.32, 1.08, 0.85, 0.64, 0.45, 0.28]
for k, (deg, kind) in enumerate(LAYOUT):
    a = math.radians(deg); o = V(math.cos(a), math.sin(a), 0); f = V(1, 0, 0)
    b = V(0.6, 0, 2.4) + o * 2.3
    pts = [b + p * 1.12 for p in catmull(tentacle_ctrl(kind, o, f), 8)]
    bones = [f"Tent{k}_{j}" for j in range(len(pts) - 1)]
    m.chain(f"Tent{k}", pts, WS, SKIN, bones=bones)
    for j in range(1, len(pts) - 1):                  # suckers on the inner side of the curl (underside where straight)
        with m.bone(bones[j]):
            t_ = (pts[j + 1] - pts[j - 1]).normalized()
            cv = pts[j + 1] - 2 * pts[j] + pts[j - 1]; cv = cv - t_ * cv.dot(t_)
            nrm = cv.normalized() if cv.length > 0.12 else (-UP - t_ * (-UP).dot(t_)).normalized()
            if kind == "plant" and j < 4: nrm = (-UP - t_ * (-UP).dot(t_)).normalized()
            bn = nrm.cross(t_).normalized(); R = Matrix((t_, bn, nrm)).transposed()
            for tt in ((0.5,) if j == 1 else (0.0, 0.5)):          # j=1 sits under the head: one sucker
                q = pts[j].lerp(pts[j + 1], tt); w = WS[j] + (WS[j + 1] - WS[j]) * tt
                m.box(f"Sucker{k}_{j}_{tt}", q + nrm * w * 0.44, (w * 0.62, w * 0.62, w * 0.2), SUC, rot=R, studs=False)
                if tt == 0.5 and j >= 2:                              # dark centres (triangle budget: not on every sucker)
                    m.box(f"SuckerHole{k}_{j}_{tt}", q + nrm * (w * 0.44 + w * 0.08), (w * 0.28, w * 0.28, w * 0.1), SUC_D, rot=R, studs=False, chamfer=0.05)

body.__exit__(None, None, None)
m.done(views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45), ("ref", 15, 18, 45)], glow_color=EYE)
