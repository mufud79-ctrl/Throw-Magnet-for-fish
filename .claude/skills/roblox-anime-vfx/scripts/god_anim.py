"""Thunder god animations (baked keyframes) + the drum ring, exported as one animated GLB for preview.

    /tmp/bpyenv/bin/python god_anim.py [clip ...] [--out DIR]       clips: idle (default)

Loads assets/meshes/thunder_god/thunder_god_rig.blend, appends the drum ring (assets/meshes/drum_ring/drum_ring.blend)
and parents its armature to the god's HumanoidRootPart, so the ring rides with the float bob.
Each clip is fully baked (a key per frame on every animated bone) so Roblox's importer and the previewer play the
same curves. Secondary motion on the sway chains is a damped wave travelling down each chain (each bone lags the
one above: follow-through / overlapping action), with only loop-frequency harmonics so loops are seamless.
Rotations are authored in armature space (X = pitch: + swings a hanging part back / toes down, Y = roll about the
forward axis, Z = yaw) via god_rig.set_world_rot.

Writes OUT/<clip>.glb (default OUT = assets/meshes/thunder_god/anim/).
"""
import os
import sys
import math
import argparse
import json
import numpy as np
import bpy
from mathutils import Vector, Euler, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import god_rig  # noqa: E402

FPS = 30
TAU = 2 * math.pi


def load_scene():
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "assets", "meshes", "thunder_god", "thunder_god_rig.blend"))
    god = bpy.data.objects["ThunderGod"]
    with bpy.data.libraries.load(os.path.join(ROOT, "assets", "meshes", "drum_ring", "drum_ring.blend")) as (src, dst):
        dst.objects = list(src.objects)
    for o in dst.objects:
        bpy.context.collection.objects.link(o)
    ring = bpy.data.objects["DrumRing"]
    # bone-parent the ring to the god's root, keeping its world placement
    ring.parent = god
    ring.parent_type = "BONE"
    ring.parent_bone = "HumanoidRootPart"
    pb = god.data.bones["HumanoidRootPart"]
    ring.matrix_parent_inverse = (god.matrix_world @ Matrix.Translation(pb.tail_local) @ pb.matrix_local.to_3x3().to_4x4()).inverted()
    bpy.context.scene.render.fps = FPS
    return god, ring


def rot(arm, name, x=0.0, y=0.0, z=0.0):
    god_rig.set_world_rot(arm, name, Euler((math.radians(x), math.radians(y), math.radians(z)), "XYZ"), 1.0)


def loc(arm, name, offset):
    """Translate a pose bone by an armature-space offset."""
    pb = arm.pose.bones[name]
    rest = arm.data.bones[name].matrix_local.to_3x3()
    pb.location = rest.inverted() @ Vector(offset)


def key_all(arm, frame):
    for pb in arm.pose.bones:
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        pb.keyframe_insert("location", frame=frame)


def reset(arm):
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)


def wave(t, T, harm, lag, i, phase=0.0):
    """Seamless loop wave: harmonic `harm` of the loop, delayed by `lag` radians per chain step `i`."""
    return math.sin(TAU * harm * t / T - lag * i + phase)


# ================================================================ clips
# ================================================================ poses
# A pose is two dicts: rots[bone] = (x, y, z) degrees in armature space, locs[bone] = (x, y, z) armature offset.
IDLE_T = 3.2
# idle arm hang (down from horizontal, forward swing, elbow bend): out and forward enough that the hands hover
# in front of the flared apron and sash instead of sinking into them (tuned with scripts/anim_audit.py)
IDLE_ARM = tuple(float(v) for v in os.environ.get("IDLE_ARM", "62,16,32").split(","))
IDLE_SWING = tuple(float(v) for v in os.environ.get("IDLE_SWING", "6,8").split(","))   # fore/aft swing, elbow swing
SIDES = (("Left", 1), ("Right", -1))
FINGER_NAMES = ("Index", "Middle", "Ring", "Pinky")


def arm(side, down, fwd, roll=0.0, elbow=20.0, twist=0.0, wflex=0.0, wside=0.0):
    """Arm pose. down: 90 hangs, 0 horizontal, <0 raised. fwd: 90 points forward, <0 behind.
    elbow: forearm bend. wflex: + curls the hand toward the palm, - bends it back. Mirrored by side."""
    s = 1 if side == "Left" else -1
    return {f"{side}UpperArm": (roll, s * down, s * -fwd), f"{side}LowerArm": (twist, 0, s * -elbow),
            f"{side}Hand": (0, s * wflex, s * -wside)}


def leg(side, fwd, knee, foot, splay=0.0):
    """fwd: + swings the thigh forward. knee: + bends. foot: + points the toes. splay: + out to the side."""
    s = 1 if side == "Left" else -1
    return {f"{side}UpperLeg": (-fwd, 0, s * splay), f"{side}LowerLeg": (knee, 0, 0), f"{side}Foot": (foot, 0, 0)}


def torso(lean=0.0, side=0.0, twist=0.0, low=0.0):
    """lean: + bends forward. twist: + turns the chest to his left. low: lower torso lean."""
    return {"UpperTorso": (lean, side, twist), "LowerTorso": (low, -0.25 * side, -0.35 * twist)}   # hips counter-rotate


def head(nod=0.0, tilt=0.0, turn=0.0):
    return {"Head": (nod, tilt, turn)}


HAND_SHAPES = {   # per finger: (k1, k2, k3 curl), spread; thumb: (k1, k2, k3 curl), thumb in/out
    # every shape keeps a natural cascade (more curl toward ring and pinky) and never bends fingers backwards
    "relaxed": ({"Index": ((28, 34, 22), -3), "Middle": ((34, 40, 26), 0), "Ring": ((40, 44, 30), 3), "Pinky": ((46, 48, 32), 6)}, ((16, 18, 14), 22)),
    "fist":    ({"Index": ((80, 95, 65), 0), "Middle": ((85, 95, 65), 0), "Ring": ((88, 95, 65), 1), "Pinky": ((90, 95, 65), 2)}, ((25, 35, 30), 38)),
    "open":    ({"Index": ((6, 8, 5), -4), "Middle": ((8, 10, 6), 0), "Ring": ((11, 13, 8), 3), "Pinky": ((14, 16, 10), 7)}, ((6, 8, 6), 10)),
    "spread":  ({"Index": ((-1, 4, 3), -12), "Middle": ((0, 4, 3), -3), "Ring": ((2, 6, 4), 6), "Pinky": ((4, 8, 5), 14)}, ((0, 4, 4), -18)),
    "point":   ({"Index": ((3, 5, 4), -2), "Middle": ((80, 95, 65), 0), "Ring": ((86, 95, 65), 1), "Pinky": ((90, 95, 65), 2)}, ((25, 35, 30), 38)),
    "claw":    ({"Index": ((22, 45, 40), -10), "Middle": ((24, 48, 40), -2), "Ring": ((26, 48, 40), 5), "Pinky": ((28, 46, 40), 12)}, ((10, 25, 25), 0)),
}


def hand(side, shape):
    s = 1 if side == "Left" else -1
    fingers, (tc, tin) = HAND_SHAPES[shape]
    out = {}
    for fn, (curls, spread) in fingers.items():
        for k in (1, 2, 3):
            out[f"{side}{fn}{k}"] = (0, s * curls[k - 1], s * spread if k == 1 else 0)
    for k in (1, 2, 3):
        c = tc[k - 1]
        out[f"{side}Thumb{k}"] = (0, s * c * 0.6, s * (tin + c * 0.6) if k == 1 else s * c * 0.4)
    return out


def merge(*ds):
    out = {}
    for d in ds:
        out.update(d)
    return out


