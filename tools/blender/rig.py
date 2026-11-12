"""Shared fish skeleton + automatic skin weights.

Every fish gets the same bone names so one Roblox animation works on all of them:
  Root -> Head -> Jaw
  Root -> Spine1 -> Spine2 -> Spine3 -> Spine4 -> Tail
  Root -> Pect_L, Pect_R
Optional extra bones (e.g. Lure, Neck_L/Neck_R) come from fish.extra_bones.
Bone local Z points to the fish's back, so side-to-side bending = rotation about Z.
"""
import bpy, numpy as np
from mathutils import Vector

BOUNDS = [0.36, 0.5, 0.64, 0.78, 0.9]
CHAIN = ["Head", "Spine1", "Spine2", "Spine3", "Spine4", "Tail"]
PECT_PREFIX = ("Pect", "Wing", "Arm_")
JAW_PREFIX = ("Jaw", "ToothL", "Kype")

def _sm(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

def _t(f, co):
    if f.rig_vertical: return (f._zmax - co[:, 2]) / (f._zmax - f._zmin)
    return (f.L / 2 - co[:, 0]) / f.L

def assign_weights(f):
    objs = f.parts + f.glow
    if f.rig_vertical:
        zs = np.concatenate([np.array([v.co.z for v in o.data.vertices]) for o in objs])
        f._zmax, f._zmin = float(zs.max()), float(zs.min())
    f._pect, f._tmax, f._jaw_c = {}, 1.0, None
    for ob in objs:
        co = np.array([v.co[:] for v in ob.data.vertices]); cen = Vector(co.mean(0).tolist())
        bone = next((e["name"] for e in f.extra_bones if e["match"](ob.name, cen)), None)
        if bone is None and ob.name.startswith(PECT_PREFIX):
            bone = "Pect_L" if cen.y > 0 else "Pect_R"
            if bone not in f._pect:
                o = np.argsort(np.abs(co[:, 1])); k = max(1, len(o) // 10)
                f._pect[bone] = (Vector(co[o[:k]].mean(0).tolist()), Vector(co[o[-k:]].mean(0).tolist()))
        if bone is None and f.jaw_hinge is not None and ob.name.startswith(JAW_PREFIX):
            bone = "Jaw"; f._jaw_c = f._jaw_c or cen
        if bone:
            ob.vertex_groups.new(name=bone).add(list(range(len(co))), 1.0, "REPLACE"); continue
        t = _t(f, co); f._tmax = max(f._tmax, float(t.max()))
        s = [_sm(b - 0.05, b + 0.05, t) for b in BOUNDS]
        ws = [1 - s[0]] + [s[i] - s[i + 1] for i in range(4)] + [s[4]]
        for name, w in zip(CHAIN, ws):
            idx = np.nonzero(w > 0.002)[0]
            if len(idx) == 0: continue
            vg = ob.vertex_groups.new(name=name)
            for i in idx: vg.add([int(i)], float(w[i]), "REPLACE")

def _P(f, t):
    if f.rig_vertical: return Vector((0, 0, f._zmax - t * (f._zmax - f._zmin)))
    tc = min(max(t, 0.0), 1.0); return f.axis(tc) + Vector((-(t - tc) * f.L, 0, 0))

def build_armature(f, xf, up, fwd, meshes):
    ad = bpy.data.armatures.new(f"{f.name}_Rig"); arm = bpy.data.objects.new(f"{f.name}_Rig", ad)
    bpy.context.scene.collection.objects.link(arm)
    bpy.ops.object.select_all(action="DESELECT"); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT"); eb = ad.edit_bones
    along = fwd if f.rig_vertical else up
    def mk(name, h, t, parent=None, roll=None):
        b = eb.new(name); b.head = xf(h); b.tail = xf(t)
        if (b.tail - b.head).length < 1e-3: b.tail = b.head + up * 0.1
        b.align_roll(roll if roll is not None else along)
        if parent: b.parent = eb[parent]
    R0 = _P(f, 0.36); off = Vector((f.R * 0.6, 0, 0)) if f.rig_vertical else Vector((0, 0, f.R * 0.6))
    mk("Root", R0, R0 + off, roll=up if f.rig_vertical else fwd)
    mk("Head", R0, _P(f, 0.0), "Root")
    prev = "Root"
    for name, a, b in zip(["Spine1", "Spine2", "Spine3", "Spine4"], [0.36] + BOUNDS[1:4], BOUNDS[1:]):
        mk(name, _P(f, a), _P(f, b), prev); prev = name
    mk("Tail", _P(f, 0.9), _P(f, max(f._tmax, 1.0) if not f.rig_vertical else 1.0), "Spine4")
    for nm, sd in (("Pect_L", 1), ("Pect_R", -1)):
        h, t = f._pect.get(nm, (_P(f, 0.25), _P(f, 0.25) + Vector((0, sd * f.R, 0))))
        mk(nm, h, t, "Root")
    if f.jaw_hinge is not None and f._jaw_c is not None: mk("Jaw", f.jaw_hinge, f._jaw_c, "Head")
    else: mk("Jaw", _P(f, 0.06), _P(f, 0.0), "Head")
    for e in f.extra_bones: mk(e["name"], e["head"], e["tail"], e.get("parent", "Head"))
    bpy.ops.object.mode_set(mode="OBJECT")
    for m in meshes:
        m.parent = arm; m.modifiers.new("Armature", "ARMATURE").object = arm
    return arm
