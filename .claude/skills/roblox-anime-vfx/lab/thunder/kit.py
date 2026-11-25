"""Thunder fruit authoring kit: plumbing only (palette, layer conventions, stack helpers, the burn-scar calling
card). Each move's staging, timing and signature are hand-written in its own spec script, never here.

Layer conventions (MODERN pass, after studying TSB / JJS / Type Soul): no crisp dark outlines - glowing lines are
additive and saturated, bloom does the halo, contrast comes from a SOFT dark backing and dimming the world.
  glow  soft blue halo       LightEmission 0.35 electric blue, translucent (tints the sand blue, no outline)
  rim   saturated outer body LightEmission 0.3  electric blue (mostly covers the sand -> stays saturated)
  mid   body                 LightEmission 0.6  cyan
  core  hot line             LightEmission 1    white
"""
import json
import os

WHITE, ICE, CYAN, BLUE, INDIGO, NAVY, SOOT = "#ffffff", "#bff3ff", "#6fe0ff", "#3a5cff", "#2a1a9a", "#2a3350", "#0e1018"
LAYERS = ("glow", "rim", "mid", "core")
LE = {"glow": 0.75, "rim": 0.3, "mid": 0.45, "core": 1}
BR = {"glow": 1.0, "rim": 1.2, "mid": 1.0, "core": 1.15}
ELEC = "#2f6bff"
STRIPS = [f"thunder_strip_v2_{i}" for i in range(1, 5)]  # v2 cel strips (anime reference)

# colour script per layer as it cools (k = 0 strike -> 1 gone): white-hot -> cyan -> blue -> indigo afterglow
COOL = {
    "glow": [[0, "#2f6bff"], [0.5, BLUE], [1, INDIGO]],
    "rim": [[0, ELEC], [0.4, BLUE], [1, INDIGO]],
    "mid": [[0, WHITE], [0.12, CYAN], [0.5, BLUE], [1, INDIGO]],
    "core": [[0, WHITE], [0.3, ICE], [0.6, CYAN], [1, BLUE]],
}
HOT = {"glow": "#2f6bff", "rim": ELEC, "mid": CYAN, "core": WHITE}
GLOW_TR = 0.68                    # the soft blue halo stays translucent


def flicker(on_until=0.15, pulses=((0.2, 0.75), (0.26, 0.05), (0.38, 0.6), (0.44, 0.1)), tail=0.55, end=1.0):
    """Transparency sequence (k over life): solid strike, two-on-one-off flicker, then a cooling fade."""
    seq = [[0, 0], [on_until, 0]]
    for k, v in pulses:
        seq.append([k, v])
    seq += [[tail, 0.25], [end, 1]]
    return seq


def trail_stack(base, widths, *, strips=STRIPS, colors=COOL, transparency=None, swap=0.05, layers=LAYERS, le=None):
    """One Trail per texture layer, identical motion. base: shared trail keys (path/move/wave, t0, t1, lifetime...)."""
    out = []
    for L in layers:
        d = dict(base)
        d.update(type="trail", width=widths[L], textures=[f"{s}_{L}" for s in strips], swap=swap, color=colors[L],
                 lightEmission=(le or LE)[L], brightness=BR[L])
        if transparency is not None:
            d["transparency"] = transparency[L] if isinstance(transparency, dict) else transparency
        out.append(d)
    return out


def plane_stack(widths, *, count=3, strips=STRIPS, colors=COOL, transparency=None, twist=None, speed=None, tlen=None,
                swap=0.05, layers=LAYERS, angle=None, bright=None):
    """vbeam plane sets, one per texture layer."""
    out = []
    for i, L in enumerate(layers):
        out.append({"count": count, "width": widths[L], "textures": [f"{s}_{L}" for s in strips], "swap": swap,
                    "color": colors[L], "lightEmission": LE[L], "brightness": (bright or {}).get(L, BR[L]),
                    "transparency": (transparency[L] if isinstance(transparency, dict) else transparency) or 0,
                    "twist": (twist or {}).get(L, 0), "textureSpeed": (speed or {}).get(L, 0),
                    "textureLength": (tlen or {}).get(L, 8), "angle": (angle or {}).get(L, 0)})
    return out