def idle_pose(t, T=IDLE_T):
    """The floating idle as data: (god rots, god locs, ring rots, ring locs)."""
    gr, gl, rr, rl = {}, {}, {}, {}
    b = wave(t, T, 1, 0, 0)
    b_lag = wave(t, T, 1, 0, 0, -0.9)
    gl["HumanoidRootPart"] = (0, 0, 0.06 + 0.018 * b)
    # upper body: the chest heaves with the breath, sways side to side and turns a little, the hips counter it;
    # the head looks around slowly and settles after the chest
    sway = wave(t, T, 1, 0, 0, 0.6)
    turn = wave(t, T, 1, 0, 0, 2.2)
    gr["LowerTorso"] = (1.0 * b_lag, -0.8 * sway, -1.2 * turn)
    gr["UpperTorso"] = (-2.5 - 2.0 * b, 2.2 * sway, 3.0 * turn)
    glance = max(0.0, wave(t, T, 1, 0, 0, -2.6)) ** 3          # once a loop he glances down at his right hand
    gr["Head"] = (4.0 + 2.2 * b_lag + 9.0 * glance + 1.5 * wave(t, T, 3, 0, 0, 0.4), -1.5 * sway + 2.5 * wave(t, T, 2, 0, 0, 1.0),
                  11.0 * wave(t, T, 1, 0, 0, 1.6) + 3.0 * wave(t, T, 2, 0, 0, 0.3) - 2.0 * turn - 10.0 * glance)
    # arms hang naturally (about 74 degrees below horizontal, slightly forward, soft elbows) and swing a little
    # as if weightless: shoulder leads, elbow trails, wrist trails last; the two arms are out of step
    for side, s, ph in (("Left", 1, 0.0), ("Right", -1, 2.1)):
        fore = wave(t, T, 1, 0, 0, ph - 0.9) + 0.3 * wave(t, T, 2, 0, 0, ph * 0.7 - 0.5)
        down0, fwd0, elb0 = IDLE_ARM
        gr.update(arm(side, down0 + 4.0 * wave(t, T, 1, 0, 0, ph - 0.3), fwd0 + IDLE_SWING[0] * fore,
                      roll=8.0 + 6.0 * wave(t, T, 1, 0, 0, ph - 1.2),
                      elbow=elb0 + IDLE_SWING[1] * wave(t, T, 1, 0, 0, ph - 1.7), twist=12.0 + 8.0 * wave(t, T, 1, 0, 0, ph - 2.0),
                      wflex=9 + 5.0 * wave(t, T, 1, 0, 0, ph - 2.5), wside=1 + 2.5 * wave(t, T, 1, 0, 0, ph - 2.8)))
        relaxed = HAND_SHAPES["relaxed"][0]
        for fi, fn in enumerate(FINGER_NAMES):
            curls, spread = relaxed[fn]
            for k in (1, 2, 3):
                curl = curls[k - 1] + (6 + 3 * k) * wave(t, T, 1, 0.45, k, ph - 2.4 + 0.35 * (3 - fi))
                gr[f"{side}{fn}{k}"] = (0, s * curl, s * (spread + 2.0 * wave(t, T, 1, 0, 0, ph + fi)) if k == 1 else 0)
        for k in (1, 2, 3):
            c = 12 + 6 * wave(t, T, 1, 0.5, k, ph - 1.9)
            gr[f"{side}Thumb{k}"] = (0, s * c * 0.6, s * (16 + c * 0.6) if k == 1 else s * c * 0.4)
    for side, sgn, ph, knee0, foot0, splay in (("Left", 1, 0.0, 30, 22, 3), ("Right", -1, math.pi * 0.85, 16, 26, -3)):
        hip = wave(t, T, 1, 0, 0, ph - 0.8)
        gr[f"{side}UpperLeg"] = ((10 if sgn > 0 else -2) + 9.0 * hip, 0, splay + 2.0 * wave(t, T, 2, 0, 0, ph))
        gr[f"{side}UpperLeg"] = (-gr[f"{side}UpperLeg"][0], 0, gr[f"{side}UpperLeg"][2])
        gr[f"{side}LowerLeg"] = (knee0 + 13.0 * wave(t, T, 1, 0, 0, ph - 1.9), 0, 0)
        gr[f"{side}Foot"] = (foot0 + 10.0 * wave(t, T, 1, 0, 0, ph - 2.8), 0, 0)
    for ci, col in enumerate("RCL"):
        for i in range(1, 5):
            gr[f"Cape_{col}_{i}"] = ((5 if i > 1 else 3) + (1.2 + 0.5 * i) * wave(t, T, 2, 0.75, i, ci * 0.9) + 1.2 * b_lag,
                                     (0.6 + 0.3 * i) * wave(t, T, 1, 0.5, i, ci * 1.4), 0)
    for li in range(1, 7):
        for k in range(1, 4):
            gr[f"Mane_{li}_{k}"] = (3 + (1.0 + 0.6 * k) * wave(t, T, 2, 0.9, k, li * 0.8) + 0.8 * b_lag,
                                    (0.5 + 0.4 * k) * wave(t, T, 1, 0.7, k, li * 1.1), 0)
    for si, sd in enumerate("LR"):
        for k, bn in enumerate((f"Sash_{sd}_1", f"Sash_{sd}_2", f"Sash_{sd}_Tassel")):
            gr[bn] = ((1.5 + 1.0 * k) * wave(t, T, 2, 0.8, k, si * 1.2) - 1.5 * b_lag, 0.8 * k * wave(t, T, 1, 0.6, k, si), 0)
    for key, sgn in (("Hakama_F", -1), ("Hakama_B", 1)):
        for k in (1, 2):
            gr[f"{key}_{k}"] = (sgn * (1.2 + 0.8 * k) * wave(t, T, 2, 0.7, k, 0.5 if sgn > 0 else 0), 0, 0)
    rl["Root"] = (0, 0, 0.012 * wave(t, T, 1, 0, 0, -1.2))
    rr["Root"] = (0, 1.0 * wave(t, T, 1, 0, 0, -0.4), 0)
    for d in range(1, 9):
        ph = -d * TAU / 8
        rl[f"Drum_{d}"] = (0, 0.004 * wave(t, T, 2, 0, 0, ph + 1.0), 0.010 * wave(t, T, 2, 0, 0, ph))
        rr[f"Drum_{d}"] = (2.0 * wave(t, T, 2, 0, 0, ph - 0.6), 0, 1.5 * wave(t, T, 1, 0, 0, ph))
        rr[f"Tassel_{d}"] = (6.0 * wave(t, T, 2, 0, 0, ph - 1.4), 4.0 * wave(t, T, 1, 0, 0, ph - 1.0), 0)
    return gr, gl, rr, rl


STANCE = idle_pose(0.0)     # every move starts and ends here (= idle frame 0, so clips chain into the idle)


# ================================================================ key tracks
def _ease(name, u):
    if name == "lin":
        return u
    if name == "in":
        return u ** 3
    if name == "out":
        return 1 - (1 - u) ** 3
    if name == "snap":                         # fast start (releases): quadratic, so no joint jumps most of its way in one frame
        return 1 - (1 - u) ** 2.2
    if name == "strike":                       # accelerate into a hit, but spread over the frames (no single-frame pop)
        return u ** 1.7
    if name == "back":                         # overshoot then settle
        c = 2.2
        return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2
    if name == "hold":
        return 0.0 if u < 1 else 1.0
    return u * u * (3 - 2 * u)                 # "inout"


class Tracks:
    """Per-bone keys. key(t, pose, ease): pose bones get a key at t; the ease shapes the move INTO this key."""
    def __init__(self):
        self.r, self.l = {}, {}

    def key(self, t, rots=None, locs=None, ease="inout"):
        for bone, v in (rots or {}).items():
            self.r.setdefault(bone, []).append((t, tuple(v), ease))
        for bone, v in (locs or {}).items():
            self.l.setdefault(bone, []).append((t, tuple(v), ease))
        return self

    @staticmethod
    def _eval(keys, t):
        keys = sorted(keys, key=lambda k: k[0])
        if t <= keys[0][0]:
            return keys[0][1]
        for (t0, v0, _), (t1, v1, e1) in zip(keys, keys[1:]):
            if t <= t1:
                u = _ease(e1, (t - t0) / max(t1 - t0, 1e-6))
                return tuple(a + (b - a) * u for a, b in zip(v0, v1))
        return keys[-1][1]

    def eval(self, t):
        return ({b: self._eval(k, t) for b, k in self.r.items()}, {b: self._eval(k, t) for b, k in self.l.items()})


# ================================================================ secondary motion (springs on cloth / hair)
class Spring:
    def __init__(self, hz, zeta):
        self.w, self.z, self.x, self.v = TAU * hz, zeta, 0.0, 0.0

    def step(self, target, dt, sub=4):
        h = dt / sub
        for _ in range(sub):
            a = self.w * self.w * (target - self.x) - 2 * self.z * self.w * self.v
            self.v += a * h
            self.x += self.v * h
        return self.x


CHAINS = {   # group: (bones by depth, spring hz, damping, pitch gain fwd, pitch gain down, roll gain side, clamp)
    "Cape": ([[f"Cape_{c}_{i}" for c in "LCR"] for i in range(1, 5)], 1.5, 0.42, 30.0, 22.0, 20.0, (-10, 22)),
    "Mane": ([[f"Mane_{l}_{k}" for l in range(1, 7)] for k in range(1, 4)], 2.1, 0.40, 26.0, 20.0, 16.0, (-18, 38)),
    "Sash": ([[f"Sash_{s}_1" for s in "LR"], [f"Sash_{s}_2" for s in "LR"], [f"Sash_{s}_Tassel" for s in "LR"]], 2.6, 0.32, -30.0, 16.0, 18.0, (-35, 25)),
}


