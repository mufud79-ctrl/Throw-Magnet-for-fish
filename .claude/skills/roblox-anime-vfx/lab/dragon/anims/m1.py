"""Dragon M1 (full form basic attack), reworked after "so stiff": the bite is a whip of the whole body, not a nod.
Path-follow (the body coils and uncoils through the head's own trail):
 -4.0-0.00 cruise in, a lazy S toward the target
 0.00-0.34 ANTICIPATION: the head rears up and back like a cobra (slowing to a hang at the top), the neck coils into
           an S behind it, jaw gapes, front claws lift, whiskers lag
 0.34-0.46 STRIKE: the head whips down and forward at ~120 studs/s; the body uncoils behind it (stretch)
 0.46      SNAP on the target, hit-stop 0.07, shake
 0.46-0.80 follow-through: the head drives past and swoops back up, a ripple cracks down to the tail
 0.80-1.60 settle into a wide turn back to a hover."""
import math
from anim_kit import NB, keys, merge, spline, wave, write

dur, PRE, TS = 1.6, -4.0, 0.46
K = [(-4.0, (26, 10, 4)), (-2.8, (19, 11.5, 8)), (-1.6, (13, 9, 5)), (-0.6, (7, 9.5, 3)),
     (0.0, (4.5, 9.0, 1.0)),                 # start of the rear-up
     (0.18, (4.0, 13.0, 3.5), 0.8),
     (0.34, (2.5, 15.5, 2.0), 0.15),         # hang at the top of the cobra S
     (0.46, (0.0, 4.0, -9.5), 1.6),          # snap at the target's chest (whips through)
     (0.58, (-1.5, 3.4, -14.0), 0.9),        # drives past, low
     (0.80, (-4.0, 8.5, -16.0)),             # swoops up
     (1.15, (-9.0, 11.0, -11.0)),
     (1.60, (-12.0, 11.0, -3.0))]
P = spline(K, 1 / 60)
life = dur - PRE
kn = lambda t: round((t - PRE) / life, 4)
jaw = [[0, 3], [kn(0.0), 4], [kn(0.30), 48, "out"], [kn(0.42), 52], [kn(TS), 0, "in"], [kn(0.62), 6], [kn(1.0), 2], [1, 2]]
tracks = {}
# extra whip after the snap, travelling tailward
for i in range(4, NB):
    d = (i - 4) * 0.022
    a = 9 * (1 - 0.4 * (i - 4) / (NB - 5))
    tracks[f"spine_{i:02d}"] = keys((0, (0, 0, 0)), (TS + d, (0, 0, 0)), (TS + 0.07 + d, (0, 0, a), "out"), (TS + 0.2 + d, (0, 0, -a * 0.7)),
                                     (TS + 0.36 + d, (0, 0, a * 0.3)), (TS + 0.6 + d, (0, 0, 0)))
for k_, tr in tracks.items():
    tr["offset"] = 0
    tr["rot"] = [[round(r[0] - PRE, 4), r[1]] + r[2:] for r in tr["rot"]]   # tracks run on age (seconds from t0)
for side in "LR":
    tracks[f"legF{side}_0"] = {"rot": [[0, [-20, 0, 0]], [-PRE + 0.0, [-20, 0, 0]], [-PRE + 0.32, [-70, 0, 0], "out"], [-PRE + TS, [40, 0, 0], "in"],
                                        [-PRE + 0.7, [20, 0, 0]], [-PRE + 1.6, [-20, 0, 0]]]}
    tracks[f"legF{side}_1"] = {"rot": [[0, [20, 0, 0]], [-PRE + 0.32, [60, 0, 0], "out"], [-PRE + TS, [-40, 0, 0], "in"], [-PRE + 1.6, [20, 0, 0]]]}
    for i in range(3):
        lag = 0.05 * (i + 1)
        tracks[f"whisker{side}_{i}"] = {"rot": [[0, [-15, 0, 0]], [-PRE + 0.34 + lag, [30, 0, 0]], [-PRE + TS + lag, [-55, 0, 0], "out"],
                                                 [-PRE + 0.8 + lag, [10, 0, 0]], [-PRE + 1.6, [-15, 0, 0]]]}
fx = {"name": "dragon_m1", "title": "Dragon M1 (bite)", "duration": dur,
      "layers": [{"type": "rig", "model": "dragon", "path": P, "t0": PRE, "life": life, "jawBone": "jaw", "jaw": jaw,
                  "boneTracks": tracks, "brightness": 1.65}],
      "dummies": [[0, 0, -11]],
      "hits": [{"t": TS, "dummy": 0, "dir": [0, -0.2, -1], "power": 1.4}],
      "hitstop": [{"t": TS + 0.02, "dur": 0.07}],
      "shakes": [{"t": TS, "amp": 0.5, "dur": 0.25, "freq": 22}],
      "camera": {"pos": [[0, [22, 10, 2]], [0.25, [21, 11, 1]], [0.3, [19, 8.5, -3], "out"], [1, [20, 9, -2]]],
                 "look": [[0, [2, 9, -3]], [0.25, [2, 9.5, -3]], [0.3, [0, 6, -8], "out"], [1, [-2, 7, -8]]], "fov": 60}, "poster": 0.3}
print(write(fx, "dragon_m1"))
