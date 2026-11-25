"""Plasma Bomb (M) - hold-charge lob. Signature: a 3D plasma orb that drinks lightning out of the ground, implodes and
bursts into radial waves of cel arcs, then plasma beads race down braided tethers to encase each chained target.

Beat sheet (rework v2: nothing here is shared with the other moves' impacts)
  0.00-0.74  CHARGE overhead: a plasma orb grows above the raised palm (neon core inside a ball of cel arcs flickering
             across its surface, crackle bush, tendrils leaping off it); arcs leap UP out of the sand
             into it; dust is dragged inward; a burn spreads under the caster                    (anticipation)
  0.74-0.82  the orb pinches, then swells; the caster coils back                                (squash)
  0.82       overhand LOB: the orb flies a high arc trailing plasma and dripping static          (arcs, follow-through)
  1.32       IMPLODE: the orb collapses to a point, arcs sucked in, a beat of darkness            (anticipation)
  1.40       BLOOM: three radial waves of cel arcs burst out over enemy A from a neon flash,
             white flash frame, hit-stop 0.1; scorched plasma pool, dark smoke at the rim          (timing)
  1.47-1.80  CHAIN: braided plasma tethers lash A -> B -> C; a bright plasma bead races down each tether and
             ENCASES the target in a small plasma sphere that pops (hit-stop 0.05 each)
  1.80-2.60  tethers flicker and cool to indigo; static clings; scars cool                       (calling card)
Run: python3 lab/thunder/moves/plasma_bomb.py
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kit import *  # noqa

TR = 0.82                  # release
TI = 1.32                  # impact -> implode
TB = 1.40                  # bloom
ORB = [1.5, 7.6, -0.3]     # above the raised palm
IMPACT = [0.0, 1.8, -19.5]
A, B, Cc = [0, 0, -20], [-7, 0, -27], [6, 0, -30]
chest = lambda d: [d[0], 3.4, d[2]]
rnd = random.Random(11)


def orb_path():
    P = [[0.0, ORB], [TR, ORB]]
    for i in range(1, 17):
        u = i / 16
        p = [ORB[j] + (IMPACT[j] - ORB[j]) * u for j in range(3)]
        p[1] += 5.0 * math.sin(math.pi * u)
        P.append([round(TR + (TI - TR) * u, 4), [round(v, 3) for v in p]])
    return P


def _keys_at(keys, k):
    """Linear read of [[k, value, ease?], ...] (python side, for placing short-lived arcs)."""
    if k <= keys[0][0]:
        return keys[0][1]
    for (k0, v0, *_), (k1, v1, *_) in zip(keys[:-1], keys[1:]):
        if k <= k1:
            u = (k - k0) / ((k1 - k0) or 1)
            return [a + (b - a) * u for a, b in zip(v0, v1)] if isinstance(v0, list) else v0 + (v1 - v0) * u
    return keys[-1][1]


def anime_ball(where, t0, life, radius_keys, *, tex="plasma_ball_v2", mode="Loop", fps=24, rot=0, z=0.3, colors=None, fade=None):
    """ONE cage of cel lightning (plasma_ball_v2 flipbook, house strokes): one locked particle per cel layer spanning the
    whole life, its Size sequence carrying the radius keys (charge, pinch, swell, implode). where: point or path."""
    S = 3.0                                              # quad size per stud of visual radius (texture cage r ~0.33 of quad)
    ks = []
    for k in [i / 24 for i in range(25)]:
        ks.append([round(k, 4), round(max(0.05, _keys_at([[a, b] for a, b, *_ in radius_keys], k)) * S, 3)])
    out = []
    is_path = isinstance(where[0], list)
    for i, L in enumerate(LAYERS):
        props = {"Texture": f"{tex}_{L}", "Color": (colors or HOT)[L], "LightEmission": LE[L], "Brightness": BR[L], "Size": ks,
                 "Lifetime": [life, life], "Speed": [0.01, 0.01], "Rotation": [rot, rot], "LockedToPart": True,
                 "FlipbookLayout": "Grid4x4", "FlipbookMode": mode, "FlipbookFramerate": [fps, fps], "ZOffset": round(z + 0.05 * i, 3),
                 "Transparency": fade if fade is not None else 0}
        e = {"type": "emitter", "emits": [[round(t0, 3), 1]], "seed": 4242, "props": props}
        if is_path:
            e["at"], e["path"] = where[0][1], where
        else:
            e["at"] = where
        out.append(e)
    return out


def plasma_sphere(where, t0, life, radius_keys, spin=240, core=True, bright=1.5, fade=None, dt=0.028, seed=0):
    """The plasma body in the house style: a small neon core inside a BALL OF CEL ARCS - short curved arcs flicker
    across the sphere surface (bowing outward) two at a time, plus a cel crackle bush at the centre. Same cel strokes
    as every other move; only the shape (a dense ball) is this move's own. where: point or time-keyed path."""
    out = []
    is_path = isinstance(where[0], list)
    pos = {"path": where} if is_path else {"at": where}
    rk = [[k, r] + rest for k, r, *rest in radius_keys]
    if core:
        out.append(dict(pos, type="shell", mesh="sphere", material="Neon", t0=t0, life=life,
                        scale=[[k, round(r * 0.38, 3)] + rest for k, r, *rest in radius_keys], color=[[0, WHITE], [1, ICE]], transparency=fade or 0))
    r_ = random.Random(seed * 31 + int(t0 * 1000))
    t = t0
    while t < t0 + life - 0.02:
        k = (t - t0) / life
        rad = _keys_at(rk, k)
        if fade and _keys_at(fade, k) > 0.8:
            t += dt
            continue
        c = _keys_at(where, t) if is_path else where
        if rad > 0.25:
            for _ in range(3):
                pts = []
                for _ in range(2):
                    z_, a_ = r_.uniform(-1, 1), r_.uniform(0, math.tau)
                    q = math.sqrt(1 - z_ * z_)
                    pts.append([math.cos(a_) * q, z_, math.sin(a_) * q])
                m = [(pts[0][i] + pts[1][i]) / 2 for i in range(3)]
                ml = math.sqrt(sum(v * v for v in m)) or 1
                bow = [round(m[i] / ml * rad * 0.45, 3) for i in range(3)]
                p0 = [round(c[i] + pts[0][i] * rad, 3) for i in range(3)]
                p1 = [round(c[i] + pts[1][i] * rad, 3) for i in range(3)]
                out += arc_jump(p0, p1, round(t, 3), life=dt * 2.1, bow=bow, width=max(0.7, min(1.9, rad * 0.8)), seed=r_.randint(0, 99))
        t += dt
    # crackle bush at the centre, sized with the orb: cel body + white core + indigo outline (independent spawns)
    n_win = 6
    for w in range(n_win):
        w0, w1 = t0 + life * w / n_win, t0 + life * (w + 1) / n_win
        rad = _keys_at(rk, (w + 0.5) / n_win)
        if fade and _keys_at(fade, (w + 0.5) / n_win) > 0.8 or rad < 0.3:
            continue
        for tex, col, le, rate, f in (("thunder_arc_v2_mid", [[0, WHITE], [0.4, CYAN], [1, BLUE]], 0.35, 40, 2.4),
                                      ("thunder_arc_v2_core", WHITE, 0.35, 22, 2.0), ("thunder_arc_v2_rim", INDIGO, 0, 18, 2.7)):
            e = dict(pos, type="emitter", rate=[[round(w0, 3), round(w1, 3), rate]], seed=900 + seed * 7 + w * 3 + len(out) % 5, props={
                "Texture": tex, "Color": col, "LightEmission": le, "Brightness": 1.4 if le else 1, "LockedToPart": True,
                "Size": [[0, round(rad * f * 0.85, 2)], [1, round(rad * f, 2)]], "Lifetime": [0.06, 0.1], "Speed": [0.01, 0.01], "Rotation": [0, 360],
                "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [24, 24], "FlipbookStartRandom": True,
                "ZOffset": 0.35 if le else 0.25})
            out.append(e)
    return out