# ================================================================ bake
def bake(god, ring, spec, hitstop=True):
    """spec: T, tracks (Tracks), life (idle drift kept on keyed body bones), hits [(t, drum, strength)],
    hitstops [(t, dur)], chain_tracks (Tracks with '@Cape'/'@Mane'/'@Sash' pitch/roll adds),
    drum_fn(d, t, root_loc) -> (loc, rot) override or None, ring_tracks (Tracks for ring bones)."""
    T = spec["T"]
    holds = sorted(spec.get("hitstops", [])) if hitstop else []
    total = T + sum(d for _, d in holds)
    n = int(round(total * FPS))
    life = spec.get("life", 0.5)
    tracks, ctr, rtr = spec["tracks"], spec.get("chain_tracks", Tracks()), spec.get("ring_tracks", Tracks())
    springs = {g: (Spring(c[1], c[2]), Spring(c[1], c[2])) for g, c in CHAINS.items()}
    head_p, head_r = Spring(2.4, 0.33), Spring(2.4, 0.33)    # head reacts to the body's motion (bob, lag, settle)
    head_off = (0.0, 0.0)
    hist = {g: [] for g in CHAINS}
    prev_root, prev_lean = None, None

    def warp(tr):                      # real time -> authored time (hit-stops freeze authored time)
        acc = 0.0
        for t0, d in holds:
            if tr < t0 + acc:
                break
            if tr < t0 + acc + d:
                return t0, True
            acc += d
        return tr - acc, False

    for f in range(n + 1):
        tr = f / FPS
        t, frozen = warp(tr)
        gr, gl, rr, rl = (dict(x) for x in idle_pose(t % IDLE_T))
        idle0 = STANCE[0]
        kr, kl = tracks.eval(t)
        if spec.get("overlap", True):                         # successive breaking of joints (follow-through)
            for b in kr:
                d = overlap_delay(b)
                if d:
                    kr[b] = Tracks._eval(tracks.r[b], max(0.0, t - d))
        for b, v in kr.items():                                  # keyed bones keep a little idle drift (no stiffness)
            drift = [life * (a - c) for a, c in zip(gr.get(b, (0, 0, 0)), idle0.get(b, (0, 0, 0)))] if "Cape" not in b else [0, 0, 0]
            if any(fn in b for fn in FINGER_NAMES + ("Thumb",)):
                drift = [0.12 * d for d in drift]
            gr[b] = tuple(x + d for x, d in zip(v, drift))
        for b, v in kl.items():
            idle_l, idle0_l = gl.get(b, (0, 0, 0)), STANCE[1].get(b, (0, 0, 0))
            gl[b] = tuple(x + life * 1.4 * (a - c) for x, a, c in zip(v, idle_l, idle0_l))   # breathing / bob keeps going
        # secondary motion: springs driven by the root's velocity and the chest's lean speed
        root = Vector(gl.get("HumanoidRootPart", (0, 0, 0)))
        lean = gr.get("UpperTorso", (0, 0, 0))[0] + gr.get("LowerTorso", (0, 0, 0))[0]
        if prev_root is None:
            vel, lean_v = Vector((0, 0, 0)), 0.0
        else:
            vel, lean_v = (root - prev_root) * FPS, (lean - prev_lean) * FPS
        if not frozen:
            prev_root, prev_lean = root.copy(), lean
        cadd = ctr.eval(t)[0] if ctr.r else {}
        for g, (bones, hz, zeta, k_fwd, k_down, k_side, (lo, hi)) in (CHAINS.items() if spec.get("springs", True) else ()):
            target_p = k_fwd * (-vel.y) + k_down * (-vel.z) + 0.25 * lean_v
            target_r = k_side * vel.x
            sp, sr = springs[g]
            if not frozen:
                hist[g].append((sp.step(max(lo, min(hi, target_p)), 1 / FPS), sr.step(max(-30, min(30, target_r)), 1 / FPS)))
            elif not hist[g]:
                hist[g].append((0.0, 0.0))
            add = cadd.get("@" + g, (0, 0, 0))
            for depth, row in enumerate(bones):
                lag = min(len(hist[g]) - 1, depth * 2)            # deeper bones follow 2 frames later each
                p, r = hist[g][-1 - lag]
                # offsets compound down the chain, so per-bone gains stay small (4 cape bones sum to ~1.8x)
                gain = 0.32 + 0.08 * depth
                for bn in row:
                    x0, y0, z0 = gr[bn]
                    gr[bn] = (x0 + p * gain + add[0] * 0.3, y0 + r * gain + add[1] * 0.3, z0)
        if spec.get("springs", True):
            # head: lags behind lunges and rises and settles with a little overshoot, tilts with sideways motion
            if not frozen:
                tp = 15.0 * vel.z - 12.0 * (-vel.y) - 0.12 * lean_v
                head_off = (head_p.step(max(-10.0, min(10.0, tp)), 1 / FPS), head_r.step(max(-8.0, min(8.0, 15.0 * vel.x)), 1 / FPS))
            hx, hy, hz = gr["Head"]
            gr["Head"] = (hx + head_off[0], hy + head_off[1], hz)
            # moving holds: a small smooth drift that never repeats, so no pose freezes between keys
            env = min(1.0, t / 0.15, max(0.0, (T - t) / 0.15))
            for b in kr:
                amp = alive_amp(b)
                if amp:
                    gr[b] = tuple(v + env * a * alive_noise(b, t, axis) for axis, (v, a) in enumerate(zip(gr[b], amp)))
        # drums: idle bob + hit recoil (+ overrides)
        kr2, kl2 = rtr.eval(t) if (rtr.r or rtr.l) else ({}, {})
        rr.update(kr2)
        rl.update(kl2)
        for (th, d, strength) in spec.get("hits", []):
            dt = t - th
            if dt < 0 or dt > 1.2:
                continue
            env = math.exp(-dt * 7.0)
            att = min(1.0, dt * FPS / 1.0)
            push = 0.05 * strength * att * env * math.cos(TAU * 6.5 * dt)
            x, y, z = rl[f"Drum_{d}"]
            rl[f"Drum_{d}"] = (x, y + push, z)
            a, b2, c = rr[f"Drum_{d}"]
            rr[f"Drum_{d}"] = (a + 14 * strength * att * env * math.sin(TAU * 6.5 * dt), b2, c)
            a, b2, c = rr[f"Tassel_{d}"]
            rr[f"Tassel_{d}"] = (a - 30 * strength * math.exp(-dt * 4) * math.sin(TAU * 2.8 * dt), b2, c)
        if spec.get("drum_fn"):
            for d in range(1, 9):
                o = spec["drum_fn"](d, t, root, rl.get("Root", (0, 0, 0)))
                if o:
                    rl[f"Drum_{d}"], rr[f"Drum_{d}"] = o
        apply_pose(god, gr, gl)
        apply_pose(ring, rr, rl)
        bpy.context.view_layer.update()
        key_all(god, f + 1)
        key_all(ring, f + 1)
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, n + 1
    return n


ALIVE = {"Head": (2.5, 2.0, 3.2), "UpperTorso": (1.2, 1.0, 1.6), "LowerTorso": (0.5, 0.4, 0.8),
         "UpperArm": (1.6, 2.0, 2.4), "LowerArm": (2.0, 0.0, 3.0), "Hand": (0.0, 3.0, 2.0),
         "UpperLeg": (1.5, 0.0, 0.8), "LowerLeg": (2.5, 0.0, 0.0), "Foot": (2.5, 0.0, 0.0)}


def alive_amp(b):
    if any(fn in b for fn in FINGER_NAMES + ("Thumb",)):
        return None
    for k, a in ALIVE.items():
        if b.endswith(k):
            return a
    return None


def alive_noise(b, t, axis):
    """Smooth, non-repeating drift in [-1, 1]: three incommensurate sines with phases hashed from the bone."""
    h = sum(ord(c) * (i + 1) for i, c in enumerate(b)) + axis * 97
    return (0.55 * math.sin(TAU * 0.37 * t + h % 6.28) + 0.3 * math.sin(TAU * 0.71 * t + (h * 3) % 6.28)
            + 0.15 * math.sin(TAU * 1.13 * t + (h * 7) % 6.28))


def overlap_delay(b):
    """Seconds a bone trails the keys: hips lead, chest on time, head after the chest, each arm joint after the
    one above, fingers last; knees and feet after the thigh. Small on the arm so strikes still land on the hit."""
    if b == "LowerTorso":
        return 0.0
    if b == "Head":
        return -0.03                      # the eyes lead: the head turns to where the action goes a beat early
    for part, d in (("UpperArm", 0.0), ("LowerArm", 0.02), ("Hand", 0.035), ("Thumb", 0.06), ("Index", 0.05),
                    ("Middle", 0.055), ("Ring", 0.06), ("Pinky", 0.065), ("LowerLeg", 0.04), ("Foot", 0.07)):
        if part in b:
            return d
    return 0.0


def apply_pose(arm_ob, rots, locs):
    reset(arm_ob)
    for b, v in rots.items():
        if b in arm_ob.pose.bones:
            rot(arm_ob, b, *v)
    for b, v in locs.items():
        if b in arm_ob.pose.bones:
            loc(arm_ob, b, v)


def stance_key(tr, t, ease="inout", bones=None):
    """Key the idle stance (frame 0) at t for the given bones (default: every keyed bone so far)."""
    gr, gl = STANCE[0], STANCE[1]
    bones = bones if bones is not None else list(tr.r.keys())
    tr.key(t, {b: gr[b] for b in bones if b in gr}, {b: gl[b] for b in tr.l if b in gl}, ease)


# ================================================================ clips
def S(*bones):
    """Stance values for the named bones (rots)."""
    return {b: STANCE[0][b] for b in bones}


ARM_BONES = lambda side: [f"{side}UpperArm", f"{side}LowerArm", f"{side}Hand"]
LEG_BONES = lambda side: [f"{side}UpperLeg", f"{side}LowerLeg", f"{side}Foot"]
HAND_BONES = lambda side: [f"{side}{fn}{k}" for fn in FINGER_NAMES + ("Thumb",) for k in (1, 2, 3)]
BODY = ["UpperTorso", "LowerTorso", "Head"] + ARM_BONES("Left") + ARM_BONES("Right") + LEG_BONES("Left") + LEG_BONES("Right")
ALL = BODY + HAND_BONES("Left") + HAND_BONES("Right")
ROOT0 = STANCE[1]["HumanoidRootPart"]


