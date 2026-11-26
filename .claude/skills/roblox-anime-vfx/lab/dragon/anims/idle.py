"""Dragon idle (full form), reworked after "so stiff, zero movement" with the reference study: the dragon never hangs
straight. Path-follow: the head slowly circles a tilted loop (radius 6.5, 5 s), so the 30-stud body COILS around under
it like the classic coiled pose and keeps flowing; it banks into the circle; a secondary ripple whips down the body;
the head bobs (figure-8 in height), the jaw breathes, whiskers stream and drift, legs paddle. Seamless 5 s loop
(the path is periodic and the body is formed by a pre-roll)."""
import math
from anim_kit import merge, ripple, wave, write

T, R, TILT = 5.0, 6.5, math.radians(32)
PRE, dur = -10.0, 10.0
P = []
for i in range(int(PRE * 30), int(dur * 30) + 1):
    t = i / 30
    th = 2 * math.pi * t / T
    x, zp = R * math.cos(th), R * math.sin(th)
    P.append([round(t, 4), [round(x, 3), round(10 + zp * math.sin(TILT) + 1.4 * math.sin(2 * th + 0.6), 3), round(-3 + zp * math.cos(TILT), 3)]])
life = dur - PRE
tracks = ripple(1.7, amp=3.5, waves=1.6, start=4, grow=0.8)
for k, v in ripple(2.5, amp=2.5, waves=1.0, start=4, grow=0.5, axis=0).items():
    tracks[k] = merge(tracks[k], v) if k in tracks else v
for side in "LR":
    for i in range(3):
        tracks[f"whisker{side}_{i}"] = merge(wave(1.25, (14, 0, 0), 0.9 * i, base=(-18, 0, 0)), wave(2.5, (0, 0, 10 if side == "L" else -10), 0.8 * i))
for leg, ph in (("legFL", 0), ("legFR", math.pi), ("legBL", math.pi * 0.5), ("legBR", math.pi * 1.5)):
    tracks[f"{leg}_0"] = wave(1.25, (28, 0, 0), ph, base=(-10, 0, 0))
    tracks[f"{leg}_1"] = wave(1.25, (-25, 0, 0), ph + 0.9, base=(10, 0, 0))
jaw = [[round((t - PRE) / life, 4), round(5 + 6 * math.sin(2 * math.pi * t / 2.5), 2)] for t in [PRE + i * 0.1 for i in range(int(life * 10) + 1)]]
fx = {"name": "dragon_idle", "title": "Dragon idle", "duration": dur,
      "layers": [{"type": "rig", "model": "dragon", "path": P, "t0": PRE, "life": life, "roll": [[0, 0], [1, 0]],
                  "jawBone": "jaw", "jaw": jaw, "boneTracks": tracks, "brightness": 1.65}],
      "camera": {"pos": [[0, [-2, 14, 17]], [1, [3, 13.5, 16]]], "look": [[0, [0, 9.5, -3]], [1, [0, 9.5, -3]]], "fov": 62},
      "poster": 0.25}
print(write(fx, "dragon_idle"))
