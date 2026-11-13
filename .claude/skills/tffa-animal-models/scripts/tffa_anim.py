"""Procedural looping clips for TFFA rigs, driven by standard bone names.

Bone axes (see Model._rig): rotation X = pitch (+ nose up / leg swings forward / tail down),
Y = yaw (+ turn to the animal's left), Z = roll (+ lowers the animal's LEFT side). Location Y = up.
Clips: Idle (always), Walk (anything with legs, a spine or tentacles), Fly (anything with wings).
Set model.gait = {...} to override: walk=False, fly=True/False, amp=1.0 (scales motion), hop=True (frog/rabbit)."""
import math
import bpy

FPS = 30
def S(t, ph=0.0, k=1.0): return math.sin(2 * math.pi * (k * t + ph))

def _has(names, *prefixes): return [n for n in names if n.startswith(prefixes)]

def _clip(arm, name, frames, poses, height):
    """poses: dict bone -> fn(t) -> (rx, ry, rz) degrees [, (lx, ly, lz) in units of model height]."""
    act = bpy.data.actions.new(f"{arm.name}_{name}"); act["clip"] = name; act["frames"] = frames; act.use_fake_user = True
    arm.animation_data_create(); arm.animation_data.action = act
    for pb in arm.pose.bones:                       # key every bone: unanimated bones hold their rest pose
        pb.rotation_mode = "XYZ"; pb.rotation_euler = (0, 0, 0); pb.location = (0, 0, 0)
        for f in (0, frames):
            pb.keyframe_insert("rotation_euler", frame=f); pb.keyframe_insert("location", frame=f)
    for f in range(0, frames + 1, 2):
        t = (f % frames) / frames
        for bn, fn in poses.items():
            pb = arm.pose.bones.get(bn)
            if pb is None: continue
            r = fn(t); rot = r[0] if isinstance(r[0], tuple) else r
            pb.rotation_euler = tuple(math.radians(a) for a in rot); pb.keyframe_insert("rotation_euler", frame=f)
            if isinstance(r[0], tuple) and len(r) > 1:
                pb.location = tuple(v * height for v in r[1]); pb.keyframe_insert("location", frame=f)
    for fc in getattr(act, "fcurves", []):
        for kp in fc.keyframe_points: kp.interpolation = "BEZIER"
    return act

