"""Hybrid (base form) pieces on the avatar, idle: horns + head-side scales (Head), torso-side scales (UpperTorso), and
the skinned tail (LowerTorso) swaying in a lazy travelling S with a curl at the tip. 4 s loop, camera orbits."""
import math
from anim_kit import merge, wave, write

T, dur = 4.0, 6.0
tail = {}
for i in range(7):
    f = i / 6
    tail[f"tail_{i}"] = merge(wave(T, (0, 0, 7 + 6 * f), 1.1 * i), wave(T / 2, (4 + 3 * f, 0, 0), 0.9 * i + 0.5, base=(3 + 4 * f, 0, 0)))
L = [{"type": "attach", "model": "dragon_hybrid_head", "part": "head", "t0": 0, "life": dur},
     {"type": "attach", "model": "dragon_hybrid_torso", "part": "torso", "t0": 0, "life": dur},
     {"type": "attach", "model": "dragon_hybrid_tail", "part": "hips", "t0": 0, "life": dur, "boneTracks": tail}]
for l in L:
    l["brightness"] = 0.95
cam = [[round(i / 40, 4), [round(6.5 * math.sin(2 * math.pi * i / 40 * 0.75 + 0.6), 3), 4.4, round(6.5 * math.cos(2 * math.pi * i / 40 * 0.75 + 0.6), 3)]] for i in range(41)]
fx = {"name": "dragon_hybrid_idle", "title": "Dragon hybrid pieces", "duration": dur, "caster": True, "layers": L,
      "pose": {"armR": [[0, 0]], "armL": [[0, 0]]},
      "camera": {"pos": cam, "look": [[0, [0, 3.6, 0]], [1, [0, 3.6, 0]]], "fov": 55}, "poster": 0.1}
print(write(fx, "dragon_hybrid_idle"))
