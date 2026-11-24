"""Rig the cleaned thunder god: R15-named humanoid skeleton + sway chains for cape, mane, sash tails, hakama panels.

    /tmp/bpyenv/bin/python god_rig.py [--src BLEND] [--out DIR] [--test-pose] [--export]

Input: assets/meshes/thunder_god/thunder_god_clean.blend (from god_cleanup.py; Z-up, faces -Y, 1.9 tall).
Skeleton (Roblox R15 bone names so the Avatar importer / Animation Editor treat it as a humanoid; the character's
left is +X):
  HumanoidRootPart > LowerTorso > UpperTorso > Head
  UpperTorso > {Left,Right}UpperArm > LowerArm > Hand
  LowerTorso > {Left,Right}UpperLeg > LowerLeg > Foot
Sway chains (extra bones; Roblox keeps them and the Animation Editor can key them; secondary motion gets baked
into keyframes later):
  Cape_{L,C,R}_1..4   cape, 3 columns x 4, rooted at UpperTorso; the cape's top row stays on UpperTorso so the
                      cut under the shoulder pads never opens
  Mane_1..6_1..3      6 locks x 3, rooted at Head
  Sash_{L,R}_1..2 + Sash_{L,R}_Tassel   the two front sash tails and their red tips, rooted at LowerTorso
  Hakama_{F,B}_1..2   front / back hakama panels, rooted at LowerTorso, blended with the legs
Weights: Body gets automatic (bone heat) weights from the R15 bones; chain weights are procedural (each chain
bone owns a band of the part, hat-function blend between neighbours and into the root bone at the top).
--test-pose writes posed previews (arms down, elbows/knees bent, head turn, cape/mane/sash swung) for the
deformation check. --export writes the Roblox FBX (only after the user approved the rig).
"""
import os
import sys
import math
import json
import argparse
import numpy as np
import bpy
from mathutils import Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
CY = -0.125                     # body centre depth (the model is not centred in Y)

# ---------------------------------------------------------------- humanoid joints (measured from cross-sections)
J = {
    "root": (0.0, CY, -0.03), "waist": (0.0, CY + 0.01, 0.20), "neck": (0.0, CY - 0.01, 0.63), "headtop": (0.0, CY - 0.02, 0.88),
    "shoulder": (0.215, -0.125, 0.515), "elbow": (0.42, -0.13, 0.49), "wrist": (0.62, -0.14, 0.462), "handtip": (0.75, -0.145, 0.443),
    "hip": (0.10, CY, -0.04), "knee": (0.19, -0.11, -0.48), "ankle": (0.215, -0.085, -0.83), "toe": (0.24, -0.27, -0.92),
}
R15 = [  # name, head, tail, parent
    ("HumanoidRootPart", "root", None, None),
    ("LowerTorso", "root", "waist", "HumanoidRootPart"),
    ("UpperTorso", "waist", "neck", "LowerTorso"),
    ("Head", "neck", "headtop", "UpperTorso"),
]
for side, s in (("Left", 1), ("Right", -1)):
    R15 += [
        (f"{side}UpperArm", ("shoulder", s), ("elbow", s), "UpperTorso"),
        (f"{side}LowerArm", ("elbow", s), ("wrist", s), f"{side}UpperArm"),
        (f"{side}Hand", ("wrist", s), ("handtip", s), f"{side}LowerArm"),
        (f"{side}UpperLeg", ("hip", s), ("knee", s), "LowerTorso"),
        (f"{side}LowerLeg", ("knee", s), ("ankle", s), f"{side}UpperLeg"),
        (f"{side}Foot", ("ankle", s), ("toe", s), f"{side}LowerLeg"),
    ]


def jp(key):
    if isinstance(key, tuple):
        k, s = key
        x, y, z = J[k]
        return Vector((x * s, y, z))
    return Vector(J[key])


def verts(ob):
    v = np.zeros(len(ob.data.vertices) * 3)
    ob.data.vertices.foreach_get("co", v)
    return v.reshape(-1, 3)


