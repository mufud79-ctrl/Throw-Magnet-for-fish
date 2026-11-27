"""Scaffold a bending move script on the house pipeline (roblox-anime-vfx lab + the Dragon kit + element looks).

    python3 .claude/skills/bending-vfx/scripts/new_move.py <look> <NN> <MoveName> [--lead "what the lead shape is"]

e.g.  new_move.py water 01 Lashline --lead "a sweeping water ribbon with a foam edge"
Writes roblox-anime-vfx/lab/bending/<look>/moves/<move_name>.py (never overwrites). The file is a WORKING placeholder
(it renders) laid out in the house order: anticipation -> PRIMARY -> SECONDARY -> TERTIARY -> OUTSIDE haze -> MASS ->
follow-through. Replace every placeholder shape with the move's real lead shape: the scaffold is plumbing, never
the design (no shared recipe: see the bending-vfx skill).
Render:  cd .claude/skills/roblox-anime-vfx/lab && node render.mjs bending/<look>/moves/<look>_<NN>_<Name>.json --hd --fps 60 --out out/bending
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", "roblox-anime-vfx", "lab"))

TEMPLATE = '''"""{title} ({look}) - {lead}.

Beat sheet (fill in: timings, the five animation rules, one lead shape)
  0.00-{ta:.2f}  anticipation: the source gathers (stance, pull-in, glow)
  {ta:.2f}       release / strike: the PRIMARY lead shape (frame 0-2)
  +1-2 frames  SECONDARY shapes; then TERTIARY sparkles
  {ta:.2f}-...   OUTSIDE haze spreads past the hit; MASS (dust, marks, debris); follow-through
Camera: fixed gameplay camera (an ability, not a cutscene).
Run: python3 lab/bending/{look}/moves/{fname}.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from elements import element_kit  # noqa: E402

K = element_kit("{look}")
kit = K.kit
TA = {ta}
DUR = 1.6
TARGET = [0, 0, -9]


def build():
    L = []
    hit = [TARGET[0], 3.0, TARGET[2] + 1.0]
    # ---- anticipation (replace): the element's source gathers at the caster
    L += K.glint([0.6, 3.2, -1.2], TA - 0.12, size=2.5, life=0.18, seed=1)
    # ---- PRIMARY (replace with the move's lead shape: {lead})
    L += K.stack("anime_slash", hit, TA, size=[[0, 7], [1, 7.5]], life=0.36, rot=-30, seed=2, z=0.6)
    # ---- SECONDARY (+1-2 frames): a dark accent + a flash
    L += K.ink(hit, TA + 0.02, 5, seed=3)
    L += K.glint([hit[0], hit[1] + 0.4, hit[2] + 0.3], TA + 0.01, size=4.5, life=0.2, seed=4)
    # ---- TERTIARY: the small bright bits
    L.append(K.needles(hit, TA + 0.02, 12, speed=(40, 70), size=3.4, spread=60, seed=5))
    # ---- OUTSIDE: the smooth haze past the hit (never skip it)
    L += K.haze([TARGET[0], 0, TARGET[2]], TA, 1.2, radius=5.0, height=4.0, strength=0.9, seed=6, cloud=0.5)
    # ---- MASS: dust ring, a ground mark, a dark anchor
    L.append(kit.dust_ring([TARGET[0], 0, TARGET[2]], TA + 0.01, n=10, speed=(20, 28), size=(2.5, 5), seed=7))
    L.append(K.dark_haze([TARGET[0], 3, TARGET[2] - 1], TA + 0.08, n=4, size=(3, 7), seed=8))
    return {{
        "name": "{fname_json}", "title": "{title}", "element": "{look}", "archetype": "{archetype}", "duration": DUR,
        "layers": L, "dummies": [TARGET],
        "hits": [{{"t": TA + 0.02, "dummy": 0, "dir": [0, 0, -1], "power": 0.6}}],
        "hitstop": [{{"t": TA + 0.04, "dur": 0.06}}],
        "shakes": [{{"t": TA + 0.02, "amp": 0.2, "dur": 0.15, "freq": 22}}],
        "lights": [K.light(hit, [[TA, 0], [TA + 0.02, 24], [TA + 0.3, 0]], rng=16)],
        "camera": kit.GAMEPLAY_CAM,
        "poster": TA + 0.06,
    }}


K.write(build(), os.path.join(os.path.dirname(__file__), "{fname_json}.json"))
print("wrote {fname_json}.json")
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("look")
    ap.add_argument("nn")
    ap.add_argument("name")
    ap.add_argument("--lead", default="describe the lead shape")
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(LAB, "bending"))
    from elements import LOOKS
    if a.look not in LOOKS:
        sys.exit(f"unknown look {a.look!r}; one of: {', '.join(LOOKS)}")
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", a.name).lower()
    d = os.path.join(LAB, "bending", a.look, "moves")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{snake}.py")
    if os.path.exists(path):
        sys.exit(f"{path} exists; not overwriting")
    open(path, "w").write(TEMPLATE.format(title=a.name, look=a.look, lead=a.lead, ta=0.35, fname=snake,
                                          fname_json=f"{a.look}_{a.nn}_{a.name}", archetype=snake))
    print("wrote", os.path.relpath(path, os.getcwd()))


if __name__ == "__main__":
    main()
