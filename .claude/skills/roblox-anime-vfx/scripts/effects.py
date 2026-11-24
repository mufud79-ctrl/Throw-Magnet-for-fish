"""RELL-style move library: 10 element kits x 10 move archetypes = 100 effects, written as JSON specs.

    python3 effects.py [--out ../lab/effects] [--only Flame,Quake] [--list]

One spec drives both the headless previewer (lab/page/vfx.js) and the Roblox runtime (templates/AnimeVFX).
Units are studs; the caster stands at the origin facing -Z; Y is up. Times are seconds from the cast.

Building blocks (all reuse the approved texture library and mesh kit):
  stack()    4 white layers (_glow/_rim/_mid/_core) on one attachment with IDENTICAL deterministic motion
             (separate Roblox emitters cannot share random numbers, so stacks never randomise; variety comes
             from several stacks with seeded offsets, angles and sizes)
  sparks()   one random emitter (embers / flecks / smoke / dust): free to randomise
  ring()     flat shockwave particle (VelocityPerpendicular, speed ~0) on the ground or facing a direction
  shell()    Part + SpecialMesh shell: scale / transparency / spin keys, Neon / ForceField / Textured / Ice
  beam(), bolt(), crater(), fling(), light(), shake(), grade(), impact()
Element kits pick colours, textures, meshes and signature extras; archetypes pick timing and staging.
"""
import os
import json
import math
import random
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "lab", "effects")
HAND = (1.5, 3.8, -2.3)      # right hand at full extension after a throw
CHEST = (0.0, 3.4, -0.6)
TARGET = (0.0, 0.0, -24.0)


def add(a, b):
    return [round(a[0] + b[0], 3), round(a[1] + b[1], 3), round(a[2] + b[2], 3)]


def lerp3(a, b, t):
    return [round(a[i] + (b[i] - a[i]) * t, 3) for i in range(3)]


class FX:
    def __init__(self, name, title, element, archetype, duration, seed):
        self.d = {"name": name, "title": title, "element": element, "archetype": archetype, "duration": duration,
                  "layers": [], "lights": [], "shakes": [], "grade": [], "impact": [], "debris": [], "dummies": []}
        self.r = random.Random(seed)

    def layer(self, L):
        L = {k: v for k, v in L.items() if v is not None}
        self.d["layers"].append(L)
        return L

    def seed(self):
        return self.r.randint(1, 10 ** 6)


# ---------------------------------------------------------------- element kits
def kit(**k):
    k.setdefault("smoke", None)
    k.setdefault("smoke_tex", "smoke_puff")
    k.setdefault("spark_tex", "flecks")
    k.setdefault("spark_le", 1)
    k.setdefault("ring_tex", "shock_ring")
    k.setdefault("shell_mat", "ForceField")
    k.setdefault("ground", None)
    k.setdefault("hero", None)
    k.setdefault("hero_mesh", None)
    k.setdefault("loop", "aura_wisp")
    k.setdefault("extra", ())
    k.setdefault("layer_le", {})
    k.setdefault("number", "#ffd23a")
    k.setdefault("burst2", None)
    k.setdefault("body", None)          # projectile body: None | {"mesh", "material", "color", "scale", "rot"} | "bolt" | "crescent"
    k.setdefault("beam_style", None)    # flame | bolts | ice | rings | slashes | void | water
    k.setdefault("column", None)        # texture for eruption columns
    k.setdefault("trail", None)         # texture left behind by projectiles and dashes
    return k


# Each element has its own painted matter (main burst, secondary burst, sparks, smoke) so moves read as that
# element, not as recoloured fire. All textures are greyscale; these colours tint them.
KITS = {
    "Flame": kit(glow="#ff5a14", rim="#d42e14", mid=[[0, "#ffd36a"], [0.35, "#ff9a2a"], [1, "#e0461c"]], core="#fff3c4",
                 main="fire_burst", loop="flame_lick", spark_tex="embers", spark="#ff8a2a", smoke="#3a302e", light="#ff8a3a",
                 beam_style="flame", trail="fire_burst", column="flame_lick",
                 shell="#ff9a3a", ring=("#ffcf7a", "#ff6a22"), ground=("crack_glow", "#ff7a2a"), hero="dragon_head",
                 hero_mesh="dragon_head", grade="#ffd8b4", number="#ffb02a"),
    "Magma": kit(glow="#ff3a0a", rim="#3a0a04", mid=[[0, "#ffb347"], [0.3, "#ff5a14"], [1, "#9a1a0a"]], core="#ffe0a0",
                 main="magma_splash", burst2="fire_burst", loop="flame_lick", spark_tex="lava_drops", spark="#ff7a2a", spark_le=0.7,
                 body={"mesh": "giant_fist", "material": "Neon", "color": "#ff5a14", "scale": [1.6, 1.6, 2.2], "rot": [0, 180, 0]},
                 beam_style="flame", trail="fire_burst",
                 smoke="#1e1614", light="#ff4a1a", shell="#ff4a14", shell_mat="Neon", ring=("#ff9a3a", "#c2280e"),
                 ground=("crack_glow", "#ff4a10"), hero="giant_fist", hero_mesh="giant_fist", grade="#ffc2a0", extra=("rocks",), number="#ff7a2a"),
    "Light": kit(glow="#ffb000", rim="#ff8000", mid="#ffd23a", core="#fff6d0", main="light_burst", burst2="star_flash",
                 body={"mesh": "spike", "material": "Neon", "color": "#ffd84a", "scale": [0.55, 2.6, 0.55], "rot": [-90, 0, 0]}, column="light_burst",
                 spark_tex="flecks", spark="#ffe27a", light="#ffd84a", shell="#ffe27a", ring=("#fff2b0", "#ffb81a"),
                 ground=("crack_glow", "#ffd84a"), hero="palm_strike", grade="#fff0c0", extra=("rays", "squares", "pit"), number="#fff06a"),
    "Quake": kit(glow="#14d8a8", rim="#067a62", mid="#4affcc", core="#e6fff7", main="glass_shatter", burst2="shock_ripple",
                 beam_style="rings", column="shock_ripple", trail="shock_ripple",
                 spark_tex="flecks", spark="#c8fff2", light="#4affd6", shell="#8affe8", ring=("#e0fff8", "#2ad8b0"),
                 ground=("crack_glow", "#3affd0"), hero="giant_fist", hero_mesh="giant_fist", grade="#c8fff4",
                 extra=("bubble", "glass", "rocks"), number="#7affe0"),
    "Ice": kit(glow="#2a8cff", rim="#1450c8", mid="#78c4ff", core="#d6efff", main="ice_burst", spark_tex="ice_chips", spark="#cfeeff",
               shell_color_ice="#5cb8ff",
               body={"mesh": "spike_bent", "material": "Ice", "color": "#9fdcff", "scale": [0.8, 2.4, 0.8], "rot": [-90, 0, 0]},
               beam_style="ice", column="ice_burst", trail="frost_mist",
               spark_le=0.4, smoke="#a8d4ff", smoke_tex="frost_mist", light="#a8e4ff", shell="#62bcff", shell_mat="Ice",
               ring=("#bfe6ff", "#3a8cff"), ground=("crack_glow", "#bfeaff"), grade="#d8f0ff", extra=("spikes", "wind"), number="#9fe4ff"),
    "Dark": kit(glow="#7a2cff", rim="#c9a0ff", mid="#3a1068", core="#07000d", main="void_smoke", burst2="void_orb",
                beam_style="void", column="void_smoke", trail="void_smoke",
                spark_tex="flecks", spark="#b07aff", smoke="#120818", light="#8a3aff", shell="#16061f", shell_mat="Neon",
                ring=("#c9a0ff", "#3a0a6a"), ground=("crack_glow", "#8a3aff"), grade="#c8b0e0", extra=("swirl", "void"),
                layer_le={"core": 0, "mid": 0}, number="#c08aff"),
    "Thunder": kit(glow="#2a7cff", rim="#1a2cd0", mid="#7ac4ff", core="#eef8ff", main="electric_burst", burst2="lightning",
                   body="bolt", beam_style="bolts", column="electric_burst", trail="electric_burst",
                   spark_tex="flecks", spark="#d6f0ff", light="#6ab8ff", shell="#8ac8ff", ring=("#bfe0ff", "#2a6cff"),
                   ground=("crack_glow", "#7ac0ff"), hero="dragon_head", hero_mesh="dragon_head", grade="#c8dcff", extra=("bolts",), number="#8ad0ff"),
    "Haki": kit(glow="#ff1e3c", rim="#5a0010", mid="#ff2a48", core="#0a0003", main="haki_burst", burst2="lightning",
                body={"mesh": "giant_fist", "material": "Neon", "color": "#0c0306", "scale": [1.6, 1.6, 2.2], "rot": [0, 180, 0]},
                beam_style="bolts", column="haki_burst", trail="haki_burst",
                spark_tex="flecks", spark="#ff6a7a", smoke="#0c0408", light="#ff2a3a", shell="#14060a", shell_mat="Neon",
                ring=("#ffd0d8", "#c00a24"), ground=("crack_glow", "#ff2040"), hero="giant_fist", hero_mesh="giant_fist",
                grade="#ffc0c8", extra=("bolts", "invert"), layer_le={"core": 0}, number="#ff5a6a"),
    "Blade": kit(glow="#2a8cff", rim="#1a3cd8", mid="#7ab8ff", core="#eef6ff", main="blade_cuts", burst2="slash",
                 body="crescent", beam_style="slashes", column="slash", trail="slash",
                 spark_tex="flecks", spark="#d0ecff", light="#7ac0ff", shell="#bfe4ff", ring=("#c6e2ff", "#3a7cff"),
                 ground=("crack_glow", "#9fd8ff"), hero="phoenix_wing", hero_mesh="phoenix_bird", grade="#d0e4ff", extra=("wind",), number="#d6efff"),
    "Water": kit(glow="#1a90ff", rim="#0a48a8", mid="#5ab8ff", core="#e8f6ff", main="water_splash", spark_tex="water_drops", spark="#d8f2ff",
                 beam_style="water", column="aura_wisp", trail="spray_puff",
                 spark_le=0.15, smoke="#eef8ff", smoke_tex="spray_puff", light="#5ac0ff", shell="#7ac8ff", shell_mat="Glass",
                 ring=("#c6e8ff", "#1a7cff"), ground=None, hero="water_shark", grade="#cfe8ff", extra=("wave",),
                 layer_le={"glow": 0.4, "core": 0.2, "mid": 0}, number="#9ad8ff"),
}

