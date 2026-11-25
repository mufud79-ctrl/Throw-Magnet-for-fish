"""Audit baked god animations for clipping, mesh artifacts and odd hand motion.

    /tmp/bpyenv/bin/python anim_audit.py [clip ...] [--json OUT]

For every frame of assets/meshes/thunder_god/anim/<clip>.glb:
  clip_*    triangle intersections between the forearm/hand/finger part of the body mesh and
            torso+legs (clip_body), head (clip_head), the cape (clip_cape) and the mane (clip_mane), per side
  stretch   edges that grew more than 0.03 units vs the rest pose (tearing / candy-wrapper artifacts)
  wrist     angle between forearm and hand bones (> 75 deg looks broken)
  pop       hand / forearm angular speed spikes (deg per frame > 22: a snap the eye reads as a glitch)
Prints a per-clip summary with the worst frames, optionally writes everything to JSON.
"""
import os
import sys
import json
import math
import argparse
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
ANIM = os.path.join(ROOT, "assets", "meshes", "thunder_god", "anim")
FPS = 30


def part_of(name):
    for side in ("Left", "Right"):
        if name.startswith(side) and any(k in name for k in ("LowerArm", "Hand", "Thumb", "Index", "Middle", "Ring", "Pinky")):
            return "arm" + side[0]
        if name.startswith(side) and "UpperArm" in name:
            return "upper" + side[0]
    if name == "Head":
        return "head"
    return "body"


def audit(clip):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = FPS            # the importer converts seconds with the scene rate (default 24)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ANIM, f"{clip}.glb"))
    sc = bpy.context.scene
    arm = next(o for o in sc.objects if o.type == "ARMATURE" and "HumanoidRootPart" in o.data.bones)
    body = next(o for o in sc.objects if o.type == "MESH" and o.name.startswith("Body"))
    cape = next(o for o in sc.objects if o.type == "MESH" and o.name.startswith("Cape"))
    mane = next(o for o in sc.objects if o.type == "MESH" and o.name.startswith("Mane"))
    # dominant bone per body face
    names = [g.name for g in body.vertex_groups]
    me = body.data
    dom_v = np.zeros(len(me.vertices), int)
    for v in me.vertices:
        if v.groups:
            dom_v[v.index] = max(v.groups, key=lambda g: g.weight).group
    vpart = np.array([part_of(names[g]) for g in dom_v])
    faces = [tuple(p.vertices) for p in me.polygons]
    fpart = []
    for f in faces:
        ps = [vpart[i] for i in f]
        fpart.append(max(set(ps), key=ps.count))
    fpart = np.array(fpart)
    edges = np.array([tuple(e.vertices) for e in me.edges])
    rest = np.array([v.co[:] for v in me.vertices])
    rest_len = np.linalg.norm(rest[edges[:, 0]] - rest[edges[:, 1]], axis=1)
    act = arm.animation_data.action if arm.animation_data else None
    f0, f1 = (int(act.frame_range[0]), int(act.frame_range[1])) if act else (sc.frame_start, sc.frame_end)
    prev_rot = {}
    rows = []
    dg = bpy.context.evaluated_depsgraph_get()

    def sub_bvh(co, mask):
        idx = np.where(mask)[0]
        if len(idx) == 0:
            return None, idx
        return BVHTree.FromPolygons([tuple(map(float, c)) for c in co], [faces[i] for i in idx]), idx

    for fr in range(f0, f1 + 1):
        sc.frame_set(fr)
        dg = bpy.context.evaluated_depsgraph_get()
        mw = body.matrix_world
        em = body.evaluated_get(dg).to_mesh()
        co = np.array([(mw @ v.co)[:] for v in em.vertices])
        body.evaluated_get(dg).to_mesh_clear()
        row = {"frame": fr, "t": round((fr - f0) / FPS, 3)}
        for side in "LR":
            ba, _ = sub_bvh(co, fpart == "arm" + side)
            if ba is None:
                continue
            bb, _ = sub_bvh(co, fpart == "body")
            bh, _ = sub_bvh(co, fpart == "head")
            row[f"clip_body_{side}"] = len(ba.overlap(bb)) if bb else 0
            row[f"clip_head_{side}"] = len(ba.overlap(bh)) if bh else 0
            for name, ob in (("cape", cape), ("mane", mane)):
                eo = ob.evaluated_get(dg)
                m2 = eo.to_mesh()
                bv = BVHTree.FromPolygons([tuple((ob.matrix_world @ v.co)[:]) for v in m2.vertices], [tuple(p.vertices) for p in m2.polygons])
                eo.to_mesh_clear()
                row[f"clip_{name}_{side}"] = len(ba.overlap(bv))
        d = np.linalg.norm(co[edges[:, 0]] - co[edges[:, 1]], axis=1) - rest_len
        row["stretch"] = int((d > 0.03).sum())
        pb = arm.pose.bones
        for side in ("Left", "Right"):
            la, hd = pb.get(f"{side}LowerArm"), pb.get(f"{side}Hand")
            if la and hd:
                a = (arm.matrix_world @ la.tail - arm.matrix_world @ la.head).normalized()
                b = (arm.matrix_world @ hd.tail - arm.matrix_world @ hd.head).normalized()
                row[f"wrist_{side[0]}"] = round(math.degrees(a.angle(b)), 1)
            # pops: change per frame of the wrist (hand relative to forearm) and of the forearm relative to the
            # upper arm. Whole-arm swings are allowed to be fast; a joint flipping inside one frame is a glitch.
            for key, child, parent in ((f"wristpop_{side[0]}", f"{side}Hand", f"{side}LowerArm"), (f"elbowpop_{side[0]}", f"{side}LowerArm", f"{side}UpperArm")):
                q = (pb[parent].matrix.inverted() @ pb[child].matrix).to_quaternion()
                if key in prev_rot:
                    ang = math.degrees(prev_rot[key].rotation_difference(q).angle)
                    row[key] = round(min(ang, 360 - ang), 1)
                prev_rot[key] = q
        rows.append(row)
    return rows


def summarize(clip, rows):
    print(f"\n== {clip}  ({len(rows)} frames)")
    keys = sorted({k for r in rows for k in r if k not in ("frame", "t")})
    for k in keys:
        vals = [(r.get(k, 0), r["t"]) for r in rows]
        if k.startswith("clip_") or k == "stretch":
            bad = [(v, t) for v, t in vals if v > 0]
            if bad:
                worst = sorted(bad, reverse=True)[:6]
                print(f"  {k:16s} frames {len(bad):3d}  worst " + ", ".join(f"{v}@{t}" for v, t in worst))
        elif k.startswith("wrist"):
            bad = [(v, t) for v, t in vals if v > 75]
            if bad:
                print(f"  {k:16s} >75deg {len(bad):3d}  worst " + ", ".join(f"{v}@{t}" for v, t in sorted(bad, reverse=True)[:6]))
        elif "pop" in k:
            bad = [(v, t) for v, t in vals if v > 22]
            if bad:
                print(f"  {k:16s} >22/f  {len(bad):3d}  worst " + ", ".join(f"{v}@{t}" for v, t in sorted(bad, reverse=True)[:6]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="*", default=["idle", "cast", "drum_barrage", "heavens_palm", "thunder_gods_wrath", "transform"])
    ap.add_argument("--json", default=None)
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    out = {}
    for c in a.clips:
        rows = audit(c)
        out[c] = rows
        summarize(c, rows)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(out, f)


if __name__ == "__main__":
    main()
