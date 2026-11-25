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
def idle(god, ring, T=3.2):
    """Floating god-mode idle: float bob, breath, arms drifting a beat behind the torso, legs dangling,
    cape / mane / sash / hakama waving down their chains, drums bobbing in a wave round the ring."""
    n = int(round(T * FPS))
    for f in range(n + 1):
        t = f / FPS
        reset(god)
        reset(ring)
        b = wave(t, T, 1, 0, 0)                 # main float cycle (rise on +)
        b_lag = wave(t, T, 1, 0, 0, -0.9)       # same cycle, a beat later (follow-through)
        # body: float bob, breath (chest lifts on the rise), head settles after the chest
        loc(god, "HumanoidRootPart", (0, 0, 0.06 + 0.018 * b))
        rot(god, "LowerTorso", 1.0 * b_lag)
        rot(god, "UpperTorso", -2.0 - 1.4 * b, 0, 0)
        rot(god, "Head", 3.0 + 1.0 * b_lag, 0, 0.8 * wave(t, T, 1, 0, 0, 1.3))
        # arms: floating stance, down and a little out, elbows bent. Arms rest along X in the T-pose, so in
        # armature space: Y = raise / lower, Z = swing fore / aft round the vertical, X = roll along the arm.
        # Mirror: X keeps its sign, Y and Z flip (the s factor). Shoulder leads, elbow trails, wrist trails last;
        # the two arms are out of step so the pose never looks mirrored.
        for side, s, ph in (("Left", 1, 0.0), ("Right", -1, 2.1)):
            fore = wave(t, T, 1, 0, 0, ph - 0.9) + 0.3 * wave(t, T, 2, 0, 0, ph * 0.7 - 0.5)
            rot(god, f"{side}UpperArm", 10.0 * wave(t, T, 1, 0, 0, ph - 1.2),
                s * (36 + 6.0 * wave(t, T, 1, 0, 0, ph - 0.3)),        # out from the hips so the hands clear the sash
                s * -(20 + 10.0 * fore))                               # always in front of the cape flaps
            rot(god, f"{side}LowerArm", 15.0 * wave(t, T, 1, 0, 0, ph - 2.0), 0,
                s * -(30 + 22.0 * wave(t, T, 1, 0, 0, ph - 1.7)))
            rot(god, f"{side}Hand", 0, s * (10 + 14.0 * wave(t, T, 1, 0, 0, ph - 2.5)),
                s * -(8 + 10.0 * wave(t, T, 1, 0, 0, ph - 2.8)))
        # fingers: relaxed curl, deeper from index to pinky; a slow ripple runs pinky -> index with each joint
        # lagging the one before (overlap); the thumb drifts on its own. Palm faces down and fingers point along
        # the arm, so curl = Y (toward the palm), spread = Z; mirrored with s.
        for side, s, ph in (("Left", 1, 0.0), ("Right", -1, 2.1)):
            for fi, (fn, base, spread) in enumerate((("Index", 12, -3), ("Middle", 16, 0), ("Ring", 20, 2), ("Pinky", 24, 5))):
                for k in (1, 2, 3):
                    curl = base * (1.0 if k == 1 else 0.9) + (7 + 3 * k) * wave(t, T, 1, 0.45, k, ph - 2.4 + 0.35 * (3 - fi))
                    rot(god, f"{side}{fn}{k}", 0, s * curl, s * (spread + 1.5 * wave(t, T, 1, 0, 0, ph + fi)) if k == 1 else 0)
            for k in (1, 2, 3):
                c = 8 + 6 * wave(t, T, 1, 0.5, k, ph - 1.9)
                rot(god, f"{side}Thumb{k}", 0, s * c * 0.6, s * (10 + c * 0.6) if k == 1 else s * c * 0.4)
        # legs dangling: a slow, gentle tread. Each leg swings from the hip, the knee bends as the thigh comes
        # forward and trails behind it, the toes point last; left and right alternate
        for side, sgn, ph, knee0, foot0, splay in (("Left", 1, 0.0, 30, 22, 3), ("Right", -1, math.pi * 0.85, 16, 26, -3)):
            hip = wave(t, T, 1, 0, 0, ph - 0.8)
            rot(god, f"{side}UpperLeg", (-10 if sgn > 0 else 2) - 9.0 * hip, 0, splay + 2.0 * wave(t, T, 2, 0, 0, ph))
            rot(god, f"{side}LowerLeg", knee0 + 13.0 * wave(t, T, 1, 0, 0, ph - 1.9))
            rot(god, f"{side}Foot", foot0 + 10.0 * wave(t, T, 1, 0, 0, ph - 2.8))
        # cape: drifting back on the updraft, a 2-per-loop wave down each column, columns out of phase,
        # plus a slow side sway; amplitude grows down the chain
        for ci, col in enumerate("RCL"):
            for i in range(1, 5):
                pitch = (5 if i > 1 else 3) + (1.2 + 0.5 * i) * wave(t, T, 2, 0.75, i, ci * 0.9) + 1.2 * b_lag
                roll = (0.6 + 0.3 * i) * wave(t, T, 1, 0.5, i, ci * 1.4)
                rot(god, f"Cape_{col}_{i}", pitch, roll, 0)
        # mane: lighter and quicker than the cape, each lock offset
        for li in range(1, 7):
            for k in range(1, 4):
                pitch = 3 + (1.0 + 0.6 * k) * wave(t, T, 2, 0.9, k, li * 0.8) + 0.8 * b_lag
                roll = (0.5 + 0.4 * k) * wave(t, T, 1, 0.7, k, li * 1.1)
                rot(god, f"Mane_{li}_{k}", pitch, roll, 0)
        # sash tails + tassels: swing fore/aft against the bob (they lag the hips), tassel snaps last
        for si, sd in enumerate("LR"):
            for k, bn in enumerate((f"Sash_{sd}_1", f"Sash_{sd}_2", f"Sash_{sd}_Tassel")):
                rot(god, bn, (1.5 + 1.0 * k) * wave(t, T, 2, 0.8, k, si * 1.2) - 1.5 * b_lag, 0.8 * k * wave(t, T, 1, 0.6, k, si))
        for key, sgn in (("Hakama_F", -1), ("Hakama_B", 1)):
            for k in (1, 2):
                rot(god, f"{key}_{k}", sgn * (1.2 + 0.8 * k) * wave(t, T, 2, 0.7, k, 0.5 if sgn > 0 else 0))
        # drum ring: floats a beat behind the god with a gentle roll; drums bob in a wave travelling over the
        # arch (left to right), tassels swing after their drum
        loc(ring, "Root", (0, 0, 0.012 * wave(t, T, 1, 0, 0, -1.2)))
        rot(ring, "Root", 0, 1.0 * wave(t, T, 1, 0, 0, -0.4), 0)
        for d in range(1, 9):
            ph = -d * TAU / 8
            loc(ring, f"Drum_{d}", (0, 0.004 * wave(t, T, 2, 0, 0, ph + 1.0), 0.010 * wave(t, T, 2, 0, 0, ph)))
            rot(ring, f"Drum_{d}", 2.0 * wave(t, T, 2, 0, 0, ph - 0.6), 0, 1.5 * wave(t, T, 1, 0, 0, ph))
            rot(ring, f"Tassel_{d}", 6.0 * wave(t, T, 2, 0, 0, ph - 1.4), 4.0 * wave(t, T, 1, 0, 0, ph - 1.0), 0)
        bpy.context.view_layer.update()
        key_all(god, f + 1)
        key_all(ring, f + 1)
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, n + 1
    return n


CLIPS = {"idle": idle}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="*", default=["idle"])
    ap.add_argument("--out", default=os.path.join(ROOT, "assets", "meshes", "thunder_god", "anim"))
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    os.makedirs(a.out, exist_ok=True)
    for clip in a.clips:
        god, ring = load_scene()
        for arm in (god, ring):
            arm.animation_data_clear()
        n = CLIPS[clip](god, ring)
        for arm in (god, ring):
            if arm.animation_data and arm.animation_data.action:
                arm.animation_data.action.name = f"{clip}_{arm.name}"
        path = os.path.join(a.out, f"{clip}.glb")
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_animations=True,
                                  export_animation_mode="SCENE", export_frame_range=True, export_force_sampling=True,
                                  export_skins=True, export_apply=False)
        print(clip, "frames", n, "->", path)


if __name__ == "__main__":
    main()