def root(dx=0.0, dy=0.0, dz=0.0):
    return {"HumanoidRootPart": (ROOT0[0] + dx, ROOT0[1] + dy, ROOT0[2] + dz)}


def start(tr):
    tr.key(0.0, S(*ALL), root())


def finish(tr, t):
    tr.key(t, S(*ALL), root(), "inout")


def idle_clip():
    """God-mode idle: static crawls over the arms now and then, a spark at a fist, faint storm grade."""
    arms = ["LeftUpperArm", "LeftLowerArm", "LeftHand", "RightUpperArm", "RightLowerArm", "RightHand"]
    vfx = [grade([(0, 0.25, 0.85, "#2a3350"), (IDLE_T, 0.25, 0.85, "#2a3350")]),
           arcs(0.25, arms[:3], life=0.28, count=2, radius=0.07, seed=1), arcs(1.15, arms[3:], life=0.24, count=2, radius=0.07, seed=2),
           arcs(1.9, ["UpperTorso"], life=0.2, count=2, radius=0.12, seed=3), arcs(2.55, arms, life=0.3, count=3, radius=0.07, seed=4),
           sprite(0.7, Bn("RightMiddle1"), "static_sparks", life=0.3, layered=False, size=((0, 0.15), (1, 0.35)), palette="spark"),
           sprite(2.2, Bn("LeftMiddle1"), "static_sparks", life=0.3, layered=False, size=((0, 0.15), (1, 0.35)), palette="spark")]
    for d, tt in ((2, 0.5), (7, 1.6), (4, 2.8)):
        vfx.append(sprite(tt, Bn(f"Drum_{d}", (0, -0.15, 0)), "static_sparks", life=0.25, layered=False, size=((0, 0.15), (1, 0.4)), palette="spark"))
    return {"T": IDLE_T, "tracks": Tracks(), "springs": False, "vfx": vfx}


# ================================================================ VFX events (played by lab/page/anim_vfx.js)
# Positions are god space (Blender Z-up, forward = -Y, ground at z = GROUND). An anchor is either a point
# [x, y, z] or {"bone": name, "off": [x, y, z]} (follows the animated bone). Times are clip time (before
# hit-stops); keys are [[u, value], ...] over the effect's life (u = 0..1).
GROUND = -0.95


def P(x, y, z):
    return [float(x), float(y), float(z)]


def Bn(bone, off=(0, 0, 0)):
    return {"bone": bone, "off": [float(v) for v in off]}


def fx(kind, t, **kw):
    d = {"type": kind, "t": float(t)}
    d.update(kw)
    return d


def bolt(t, frm, to, life=0.22, width=0.05, seg=9, kink=0.22, branches=2, seed=1, strands=1, palette="thunder"):
    return fx("bolt", t, life=life, **{"from": frm, "to": to}, width=width, seg=seg, kink=kink, branches=branches,
              seed=seed, strands=strands, palette=palette)


def sprite(t, at, tex, life=0.3, size=((0, 0.5), (1, 0.8)), alpha=((0, 1), (0.6, 1), (1, 0)), grid=4, layered=True,
           palette="thunder", rot=0.0, spin=0.0, move=None, blend="add", inner=1.0):
    return fx("sprite", t, at=at, tex=tex, life=life, size=[list(k) for k in size], alpha=[list(k) for k in alpha],
              grid=grid, layered=layered, palette=palette, rot=rot, spin=spin, move=move, blend=blend, inner=inner)


def decal(t, at, size=2.0, life=2.0, tex="lichtenberg", grow=0.12, scorch=True):
    return fx("decal", t, at=at, tex=tex, life=life, size=size, grow=grow, scorch=scorch)


def ring(t, at, size=((0, 0.2), (1, 3.0)), life=0.45, orient="ground", alpha=((0, 1), (1, 0)), palette="thunder"):
    return fx("ring", t, at=at, size=[list(k) for k in size], life=life, orient=orient, alpha=[list(k) for k in alpha], palette=palette)


def beam(t, at, height=6.0, radius=((0, 0.5), (1, 0.5)), life=0.4, alpha=((0, 1), (0.7, 1), (1, 0)), speed=6.0, tex="thunder_strip_1"):
    return fx("beam", t, at=at, height=height, radius=[list(k) for k in radius], life=life, alpha=[list(k) for k in alpha], speed=speed, tex=tex)


def arcs(t, bones, life=0.4, count=3, radius=0.12, width=0.012, seed=3):
    return fx("arcs", t, bones=bones, life=life, count=count, radius=radius, width=width, seed=seed)


def light(t, at, life=0.4, intensity=((0, 6), (1, 0)), color="#6fe0ff", rng=6.0):
    return fx("light", t, at=at, life=life, intensity=[list(k) for k in intensity], color=color, range=rng)


def flash(t, life=0.2, alpha=((0, 0.8), (1, 0)), color="#ffffff"):
    return fx("flash", t, life=life, alpha=[list(k) for k in alpha], color=color)


def impact(t, frames=2, mode="invert"):
    return fx("impact", t, frames=frames, mode=mode)


def shake(t, amp=0.3, dur=0.4):
    return fx("shake", t, amp=amp, dur=dur)


def grade(keys):
    """keys: [(t, darkness 0..1, saturation 0..1, tint)] background storm grade."""
    return fx("grade", 0.0, keys=[[float(a), float(b), float(c), d] for a, b, c, d in keys])


def letterbox(t0, t1):
    return fx("letterbox", t0, t1=t1)


def sky(t, at, life, size=8.0, spin=12.0, alpha=((0, 0), (0.15, 0.95), (0.85, 0.95), (1, 0))):
    return fx("sky", t, at=at, life=life, size=size, spin=spin, alpha=[list(k) for k in alpha])


def eye(t, at, life, size=2.2, open_keys=((0, 0), (0.25, 1), (0.8, 1), (0.88, 0.05), (0.93, 1), (1, 0))):
    return fx("eye", t, at=at, life=life, size=size, open=[list(k) for k in open_keys])


def pillar(t, x, y, seed, big=False):
    """One sky-to-ground lightning pillar with its ground hit (strands + beam + scar + burst + light)."""
    top, bot = P(x, y, 4.6), P(x, y, GROUND)
    w = 0.11 if big else 0.05
    out = [bolt(t, top, bot, life=0.32 if big else 0.22, width=w, seg=12, kink=0.18, branches=4 if big else 2, seed=seed, strands=5 if big else 3),
           beam(t, P(x, y, GROUND), height=5.6, radius=((0, 0.8 if big else 0.2), (1, 0.1 if big else 0.05)), life=0.5 if big else 0.3),
           sprite(t, P(x, y, GROUND + 0.35), "thunder_burst", life=0.35, size=((0, 1.0 if big else 0.5), (1, 3.8 if big else 1.5))),
           decal(t, P(x, y, GROUND), size=6.0 if big else 1.5, life=3.0 if big else 1.8),
           light(t, P(x, y, GROUND + 0.6), life=0.45, intensity=((0, 14 if big else 5), (1, 0)), rng=10 if big else 4)]
    return out