GRID = {t: "Grid4x4" for t in ("fire_burst", "flame_lick", "aura_wisp", "star_flash", "god_rays", "orb_glow", "slash", "lightning",
                               "smoke_puff", "dust_burst", "embers", "magma_splash", "lava_drops", "light_burst", "shock_ripple",
                               "ice_burst", "frost_mist", "ice_chips", "void_smoke", "void_orb", "electric_burst", "haki_burst",
                               "blade_cuts", "water_splash", "spray_puff", "water_drops")}
GRID.update({"flecks": "Grid2x2", "wind_arcs": "Grid2x2"})
LOOPING = {"flame_lick", "aura_wisp", "orb_glow", "void_orb"}
GROUNDED = {"magma_splash", "water_splash"}        # painted with their base at the bottom of the cell
LAYER = {  # per-layer look in a stack (kits can override LightEmission with layer_le)
    "glow": {"LightEmission": 1, "Brightness": 1.0, "dt": 0.58, "z": 0.0},
    "rim": {"LightEmission": 0, "Brightness": 1.0, "dt": 0.0, "z": 0.05},
    "mid": {"LightEmission": 0.1, "Brightness": 1.15, "dt": 0.0, "z": 0.1},
    "core": {"LightEmission": 0.35, "Brightness": 1.35, "dt": 0.0, "z": 0.15},
}
SQUASH_HIT = [[0, -0.45], [0.16, 0.28], [0.4, 0]]     # squash flat on contact, stretch, settle



def tseq(base, add_=0.0):
    """Transparency sequence with an offset (glow layer is fainter)."""
    if isinstance(base, (int, float)):
        return min(1.0, base + add_)
    return [[k[0], round(min(1.0, k[1] + add_), 3)] + k[2:] for k in base]


# ---------------------------------------------------------------- building blocks
def stack(fx, tex, at, K, t, size, life, count=1, speed=0.0, direction="Top", rot=None, rotation=0, rotspeed=0,
          orient="FacingCamera", accel=None, drag=0, transp=None, colors=None, move=None, locked=False, rate=None,
          layers=("glow", "rim", "mid", "core"), z=0.0, squash=0, fps=None, zb=0.0):
    seed = fx.seed()
    colors = colors or K
    transp = transp if transp is not None else [[0, 0], [0.75, 0.15], [1, 1]]
    grid = GRID.get(tex, "None")
    for L in layers:
        lk = LAYER[L]
        tname = f"{tex}_{L}"
        le = (colors.get("layer_le") or {}).get(L, lk["LightEmission"]) if isinstance(colors, dict) else lk["LightEmission"]
        props = {"Texture": tname, "Color": colors[L], "LightEmission": le, "Brightness": lk["Brightness"],
                 "Size": size, "Transparency": tseq(transp, lk["dt"]), "Lifetime": life, "Speed": speed, "Rotation": rotation,
                 "RotSpeed": rotspeed, "EmissionDirection": direction, "Orientation": orient, "ZOffset": round(zb + lk["z"] + z, 3),
                 "LockedToPart": locked, "Drag": drag}
        if squash:
            props["Squash"] = squash
        if accel:
            props["Acceleration"] = accel
        if grid != "None":
            props["FlipbookLayout"] = grid
            if tex in LOOPING:
                props.update(FlipbookMode="Loop", FlipbookFramerate=fps or 24)
            else:
                props["FlipbookMode"] = "OneShot"
        Ly = {"type": "emitter", "at": list(at), "props": props, "seed": seed, "stack": tex}
        if rot:
            Ly["rot"] = rot
        if move:
            Ly["move"] = move
        if rate:
            Ly["rate"] = rate
        else:
            Ly["emits"] = [[round(t, 3), count]]
        fx.layer(Ly)


def sparks(fx, at, K, t, count=24, speed=(18, 34), life=(0.35, 0.7), size=(0.5, 0.25), spread=180, direction="Top",
           tex=None, color=None, accel=(0, -30, 0), drag=2.5, le=None, move=None, rate=None, part=None, orient=None, rot=None):
    """Random single-texture emitter. Default gravity makes every spark fall on an arc (rule 5)."""
    le = (K["spark_le"] if not tex else 1) if le is None else le
    tex = tex or K["spark_tex"]
    grid = GRID.get(tex, "None")
    props = {"Texture": tex, "Color": color or K["spark"], "LightEmission": le, "Brightness": 1.6,
             "Size": [[0, size[0]], [1, size[1]]] if isinstance(size, tuple) else size, "Transparency": [[0, 0], [0.7, 0.1], [1, 1]],
             "Lifetime": list(life), "Speed": list(speed) if isinstance(speed, tuple) else speed, "SpreadAngle": [spread, spread],
             "EmissionDirection": direction, "Acceleration": list(accel), "Drag": drag, "Rotation": [0, 360], "RotSpeed": [-300, 300],
             "ZOffset": 0.3}
    if orient:
        props["Orientation"] = orient
    if grid != "None":
        props.update(FlipbookLayout=grid, FlipbookMode="Loop", FlipbookFramerate=0.01, FlipbookStartRandom=True)
    L = {"type": "emitter", "at": list(at), "props": props, "seed": fx.seed()}
    if rot:
        L["rot"] = rot
    if move:
        L["move"] = move
    if part:
        L["part"] = part
    if rate:
        L["rate"] = rate
    else:
        L["emits"] = [[round(t, 3), count]]
    fx.layer(L)


def smoke(fx, at, K, t, count=8, size=(4, 9), life=(0.9, 1.4), speed=(4, 9), spread=70, color=None, tex=None, rise=3, direction="Top", part=None):
    if not (color or K["smoke"]):
        return
    tex = tex or K["smoke_tex"]
    accel = list(rise) if isinstance(rise, (list, tuple)) else [0, rise, 0]
    props = {"Texture": tex, "Color": color or K["smoke"], "LightEmission": 0, "Brightness": 1, "Size": [[0, size[0]], [1, size[1]]],
             "Transparency": [[0, 0.05], [0.7, 0.2], [1, 1]], "Lifetime": list(life), "Speed": list(speed), "SpreadAngle": [spread, spread],
             "EmissionDirection": direction, "Acceleration": accel, "Drag": 2.5, "Rotation": [0, 360], "RotSpeed": [-30, 30],
             "FlipbookLayout": "Grid4x4", "FlipbookMode": "OneShot", "ZOffset": -0.2}
    L = {"type": "emitter", "at": list(at), "props": props, "emits": [[round(t, 3), count]], "seed": fx.seed()}
    if part:
        L["part"] = part
    fx.layer(L)


def dust(fx, at, t, count=6, size=(5, 12), color="#efe3c8"):
    props = {"Texture": "dust_burst", "Color": color, "LightEmission": 0, "Size": [[0, size[0]], [1, size[1]]],
             "Transparency": [[0, 0.1], [0.6, 0.25], [1, 1]], "Lifetime": [0.8, 1.2], "Speed": [8, 16], "SpreadAngle": [85, 10],
             "EmissionDirection": "Top", "Acceleration": [0, 2, 0], "Drag": 3, "Rotation": [-10, 10], "FlipbookLayout": "Grid4x4",
             "FlipbookMode": "OneShot", "ZOffset": -0.3, "Orientation": "FacingCameraWorldUp"}
    fx.layer({"type": "emitter", "at": list(at), "props": props, "emits": [[round(t, 3), count]], "seed": fx.seed(), "rot": [0, 0, 90]})


def ring(fx, at, K, t, s0=2, s1=26, life=0.45, facing="Top", tex=None, colors=None, rot=None, transp=None, layers=("glow", "mid", "core")):
    """Flat shockwave: VelocityPerpendicular particle with ~zero speed lies flat across the facing axis."""
    tex = tex or K["ring_tex"]
    c_core, c_mid = colors or K["ring"]
    cols = {"glow": c_mid, "rim": K["rim"], "mid": c_mid, "core": c_core}
    stack(fx, tex, at, cols, t, [[0, s0], [1, s1, ]], life, speed=0.01, direction=facing, orient="VelocityPerpendicular",
          transp=transp or [[0, 0.05], [0.5, 0.3], [1, 1]], layers=layers, rot=rot, zb=0.4)


def flash(fx, at, K, t, size=10, life=0.35, rays=True):
    mid = K["mid"] if isinstance(K["mid"], str) else K["mid"][0][1]
    core = K["core"] if K["core"] not in ("#07000d", "#0a0003") else mid
    stack(fx, "star_flash", at, {"glow": K["glow"], "rim": K["rim"], "mid": mid, "core": core, "layer_le": K["layer_le"]},
          t, [[0, size * 0.6], [0.2, size], [1, size * 0.8]], life, rotation=fx.r.randint(0, 90), zb=0.8, squash=SQUASH_HIT)
    if rays:
        stack(fx, "god_rays", at, {"glow": K["glow"], "rim": K["rim"], "mid": mid, "core": core}, t,
              [[0, size * 1.2], [1, size * 2.2]], life * 1.6, rotation=fx.r.randint(0, 90), layers=("glow", "mid"), zb=0.5,
              transp=[[0, 0.2], [0.7, 0.4], [1, 1]])