def build():
    P = orb_path()
    L = []
    # ---- the orb (rides the path: overhead hold, then the lob); pinch + swell before release; implodes at impact
    kk = lambda t: round(t / TB, 4)
    R = [[0, 0.25], [kk(0.6), 1.7, "out"], [kk(0.74), 1.95], [kk(0.79), 1.35, "in"], [kk(TR), 2.1, "outBack"], [kk(TI), 2.0],
         [kk(TB - 0.01), 0.15, "in"], [1, 0.05]]
    L += anime_ball(P, 0.0, TB, R)
    L += anime_ball(P, 0.0, TB, [[k, r * 0.82] + e for k, r, *e in R], fps=30, rot=100, z=0.2, colors=COOL)      # counter cage -> 3D
    # MODERN: a dim fresnel volume holds the cage together + an orbiting swirl
    L += swirl(ORB, 0.1, [[0, 4], [1, 7.5]], TR - 0.1, seed=891, rot=20)
    L.append({"type": "shell", "mesh": "sphere", "material": "Neon", "path": P, "at": ORB, "t0": 0.0, "life": TB,
              "scale": [[k, round(r * 0.12, 3)] + e for k, r, *e in R], "color": [[0, WHITE], [1, ICE]], "transparency": 0.3})
    # tendrils leaping off the orb surface while it charges
    t = 0.15
    while t < TR:
        a, e = rnd.uniform(0, math.tau), rnd.uniform(-0.6, 1.0)
        rr = 1.5 + 1.6 * (t / TR)
        tip = [round(ORB[0] + math.cos(a) * math.cos(e) * rr * 1.7, 2), round(ORB[1] + math.sin(e) * rr * 1.7, 2), round(ORB[2] + math.sin(a) * math.cos(e) * rr * 1.7, 2)]
        L += arc_jump(ORB, tip, round(t, 3), life=0.06, bow=[0, 0.4, 0], width=0.7, seed=int(t * 100))
        t += rnd.uniform(0.07, 0.11)
    # arcs leap UP out of the sand into the orb (the charge drinks from the ground)
    t = 0.12
    while t < TR - 0.04:
        a, r = rnd.uniform(0, math.tau), rnd.uniform(2.5, 7)
        g = [round(ORB[0] + math.cos(a) * r, 2), 0.2, round(ORB[2] + math.sin(a) * r, 2)]
        side = [round(-math.sin(a) * 1.5, 2), 0, round(math.cos(a) * 1.5, 2)]
        L += arc_jump(g, ORB, round(t, 3), life=0.08, bow=side, width=1.3, seed=int(t * 97))
        L += emit_stack("thunder_arc_v2", g, round(t, 3), size=2.2, life=0.1, seed=int(t * 1000) % 997)
        t += rnd.uniform(0.06, 0.1)
    # dust dragged inward along the ground, burn spreading under the caster, haze
    L.append({"type": "emitter", "at": [ORB[0], 0.5, ORB[2]], "part": [16, 0.2, 16], "rate": [[0.1, TR, 24]], "seed": 801, "props": {
        "Texture": "dust_burst", "Color": "#d9d3c6", "LightEmission": 0, "Brightness": 1, "Shape": "Disc", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "EmissionDirection": "Top", "Size": [[0, 3], [1, 1.5]], "Lifetime": [0.4, 0.5], "Speed": [12, 16],
        "Transparency": [[0, 0.5], [0.4, 0.3], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot",
        "Orientation": "FacingCameraWorldUp", "ZOffset": 0.0}})
    L += scar([ORB[0], 0, ORB[2]], 0.15, size=11, rot=20, glow_life=TR, soot_life=3.0, soot_in=TR + 0.2)
    L.append(haze([ORB[0], 0.6, ORB[2]], 0.1, TR, 18, size=(3, 7), rise=1, part=[8, 0.6, 8], seed=802))

    # ---- lob: plasma trail + static dripping off the orb
    base = {"path": P, "t0": TR, "t1": TI, "lifetime": 0.32, "faceCamera": True, "textureMode": "Static", "textureLength": 7,
            "widthScale": [[0, 1.0], [1, 0.25]]}
    L += trail_stack(base, {"glow": 5.5, "rim": 3.4, "mid": 3.0, "core": 1.5},
                     transparency={"glow": [[0, 0.35], [1, 1]], "rim": [[0, 0], [1, 1]], "mid": [[0, 0], [0.6, 0.35], [1, 1]], "core": [[0, 0], [0.5, 0.3], [1, 1]]})
    L.append({"type": "emitter", "at": ORB, "path": P, "rate": [[TR, TI, 50]], "seed": 803, "props": {
        "Texture": "static_sparks", "Color": [[0, WHITE], [0.4, CYAN], [1, BLUE]], "LightEmission": 1, "Brightness": 1.5,
        "Size": [[0, 1.3], [1, 0.4]], "Lifetime": [0.25, 0.45], "Speed": [2, 6], "SpreadAngle": [180, 180], "Acceleration": [0, -30, 0],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [20, 20], "FlipbookStartRandom": True, "ZOffset": 0.3}})

    # ---- implode: everything sucked into the point
    L.append({"type": "emitter", "at": IMPACT, "part": [12, 12, 12], "rate": [[TI, TB, 240]], "seed": 804, "props": {
        "Texture": "static_sparks", "Color": [[0, BLUE], [1, WHITE]], "LightEmission": 1, "Brightness": 1.6, "Shape": "Sphere", "ShapeInOut": "Inward",
        "ShapeStyle": "Surface", "Size": [[0, 0.8], [1, 1.6]], "Lifetime": [0.07, 0.08], "Speed": [80, 90], "Orientation": "VelocityParallel",
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [25, 25], "FlipbookStartRandom": True, "ZOffset": 0.4}})

    # ---- bloom: the implode releases radial waves of cel arcs bursting out over A (house matter, this move's shape)
    L += emit_stack("plasma_blast_v2", [IMPACT[0], 3.2, IMPACT[2]], TB + 0.11, size=12, life=0.5, z=0.6)
    L.append(flare([IMPACT[0], 3, IMPACT[2]], TB, size=16, life=0.26, seed=892))
    L += impact_v3([IMPACT[0], 3, IMPACT[2]], TB + 0.005, size=9, life=0.45, seed=893)
    L += shockwave([IMPACT[0], 0, IMPACT[2]], TB + 0.02, 15, life=0.55, seed=894)
    L.append(streaks([IMPACT[0], 2.5, IMPACT[2]], TB + 0.02, 34, speed=(70, 130), length=(3, 8), spread=75, seed=895))
    L.append(dust_ring([IMPACT[0], 0, IMPACT[2]], TB + 0.02, n=22, speed=(40, 55), size=(4.5, 10), seed=896))
    L.append(smoke3([IMPACT[0], 2, IMPACT[2]], TB + 0.06, n=7, size=(5, 10), speed=(5, 11), seed=897))
    L += crack([IMPACT[0], 0, IMPACT[2]], TB + 0.01, size=22, life=1.6, rot=-15, seed=898)
    for w, (dtw, n, rad, hgt, wd) in enumerate([(0.02, 9, 8.0, 5.5, 1.6)]):
        for i in range(n):
            a, e = i / n * math.tau + w * 0.4 + rnd.uniform(-0.15, 0.15), rnd.uniform(0.1, 1.0)
            tip = [round(IMPACT[0] + math.cos(a) * math.cos(e) * rad, 2), round(0.3 + math.sin(e) * hgt, 2), round(IMPACT[2] + math.sin(a) * math.cos(e) * rad, 2)]
            L += arc_jump([IMPACT[0], 2.2, IMPACT[2]], tip, round(TB + 0.005 + dtw, 3), life=0.1 + 0.03 * w, bow=[0, round(1.0 + 0.4 * w, 2), 0],
                          width=wd, seed=60 + w * 20 + i)
    L += scar([IMPACT[0], 0, IMPACT[2]], TB, size=16, rot=-15, glow_life=1.2, soot_life=3.2, soot_in=1.0)

    # ---- chain: braided tethers lash out, a plasma bead races down each, the target is encased and it pops
    hits = [{"t": TB, "dummy": 0, "dir": [0, 0, -1], "power": 0.5}]
    hs = [{"t": TB + 0.015, "dur": 0.1}]
    numbers = [{"t": TB + 0.02, "at": [1.6, 7.2, -20], "text": "120", "color": CYAN, "vel": [2, 10, 0], "size": 1.9, "life": 0.5}]
    encase = [(A, TB)]
    for n, (p, q, tl) in enumerate([(A, B, 1.6), (B, Cc, 1.8)]):
        a_, b_ = chest(p), chest(q)
        tb = tl + 0.13                                  # bead arrives
        for s, ph in enumerate((0, 120, 240)):          # three strands braided around the line
            ang = math.radians(ph)
            for lay, w in (("rim", 2.8), ("mid", 2.3), ("core", 1.2)):
                L.append({"type": "beam", "from": a_, "to": b_, "t0": tl, "life": 0.62, "reach": [[0, 0], [0.07, 1, "out"]],
                          "curve": [[0, [round(math.cos(ang) * 1.6, 2), round(math.sin(ang) * 1.6, 2), 0]],
                                    [0.5, [round(math.cos(ang + 2) * 1.6, 2), round(math.sin(ang + 2) * 1.6, 2), 0]],
                                    [1, [round(math.cos(ang + 4) * 1.6, 2), round(math.sin(ang + 4) * 1.6, 2), 0]]],
                          "textures": [f"{st}_{lay}" for st in STRIPS[s:] + STRIPS[:s]], "swap": 0.04, "textureLength": 4, "segments": 16,
                          "color": COOL[lay], "lightEmission": LE[lay], "brightness": BR[lay], "width": [[0, w * 1.4], [0.2, w], [1, w * 0.3]],
                          "transparency": [[0, 0], [0.4, 0], [0.45, 0.7], [0.5, 0.05], [0.7, 0.4], [1, 1]]})
        # the plasma bead (a small plasma sphere) racing down the tether
        L += anime_ball([[tl + 0.02, a_], [tb, b_]], tl + 0.02, tb - tl - 0.02, [[0, 0.9], [1, 1.1]], fps=40)
        encase.append((q, tb))
        hits.append({"t": tb, "dummy": n + 1, "dir": [round((q[0] - p[0]) / 12, 2), 0, -0.6], "power": 0.35})
        hs.append({"t": tb + 0.012, "dur": 0.05})
        numbers.append({"t": tb + 0.02, "at": [q[0] + 1.5, 6.8, q[2]], "text": "70", "color": CYAN, "vel": [2, 9, 0], "size": 1.7, "life": 0.5})
    for j, (d, te) in enumerate(encase):                # each target: encased in a plasma sphere that pops
        c = chest(d)
        L += anime_ball(c, te, 0.3, [[0, 0.6], [0.2, 2.7], [0.8, 2.4], [1, 1.6]], fps=32, rot=40 * j, z=0.4)
        L += emit_stack("plasma_blast_v2", c, te + 0.29, size=10, life=0.4, z=0.5, rot=30 * j)
        L.append(sparks(c, te + 0.29, 8, speed=(10, 24), seed=820 + j))
        L.append(streaks(c, te + 0.29, 14, speed=(50, 90), length=(2, 5), seed=840 + j))
        L.append(flare(c, te + 0.29, size=10, life=0.2, seed=850 + j))
        L += emit_stack("thunder_arc_v2", c, te, size=[[0, 3.8], [1, 4.4]], life=0.14, mode="Loop", rate=[[te + 0.3, te + 1.0, 8]],
                        seed=830 + j, colors=COOL, transparency=[[0, 0], [0.6, 0.3], [1, 1]])
        if j:
            L += scar([d[0], 0, d[2]], te, size=7, rot=50 * j, glow_life=0.8, soot_life=2.4, soot_in=0.6)

    dur = 2.8
    kd = lambda t: round(t / dur, 4)
    return {
        "name": "thunder_07_PlasmaBomb", "title": "Plasma Bomb", "element": "Thunder", "archetype": "charged_plasma_chain", "duration": dur,
        "layers": L, "dummies": [A, B, Cc], "hits": hits, "numbers": numbers, "hitstop": hs,
        "impact": [{"t": TB + 0.015, "dur": 0.034, "mode": "white"}],
        "shakes": [{"t": 0.3, "amp": 0.08, "dur": 0.5, "freq": 30}, {"t": TR, "amp": 0.2, "dur": 0.12, "freq": 26}, {"t": TB, "amp": 0.8, "dur": 0.45, "freq": 22}]
                  + [{"t": te, "amp": 0.22, "dur": 0.15, "freq": 28} for _, te in encase[1:]],
        "lights": [{"at": ORB, "path": P, "color": CYAN, "range": 14, "brightness": [[0, 0], [0.6, 7], [TR, 9], [TI, 7], [TB, 0]]},
                   light([IMPACT[0], 4, IMPACT[2]], [[TB - 0.005, 0], [TB, 24], [TB + 0.5, 5], [TB + 1.1, 0]], rng=18)]
                  + [light(chest(d), [[te - 0.005, 0], [te, 10], [te + 0.35, 0]], rng=9) for d, te in encase[1:]],
        "grade": [[0, 0, 0, 0, "#ffffff"], [TR - 0.05, -0.06, 0.12, -0.02, "#e2eaff"], [TI, -0.05, 0.1, 0, "#e6edff"],
                  [TB - 0.01, -0.24, 0.25, -0.15, "#c8d4f2"], [TB + 0.1, -0.04, 0.1, 0.02, "#eaf0ff"], [dur, 0, 0, 0, "#ffffff"]],
        "pose": {"armR": [[0, 0], [0.18, 175, "out"], [0.74, 178], [0.79, 200, "out"], [TR, 205], [TR + 0.06, 70, "out"], [TR + 0.16, 55], [TR + 0.9, 0]],
                 "armRz": [[0, 0], [0.18, -8], [TR, -8], [TR + 0.5, 0]],
                 "armL": [[0, 0], [0.18, 60, "out"], [TR, 75], [TR + 0.06, -30, "out"], [TR + 0.8, 0]],
                 "lean": [[0, 0], [0.3, -6, "out"], [0.79, -16, "out"], [TR, -16], [TR + 0.06, 18, "out"], [TR + 0.4, 6], [TR + 0.9, 0]],
                 "scale": [[0, [1, 1, 1]], [0.79, [1.05, 0.94, 1.05]], [TR + 0.05, [0.95, 1.06, 0.95]], [TR + 0.2, [1, 1, 1]]]},
        # behind the caster for the charge, follows the lob up, then drops low behind A so B (left) and C (right) spread out
        "camera": {"pos": [[0, [8, 7, 9]], [kd(TR), [8.5, 7.5, 8]], [kd(TR + 0.3), [9, 13, 3]], [kd(TB), [8, 14, -5]], [kd(TB + 0.15), [3, 9.5, -7], "out"], [1, [2.5, 9, -8]]],
                   "look": [[0, [0.8, 5, -2]], [kd(TR), [0.8, 5.2, -3]], [kd(TR + 0.3), [0, 3, -15]], [kd(TB), [0, 2.5, -22]], [kd(TB + 0.15), [-0.5, 3, -26], "out"], [1, [-0.5, 3, -27]]],
                   "fov": [[0, 55], [kd(TR), 55], [kd(TB) - 0.004, 58], [kd(TB) + 0.008, 52, "out"], [kd(TB + 0.15), 58], [1, 58]]},
        "poster": TB + 0.04,
    }


write(build(), os.path.join(os.path.dirname(__file__), "thunder_07_PlasmaBomb.json"))
print("wrote thunder_07_PlasmaBomb.json")