# ================================================================ clips (polished)
def cast():
    """Palm thrust. A small dip first (anticipation of the anticipation), then the wind-up coils the whole body:
    chest turns away, the right hand cocks back by the ear palm-forward, the left hand reaches toward the target,
    a knee lifts. Snap release: the chest whips round, the right palm drives forward, the left fist pulls back
    to the hip (counter-motion), the back leg kicks. Hit-stop, overshoot, recoil, settle."""
    tr = Tracks()
    start(tr)
    tr.key(0.10, merge(torso(6, 2, -6, 3), head(2, 0, 3), arm("Right", 56, 28, roll=10, elbow=40), arm("Left", 58, 28, elbow=36)),
           root(0, 0.01, -0.03), "inout")
    tr.key(0.34, merge(torso(-6, 5, -30, -2), head(-2, -3, 22),
                       arm("Right", 18, -50, roll=-30, elbow=105, twist=-15, wflex=-35),
                       arm("Left", 40, 68, roll=12, elbow=32, wflex=-12, wside=-5),
                       hand("Right", "claw"), hand("Left", "open"),
                       leg("Left", 18, 32, 18, 3), leg("Right", 26, 62, 22, 4)), root(0, 0.05, 0.04), "inout")
    tr.key(0.38, merge(arm("Right", 15, 30, roll=-18, elbow=72, twist=-6, wflex=-48)), None, "in")
    tr.key(0.43, merge(torso(9, -4, 28, 4), head(3, 2, -12),
                       arm("Right", 8, 88, roll=0, elbow=12, twist=6, wflex=-62),
                       arm("Left", 72, -18, roll=-10, elbow=78, wflex=10),
                       hand("Right", "spread"), hand("Left", "fist"),
                       leg("Left", 22, 40, 20, 3), leg("Right", -16, 24, 30, 3)), root(0, -0.08, 0.0), "lin")
    tr.key(0.56, merge(torso(12, -5, 34, 5), arm("Right", 3, 95, elbow=0, wflex=-74)), root(0, -0.10, 0.005), "out")
    tr.key(0.72, merge(torso(7, -2, 20, 2), arm("Right", 22, 80, elbow=22, wflex=-40)), root(0, -0.07, 0), "inout")
    tr.key(1.0, merge(torso(2, 0, 6, 1), head(2, 0, -2), arm("Right", 55, 45, roll=6, elbow=40, wflex=-5),
                      arm("Left", 70, 15, elbow=40), hand("Right", "relaxed"), hand("Left", "relaxed")), root(0, -0.03, 0), "inout")
    finish(tr, 1.35)
    hand_pt, tgt = Bn("RightMiddle1", (0, -0.04, 0)), P(0.3, -5.6, 0.1)
    vfx = [grade([(0, 0.0, 1.0, "#000000"), (0.3, 0.25, 0.8, "#2a3350"), (0.9, 0.15, 0.9, "#2a3350"), (1.35, 0.0, 1.0, "#000000")]),
           arcs(0.10, ["RightUpperArm", "RightLowerArm", "RightHand"], life=0.33, count=3, radius=0.07, seed=11),
           sprite(0.12, hand_pt, "plasma_orb", life=0.31, size=((0, 0.05), (0.7, 0.32), (0.88, 0.18), (1, 0.26)), alpha=((0, 0.2), (0.3, 1), (1, 1))),
           light(0.12, hand_pt, life=0.31, intensity=((0, 0), (1, 4))),
           sprite(0.43, hand_pt, "thunder_burst", life=0.32, size=((0, 0.4), (1, 1.1))),
           sprite(0.43, hand_pt, "star_flash", life=0.16, size=((0, 0.5), (1, 1.2))),
           bolt(0.43, hand_pt, tgt, life=0.38, width=0.07, seg=11, kink=0.2, branches=3, seed=21, strands=2),
           light(0.43, hand_pt, life=0.3, intensity=((0, 10), (1, 0))),
           sprite(0.43, tgt, "thunder_burst", life=0.4, size=((0, 0.6), (1, 1.8))),
           decal(0.44, P(0.3, -5.6, GROUND), size=2.2, life=2.2),
           light(0.43, tgt, life=0.45, intensity=((0, 8), (1, 0)), rng=7),
           shake(0.43, amp=0.12, dur=0.25)]
    return {"T": 1.35, "tracks": tr, "hitstops": [(0.43, 0.07)], "hits": [(0.43, 2, 0.6), (0.43, 3, 0.6)], "vfx": vfx}


def drum_barrage():
    """Eight hammer-fist strikes on a 0.12 s beat. Each fist cocks back above the head and slams down-forward
    while the chest crunches and twists into it and the head nods with the hit; the other fist is already
    cocking. Drum k fires a bolt at its own target on beat k. The 8th strike is both fists from overhead with a
    hit-stop; the arms rebound and the hands shake out."""
    tr = Tracks()
    start(tr)
    cock = lambda side: arm(side, -45, 40, roll=-8, elbow=96, twist=-8, wflex=22)
    strike = lambda side: arm(side, 22, 76, roll=4, elbow=30, wflex=-4)          # ends out in front of the chest, clear of the belly
    tr.key(0.12, merge(torso(5, 0, 0, 2), head(3), arm("Left", 62, 40, elbow=55), arm("Right", 62, 40, elbow=55),
                       hand("Left", "fist"), hand("Right", "fist")), root(0, 0, -0.02), "inout")
    tr.key(0.26, merge(torso(-12, 0, -10, -3), head(-8, 0, 6), cock("Right"), arm("Left", 30, 50, elbow=90, wflex=10),
                       leg("Left", 26, 56, 20, 3), leg("Right", 12, 42, 25, 3)), root(0, 0.03, 0.07), "inout")
    beats = [0.30 + 0.12 * k for k in range(8)]
    hits, vfx = [], [grade([(0, 0, 1, "#000000"), (0.25, 0.35, 0.75, "#2a3350"), (1.5, 0.3, 0.8, "#2a3350"), (1.8, 0, 1, "#000000")]),
                     arcs(0.26, ["RightHand", "LeftHand", "RightLowerArm", "LeftLowerArm"], life=1.0, count=3, radius=0.08, seed=5)]
    for k, tb in enumerate(beats[:7]):
        side = "Right" if k % 2 == 0 else "Left"
        other = "Left" if side == "Right" else "Right"
        tr.key(tb - 0.09, cock(side), None, "out")
        tr.key(tb, strike(side), None, "strike")
        tr.key(tb, cock(other) if k < 6 else arm(other, -70, 28, elbow=60, wflex=20), None, "out")
        tw = -16 if side == "Right" else 16
        tr.key(tb, merge(torso(10, 8 if side == "Right" else -8, tw, 3), head(10, 0, tw * 0.6)), root(0, -0.01, 0.045), "snap")
        tr.key(tb + 0.07, merge(torso(-3, 0, tw * 0.25, 0), head(-3, 0, 0)), root(0, 0.01, 0.065), "out")
    tr.key(beats[6] + 0.08, merge(arm("Left", -72, 26, elbow=58, wflex=22), arm("Right", -72, 26, elbow=58, wflex=22), torso(-14, 0, 0, -3), head(-8)),
           root(0, 0.02, 0.08), "out")
    tb = beats[7]
    tr.key(tb, merge(arm("Left", 34, 68, elbow=22, wflex=-6), arm("Right", 34, 68, elbow=22, wflex=-6), torso(18, 0, 0, 5), head(-2)),
           root(0, -0.03, 0.02), "strike")
    tr.key(1.30, merge(arm("Left", 15, 55, elbow=40, wflex=15), arm("Right", 18, 58, elbow=36, wflex=15), torso(4), head(2)), root(0, 0, 0.05), "out")
    for i, tt in enumerate((1.38, 1.44, 1.50)):
        j = 1 if i % 2 == 0 else -1
        tr.key(tt, merge(arm("Left", 55, 40, elbow=40, wflex=10 + 12 * j), arm("Right", 55, 40, elbow=40, wflex=10 - 12 * j),
                         hand("Left", "relaxed"), hand("Right", "relaxed")), None, "inout")
    finish(tr, 1.9)
    for k, tb in enumerate(beats):
        d = k + 1
        tx, ty = -2.1 + 0.6 * k, -3.6 - 0.5 * (k % 2)
        last = k == 7
        hits.append((tb, d, 1.4 if last else 1.0))
        vfx += [sprite(tb, Bn(f"Drum_{d}", (0, -0.15, 0)), "thunder_burst", life=0.22, size=((0, 0.3), (1, 0.75))),
                ring(tb, Bn(f"Drum_{d}", (0, -0.14, 0)), size=((0, 0.2), (1, 0.9)), life=0.25, orient="face"),
                bolt(tb, Bn(f"Drum_{d}", (0, -0.16, 0)), P(tx, ty, GROUND), life=0.26, width=0.045, seg=10, branches=2, seed=40 + k),
                decal(tb + 0.01, P(tx, ty, GROUND), size=1.1, life=1.5),
                sprite(tb, P(tx, ty, GROUND + 0.2), "thunder_burst", life=0.25, size=((0, 0.3), (1, 0.9))),
                light(tb, P(tx, ty, GROUND + 0.5), life=0.25, intensity=((0, 4), (1, 0)), rng=4)]
    tb = beats[7]
    vfx += [bolt(tb, Bn(f"Drum_{d}", (0, -0.16, 0)), P(0, -4.2, GROUND), life=0.35, width=0.03, seed=80 + d) for d in range(1, 8)]
    vfx += [sprite(tb, P(0, -4.2, GROUND + 0.4), "thunder_burst", life=0.45, size=((0, 1.0), (1, 3.2))),
            ring(tb, P(0, -4.2, GROUND + 0.02), size=((0, 0.4), (1, 5.0)), life=0.55),
            decal(tb, P(0, -4.2, GROUND), size=4.0, life=2.4), impact(tb), shake(tb, amp=0.45, dur=0.4),
            flash(tb, life=0.18, alpha=((0, 0.45), (1, 0))), light(tb, P(0, -4.2, GROUND + 0.8), life=0.5, intensity=((0, 16), (1, 0)), rng=10)]
    return {"T": 1.9, "tracks": tr, "hitstops": [(beats[-1], 0.08)], "hits": hits, "life": 0.4, "vfx": vfx}