def shell(fx, mesh, at, t, life, scale, color, material="ForceField", transp=None, rot=None, spin=None, spin_axis=None,
          texture=None, scroll=None, move=None, brightness=1.0, velocity=None, tile=None, z=0):
    L = {"type": "shell", "mesh": mesh, "at": list(at), "t0": round(t, 3), "life": life, "scale": scale, "color": color,
         "material": material, "transparency": transp if transp is not None else [[0, 0.1], [0.6, 0.4], [1, 1]],
         "brightness": brightness, "z": z}
    for k, v in (("rot", rot), ("spin", spin), ("spinAxis", spin_axis), ("texture", texture), ("scroll", scroll),
                 ("move", move), ("velocity", velocity), ("tile", tile)):
        if v is not None:
            L[k] = v
    fx.layer(L)


def beam(fx, a, b, t, life, K, width=(3, 2.4), tex="beam_strip_mid", color=None, reach=None, speed=-40, curve=None, layers=True):
    w = [[0, [0, 0]], [0.08, list(width), "out"], [0.8, list(width)], [1, [0, 0], "in"]]
    if layers:
        fx.layer({"type": "beam", "from": list(a), "to": list(b), "t0": t, "life": life, "texture": "beam_strip_glow", "color": K["glow"],
                  "width": [[k[0], [x * 1.45 for x in k[1]]] + k[2:] for k in w], "lightEmission": 1, "textureSpeed": speed, "textureLength": 10,
                  "transparency": 0.35,
                  "reach": reach, "curve": curve})
        fx.layer({"type": "beam", "from": list(a), "to": list(b), "t0": t, "life": life, "texture": "beam_strip_mid", "color": color or (K["mid"] if isinstance(K["mid"], str) else K["mid"][1][1]),
                  "width": w, "lightEmission": 0.2, "textureSpeed": speed, "textureLength": 10, "reach": reach, "curve": curve})
    fx.layer({"type": "beam", "from": list(a), "to": list(b), "t0": t, "life": life, "texture": "beam_strip_core", "color": "#ffffff",
              "width": [[k[0], [x * 0.28 for x in k[1]]] + k[2:] for k in w], "lightEmission": 0.4, "brightness": 1.3,
              "textureSpeed": speed * 1.3, "textureLength": 10, "reach": reach, "curve": curve})


def bolt(fx, a, b, t, life, color, thickness=0.35, jitter=1.4, segments=9, flicker=0.05):
    fx.layer({"type": "bolt", "from": list(a), "to": list(b), "t0": t, "life": life, "color": color, "thickness": thickness,
              "jitter": jitter, "segments": segments, "flicker": flicker, "seed": fx.seed(), "transparency": [[0, 0], [0.7, 0.1], [1, 1]]})


def crater(fx, at, t, radius=8, count=14, size=3, life=3.0, pit="#2a2420"):
    fx.d["debris"].append({"kind": "crater", "at": list(at), "t": t, "radius": radius, "count": count, "size": size, "life": life,
                           "seed": fx.seed(), "pitColor": pit})


def fling(fx, at, t, count=14, speed=34, size=1.4, life=1.8, color=None):
    D = {"kind": "fling", "at": list(at), "t": t, "count": count, "speed": speed, "size": size, "life": life, "seed": fx.seed()}
    if color:
        D["color"] = color
    fx.d["debris"].append(D)


def light(fx, at, t, color, peak=6, rng_=22, life=0.6, move=None):
    L = {"at": list(at), "color": color, "range": rng_, "brightness": [[t, 0], [t + 0.04, peak], [t + life, 0]]}
    if move:
        L["move"] = move
    fx.d["lights"].append(L)


def shake(fx, t, amp=0.6, dur=0.4, freq=22):
    fx.d["shakes"].append({"t": t, "amp": amp, "dur": dur, "freq": freq})


def impact(fx, t, mode="invert", dur=0.05):
    fx.d["impact"].append({"t": t, "dur": dur, "mode": mode})


def grade(fx, keys):
    fx.d["grade"] = keys


def ground_mark(fx, at, K, t, size=14, life=1.6):
    if not K["ground"]:
        return
    tex, col = K["ground"]
    stack(fx, tex, add(at, (0, 0.15, 0)), {"glow": col, "rim": "#1a0d08", "mid": col, "core": "#ffffff"}, t,
          [[0, size * 0.7], [0.1, size], [1, size]], life, speed=0.01, orient="VelocityPerpendicular",
          transp=[[0, 0.1], [0.6, 0.3], [1, 1]], layers=("mid", "core"), rotation=fx.r.randint(0, 360), zb=-0.5)


# ---------------------------------------------------------------- element signatures
# ---------------------------------------------------------------- animation rules
# The five rules every move follows (Disney, 1930s):
#   1 anticipation   caster winds up and leans back while energy gathers; the charge orb pinches before release
#   2 squash/stretch projectiles stretch along their flight; bursts and shells squash flat on contact, then
#                    stretch; the target squashes on the hit
#   3 follow-through caster overshoots and settles; trails lag and linger; the burst keeps flying on past the
#                    target along the travel direction; smoke drifts after
#   4 timing         hit-stop: the simulation freezes for a few frames on every hit (shake keeps going)
#   5 arcs           projectiles curve, sparks / debris / damage numbers fly on gravity arcs
HAND_BACK = (1.7, 3.7, 2.1)      # right hand cocked behind the shoulder (anticipation)


def dir_rot(d):
    """Euler XYZ degrees that turn the emitter's Front (-Z) toward direction d."""
    dx, dy, dz = d
    yaw = math.degrees(math.atan2(-dx, -dz))
    pitch = math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    return [round(pitch, 2), round(yaw, 2), 0]


def unit(d):
    l = math.sqrt(sum(c * c for c in d)) or 1
    return [d[0] / l, d[1] / l, d[2] / l]


def pose(fx, **tracks):
    P = fx.d.setdefault("pose", {})
    for k, v in tracks.items():
        P[k] = v


def pose_throw(fx, tr, wind=0.35, k=1.0):
    """Wind up (lean back, arm cocked, body squashes), snap the throw, overshoot, settle."""
    w0 = max(0.0, tr - wind)
    pose(fx,
         lean=[[0, 0], [w0, 0], [tr - 0.03, 16 * k, "out"], [tr + 0.06, -22 * k, "out"], [tr + 0.3, -7 * k], [tr + 0.75, 0]],
         twist=[[0, 0], [w0, 0], [tr - 0.03, 28 * k, "out"], [tr + 0.06, -22 * k, "out"], [tr + 0.5, 0]],
         armR=[[0, 0], [w0, 0], [tr - 0.03, -78, "out"], [tr + 0.05, 95, "out"], [tr + 0.4, 84], [tr + 0.95, 8]],
         armL=[[0, 0], [w0, 0], [tr - 0.03, 32], [tr + 0.05, -38, "out"], [tr + 0.6, 0]],
         offset=[[0, [0, 0, 0]], [w0, [0, 0, 0]], [tr - 0.03, [0, 0, 0.35]], [tr + 0.08, [0, 0, -0.7], "out"], [tr + 0.6, [0, 0, -0.55]]],
         scale=[[0, [1, 1, 1]], [w0, [1, 1, 1]], [tr - 0.04, [1.05, 0.92, 1.05], "out"], [tr + 0.05, [0.95, 1.07, 0.95]], [tr + 0.28, [1, 1, 1]]])


def hit(fx, at, K, t, scale=1.0, direction=(0, 0, -1), dummy=0, dmg=None, stop=0.08, ground=True, number=True):
    """Every connecting hit: hit-stop, target squash + knockback, arcing damage number, the element burst
    (squash -> stretch) and a follow-through spray that keeps flying along the travel direction."""
    fx.d.setdefault("hitstop", []).append({"t": round(t, 3), "dur": round(stop * (0.75 + 0.25 * min(scale, 2)), 3)})
    d = unit(direction)
    if dummy is not None and fx.d["dummies"]:
        fx.d.setdefault("hits", []).append({"t": round(t, 3), "dummy": dummy, "dir": [round(d[0], 3), 0, round(d[2], 3)],
                                           "power": round(min(1.4, 0.55 + 0.4 * scale), 2)})
    if number:
        dmg = dmg or int(fx.r.uniform(60, 140) * scale)
        fx.d.setdefault("numbers", []).append({"t": round(t, 3), "at": add(at, (fx.r.uniform(-1, 1), 6.2, 0)), "text": str(dmg),
                                              "color": K["number"], "vel": [round(fx.r.choice([-1, 1]) * fx.r.uniform(2.5, 4.5), 2), 17, 0],
                                              "size": round(2.0 + 0.5 * min(scale, 2), 2)})
    element_impact(fx, at, K, t, scale, ground)
    follow_through(fx, at, K, t, scale, d)


def follow_through(fx, at, K, t, s, d):
    """The burst flies on: sparks and a secondary puff carried forward along d, smoke drifting after."""
    c = add(at, (0, 2.5 * s, 0))
    sparks(fx, c, K, t, count=int(26 * s), speed=(30 * s, 56 * s), life=(0.45, 0.85), size=(0.9 * s, 0.25 * s), spread=32,
           direction="Front", rot=dir_rot(d), accel=(0, -40, 0), drag=1.8)
    tex = K["burst2"] or K["main"]
    if tex in GRID and tex not in GROUNDED:
        far = add(c, (d[0] * 7 * s, d[1] * 7 * s + 0.8, d[2] * 7 * s))
        stack(fx, tex, c, K, t + 0.02, [[0, 5 * s], [1, 8 * s]], 0.55, move={"from": c, "to": far, "t0": t + 0.02, "t1": t + 0.5, "ease": "out"},
              locked=True, rotation=fx.r.randint(0, 360), transp=[[0, 0.1], [0.7, 0.3], [1, 1]], squash=SQUASH_HIT)
    if K["smoke"]:
        smoke(fx, c, K, t + 0.08, count=int(6 * s), size=(4 * s, 9 * s), speed=(3, 7), rise=(d[0] * 6, 2.5, d[2] * 6))