def emit_stack(tex, at, t, *, size, life, layout="Grid4x4", mode="OneShot", count=1, colors=None, rot=0, z=0.0,
               orient="FacingCamera", transparency=None, layers=LAYERS, move=None, rate=None, squash=None, seed=None):
    """Deterministic emitter stack for a layered flipbook (no randomness: stacks can't share random numbers)."""
    out = []
    for i, L in enumerate(layers):
        props = {"Texture": f"{tex}_{L}", "Color": (colors or HOT)[L], "LightEmission": LE[L], "Brightness": BR[L],
                 "Size": size, "Lifetime": [life, life], "Speed": [0.01, 0.01], "Rotation": [rot, rot],
                 "Orientation": orient, "FlipbookLayout": layout, "FlipbookMode": mode, "ZOffset": round(z + 0.05 * i, 3),
                 "Transparency": transparency if transparency is not None else 0}
        if squash is not None:
            props["Squash"] = squash
        e = {"type": "emitter", "at": at, "props": props, "seed": seed or 4242}
        if rate:
            e["rate"] = rate
        else:
            e["emits"] = [[t, count]]
        if move:
            e["move"] = move
        out.append(e)
    return out


def scar(at, t, size=10, rot=0, glow_life=0.9, soot_life=3.2, soot_in=None):
    """Calling card: a Lichtenberg burn flat on the ground that flashes hot, cools through the colour script to
    indigo, and leaves the soot scar under it fading last. soot_in (seconds): the soot only fades in as the glow
    cools (use it wherever the scar sits under a long-lived effect, so it reads as glowing lightning, not cracks)."""
    g = [at[0], 0.1, at[2]]   # ground decals: never a negative ZOffset (it pushes the quad into the ground and hides it)
    soot = {"type": "emitter", "at": [at[0], 0.06, at[2]], "emits": [[t, 1]], "props": {
        "Texture": "scorch_burn", "Color": SOOT, "LightEmission": 0, "Brightness": 1, "Size": [[0, size * 0.9], [0.05, size * 1.05], [1, size * 1.05]],
        "Lifetime": [soot_life, soot_life], "Speed": [0.01, 0.01], "Rotation": [rot, rot], "Orientation": "VelocityPerpendicular",
        "Transparency": ([[0, 1], [min(0.9, soot_in / soot_life), 0.2], [0.8, 0.35], [1, 1]] if soot_in else [[0, 0.15], [0.7, 0.3], [1, 1]]),
        "ZOffset": 0.02}}
    glow = emit_stack("lichtenberg", g, t, size=[[0, size * 0.85], [0.06, size], [1, size]], life=glow_life, layout="None",
                      colors=COOL, rot=rot, orient="VelocityPerpendicular", z=0.05,
                      transparency=[[0, 0], [0.1, 0], [0.14, 0.5], [0.2, 0.05], [0.5, 0.35], [1, 1]])
    return [soot] + glow