def heavens_palm():
    """Gather: the body curls and the right hand draws across the belly. The arm sweeps out and up in an arc to
    the sky, palm forward, while the chest arches and bends away, the head follows the hand and a knee lifts.
    A trembling hold, fingers claw; the arm cocks back a touch (last anticipation), then sweeps over and down
    in an arc to press the palm at the ground ahead, the chest crunches and twists into it, the left arm flings
    back. Hit-stop, overshoot, recoil, settle."""
    tr = Tracks()
    start(tr)
    tr.key(0.16, merge(torso(7, -2, 8, 3), head(4, 0, 4), arm("Right", 44, 62, roll=20, elbow=30, twist=-30, wflex=12),
                       arm("Left", 66, 30, elbow=58), hand("Right", "relaxed")), root(0, 0.01, -0.03), "inout")
    tr.key(0.38, merge(torso(-6, 6, -6, -1), head(-8, 0, -8), arm("Right", -10, 32, roll=40, elbow=30, wflex=-10), hand("Right", "open")),
           root(0, 0.01, 0.06), "inout")
    tr.key(0.56, merge(torso(-16, 10, -12, -4), head(-22, -4, -10), arm("Right", -82, 12, roll=80, elbow=6, wflex=-15),
                       arm("Left", 58, -18, roll=-8, elbow=42, wflex=8), hand("Right", "spread"), hand("Left", "open"),
                       leg("Left", 6, 26, 26, 3), leg("Right", 26, 56, 22, 4)), root(0, 0.02, 0.14), "out")
    for i, tt in enumerate((0.60, 0.63, 0.66, 0.69, 0.72)):
        j = i % 2
        tr.key(tt, merge(arm("Right", -84 + 4 * j, 12 + 2 * j, roll=80, elbow=6, wflex=-15), torso(-16 - j, 10, -12, -4)),
               root(0, 0.02, 0.142 + 0.004 * j), "lin")
    tr.key(0.74, hand("Right", "claw"), None, "inout")
    tr.key(0.78, merge(arm("Right", -88, -6, roll=80, elbow=10, wflex=-20), torso(-21, 10, -14, -5), head(-24, -4, -10)), root(0, 0.03, 0.15), "out")
    tr.key(0.82, merge(arm("Right", -28, 70, roll=40, elbow=10, wflex=-45), hand("Right", "spread")), None, "in")
    tr.key(0.86, merge(torso(14, -6, 16, 3), head(-4, 0, 4), arm("Right", 38, 82, roll=10, elbow=4, wflex=-64),
                       arm("Left", 48, -44, roll=-10, elbow=24, wflex=10), leg("Left", 30, 60, 15, 3), leg("Right", -15, 15, 30, 3)),
           root(0, -0.06, -0.05), "in")
    tr.key(1.02, merge(torso(18, -6, 18, 4), head(-2, 0, 4), arm("Right", 46, 80, elbow=4, wflex=-66)), root(0, -0.07, -0.07), "out")
    tr.key(1.12, head(10, 0, 6), None, "out")                     # looks down at the impact...
    tr.key(1.22, merge(torso(10, -3, 10, 2), arm("Right", 40, 72, elbow=20, wflex=-50)), root(0, -0.05, -0.04), "inout")
    tr.key(1.40, head(-4, 2, 0), None, "inout")                    # ...then lifts his chin
    tr.key(1.45, merge(torso(4, 0, 4, 1), arm("Right", 62, 40, roll=10, elbow=35, wflex=-10), arm("Left", 68, 15, elbow=35),
                       hand("Right", "relaxed"), hand("Left", "relaxed")), root(0, -0.02, 0), "inout")
    finish(tr, 1.95)
    tgt = P(0, -4.0, GROUND)
    vfx = [grade([(0, 0, 1, "#000000"), (0.55, 0.75, 0.55, "#2a3350"), (1.2, 0.45, 0.7, "#2a3350"), (1.95, 0.1, 1, "#000000")]),
           sky(0.15, P(0, -3.0, 3.3), life=1.6, size=8.0, spin=10),
           arcs(0.50, ["RightUpperArm", "RightLowerArm", "RightHand"], life=0.36, count=3, radius=0.08, seed=17),
           sprite(0.58, Bn("RightMiddle1"), "static_sparks", life=0.28, layered=False, size=((0, 0.3), (1, 0.6)), palette="spark"),
           bolt(0.62, P(0.4, -2.6, 4.2), Bn("RightMiddle1"), life=0.12, width=0.03, seed=61),
           bolt(0.70, P(-0.5, -2.8, 4.2), Bn("RightMiddle1"), life=0.12, width=0.03, seed=62),
           light(0.56, Bn("RightMiddle1"), life=0.3, intensity=((0, 0), (1, 5))),
           sprite(0.76, P(0, -4.0, 3.4), "palm_strike", life=0.34, grid=1, size=((0, 2.4), (0.3, 2.8), (1, 3.0)),
                  alpha=((0, 0.0), (0.1, 1), (0.35, 0.9), (1, 0)), move={"to": P(0, -4.0, 0.5), "dur": 0.10, "ease": "in"}, inner=0.3),
           impact(0.86), shake(0.86, amp=0.7, dur=0.5), flash(0.86, life=0.22, alpha=((0, 0.65), (1, 0))),
           ring(0.86, P(0, -4.0, GROUND + 0.02), size=((0, 0.6), (1, 7.0)), life=0.6),
           ring(0.89, P(0, -4.0, GROUND + 0.03), size=((0, 0.4), (1, 4.5)), life=0.5),
           decal(0.86, tgt, size=5.0, life=2.8),
           sprite(0.86, P(0, -4.0, GROUND + 0.5), "thunder_burst", life=0.4, size=((0, 1.0), (1, 2.6))),
           sprite(0.86, P(0, -4.0, GROUND + 0.3), "dust_burst", life=0.9, layered=False, size=((0, 1.5), (1, 4.5)),
                  alpha=((0, 0.9), (1, 0)), palette="dust", blend="normal"),
           light(0.86, P(0, -4.0, GROUND + 0.8), life=0.6, intensity=((0, 18), (1, 0)), rng=12)]
    for i in range(7):
        a = math.radians(i * 360 / 7 + 15)
        vfx.append(bolt(0.86, P(0, -4.0, GROUND + 0.05), P(2.8 * math.cos(a), -4.0 + 2.8 * math.sin(a), GROUND + 0.05),
                        life=0.3, width=0.02, seg=9, branches=1, seed=70 + i))
    return {"T": 1.95, "tracks": tr, "hitstops": [(0.86, 0.15)], "hits": [(0.86, d, 0.5) for d in range(1, 9)], "vfx": vfx}