def element_impact(fx, at, K, t, s=1.0, ground=True):
    """The element's own burst: its painted main matter (squash -> stretch), secondary burst, flash, sparks,
    smoke, ground ring/mark, light, shake and signature extras."""
    main, b2 = K["main"], K["burst2"]
    chest = add(at, (0, 3 * s, 0))
    if main == "fire_burst":
        for k in range(3):
            off = (fx.r.uniform(-1.5, 1.5) * s, fx.r.uniform(0.5, 2.5) * s, fx.r.uniform(-1.5, 1.5) * s)
            stack(fx, "fire_burst", add(at, off), K, t + k * 0.04, [[0, 7 * s], [1, 13 * s]], 0.9 + 0.1 * k,
                  rotation=fx.r.randint(-30, 30), transp=[[0, 0], [0.8, 0.05], [1, 1]], squash=SQUASH_HIT)
    elif main in GROUNDED:
        for k, dx in enumerate((-1.2, 1.0, 0.0)):
            sz = (12 if k == 2 else 9) * s
            stack(fx, main, add(at, (dx * s, sz * 0.42, 0)), K, t + k * 0.04, sz, 0.9, rotation=fx.r.randint(-12, 12),
                  transp=[[0, 0], [0.85, 0.05], [1, 1]], squash=[[0, -0.35], [0.2, 0.15], [0.5, 0]], zb=0.3)
    else:
        stack(fx, main, chest, K, t, [[0, 9 * s], [0.25, 14 * s], [1, 15 * s]], 0.75, rotation=fx.r.randint(0, 360),
              transp=[[0, 0], [0.75, 0.1], [1, 1]], squash=SQUASH_HIT, zb=0.6)
    if b2 and b2 != main:
        stack(fx, b2, chest, K, t + 0.03, [[0, 8 * s], [1, 12 * s]], 0.6, rotation=fx.r.randint(0, 360),
              transp=[[0, 0], [0.7, 0.15], [1, 1]], squash=SQUASH_HIT, zb=0.5, layers=("glow", "mid", "core"))
    flash(fx, chest, K, t, size=9 * s, rays=main != "light_burst")
    sparks(fx, add(at, (0, 2 * s, 0)), K, t, count=int(22 * s), speed=(20 * s, 40 * s), size=(0.9 * s, 0.3 * s))
    smoke(fx, add(at, (0, 1.5 * s, 0)), K, t + 0.05, count=int((5 if K["smoke_tex"] != "smoke_puff" else 8) * s), size=(5 * s, 11 * s), speed=(6 * s, 12 * s))
    if ground:
        ring(fx, add(at, (0, 0.3, 0)), K, t, 2 * s, 26 * s, 0.5)
        ground_mark(fx, at, K, t, 15 * s)
        dust(fx, at, t + 0.03, size=(6 * s, 14 * s))
    light(fx, add(at, (0, 3, 0)), t, K["light"], peak=7, rng_=24 * s)
    shake(fx, t, 0.5 * s, 0.4)
    ex = K["extra"]
    if "bubble" in ex:   # quake: a refracting shock sphere that squashes then stretches
        shell(fx, "sphere", chest, t, 0.4, [[0, [1 * s, 0.5 * s, 1 * s]], [0.3, [5 * s, 6 * s, 5 * s], "outExpo"], [1, [7 * s, 6.6 * s, 7 * s]]],
              K["shell"], "ForceField", transp=[[0, 0.5], [0.5, 0.7], [1, 1]], brightness=0.6)
        shell(fx, "sphere", chest, t, 0.35, [[0, 1 * s], [1, 9 * s, "outExpo"]], K["shell"], "Glass", transp=[[0, 0.5], [1, 1]])
    if "glass" in ex:
        stack(fx, "crack_glow", add(at, (0, 0.2, 0)), K, t, [[0, 10 * s], [0.1, 18 * s], [1, 18 * s]], 1.4, speed=0.01,
              orient="VelocityPerpendicular", transp=[[0, 0], [0.7, 0.2], [1, 1]], layers=("mid", "core"))
    if "rocks" in ex and ground:
        fling(fx, at, t, count=int(14 * s), speed=30 * s, size=1.6 * s)
    if "rays" in ex:
        stack(fx, "god_rays", chest, K, t, [[0, 14 * s], [1, 26 * s]], 0.7, layers=("glow", "mid", "core"))
    if "squares" in ex:
        sparks(fx, chest, K, t, count=int(26 * s), speed=(6, 18), life=(0.8, 1.4), size=(1.0, 0.2), accel=(0, 4, 0), drag=2, tex="flecks")
    if "pit" in ex and ground and s >= 1.0:
        crater(fx, at, t, radius=6.5 * s, count=14, size=2.6 * s, pit="#1a1610")
    if "spikes" in ex and ground:
        for k in range(6):
            a = k / 6 * 360 + fx.r.uniform(-20, 20)
            off = (math.cos(math.radians(a)) * 3.5 * s, 0, math.sin(math.radians(a)) * 3.5 * s)
            shell(fx, "spike_bent", add(at, off), t + 0.02 * k, 1.6,
                  [[0, [0.3, 0.1, 0.3]], [0.1, [1.6 * s, 2.4 * s, 1.6 * s], "out"], [0.18, [1.3 * s, 3.4 * s, 1.3 * s]], [0.85, [1.4 * s, 3.2 * s, 1.4 * s]], [1, [1.2 * s, 0.2, 1.2 * s]]],
                  K["shell"], "Ice", transp=[[0, 0.05], [0.85, 0.1], [1, 1]], rot=[fx.r.uniform(-25, 25), -a, fx.r.uniform(15, 35)])
        shell(fx, "claw_cluster", add(at, (0, 1, 0)), t, 1.6, [[0, 0.3], [0.1, [4.4 * s, 2.6 * s, 4.4 * s], "out"], [0.2, 3.8 * s], [0.85, 3.8 * s], [1, 0.4]],
              K["shell"], "Ice", transp=[[0, 0.05], [0.85, 0.1], [1, 1]], rot=[0, fx.r.uniform(0, 360), 0])
    if "wind" in ex:
        sparks(fx, chest, K, t, count=4, tex="wind_arcs", color=K["mid"] if isinstance(K["mid"], str) else "#ffffff", speed=(0.5, 1), life=(0.3, 0.45),
               size=(5 * s, 12 * s), accel=(0, 0, 0), drag=0, le=0.15)
    if "swirl" in ex:
        shell(fx, "swirl", add(at, (0, 2 * s, 0)), t, 0.8, [[0, 2 * s], [1, 7 * s, "out"]], K["glow"], "ForceField", spin=-540,
              transp=[[0, 0.1], [1, 1]], brightness=1.5)
    if "void" in ex:
        shell(fx, "sphere", chest, t, 0.55, [[0, [1 * s, 0.6 * s, 1 * s]], [0.35, [5 * s, 6.5 * s, 5 * s], "outExpo"], [1, 0.2]], "#05000a", "Neon",
              transp=[[0, 0], [1, 0.1]])
    if "bolts" in ex:
        for k in range(5):
            a = fx.r.uniform(0, math.tau)
            end = add(at, (math.cos(a) * 9 * s, fx.r.uniform(0.5, 6) * s, math.sin(a) * 9 * s))
            bolt(fx, chest, end, t + 0.02 * k, 0.3, K["glow"], thickness=0.3 * s)
    if "invert" in ex and s >= 0.9:
        impact(fx, t, "invert", 0.05)
        impact(fx, t + 0.05, "mono", 0.04)
    if "wave" in ex and ground:
        for k in range(4):
            a = k * 90 + 45
            shell(fx, "wave_curl", add(at, (math.cos(math.radians(a)) * 2 * s, 0, math.sin(math.radians(a)) * 2 * s)), t, 0.9,
                  [[0, [1, 0.2, 1]], [0.25, [3 * s, 3.4 * s, 3 * s], "outBack"], [1, [4 * s, 1.5 * s, 4 * s]]], K["shell"], "Glass",
                  transp=[[0, 0.1], [0.6, 0.3], [1, 1]], rot=[0, -a - 90, 0])


