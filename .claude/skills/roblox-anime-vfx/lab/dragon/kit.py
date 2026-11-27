"""Dragon fruit authoring kit: plumbing only (palettes, layer conventions, stack helpers, calling cards, the warm
grade, avatar hand tracking, the stand-in dragon rig). Every move's staging, timing and signature are hand-written
in its own script under moves/, never here. Template: lab/thunder/kit.py.

Layer conventions (DESIGN.md section 2, from the Type Soul fire study):
  glow  soft halo        LightEmission 0.75, ~70% transparent   orange   -> crimson
  rim   saturated body   LightEmission 0.2 (covers the sand)    crimson  -> ember red -> char
  mid   body             LightEmission 0.4                      gold     -> orange -> crimson
  core  hot line         LightEmission 1 (thin; the only white) white-gold -> gold -> orange
Palettes: "fire" is the fruit's colour script. "violet" (the heat-beam breath) and "gold" (the wind blades / yellow
beams) are the two extra beam colours the user asked for: same textures and layer roles, different tints, so the
fruit keeps one visual language.
"""
import json
import math
import os

LAYERS = ("glow", "rim", "mid", "core")
LE = {"glow": 0.3, "rim": 0.0, "mid": 0.3, "core": 0.8}    # value pass: the rim is a DARK alpha-blended edge (grayscale test on sand)
BR = {"glow": 1.4, "rim": 1.15, "mid": 1.1, "core": 1.2}
GLOW_TR = 0.55

# Type Soul pass: the named colours shift with the palette (yellow-dominant); CRIMSON is now the orange-red edge
WHITE_GOLD, GOLD, ORANGE, CRIMSON, EMBER, CHAR = "#fff6b0", "#ffd21a", "#ff8a14", "#9a1a0e", "#6a100a", "#2a2226"
SMOKE = "#3a2c2a"          # black smoke (smoke_cel_v3 is shaded 0.32..1, so this reads as a lit charcoal volume)
SAND_DUST = "#cdb48a"
AZURE = "#7fb0ff"          # stand-in dragon tint (thunder_serpent until assets/models/dragon.glb exists)

PALS = {
    "fire": {   # Type Soul fire on sand: huge flat YELLOW masses, thin orange-red edges, dark-red accents
        "HOT": {"glow": "#ff8a14", "rim": "#9a1a0e", "mid": "#ffd21a", "core": "#fff6b0"},   # VALUE: dark edge / bright body / white core
        "COOL": {"glow": [[0, "#ff8a14"], [0.6, "#e0401a"], [1, "#8a1a10"]],
                 "rim": [[0, "#9a1a0e"], [0.55, "#6a100a"], [1, "#3a0a08"]],
                 "mid": [[0, "#ffd21a"], [0.5, "#ffb01a"], [1, "#ff6a10"]],
                 "core": [[0, "#fff6b0"], [0.4, "#ffe25a"], [1, "#ffb01a"]]},
        "spark": [[0, "#fff6b0"], [0.3, "#ffd21a"], [0.7, "#ff8a14"], [1, "#e0401a"]], "light": "#ff9a2a",
    },
    "violet": {
        "HOT": {"glow": "#b04cff", "rim": "#6a16d0", "mid": "#d98aff", "core": "#fbeeff"},
        "COOL": {"glow": [[0, "#b04cff"], [0.6, "#7a22d8"], [1, "#3c0f70"]],
                 "rim": [[0, "#6a16d0"], [0.55, "#3c0f70"], [1, "#1c1028"]],
                 "mid": [[0, "#d98aff"], [0.4, "#b04cff"], [1, "#6a16d0"]],
                 "core": [[0, "#fbeeff"], [0.35, "#efc4ff"], [1, "#d98aff"]]},
        "spark": [[0, "#fbeeff"], [0.3, "#e3a6ff"], [0.7, "#b04cff"], [1, "#6a16d0"]], "light": "#b866ff",
    },
    "gold": {
        "HOT": {"glow": "#ffc83a", "rim": "#e0870f", "mid": "#ffe768", "core": "#fffbe8"},
        "COOL": {"glow": [[0, "#ffc83a"], [0.6, "#e0870f"], [1, "#8a4210"]],
                 "rim": [[0, "#e0870f"], [0.55, "#8a4210"], [1, CHAR]],
                 "mid": [[0, "#ffe768"], [0.4, "#ffc23a"], [1, "#e0870f"]],
                 "core": [[0, "#fffbe8"], [0.35, "#fff1a8"], [1, "#ffe768"]]},
        "spark": [[0, "#fffbe8"], [0.3, "#ffe768"], [0.7, "#ffc23a"], [1, "#e0870f"]], "light": "#ffd060",
    },
}
HOT, COOL = PALS["fire"]["HOT"], PALS["fire"]["COOL"]
STRIPS = [f"flame_strip_{i}" for i in range(1, 5)]
DRAGON_MODEL = "dragon"           # rigged by the rigging session (assets/models/dragon.glb, 30 studs, 35 bones)


def R(v, n=3):
    if isinstance(v, (list, tuple)):
        return [R(x, n) for x in v]
    return round(float(v), n)


# ---------------------------------------------------------------- stacks
def emit_stack(tex, at, t, *, size, life, pal="fire", cool=True, layout="Grid4x4", mode="OneShot", count=1, rot=0, z=0.0,
               orient="FacingCamera", transparency=None, layers=LAYERS, move=None, path=None, rate=None, squash=None,
               seed=4242, fps=None, locked=False, speed=0.01, direction=None, accel=None):
    """Deterministic emitter stack for a layered flipbook (stacks can't share random numbers in Roblox)."""
    P = PALS[pal]
    out = []
    for i, L in enumerate(layers):
        props = {"Texture": f"{tex}_{L}", "Color": (P["COOL"] if cool else P["HOT"])[L], "LightEmission": LE[L], "Brightness": BR[L],
                 "Size": size, "Lifetime": [life, life], "Speed": [speed, speed], "Rotation": [rot, rot], "Orientation": orient,
                 "FlipbookLayout": layout, "FlipbookMode": mode, "ZOffset": R(z + 0.05 * i),
                 "Transparency": transparency if transparency is not None else 0}
        if squash is not None:
            props["Squash"] = squash
        if fps:
            props["FlipbookFramerate"] = [fps, fps]
        if locked:
            props["LockedToPart"] = True
        if accel:
            props["Acceleration"] = accel
        e = {"type": "emitter", "at": R(at), "props": props, "seed": seed}
        if direction:
            e["rot"] = direction
        if rate:
            e["rate"] = rate
        else:
            e["emits"] = [[t, count]]
        if move:
            e["move"] = move
        if path:
            e["path"] = path
        out.append(e)
    return out


def _fb(tex, at, t, size, life, *, color=WHITE_GOLD, le=1, br=1.4, rot=0, orient="FacingCamera", z=0.3, tr=None, seed=1,
        mode="OneShot", fps=None, layout="Grid4x4"):
    p = {"Texture": tex, "Color": color, "LightEmission": le, "Brightness": br, "Size": size, "Lifetime": [life, life],
         "Speed": [0.01, 0.01], "Rotation": [rot, rot] if not isinstance(rot, list) else rot, "Orientation": orient,
         "FlipbookLayout": layout, "FlipbookMode": mode, "ZOffset": z, "Transparency": tr if tr is not None else 0}
    if fps:
        p["FlipbookFramerate"] = [fps, fps]
    return {"type": "emitter", "at": R(at), "emits": [[t, 1]], "seed": seed, "props": p}


def trail_stack(base, widths, *, pal="fire", strips=STRIPS, transparency=None, swap=0.06, layers=LAYERS, cool=True):
    """One Trail per texture layer riding the same path (flame ribbons, wakes, washes)."""
    P = PALS[pal]
    out = []
    for L in layers:
        if L not in widths:
            continue
        d = dict(base)
        d.update(type="trail", width=widths[L], textures=[f"{s}_{L}" for s in strips], swap=swap,
                 color=(P["COOL"] if cool else P["HOT"])[L], lightEmission=LE[L], brightness=BR[L])
        if transparency is not None:
            d["transparency"] = transparency[L] if isinstance(transparency, dict) else transparency
        out.append(d)
    return out