def _modernize(L):
    """Apply the modern layer conventions to every layer that uses a layered texture: the old indigo LE0 rim
    becomes additive electric blue, the glow becomes a translucent soft dark backing."""
    def lay_of(tex):
        for k in LAYERS:
            if isinstance(tex, str) and tex.endswith("_" + k):
                return k
        return None
    if L.get("type") == "emitter":
        pr = L["props"]; k = lay_of(pr.get("Texture"))
        if k == "glow":
            pr["LightEmission"] = LE["glow"]
            tr = pr.get("Transparency", 0)
            pr["Transparency"] = round(GLOW_TR + (1 - GLOW_TR) * tr, 3) if isinstance(tr, (int, float)) else [[a, round(GLOW_TR + (1 - GLOW_TR) * v, 3)] + e for a, v, *e in tr]
            pr["Color"] = HOT["glow"]
        elif k == "rim":
            pr["LightEmission"] = LE["rim"]; pr["Brightness"] = BR["rim"]
            if pr.get("Color") in (INDIGO, BLUE, None) or isinstance(pr.get("Color"), list): pr["Color"] = COOL["rim"] if isinstance(pr.get("Color"), list) else ELEC
        elif k in ("mid", "core"):
            pr["LightEmission"] = LE[k]
    elif L.get("type") in ("beam", "trail"):
        texs = L.get("textures") or [L.get("texture")]
        k = lay_of(texs[0])
        if k == "glow":
            L["lightEmission"] = LE["glow"]; L["color"] = HOT["glow"]
            tr = L.get("transparency", 0)
            L["transparency"] = round(GLOW_TR + (1 - GLOW_TR) * tr, 3) if isinstance(tr, (int, float)) else [[a, round(GLOW_TR + (1 - GLOW_TR) * v, 3)] + e for a, v, *e in tr]
        elif k == "rim":
            L["lightEmission"] = LE["rim"]; L["brightness"] = BR["rim"]
            L["color"] = COOL["rim"] if isinstance(L.get("color"), list) else ELEC
        elif k in ("mid", "core"):
            L["lightEmission"] = LE[k]
    elif L.get("type") == "vbeam":
        for ps in (L.get("planes") if isinstance(L.get("planes"), list) else [L.get("planes")]) or []:
            if not ps: continue
            texs = ps.get("textures") or [ps.get("texture")]
            k = lay_of(texs[0])
            if k == "rim":
                ps["lightEmission"] = LE["rim"]; ps["color"] = ELEC
            elif k == "glow":
                ps["lightEmission"] = LE["glow"]; ps["color"] = HOT["glow"]


def write(fx, path):
    for L in fx.get("layers", []):
        _modernize(L)
    fx.setdefault("bloom", 0.5)
    # modern staging: the world dims and desaturates while the move plays (TSB / Type Soul), so the effect owns
    # the frame; the move's own grade keys still ride on top.
    dur = fx.get("duration", 2)
    g = fx.get("grade") or [[0, 0, 0, 0, "#ffffff"], [dur, 0, 0, 0, "#ffffff"]]
    dim = lambda t: 1.0 if 0.12 <= t <= dur - 0.45 else max(0.0, min(t / 0.12, (dur - t) / 0.45))
    fx["grade"] = [[k[0], round(k[1] - 0.12 * dim(k[0]), 3), round(k[2] + 0.12 * dim(k[0]), 3), round(k[3] - 0.08 * dim(k[0]), 3), k[4] if dim(k[0]) < 0.5 or k[4] not in ("#ffffff",) else "#dde6ff"] for k in g]
    if not any(abs(k[0] - 0.12) < 0.02 for k in fx["grade"]):
        fx["grade"] += [[0.12, -0.12, 0.12, -0.08, "#dde6ff"], [max(0.13, dur - 0.45), -0.12, 0.12, -0.08, "#dde6ff"]]
    fx["grade"].sort(key=lambda k: k[0])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(fx, open(path, "w"), indent=1)


def leg_trails(base, path, widths, **kw):
    """Angular ribbons: one trail stack per straight leg of a time-keyed path. A Trail samples once per frame and
    cuts corners that fall between frames (rounded kinks); a leg that starts and stops exactly on its corners
    keeps every kink sharp in the previewer and in Roblox."""
    out = []
    for (ta, pa), (tb, pb) in zip(path[:-1], path[1:]):
        b = dict(base, path=[[ta, pa], [tb, pb]], t0=ta, t1=tb)
        out += trail_stack(b, widths, **kw)
    return out


# ---------------------------------------------------------------- building blocks (compose per move; never a fixed recipe)
def sparks(at, t, n, speed=(8, 18), life=(0.25, 0.45), size=(0.8, 1.4), seed=7, color=CYAN, grav=-35):
    return {"type": "emitter", "at": at, "emits": [[t, n]], "seed": seed, "props": {
        "Texture": "static_sparks", "Color": [[0, WHITE], [0.3, color], [1, BLUE]], "LightEmission": 1, "Brightness": 1.6,
        "Size": [[0, size[1]], [1, size[0] * 0.4]], "Lifetime": list(life), "Speed": list(speed), "SpreadAngle": [180, 180],
        "Acceleration": [0, grav, 0], "Drag": 3, "Rotation": [0, 360], "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random",
        "FlipbookFramerate": [20, 30], "FlipbookStartRandom": True, "ZOffset": 0.4}}