def add_clips(arm, model):
    names = [b.name for b in arm.data.bones]; g = dict(getattr(model, "gait", {}) or {})
    H = float(arm.get("height", 3.0)); amp = g.get("amp", 1.0)
    quad = all(f"Leg_{k}" in names for k in ("FL", "FR", "BL", "BR"))
    biped = "Leg_L" in names and "Leg_R" in names and not quad
    wings = "Wing_L" in names and "Wing_R" in names
    tails = sorted(_has(names, "Tail"), key=lambda n: int("".join(c for c in n if c.isdigit()) or 0))
    necks = sorted(_has(names, "Neck"), key=lambda n: int("".join(c for c in n if c.isdigit()) or 0))
    tents = _has(names, "Tent")
    ears = _has(names, "Ear_"); fins = _has(names, "Fin_")
    clips = []

    # ------------------------------------------------------------------ Idle (72 f): breathe, look around, wag, blink-ish ear twitch
    P = {"Body": lambda t: ((1.2 * S(t), 0, 0), (0, 0.012 * amp * S(t), 0))}
    for i, n in enumerate(necks): P[n] = (lambda i: lambda t: (2.5 * S(t, 0.1 * i), 4 * S(t, 0.25 + 0.1 * i), 0))(i)
    P["Head"] = lambda t: (3 * S(t, 0.15, 2), 9 * amp * S(t, 0.3), 2 * S(t, 0.1))
    if "Jaw" in names: P["Jaw"] = lambda t: (4 * max(0, S(t, 0, 2)), 0, 0)
    for i, n in enumerate(tails): P[n] = (lambda i: lambda t: (2 * S(t, -0.1 * i), 11 * amp * S(t, -0.12 * i), 0))(i)
    for n in ears: P[n] = (lambda s: lambda t: (14 * max(0, math.sin(math.pi * min(1, max(0, (t - 0.55) / 0.08)))), 0, 0))(n)
    if wings:
        P["Wing_L"] = lambda t: (0, 0, -3 + 3 * S(t, 0, 2)); P["Wing_R"] = lambda t: (0, 0, 3 - 3 * S(t, 0, 2))
    for n in fins: P[n] = (lambda s: lambda t: (0, 0, s * 8 * S(t, 0, 2)))(1 if n.endswith("L") else -1)
    for n in tents: P[n] = (lambda k, j: lambda t: (7 * S(t, -0.15 * j + 0.13 * k), 4 * S(t, 0.2 * k), 0))(*_tk(n))
    clips.append(_clip(arm, "Idle", 72, P, H))

    # ------------------------------------------------------------------ Walk
    if g.get("walk", True) and (quad or biped or tails or tents or fins or necks):
        if quad:
            T = 24; A = 24 * amp; hop = g.get("hop", False)
            P = {}
            if hop:          # bunny hop: front pair together, back pair together
                P = {"Leg_FL": lambda t: (A * S(t), 0, 0), "Leg_FR": lambda t: (A * S(t), 0, 0),
                     "Leg_BL": lambda t: (A * S(t, 0.5), 0, 0), "Leg_BR": lambda t: (A * S(t, 0.5), 0, 0),
                     "Body": lambda t: ((5 * S(t, 0.25), 0, 0), (0, 0.07 * max(0, S(t)), 0))}
            else:            # trot: diagonal pairs
                P = {"Leg_FL": lambda t: (A * S(t), 0, 0), "Leg_BR": lambda t: (A * S(t), 0, 0),
                     "Leg_FR": lambda t: (-A * S(t), 0, 0), "Leg_BL": lambda t: (-A * S(t), 0, 0),
                     "Body": lambda t: ((1.5 * S(t, 0.25, 2), 1.5 * S(t), 2 * S(t)), (0, 0.025 * (0.5 - 0.5 * math.cos(4 * math.pi * t)), 0))}
            P["Head"] = lambda t: (-4 * S(t, 0.1, 2), -2 * S(t), 0)
            for i, n in enumerate(necks): P[n] = (lambda i: lambda t: (3 * S(t, 0.05, 2), 0, 0))(i)
            for i, n in enumerate(tails): P[n] = (lambda i: lambda t: (3 * S(t, -0.1 * i, 2), 14 * S(t, -0.15 * i), 0))(i)
        elif biped:
            T = 28; A = 28 * amp
            P = {"Leg_L": lambda t: (A * S(t), 0, 0), "Leg_R": lambda t: (-A * S(t), 0, 0),
                 "Arm_L": lambda t: (-0.7 * A * S(t), 0, 0), "Arm_R": lambda t: (0.7 * A * S(t), 0, 0),
                 "Body": lambda t: ((2 * S(t, 0.25, 2), 4 * S(t), -4 * S(t)), (0, 0.03 * (0.5 - 0.5 * math.cos(4 * math.pi * t)), 0)),
                 "Head": lambda t: (-3 * S(t, 0.1, 2), -3 * S(t), 3 * S(t))}
            for i, n in enumerate(tails): P[n] = (lambda i: lambda t: (2 * S(t, -0.1 * i, 2), -10 * S(t, -0.12 * i), 0))(i)
            for i, n in enumerate(necks): P[n] = (lambda i: lambda t: (4 * S(t, 0.05, 2), 0, 0))(i)
            if wings: P["Wing_L"] = lambda t: (0, 0, -4 * S(t, 0, 2)); P["Wing_R"] = lambda t: (0, 0, 4 * S(t, 0, 2))
        else:                # no legs: slither / flop / swim-crawl with the spine, tentacles or fins
            T = 36
            P = {"Body": lambda t: ((3 * S(t, 0, 2), 6 * S(t), 0), (0, 0.03 * max(0, S(t, 0, 2)), 0)), "Head": lambda t: (-3 * S(t, 0.2, 2), -8 * S(t, 0.2), 0)}
            for i, n in enumerate(necks): P[n] = (lambda i: lambda t: (0, 14 * S(t, -0.15 * i), 0))(i)
            for i, n in enumerate(tails): P[n] = (lambda i: lambda t: (10 * S(t, -0.15 * i, 2), 14 * S(t, -0.15 * i), 0))(i)
            for n in tents: P[n] = (lambda k, j: lambda t: (16 * S(t, -0.18 * j + 0.25 * k), 6 * S(t, 0.25 * k), 0))(*_tk(n))
            for n in fins: P[n] = (lambda s: lambda t: (20 * S(t, 0, 2), 0, s * 12 * S(t, 0, 2)))(1 if n.endswith("L") else -1)
        clips.append(_clip(arm, "Walk", T, P, H))

    # ------------------------------------------------------------------ Fly (20 f): big flaps, body bobs against the stroke, legs tucked
    if wings and g.get("fly", True):
        T = 20; A = 34 * amp
        P = {"Wing_L": lambda t: (0, 0, A * S(t) - 6), "Wing_R": lambda t: (0, 0, -A * S(t) + 6),
             "Body": lambda t: ((-8 + 2 * S(t, 0.25), 0, 0), (0, 0.18 + 0.05 * S(t, 0.5), 0)),
             "Head": lambda t: (8 - 2 * S(t, 0.25), 0, 0)}
        for n in ("Leg_FL", "Leg_FR", "Leg_BL", "Leg_BR", "Leg_L", "Leg_R"):
            if n in names: P[n] = (lambda b: lambda t: (b + 3 * S(t, 0.2), 0, 0))(35 if n.startswith("Leg_F") else -40)
        for i, n in enumerate(tails): P[n] = (lambda i: lambda t: (4 * S(t, -0.12 * i), 5 * S(t, -0.2 * i, 0.5), 0))(i)
        for i, n in enumerate(necks): P[n] = (lambda i: lambda t: (2 * S(t, 0.3), 0, 0))(i)
        clips.append(_clip(arm, "Fly", T, P, H))
    return clips

def _tk(n):
    k, j = n[4:].split("_"); return int(k), int(j)