def element_travel(fx, a, b, t0, t1, K, size=4.0, arc=1.5):
    """Projectile: a stretched core (VelocityParallel + Squash, rule 2) riding a curved path (rule 5), a trail
    of element matter left behind with drag so it lags and lingers (rule 3), arcing sparks and a light."""
    d = unit([b[i] - a[i] for i in range(3)])
    move = {"from": list(a), "to": list(b), "t0": t0, "t1": t1, "ease": "in", "arc": arc}
    life = t1 - t0 + 0.02
    body = K["body"]
    orb = size * (0.6 if body else 1.0)
    stack(fx, "orb_glow", a, K, t0, orb, life, move=move, locked=True, transp=[[0, 0], [1, 0]], zb=0.5, speed=0.05,
          direction="Front", rot=dir_rot(d), orient="VelocityParallel", squash=0.9)
    k = size / 4.5
    if isinstance(body, dict):      # a mesh flying point-first (spear, ice shard, molten / armament fist)
        sc = [round(c * k, 3) for c in body["scale"]]
        r = body["rot"]
        rot = [r[0] + dir_rot(d)[0], r[1] + dir_rot(d)[1], r[2]]
        shell(fx, body["mesh"], a, t0, life, [[0, [c * 0.5 for c in sc]], [0.15, [sc[0] * 0.8, sc[1] * 1.25, sc[2] * 1.25], "out"], [1, sc]],
              body["color"], body["material"], rot=rot, move=move, transp=[[0, 0], [1, 0]], brightness=1.6)
        if body["mesh"] in ("giant_fist",):   # glowing rim around the fist
            shell(fx, body["mesh"], a, t0, life, [[0, [c * 0.55 for c in sc]], [1, [c * 1.12 for c in sc]]], K["glow"], "ForceField",
                  rot=rot, move=move, transp=[[0, 0.1], [1, 0.1]], brightness=2.0)
    elif body == "crescent":        # a flying slash: spinning crescent shell
        shell(fx, "crescent_wide", a, t0, life, [[0, 2.5 * k], [0.2, 4.2 * k, "out"], [1, 4.6 * k]], K["mid"], "Textured", texture="slash_strip",
              rot=[90, dir_rot(d)[1], 0], spin=-900, spin_axis=[0, 0, 1], move=move, transp=[[0, 0], [1, 0.1]], brightness=1.8)
    elif body == "bolt":            # a lightning projectile: bolt segments chasing the orb
        steps = 5
        for j in range(steps):
            ta, tb_ = t0 + (t1 - t0) * j / steps, t0 + (t1 - t0) * (j + 1) / steps
            pa, pb = lerp3(a, b, j / steps), lerp3(a, b, (j + 1) / steps)
            bolt(fx, pa, pb, ta, (tb_ - ta) + 0.12, K["glow"], thickness=0.3 * k, jitter=1.0)
    trail = K["trail"] or ("fire_burst" if K["loop"] == "flame_lick" else K["loop"])
    if trail in GROUNDED:
        trail = K["loop"]
    if trail in ("frost_mist", "spray_puff"):     # shaded smoky trails
        smoke(fx, a, K, t0, count=0, tex=trail, color=K["smoke"] or "#ffffff")
        fx.d["layers"][-1].pop("emits")
        fx.d["layers"][-1].update(rate=[[t0, t1, 24]], move=move)
        fx.d["layers"][-1]["props"].update(Size=[[0, size * 0.8], [1, size * 1.6]], Lifetime=[0.35, 0.55], Speed=[0.5, 2])
    else:
        stack(fx, trail, a, K, t0, [[0, size * 0.9], [1, size * 1.3]], 0.3, rate=[[t0, t1, 16]], move=move, drag=4,
              speed=2, direction="Back", rot=dir_rot(d), transp=[[0, 0], [0.5, 0.25], [1, 1]], layers=("glow", "rim", "mid", "core"))
    sparks(fx, a, K, t0, rate=[[t0, t1, 70]], move=move, speed=(2, 7), life=(0.3, 0.6), size=(0.6, 0.15), accel=(0, -14, 0))
    if K["smoke"]:
        smoke(fx, a, K, t0, count=0)
        fx.d["layers"][-1].pop("emits")
        fx.d["layers"][-1]["rate"] = [[t0, t1, 14]]
        fx.d["layers"][-1]["move"] = move
        fx.d["layers"][-1]["props"].update(Size=[[0, size * 0.6], [1, size * 1.4]], Lifetime=[0.5, 0.8], Speed=[0.5, 2])
    fx.d["lights"].append({"at": list(a), "move": move, "color": K["light"], "range": 10, "brightness": [[t0, 3], [t1, 3], [t1 + 0.01, 0]]})


def beam_extras(fx, a, b, t0, life, K):
    """Give each element's beam its own body so beams don't all read as the same white bar."""
    st = K["beam_style"]
    n = 7
    pts = [lerp3(a, b, (j + 1) / (n + 1)) for j in range(n)]
    if st == "flame":
        for j, p in enumerate(pts):
            stack(fx, "flame_lick" if K["loop"] == "flame_lick" else "fire_burst", p, K, t0 + 0.05 + j * 0.02, [[0, 3], [1, 5]], 0.3,
                  rate=[[t0 + 0.05 + j * 0.02, t0 + life - 0.15, 8]], speed=3, direction="Top", transp=[[0, 0.1], [0.6, 0.3], [1, 1]],
                  layers=("glow", "rim", "mid", "core"))
    elif st == "bolts":
        for j in range(int(life / 0.12)):
            bolt(fx, a, b, t0 + j * 0.12, 0.14, K["glow"], thickness=0.45, jitter=2.2, segments=14)
    elif st == "ice":
        for j, p in enumerate(pts):
            g = (p[0], 0, p[2])
            shell(fx, "spike_cluster", g, t0 + 0.04 + j * 0.035, life + 0.4, [[0, [0.2, 0.05, 0.2]], [0.06, [2.6, 2.0, 2.6], "out"], [0.12, [2.2, 2.8, 2.2]], [0.85, [2.2, 2.6, 2.2]], [1, [2.0, 0.1, 2.0]]],
                  K["shell"], "Ice", rot=[0, fx.r.uniform(0, 360), 0], transp=[[0, 0.05], [0.85, 0.1], [1, 1]])
        smoke(fx, lerp3(a, b, 0.5), K, t0 + 0.1, count=10, part=[2, 2, 22], size=(3, 7), speed=(1, 3), tex="frost_mist", color="#eef8ff")
        fx.d["layers"][-1]["rot"] = dir_rot(unit([b[i] - a[i] for i in range(3)]))
    elif st == "rings":
        for j, p in enumerate(pts):
            ring(fx, p, K, t0 + 0.04 + j * 0.03, 2, 9, 0.35, facing="Front", rot=dir_rot(unit([b[i] - a[i] for i in range(3)])),
                 tex="shock_ripple" if False else None, layers=("glow", "mid", "core"))
            stack(fx, "shock_ripple", p, K, t0 + 0.06 + j * 0.03, 8, 0.45, layers=("glow", "mid"), zb=0.3)
    elif st == "slashes":
        d = unit([b[i] - a[i] for i in range(3)])
        for j in range(5):
            ta = t0 + j * life / 5
            shell(fx, "crescent_wide", a, ta, 0.32, [[0, 2.5], [1, 4.2, "out"]], K["mid"], "Textured", texture="slash_strip",
                  rot=[90, dir_rot(d)[1], fx.r.uniform(-30, 30)], spin=-900, spin_axis=[0, 0, 1], brightness=1.8,
                  move={"from": list(a), "to": list(b), "t0": ta, "t1": ta + 0.3, "ease": "linear"}, transp=[[0, 0], [1, 0.2]])
    elif st == "void":
        for j, p in enumerate(pts):
            stack(fx, "void_smoke", p, K, t0 + 0.05 + j * 0.03, [[0, 3], [1, 6]], 0.5, rate=[[t0 + 0.05 + j * 0.03, t0 + life - 0.2, 5]],
                  rotation=fx.r.randint(0, 360), rotspeed=200, transp=[[0, 0.1], [0.6, 0.3], [1, 1]])
    elif st == "water":
        d = unit([b[i] - a[i] for i in range(3)])
        shell(fx, "swirl_tight", lerp3(a, b, 0.5), t0, life, [[0, [1.2, 0.2, 1.2]], [0.12, [1.6, 12, 1.6], "out"], [1, [1.8, 12, 1.8]]], K["mid"], "Glass",
              rot=[-90 + dir_rot(d)[0], dir_rot(d)[1], 0], spin=-1200, transp=[[0, 0.2], [0.85, 0.3], [1, 1]])
        sparks(fx, a, K, t0, rate=[[t0, t0 + life - 0.1, 90]], speed=(30, 44), spread=6, direction="Front", rot=dir_rot(d),
               life=(0.45, 0.6), size=(0.8, 0.4), accel=(0, -14, 0), drag=0.5)


def charge(fx, K, t0, tr, size=4.0, back=HAND_BACK, front=HAND):
    """Anticipation: aura wisps on the caster, particles pulled inward, an orb that grows at the cocked hand,
    pinches smaller right before release, then snaps forward with the throw."""
    dur = tr - t0
    stack(fx, K["loop"], (0, 2.6, 0), K, t0, 7, dur + 0.1, locked=True, transp=[[0, 0.7], [0.4, 0.25], [0.85, 0.2], [1, 1]],
          layers=("glow", "mid", "core"))
    move = {"from": list(back), "to": list(front), "t0": tr - 0.06, "t1": tr, "ease": "out"}
    stack(fx, "orb_glow", back, K, t0, [[0, size * 0.2], [0.78, size], [0.92, size * 0.6], [1, size * 0.85]], dur + 0.02,
          move=move, locked=True, transp=[[0, 0.3], [1, 0]], zb=0.5)
    sparks(fx, back, K, t0, rate=[[t0, tr - 0.04, 55]], speed=(8, 14), part=[9, 9, 9], life=(0.3, 0.45), size=(0.6, 0.1),
           accel=(0, 0, 0), drag=0, move=move)
    fx.d["layers"][-1]["props"].update(Shape="Sphere", ShapeStyle="Surface", ShapeInOut="Inward")


# ---------------------------------------------------------------- archetypes
CAM_SIDE = {"pos": [19, 6.5, -12], "look": [0, 3, -12.5]}
CAM_WIDE = {"pos": [17, 8, -9], "look": [0, 3.5, -13]}


def a_projectile(fx, K):
    tr, th = 0.42, 0.74
    fx.d.update(duration=2.2, camera=CAM_SIDE, poster=0.8, dummies=[[0, 0, -24]])
    pose_throw(fx, tr)
    charge(fx, K, 0.0, tr, 3.5)
    element_travel(fx, HAND, (0, 3, -23), tr, th, K, size=4.5, arc=1.8)
    flash(fx, HAND, K, tr, size=5, rays=False)
    hit(fx, TARGET, K, th, 1.25)