def haze(at, t0, t1, rate, size=(4, 8), rise=2.5, seed=11, part=None, color=NAVY, tr=0.45):
    e = {"type": "emitter", "at": at, "rate": [[t0, t1, rate]], "seed": seed, "props": {
        "Texture": "ion_haze", "Color": color, "LightEmission": 0, "Brightness": 1,
        "Size": [[0, size[0]], [1, size[1]]], "Lifetime": [0.9, 1.4], "Speed": [0.5, rise], "SpreadAngle": [40, 40],
        "Rotation": [0, 360], "RotSpeed": [-20, 20], "Transparency": [[0, 1], [0.2, tr], [1, 1]],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot", "ZOffset": -0.3}}
    if part:
        e["part"] = part
        e["props"]["Shape"] = "Cylinder"
    return e


def crackle(at, t, size=4.0, life=0.16, seed=50):
    """Instant arc flash (thunder_arc played once): the angular replacement for camera-facing ring bursts."""
    return emit_stack("thunder_arc_v2", at, t, size=[[0, size * 0.8], [0.2, size], [1, size * 1.1]], life=life, seed=seed,
                      colors=COOL, transparency=[[0, 0], [0.5, 0.2], [1, 1]])


def ground_ring(at, t, size=12.0, life=0.45, seed=55):
    """MODERN: flat flipbook shockwave + a quick flat lightning rake (was a flat burst only)."""
    out = shockwave(at, t, size * 0.5, life=life, seed=seed)
    out += emit_stack("thunder_burst_v2", [at[0], 0.25, at[2]], t, size=[[0, size * 0.5], [0.15, size * 0.7], [1, size * 0.75]], life=life * 0.7,
                      seed=seed, orient="VelocityPerpendicular", colors=COOL, z=-0.2)
    return out


def dust(at, t, n=9, size=(5, 11), seed=61):
    """MODERN: radial shaded dust ring hugging the ground (was a puff that rose)."""
    return dust_ring(at, t, n=n + 6, speed=(26, 38), size=(size[0] * 0.6, size[1] * 0.65), seed=seed)


def smoke_burst(at, t, n=6, seed=63):
    """MODERN: shaded grey cel smoke kicked up by the strike (was flat navy puffs)."""
    return smoke3(at, t, n=n, size=(3, 7), speed=(4, 9), seed=seed, tr0=0.1)


def light(at, keys, color=CYAN, rng=14):
    # Roblox PointLight brightness ~1-8; anything hotter floods the sand white
    return {"at": at, "color": color, "range": rng, "brightness": [[t, round(v * 0.18, 2)] + k[2:] for t, v, *k in [list(x) for x in keys]]}


def arc_jump(a, b, t, life=0.09, bow=(0, 2.5, 0), width=1.0, seed=0, layers=("rim", "mid", "core")):
    """A curved cel arc that leaps between two points for a couple of frames (electricity jumping a gap)."""
    out = []
    strips = STRIPS[seed % 4:] + STRIPS[:seed % 4]
    for lay, w in zip(layers, (2.2, 1.8, 0.9)):
        out.append({"type": "beam", "from": a, "to": b, "curve": list(bow), "t0": t, "life": life,
                    "textures": [f"{st}_{lay}" for st in strips], "swap": 0.034, "textureLength": 3.5, "segments": 10,
                    "color": HOT[lay], "lightEmission": LE[lay], "brightness": BR[lay], "width": [[0, w * width * 1.2], [1, w * width * 0.6]],
                    "transparency": [[0, 0], [0.45, 0], [0.5, 0.7], [0.62, 0], [1, 0.3]]})
    return out


# ================================================================ MODERN toolkit (big shapes + mass + flipbooks)
def _fb(tex, at, t, size, life, *, color=WHITE, le=1, br=1.4, rot=0, orient="FacingCamera", z=0.3, tr=None, seed=1, mode="OneShot", fps=None):
    p = {"Texture": tex, "Color": color, "LightEmission": le, "Brightness": br, "Size": size, "Lifetime": [life, life],
         "Speed": [0.01, 0.01], "Rotation": [rot, rot] if not isinstance(rot, list) else rot, "Orientation": orient,
         "FlipbookLayout": "Grid4x4", "FlipbookMode": mode, "ZOffset": z, "Transparency": tr if tr is not None else 0}
    if fps:
        p["FlipbookFramerate"] = [fps, fps]
    return {"type": "emitter", "at": at, "emits": [[t, 1]], "seed": seed, "props": p}


def impact_v3(at, t, size=10, life=0.5, seed=1, rot=0):
    """Animated electric impact (elec_impact_v3 cel stack, additive conventions applied by write)."""
    return emit_stack("elec_impact_v3", at, t, size=size, life=life, seed=seed, rot=rot, colors=COOL, z=0.5)


def shockwave(at, t, radius, life=0.4, flat=True, color=CYAN, seed=2, rot=None, edge=False):
    """Big shape: a flipbook shockwave ring (flat on the ground in perspective, or facing camera) + a thin mesh ring
    racing out on ease-out for a crisp leading edge."""
    pos = [at[0], 0.2 if flat else at[1], at[2]]
    out = [_fb("shockwave_v3", pos, t, radius * 2.4, life, color=[[0, color], [0.3, ELEC], [1, BLUE]], orient="VelocityPerpendicular" if flat else "FacingCamera",
               z=0.1, seed=seed, br=0.9, le=0.6)]
    if not edge:
        return out
    out.append({"type": "shell", "mesh": "ring_thin", "material": "Neon", "at": pos, "t0": t, "life": life * 0.8, "rot": rot or ([0, 0, 0] if flat else [90, 0, 0]),
                "scale": [[0, radius * 0.15], [1, radius * 1.05, "outExpo"]], "color": [[0, WHITE], [0.4, color], [1, BLUE]],
                "transparency": [[0, 0], [0.5, 0.25], [1, 1]]})
    return out


def energy_sphere(at, t, life, radius_keys, color=CYAN, bright=1.6, tr=None, path=None):
    """Big shape: fresnel energy sphere (ForceField material - rim glows, centre clear) - the modern 'volume'."""
    L = {"type": "shell", "mesh": "sphere", "material": "ForceField", "t0": t, "life": life, "scale": radius_keys,
         "color": color, "brightness": bright, "transparency": tr if tr is not None else 0}
    if path:
        L["path"] = path; L["at"] = path[0][1]
    else:
        L["at"] = at
    return L


def streaks(at, t, n, speed=(60, 110), length=(3, 6), life=(0.14, 0.28), spread=180, direction=None, color=CYAN, seed=3, part=None):
    """Straight light streaks shooting out of an impact (spark_streak, VelocityParallel, heavy drag)."""
    e = {"type": "emitter", "at": at, "emits": [[t, n]], "seed": seed, "props": {
        "Texture": "spark_streak", "Color": [[0, WHITE], [0.35, color], [1, BLUE]], "LightEmission": 1, "Brightness": 2.0,
        "Size": [[0, length[1]], [0.6, length[0]], [1, 0.2]], "Lifetime": list(life), "Speed": list(speed), "SpreadAngle": [spread, spread],
        "Drag": 9, "Orientation": "VelocityParallel", "ZOffset": 0.6}}
    if direction:
        e["rot"] = direction
    if part:
        e["part"] = part
    return e


def spark_burst(at, t, size=9, life=0.35, seed=4, rot=0):
    return _fb("spark_burst_v3", at, t, size, life, color=[[0, WHITE], [0.4, CYAN], [1, BLUE]], br=2.0, seed=seed, rot=rot, z=0.55)


def flare(at, t, size=14, life=0.3, seed=5):
    """Anamorphic glint on a strike (flare_v3)."""
    return _fb("flare_v3", at, t, size, life, color=[[0, ICE], [0.3, CYAN], [1, BLUE]], br=0.8, le=0.8, seed=seed, z=0.8)


def swirl(at, t, size, life, path=None, seed=6, colors=None, rot=0, fps=24):
    """Looping charge swirl (elec_swirl_v3 cel stack); rides a path if given."""
    out = emit_stack("elec_swirl_v3", at, t, size=size, life=life, mode="Loop", seed=seed, colors=colors or HOT, rot=rot)
    for L in out:
        L["props"]["FlipbookFramerate"] = [fps, fps]
        L["props"]["LockedToPart"] = True
        if path:
            L["path"] = path
    return out


def crack(at, t, size=12, life=1.6, rot=0, seed=7):
    """Animated calling card: ground_crack_v3 grows across the sand and cools (flat)."""
    return emit_stack("ground_crack_v3", [at[0], 0.12, at[2]], t, size=size, life=life, rot=rot, seed=seed, colors=COOL,
                      orient="VelocityPerpendicular", z=-0.1)


def smoke3(at, t, n=6, size=(4, 9), speed=(4, 9), life=(0.9, 1.4), color="#b4b8c4", spread=70, rise=1.2, seed=8, part=None, tr0=0.0):
    """Shaded cel smoke volumes (smoke_cel_v3): grey, lit from above, eroding away - the soft mass under sharp light."""
    e = {"type": "emitter", "at": at, "emits": [[t, n]], "seed": seed, "props": {
        "Texture": "smoke_cel_v3", "Color": color, "LightEmission": 0, "Brightness": 1,
        "Size": [[0, size[0]], [1, size[1]]], "Lifetime": list(life), "Speed": list(speed), "SpreadAngle": [spread, spread],
        "Drag": 3.5, "Acceleration": [0, rise, 0], "Rotation": [-25, 25], "RotSpeed": [-15, 15],
        "Transparency": [[0, tr0], [0.75, tr0 + 0.1], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot",
        "Orientation": "FacingCameraWorldUp", "ZOffset": -0.4}}
    if part:
        e["part"] = part
    return e


def dust_ring(at, t, n=16, speed=(30, 42), size=(4, 9), color="#e3d7ba", seed=9, life=(0.7, 1.0)):
    """Modern ground dust ring: shaded smoke thrown out flat along the ground from the impact, heavy drag."""
    return {"type": "emitter", "at": [at[0], 0.9, at[2]], "emits": [[t, n]], "seed": seed, "part": [2.5, 0.6, 2.5], "props": {
        "Texture": "smoke_cel_v3", "Color": color, "LightEmission": 0, "Brightness": 1, "Shape": "Cylinder", "ShapeInOut": "Outward",
        "ShapeStyle": "Surface", "Size": [[0, size[0]], [1, size[1]]], "Lifetime": list(life), "Speed": list(speed),
        "SpreadAngle": [4, 4], "Drag": 6, "Acceleration": [0, 1.5, 0], "Rotation": [-20, 20], "RotSpeed": [-20, 20],
        "Transparency": [[0, 0], [0.7, 0.15], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot",
        "Orientation": "FacingCameraWorldUp", "ZOffset": -0.5}}


def rocks(at, t, radius=6, count=12, size=1.6, speed=34, crater=True, seed=10):
    """Mass: a crater rim of tilted slabs + flung chunks (top-level 'debris' entries)."""
    out = []
    if crater:
        out.append({"kind": "crater", "at": [at[0], 0, at[2]], "t": t, "radius": radius, "count": count, "size": size * 1.4, "life": 3.2, "seed": seed})
    out.append({"kind": "fling", "at": [at[0], 0, at[2]], "t": t, "radius": radius * 0.4, "count": count, "size": size, "speed": speed, "life": 2.4, "seed": seed + 1})
    return out