def thunder_gods_wrath():
    """Ultimate. Crouch-coil, then rise with the arms opening forward and up, elbows bent, palms up (an offering
    to the storm, not a T). Drum crescendo: arms climb into a fisted V and pump on the accelerating beat. Rain of
    pillars: he conducts, pointing at each target with the index finger while the other fist pulls back to the
    hip and the chest whips toward the target. Wind-up: both fists meet overhead, legs tuck, a hanging moment;
    then both fists drive down for the colossal strike (hit-stop), overshoot, a heaving breath, and he descends."""
    tr = Tracks()
    start(tr)
    tr.key(0.22, merge(torso(10, 0, 0, 4), head(6), arm("Left", 36, 50, roll=-10, elbow=100, wflex=12), arm("Right", 36, 50, roll=-10, elbow=100, wflex=12),
                       hand("Left", "fist"), hand("Right", "fist"), leg("Left", 35, 70, 20, 3), leg("Right", 30, 65, 22, 3)), root(0, 0, -0.04), "inout")
    tr.key(0.85, merge(torso(-16, 0, 4, -4), head(-22, 2, 0),
                       arm("Left", -12, 40, roll=-60, elbow=45, wflex=-22), arm("Right", -20, 36, roll=-60, elbow=40, wflex=-22),
                       hand("Left", "open"), hand("Right", "open"), leg("Left", 4, 18, 32, 3), leg("Right", -4, 12, 34, 3)),
           root(0, 0, 0.55), "inout")
    tr.key(1.30, merge(arm("Left", -60, 26, elbow=26, wflex=10), arm("Right", -60, 26, elbow=26, wflex=10), hand("Left", "fist"), hand("Right", "fist"),
                       torso(-18), head(-24)), root(0, 0, 0.62), "inout")
    hits = []
    t, dt, k = 0.88, 0.2, 0
    while t < 2.0:
        hits.append((t, k % 8 + 1, 0.5 + 0.7 * (t - 0.88) / 1.12))
        if t > 1.32:
            side = "Left" if k % 2 == 0 else "Right"
            tr.key(t, arm(side, -72, 22, elbow=16, wflex=14), None, "snap")
            tr.key(t + min(dt, 0.12) * 0.8, arm(side, -58, 26, elbow=28, wflex=10), None, "out")
        t += dt
        dt = max(0.05, dt * 0.85)
        k += 1
    ready = lambda side: arm(side, 15, 50, elbow=52, wflex=10)
    tr.key(1.98, merge(ready("Left"), ready("Right"), hand("Left", "point"), hand("Right", "point"), torso(-4), head(-4)), None, "out")
    targets = [(-1.6, -3.4), (1.5, -3.8), (-0.6, -4.8), (2.3, -2.6), (-2.4, -2.4), (0.6, -3.0)]
    for i, tp in enumerate((2.05, 2.2, 2.35, 2.5, 2.65, 2.8)):
        x, y = targets[i]
        side = "Right" if x < 0 else "Left"
        other = "Left" if side == "Right" else "Right"
        tw = -24 if side == "Right" else 24
        tr.key(tp - 0.07, ready(side), None, "out")
        tr.key(tp, merge(arm(side, 34, 74, roll=0, elbow=8, wflex=-8, wside=-8), arm(other, 60, -12, elbow=70, wflex=5),
                         hand(other, "fist"), hand(side, "point"),
                         torso(8, 6 if side == "Right" else -6, tw, 2), head(11, 0, tw * 0.85)), None, "snap")
        tr.key(tp + 0.1, merge(ready(side), ready(other), hand(other, "point")), None, "out")
    tr.key(3.05, merge(arm("Left", -80, 22, roll=0, elbow=30, wflex=10), arm("Right", -80, 22, roll=0, elbow=30, wflex=10),
                       hand("Left", "fist"), hand("Right", "fist"), torso(-22), head(-25), leg("Left", 35, 80, 25), leg("Right", 35, 80, 25)),
           root(0, 0.02, 0.70), "out")
    tr.key(3.14, merge(arm("Left", -84, 18, elbow=26), arm("Right", -84, 18, elbow=26), torso(-24), head(-26)), root(0, 0.025, 0.73), "out")
    tr.key(3.25, merge(arm("Left", 42, 76, elbow=8, wflex=-4), arm("Right", 42, 76, elbow=8, wflex=-4), torso(16, 0, 0, 4), head(-4),
                       leg("Left", -20, 20, 30), leg("Right", -20, 20, 30)), root(0, -0.05, 0.35), "in")
    tr.key(3.45, merge(torso(18, 0, 0, 4), head(-2), arm("Left", 48, 80, elbow=10), arm("Right", 48, 80, elbow=10)), root(0, -0.06, 0.32), "out")
    tr.key(3.7, merge(torso(-6), head(-6), arm("Left", 40, 22, elbow=22, wflex=10), arm("Right", 41, 20, elbow=20, wflex=10),
                      hand("Left", "relaxed"), hand("Right", "relaxed")), root(0, -0.03, 0.3), "inout")
    tr.key(3.95, merge(torso(6), head(4), hand("Left", "relaxed"), hand("Right", "relaxed")), root(0, -0.02, 0.2), "inout")
    finish(tr, 4.4)
    hits += [(3.25, d, 1.5) for d in range(1, 9)]
    for i, tp in enumerate((2.05, 2.2, 2.35, 2.5, 2.65, 2.8)):
        hits += [(tp, (2 * i) % 8 + 1, 0.8), (tp, (2 * i + 4) % 8 + 1, 0.8)]
    vfx = [grade([(0, 0, 1, "#000000"), (0.85, 0.85, 0.45, "#2a3350"), (3.2, 0.9, 0.4, "#1a1f35"), (3.6, 0.5, 0.75, "#2a3350"), (4.4, 0.15, 1, "#000000")]),
           letterbox(0.2, 4.2), sky(0.2, P(0, -2.0, 3.4), life=4.1, size=11.0, spin=8),
           arcs(0.3, ["UpperTorso", "LeftUpperArm", "RightUpperArm", "LeftLowerArm", "RightLowerArm", "LeftHand", "RightHand"], life=1.75, count=5, radius=0.1, seed=31)]
    for (th, d, st) in hits:
        if th < 2.0:
            vfx += [sprite(th, Bn(f"Drum_{d}", (0, -0.15, 0)), "thunder_burst", life=0.2, size=((0, 0.25), (1, 0.6 + 0.3 * st))),
                    bolt(th, Bn(f"Drum_{d}", (0, 0, 0.1)), P((d - 4.5) * 0.9, 0.5, 4.6), life=0.14, width=0.03, seed=100 + int(th * 100))]
    rng_targets = [(-3.0, -1.0), (2.9, -1.5), (-1.2, -5.6), (1.0, -6.0), (3.4, -4.2), (-3.6, -4.0), (0.2, -2.2), (-2.2, -5.0),
                   (2.0, -5.2), (-0.4, -6.6), (3.8, -2.8), (-3.9, -2.2), (1.6, -1.2), (-1.8, -1.4)]
    for i, (x, y) in enumerate(targets):
        vfx += pillar((2.05, 2.2, 2.35, 2.5, 2.65, 2.8)[i] + 0.01, x, y, 200 + i)
    for i, (x, y) in enumerate(rng_targets):
        vfx += pillar(2.08 + i * 0.065, x, y, 300 + i)
    vfx += pillar(3.25, 0, -4.0, 400, big=True)
    vfx += [impact(3.25), shake(3.25, amp=1.0, dur=0.7), flash(3.25, life=0.3, alpha=((0, 0.85), (1, 0))),
            ring(3.25, P(0, -4.0, GROUND + 0.02), size=((0, 0.8), (1, 10.0)), life=0.7),
            ring(3.30, P(0, -4.0, GROUND + 0.03), size=((0, 0.5), (1, 6.5)), life=0.6),
            sprite(3.25, P(0, -4.0, GROUND + 0.3), "dust_burst", life=1.1, layered=False, size=((0, 2.0), (1, 6.5)),
                   alpha=((0, 0.9), (1, 0)), palette="dust", blend="normal")]
    return {"T": 4.4, "tracks": tr, "hitstops": [(3.25, 0.18)], "hits": hits, "life": 0.4, "vfx": vfx}


