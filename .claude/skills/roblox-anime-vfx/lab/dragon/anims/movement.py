"""Dragon movement (full form): flying/swimming through the sky. Path-follow: the head flies an S-weave and every spine
bone follows the head's own trail, so the body draws real S-curves; it banks into each turn (roll), legs tuck back
against the belly with a small paddle, whiskers stream back and flutter, the jaw stays shut. 4.5 s fly-by."""
import math
from anim_kit import merge, wave, write

dur = 4.5
T0 = -1.8                                    # the head starts flying before the clip, so the whole body is airborne at t=0
P = []
for i in range(int(T0 * 20), int(dur * 20) + 1):
    t = i / 20
    P.append([round(t, 3), [round(-34 + 17 * t, 3), round(13 + 4.2 * math.sin(2.1 * t), 3), round(10 * math.sin(1.4 * t + 0.4) - 4, 3)]])
# bank into the turns: roll follows the lateral acceleration of the weave (normalized keys over life)
life = dur - T0
roll = [[round(i / 60, 4), round(-22 * math.sin(1.4 * (T0 + i / 60 * life) + 0.4), 2)] for i in range(61)]
tracks = {}
for leg, ph in (("legFL", 0), ("legFR", math.pi), ("legBL", math.pi * 0.5), ("legBR", math.pi * 1.5)):
    tracks[f"{leg}_0"] = wave(0.8, (8, 0, 0), ph, base=(-45, 0, 0))       # tucked back, small paddle
    tracks[f"{leg}_1"] = wave(0.8, (-8, 0, 0), ph + 0.8, base=(40, 0, 0))
for side in "LR":
    for i in range(3):
        tracks[f"whisker{side}_{i}"] = merge(wave(0.5, (9, 0, 0), 0.9 * i, base=(-35 if i == 0 else -12, 0, 0)), wave(0.35, (0, 0, 7), 1.1 * i))
look = [[round(i / 30, 4), [round(-34 + 17 * (i / 30 * dur) - 9, 2), 11, -3]] for i in range(31)]
fx = {"name": "dragon_movement", "title": "Dragon movement", "duration": dur,
      "layers": [{"type": "rig", "model": "dragon", "path": P, "t0": T0, "life": life, "roll": roll, "jawBone": "jaw",
                  "jaw": [[0, 0], [1, 0]], "boneTracks": tracks, "brightness": 1.9}],
      "camera": {"pos": [[0, [-30, 26, 30]], [1, [12, 25, 32]]], "look": look, "fov": 60}, "poster": 0.55}
print(write(fx, "dragon_movement"))