def vert_colours(ob):
    """Texture colour per vertex (first loop's UV)."""
    me = ob.data
    uv = np.zeros(len(me.loops) * 2)
    me.uv_layers.active.data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    lv = np.zeros(len(me.loops), int)
    me.loops.foreach_get("vertex_index", lv)
    vuv = np.zeros((len(me.vertices), 2))
    vuv[lv] = uv
    img = [n for n in me.materials[0].node_tree.nodes if n.type == "TEX_IMAGE"][0].image
    W, H = img.size
    px = np.array(img.pixels[:], np.float32).reshape(H, W, 4)
    xi = np.clip((vuv[:, 0] % 1) * W, 0, W - 1).astype(int)
    yi = np.clip((vuv[:, 1] % 1) * H, 0, H - 1).astype(int)
    return px[yi, xi, :3]


def hat_weights(s, nb):
    """s in [0, nb] along a chain of nb bones -> (n, nb) weights, hat functions centred on bone midpoints."""
    s = np.clip(s, 0.5, nb - 0.5)
    w = np.maximum(0, 1 - np.abs(s[:, None] - (np.arange(nb)[None, :] + 0.5)))
    return w / (w.sum(1, keepdims=True) + 1e-9)


def chain_joints(P, mask_fn, z_levels, xy_default):
    """Joint positions along a chain: mean x/y of the part's verts near each z level (inside mask_fn)."""
    out = []
    for z in z_levels:
        m = mask_fn(P) & (np.abs(P[:, 2] - z) < 0.04)
        if m.sum() >= 3:
            x, y = P[m, 0].mean(), P[m, 1].mean()
        else:
            x, y = xy_default
        out.append(Vector((x, y, z)))
    return out


