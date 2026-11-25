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
    return {"UpperTorso": (lean, side, twist), "LowerTorso": (low, 0, 0)}


def head(nod=0.0, tilt=0.0, turn=0.0):
    return {"Head": (nod, tilt, turn)}


HAND_SHAPES = {   # per finger: (k1, k2, k3 curl), spread; thumb: (k1, k2, k3 curl), thumb in/out
    "relaxed": ({"Index": ((12, 11, 11), -3), "Middle": ((16, 14, 14), 0), "Ring": ((20, 18, 18), 2), "Pinky": ((24, 22, 22), 5)}, ((8, 8, 8), 10)),
    "fist":    ({"Index": ((80, 95, 65), 0), "Middle": ((85, 95, 65), 0), "Ring": ((88, 95, 65), 1), "Pinky": ((90, 95, 65), 2)}, ((25, 35, 30), 38)),
    "open":    ({"Index": ((3, 3, 2), -4), "Middle": ((3, 3, 2), 0), "Ring": ((4, 3, 2), 3), "Pinky": ((5, 4, 3), 6)}, ((2, 2, 2), 2)),
    "spread":  ({"Index": ((-6, 0, 0), -14), "Middle": ((-6, 0, 0), -3), "Ring": ((-5, 0, 0), 7), "Pinky": ((-4, 0, 0), 16)}, ((-4, 0, 0), -22)),
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
    gr["LowerTorso"] = (1.0 * b_lag, 0, 0)
    gr["UpperTorso"] = (-2.0 - 1.4 * b, 0, 0)
    gr["Head"] = (3.0 + 1.0 * b_lag, 0, 0.8 * wave(t, T, 1, 0, 0, 1.3))
    for side, s, ph in (("Left", 1, 0.0), ("Right", -1, 2.1)):
        fore = wave(t, T, 1, 0, 0, ph - 0.9) + 0.3 * wave(t, T, 2, 0, 0, ph * 0.7 - 0.5)
        gr.update(arm(side, 36 + 6.0 * wave(t, T, 1, 0, 0, ph - 0.3), 20 + 10.0 * fore,
                      roll=10.0 * wave(t, T, 1, 0, 0, ph - 1.2),
                      elbow=30 + 22.0 * wave(t, T, 1, 0, 0, ph - 1.7), twist=15.0 * wave(t, T, 1, 0, 0, ph - 2.0),
                      wflex=10 + 14.0 * wave(t, T, 1, 0, 0, ph - 2.5), wside=8 + 10.0 * wave(t, T, 1, 0, 0, ph - 2.8)))
        for fi, (fn, base, spread) in enumerate((("Index", 12, -3), ("Middle", 16, 0), ("Ring", 20, 2), ("Pinky", 24, 5))):
            for k in (1, 2, 3):
                curl = base * (1.0 if k == 1 else 0.9) + (7 + 3 * k) * wave(t, T, 1, 0.45, k, ph - 2.4 + 0.35 * (3 - fi))
                gr[f"{side}{fn}{k}"] = (0, s * curl, s * (spread + 1.5 * wave(t, T, 1, 0, 0, ph + fi)) if k == 1 else 0)
        for k in (1, 2, 3):
            c = 8 + 6 * wave(t, T, 1, 0.5, k, ph - 1.9)
            gr[f"{side}Thumb{k}"] = (0, s * c * 0.6, s * (10 + c * 0.6) if k == 1 else s * c * 0.4)
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
    if name == "snap":                         # very fast start: strikes, releases
        return 1 - (1 - u) ** 5
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
    "Cape": ([[f"Cape_{c}_{i}" for c in "LCR"] for i in range(1, 5)], 1.5, 0.42, 40.0, 28.0, 30.0, (-20, 70)),
    "Mane": ([[f"Mane_{l}_{k}" for l in range(1, 7)] for k in range(1, 4)], 2.1, 0.40, 30.0, 24.0, 22.0, (-25, 55)),
    "Sash": ([[f"Sash_{s}_1" for s in "LR"], [f"Sash_{s}_2" for s in "LR"], [f"Sash_{s}_Tassel" for s in "LR"]], 2.6, 0.32, -35.0, 20.0, 25.0, (-50, 40)),
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
    life = spec.get("life", 0.35)
    tracks, ctr, rtr = spec["tracks"], spec.get("chain_tracks", Tracks()), spec.get("ring_tracks", Tracks())
    springs = {g: (Spring(c[1], c[2]), Spring(c[1], c[2])) for g, c in CHAINS.items()}
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
        for b, v in kr.items():                                  # keyed bones keep a little idle drift (no stiffness)
            drift = [life * (a - c) for a, c in zip(gr.get(b, (0, 0, 0)), idle0.get(b, (0, 0, 0)))] if "Cape" not in b else [0, 0, 0]
            if any(fn in b for fn in FINGER_NAMES + ("Thumb",)):
                drift = [0.5 * d for d in drift]
            gr[b] = tuple(x + d for x, d in zip(v, drift))
        for b, v in kl.items():
            gl[b] = v
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
                gain = 0.45 + 0.3 * depth
                for bn in row:
                    x0, y0, z0 = gr[bn]
                    gr[bn] = (x0 + p * gain + add[0] * (0.6 + 0.25 * depth), y0 + r * gain + add[1], z0)
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
    return {"T": IDLE_T, "tracks": Tracks(), "springs": False}


def cast():
    """Generic cast: right palm thrust. Wind-up (lean back, chest turns, hand cocks by the ear), snap release
    (palm forward, fingers spread, opposite arm swings back), hit-stop, overshoot, settle."""
    tr = Tracks()
    start(tr)
    tr.key(0.32, merge(torso(-8, 0, -22, -3), head(-2, 0, 18),
                       arm("Right", 35, -35, roll=-20, elbow=110, wflex=-20), arm("Left", 45, 55, elbow=50),
                       hand("Right", "claw"), hand("Left", "relaxed"),
                       leg("Left", 20, 35, 15, 3), leg("Right", -10, 20, 25, 3)), root(0, 0.05, 0.03))
    tr.key(0.42, merge(torso(8, 0, 20, 4), head(4, 0, -14),
                       arm("Right", 2, 88, elbow=4, wflex=-60), arm("Left", 70, -25, elbow=25, wflex=10),
                       hand("Right", "spread"), leg("Left", -5, 15, 25, 3), leg("Right", 15, 30, 20, 3)),
           root(0, -0.07, 0.0), "snap")
    tr.key(0.56, merge(torso(11, 0, 26, 5), arm("Right", -4, 94, elbow=0, wflex=-64)), root(0, -0.09, 0.005), "out")
    tr.key(0.88, merge(torso(3, 0, 8, 1), arm("Right", 30, 55, elbow=35, wflex=-10), hand("Right", "open")), root(0, -0.03, 0), "inout")
    finish(tr, 1.3)
    return {"T": 1.3, "tracks": tr, "hitstops": [(0.42, 0.07)], "hits": [(0.42, 2, 0.6), (0.42, 3, 0.6)]}


def drum_barrage():
    """Drum Barrage: wind-up (fists high, lean back), 8 strikes on a 0.12 s beat alternating fists (right first),
    each drum recoils on its beat (left to right over the arch), the 8th strike is both fists with a hit-stop,
    then the arms bounce and settle."""
    tr = Tracks()
    start(tr)
    raised = lambda side: arm(side, -45, 20, elbow=80, wflex=25)
    strike = lambda side, deep=0: arm(side, 25 + deep, 75, elbow=25 - deep, wflex=15)
    tr.key(0.26, merge(torso(-10), head(-6), raised("Left"), raised("Right"), hand("Left", "fist"), hand("Right", "fist"),
                       leg("Left", 25, 55, 20, 3), leg("Right", 10, 40, 25, 3)), root(0, 0.03, 0.06), "inout")
    beats = [0.30 + 0.12 * k for k in range(8)]
    hits = []
    for k, tb in enumerate(beats):
        last = k == 7
        sides = ["Left", "Right"] if last else ["Right" if k % 2 == 0 else "Left"]
        for side in sides:
            if tb - 0.05 > 0.27:
                tr.key(tb - 0.05, raised(side), None, "out")
            tr.key(tb, strike(side, 10 if last else 0), None, "in")
            if not last:
                tr.key(tb + 0.11, raised(side), None, "out")
        tw = 0 if last else (-12 if sides[0] == "Right" else 12)
        tr.key(tb, merge(torso(16 if last else 6, 0, tw, 4 if last else 1), head(8 if last else 2, 0, tw * 0.5)),
               root(0, -0.02 if last else 0, 0.03 if last else 0.045), "snap")
        if not last:
            tr.key(tb + 0.07, merge(torso(-2, 0, tw * 0.3), head(-2, 0, 0)), root(0, 0.01, 0.06), "out")
        hits.append((tb, k + 1, 1.4 if last else 1.0))
    tr.key(1.32, merge(arm("Left", 10, 60, elbow=30), arm("Right", 10, 60, elbow=30), torso(4)), root(0, 0, 0.04), "out")
    tr.key(1.42, merge(hand("Left", "relaxed"), hand("Right", "relaxed")))
    finish(tr, 1.8)
    return {"T": 1.8, "tracks": tr, "hitstops": [(beats[-1], 0.08)], "hits": hits, "life": 0.25}


def heavens_palm():
    """Heaven's Palm: right arm rises to the sky, fingers spread, body lifts and arches (anticipation); a
    trembling hold while the fingers claw (power gathering); the arm slams down to press the palm at the
    ground ahead, the body crunches forward and a knee comes up; hit-stop, overshoot, settle."""
    tr = Tracks()
    start(tr)
    up = merge(torso(-12, 8, -10, -3), head(-18, 0, -8), arm("Right", -80, 10, elbow=5, wflex=-10),
               arm("Left", 60, 30, elbow=40), hand("Right", "spread"), leg("Left", 20, 45, 20, 3), leg("Right", 0, 30, 25, 3))
    tr.key(0.55, up, root(0, 0.02, 0.12), "inout")
    for i, tt in enumerate((0.60, 0.63, 0.66, 0.69, 0.72)):
        tr.key(tt, arm("Right", -82 + 4 * (i % 2), 10 + 2 * (i % 2), elbow=5, wflex=-10), root(0, 0.02, 0.125 + 0.004 * (i % 2)), "lin")
    tr.key(0.74, merge(hand("Right", "claw"), torso(-15, 8, -12, -4)), None, "inout")
    tr.key(0.84, merge(torso(22, -4, 12, 6), head(12, 0, 4), arm("Right", 40, 80, elbow=0, wflex=-75),
                       arm("Left", 70, -30, elbow=20), hand("Right", "spread"),
                       leg("Left", 30, 60, 15, 3), leg("Right", -15, 15, 30, 3)), root(0, -0.06, -0.05), "in")
    tr.key(1.0, merge(torso(26, -4, 14, 7), arm("Right", 48, 78, elbow=0, wflex=-78)), root(0, -0.07, -0.07), "out")
    tr.key(1.35, merge(torso(8, 0, 4, 2), arm("Right", 55, 50, elbow=25, wflex=-20), hand("Right", "open")), root(0, -0.02, 0), "inout")
    finish(tr, 1.85)
    return {"T": 1.85, "tracks": tr, "hitstops": [(0.84, 0.15)], "hits": [(0.84, d, 0.5) for d in range(1, 9)]}


def thunder_gods_wrath():
    """Ultimate: rise with arms spread (looking up), drum crescendo on an accelerating beat while the arms climb
    into a V with fists, conduct a rain of pillars (alternating points down at targets), wind up with both fists
    overhead and legs tucked, drive both fists down for the colossal strike (hit-stop), then descend."""
    tr = Tracks()
    start(tr)
    hits = []
    tr.key(0.8, merge(torso(-14), head(-20), arm("Left", -30, 0, elbow=10, wflex=-20), arm("Right", -30, 0, elbow=10, wflex=-20),
                      hand("Left", "spread"), hand("Right", "spread"), leg("Left", 0, 10, 30), leg("Right", 0, 10, 30)),
           root(0, 0, 0.55), "inout")
    t, dt, k = 0.85, 0.2, 0
    while t < 2.0:
        hits.append((t, k % 8 + 1, 0.5 + 0.7 * (t - 0.85) / 1.15))
        t += dt
        dt = max(0.05, dt * 0.85)
        k += 1
    tr.key(1.3, merge(arm("Left", -55, 10, elbow=20), arm("Right", -55, 10, elbow=20), hand("Left", "fist"), hand("Right", "fist"),
                      torso(-18), head(-24)), root(0, 0, 0.62), "inout")
    for i, tt in enumerate((1.5, 1.56, 1.62, 1.68, 1.74, 1.8, 1.86, 1.92)):
        j = 2 * (i % 2) - 1
        tr.key(tt, merge(arm("Left", -57 + 3 * j, 10, elbow=20), arm("Right", -57 - 3 * j, 10, elbow=20)), root(0, 0, 0.62 + 0.006 * j), "lin")
    up_l, up_r = arm("Left", -20, 30, elbow=30), arm("Right", -20, 30, elbow=30)
    tr.key(1.98, merge(up_l, up_r, hand("Left", "spread"), hand("Right", "spread"), torso(-6), head(-6)), None, "out")
    for i, tp in enumerate((2.05, 2.2, 2.35, 2.5, 2.65, 2.8)):
        side = "Right" if i % 2 == 0 else "Left"
        tw = -15 if side == "Right" else 15
        tr.key(tp - 0.04, up_r if side == "Right" else up_l, None, "out")
        tr.key(tp, merge(arm(side, 35, 70, elbow=0, wflex=-30, wside=-20), torso(6, 0, tw), head(10, 0, tw * 0.6)), None, "snap")
        tr.key(tp + 0.1, up_r if side == "Right" else up_l, None, "out")
        hits += [(tp, (2 * i) % 8 + 1, 0.8), (tp, (2 * i + 4) % 8 + 1, 0.8)]
    tr.key(3.12, merge(arm("Left", -85, 10, elbow=15), arm("Right", -85, 10, elbow=15), hand("Left", "fist"), hand("Right", "fist"),
                       torso(-20), head(-25), leg("Left", 35, 80, 25), leg("Right", 35, 80, 25)), root(0, 0.02, 0.7), "out")
    tr.key(3.25, merge(arm("Left", 45, 80, elbow=0), arm("Right", 45, 80, elbow=0), torso(30, 0, 0, 8), head(15),
                       leg("Left", -20, 20, 30), leg("Right", -20, 20, 30)), root(0, -0.05, 0.35), "in")
    hits += [(3.25, d, 1.5) for d in range(1, 9)]
    tr.key(3.45, merge(torso(34, 0, 0, 9), arm("Left", 55, 78, elbow=5), arm("Right", 55, 78, elbow=5)), root(0, -0.06, 0.32), "out")
    tr.key(3.6, merge(hand("Left", "relaxed"), hand("Right", "relaxed")))
    finish(tr, 4.3)
    return {"T": 4.3, "tracks": tr, "hitstops": [(3.25, 0.18)], "hits": hits, "life": 0.25}


def transform():
    """Raijin Ascension (god side of the approved beat sheet). 0-0.96 curled low inside the strike (hidden by
    VFX); 0.96-1.85 the pour: curled body spins once and rises; 1.40 drum forge: 8 drums appear on the ground
    ring 0.06 s apart; 1.85 squeeze (anticipation); 1.95 BURST: unfurls, chest out, arms flung wide, fingers
    spread; slow-mo float while cape and mane billow up and the frame rises in; 2.36 drums fly up on arcs and
    lock into the arch 0.07 s apart (clang); 2.8 FIRST BEAT: arms thrust down-out, every drum strikes,
    hit-stop; 3.4 settles into the idle."""
    import drum_ring as dr
    tr = Tracks()
    curl = merge(torso(35, 0, 0, 20), head(35), arm("Left", 60, 75, roll=20, elbow=115), arm("Right", 60, 75, roll=20, elbow=115),
                 hand("Left", "fist"), hand("Right", "fist"), leg("Left", 70, 120, 30), leg("Right", 70, 120, 30))
    tr.key(0.0, merge(curl, {"LowerTorso": (20, 0, -360)}), root(0, 0, -0.42))
    tr.key(0.96, merge(curl, {"LowerTorso": (20, 0, -360)}), root(0, 0, -0.36), "lin")
    tr.key(1.85, merge(curl, torso(42, 0, 0, 24), {"LowerTorso": (24, 0, 0)}, leg("Left", 75, 130, 30), leg("Right", 75, 130, 30)),
           root(0, 0, -0.2), "inout")
    burst = merge(torso(-18, 0, 0, -6), head(-22), arm("Left", -35, -5, elbow=10, wflex=-30), arm("Right", -35, -5, elbow=10, wflex=-30),
                  hand("Left", "spread"), hand("Right", "spread"), leg("Left", -5, 12, 35), leg("Right", -5, 12, 35))
    tr.key(1.95, burst, root(0, 0, 0.40), "snap")
    tr.key(2.62, merge(arm("Left", -42, -8, elbow=8, wflex=-32), arm("Right", -42, -8, elbow=8, wflex=-32), head(-8), torso(-14, 0, 0, -4)),
           root(0, 0, 0.46), "out")
    tr.key(2.74, merge(arm("Left", 10, 40, elbow=60), arm("Right", 10, 40, elbow=60), torso(8, 0, 0, 3), head(6),
                       hand("Left", "fist"), hand("Right", "fist")), root(0, 0, 0.42), "inout")
    tr.key(2.80, merge(arm("Left", 20, -10, elbow=5, wflex=-40), arm("Right", 20, -10, elbow=5, wflex=-40), torso(-10), head(4),
                       hand("Left", "spread"), hand("Right", "spread"), leg("Left", 10, 30, 25, 3), leg("Right", 0, 18, 28, 3)),
           root(0, 0, 0.36), "snap")
    tr.key(3.0, merge(hand("Left", "open"), hand("Right", "open")), None, "inout")
    finish(tr, 3.5)
    ctr = Tracks()
    ctr.key(1.95, {"@Cape": (0, 0, 0), "@Mane": (0, 0, 0)})
    ctr.key(2.3, {"@Cape": (30, 0, 0), "@Mane": (26, 0, 0)}, None, "out")
    ctr.key(2.75, {"@Cape": (26, 0, 0), "@Mane": (22, 0, 0)}, None, "inout")
    ctr.key(3.1, {"@Cape": (0, 0, 0), "@Mane": (0, 0, 0)}, None, "inout")
    rtr = Tracks()
    rtr.key(0.0, None, {"Root": (0, 0, -25)})
    rtr.key(2.199, None, {"Root": (0, 0, -25)}, "hold")
    rtr.key(2.2, None, {"Root": (0, 0, -1.4)}, "lin")
    rtr.key(2.36, None, {"Root": (0, 0, 0)}, "out")
    rtr.key(2.8, None, {"Root": (0, 0, 0)}, "lin")
    rtr.key(3.5, None, {"Root": STANCE[3]["Root"]}, "inout")
    hits = [(2.8, d, 1.3) for d in range(1, 9)]
    slots = {d: Vector(dr.arch_pt(dr.DRUM_ANG[d - 1], dr.R, dr.DRUM_Y)) for d in range(1, 9)}
    for d in range(1, 9):
        hits.append((2.36 + 0.07 * (d - 1) + 0.30, d, 0.7))

    def drum_fn(d, t, root_loc, ring_root):
        tf, ta, fl = 1.40 + 0.06 * (d - 1), 2.36 + 0.07 * (d - 1), 0.30
        th = math.radians(-90 + (d - 1) * 45)
        ground = Vector((2.0 * math.cos(th), 2.0 * math.sin(th), -0.95 + 0.19))
        spin = 0.0
        if t < tf:
            world = Vector((0, 0, -30))
        elif t < ta:
            pop = 0.12 * math.exp(-(t - tf) * 9) * math.sin(min(math.pi, (t - tf) * 30))
            world = ground + Vector((0, 0, pop))
        elif t < ta + fl:
            u = (t - ta) / fl
            e = 1 - (1 - u) ** 2
            world = ground.lerp(slots[d], e) + Vector((0, 0, 0.9 * math.sin(math.pi * u)))
            spin = 360 * (1 - e)
        else:
            return None
        off = world - slots[d] - root_loc - Vector(ring_root)
        return (tuple(off), (0, 0, spin))

    return {"T": 3.5, "tracks": tr, "chain_tracks": ctr, "ring_tracks": rtr, "hits": hits, "drum_fn": drum_fn,
            "hitstops": [(2.8, 0.14)], "life": 0.15}


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
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_animations=True,
                                  export_animation_mode="SCENE", export_frame_range=True, export_force_sampling=True,
                                  export_skins=True, export_apply=False)
        print(clip, "frames", n, "->", path)


if __name__ == "__main__":
    main()
