"""Dragon idle (full form): a 4 s seamless loop, hovering. The head holds steady and watches; the long body ripples
in a lazy travelling S (yaw + a little pitch); a slow breath lifts the chest and parts the jaw; whiskers drift with
overlapping lag; the small legs paddle the air out of phase (front vs back). Rendered over 8 s (two loops)."""
import math
from anim_kit import NB, body_wave, merge, wave, write

T = 4.0
tracks = body_wave(T, yaw=8.0, pitch=1.4, waves=1.1, start=2, grow=0.5,
                   yaw_base=lambda f: 15 * math.sin(math.pi * 2 * f * 0.85))       # resting S-curve
tracks["spine_01"] = wave(T, (2.5, 0, 0), 0.4)                                     # neck breathes (head bob)
for side in "LR":
    for i in range(3):
        tracks[f"whisker{side}_{i}"] = merge(wave(T, (10, 0, 0), 0.9 * i), wave(T / 2, (0, 0, 6 if side == "L" else -6), 0.7 * i + (0 if side == "L" else 1.2)))
for leg, ph in (("legFL", 0), ("legFR", math.pi), ("legBL", math.pi * 0.5), ("legBR", math.pi * 1.5)):
    tracks[f"{leg}_0"] = wave(T, (16, 0, 0), ph)
    tracks[f"{leg}_1"] = wave(T, (-14, 0, 0), ph + 0.8, base=(-10, 0, 0))
breath = [[round(T * i / 24, 3), round(4 + 4 * math.sin(2 * math.pi * i / 24 - 0.3), 2)] for i in range(25)]
dur = 8.0
jaw = [[round(k / dur, 4), v] for k, v in breath] + [[round((k + T) / dur, 4), v] for k, v in breath[1:]]
bob = [[round(t * 0.1, 2), [0, round(9 + 0.35 * math.sin(2 * math.pi * t * 0.1 / T), 3), 0]] for t in range(81)]
orient = [[round(t * 0.1, 2), [round(1.5 * math.sin(2 * math.pi * t * 0.1 / T + 1), 3), round(-28 + 3 * math.sin(2 * math.pi * t * 0.1 / (2 * T)), 3), 0]] for t in range(81)]
fx = {"name": "dragon_idle", "title": "Dragon idle", "duration": dur,
      "layers": [{"type": "rig", "model": "dragon", "follow": "rigid", "t0": 0, "life": dur, "path": bob, "orient": orient,
                  "jawBone": "jaw", "jaw": jaw, "boneTracks": tracks, "brightness": 1.9}],
      "camera": {"pos": [[0, [-3, 11, -27]], [1, [-1.5, 10.6, -25.5]]], "look": [[0, [1, 8.6, -4]], [1, [1, 8.6, -4]]], "fov": 52},
      "poster": 0.3}
print(write(fx, "dragon_idle"))