def plane_stack(widths, *, pal="fire", count=3, strips=STRIPS, transparency=None, twist=None, speed=None, tlen=None,
                swap=0.06, layers=LAYERS, angle=None):
    """vbeam plane sets, one per layer (the torrent body)."""
    P = PALS[pal]
    out = []
    for L in layers:
        if L not in widths:
            continue
        out.append({"count": count, "width": widths[L], "textures": [f"{s}_{L}" for s in strips], "swap": swap,
                    "color": P["HOT"][L], "lightEmission": LE[L], "brightness": BR[L],
                    "transparency": (transparency.get(L, 0) if isinstance(transparency, dict) else transparency) or 0,
                    "twist": (twist or {}).get(L, 0), "textureSpeed": (speed or {}).get(L, 0),
                    "textureLength": (tlen or {}).get(L, 10), "angle": (angle or {}).get(L, 0)})
    return out


# ---------------------------------------------------------------- the fire matter (big / medium)
def billow(at, t, size, life=0.8, pal="fire", rot=0, seed=11, move=None, z=0.2, grow=1.25, transparency=None):
    """A flame_billow: lobes bloom, roll up, tear into tongues, burn down. size = studs at birth."""
    return emit_stack("flame_billow", at, t, size=[[0, size * 0.8], [0.25, size], [1, size * grow]], life=life, pal=pal,
                      rot=rot, seed=seed, move=move, z=z, transparency=transparency)


def tongue(base, t, height, life=0.7, pal="fire", rot=0, seed=12, layers=("rim", "mid", "core"), z=0.1):
    """One torn flame tongue standing on `base` (the sheet's base sits near the bottom of the cell)."""
    at = [base[0], base[1] + height * 0.43, base[2]]
    return emit_stack("flame_tongue", at, t, size=[[0, height * 0.9], [1, height]], life=life, pal=pal, rot=rot, seed=seed,
                      layers=layers, z=z, orient="FacingCameraWorldUp")


def burning(base, t0, t1, height, every=0.22, life=0.6, pal="fire", seed=13, layers=("rim", "mid", "core")):
    """A spot of burning ground: tongues re-lit every `every` s between t0 and t1 (one per spot, deterministic)."""
    at = [base[0], base[1] + height * 0.43, base[2]]
    return emit_stack("flame_tongue", at, t0, size=[[0, height * 0.85], [1, height]], life=life, pal=pal, seed=seed,
                      layers=layers, rate=[[t0, t1, 1.0 / every]], orient="FacingCameraWorldUp")


def impact(at, t, size=8, life=0.5, pal="fire", seed=14, rot=0):
    """fire_impact: star pinch -> gold burst -> torn crimson ring -> flakes."""
    return emit_stack("fire_impact", at, t, size=[[0, size * 0.75], [0.3, size], [1, size * 1.15]], life=life, pal=pal,
                      seed=seed, rot=rot, z=0.5)


def crescent(at, t, size, life=0.45, pal="fire", rot=0, seed=15, move=None, orient="FacingCamera", direction=None, speed=0.01):
    return emit_stack("fire_crescent", at, t, size=[[0, size * 0.92], [1, size * 1.08]], life=life, pal=pal, rot=rot, seed=seed,
                      move=move, orient=orient, direction=direction, speed=speed, z=0.4)


def rake(at, t, size, life=0.6, pal="fire", rot=0, seed=16):
    return emit_stack("claw_rake", at, t, size=[[0, size * 0.95], [1, size * 1.05]], life=life, pal=pal, rot=rot, seed=seed, z=0.45)


def fire_ring(at, t, radius, life=0.6, pal="fire", seed=17, rot=0):
    """Flat ring wave on the ground (fire_ring laid VelocityPerpendicular; the sheet's ring ends at ~0.86 of the cell)."""
    g = [at[0], 0.25, at[2]]
    return emit_stack("fire_ring", g, t, size=[[0, radius * 1.9], [1, radius * 2.35]], life=life, pal=pal, seed=seed, rot=rot,
                      orient="VelocityPerpendicular", z=0.05)


def heat_ring(at, t, size, life=0.5, pal="fire", seed=18, flat=False, rot=0):
    o = "VelocityPerpendicular" if flat else "FacingCamera"
    return emit_stack("heat_ring", at, t, size=[[0, size * 0.8], [1, size * 1.1]], life=life, pal=pal, seed=seed, orient=o, rot=rot, z=0.3)


def torrent(frm, to, t0, life, width=4.0, pal="fire", reach=None, seed=19, twist=40, speed=3.5, tr=None):
    """The breath body: a vbeam of crossed flame_strip planes (crimson rim, gold body, a thin white-gold core twisting
    the other way). Never a laser: pair it with billow(), embers() and smoke() riding along it, and a splash()."""
    w = {"glow": [[0, [width * 1.9, width * 2.4]], [1, [width * 1.9, width * 2.4]]],
         "rim": [[0, [width * 0.9, width * 1.35]], [1, [width * 0.9, width * 1.35]]],
         "mid": [[0, [width * 0.62, width * 0.95]], [1, [width * 0.62, width * 0.95]]],
         "core": [[0, [width * 0.18, width * 0.26]], [1, [width * 0.18, width * 0.26]]]}
    planes = plane_stack(w, pal=pal, count=3, twist={"glow": twist * 0.5, "rim": twist, "mid": -twist * 0.7, "core": -twist * 1.4},
                         speed={"glow": speed * 0.8, "rim": speed, "mid": speed * 1.2, "core": speed * 1.6},
                         tlen={"glow": 14, "rim": 10, "mid": 9, "core": 8}, transparency=tr or {"glow": GLOW_TR})
    return {"type": "vbeam", "from": R(frm), "to": R(to), "t0": t0, "life": life, "reach": reach or [[0, 0], [0.08, 1, "out"], [1, 1]],
            "planes": planes}


# ---------------------------------------------------------------- small + mass
def streaks(at, t, n, speed=(55, 100), length=(2.5, 5.5), life=(0.14, 0.3), spread=180, direction=None, pal="fire", seed=21, part=None):
    e = {"type": "emitter", "at": R(at), "emits": [[t, n]], "seed": seed, "props": {
        "Texture": "spark_streak", "Color": PALS[pal]["spark"], "LightEmission": 1, "Brightness": 1.8,
        "Size": [[0, length[1]], [0.6, length[0]], [1, 0.2]], "Lifetime": list(life), "Speed": list(speed), "SpreadAngle": [spread, spread],
        "Drag": 9, "Orientation": "VelocityParallel", "ZOffset": 0.6}}
    if direction:
        e["rot"] = direction
    if part:
        e["part"] = part
    return e


def embers(at, t, n=0, rate=None, speed=(6, 16), life=(0.5, 1.1), size=(0.35, 0.8), grav=-6, spread=180, seed=22, pal="fire",
           part=None, direction=None, rise=0, drag=1.5, move=None, path=None):
    """Ember flakes (embers sheet, additive, random): the small layer of every fire beat. grav < 0 falls, rise > 0 drifts up."""
    e = {"type": "emitter", "at": R(at), "seed": seed, "props": {
        "Texture": "embers", "Color": PALS[pal]["spark"], "LightEmission": 1, "Brightness": 1.6,
        "Size": [[0, size[1]], [1, size[0] * 0.4]], "Lifetime": list(life), "Speed": list(speed), "SpreadAngle": [spread, spread],
        "Acceleration": [0, grav + rise, 0], "Drag": drag, "Rotation": [0, 360], "RotSpeed": [-180, 180],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [0.01, 0.01], "FlipbookStartRandom": True, "ZOffset": 0.35}}
    if rate:
        e["rate"] = rate
    else:
        e["emits"] = [[t, n]]
    if part:
        e["part"] = part
        e["props"]["Shape"] = "Box"
    if direction:
        e["rot"] = direction
    if move:
        e["move"] = move
    if path:
        e["path"] = path
    return e