def a_beam(fx, K):
    tr = 0.45
    fx.d.update(duration=2.4, camera=CAM_WIDE, poster=0.9, dummies=[[0, 0, -26]])
    pose_throw(fx, tr, 0.4, 0.8)
    fx.d["pose"]["armL"] = [[0, 0], [tr - 0.03, -40], [tr + 0.05, 92, "out"], [tr + 1.1, 88], [tr + 1.5, 0]]
    fx.d["pose"]["armR"] = [[0, 0], [tr - 0.03, -60], [tr + 0.05, 92, "out"], [tr + 1.1, 88], [tr + 1.5, 0]]
    fx.d["pose"]["lean"] = [[0, 0], [tr - 0.03, 14, "out"], [tr + 0.05, -14, "out"], [tr + 0.2, 6], [tr + 1.1, 4], [tr + 1.5, 0]]   # recoil
    charge(fx, K, 0.0, tr, 4.5, front=(0.2, 3.8, -2.2))
    src, end = (0.2, 3.8, -2.2), (0, 2.5, -26)
    plain = K["beam_style"] in (None, "void", "rings")
    beam(fx, src, end, tr, 1.1, K, width=(3.2, 2.6) if plain else (2.0, 1.6), reach=[[0, 0], [0.12, 1, "out"]], layers=K["beam_style"] != "slashes")
    beam_extras(fx, src, end, tr, 1.1, K)
    flash(fx, src, K, tr, size=7, rays=False)
    stack(fx, "orb_glow", src, K, tr, [[0, 3], [0.1, 7, "out"], [0.9, 6], [1, 0]], 1.1, transp=[[0, 0], [0.9, 0], [1, 1]], zb=0.6)
    for k in range(5):
        hit(fx, (0, 0, -26), K, tr + 0.12 + k * 0.18, 0.45, dmg=int(fx.r.uniform(18, 30)), stop=0.04, ground=k == 0)
    hit(fx, (0, 0, -26), K, tr + 1.05, 1.0)
    shake(fx, tr, 0.25, 1.0, 30)


def a_slam(fx, K):
    th = 0.5
    at = (0, 0, -6.5)
    fx.d.update(duration=2.4, camera={"pos": [16, 8, 7], "look": [0, 2.5, -6]}, poster=th + 0.1, dummies=[[3.5, 0, -11]])
    pose(fx,
         offset=[[0, [0, 0, 0]], [0.14, [0, -0.35, 0]], [0.34, [0, 5, -3], "out"], [th, [0, 0, -5], "in"], [th + 0.5, [0, 0, -5]]],
         scale=[[0, [1, 1, 1]], [0.14, [1.15, 0.8, 1.15], "out"], [0.22, [0.9, 1.15, 0.9]], [th - 0.01, [0.9, 1.12, 0.9]], [th + 0.05, [1.3, 0.7, 1.3], "out"], [th + 0.17, [0.95, 1.08, 0.95]], [th + 0.35, [1, 1, 1]]],
         armR=[[0, 0], [0.14, 20], [0.34, -170, "out"], [th, 40, "in"], [th + 0.6, 10]], armL=[[0, 0], [0.14, 20], [0.34, -170, "out"], [th, 40, "in"], [th + 0.6, 10]],
         lean=[[0, 0], [0.14, -18], [0.34, 12, "out"], [th, -38, "in"], [th + 0.2, -30], [th + 0.8, 0]])
    charge(fx, K, 0.0, 0.3, 3, back=(0, 9, -2), front=(0, 7.5, -3.5))
    impact(fx, th, "white", 0.04)
    hit(fx, at, K, th, 1.25, direction=(0.6, 0, -0.8), stop=0.11)
    crater(fx, at, th, radius=7.5, count=16, size=3.2)
    ring(fx, add(at, (0, 0.4, 0)), K, th + 0.08, 3, 34, 0.6)
    shake(fx, th, 1.0, 0.6)


def a_eruption(fx, K):
    te = 0.5
    at = (0, 0, -18)
    fx.d.update(duration=2.6, camera=CAM_WIDE, poster=te + 0.25, dummies=[[0, 0, -18]])
    pose(fx, armR=[[0, 0], [0.2, -30], [te - 0.05, 150, "out"], [te + 0.7, 140], [te + 1.2, 0]], lean=[[0, 0], [0.2, 8], [te - 0.05, -10, "out"], [te + 1, 0]],
         scale=[[0, [1, 1, 1]], [0.25, [1.06, 0.92, 1.06]], [te - 0.05, [0.95, 1.08, 0.95], "out"], [te + 0.3, [1, 1, 1]]])
    ground_mark(fx, at, K, 0.0, 10, 0.6)
    stack(fx, "orb_glow", add(at, (0, 0.5, 0)), K, 0.0, [[0, 2], [0.8, 7], [0.95, 4.5], [1, 6]], te, speed=0.01, orient="VelocityPerpendicular",
          transp=[[0, 0.5], [1, 0]], layers=("glow", "mid", "core"))
    sparks(fx, add(at, (0, 0.5, 0)), K, 0.05, rate=[[0.05, te, 40]], part=[8, 0.5, 8], speed=(1, 3), life=(0.3, 0.5), accel=(0, 8, 0))
    shell(fx, "cone_tube", add(at, (0, 9, 0)), te, 0.9, [[0, [2.5, 0.3, 2.5]], [0.1, [5, 6, 5], "out"], [0.25, [4, 10, 4]], [1, [5.5, 10.5, 5.5]]], K["shell"],
          "ForceField", texture="energy_strip", scroll=[0.8, -2.5], transp=[[0, 0], [0.6, 0.2], [1, 1]], brightness=2.2, tile=[2, 1])
    col = K["column"] or K["loop"]
    for k in range(5):
        stack(fx, col, add(at, (fx.r.uniform(-1.5, 1.5), 4 + k * 2.6, fx.r.uniform(-1.5, 1.5))), K, te + k * 0.035, [[0, 7], [1, 11]], 0.8,
              transp=[[0, 0], [0.7, 0.15], [1, 1]], squash=[[0, 0.6], [0.3, -0.1], [0.6, 0]])
    sparks(fx, add(at, (0, 1, 0)), K, te, count=40, speed=(42, 72), spread=18, size=(1.0, 0.3), accel=(0, -45, 0), drag=0.8)
    hit(fx, at, K, te, 1.15, direction=(0, 1, 0), stop=0.1)
    fling(fx, at, te, count=12, speed=44, size=1.6)


def a_slash(fx, K):
    fx.d.update(duration=2.0, camera={"pos": [10, 7, 9], "look": [0, 3, -5]}, poster=0.5, dummies=[[0, 0, -9]])
    times = [0.18, 0.42, 0.68]
    pose(fx,
         twist=[[0, 0], [0.12, 45, "out"], [0.2, -50, "out"], [0.36, -55], [0.44, 50, "out"], [0.62, 40], [0.7, -30, "out"], [1.1, 0]],
         armR=[[0, 0], [0.12, -60], [0.2, 100, "out"], [0.36, 110], [0.44, -20, "out"], [0.62, -150], [0.7, 80, "in"], [1.2, 0]],
         lean=[[0, 0], [0.12, 8], [0.2, -15, "out"], [0.44, -12], [0.62, 10], [0.7, -28, "in"], [0.95, -18], [1.3, 0]],
         offset=[[0, [0, 0, 0]], [0.2, [0, 0, -0.8], "out"], [0.44, [0, 0, -1.6], "out"], [0.7, [0, 0, -2.6], "out"], [1.1, [0, 0, -2.4]]])
    cols = dict(K, mid=K["mid"] if isinstance(K["mid"], str) else K["mid"][1][1])
    for k, (t, ang, tilt) in enumerate(zip(times, (0, 180, 90), (20, -25, 70))):
        c = (0, 3.2, -4.8 - k * 0.8)
        shell(fx, "crescent_wide", c, t - 0.04, 0.34, [[0, [4.0, 4.0, 4.0]], [0.25, [6.4, 5.2, 6.4], "out"], [1, [6.8, 5.6, 6.8]]], cols["mid"], "Textured",
              texture="slash_strip", rot=[tilt, ang, 0], spin=[[0, 0], [1, -150, "out"]], transp=[[0, 0], [0.5, 0.1], [1, 1]], brightness=1.8)
        shell(fx, "crescent_thin", c, t - 0.04, 0.3, [[0, 4.4], [1, 7.0, "out"]], "#ffffff", "Neon", rot=[tilt, ang, 0],
              spin=[[0, 0], [1, -160, "out"]], transp=[[0, 0.1], [1, 1]], brightness=1.4)
        stack(fx, "slash", c, cols, t - 0.04, 13, 0.32, rotation=ang + tilt, zb=0.4)
        last = k == len(times) - 1
        hit(fx, (0, 0, -9), K, t, 1.0 if last else 0.55, direction=(0, 0, -1), stop=0.1 if last else 0.06, ground=last)
    if K["main"] == "blade_cuts":
        stack(fx, "blade_cuts", (0, 3.5, -9), K, times[-1] + 0.05, 14, 0.6, rotation=fx.r.randint(0, 90), zb=0.7)