# ================================================================ build
def build(src):
    bpy.ops.wm.open_mainfile(filepath=src)
    body, cape, mane = (bpy.data.objects[n] for n in ("Body", "Cape", "Mane"))
    PB, PC, PM = verts(body), verts(cape), verts(mane)
    chains = {}            # chain name -> dict(bones=[names], joints=[Vector], parent=root bone)

    # ---- cape: 3 columns by angle round the body axis (0 = straight back, + = character's left)
    th_c = np.degrees(np.arctan2(PC[:, 0], PC[:, 1] - CY))
    side = 0.62 * np.percentile(np.abs(th_c), 95)
    cz_top, cz_bot = 0.44, PC[:, 2].min() + 0.015
    zl = np.linspace(cz_top, cz_bot, 5)
    for col, th0 in (("R", -side), ("C", 0.0), ("L", side)):
        fn = lambda P, th0=th0: np.abs(np.degrees(np.arctan2(P[:, 0], P[:, 1] - CY)) - th0) < 14
        jts = chain_joints(PC, fn, zl, (0.0, 0.1))
        chains[f"Cape_{col}"] = dict(bones=[f"Cape_{col}_{i}" for i in range(1, 5)], joints=jts, parent="UpperTorso", theta=th0)

    # ---- mane: 6 locks by angle round the head axis, equal vertex counts
    th_m = np.degrees(np.arctan2(PM[:, 0], PM[:, 1] - (CY - 0.02)))
    edges = np.percentile(th_m, np.linspace(0, 100, 7))
    centres = (edges[:-1] + edges[1:]) / 2
    mz_top, mz_bot = 0.72, PM[:, 2].min() + 0.015
    zl = np.linspace(mz_top, mz_bot, 4)
    for i, th0 in enumerate(centres, 1):
        lo, hi = edges[i - 1], edges[i]
        fn = lambda P, lo=lo, hi=hi: (lambda t: (t >= lo) & (t <= hi))(np.degrees(np.arctan2(P[:, 0], P[:, 1] - (CY - 0.02))))
        jts = chain_joints(PM, fn, zl, (0.0, 0.05))
        chains[f"Mane_{i}"] = dict(bones=[f"Mane_{i}_{k}" for k in range(1, 4)], joints=jts, parent="Head", theta=th0, edges=(lo, hi))

    # ---- sash tails (white strips + red tips at the front of the waist), from texture colour + position
    colB = vert_colours(body)
    r, g, b = colB.T
    mx, mn = colB.max(1), colB.min(1)
    sat = (mx - mn) / (mx + 1e-6)
    white = (mn > 0.55) & (sat < 0.22)
    red = (r > g * 1.6) & (r > b * 1.3) & (sat > 0.35)
    x, y, z = PB.T
    tail = (white | red) & (np.abs(x) < 0.13) & (z < 0.10) & (z > -0.32) & (y < -0.24)
    sz_top, sz_bot = 0.09, (z[tail].min() + 0.01) if tail.any() else -0.25
    zl = np.linspace(sz_top, sz_bot, 4)
    for sd, sgn in (("L", 1), ("R", -1)):
        jts = chain_joints(PB, lambda P, sgn=sgn: tail & ((P[:, 0] >= 0) == (sgn > 0)), zl, (0.04 * sgn, -0.3))
        chains[f"Sash_{sd}"] = dict(bones=[f"Sash_{sd}_1", f"Sash_{sd}_2", f"Sash_{sd}_Tassel"], joints=jts, parent="LowerTorso")

    # ---- hakama panels (front / back centre of the trousers)
    hz = np.linspace(0.0, -0.42, 3)
    chains["Hakama_F"] = dict(bones=["Hakama_F_1", "Hakama_F_2"], joints=[Vector((0, -0.27, z0)) for z0 in hz], parent="LowerTorso")
    chains["Hakama_B"] = dict(bones=["Hakama_B_1", "Hakama_B_2"], joints=[Vector((0, 0.02, z0)) for z0 in hz], parent="LowerTorso")

    # ---- armature
    arm_data = bpy.data.armatures.new("ThunderGod")
    arm = bpy.data.objects.new("ThunderGod", arm_data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones
    for name, h, t, par in R15:
        bone = eb.new(name)
        bone.head = jp(h)
        bone.tail = jp(t) if t else jp(h) + Vector((0, 0, 0.12))
        if par:
            bone.parent = eb[par]
            if name not in ("LeftUpperArm", "RightUpperArm", "LeftUpperLeg", "RightUpperLeg"):
                bone.use_connect = (bone.head - eb[par].tail).length < 1e-4
    for cname, c in chains.items():
        prev = eb[c["parent"]]
        for i, bn in enumerate(c["bones"]):
            bone = eb.new(bn)
            bone.head, bone.tail = c["joints"][i], c["joints"][i + 1]
            if (bone.tail - bone.head).length < 0.01:
                bone.tail = bone.head + Vector((0, 0, -0.05))
            bone.parent = prev
            bone.use_connect = i > 0
            prev = bone
    bpy.ops.object.mode_set(mode="OBJECT")
    chain_bones = [bn for c in chains.values() for bn in c["bones"]]

    # ---- body: smooth analytic weights along the R15 bones (bone heat gave rigid, torn weights on this mesh)
    names_r15 = [b[0] for b in R15 if b[0] != "HumanoidRootPart"]
    groups = analytic_body_weights(PB)
    W = np.stack([groups[n] for n in names_r15], 1)
    body.parent = arm
    body.modifiers.new("Armature", "ARMATURE").object = arm

    # sash tails: the white strips are painted on the front apron (fused to the hakama), so the chain owns a
    # smooth front region rather than the painted pixels; left/right blend across the centre line
    extra = {}
    x, y, z = PB.T
    front = 1 - smoothstep(-0.29, -0.245, y)
    sash_w = front * (1 - smoothstep(0.09, 0.13, np.abs(x))) * smoothstep(sz_top + 0.03, sz_top - 0.04, z)
    s_ = (sz_top - z) / (sz_top - sz_bot) * 3
    hw = hat_weights(s_, 3)
    root_w = np.clip(1 - s_ / 0.6, 0, 1)
    left = smoothstep(-0.02, 0.02, x)
    for sd, sw in (("L", left), ("R", 1 - left)):
        w = sash_w * sw * (1 - root_w)
        idx = np.where(w > 1e-3)[0]
        add_chain(extra, idx, chains[f"Sash_{sd}"]["bones"], hw[idx] * w[idx, None])
    # hakama panels: front / back centre of the trousers, blended with the legs, strongest at the hem
    for key, side_w in (("Hakama_F", (1 - smoothstep(-0.2, -0.14, y)) * (1 - sash_w)), ("Hakama_B", smoothstep(-0.07, -0.02, y))):
        c = chains[key]
        s_ = np.clip((0.0 - z) / 0.42 * 2, 0, 2)
        w = side_w * (1 - smoothstep(0.08, 0.17, np.abs(x))) * smoothstep(0.0, -0.06, z) * smoothstep(-0.50, -0.42, z) * np.clip(s_ / 2, 0, 1) * 0.55
        idx = np.where(w > 1e-3)[0]
        add_chain(extra, idx, c["bones"], hat_weights(s_[idx], 2) * w[idx, None])
    apply_weights(body, W, names_r15, extra)
    smooth_groups(body, iterations=3)

    # ---- cape and mane: procedural chain weights
    for ob, P, prefix, top, bot, nb, root in ((cape, PC, "Cape", cz_top, cz_bot, 4, "UpperTorso"), (mane, PM, "Mane", mz_top, mz_bot, 3, "Head")):
        groups = {}
        s = (top - P[:, 2]) / (top - bot) * nb
        root_w = np.clip(1 - s / 0.6, 0, 1)
        if prefix == "Cape":
            th = np.degrees(np.arctan2(P[:, 0], P[:, 1] - CY))
            cols = [("R", -side), ("C", 0.0), ("L", side)]
            cw = np.stack([np.maximum(0, 1 - np.abs(np.clip(th, -side, side) - t0) / side) for _, t0 in cols], 1)
            names = [[f"Cape_{c}_{i}" for i in range(1, 5)] for c, _ in cols]
        else:
            th = np.degrees(np.arctan2(P[:, 0], P[:, 1] - (CY - 0.02)))
            cw = np.stack([np.maximum(0, 1 - np.abs(np.clip(th, centres[0], centres[-1]) - t0) / (np.diff(centres).mean())) for t0 in centres], 1)
            names = [[f"Mane_{i}_{k}" for k in range(1, 4)] for i in range(1, 7)]
        cw /= cw.sum(1, keepdims=True) + 1e-9
        hw = hat_weights(s, nb)
        groups[root] = root_w
        for ci, col_names in enumerate(names):
            for bi, bn in enumerate(col_names):
                groups[bn] = cw[:, ci] * hw[:, bi] * (1 - root_w)
        set_groups(ob, groups, arm)
    return arm, chains


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def analytic_body_weights(P):
    """Per-vertex R15 weights from position: segment by body region, blend smoothly across each joint.
    Joint positions come from J (cross-section measurements)."""
    x, y, z = P.T
    ax = np.abs(x)
    el, wr = J["elbow"][0], J["wrist"][0]
    kn, an = J["knee"][2], J["ankle"][2]
    # arms: out past the shoulder, above the armpit, and not behind the back plane (the cape remnant stays torso)
    armw = smoothstep(0.16, 0.24, ax) * smoothstep(0.37, 0.42, z) * (1 - smoothstep(-0.01, 0.03, y))
    up_lo = smoothstep(el - 0.035, el + 0.035, ax)
    lo_hd = smoothstep(wr - 0.025, wr + 0.025, ax)
    head = smoothstep(0.585, 0.665, z) * (1 - smoothstep(0.15, 0.2, ax) * (1 - smoothstep(0.64, 0.70, z)))
    rest = (1 - armw) * (1 - head)
    ut = smoothstep(0.13, 0.27, z)
    legw = 1 - smoothstep(-0.13, 0.0, z)
    lt_legs = rest * (1 - ut)
    left = smoothstep(-0.03, 0.03, x)
    ul_ll = smoothstep(kn - 0.05, kn + 0.05, z)          # 1 above the knee
    ll_ft = smoothstep(an - 0.03, an + 0.03, z)          # 1 above the ankle
    g = {"Head": (1 - armw) * head, "UpperTorso": rest * ut, "LowerTorso": lt_legs * (1 - legw)}
    for side, sw_arm, sw_leg in (("Left", (x > 0).astype(float), left), ("Right", (x <= 0).astype(float), 1 - left)):
        a = armw * sw_arm
        g[f"{side}UpperArm"] = a * (1 - up_lo)
        g[f"{side}LowerArm"] = a * up_lo * (1 - lo_hd)
        g[f"{side}Hand"] = a * up_lo * lo_hd
        l = lt_legs * legw * sw_leg
        g[f"{side}UpperLeg"] = l * ul_ll
        g[f"{side}LowerLeg"] = l * (1 - ul_ll) * ll_ft
        g[f"{side}Foot"] = l * (1 - ul_ll) * (1 - ll_ft)
    return g


def smooth_groups(ob, iterations=3, keep=0.5):
    """Laplacian-smooth every vertex group over the mesh edges (removes speckle and hard seams), renormalise."""
    me = ob.data
    n = len(me.vertices)
    e = np.zeros(len(me.edges) * 2, int)
    me.edges.foreach_get("vertices", e)
    e = e.reshape(-1, 2)
    import scipy.sparse as sp
    A = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
    deg = np.asarray(A.sum(1)).ravel()
    names = [vg.name for vg in ob.vertex_groups]
    W = weight_matrix(ob, names)
    for _ in range(iterations):
        W = keep * W + (1 - keep) * (A @ W) / np.maximum(deg, 1)[:, None]
    W /= np.maximum(W.sum(1, keepdims=True), 1e-9)
    for vg in list(ob.vertex_groups):
        ob.vertex_groups.remove(vg)
    set_groups(ob, {nm: W[:, k] for k, nm in enumerate(names)}, None)


def weight_matrix(ob, names):
    n = len(ob.data.vertices)
    W = np.zeros((n, len(names)))
    gi = {ob.vertex_groups[nm].index: k for k, nm in enumerate(names) if nm in ob.vertex_groups}
    for v in ob.data.vertices:
        for g in v.groups:
            k = gi.get(g.group)
            if k is not None:
                W[v.index, k] = g.weight
    return W


def nearest_bone_weights(P, arm, _):
    names = [b[0] for b in R15 if b[0] != "HumanoidRootPart"]
    segs = [(arm.data.bones[n].head_local, arm.data.bones[n].tail_local) for n in names]
    out = np.zeros((len(P), len(names)))
    for i, p in enumerate(P):
        p = Vector(p)
        d = []
        for a, b in segs:
            ab = b - a
            t = max(0, min(1, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
            d.append((p - (a + ab * t)).length)
        out[i, int(np.argmin(d))] = 1
    return out


def add_chain(extra, idx, bones, w):
    for k, bn in enumerate(bones):
        a = extra.setdefault(bn, {})
        for i, val in zip(idx, w[:, k]):
            if val > 1e-4:
                a[i] = a.get(i, 0) + val


def apply_weights(ob, W, names, extra):
    n = len(ob.data.vertices)
    tot = np.zeros(n)
    for bn, d in extra.items():
        for i, val in d.items():
            tot[i] += val
    tot = np.clip(tot, 0, 0.95)
    s = W.sum(1, keepdims=True)
    W = W / np.where(s > 0, s, 1) * (1 - tot)[:, None]
    groups = {nm: W[:, k] for k, nm in enumerate(names)}
    for bn, d in extra.items():
        a = np.zeros(n)
        for i, val in d.items():
            a[i] = val
        a = a * np.where(tot > 0, np.clip(tot, 0, 0.95) / np.maximum(sum_extra(extra, n), 1e-9), 0)
        groups[bn] = a
    for vg in list(ob.vertex_groups):
        ob.vertex_groups.remove(vg)
    set_groups(ob, groups, None)


_sum_cache = {}


def sum_extra(extra, n):
    key = id(extra)
    if key not in _sum_cache:
        t = np.zeros(n)
        for d in extra.values():
            for i, val in d.items():
                t[i] += val
        _sum_cache[key] = t
    return _sum_cache[key]


def set_groups(ob, groups, arm):
    for nm, w in groups.items():
        vg = ob.vertex_groups.get(nm) or ob.vertex_groups.new(name=nm)
        w = np.asarray(w)
        for val in np.unique(np.round(w[w > 1e-3], 3)):
            idx = np.where(np.abs(np.round(w, 3) - val) < 1e-9)[0].tolist()
            vg.add(idx, float(val), "REPLACE")
    if arm is not None:
        ob.parent = arm
        if not any(m.type == "ARMATURE" for m in ob.modifiers):
            mod = ob.modifiers.new("Armature", "ARMATURE")
            mod.object = arm


# ================================================================ test pose + outputs
def test_pose(arm, chains, amount=1.0):
    """Deformation check pose. All rotations are in armature space (X = pitch: + swings a hanging part back,
    - swings it forward; Y = roll about the forward axis; Z = yaw) and compound down each chain."""
    def r(name, x=0, y=0, z=0):
        set_world_rot(arm, name, Euler((math.radians(x), math.radians(y), math.radians(z)), "XYZ"), amount)
    r("LeftUpperArm", 0, 58, 0); r("RightUpperArm", 0, -58, 0)          # arms down to the sides
    r("LeftLowerArm", 0, 0, -50); r("RightLowerArm", 0, 0, 50)          # elbows bent forward
    r("LeftUpperLeg", -32, 0, 0); r("LeftLowerLeg", 45, 0, 0)           # left leg forward, knee bent
    r("RightUpperLeg", 14, 0, 0)
    r("UpperTorso", 0, 0, 12); r("Head", 0, 0, 22)                     # torso twist + head turn
    for col in "LCR":
        for i in range(1, 5):
            r(f"Cape_{col}_{i}", 7 if i == 1 else 11)
    for i in range(1, 7):
        for k in range(1, 4):
            r(f"Mane_{i}_{k}", 9)
    for sd in "LR":
        for bn in (f"Sash_{sd}_1", f"Sash_{sd}_2", f"Sash_{sd}_Tassel"):
            r(bn, -16)
    r("Hakama_F_1", -10); r("Hakama_B_1", 10)
    bpy.context.view_layer.update()


def set_world_rot(arm, name, e, amount):
    """Rotate a bone in armature space (so 'down' is down regardless of the bone roll)."""
    pb = arm.pose.bones[name]
    pb.rotation_mode = "QUATERNION"
    rest = arm.data.bones[name].matrix_local.to_3x3()
    q_arm = Euler((e.x * amount, e.y * amount, e.z * amount), "XYZ").to_quaternion()
    q_local = (rest.inverted() @ q_arm.to_matrix() @ rest).to_quaternion()
    pb.rotation_quaternion = q_local


def bone_sticks(arm, name="XRAY_Bones"):
    """Thin octahedral sticks for every bone (for skeleton overlay renders)."""
    V, F = [], []
    for b in arm.data.bones:
        h, t = arm.matrix_world @ b.head_local, arm.matrix_world @ b.tail_local
        d = t - h
        L = d.length
        if L < 1e-5:
            continue
        ax = d.normalized()
        up = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
        u = ax.cross(up).normalized() * min(0.012, L * 0.12)
        w = ax.cross(u).normalized() * min(0.012, L * 0.12)
        m = h + d * 0.2
        o = len(V)
        V += [h, m + u, m + w, m - u, m - w, t]
        F += [(o, o + 1, o + 2), (o, o + 2, o + 3), (o, o + 3, o + 4), (o, o + 4, o + 1),
              (o + 5, o + 2, o + 1), (o + 5, o + 3, o + 2), (o + 5, o + 4, o + 3), (o + 5, o + 1, o + 4)]
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in V], [], F)
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    mat = bpy.data.materials.new("XRAY_bone")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.75, 0.1, 1)
    me.materials.append(mat)
    return ob