def smoke(at, t, n=6, size=(4, 9), speed=(4, 9), life=(1.0, 1.6), color=SMOKE, spread=70, rise=3.0, seed=23, part=None, tr0=0.3,
          rate=None, direction=None, drag=3.5, move=None, path=None):
    """Black billowing smoke (smoke_cel_v3 in charcoal, alpha-blended): the dark anchor of every big fire shape."""
    e = {"type": "emitter", "at": R(at), "seed": seed, "props": {
        "Texture": "smoke_cel_v3", "Color": color, "LightEmission": 0, "Brightness": 1,
        "Size": [[0, size[0]], [1, size[1]]], "Lifetime": list(life), "Speed": list(speed), "SpreadAngle": [spread, spread],
        "Drag": drag, "Acceleration": [0, rise, 0], "Rotation": [-25, 25], "RotSpeed": [-15, 15],
        "Transparency": [[0, 1], [0.12, tr0], [0.7, tr0 + 0.15], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot",
        "Orientation": "FacingCameraWorldUp", "ZOffset": -0.8}}
    if rate:
        e["rate"] = rate
    else:
        e["emits"] = [[t, n]]
    if part:
        e["part"] = part
    if direction:
        e["rot"] = direction
    if move:
        e["move"] = move
    if path:
        e["path"] = path
    return e


def dust_ring(at, t, n=16, speed=(28, 40), size=(3.5, 8), color=SAND_DUST, seed=24, life=(0.7, 1.0), radius=2.5):
    """Radial sand ring hugging the ground (Cylinder / Surface / Outward, never Disc)."""
    return {"type": "emitter", "at": R([at[0], 0.9, at[2]]), "emits": [[t, n]], "seed": seed, "part": R([radius, 0.6, radius]), "props": {
        "Texture": "smoke_cel_v3", "Color": color, "LightEmission": 0, "Brightness": 1, "Shape": "Cylinder", "ShapeInOut": "Outward",
        "ShapeStyle": "Surface", "Size": [[0, size[0]], [1, size[1]]], "Lifetime": list(life), "Speed": list(speed),
        "SpreadAngle": [4, 4], "Drag": 6, "Acceleration": [0, 1.5, 0], "Rotation": [-20, 20], "RotSpeed": [-20, 20],
        "Transparency": [[0, 0], [0.7, 0.15], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot",
        "Orientation": "FacingCameraWorldUp", "ZOffset": -0.5}}


def shockwave(at, t, radius, life=0.4, pal="fire", seed=25, flat=True):
    pos = [at[0], 0.2 if flat else at[1], at[2]]
    return _fb("shockwave_v3", pos, t, radius * 2.4, life, color=[[0, PALS[pal]["HOT"]["core"]], [0.3, PALS[pal]["HOT"]["mid"]], [1, PALS[pal]["HOT"]["rim"]]],
               orient="VelocityPerpendicular" if flat else "FacingCamera", z=0.1, seed=seed, br=0.9, le=0.6)


def flare(at, t, size=12, life=0.26, pal="fire", seed=26):
    return _fb("flare_v3", at, t, size, life, color=[[0, PALS[pal]["HOT"]["core"]], [0.3, PALS[pal]["HOT"]["mid"]], [1, PALS[pal]["HOT"]["rim"]]],
               br=0.8, le=0.8, seed=seed, z=0.8)


def rocks(at, t, radius=6, count=12, size=1.6, speed=34, crater=True, seed=27, life=3.2):
    out = []
    if crater:
        out.append({"kind": "crater", "at": R([at[0], 0, at[2]]), "t": t, "radius": radius, "count": count, "size": size * 1.4, "life": life, "seed": seed})
    out.append({"kind": "fling", "at": R([at[0], 0, at[2]]), "t": t, "radius": radius * 0.4, "count": count, "size": size, "speed": speed, "life": 2.4, "seed": seed + 1})
    return out


def light(at, keys, color="#ff8a2a", rng=14, path=None):
    """PointLight; keys are [t, v] with v on a 0..44 scale -> brightness v * 0.18 (<= ~8 equivalent)."""
    L = {"at": R(at), "color": color, "range": rng, "brightness": [[t, round(v * 0.18, 2)] + list(k) for t, v, *k in keys]}
    if path:
        L["path"] = path
    return L


# ---------------------------------------------------------------- light + ambience (the glue between elements)
def glow_pool(at, t, size, life=0.5, pal="fire", peak=0.35, seed=71, rate=None, path=None, hold=0.15):
    """Fake light: a soft additive pool on the ground under fire (soft_glow laid flat). The previewer's PointLights
    barely light the sand; in Roblox a PointLight does, but a pool reads warmer and cheaper. Use under every fire
    source so fire and ground feel connected."""
    size, peak = size * 1.4, min(0.7, peak * 1.15)           # polish pass: fire lights a big patch of ground
    e = {"type": "emitter", "at": R([at[0], 0.08, at[2]]), "seed": seed, "props": {
        "Texture": "soft_glow", "Color": "#ff6a1a", "LightEmission": 0.5, "Brightness": 1.1, "Size": [[0, size * 0.8], [hold, size], [1, size * 1.1]],
        "Lifetime": [life, life], "Speed": [0.01, 0.01], "Orientation": "VelocityPerpendicular", "FlipbookLayout": "None",
        "Transparency": [[0, 1 - peak], [hold, 1 - peak], [1, 1]], "ZOffset": 0.01}}
    if rate:
        e["rate"] = rate
    else:
        e["emits"] = [[t, 1]]
    if path:
        e["path"] = path
    return e


def glow_orb(at, t, size, life=0.3, pal="fire", tr=0.45, seed=72, rate=None, path=None, locked=False):
    """A soft camera-facing glow (soft_glow): hands on fire, a charging throat, a fireball's aura."""
    e = {"type": "emitter", "at": R(at), "seed": seed, "props": {
        "Texture": "soft_glow", "Color": PALS[pal]["HOT"]["glow"], "LightEmission": 1, "Brightness": 1,
        "Size": [[0, size * 0.85], [0.3, size], [1, size * 0.9]], "Lifetime": [life, life], "Speed": [0.01, 0.01],
        "FlipbookLayout": "None", "Transparency": [[0, 1], [0.15, tr], [0.7, tr + 0.1], [1, 1]], "ZOffset": -0.1}}
    if locked:
        e["props"]["LockedToPart"] = True
    if rate:
        e["rate"] = rate
    else:
        e["emits"] = [[t, 1]]
    if path:
        e["path"] = path
    return e


def ambience(centre, t0, t1, radius=10, rate=10, pal="fire", seed=73, big=0.5):
    """Ability ambience for the whole move. The BIG layer is what sells an ability (user: "haze particles, dust
    particles, not tiny ones, big large pieces"): large sand-dust veils rolling along the ground, big heat-haze sheets
    rising, large ember pieces drifting and tumbling, a soft high smoke veil - plus the small drifting embers."""
    c = [centre[0], 0, centre[2]]
    span = [radius * 2, 1.0, radius * 2]
    out = [embers([c[0], 1.0, c[2]], 0, rate=[[t0, t1, rate]], speed=(0.5, 2), life=(1.4, 2.4), size=(0.2, 0.45),
                  rise=2.2, grav=0, drag=0.6, part=span, seed=seed, pal=pal)]
    if big <= 0:
        return out
    # rolling ground dust veils
    out.append({"type": "emitter", "at": R([c[0], 1.4, c[2]]), "rate": [[t0, t1, 2.6 * big]], "seed": seed + 1, "part": R([radius * 2.2, 0.5, radius * 2.2]), "props": {
        "Texture": "dust_veil", "Color": SAND_DUST, "LightEmission": 0, "Brightness": 1, "Size": [[0, 9], [1, 16]],
        "Lifetime": [2.0, 3.0], "Speed": [1.5, 3.5], "SpreadAngle": [180, 8], "Drag": 0.6, "Acceleration": [0, 0.25, 0],
        "Rotation": [-12, 12], "RotSpeed": [-6, 6], "Transparency": [[0, 1], [0.25, 0.58], [0.7, 0.7], [1, 1]],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot", "Orientation": "FacingCameraWorldUp", "ZOffset": -1.0}})
    # big heat-haze sheets
    out.append({"type": "emitter", "at": R([c[0], 3.5, c[2]]), "rate": [[t0, t1, 1.6 * big]], "seed": seed + 2, "part": R([radius * 1.6, 2, radius * 1.6]), "props": {
        "Texture": "heat_haze", "Color": "#ffd2a0", "LightEmission": 0.3, "Brightness": 1, "Size": [[0, 11], [1, 17]],
        "Lifetime": [1.6, 2.4], "Speed": [1, 2.5], "SpreadAngle": [20, 20], "Rotation": [0, 0],
        "Transparency": [[0, 1], [0.3, 0.8], [0.7, 0.84], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "Loop",
        "FlipbookFramerate": [12, 12], "ZOffset": -0.6}})
    # large ember pieces tumbling up through the air
    out.append({"type": "emitter", "at": R([c[0], 1.5, c[2]]), "rate": [[t0, t1, 6 * big]], "seed": seed + 3, "part": span, "props": {
        "Texture": "embers", "Color": [[0, "#ffb02a"], [0.4, "#ff6a14"], [1, "#b0200f"]], "LightEmission": 0.5, "Brightness": 1.3,
        "Size": [[0, 0.85], [0.7, 0.6], [1, 0.2]],
        "Lifetime": [2.0, 3.2], "Speed": [1.5, 3.5], "SpreadAngle": [35, 35], "Acceleration": [0, 1.4, 0], "Drag": 0.4,
        "Rotation": [0, 360], "RotSpeed": [-90, 90], "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random",
        "FlipbookFramerate": [0.01, 0.01], "FlipbookStartRandom": True, "ZOffset": 0.3}})
    # soft high smoke veil (warm grey, very translucent) drifting above the fight
    out.append({"type": "emitter", "at": R([c[0], 8, c[2]]), "rate": [[t0, t1, 1.2 * big]], "seed": seed + 4, "part": R([radius * 1.8, 3, radius * 1.8]), "props": {
        "Texture": "dust_veil", "Color": "#6a5850", "LightEmission": 0, "Brightness": 1, "Size": [[0, 14], [1, 22]],
        "Lifetime": [2.4, 3.4], "Speed": [0.5, 1.5], "SpreadAngle": [180, 10], "Rotation": [-10, 10],
        "Transparency": [[0, 1], [0.3, 0.72], [0.7, 0.78], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot",
        "Orientation": "FacingCameraWorldUp", "ZOffset": -1.2}})
    return out


def dust_rollout(at, t, radius=3.0, n=10, size=(10, 18), speed=(12, 20), color=SAND_DUST, seed=74, life=(1.6, 2.4)):
    """BIG dust veils rolling out along the ground from an impact (the heavy version of dust_ring)."""
    return {"type": "emitter", "at": R([at[0], 1.6, at[2]]), "emits": [[t, n]], "seed": seed, "part": R([radius, 0.6, radius]), "props": {
        "Texture": "dust_veil", "Color": color, "LightEmission": 0, "Brightness": 1, "Shape": "Cylinder", "ShapeInOut": "Outward",
        "ShapeStyle": "Surface", "Size": [[0, size[0]], [1, size[1]]], "Lifetime": list(life), "Speed": list(speed), "SpreadAngle": [6, 6],
        "Drag": 2.5, "Acceleration": [0, 0.6, 0], "Rotation": [-15, 15], "RotSpeed": [-8, 8],
        "Transparency": [[0, 0.4], [0.6, 0.55], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot",
        "Orientation": "FacingCameraWorldUp", "ZOffset": -0.9}}


# ---------------------------------------------------------------- calling cards (ground marks that glow, cool, drift embers)
def _mark(tex, at, t, size, rot, glow_life, char_life, pal, seed):
    g = [at[0], 0.09, at[2]]
    char = {"type": "emitter", "at": R([at[0], 0.06, at[2]]), "emits": [[t, 1]], "seed": seed, "props": {
        "Texture": f"{tex}_rim", "Color": CHAR, "LightEmission": 0, "Brightness": 1, "Size": [[0, size], [1, size]],
        "Lifetime": [char_life, char_life], "Speed": [0.01, 0.01], "Rotation": [rot, rot], "Orientation": "VelocityPerpendicular",
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot", "FlipbookFramerate": [16 / glow_life, 16 / glow_life],
        "Transparency": [[0, 1], [min(0.9, glow_life * 0.55 / char_life), 0.15], [0.8, 0.3], [1, 1]], "ZOffset": 0.0}}
    glow = emit_stack(tex, g, t, size=size, life=glow_life, pal=pal, rot=rot, orient="VelocityPerpendicular", z=0.02, seed=seed + 1,
                      transparency=[[0, 0], [0.75, 0.1], [1, 1]])
    return [char] + glow


def molten_crack(at, t, size=12, rot=0, glow_life=1.6, char_life=3.4, pal="fire", seed=31, flames=True):
    """Slam calling card: branching molten cracks spread, glow white-gold, cool to charcoal; small flames lick along
    the trunks while they're hot; embers drift off."""
    out = _mark("molten_crack", at, t, size, rot, glow_life, char_life, pal, seed)
    if flames:
        for k in range(5):
            a = math.radians(rot + 72 * k + 20)
            p = [at[0] + math.cos(a) * size * 0.24, 0, at[2] + math.sin(a) * size * 0.24]
            out += burning(p, t + 0.08 + 0.03 * k, t + glow_life * 0.6, height=1.4 + 0.3 * (k % 2), every=0.25, life=0.5, pal=pal, seed=seed + 10 + k)
    out.append(embers([at[0], 0.4, at[2]], 0, rate=[[t + 0.1, t + glow_life, 14]], speed=(1, 3), life=(0.8, 1.4), rise=4, grav=0,
                      part=[size * 0.6, 0.2, size * 0.6], seed=seed + 20, pal=pal))
    return out


def gouge(at, t, size=8, rot=0, glow_life=1.3, char_life=3.0, pal="fire", seed=41):
    """Claw calling card: three burning gouges in the sand."""
    out = _mark("claw_gouge", at, t, size, rot, glow_life, char_life, pal, seed)
    out.append(embers([at[0], 0.4, at[2]], 0, rate=[[t + 0.05, t + glow_life, 12]], speed=(1, 3), life=(0.7, 1.2), rise=4, grav=0,
                      part=[size * 0.6, 0.2, size * 0.3], seed=seed + 20, pal=pal))
    return out


def slice_mark(at, t, length=14, rot=0, glow_life=1.2, char_life=3.0, pal="fire", seed=51):
    """Blade calling card: one long burning cut (fire_slice)."""
    out = _mark("fire_slice", at, t, length, rot, glow_life, char_life, pal, seed)
    return out


def scorch(at, t, size=8, life=3.0, seed=61, tex="fire_scorch", rot=0):
    """A plain char scorch decal (dark anchor on the ground)."""
    return {"type": "emitter", "at": R([at[0], 0.05, at[2]]), "emits": [[t, 1]], "seed": seed, "props": {
        "Texture": tex, "Color": CHAR, "LightEmission": 0, "Brightness": 1, "Size": [[0, size * 0.85], [0.08, size], [1, size]],
        "Lifetime": [life, life], "Speed": [0.01, 0.01], "Rotation": [rot, rot], "Orientation": "VelocityPerpendicular",
        "FlipbookLayout": "None", "Transparency": [[0, 0.2], [0.75, 0.35], [1, 1]], "ZOffset": 0.0}}


# ---------------------------------------------------------------- avatar (hybrid) + dragon stand-in
def _keys(K, t, d):
    if K is None:
        return d
    if not isinstance(K, list) or not K or not isinstance(K[0], list):
        return K
    if t <= K[0][0]:
        return K[0][1]
    for a, b in zip(K[:-1], K[1:]):
        if t <= b[0]:
            k = (t - a[0]) / ((b[0] - a[0]) or 1)
            ez = b[2] if len(b) > 2 else None
            if ez == "out":
                k = 1 - (1 - k) ** 2
            elif ez == "in":
                k = k * k
            elif ez == "outExpo":
                k = 1 if k >= 1 else 1 - 2 ** (-10 * k)
            elif ez == "outBack":
                c = 1.70158
                k = 1 + (c + 1) * (k - 1) ** 3 + c * (k - 1) ** 2
            if isinstance(a[1], list):
                return [x + (y - x) * k for x, y in zip(a[1], b[1])]
            return a[1] + (b[1] - a[1]) * k
    return K[-1][1]


def _rx(v, a):
    c, s = math.cos(a), math.sin(a)
    return [v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c]


def _ry(v, a):
    c, s = math.cos(a), math.sin(a)
    return [v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c]


def _rz(v, a):
    c, s = math.cos(a), math.sin(a)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2]]


def hand(pose, t, side="R", reach=1.9, lateral=0.0, fwd=0.0):
    """World position of the previewer avatar's hand at effect time t (same FK as poseAvatar in lab/page/vfx.js:
    root (feet) > upper (pivot at the hips, lean = X, twist = Y) > arm (shoulder, X then Z)). Lets claw fire ride the
    hands until rig v2's `attach` layer exists."""
    D = math.pi / 180
    ax = _keys(pose.get("arm" + side), t, 0) * D
    az = _keys(pose.get("arm" + side + "z"), t, 0) * D
    v = [lateral, -reach, fwd]
    v = _rz(v, az); v = _rx(v, ax)       # three.js Euler XYZ: R = Rx * Ry * Rz
    v = [v[0] + (1.5 if side == "R" else -1.5), v[1] + 1.9, v[2]]
    lean = _keys(pose.get("lean"), t, 0) * D
    tw = _keys(pose.get("twist"), t, 0) * D
    v = _ry(v, tw); v = _rx(v, lean)
    v = [v[0], v[1] + 2, v[2]]
    sc = _keys(pose.get("scale"), t, [1, 1, 1])
    off = _keys(pose.get("offset"), t, [0, 0, 0])
    return [v[0] * sc[0] + off[0], v[1] * sc[1] + off[1], v[2] * sc[2] + off[2]]


def hand_path(pose, t0, t1, side="R", step=1 / 60, reach=1.9, lateral=0.0, fwd=0.0):
    """Dense time-keyed path of a point on the hand (lateral / fwd offsets in the arm's frame: claw tips)."""
    n = max(2, int((t1 - t0) / step))
    return [[R(t0 + (t1 - t0) * i / n, 4), R(hand(pose, t0 + (t1 - t0) * i / n, side, reach, lateral, fwd))] for i in range(n + 1)]


def smooth(ctrl, dt=1 / 60):
    """Fluid pose curves: Catmull-Rom through control keys [[t, v], ...] (v scalar or list), resampled densely, so arms
    swing on arcs with ease and overshoot instead of snapping linearly between a few keys. Add an overshoot key past
    the target and a settle key after it for follow-through."""
    ts = [c[0] for c in ctrl]
    vs = [c[1] for c in ctrl]
    vec = isinstance(vs[0], list)
    def at(i):
        return vs[max(0, min(len(vs) - 1, i))]
    out = []
    t = ts[0]
    while t <= ts[-1] + 1e-9:
        j = max(0, min(len(ts) - 2, next((k for k in range(len(ts) - 1) if t <= ts[k + 1]), len(ts) - 2)))
        u = (t - ts[j]) / ((ts[j + 1] - ts[j]) or 1)
        p0, p1, p2, p3 = at(j - 1), at(j), at(j + 1), at(j + 2)
        def cr(a, b, c, d):
            return 0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (-a + 3 * b - 3 * c + d) * u ** 3)
        v = [cr(a, b, c, d) for a, b, c, d in zip(p0, p1, p2, p3)] if vec else cr(p0, p1, p2, p3)
        out.append([round(t, 4), R(v)])
        t += dt
    return out


def dragon(path, t0, life, *, jaw=None, scale=1.0, color=None, brightness=1.65, transparency=None, roll=None, model=None,
           tracks=None):
    """The full-form dragon (rig layer v2 by the rigging session, path-follow): assets/models/dragon.glb, 30 studs,
    spine_00 (head) .. spine_19, jaw (+ opens), whiskerL/R_0..2, legFL/FR/BL/BR_0/1. Keep the head moving (coils,
    loops, waves): the user rejected stiff, straight poses. Give the path a pre-roll (t0 < 0) or start it inside cover
    (cocoon, ground) so the body is formed. tracks = boneTracks (see anims/anim_kit.py)."""
    L = {"type": "rig", "model": model or DRAGON_MODEL, "t0": t0, "life": life, "path": path, "scale": scale,
         "bones": {"prefix": "spine_"}, "jawBone": "jaw", "brightness": brightness}
    if color:
        L["color"] = color
    if jaw:
        L["jaw"] = jaw
    if transparency:
        L["transparency"] = transparency
    L["roll"] = roll or [[0, 0], [1, 0]]
    if tracks:
        L["boneTracks"] = tracks
    return L


def loop_path(t0, t1, centre, radius=(5, 3), height=0.0, turns=1.0, phase=0.0, bob=0.6, step=0.02, tilt=0.0):
    """A slow figure the head swims while 'hovering': an ellipse in XZ with a vertical bob."""
    n = max(4, int((t1 - t0) / step))
    out = []
    for i in range(n + 1):
        u = i / n
        a = phase + 2 * math.pi * turns * u
        out.append([R(t0 + (t1 - t0) * u, 4), R([centre[0] + math.cos(a) * radius[0],
                                                  centre[1] + height + bob * math.sin(2 * a) + tilt * math.sin(a),
                                                  centre[2] + math.sin(a) * radius[1]])])
    return out


# ---------------------------------------------------------------- write (applies the conventions + the warm grade)
def _layer_of(tex):
    for k in LAYERS:
        if isinstance(tex, str) and tex.endswith("_" + k):
            return k
    return None


RIM_FADE = [[0, 0], [0.5, 0.05], [0.8, 0.45], [1, 1]]   # a cooling rim thins out instead of holding a flat red cut-out


def _modernize(L):
    """Fire conventions on every layered texture use: glow ~70% transparent at LE 0.75, rim LE 0.2, mid 0.4, core 1.
    (Char decals that reuse a _rim texture at LE 0 are left alone.)"""
    def glow_tr(tr):
        return round(GLOW_TR + (1 - GLOW_TR) * tr, 3) if isinstance(tr, (int, float)) else [[a, round(GLOW_TR + (1 - GLOW_TR) * v, 3)] + e for a, v, *e in tr]
    if L.get("type") == "emitter":
        pr = L["props"]; k = _layer_of(pr.get("Texture"))
        if k is None or pr.get("Color") == CHAR:          # char decals keep their own settings
            return
        pr["LightEmission"] = LE[k]
        if k == "glow":
            pr["Transparency"] = glow_tr(pr.get("Transparency", 0))
        elif k == "rim" and pr.get("Transparency", 0) == 0 and pr.get("FlipbookMode") == "OneShot":
            pr["Transparency"] = RIM_FADE
    elif L.get("type") == "trail":
        k = _layer_of((L.get("textures") or [L.get("texture")])[0])
        if k is None or L.get("lightEmission") == 0:
            return
        L["lightEmission"] = LE[k]
        if k == "glow":
            L["transparency"] = glow_tr(L.get("transparency", 0))


def write(fx, path, form="hybrid"):
    """form 'hybrid': warm dim (brightness -0.1, contrast +0.12, tint #ffe2c8). 'full': deep warm dim (-0.2, +0.18,
    #ffc9a8) that holds while the dragon exists. 'into_full' ramps from hybrid to full and holds (Transform);
    'from_full' starts full and ramps back to normal (Revert). Saturation stays 0: desaturating killed thunder's colour."""
    flat = []
    for L in fx.get("layers", []):
        flat.extend(L if isinstance(L, list) else [L])      # helpers may return lists (ambience)
    fx["layers"] = flat
    for L in flat:
        _modernize(L)
    fx.setdefault("bloom", 0.38)
    dur = fx.get("duration", 2)
    H, F, N = (-0.03, 0.08, 0, "#fff1e2"), (-0.06, 0.1, 0, "#ffe8d4"), (0, 0, 0, "#ffffff")   # abilities, not ultimates: never darken the sky
    if form == "hybrid":
        g = [[0, *N], [0.12, *H], [max(0.13, dur - 0.45), *H], [dur, *N]]
    elif form == "full":
        g = [[0, *F], [dur, *F]]
    elif form == "into_full":
        T = fx.get("_swap", dur * 0.5)
        g = [[0, *N], [0.15, *H], [T, *H], [T + 0.3, *F], [dur, *F]]
    else:  # from_full
        T = fx.get("_swap", dur * 0.5)
        g = [[0, *F], [T, *F], [min(dur, T + 0.6), *N], [dur, *N]]
    extra = fx.pop("grade_extra", [])        # move-specific keys (e.g. a darker beat) ride on top
    for k in extra:
        g.append(k)
    g.sort(key=lambda k: k[0])
    fx["grade"] = [[R(k[0], 4), R(k[1]), R(k[2]), R(k[3]), k[4]] for k in g]
    fx.pop("_swap", None)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(fx, open(path, "w"), indent=1)


def out_path(here, name):
    return os.path.join(here, f"{name}.json")


# ---------------------------------------------------------------- the preview camera
# Moves are abilities, not cutscenes: one fixed third-person gameplay view (behind, above and right of the caster,
# who faces -Z), the same for every hybrid move, so the effects are judged from what a player actually sees.
GAMEPLAY_CAM = {"pos": [[0, [7.2, 6.2, 6.2]], [1, [7.2, 6.2, 6.2]]], "look": [[0, [-1.2, 3.0, -5.5]], [1, [-1.2, 3.0, -5.5]]], "fov": [[0, 70], [1, 70]]}
# Full form: the same idea pulled back for a ~23-stud dragon.
GAMEPLAY_CAM_FULL = {"pos": [[0, [12, 16, 26]], [1, [12, 16, 26]]], "look": [[0, [0, 6, -8]], [1, [0, 6, -8]]], "fov": [[0, 62], [1, 62]]}


# ---------------------------------------------------------------- filler matter (the glue: use generously)
def wisps(at, t0, t1, rate, size=2.2, life=0.45, pal="fire", seed=81, path=None, rots=(-20, 25), rise=4.0, locked=False):
    """Curling fire wisps shed off a source (hands, horns, a burning target, the dragon's body). One deterministic
    stack per fixed rotation (stacks can't share random numbers)."""
    out = []
    for k, rot in enumerate(rots):
        for e in emit_stack("fire_wisp", at, t0, size=[[0, size * 0.85], [1, size * 1.1]], life=life, pal=pal, rot=rot,
                            seed=seed + k, rate=[[t0, t1, rate / len(rots)]], layers=("rim", "mid", "core"),
                            orient="FacingCameraWorldUp", speed=rise, direction=None, locked=locked):
            if path:
                e["path"] = path
            out.append(e)
    return out


def swirl(at, t0, t1, size, pal="fire", seed=82, path=None, fps=22, rot=0):
    """Looping charge swirl (fire_swirl) riding a point: one long particle that loops while the charge lasts."""
    out = emit_stack("fire_swirl", at, t0, size=[[0, size * 0.6], [0.15, size], [0.85, size], [1, size * 0.4]], life=t1 - t0, pal=pal,
                     cool=False, mode="Loop", fps=fps, seed=seed, locked=True, rot=rot, transparency=[[0, 1], [0.1, 0], [0.85, 0], [1, 1]])
    if path:
        for e in out:
            e["path"] = path
    return out


def flicker(base, t0, t1, height, pal="fire", seed=83, path=None):
    """A small looping flame standing on `base` for t0..t1 (one long Loop particle)."""
    at = [base[0], base[1] + height * 0.42, base[2]]
    out = emit_stack("flame_flicker", at, t0, size=height, life=t1 - t0, pal=pal, cool=False, mode="Loop", fps=20, seed=seed,
                     orient="FacingCameraWorldUp", locked=True, layers=("glow", "rim", "mid", "core"),
                     transparency=[[0, 1], [0.08, 0], [0.75, 0.1], [1, 1]])
    if path:
        for e in out:
            e["path"] = path
    return out


def ember_spray(at, t, size=6, life=0.5, pal="fire", seed=84, rot=0):
    """Radial spray of hot droplets arcing down (ember_burst): the small layer on every hit."""
    return emit_stack("ember_burst", at, t, size=[[0, size * 0.9], [1, size * 1.1]], life=life, pal=pal, seed=seed, rot=rot, z=0.55,
                      layers=("glow", "rim", "mid", "core"))


def smear(at, t, size, rot, life=0.2, pal="fire", seed=85):
    """Motion smear along a swing (smear_arc): snaps on in 2 frames, streaks off. Head at the swing's end."""
    return emit_stack("smear_arc", at, t, size=size, life=life, pal=pal, rot=rot, seed=seed, z=0.2, cool=False, layers=("rim", "mid", "core"))


def gusts(at, t, size=8, life=0.35, rot=0, color="#ffe2b0", seed=86, tr=0.25, rate=None, orient="FacingCamera", move=None):
    """Wind gust lines (white sheet, warm tint, additive-ish)."""
    e = _fb("gust_lines", at, t, size, life, color=color, le=0.6, br=1.2, rot=rot, z=0.3, tr=[[0, tr], [0.7, tr + 0.2], [1, 1]],
            seed=seed, orient=orient)
    if rate:
        e.pop("emits"); e["rate"] = rate
    if move:
        e["move"] = move
    return e


def haze(at, t0, t1, size=8, seed=87, path=None, tr=0.82):
    """Heat shimmer above fire (heat_haze loop): faint, warm, alpha-blended."""
    e = _fb("heat_haze", at, t0, size, t1 - t0, color="#ffd2a0", le=0.25, br=1, z=-0.2, tr=[[0, 1], [0.15, tr], [0.8, tr], [1, 1]],
            seed=seed, mode="Loop", fps=12)
    if path:
        e["path"] = path
    return e


def smoke_wisps(at, t0, t1, rate, size=4, life=(1.0, 1.6), seed=88, part=None, color=SMOKE):
    """Thin curling after-smoke rising off burnt things (smoke_wisp, random)."""
    e = {"type": "emitter", "at": R(at), "rate": [[t0, t1, rate]], "seed": seed, "props": {
        "Texture": "smoke_wisp", "Color": color, "LightEmission": 0, "Brightness": 1, "Size": [[0, size * 0.8], [1, size * 1.3]],
        "Lifetime": list(life), "Speed": [1.5, 3], "SpreadAngle": [15, 15], "Rotation": [-15, 15], "Acceleration": [0, 1.5, 0],
        "Transparency": [[0, 1], [0.15, 0.35], [0.7, 0.5], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot",
        "Orientation": "FacingCameraWorldUp", "ZOffset": -0.6}}
    if part:
        e["part"] = part
    return e


def ash(at, t0, t1, rate, part=(20, 2, 20), seed=89, fall=-2.5):
    """Grey ash flakes drifting down (ash_flakes, random frames)."""
    return {"type": "emitter", "at": R(at), "rate": [[t0, t1, rate]], "seed": seed, "part": list(part), "props": {
        "Texture": "ash_flakes", "Color": "#9a948e", "LightEmission": 0, "Brightness": 1, "Size": [0.4, 0.9],
        "Lifetime": [2.0, 3.0], "Speed": [0.5, 1.5], "SpreadAngle": [180, 180], "Acceleration": [0, fall, 0], "Drag": 1.2,
        "Rotation": [0, 360], "RotSpeed": [-120, 120], "Transparency": [[0, 1], [0.1, 0.1], [0.85, 0.2], [1, 1]],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [0.01, 0.01], "FlipbookStartRandom": True, "ZOffset": 0.1}}


def glint(at, t, size=4, life=0.22, pal="fire", seed=90, rot=0):
    """Anime star glint (anime_glint): the sharp 4-point sparkle on a strike's hot point."""
    return emit_stack("anime_glint", at, t, size=size, life=life, pal=pal, cool=False, rot=rot, seed=seed, z=0.9)



def follow_cam(pose, dur, base=None, step=0.05, y_follow=0.0):
    """The gameplay camera follows the player (no cinematic moves): base framing + the caster's pose offset."""
    base = base or GAMEPLAY_CAM
    P0, L0 = base["pos"][0][1], base["look"][0][1]
    pos, look = [], []
    n = max(2, int(dur / step))
    for i in range(n + 1):
        t = dur * i / n
        o = _keys(pose.get("offset"), t, [0, 0, 0])
        pos.append([round(i / n, 4), R([P0[0] + o[0], P0[1] + o[1] * y_follow, P0[2] + o[2]])])
        look.append([round(i / n, 4), R([L0[0] + o[0], L0[1] + o[1] * y_follow, L0[2] + o[2]])])
    return {"pos": pos, "look": look, "fov": base["fov"]}


# ---------------------------------------------------------------- fire walls (one fused ribbon of flame_wall, never candles)
WALLS = [f"flame_wall_{i}" for i in range(1, 5)]


def _lerp_keys(A, B, f):
    """Point f of the way from keys A to keys B (both constant points or [[k, p], ...] keyed on the same k)."""
    if A and isinstance(A[0], list):
        return [[a[0], R([x + (y - x) * f for x, y in zip(a[1], b[1])])] + a[2:] for a, b in zip(A, B)]
    return R([x + (y - x) * f for x, y in zip(A, B)])


def wall_beam(frm, to, t0, life, height, *, pal="fire", tlen=18, swap=0.07, tr=None, speed=0.0, flip=True, taper=0.22, end=0.3, bow=None):
    """A moving wall of fire: camera-facing Beams spanning frm -> to (keys over the beam's life allowed); beam width =
    the wall's height (the centre line sits at mid-height). Three spans: the end spans taper to `end` x height so the
    wall fades into short flames at its edges instead of a cut-off rectangle. No glow layer (a glow Beam shows its
    rectangle). `height` may be keys over life [[k, h], ...]."""
    P = PALS[pal]
    out = []
    a, b = (to, frm) if flip else (frm, to)
    hk = height if isinstance(height, list) else [[0, height], [1, height]]
    pts = [a, _lerp_keys(a, b, taper), _lerp_keys(a, b, 1 - taper), b]
    if bow:                                   # push the inner points along `bow` (e.g. [0, 0, -2]): the wall bows forward
        def push(K):
            if K and isinstance(K[0], list):
                return [[k[0], R([x + d for x, d in zip(k[1], bow)])] + k[2:] for k in K]
            return R([x + d for x, d in zip(K, bow)])
        pts[1], pts[2] = push(pts[1]), push(pts[2])
    spans = [(0, 1, end, 1.0), (1, 2, 1.0, 1.0), (2, 3, 1.0, end)]
    for i, j, w0, w1 in spans:
        seg_len = taper if i != 1 else 1 - 2 * taper
        for L in ("rim", "mid", "core"):
            out.append({"type": "beam", "from": pts[i], "to": pts[j], "t0": t0, "life": life, "textures": [f"{w}_{L}" for w in WALLS],
                        "swap": swap, "textureLength": tlen * (1 if i == 1 else 0.6), "textureSpeed": speed, "segments": 8,
                        "color": P["HOT"][L], "lightEmission": LE[L], "brightness": BR[L],
                        "width": [[k, [v * w0, v * w1]] + e for k, v, *e in hk],
                        "transparency": (tr[L] if isinstance(tr, dict) else tr) if tr is not None else 0})
    return out


def ring_wall(centre, radius, t0, life, height, *, sweep=0.12, pal="fire", tlen=16, swap=0.07, start=0.0, reverse=False, fade=None, base=0.0):
    """A ring of fire: a vertical Trail (up = world Y) drawn around the circle in `sweep` s; the curtain it leaves IS the
    ring (one continuous fused fire, not separate tongues). The trail point rides at mid-height."""
    P = PALS[pal]
    n = 48
    path = []
    for i in range(n + 1):
        u = i / n
        a = start + (-1 if reverse else 1) * u * 2 * math.pi * 1.04
        path.append([R(t0 + sweep * u, 4), R([centre[0] + math.cos(a) * radius, base + height / 2, centre[2] + math.sin(a) * radius])])
    out = []
    for L in ("rim", "mid", "core"):
        out.append({"type": "trail", "path": path, "at": path[0][1], "t0": t0, "t1": t0 + sweep, "lifetime": life, "width": height,
                    "up": [0, 1, 0], "textures": [f"{w}_{L}" for w in WALLS], "swap": swap, "textureMode": "Wrap", "textureLength": tlen,
                    "color": P["HOT"][L], "lightEmission": LE[L], "brightness": BR[L],
                    "transparency": fade or [[0, 0], [0.7, 0.1], [1, 1]]})
    return out


PILLARS = [f"flame_pillar_{i}" for i in range(1, 5)]


def pillar(base, height, t0, life, width=4.0, pal="fire", reach=None, swap=0.07, flip=False):
    """A column of fire: ONE camera-facing Beam of flame_pillar from the ground up (base at u=0), growing with `reach`
    (it erupts out of the sand). Fused fire, not a beam of stripes."""
    P = PALS[pal]
    a, b = [base[0], base[1], base[2]], [base[0], base[1] + height, base[2]]
    if flip:
        a, b = b, a
    return [{"type": "beam", "from": R(a), "to": R(b), "t0": t0, "life": life, "textures": [f"{w}_{L}" for w in PILLARS], "swap": swap,
             "segments": 8, "color": P["HOT"][L], "lightEmission": LE[L], "brightness": BR[L], "width": [[0, [width, width]], [1, [width, width]]],
             "reach": reach or [[0, 0], [0.15, 1, "out"], [1, 1]], "transparency": [[0, 0], [0.7, 0.05], [1, 1]]}
            for L in ("rim", "mid", "core")]


def fire_streams(centre, t0, dur, *, r0=1.5, r1=9.0, n=7, y0=0.5, rise=0.0, turns=0.9, width=1.4, life=0.4, pal="fire", seed=0,
                 reverse=False, n_pts=40):
    """Big swirling flame streams wrapping a point (the reference 'Fuga' look): n flame ribbons spiral outward from r0 to
    r1 around `centre` over `dur` s, each a hot-headed Trail that cools along its length. The flowing primary shape of a
    fire impact or a charge (make r1 < r0 for streams spiralling IN)."""
    out = []
    for k in range(n):
        ph = k / n * 2 * math.pi + seed * 0.37
        lag = (k % 3) * dur * 0.08
        sp = []
        for i in range(n_pts + 1):
            u = i / n_pts
            t = t0 + lag + dur * u
            a = ph + (-1 if reverse else 1) * turns * 2 * math.pi * (u ** 0.8)
            r = r0 + (r1 - r0) * (1 - (1 - u) ** 2)
            sp.append([R(t, 4), R([centre[0] + math.cos(a) * r, y0 + rise * u + 0.35 * math.sin(k * 1.7 + u * 6), centre[2] + math.sin(a) * r])])
        w = width * (0.75 + 0.5 * ((k * 7) % 5) / 4)
        out += trail_stack({"path": sp, "at": sp[0][1], "t0": t0 + lag, "t1": t0 + lag + dur, "lifetime": life, "faceCamera": True,
                            "transparency": [[0, 0], [0.5, 0.15], [1, 1]], "widthScale": [[0, 1], [0.7, 0.6], [1, 0.1]], "textureMode": "Stretch"},
                           {"glow": w * 2.0, "rim": w, "mid": w * 0.82, "core": w * 0.3}, pal=pal)
    return out


def fire_bloom(centre, t, radius=8.0, dur=0.9, height=7.0, pal="fire", seed=0, arcs=3, fronds=1.0):
    """The reference look at a main fire beat, in one call:
      - a huge two-layer ground glow (orange heart -> red edge, ~3x the radius) that lights the sand around the fire
      - a VOLUMETRIC fire mass: many big, overlapping, semi-transparent flame wisps/tongues rising and swaying, so the
        fire reads as one glowing cloud of flame, not separate crisp pieces
      - tall sweeping flame arcs curling up over the beat (big camera-facing crescents)
      - a sustained hot yellow-white heart at the centre
    Pair it with fire_streams (the swirl on the ground)."""
    c = [centre[0], 0, centre[2]]
    out = []
    # ground glow: big red outer, orange inner (soft_glow flat)
    for sz, col, le, tr, hold in ((radius * 3.4, "#d8301a", 0.45, 0.45, 0.5), (radius * 1.9, "#ff8a1a", 0.6, 0.35, 0.35)):
        out.append({"type": "emitter", "at": R([c[0], 0.07, c[2]]), "emits": [[t, 1]], "seed": seed + 1, "props": {
            "Texture": "soft_glow", "Color": col, "LightEmission": le, "Brightness": 1.1, "Size": [[0, sz * 0.6], [0.15, sz], [1, sz * 1.05]],
            "Lifetime": [dur * 1.3, dur * 1.3], "Speed": [0.01, 0.01], "Orientation": "VelocityPerpendicular", "FlipbookLayout": "None",
            "Transparency": [[0, tr], [hold, tr], [1, 1]], "ZOffset": 0.0}})
    # volumetric mass: big translucent tongues + wisps standing all over the core area (deterministic placement)
    nfr = int(14 * fronds)
    for k in range(nfr):
        a = k * 2.39996 + seed
        r = radius * 0.55 * math.sqrt((k + 0.5) / nfr)
        p = [c[0] + math.cos(a) * r, 0, c[2] + math.sin(a) * r]
        h = height * (1.0 - 0.45 * r / (radius * 0.55)) * (0.8 + 0.4 * ((k * 7) % 5) / 4)
        tk = t + 0.02 + 0.015 * (k % 6)
        out += emit_stack("flame_tongue", [p[0], h * 0.43, p[2]], tk, size=[[0, h * 0.8], [1, h * 1.05]], life=dur * 0.7, pal=pal, rot=(k % 5 - 2) * 9,
                          seed=seed + 10 + k, layers=("glow", "rim", "mid"), orient="FacingCameraWorldUp", z=0.05 * (k % 3),
                          transparency=[[0, 0.35], [0.6, 0.45], [1, 1]], rate=[[tk, t + dur * 0.55, 3.0]])
    out += wisps([c[0], height * 0.5, c[2]], t, t + dur * 0.8, 26, size=height * 0.6, life=0.55, pal=pal, seed=seed + 40, rots=(-30, 0, 30), rise=6)
    for e in out[-9:]:
        e["part"] = R([radius * 0.9, height * 0.4, radius * 0.9])
    # big solid yellow crescents sweeping AROUND the beat (Type Soul rings): hot colours, opaque, low over the ground
    for k in range(arcs):
        a = seed * 0.7 + k * 2 * math.pi / arcs
        p = [c[0] + math.cos(a) * radius * 0.35, height * 0.42, c[2] + math.sin(a) * radius * 0.35]
        out += emit_stack("fire_crescent", p, t + 0.02 + 0.06 * k, size=[[0, radius * 1.5], [1, radius * 1.9]], life=0.4, pal=pal, cool=False,
                          rot=k * 360 / max(1, arcs) + 30, seed=seed + 50 + k, z=0.35, transparency=[[0, 0], [0.7, 0.1], [1, 1]])
    # sustained hot heart
    out.append({"type": "emitter", "at": R([c[0], height * 0.28, c[2]]), "emits": [[t, 1]], "seed": seed + 60, "props": {
        "Texture": "soft_glow", "Color": [[0, "#fff6c8"], [0.4, "#ffd04a"], [1, "#ff7a1a"]], "LightEmission": 1, "Brightness": 1.3,
        "Size": [[0, radius * 0.6], [0.2, radius * 0.9], [1, radius * 0.5]], "Lifetime": [dur * 0.8, dur * 0.8], "Speed": [0.01, 0.01],
        "FlipbookLayout": "None", "Transparency": [[0, 0.05], [0.5, 0.3], [1, 1]], "ZOffset": 0.2}})
    return out



def dark_spikes(at, t, size=10, life=0.35, seed=95, rot=0, color="#5a0c0a"):
    """Sharp dark-red anime spikes radiating out of a fire hit (spike_burst, alpha-blended dark): the dark accent."""
    out = emit_stack("spike_burst", at, t, size=size, life=life, cool=False, rot=rot, seed=seed, z=0.6, layers=("rim", "mid"))
    for e in out:
        e["props"]["Color"] = color if e["props"]["Texture"].endswith("_rim") else "#a01810"
        e["props"]["LightEmission"] = 0
    return out


def fire_scraps(at, t, n=18, speed=(14, 26), size=(1.2, 2.6), life=(0.5, 0.9), seed=96, spread=180, grav=-12, direction=None):
    """Torn flame scraps flung out of a fire hit, tumbling (flame_tongue rim, random frames, red-orange)."""
    e = {"type": "emitter", "at": R(at), "emits": [[t, n]], "seed": seed, "props": {
        "Texture": "flame_tongue_rim", "Color": [[0, "#ff7a14"], [0.5, "#e0401a"], [1, "#8a1a10"]], "LightEmission": 0.2, "Brightness": 1.1,
        "Size": [[0, size[1]], [1, size[0] * 0.5]], "Lifetime": list(life), "Speed": list(speed), "SpreadAngle": [spread, spread],
        "Acceleration": [0, grav, 0], "Drag": 2.5, "Rotation": [0, 360], "RotSpeed": [-360, 360],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random", "FlipbookFramerate": [0.01, 0.01], "FlipbookStartRandom": True,
        "Transparency": [[0, 0], [0.7, 0.1], [1, 1]], "ZOffset": 0.4}}
    if direction:
        e["rot"] = direction
    return e


def aura_haze(centre, t0, dur, radius=10.0, height=6.0, col="#ff6a24", deep="#c8281a", strength=1.0, seed=97):
    """The OUTSIDE of an effect (user: "there's no outside effect other than the affected area, no transparent haze"):
    the atmosphere that spreads well past the hit in every reference.
      - a huge soft glow cloud hanging around the effect (camera-facing soft_glow, translucent)
      - layered translucent coloured haze sheets drifting outward past the impact (dust_veil tinted warm)
      - a wide ground haze (flat soft glow) far beyond the crater
      - visible embers + star sparkles floating across a big area
    Fades in fast, holds, then thins over `dur`."""
    c = [centre[0], 0, centre[2]]
    S = strength
    out = []
    # glow cloud (two sizes)
    for sz, cl, tr, h in ((radius * 3.6, deep, 0.5, height * 0.55), (radius * 2.2, col, 0.4, height * 0.45)):
        out.append({"type": "emitter", "at": R([c[0], h, c[2]]), "emits": [[t0, 1]], "seed": seed + 1, "props": {
            "Texture": "soft_glow", "Color": cl, "LightEmission": 0.45, "Brightness": 1.1,
            "Size": [[0, sz * 0.5], [0.12, sz], [1, sz * 1.15]], "Lifetime": [dur, dur], "Speed": [0.01, 0.01], "FlipbookLayout": "None",
            "Transparency": [[0, 1], [0.08, 1 - (1 - tr) * S], [0.55, 1 - (1 - tr) * S * 0.8], [1, 1]], "ZOffset": -2.0}})
    # translucent coloured haze: MANY smooth soft puffs at low opacity (smooth single image, no flipbook stepping),
    # pushed out gently all round and left to drift, grow and thin slowly - builds up into one continuous veil
    out.append({"type": "emitter", "at": R([c[0], height * 0.4, c[2]]), "emits": [[t0 + 0.01, int(26 * S)]], "rate": [[t0 + 0.05, t0 + dur * 0.5, 14 * S]],
                "seed": seed + 2, "part": R([radius * 0.6, height * 0.5, radius * 0.6]), "props": {
        "Texture": "haze_soft", "Color": [[0, col], [0.5, deep], [1, deep]], "LightEmission": 0.4, "Brightness": 1.1,
        "Shape": "Cylinder", "ShapeInOut": "Outward", "ShapeStyle": "Volume",
        "Size": [[0, radius * 0.9], [0.4, radius * 1.6], [1, radius * 2.1]], "Lifetime": [dur * 0.8, dur * 1.1], "Speed": [radius * 0.25, radius * 0.6],
        "SpreadAngle": [25, 25], "Drag": 2.0, "Acceleration": [0, 0.6, 0], "Rotation": [0, 360], "RotSpeed": [-8, 8],
        "Transparency": [[0, 1], [0.15, 1 - 0.32 * S], [0.55, 1 - 0.24 * S], [1, 1]], "FlipbookLayout": "None",
        "Orientation": "FacingCamera", "ZOffset": -1.5}})
    # wide ground haze
    out.append({"type": "emitter", "at": R([c[0], 0.06, c[2]]), "emits": [[t0, 1]], "seed": seed + 3, "props": {
        "Texture": "soft_glow", "Color": col, "LightEmission": 0.4, "Brightness": 1.1, "Size": [[0, radius * 2], [0.2, radius * 5], [1, radius * 5.5]],
        "Lifetime": [dur, dur], "Speed": [0.01, 0.01], "Orientation": "VelocityPerpendicular", "FlipbookLayout": "None",
        "Transparency": [[0, 1], [0.1, 1 - 0.62 * S], [0.6, 1 - 0.48 * S], [1, 1]], "ZOffset": -0.1}})
    # embers + star sparkles floating across a big area
    out.append({"type": "emitter", "at": R([c[0], height * 0.5, c[2]]), "emits": [[t0 + 0.02, int(40 * S)]], "rate": [[t0, t0 + dur * 0.8, 30 * S]],
                "seed": seed + 4, "part": R([radius * 2.6, height * 1.2, radius * 2.6]), "props": {
        "Texture": "embers", "Color": [[0, "#fff6b0"], [0.4, "#ffb02a"], [1, "#e0401a"]], "LightEmission": 0.8, "Brightness": 1.5,
        "Size": [[0, 0.75], [0.7, 0.55], [1, 0.1]], "Lifetime": [1.0, 1.8], "Speed": [1, 4], "SpreadAngle": [180, 180], "Acceleration": [0, 2.5, 0],
        "Drag": 0.8, "Rotation": [0, 360], "RotSpeed": [-160, 160], "FlipbookLayout": "Grid4x4", "FlipbookMode": "Random",
        "FlipbookFramerate": [0.01, 0.01], "FlipbookStartRandom": True, "ZOffset": 0.3}})
    for k in range(int(9 * S)):
        a = k * 2.399 + seed
        r = radius * (0.6 + 1.5 * ((k * 5) % 7) / 6)
        out += glint([c[0] + math.cos(a) * r, height * (0.3 + 0.9 * ((k * 3) % 5) / 4), c[2] + math.sin(a) * r], t0 + 0.08 + dur * 0.06 * k,
                     size=1.6 + 0.9 * (k % 3), life=0.22, seed=seed + 10 + k)
    return out