def a_dash(fx, K):
    t0, t1 = 0.22, 0.36
    fx.d.update(duration=2.0, camera={"pos": [18, 6, -10], "look": [0, 3, -12]}, poster=t1 + 0.08, dummies=[[0, 0, -25]])
    pose(fx,
         offset=[[0, [0, 0, 0]], [t0 - 0.02, [0, -0.3, 0.4]], [t1, [0, 0, -21.6], "out"], [t1 + 0.12, [0, 0, -21.1]], [t1 + 0.4, [0, 0, -21]]],
         lean=[[0, 0], [t0 - 0.02, -30, "out"], [t1, -35], [t1 + 0.08, 14, "out"], [t1 + 0.35, -4], [t1 + 0.7, 0]],
         scale=[[0, [1, 1, 1]], [t0 - 0.02, [1.12, 0.84, 1.12], "out"], [t0 + 0.04, [0.85, 1.2, 0.85]], [t1, [0.9, 1.1, 0.9]], [t1 + 0.06, [1.15, 0.85, 1.15]], [t1 + 0.3, [1, 1, 1]]],
         armR=[[0, 0], [t0, 40], [t1, 60], [t1 + 0.08, 100, "out"], [t1 + 0.6, 0]])
    charge(fx, K, 0.0, t0, 2.5, back=(0.8, 2.6, 0.6), front=(0.8, 2.6, -0.6))
    a, b = (0, 3, -1), (0, 3, -22)
    move = {"from": list(a), "to": list(b), "t0": t0, "t1": t1, "ease": "out"}
    # afterimages left along the path (they fade and drift back: follow-through)
    for j in range(5):
        k = (j + 1) / 6
        e = 1 - (1 - k) ** 2
        fx.d.setdefault("ghosts", []).append({"t": round(t0 + (t1 - t0) * k, 3), "at": [0, 0, round(-21 * e, 2)], "color": K["glow"], "life": 0.4, "lean": -32})
    sparks(fx, a, K, t0, rate=[[t0, t1, 200]], move=move, speed=(0.5, 2), life=(0.3, 0.5), size=(2.0, 0.2),
           accel=(0, 0, 0), drag=0, tex="flecks", orient="VelocityParallel")
    trail = K["trail"] or K["loop"]
    if trail in ("frost_mist", "spray_puff"):
        smoke(fx, a, K, t0, count=0, tex=trail, color=K["smoke"] or "#ffffff")
        fx.d["layers"][-1].pop("emits")
        fx.d["layers"][-1].update(rate=[[t0, t1, 60]], move=move)
        fx.d["layers"][-1]["props"].update(Size=[[0, 3], [1, 6]], Lifetime=[0.4, 0.7], Speed=[0.5, 2])
    else:
        stack(fx, trail, a, K, t0, [[0, 3.5], [1, 5]], 0.35, rate=[[t0, t1, 70]], move=move, drag=3, transp=[[0, 0.05], [0.6, 0.3], [1, 1]])
    fx.d["layers"].append({"type": "beam", "from": list(a), "to": list(b), "t0": t0, "life": 0.6, "texture": "wind_strip", "color": K["mid"] if isinstance(K["mid"], str) else K["mid"][1][1],
                           "width": [[0, [0, 0]], [0.3, [5, 5], "out"], [1, [0, 0]]], "lightEmission": 0.6, "textureSpeed": -60, "textureLength": 14})
    dust(fx, (0, 0, -1), t0, size=(4, 9))
    hit(fx, (0, 0, -25), K, t1 + 0.02, 0.85, stop=0.09)


def a_barrage(fx, K):
    fx.d.update(duration=2.6, camera=CAM_WIDE, poster=1.0, dummies=[[0, 0, -24]])
    charge(fx, K, 0.0, 0.28, 3)
    armR, armL = [[0, 0], [0.24, -40]], [[0, 0], [0.24, -40]]
    for k in range(7):
        t0 = 0.28 + k * 0.17
        right = k % 2 == 0
        (armR if right else armL).extend([[t0 - 0.05, -30], [t0 + 0.03, 95, "out"], [t0 + 0.12, 40]])
        src = add(HAND if right else (-1.5, 3.8, -2.3), (0, fx.r.uniform(-0.3, 0.6), 0))
        dst = (fx.r.uniform(-3, 3), fx.r.uniform(1.5, 4), -23 + fx.r.uniform(-1.5, 1.5))
        element_travel(fx, src, dst, t0, t0 + 0.24, K, size=2.4, arc=fx.r.uniform(1.0, 3.0) * (1 if right else -0.6))
        hit(fx, (dst[0], 0, dst[2]), K, t0 + 0.24, 0.45, dmg=int(fx.r.uniform(14, 32)), stop=0.035, ground=False)
    armR.append([1.7, 0]); armL.append([1.7, 0])
    armR.sort(key=lambda kf: kf[0]); armL.sort(key=lambda kf: kf[0])
    pose(fx, armR=armR, armL=armL, lean=[[0, 0], [0.24, 10], [0.32, -12, "out"], [1.45, -10], [1.9, 0]])
    hit(fx, TARGET, K, 1.55, 0.95, stop=0.09)


def a_aura(fx, K):
    tb = 0.62
    fx.d.update(duration=2.8, camera={"pos": [9, 6, 11], "look": [0, 3.5, 0]}, poster=tb + 0.35)
    pose(fx,   # crouch and fold in (anticipation), explode open, hold, settle
         scale=[[0, [1, 1, 1]], [tb - 0.05, [1.12, 0.82, 1.12], "out"], [tb + 0.06, [0.9, 1.15, 0.9], "out"], [tb + 0.3, [1, 1, 1]]],
         armRz=[[0, 0], [tb - 0.05, -20], [tb + 0.06, 115, "out"], [tb + 1.5, 105], [tb + 2.0, 0]],
         armLz=[[0, 0], [tb - 0.05, 20], [tb + 0.06, -115, "out"], [tb + 1.5, -105], [tb + 2.0, 0]],
         lean=[[0, 0], [tb - 0.05, -18], [tb + 0.06, 12, "out"], [tb + 1.6, 6], [tb + 2.0, 0]])
    charge(fx, K, 0.0, tb, 4, back=(0, 3.4, -0.8), front=(0, 3.4, -0.8))
    for k in range(4):
        a = k * 90
        stack(fx, K["loop"], (math.cos(math.radians(a)) * 1.2, 3, math.sin(math.radians(a)) * 1.2), K, tb - 0.05, [[0, 5], [0.1, 9], [1, 8]], 2.1,
              locked=True, transp=[[0, 1], [0.08, 0.15], [0.85, 0.2], [1, 1]], layers=("glow", "rim", "mid", "core"), fps=20 + k * 3)
    sparks(fx, (0, 2, 0), K, tb, rate=[[tb, 2.4, 30]], part=[4, 1, 4], speed=(4, 9), life=(0.6, 1.0), size=(0.5, 0.1), accel=(0, 6, 0), spread=10)
    shell(fx, "tube", (0, 6, 0), tb, 0.8, [[0, [2.4, 0.6, 2.4]], [0.12, [3.4, 3, 3.4], "out"], [0.3, [3, 5, 3]], [1, [4.5, 6, 4.5]]], K["shell"], "ForceField",
          texture="energy_strip", scroll=[0, -3], transp=[[0, 0.15], [0.5, 0.45], [1, 1]], brightness=1.6, tile=[2, 1])
    ring(fx, (0, 0.4, 0), K, tb, 2, 30, 0.6)
    ring(fx, (0, 0.4, 0), K, tb + 0.15, 2, 22, 0.5, layers=("mid", "core"))
    stack(fx, K["burst2"] or K["main"] if (K["burst2"] or K["main"]) not in GROUNDED else "star_flash", (0, 3.2, 0), K, tb, [[0, 8], [1, 14]], 0.6,
          squash=SQUASH_HIT, zb=0.7, layers=("glow", "mid", "core"))
    flash(fx, (0, 3, 0), K, tb, size=11)
    light(fx, (0, 4, 0), tb, K["light"], peak=6, rng_=22, life=1.8)
    dust(fx, (0, 0, 0), tb, size=(6, 14))
    shake(fx, tb, 0.7, 0.5)
    fx.d.setdefault("hitstop", []).append({"t": tb, "dur": 0.08})
    grade(fx, [[0, 0, 0, 0, "#ffffff"], [tb - 0.05, -0.04, 0.1, -0.15, "#ffffff"], [tb + 0.02, 0.03, 0.18, 0.15, K["grade"]], [2.4, 0.01, 0.06, 0.06, K["grade"]], [2.8, 0, 0, 0, "#ffffff"]])
    if "invert" in K["extra"]:
        impact(fx, tb, "invert", 0.06)
    if "bolts" in K["extra"]:
        for k in range(8):
            a = fx.r.uniform(0, math.tau)
            bolt(fx, (0, 3, 0), (math.cos(a) * 6, fx.r.uniform(0, 7), math.sin(a) * 6), tb + 0.05 + k * 0.18, 0.18, K["glow"], thickness=0.25)
    if "spikes" in K["extra"]:
        element_impact(fx, (0, 0, 0), K, tb, 0.6)


