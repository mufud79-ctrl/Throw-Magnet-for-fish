"""Dragon movement (full form), reworked after "so stiff": big flowing waves like the reference, not a straight noodle.
Path-follow: the head swims forward at ~20 studs/s through a large vertical S (amp 6, wavelength ~26 studs) and a wide
lateral weave, so the whole 30-stud body ripples through two full curves at once; it rolls into each sideways turn; a
fast secondary whip runs down to the tail; legs tucked with a quick paddle, whiskers streaming and fluttering."""
import math
from anim_kit import merge, ripple, wave, write

dur, PRE = 5.0, -2.5
SPD, WL, AY, AZ = 19.0, 26.0, 6.0, 7.0
pos = lambda t: (-38 + SPD * t, 13 + AY * math.sin(2 * math.pi * SPD * t / WL), AZ * math.sin(2 * math.pi * SPD * t / (WL * 1.7) + 0.7) - 6)
P = [[round(i / 30, 4), [round(v, 3) for v in pos(i / 30)]] for i in range(int(PRE * 30), int(dur * 30) + 1)]
life = dur - PRE
# roll into the lateral turns: proportional to the weave's lateral acceleration
roll = []
for i in range(61):
    t = PRE + life * i / 60
    roll.append([round(i / 60, 4), round(30 * math.sin(2 * math.pi * SPD * t / (WL * 1.7) + 0.7), 2)])
tracks = ripple(0.55, amp=4.5, waves=2.0, start=5, grow=0.9)
for leg, ph in (("legFL", 0), ("legFR", math.pi), ("legBL", math.pi * 0.5), ("legBR", math.pi * 1.5)):
    tracks[f"{leg}_0"] = wave(0.55, (14, 0, 0), ph, base=(-50, 0, 0))
    tracks[f"{leg}_1"] = wave(0.55, (-12, 0, 0), ph + 0.8, base=(45, 0, 0))
for side in "LR":
    for i in range(3):
        tracks[f"whisker{side}_{i}"] = merge(wave(0.4, (12, 0, 0), 1.0 * i, base=(-40 if i == 0 else -15, 0, 0)), wave(0.3, (0, 0, 9), 1.2 * i))
jaw = [[0, 8], [1, 8]]
look = [[round(i / 30, 4), [round(pos(dur * i / 30)[0] - 10, 2), 12, -5]] for i in range(31)]
cam = [[round(i / 30, 4), [round(pos(dur * i / 30)[0] - 2, 2), 17, 24]] for i in range(31)]
fx = {"name": "dragon_movement", "title": "Dragon movement", "duration": dur,
      "layers": [{"type": "rig", "model": "dragon", "path": P, "t0": PRE, "life": life, "roll": roll, "jawBone": "jaw",
                  "jaw": jaw, "boneTracks": tracks, "brightness": 1.65}],
      "camera": {"pos": cam, "look": look, "fov": 62}, "poster": 0.5}
print(write(fx, "dragon_movement"))