def export_glb(path, objs, apply=False):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=apply,
                              export_skins=not apply, export_animations=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(ROOT, "assets", "meshes", "thunder_god", "thunder_god_clean.blend"))
    ap.add_argument("--out", default=os.path.join(ROOT, "assets", "meshes", "thunder_god"))
    ap.add_argument("--preview", default=None, help="dir for preview GLBs (skeleton overlay, test pose)")
    ap.add_argument("--export", action="store_true")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    arm, chains = build(a.src)
    parts = [bpy.data.objects[n] for n in ("Body", "Cape", "Mane")]
    info = {"bones": [b.name for b in arm.data.bones], "chains": {k: v["bones"] for k, v in chains.items()},
            "tris": {o.name: len(o.data.polygons) for o in parts}}
    print("bones", len(info["bones"]))
    with open(os.path.join(a.out, "thunder_god_rig.json"), "w") as f:
        json.dump(info, f, indent=1)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(a.out, "thunder_god_rig.blend"))
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        sticks = bone_sticks(arm)
        export_glb(os.path.join(a.preview, "rest_bones.glb"), parts + [sticks], apply=True)
        bpy.data.objects.remove(sticks)
        for amt, tag in ((1.0, "pose"), (1.8, "pose_strong")):
            test_pose(arm, chains, amt)
            sticks = bone_sticks_posed(arm)
            export_glb(os.path.join(a.preview, f"{tag}.glb"), parts, apply=True)
            export_glb(os.path.join(a.preview, f"{tag}_bones.glb"), parts + [sticks], apply=True)
            bpy.data.objects.remove(sticks)
            for p in arm.pose.bones:
                p.rotation_mode = "QUATERNION"
                p.rotation_quaternion = (1, 0, 0, 0)
    if a.export:
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.export_scene.fbx(filepath=os.path.join(a.out, "thunder_god.fbx"), use_selection=False, add_leaf_bones=False,
                                 axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True, bake_anim=False)