def a_vortex(fx, K):
    at = (0, 0, -16)
    tb = 2.05
    fx.d.update(duration=3.0, camera=CAM_WIDE, poster=1.2, dummies=[[0, 0, -16]])
    pose(fx, armR=[[0, 0], [0.18, -40], [0.3, 150, "out"], [tb - 0.1, 140], [tb, 100, "out"], [tb + 0.6, 0]],
         lean=[[0, 0], [0.18, 8], [0.3, -8, "out"], [tb - 0.1, -6], [tb, -16, "out"], [tb + 0.6, 0]])
    shell(fx, "swirl", add(at, (0, 5, 0)), 0.25, tb - 0.2, [[0, [2, 1, 2]], [0.15, [7, 6.5, 7], "out"], [0.25, [6.5, 6, 6.5]], [0.9, [7, 6, 7]], [1, [3, 8, 3], "in"]],
          K["shell"], "ForceField", texture="wind_strip", spin=-720, scroll=[1.2, 0], transp=[[0, 0.3], [0.15, 0.05], [0.9, 0.1], [1, 0.6]], brightness=2.4)
    shell(fx, "swirl_tight", add(at, (0, 5, 0)), 0.3, tb - 0.25, [[0, [1, 3, 1]], [0.2, [4.5, 5, 4.5], "out"], [1, [2, 6, 2], "in"]], K["glow"],
          "ForceField", spin=-1000, transp=[[0, 0.2], [0.85, 0.1], [1, 0.5]], brightness=1.6)
    # the core contracts before the final burst (anticipation inside the move)
    stack(fx, "orb_glow", add(at, (0, 3, 0)), K, 0.3, [[0, 2], [0.2, 6], [0.85, 6], [1, 2.5]], tb - 0.28, transp=[[0, 0.2], [0.95, 0], [1, 1]], zb=0.5)
    sparks(fx, add(at, (0, 3, 0)), K, 0.3, rate=[[0.3, tb - 0.1, 60]], part=[16, 6, 16], speed=(10, 16), life=(0.5, 0.8), size=(0.7, 0.1), accel=(0, 4, 0), drag=0)
    fx.d["layers"][-1]["props"].update(Shape="Cylinder", ShapeStyle="Surface", ShapeInOut="Inward")
    smoke(fx, add(at, (0, 1, 0)), K, 0.35, count=10, size=(6, 10), speed=(1, 3), life=(1.2, 1.6))
    ring(fx, add(at, (0, 0.3, 0)), K, 0.3, 18, 4, tb - 0.3, transp=[[0, 1], [0.2, 0.4], [0.9, 0.3], [1, 1]], layers=("glow", "mid"))
    for k in range(4):
        hit(fx, at, K, 0.6 + k * 0.33, 0.35, dmg=int(fx.r.uniform(10, 20)), stop=0.03, ground=False)
    hit(fx, at, K, tb, 1.25, direction=(0, 0.3, -1), stop=0.12)


def a_finisher(fx, K):
    tr, th = 1.2, 1.52
    fx.d.update(duration=3.6, poster=th + 0.08, dummies=[[0, 0, -26]])
    fx.d["camera"] = {"pos": [[0, [6, 4, 7]], [0.32, [7, 5, 9]], [0.38, [24, 13, 4], "out"], [1, [26, 14, 2]]],
                      "look": [[0, [0, 3.5, -1]], [0.32, [0, 3.5, -2]], [0.38, [0, 4, -14], "out"], [1, [0, 4, -16]]],
                      "fov": [[0, 55], [0.34, 48], [0.4, 68, "out"], [1, 62]]}
    pose_throw(fx, tr, 1.0, 1.4)
    charge(fx, K, 0.0, tr, 3.6)
    stack(fx, K["loop"], (0, 3, 0), K, 0.0, 9, tr, locked=True, transp=[[0, 0.8], [0.4, 0.2], [1, 0.4]], layers=("glow", "mid", "core"))
    grade(fx, [[0, 0, 0, 0, "#ffffff"], [0.2, -0.08, 0.2, -0.3, K["grade"]], [tr - 0.05, -0.14, 0.3, -0.45, K["grade"]], [tr + 0.1, 0.05, 0.3, 0.25, K["grade"]], [3.2, 0, 0.05, 0.05, "#ffffff"], [3.6, 0, 0, 0, "#ffffff"]])
    impact(fx, tr - 0.05, "invert", 0.06)
    impact(fx, tr + 0.01, "mono", 0.05)
    fx.d.setdefault("hitstop", []).append({"t": tr - 0.05, "dur": 0.12})
    end = (0, 3.5, -24)
    move = {"from": list(HAND), "to": list(end), "t0": tr, "t1": th, "ease": "in", "arc": 1.5}
    if K["hero"]:
        stack(fx, K["hero"], HAND, K, tr, [[0, 9], [0.3, 15], [1, 16]], th - tr + 0.03, move=move, locked=True, transp=[[0, 0], [0.85, 0], [1, 1]],
              speed=0.05, direction="Front", rot=dir_rot((0, 0, -1)), squash=[[0, 0.6], [0.5, 0.3], [1, 0.2]], zb=0.6)
    else:
        element_travel(fx, HAND, end, tr, th, K, size=9)
    if K["hero_mesh"]:
        hm = K["hero_mesh"]
        rot = {"giant_fist": [0, 180, 0], "dragon_head": [0, 90, 0], "phoenix_bird": [0, 180, 0]}[hm]
        shell(fx, hm, HAND, tr, th - tr + 0.05, [[0, [2, 2, 3]], [0.3, [6, 6, 9], "out"], [1, [7, 7, 10]]], K["shell"], "ForceField", rot=rot,
              move=move, transp=[[0, 0], [0.85, 0.1], [1, 1]], brightness=1.8)
    trail = "fire_burst" if K["loop"] == "flame_lick" else K["loop"]
    stack(fx, trail, HAND, K, tr, [[0, 7], [1, 11]], 0.5, rate=[[tr, th, 40]], move=move, drag=3, transp=[[0, 0], [0.5, 0.3], [1, 1]])
    beam(fx, HAND, end, tr, 0.55, K, width=(6, 5), reach=[[0, 0], [0.55, 1, "in"]])
    hit(fx, (0, 0, -24), K, th, 2.0, stop=0.16)
    crater(fx, (0, 0, -24), th, radius=12, count=20, size=4.2)
    ring(fx, (0, 0.5, -24), K, th + 0.08, 4, 60, 0.9)
    shell(fx, "dome", (0, 0, -24), th, 0.9, [[0, [3, 0.8, 3]], [0.2, [14, 11, 14], "outExpo"], [1, [19, 15, 19]]], K["shell"], "ForceField",
          transp=[[0, 0.35], [0.5, 0.55], [1, 1]], brightness=0.85)
    shake(fx, th, 1.6, 1.0, 18)



ARCHETYPES = [("projectile", a_projectile), ("beam", a_beam), ("slam", a_slam), ("eruption", a_eruption), ("slash", a_slash),
              ("dash", a_dash), ("barrage", a_barrage), ("aura", a_aura), ("vortex", a_vortex), ("finisher", a_finisher)]

NAMES = {
    "Flame": ["Fire Fist", "Flame Lance", "Blazing Slam", "Pyre Eruption", "Ember Crescent", "Blaze Step", "Ember Barrage", "Inferno Aura", "Fire Cyclone", "Dragon's Roar"],
    "Magma": ["Magma Fist", "Lava Stream", "Volcanic Slam", "Meteor Geyser", "Molten Crescent", "Lava Rush", "Meteor Shower", "Magma Mantle", "Lava Maelstrom", "Great Eruption"],
    "Light": ["Light Spear", "Radiant Ray", "Solar Slam", "Pillar of Dawn", "Prism Crescent", "Light Speed", "Starfall Barrage", "Divine Aura", "Halo Vortex", "Heaven's Palm"],
    "Quake": ["Tremor Shot", "Seismic Ray", "Tectonic Slam", "Fault Eruption", "Shatter Crescent", "Quake Step", "Aftershock Barrage", "Tremor Aura", "Shockwave Maelstrom", "World Shatter"],
    "Ice": ["Frost Shard", "Glacial Ray", "Permafrost Slam", "Glacier Eruption", "Frost Crescent", "Ice Glide", "Hailstorm", "Frozen Aura", "Blizzard Vortex", "Absolute Zero"],
    "Dark": ["Void Orb", "Abyss Ray", "Black Hole Slam", "Shadow Geyser", "Void Crescent", "Shadow Step", "Umbral Barrage", "Abyssal Aura", "Black Vortex", "Eclipse"],
    "Thunder": ["Thunder Bolt", "Storm Ray", "Thunderclap Slam", "Lightning Pillar", "Volt Crescent", "Flash Step", "Thunder Barrage", "Storm Aura", "Tempest Vortex", "Thunder Dragon"],
    "Haki": ["Armament Shot", "Conqueror Ray", "Haki Slam", "Crimson Eruption", "Crimson Crescent", "Haki Rush", "Haki Barrage", "Conqueror's Aura", "Crimson Vortex", "Supreme Fist"],
    "Blade": ["Air Slash", "Sky Cutter", "Crescent Slam", "Blade Storm Pillar", "Triple Crescent", "Iai Dash", "Thousand Cuts", "Blade Aura", "Cyclone Blades", "Phoenix Slash"],
    "Water": ["Water Bullet", "Torrent Ray", "Tidal Slam", "Geyser", "Wave Crescent", "Riptide Dash", "Rain Barrage", "Tide Aura", "Whirlpool", "Shark Tsunami"],
}


def build_all(only=None):
    out = []
    for ei, (el, K) in enumerate(KITS.items()):
        if only and el not in only:
            continue
        for ai, (arch, fn) in enumerate(ARCHETYPES):
            title = NAMES[el][ai]
            name = f"{ei:02d}{ai}_" + "".join(w.capitalize() for w in title.replace("'", "").split())
            fx = FX(name, title, el, arch, 2.0, seed=ei * 100 + ai)
            fn(fx, K)
            fx.d["layers"] = [L for L in fx.d["layers"] if L]
            out.append(fx.d)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--only", default="")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    only = set(a.only.split(",")) if a.only else None
    fxs = build_all(only)
    for fx in fxs:
        if a.list:
            print(fx["name"], fx["title"], len(fx["layers"]))
            continue
        json.dump(fx, open(os.path.join(a.out, fx["name"] + ".json"), "w"), separators=(",", ":"))
    if not a.list:
        print(f"wrote {len(fxs)} effects to {os.path.abspath(a.out)}")


if __name__ == "__main__":
    main()
