"""Thunder fruit authoring kit: plumbing only (palette, layer conventions, stack helpers, the burn-scar calling
card). Each move's staging, timing and signature are hand-written in its own spec script, never here.

Layer conventions for the approved layered textures (same as the approved texture previews):
  glow  additive halo        LightEmission 1    blue
  rim   alpha-blended edge   LightEmission 0    indigo   <- the dark outline that stops white-out on sand
  mid   body                 LightEmission 0.1  cyan
  core  hot line             LightEmission 0.35 white
"""
import json
import os

WHITE, ICE, CYAN, BLUE, INDIGO, NAVY, SOOT = "#ffffff", "#bff3ff", "#6fe0ff", "#3a5cff", "#2a1a9a", "#2a3350", "#0e1018"
LAYERS = ("glow", "rim", "mid", "core")
LE = {"glow": 1, "rim": 0, "mid": 0.1, "core": 0.35}
BR = {"glow": 1.0, "rim": 1.0, "mid": 1.15, "core": 1.4}
STRIPS = [f"thunder_strip_v2_{i}" for i in range(1, 5)]  # v2 cel strips (anime reference)

# colour script per layer as it cools (k = 0 strike -> 1 gone): white-hot -> cyan -> blue -> indigo afterglow
COOL = {
    "glow": [[0, BLUE], [0.4, "#3040d0"], [1, INDIGO]],
    "rim": [[0, BLUE], [0.4, INDIGO], [1, NAVY]],
    "mid": [[0, WHITE], [0.12, CYAN], [0.5, BLUE], [1, INDIGO]],
    "core": [[0, WHITE], [0.3, ICE], [0.6, CYAN], [1, BLUE]],
}
HOT = {"glow": BLUE, "rim": INDIGO, "mid": CYAN, "core": WHITE}


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


def scar(at, t, size=10, rot=0, glow_life=0.9, soot_life=3.2):
    """Calling card: a Lichtenberg burn flat on the ground that flashes hot, cools through the colour script to
    indigo, and leaves the soot scar under it fading last."""
    g = [at[0], 0.1, at[2]]   # ground decals: never a negative ZOffset (it pushes the quad into the ground and hides it)
    soot = {"type": "emitter", "at": [at[0], 0.06, at[2]], "emits": [[t, 1]], "props": {
        "Texture": "scorch_burn", "Color": SOOT, "LightEmission": 0, "Brightness": 1, "Size": [[0, size * 0.9], [0.05, size * 1.05], [1, size * 1.05]],
        "Lifetime": [soot_life, soot_life], "Speed": [0.01, 0.01], "Rotation": [rot, rot], "Orientation": "VelocityPerpendicular",
        "Transparency": [[0, 0.15], [0.7, 0.3], [1, 1]], "ZOffset": 0.02}}
    glow = emit_stack("lichtenberg", g, t, size=[[0, size * 0.85], [0.06, size], [1, size]], life=glow_life, layout="None",
                      colors=COOL, rot=rot, orient="VelocityPerpendicular", z=0.05,
                      transparency=[[0, 0], [0.1, 0], [0.14, 0.5], [0.2, 0.05], [0.5, 0.35], [1, 1]])
    return [soot] + glow


def write(fx, path):
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
    """thunder_burst laid flat on the ground: its shock ring becomes a shockwave in perspective, its bolts rake the sand."""
    return emit_stack("thunder_burst_v2", [at[0], 0.25, at[2]], t, size=[[0, size * 0.7], [0.15, size], [1, size * 1.08]], life=life,
                      seed=seed, orient="VelocityPerpendicular", colors=COOL, z=-0.2)


def dust(at, t, n=9, size=(5, 11), seed=61):
    """White anime dust thrown out low and sideways from a landing (RELL impact)."""
    return {"type": "emitter", "at": [at[0], 0.6, at[2]], "emits": [[t, n]], "seed": seed, "part": [5, 0.2, 5], "props": {
        "Texture": "dust_burst", "Color": "#d9d3c6", "LightEmission": 0, "Brightness": 1.0, "Shape": "Disc",
        "Size": [[0, size[0]], [1, size[1]]], "Lifetime": [0.6, 0.9], "Speed": [18, 26], "SpreadAngle": [8, 8],
        "EmissionDirection": "Top", "ShapeInOut": "Outward", "Drag": 4, "Acceleration": [0, 2, 0], "Rotation": [-15, 15],
        "Transparency": [[0, 0.05], [0.6, 0.3], [1, 1]], "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot",
        "Orientation": "FacingCameraWorldUp", "ZOffset": -0.6}}


def smoke_burst(at, t, n=6, seed=63):
    """Dark storm smoke kicked up by the strike (the dark anchor at the hit)."""
    return {"type": "emitter", "at": at, "emits": [[t, n]], "seed": seed, "props": {
        "Texture": "smoke_puff", "Color": [[0, "#3a4570"], [1, NAVY]], "LightEmission": 0, "Brightness": 1,
        "Size": [[0, 3], [1, 7.5]], "Lifetime": [0.8, 1.2], "Speed": [4, 9], "SpreadAngle": [70, 70], "Drag": 3,
        "Acceleration": [0, 3, 0], "Rotation": [0, 360], "RotSpeed": [-30, 30], "Transparency": [[0, 0.15], [0.7, 0.5], [1, 1]],
        "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot", "ZOffset": -0.4}}


def light(at, keys, color=CYAN, rng=14):
    # Roblox PointLight brightness ~1-8; anything hotter floods the sand white
    return {"at": at, "color": color, "range": rng, "brightness": [[t, round(v * 0.18, 2)] + k[2:] for t, v, *k in [list(x) for x in keys]]}