def bone_sticks_posed(arm):
    """Sticks at the posed bone positions."""
    V, F = [], []
    for pbn in arm.pose.bones:
        h, t = arm.matrix_world @ pbn.head, arm.matrix_world @ pbn.tail
        d = t - h
        L = d.length
        if L < 1e-5:
            continue
        ax = d.normalized()
        up = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
        u = ax.cross(up).normalized() * min(0.012, L * 0.12)
        w = ax.cross(u).normalized() * min(0.012, L * 0.12)
        m = h + d * 0.2
        o = len(V)
        V += [h, m + u, m + w, m - u, m - w, t]
        F += [(o, o + 1, o + 2), (o, o + 2, o + 3), (o, o + 3, o + 4), (o, o + 4, o + 1),
              (o + 5, o + 2, o + 1), (o + 5, o + 3, o + 2), (o + 5, o + 4, o + 3), (o + 5, o + 1, o + 4)]
    me = bpy.data.meshes.new("XRAY_Bones")
    me.from_pydata([tuple(v) for v in V], [], F)
    ob = bpy.data.objects.new("XRAY_Bones", me)
    bpy.context.collection.objects.link(ob)
    mat = bpy.data.materials.get("XRAY_bone") or bpy.data.materials.new("XRAY_bone")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.75, 0.1, 1)
    me.materials.append(mat)
    return ob


if __name__ == "__main__":
    main()
