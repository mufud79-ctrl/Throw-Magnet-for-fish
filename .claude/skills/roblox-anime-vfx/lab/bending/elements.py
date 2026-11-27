"""Element looks for the bending game: palettes + per-element defaults on top of the Dragon kit's plumbing.

    sys.path.insert(0, <lab>/bending); from elements import element_kit
    K = element_kit("water")          # K.pal, K.haze(...), K.needles(...), K.ink(...), K.crater(...), K.write(...)

Every look follows the Dragon layer conventions (glow / rim / mid / core) and the lessons in DRAGON_MOVES_NOTES.md:
a DARK accent for the value test on sand, a thin white core only, a smooth coloured haze for the outside effect.
Palette keys:
  HOT / COOL     per-layer colours (fresh -> cooling), same roles as the fire palette
  spark          colour sequence for embers / needles / small bright bits
  light          PointLight colour
  haze, deep     the outside haze (aura_haze col / deep)
  ink            the dark accent (ink shards, outlines)
  smoke          the dark-anchor haze colour sequence (dark_haze)
  dust, slab     ground dust / crater slab colours
  hot_core       crater hot-core colour sequence (None = no hot core)
  tint           world grade tint while the move plays (keep near white: abilities never darken the world)
  needle_le      LightEmission of needles (opaque matter like rock or blood uses low values)
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dragon"))
import kit  # noqa: E402


def _pal(glow, rim, mid, core, cool_to, spark, light, **look):
    """HOT is the fresh look; COOL drifts every layer toward `cool_to` (where the element settles as it dies)."""
    hot = {"glow": glow, "rim": rim, "mid": mid, "core": core}
    cool = {k: [[0, v], [0.6, v], [1, cool_to.get(k, v)]] for k, v in hot.items()}
    return dict({"HOT": hot, "COOL": cool, "spark": spark, "light": light}, **look)


LOOKS = {
    # ---- WATER family (blue body, white foam core, deep navy accent; cool mist haze)
    "water": _pal("#4fc3ff", "#0b3a8a", "#8fdcff", "#ffffff", {"glow": "#2a7fd0", "mid": "#4fa8e8", "core": "#cfeeff"},
                  [[0, "#ffffff"], [0.4, "#bfeaff"], [1, "#4fa8e8"]], "#8fd0ff",
                  haze="#6cbcf0", deep="#2a70c8", ink="#061a3a", smoke=[[0, "#b8d8ee"], [1, "#dceaf4"]], dust="#e8f2f8",
                  slab="#b8a888", hot_core=None, tint="#eef6ff", needle_le=0.8),
    "ice": _pal("#9fe6ff", "#1a4f9a", "#e6faff", "#ffffff", {"glow": "#6ab8e8", "mid": "#bfe6f8"},
                [[0, "#ffffff"], [0.5, "#dff6ff"], [1, "#8fd0f0"]], "#bfe8ff",
                haze="#9cd8f4", deep="#5aa8e0", ink="#0a2448", smoke=[[0, "#dceef8"], [1, "#f2f8fc"]], dust="#f0f8ff",
                slab="#d8eef8", hot_core=[[0, "#ffffff"], [0.3, "#cfefff"], [1, "#6ab8e8"]], tint="#f0f8ff", needle_le=0.7),
    "healing": _pal("#7fe8ff", "#1a6aa8", "#c8f6ff", "#ffffff", {"glow": "#4ab8e0"},
                    [[0, "#ffffff"], [0.4, "#c8f6ff"], [1, "#7fe8ff"]], "#9ff0ff",
                    haze="#7ce0f8", deep="#3ab0e0", ink="#0a2a48", smoke=[[0, "#d8f4fc"], [1, "#eefaff"]], dust="#eefaff",
                    slab="#b8a888", hot_core=None, tint="#f2fbff", needle_le=1),
    "plant": _pal("#7ed05a", "#1e4a14", "#b8f07a", "#f4ffd8", {"glow": "#4a8a2a", "mid": "#6aa83a"},
                  [[0, "#f4ffd8"], [0.4, "#b8f07a"], [1, "#4a8a2a"]], "#a8e07a",
                  haze="#b8e8a0", deep="#5aa83a", ink="#0e2008", smoke=[[0, "#5a6a3a"], [1, "#8a9a6a"]], dust="#a8b888",
                  slab="#6a5a3a", hot_core=None, tint="#f6fff0", needle_le=0.5),
    "blood": _pal("#d02a3a", "#2a0408", "#ff5a6a", "#ffd8dc", {"glow": "#7a0a14", "mid": "#a01a28"},
                  [[0, "#ffd8dc"], [0.4, "#ff5a6a"], [1, "#7a0a14"]], "#c0283a",
                  haze="#c04050", deep="#6a0a18", ink="#120204", smoke=[[0, "#2a0a10"], [1, "#4a1a20"]], dust="#c8b0a8",
                  slab="#9a8070", hot_core=None, tint="#fff0f0", needle_le=0.6),
    "spirit": _pal("#7ad8ff", "#2a2a8a", "#c8f0ff", "#ffffff", {"glow": "#6a7ae8", "mid": "#a0c0ff"},
                   [[0, "#ffffff"], [0.4, "#c8f0ff"], [1, "#8a8aff"]], "#a8d8ff",
                   haze="#a8c8ff", deep="#6a6ae0", ink="#0a0a30", smoke=[[0, "#3a3a6a"], [1, "#6a6aa0"]], dust="#e0e8ff",
                   slab="#a8a8c8", hot_core=None, tint="#f2f4ff", needle_le=1),
    # ---- EARTH family (opaque matter: low emission, a lit top / dark underside; dust haze)
    "earth": _pal("#c8a878", "#3a2a1a", "#a88a5a", "#e8d8b8", {"glow": "#8a6a48", "mid": "#7a5a3a"},
                  [[0, "#e8d8b8"], [0.5, "#b89a70"], [1, "#6a5038"]], "#e0c89a",
                  haze="#c8b088", deep="#987858", ink="#1a1208", smoke=[[0, "#8a7a62"], [1, "#b8a888"]], dust="#cdb48a",
                  slab="#a8906a", hot_core=None, tint="#fffaf0", needle_le=0.1),
    "metal": _pal("#b8c4cc", "#1e2428", "#dfe6ea", "#ffffff", {"glow": "#7a868e", "mid": "#a0aab0"},
                  [[0, "#ffffff"], [0.3, "#ffe08a"], [1, "#ff9a3a"]], "#e0e8f0",
                  haze="#c8d0d8", deep="#8a96a0", ink="#0a0e10", smoke=[[0, "#5a6068"], [1, "#8a9098"]], dust="#c8c0b0",
                  slab="#8a9098", hot_core=None, tint="#f6f8fa", needle_le=0.6),
    "lava": dict(kit.PALS["fire"], haze="#ff8a3a", deep="#c8281a", ink="#1a0604", smoke=[[0, "#3a2420"], [1, "#5a4038"]],
                 dust="#8a7060", slab="#3a2a24", hot_core=[[0, "#fff6b0"], [0.15, "#ffb02a"], [0.5, "#e0401a"], [1, "#3a0a08"]],
                 tint="#fff2e6", needle_le=1),
    "sand": _pal("#e8d0a0", "#7a5a30", "#f4e4c0", "#fffaf0", {"glow": "#c8a870", "mid": "#d8b880"},
                 [[0, "#fffaf0"], [0.5, "#f0dcb0"], [1, "#c8a870"]], "#f0dcb0",
                 haze="#e0c898", deep="#b89060", ink="#2a1a08", smoke=[[0, "#c8b090"], [1, "#e0d0b0"]], dust="#e8d6b0",
                 slab="#d8c098", hot_core=None, tint="#fffaf0", needle_le=0.2),
    "seismic": _pal("#f0f4ff", "#3a4a6a", "#ffffff", "#ffffff", {"glow": "#a8b8e0"},
                    [[0, "#ffffff"], [1, "#c8d4f0"]], "#e0e8ff",
                    haze="#b8c4e8", deep="#8090c0", ink="#0a1020", smoke=[[0, "#8a8a9a"], [1, "#b0b0c0"]], dust="#cdb48a",
                    slab="#a8906a", hot_core=None, tint="#f8faff", needle_le=0.8),
    # ---- FIRE family (the Dragon fire is the base; lightning is the cold-blooded white-blue)
    "fire": dict(kit.PALS["fire"], haze="#ff9a3a", deep="#ff5a1e", ink="#1a0806", smoke=[[0, "#4a2a22"], [1, "#6a4a3e"]],
                 dust="#cdb48a", slab="#c9ad80", hot_core=[[0, "#fff6b0"], [0.15, "#ffb02a"], [0.5, "#e0401a"], [1, "#6a100a"]],
                 tint="#fff1e2", needle_le=1),
    "lightning": _pal("#6fc8ff", "#1a1a7a", "#c8ecff", "#ffffff", {"glow": "#3a6ae0", "mid": "#8ab8ff"},
                      [[0, "#ffffff"], [0.3, "#c8ecff"], [1, "#4a7aff"]], "#9fd0ff",
                      haze="#a8c8ff", deep="#4a6ae0", ink="#060a28", smoke=[[0, "#2a3050"], [1, "#4a5070"]], dust="#cdb48a",
                      slab="#a8906a", hot_core=[[0, "#ffffff"], [0.2, "#c8ecff"], [1, "#2a3a8a"]], tint="#f2f6ff", needle_le=1),
    "combustion": dict(kit.PALS["fire"], haze="#ffb04a", deep="#ff6a1e", ink="#1a0806", smoke=[[0, "#3a2420"], [1, "#5a4038"]],
                       dust="#cdb48a", slab="#c9ad80", hot_core=[[0, "#ffffff"], [0.1, "#fff6b0"], [0.4, "#ff8a14"], [1, "#6a100a"]],
                       tint="#fff4e6", needle_le=1),
    "dragonfire": _pal("#ff5aa0", "#5a1a8a", "#ffd24a", "#ffffff", {"glow": "#3ad0ff", "mid": "#7aff8a"},
                       [[0, "#ffffff"], [0.2, "#ffd24a"], [0.45, "#ff5aa0"], [0.7, "#7a8aff"], [1, "#3ad0ff"]], "#ffb0e0",
                       haze="#ffb0d8", deep="#a07aff", ink="#1a0a2a", smoke=[[0, "#4a2a4a"], [1, "#6a4a6a"]], dust="#cdb48a",
                       slab="#c9ad80", hot_core=None, tint="#fff4fa", needle_le=1),
    # ---- AIR family (mostly invisible: white/pale streaks, swirl lines, kicked-up dust; a soft grey-blue accent)
    "air": _pal("#e8f4ff", "#5a7a9a", "#ffffff", "#ffffff", {"glow": "#b8d0e8"},
                [[0, "#ffffff"], [1, "#d8e8f8"]], "#f0f8ff",
                haze="#c8dcee", deep="#98b4d0", ink="#1a2a3a", smoke=[[0, "#c8d4e0"], [1, "#e4ecf4"]], dust="#e0d0b0",
                slab="#c8b48a", hot_core=None, tint="#f8fbff", needle_le=0.6),
    "flight": _pal("#f4faff", "#6a8ab0", "#ffffff", "#ffffff", {"glow": "#c8dcf0"},
                   [[0, "#ffffff"], [1, "#d8e8f8"]], "#f4faff",
                   haze="#d0e2f2", deep="#a0bcd8", ink="#1a2a40", smoke=[[0, "#d0dce8"], [1, "#eef4fa"]], dust="#e0d0b0",
                   slab="#c8b48a", hot_core=None, tint="#fafcff", needle_le=0.6),
    "projection": _pal("#9ff0ff", "#2a5aa0", "#dffaff", "#ffffff", {"glow": "#6ac0f0"},
                       [[0, "#ffffff"], [1, "#9ff0ff"]], "#b8f4ff",
                       haze="#8ce4f8", deep="#4ab8e8", ink="#0a2040", smoke=[[0, "#a8c8e0"], [1, "#d8ecf8"]], dust="#e0e8f0",
                       slab="#b8c8d8", hot_core=None, tint="#f4fcff", needle_le=1),
    # ---- AVATAR-only
    "energy": _pal("#ffffff", "#3a2a8a", "#e8e0ff", "#ffffff", {"glow": "#c0a8ff", "mid": "#a8c8ff"},
                   [[0, "#ffffff"], [0.3, "#ffe8a8"], [0.6, "#a8d0ff"], [1, "#c0a8ff"]], "#f0e8ff",
                   haze="#c8b8ff", deep="#8a70e8", ink="#0a0828", smoke=[[0, "#4a4070"], [1, "#7a70a0"]], dust="#e0d8f0",
                   slab="#b8b0c8", hot_core=[[0, "#ffffff"], [0.3, "#e8e0ff"], [1, "#6a5ac0"]], tint="#faf8ff", needle_le=1),
}
for name, look in LOOKS.items():
    kit.PALS.setdefault(name, look)


def element_kit(name):
    """The Dragon kit's plumbing with this element's colours as defaults."""
    L = LOOKS[name]
    ns = SimpleNamespace(name=name, look=L, pal=name, kit=kit)
    ns.haze = lambda centre, t0, dur, **kw: kit.aura_haze(centre, t0, dur, **dict({"col": L["haze"], "deep": L["deep"], "pal": name}, **kw))
    ns.needles = lambda *a, **kw: kit.needles(*a, **dict({"color": L["spark"], "le": L["needle_le"]}, **kw))
    ns.ink = lambda *a, **kw: kit.ink(*a, **dict({"color": L["ink"]}, **kw))
    ns.speed_lines = lambda *a, **kw: kit.speed_lines(*a, **dict({"color": L["spark"]}, **kw))
    ns.dark_haze = lambda *a, **kw: kit.dark_haze(*a, **dict({"color": L["smoke"]}, **kw))
    ns.crater = lambda *a, **kw: kit.crater(*a, **dict({"core": L["hot_core"], "hot": L["hot_core"] is not None, "slab_color": L["slab"]}, **kw))
    ns.glint = lambda *a, **kw: kit.glint(*a, **dict({"pal": name}, **kw))
    ns.stack = lambda tex, at, t, **kw: kit.emit_stack(tex, at, t, **dict({"pal": name, "cool": False}, **kw))
    ns.light = lambda at, keys, **kw: kit.light(at, keys, **dict({"color": L["light"]}, **kw))
    ns.write = lambda fx, path, form="hybrid": kit.write(fx, path, form=form, tint=L["tint"])
    return ns
