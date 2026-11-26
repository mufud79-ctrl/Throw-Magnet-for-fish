"""Ember Breath (hybrid B) - a short cone breath (10 studs) sweeping 50 degrees. Signature: a FAN-SHAPED scorched wedge
burned into the sand, with one continuous low curtain of fire licking along its arc - short and wide, the opposite of
the full form's long line.

Beat sheet (fluid: the body rears back, then the head leads the sweep)
  0.00-0.30  inhale: rear back, heat swells at the mouth (glow + swirl), embers and shimmer sucked in  (anticipation)
  0.30       release: a glint at the mouth; the cone bursts out (squash: short and fat, then it stretches to length)
  0.30-1.10  the breath: ONE fused tapered ribbon of rolling flame from the mouth to the sand, sweeping left -> right;
             billows roll at the cone's mouth, an ember spray streams out, black smoke rides its top; where it touches
             the sand it draws a continuous curtain of fire along the arc and scorches it; hit-stop 0.04 on each target
  1.10-1.50  the breath cuts; smoke curls from the mouth; the wedge smoulders: flickers, after-smoke, shimmer
GAP: no jaw mask on the avatar yet (rig v2 `attach`, rigging session); the breath leaves the head.
Camera: gameplay view.
Run: python3 lab/dragon/moves/ember_breath.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa
from kit import _keys

TR, TC = 0.30, 1.10
DUR = 1.55
REACH = 10.0
A0, A1 = -25.0, 25.0
TARGETS = [[-2.6, 0, -8.6], [2.4, 0, -9.4]]

POSE = {
    "lean": smooth([[0, 0], [0.24, 18], [TR, 16], [TR + 0.06, -14], [0.7, -12], [TC, -10], [1.3, -2], [DUR, 0]]),
    "twist": smooth([[0, 0], [0.24, 20], [TR, 22], [TR + 0.08, -A0 * 0.9], [0.7, 0], [TC, -A1 * 0.9], [1.3, -18], [DUR, -10]]),
    "armR": smooth([[0, 0], [0.24, -30], [TR + 0.06, -50], [TC, -40], [1.4, 0], [DUR, 0]]),
    "armL": smooth([[0, 0], [0.24, -30], [TR + 0.06, -50], [TC, -40], [1.4, 0], [DUR, 0]]),
    "armRz": smooth([[0, 0], [0.24, 25], [TC, 30], [1.4, 0], [DUR, 0]]),
    "armLz": smooth([[0, 0], [0.24, -25], [TC, -30], [1.4, 0], [DUR, 0]]),
    "scale": smooth([[0, [1, 1, 1]], [0.24, [0.96, 1.06, 0.96]], [TR + 0.05, [1.05, 0.95, 1.05]], [0.6, [1, 1, 1]], [DUR, [1, 1, 1]]]),
}


def mouth(t):
    lean = _keys(POSE["lean"], t, 0) * math.pi / 180
    tw = _keys(POSE["twist"], t, 0) * math.pi / 180
    v = [0, 2.55, -0.75]
    c, s = math.cos(lean), math.sin(lean)
    v = [v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c]
    v = [v[0] * math.cos(tw) + v[2] * math.sin(tw), v[1], -v[0] * math.sin(tw) + v[2] * math.cos(tw)]
    return [v[0], v[1] + 2, v[2]]


def contact(t, r=REACH, y=0.4):
    k = min(1.0, max(0.0, (t - TR) / (TC - TR)))
    k = k * k * (3 - 2 * k)
    a = math.radians(A0 + (A1 - A0) * k)
    return [math.sin(a) * r, y, -math.cos(a) * r]


def keyed(fn, t0, t1, n=40, **kw):
    """Keys over a layer's life (0..1) sampled from fn(t)."""
    return [[round(i / n, 4), R(fn(t0 + (t1 - t0) * i / n, **kw))] for i in range(n + 1)]


def path(fn, t0, t1, n=60, **kw):
    return [[R(t0 + (t1 - t0) * i / n, 4), R(fn(t0 + (t1 - t0) * i / n, **kw))] for i in range(n + 1)]