def transform():
    """Raijin Ascension (approved beat sheet). 0-0.96 curled low inside the strike; 0.96-1.85 the pour: the curled
    body spins once and rises; 1.40 drum forge (8 drums on the ground ring, 0.06 s apart); 1.85 squeeze;
    1.95 BURST into an asymmetric power pose (one arm up and forward, one down and back, chest arched, a knee
    up), slow float while the cape and mane billow and the frame rises in; 2.20 drums fly up on arcs (over his
    head for the front ones) and lock in 0.05 s apart; 2.74 fists gather at the chest; 2.80 FIRST BEAT: arms
    drive down and out (not a T), every drum strikes, hit-stop; settles into the idle."""
    import drum_ring as dr
    tr = Tracks()
    curl = merge(torso(20, 0, 0, 12), head(26), arm("Left", 24, 86, roll=-10, elbow=118, wflex=10), arm("Right", 30, 86, roll=-10, elbow=114, wflex=10),
                 hand("Left", "fist"), hand("Right", "fist"), leg("Left", 62, 108, 30, 6), leg("Right", 62, 108, 30, 6))
    tr.key(0.0, merge(curl, {"LowerTorso": (15, 0, -360)}), root(0, 0, -0.42))
    tr.key(0.96, merge(curl, {"LowerTorso": (15, 0, -360)}), root(0, 0, -0.36), "lin")
    tr.key(1.85, merge(curl, torso(27, 0, 0, 15), {"LowerTorso": (15, 0, 0)}, leg("Left", 66, 112, 30, 8), leg("Right", 66, 112, 30, 8)),
           root(0, 0, -0.2), "inout")
    burst = merge(torso(-20, -4, 8, -6), head(-24, 3, -4),
                  arm("Right", -55, 30, roll=-20, elbow=25, wflex=-30), arm("Left", 30, -25, roll=10, elbow=22, wflex=-20),
                  hand("Left", "spread"), hand("Right", "spread"), leg("Left", -8, 12, 38), leg("Right", 30, 70, 30, 4))
    tr.key(1.95, burst, root(0, 0, 0.40), "lin")
    tr.key(2.62, merge(arm("Right", -64, 28, roll=-24, elbow=22, wflex=-32), arm("Left", 24, -28, roll=12, elbow=20, wflex=-22),
                       head(2, 2, 0), torso(-14, -3, 4, -4)), root(0, 0, 0.46), "out")
    tr.key(2.70, merge(arm("Left", 38, 82, elbow=84, wflex=10), arm("Right", 38, 82, elbow=84, wflex=10), torso(8, 0, 0, 3), head(6),
                       hand("Left", "fist"), hand("Right", "fist"), leg("Left", 24, 50, 20, 3), leg("Right", 20, 45, 22, 3)), root(0, 0, 0.42), "inout")
    tr.key(2.80, merge(arm("Left", 55, 14, roll=8, elbow=12, wflex=-30), arm("Right", 52, 18, roll=8, elbow=14, wflex=-30), torso(-10, 0, 0, -2), head(2),
                       hand("Left", "spread"), hand("Right", "spread"), leg("Left", 10, 30, 25, 3), leg("Right", 0, 18, 28, 3)),
           root(0, 0, 0.36), "snap")
    tr.key(3.0, merge(hand("Left", "relaxed"), hand("Right", "relaxed"), arm("Left", 62, 18, elbow=22), arm("Right", 60, 20, elbow=24)), None, "inout")
    finish(tr, 3.5)
    ctr = Tracks()
    ctr.key(1.95, {"@Cape": (0, 0, 0), "@Mane": (0, 0, 0)})
    ctr.key(2.3, {"@Cape": (34, 0, 0), "@Mane": (30, 0, 0)}, None, "out")
    ctr.key(2.75, {"@Cape": (30, 0, 0), "@Mane": (26, 0, 0)}, None, "inout")
    ctr.key(3.1, {"@Cape": (0, 0, 0), "@Mane": (0, 0, 0)}, None, "inout")
    rtr = Tracks()
    rtr.key(0.0, None, {"Root": (0, 0, -25)})
    rtr.key(2.059, None, {"Root": (0, 0, -25)}, "hold")
    rtr.key(2.06, None, {"Root": (0, 0, -1.4)}, "lin")
    rtr.key(2.2, None, {"Root": (0, 0, 0)}, "out")
    rtr.key(2.8, None, {"Root": (0, 0, 0)}, "lin")
    rtr.key(3.5, None, {"Root": STANCE[3]["Root"]}, "inout")
    hits = [(2.8, d, 1.3) for d in range(1, 9)]
    slots = {d: Vector(dr.arch_pt(dr.DRUM_ANG[d - 1], dr.R, dr.DRUM_Y)) for d in range(1, 9)}
    TA, GAP, FL = 2.20, 0.05, 0.20           # assembly: first launch, stagger, flight time (all locked by 2.75)
    for d in range(1, 9):
        hits.append((TA + GAP * (d - 1) + FL, d, 0.7))

    def ground_of(d):
        th = math.radians(-90 + (d - 1) * 45)
        return th, Vector((2.0 * math.cos(th), 2.0 * math.sin(th), GROUND + 0.19))

    def drum_fn(d, t, root_loc, ring_root):
        tf, ta, fl = 1.40 + 0.06 * (d - 1), TA + GAP * (d - 1), FL
        th, ground = ground_of(d)
        spin = 0.0
        if t < tf:
            world = Vector((0, 0, -30))
        elif t < ta:
            pop = 0.12 * math.exp(-(t - tf) * 9) * math.sin(min(math.pi, (t - tf) * 30))
            world = ground + Vector((0, 0, pop))
        elif t < ta + fl:
            u = (t - ta) / fl
            e = 1 - (1 - u) ** 2
            arc = 0.9 + 0.9 * max(0.0, -math.sin(th))       # drums forged in front arc over his head
            world = ground.lerp(slots[d], e) + Vector((0, 0, arc * math.sin(math.pi * u)))
            spin = 360 * (1 - e)
        else:
            return None
        off = world - slots[d] - root_loc - Vector(ring_root)
        return (tuple(off), (0, 0, spin))

    me = Bn("UpperTorso")
    vfx = [grade([(0, 0.0, 1.0, "#000000"), (0.3, 0.8, 0.15, "#1a1f35"), (1.9, 0.9, 0.1, "#141826"), (2.0, 0.55, 0.6, "#2a3350"),
                  (2.8, 0.6, 0.7, "#203a5a"), (3.5, 0.35, 0.95, "#1d4a66")]),
           letterbox(0.25, 3.25), sky(0.2, P(0, 0, 3.4), life=3.3, size=10.0, spin=30),
           eye(0.30, P(0, 0, 3.2), life=0.62, size=2.4),
           ring(0.45, P(0, 0, GROUND + 0.02), size=((0, 0.2), (1, 3.2)), life=0.4), flash(0.45, life=0.12, alpha=((0, 0.25), (1, 0))),
           ring(0.62, P(0, 0, GROUND + 0.02), size=((0, 0.2), (1, 3.8)), life=0.4), flash(0.62, life=0.12, alpha=((0, 0.3), (1, 0))),
           decal(0.62, P(0, 0, GROUND), size=3.5, life=2.9, grow=0.25),
           arcs(0.55, ["LeftLowerLeg", "RightLowerLeg", "LeftUpperLeg", "RightUpperLeg"], life=0.28, count=4, radius=0.1, seed=7),
           bolt(0.80, P(0, 0, 4.3), P(0, 0, GROUND), life=0.18, width=0.13, seg=12, kink=0.16, branches=4, seed=501, strands=5),
           impact(0.80), shake(0.80, amp=0.9, dur=0.5), flash(0.80, life=0.2, alpha=((0, 0.7), (1, 0))),
           sprite(0.80, me, "thunder_burst", life=0.4, size=((0, 1.0), (1, 3.0))),
           light(0.80, me, life=0.5, intensity=((0, 16), (1, 0)), rng=10),
           beam(0.90, P(0, 0, GROUND), height=6.0, radius=((0, 0.2), (0.1, 0.8), (0.9, 0.85), (1, 0.05)), life=1.07,
                alpha=((0, 0), (0.08, 1), (0.92, 1), (1, 0)), speed=8.0),
           beam(0.90, P(0, 0, GROUND), height=6.0, radius=((0, 0.1), (0.1, 0.38), (0.9, 0.4), (1, 0.02)), life=1.07,
                alpha=((0, 0), (0.08, 1), (0.92, 1), (1, 0)), speed=12.0, tex="thunder_strip_3"),
           arcs(0.96, ["UpperTorso", "LowerTorso", "Head", "LeftUpperArm", "RightUpperArm"], life=0.99, count=5, radius=0.14, seed=9),
           light(0.90, me, life=1.07, intensity=((0, 0), (0.1, 7), (0.9, 7), (1, 0)), rng=8),
           impact(1.95), flash(1.95, life=0.2, alpha=((0, 0.7), (1, 0))), shake(1.95, amp=0.6, dur=0.4),
           sprite(1.95, me, "thunder_burst", life=0.45, size=((0, 1.2), (1, 3.0))),
           ring(1.95, me, size=((0, 0.5), (1, 6.0)), life=0.5, orient="face"),
           light(1.95, me, life=0.6, intensity=((0, 20), (1, 0)), rng=12),
           arcs(2.0, ["LeftHand", "RightHand", "LeftLowerArm", "RightLowerArm"], life=0.8, count=3, radius=0.08, seed=13)]
    for d in range(1, 9):
        tf = 1.40 + 0.06 * (d - 1)
        th, g = ground_of(d)
        gp = P(g.x, g.y, GROUND)
        vfx += [bolt(tf, P(g.x * 1.3, g.y * 1.3, 4.6), gp, life=0.2, width=0.06, seg=11, branches=2, seed=600 + d, strands=2),
                sprite(tf, P(g.x, g.y, GROUND + 0.25), "thunder_burst", life=0.28, size=((0, 0.4), (1, 1.2))),
                ring(tf, P(g.x, g.y, GROUND + 0.02), size=((0, 0.2), (1, 1.4)), life=0.3),
                decal(tf, gp, size=1.2, life=1.6),
                arcs(TA + GAP * (d - 1), [f"Drum_{d}"], life=FL, count=2, radius=0.2, width=0.01, seed=700 + d),
                sprite(TA + GAP * (d - 1) + FL, Bn(f"Drum_{d}"), "star_flash", life=0.2, size=((0, 0.3), (1, 0.75)), palette="gold")]
    vfx += [impact(2.80), shake(2.80, amp=0.8, dur=0.45), flash(2.80, life=0.2, alpha=((0, 0.5), (1, 0))),
            ring(2.80, P(0, 0, GROUND + 0.02), size=((0, 0.5), (1, 10.0)), life=0.75),
            ring(2.86, P(0, 0, GROUND + 0.03), size=((0, 0.4), (1, 6.0)), life=0.6),
            decal(2.80, P(0, 0, GROUND), size=9.0, life=0.7 + 2.0, grow=0.18),
            light(2.80, me, life=0.6, intensity=((0, 14), (1, 0)), rng=12)]
    vfx += [sprite(2.80, Bn(f"Drum_{d}", (0, -0.15, 0)), "thunder_burst", life=0.3, size=((0, 0.35), (1, 1.0))) for d in range(1, 9)]
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        vfx.append(bolt(2.80, P(0, 0, GROUND + 0.05), P(4.6 * math.cos(a), 4.6 * math.sin(a), GROUND + 0.05), life=0.32, width=0.022, branches=2, seed=800 + i))
    for i, tt in enumerate((3.05, 3.22, 3.4)):
        vfx.append(bolt(tt, P(-2 + 2 * i, 1.5, 4.8), P(-2.5 + 2.4 * i, 2.5, 3.2), life=0.12, width=0.03, seed=900 + i))
    return {"T": 3.5, "tracks": tr, "chain_tracks": ctr, "ring_tracks": rtr, "hits": hits, "drum_fn": drum_fn,
            "hitstops": [(2.8, 0.14)], "life": 0.3, "vfx": vfx}


CLIPS = {"idle": idle_clip, "cast": cast, "drum_barrage": drum_barrage, "heavens_palm": heavens_palm,
         "thunder_gods_wrath": thunder_gods_wrath, "transform": transform}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="*", default=["idle"])
    ap.add_argument("--out", default=os.path.join(ROOT, "assets", "meshes", "thunder_god", "anim"))
    ap.add_argument("--no-hitstop", action="store_true", help="export without hit-stop holds (the runtime adds them)")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    os.makedirs(a.out, exist_ok=True)
    for clip in (list(CLIPS) if a.clips == ["all"] else a.clips):
        god, ring = load_scene()
        for arm_ob in (god, ring):
            arm_ob.animation_data_clear()
        spec = CLIPS[clip]()
        n = bake(god, ring, spec, hitstop=not a.no_hitstop)
        for arm_ob in (god, ring):
            if arm_ob.animation_data and arm_ob.animation_data.action:
                arm_ob.animation_data.action.name = f"{clip}_{arm_ob.name}"
        path = os.path.join(a.out, f"{clip}.glb")
        holds = [] if a.no_hitstop else spec.get("hitstops", [])
        with open(os.path.join(a.out, f"{clip}.vfx.json"), "w") as fh:
            json.dump({"clip": clip, "ground": GROUND, "holds": [[float(t0), float(d)] for t0, d in holds],
                       "events": spec.get("vfx", [])}, fh, indent=0)
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_animations=True,
                                  export_animation_mode="SCENE", export_frame_range=True, export_force_sampling=True,
                                  export_skins=True, export_apply=False)
        print(clip, "frames", n, "->", path)


if __name__ == "__main__":
    main()
