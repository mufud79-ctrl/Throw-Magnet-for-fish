"""Dragon M1 (full form basic attack): a bite lunge. Rigid follow (the body holds its shape while the head strikes).
0.00-0.30 anticipation: the head rears up and draws back (root pulls back, pitch up, neck counter-bends so the body
stays level), the jaw gapes, front claws lift, whiskers lag / 0.30-0.40 strike: the whole dragon lunges forward and the
head drives down at the target / 0.42 the jaw SNAPS shut on contact, hit-stop 0.06, small shake / 0.45-0.70
follow-through: the head overshoots down and a ripple whips back down the body to the tail / 0.70-1.40 settle back to
the hover. Squash/stretch: the neck stretches on the lunge (pitch spread over neck bones), compresses on the rear."""
import math
from anim_kit import NB, keys, merge, wave, write

dur = 1.4
TS = 0.42                                                    # snap
root = [[0, [0, 7, 8]], [0.30, [0, 8.2, 10.5], "out"], [0.40, [0, 6.2, 2.5], "in"], [0.50, [0, 6.0, 1.8], "out"],
        [0.75, [0, 6.6, 5.5]], [1.4, [0, 7, 8], "out"]]
orient = [[0, [0, 0, 0]], [0.30, [20, 0, 0], "out"], [0.40, [-14, 0, 0], "in"], [0.52, [-18, 0, 0], "out"],
          [0.80, [-4, 0, 0]], [1.4, [0, 0, 0], "out"]]
jaw = [[0, 0], [0.30 / dur, 42, "out"], [0.385 / dur, 46], [TS / dur, 0, "in"], [0.60 / dur, 4], [1, 0]]
tracks = {
    # neck counter-bend: keep the body level while the root pitches (neck carries the head up/down)
    "spine_01": keys((0, (0, 0, 0)), (0.30, (-9, 0, 0), "out"), (0.40, (6, 0, 0), "in"), (0.52, (8, 0, 0)), (0.80, (2, 0, 0)), (1.4, (0, 0, 0), "out")),
    "spine_02": keys((0, (0, 0, 0)), (0.30, (-11, 0, 0), "out"), (0.40, (8, 0, 0), "in"), (0.52, (10, 0, 0)), (0.80, (2, 0, 0)), (1.4, (0, 0, 0), "out")),
}
# follow-through ripple: a yaw kick travelling tailward after the snap
for i in range(3, NB):
    d = (i - 3) * 0.025
    a = 7 * (1 - 0.3 * (i - 3) / (NB - 4))
    tracks[f"spine_{i:02d}"] = keys((0, (0, 0, 0)), (0.30 + d, (0, 0, -a * 0.5)), (TS + d, (0, 0, a), "out"), (0.62 + d, (0, 0, -a * 0.6)),
                                     (0.85 + d, (0, 0, a * 0.25)), (1.4, (0, 0, 0), "out"))
for side in "LR":
    tracks[f"legF{side}_0"] = keys((0, (0, 0, 0)), (0.28, (-55, 0, 0), "out"), (0.40, (35, 0, 0), "in"), (0.55, (25, 0, 0)), (1.4, (0, 0, 0), "out"))
    tracks[f"legF{side}_1"] = keys((0, (0, 0, 0)), (0.28, (40, 0, 0), "out"), (0.40, (-30, 0, 0), "in"), (0.6, (-15, 0, 0)), (1.4, (0, 0, 0), "out"))
    for i in range(3):
        lag = 0.04 * (i + 1)
        tracks[f"whisker{side}_{i}"] = keys((0, (0, 0, 0)), (0.30 + lag, (25, 0, 0)), (0.42 + lag, (-35, 0, 0), "out"), (0.70 + lag, (12, 0, 0)), (1.4, (0, 0, 0), "out"))
fx = {"name": "dragon_m1", "title": "Dragon M1 (bite)", "duration": dur,
      "layers": [{"type": "rig", "model": "dragon", "follow": "rigid", "t0": 0, "life": dur, "path": root, "orient": orient,
                  "jawBone": "jaw", "jaw": jaw, "boneTracks": tracks, "brightness": 1.9}],
      "dummies": [[0, 0, -11]],
      "hits": [{"t": TS, "dummy": 0, "dir": [0, -0.3, -1], "power": 1.0}],
      "hitstop": [{"t": TS + 0.02, "dur": 0.06}],
      "shakes": [{"t": TS, "amp": 0.35, "dur": 0.22, "freq": 22}],
      "camera": {"pos": [[0, [17, 8, -9]], [0.3, [16, 7.6, -8]], [0.45, [14.5, 7, -8], "out"], [1, [15.5, 7.4, -8]]],
                 "look": [[0, [0, 5.5, -5]], [1, [0, 5, -6]]], "fov": 55}, "poster": 0.3}
print(write(fx, "dragon_m1"))