def build():
    L = [ambience([0, 0, -5], 0, DUR, radius=10, rate=9, seed=901)]
    mp = path(mouth, 0, DUR)
    # ---- inhale: heat swells at the mouth, embers + shimmer pulled in
    L.append(glow_orb(mp[0][1], 0, 3.0, life=0.2, rate=[[0.02, TR, 16]], path=mp, locked=True, tr=0.4, seed=902))
    L += swirl(mp[0][1], 0.02, TR + 0.02, 3.0, path=mp, seed=903)
    L.append({"type": "emitter", "at": mouth(0.15), "part": [6, 5, 6], "rate": [[0.0, TR - 0.02, 40]], "seed": 904, "props": {
        "Texture": "spark_streak", "Color": PALS["fire"]["spark"], "LightEmission": 1, "Brightness": 1.5, "Shape": "Sphere", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "Size": [[0, 1.4], [1, 0.4]], "Lifetime": [0.12, 0.16], "Speed": [20, 26], "Orientation": "VelocityParallel",
        "Transparency": [[0, 0.3], [1, 0.8]], "ZOffset": 0.3}})
    L.append(haze(mouth(0.1), 0.0, TR + 0.1, size=6, seed=905))

    # ---- release
    L += glint(mouth(TR), TR, size=4.5, life=0.2, seed=906)
    L.append(flare(mouth(TR), TR, size=9, life=0.18, seed=907))

    # ---- the cone: ONE fused tapered ribbon of rolling flame (camera-facing Beams of the torrent strips)
    life = TC - TR + 0.08
    frm = keyed(mouth, TR, TR + life)
    to = keyed(contact, TR, TR + life)
    wk = [[0, [0.5, 2.0]], [0.08, [1.0, 4.6], "out"], [0.85, [0.9, 4.2]], [1, [0.3, 1.4], "in"]]
    reach = [[0, 0.15], [0.06, 1, "out"], [0.9, 1], [1, 1]]
    for lay, wm, sp in (("rim", 1.0, 3.2), ("mid", 0.72, 3.8), ("core", 0.26, 4.6)):
        L.append({"type": "beam", "from": frm, "to": to, "t0": TR, "life": life, "textures": [f"{st}_{lay}" for st in STRIPS], "swap": 0.06,
                  "textureLength": 6, "textureSpeed": sp, "segments": 12, "color": PALS["fire"]["HOT"][lay], "lightEmission": LE[lay],
                  "brightness": BR[lay], "width": [[k, [w[0] * wm, w[1] * wm]] + e for k, w, *e in wk], "reach": reach,
                  "transparency": [[0, 0], [0.9, 0.05], [1, 0.6]]})
    # volume: billows rolling INSIDE the cone at three depths (small near the mouth, big at the far end) - a torrent,
    # never a laser
    for j, (f, sz, rt) in enumerate(((0.3, 3.6, 22), (0.58, 5.4, 20), (0.82, 7.0, 18))):
        bp = [[R(TR + (TC - TR) * i / 40, 4), R([m + (c - m) * f for m, c in zip(mouth(TR + (TC - TR) * i / 40), contact(TR + (TC - TR) * i / 40, y=1.4 + 0.8 * (1 - f)))])] for i in range(41)]
        for e in billow(bp[0][1], TR, sz, life=0.32, seed=917 + j * 3, grow=1.3, rot=60 * j):
            e.pop("emits", None); e["rate"] = [[TR + 0.03 * j, TC, rt]]; e["path"] = bp
            L.append(e)
    # billows rolling at the cone's mouth (riding the contact point), an ember spray, smoke riding the top
    cp = path(contact, TR, TC, y=1.6)
    for e in billow(cp[0][1], TR, 4.8, life=0.45, seed=911, grow=1.35):
        e.pop("emits", None); e["rate"] = [[TR + 0.04, TC, 18]]; e["path"] = cp
        L.append(e)
    L.append(embers(cp[0][1], 0, rate=[[TR, TC, 70]], speed=(8, 18), life=(0.35, 0.7), grav=-10, spread=60, path=cp, seed=912))
    L.append(smoke([0, 4.5, -6], 0, rate=[[TR + 0.1, TC + 0.05, 14]], size=(3.5, 7), speed=(2, 4), life=(0.9, 1.3), seed=913,
                   path=path(contact, TR, TC, r=REACH * 0.7, y=4.8)))
    L += wisps(cp[0][1], TR, TC, 16, size=2.6, life=0.45, path=cp, seed=914)
    L.append(glow_pool([0, 0, -8], TR, 9, life=0.3, rate=[[TR, TC, 14]], peak=0.4, seed=916, path=path(contact, TR, TC, y=0)))

    # ---- the scorched wedge: a continuous curtain of fire drawn along the arc where the breath touches, scorch fan
    gp = path(contact, TR + 0.03, TC, y=1.15)
    for lay in ("rim", "mid", "core"):
        L.append({"type": "trail", "path": gp, "at": gp[0][1], "t0": TR + 0.03, "t1": TC, "lifetime": 0.9, "width": 2.3, "up": [0, 1, 0],
                  "textures": [f"{w}_{lay}" for w in WALLS], "swap": 0.07, "textureMode": "Wrap", "textureLength": 7,
                  "color": PALS["fire"]["HOT"][lay], "lightEmission": LE[lay], "brightness": BR[lay],
                  "transparency": [[0, 0], [0.7, 0.1], [1, 1]], "widthScale": [[0, 1], [0.7, 0.85], [1, 0.4]]})
    for k in range(7):
        u = k / 6
        a = math.radians(A0 + (A1 - A0) * u)
        for rr, sz in ((REACH * 0.55, 4.5), (REACH * 0.92, 5.5)):
            L.append(scorch([math.sin(a) * rr, 0, -math.cos(a) * rr], TR + 0.06 + (TC - TR) * u, size=sz, life=2.0, seed=921 + k * 2 + int(rr)))
        L += flicker([math.sin(a) * REACH * 0.9, 0, -math.cos(a) * REACH * 0.9], TR + 0.15 + (TC - TR) * u, DUR, 1.3 + 0.3 * (k % 2), seed=941 + k)

    # ---- targets: the cone sweeps across them
    hits, numbers = [], []
    stops = []
    for i, q in enumerate(TARGETS):
        a = math.degrees(math.atan2(q[0], -q[2]))
        k = (a - A0) / (A1 - A0)
        k = min(1, max(0, k))
        # invert the smoothstep sweep to find when the cone passes the target
        lo, hi = 0.0, 1.0
        for _ in range(30):
            mid = (lo + hi) / 2
            (lo, hi) = (mid, hi) if mid * mid * (3 - 2 * mid) < k else (lo, mid)
        th = TR + (TC - TR) * lo
        L += impact([q[0], 3.0, q[2] + 0.8], th, size=5, life=0.4, seed=951 + i)
        L += ember_spray([q[0], 3.0, q[2] + 0.6], th, size=5, life=0.45, seed=953 + i)
        L += wisps([q[0], 2.5, q[2]], th, th + 0.6, 10, size=2.2, life=0.45, seed=955 + 3 * i)
        hits.append({"t": th, "dummy": i, "dir": [0, 0, -1], "power": 0.4})
        numbers.append({"t": th + 0.02, "at": [q[0] + 1.0, 6.2, q[2]], "text": str(31 + 6 * i), "color": GOLD, "vel": [0, 9, 0], "size": 1.5})
        stops.append({"t": th + 0.02, "dur": 0.04})

    # ---- after: smoke curls from the mouth, after-smoke off the wedge, shimmer
    L.append(smoke_wisps(mouth(TC + 0.1), TC, DUR, 6, size=2.2, part=[0.4, 0.3, 0.4], seed=961))
    L.append(smoke_wisps([0, 0.4, -8], TC - 0.2, DUR, 10, size=3.5, part=[12, 0.2, 4], seed=962))
    L.append(haze([0, 3.5, -8], TR, DUR, size=13, seed=963))

    return {
        "name": "dragon_05_EmberBreath", "title": "Ember Breath", "element": "Dragon", "archetype": "cone_breath", "duration": DUR,
        "layers": L, "dummies": TARGETS, "hits": hits, "numbers": numbers,
        "hitstop": sorted(stops, key=lambda h: h["t"]),
        "shakes": [{"t": TR, "amp": 0.25, "dur": 0.8, "freq": 18}],
        "lights": [light(mouth(0), [[0, 0], [TR - 0.05, 10], [TR, 30], [TC, 26], [TC + 0.3, 0]], rng=18,
                         path=path(contact, 0, DUR, y=2.0))],
        "pose": POSE,
        "camera": GAMEPLAY_CAM,
        "poster": 0.7,
    }


write(build(), out_path(os.path.dirname(__file__), "dragon_05_EmberBreath"), form="hybrid")
print("wrote dragon_05_EmberBreath.json")
