"""Dragon (full form): Meshy v5 body + head -> one game-ready rigged mesh.

    /tmp/bpyenv/bin/python scripts/rig_dragon.py [--length 30] [--head-tris 9500] [--body-tris 8500] [--pose-test out.glb]

Built on scripts/build_dragon.py (assemble) and the serpent pipeline (scripts/rig_serpent.py):
  head (in its own Meshy coordinates, snout -Y, Z up), before it is seated on the body
    - the Meshy whiskers are fused into the mesh and lumpy: they are cut away (below the chin, in front of the lower
      jaw, and the blue strands crossing the open mouth) and replaced by two clean procedural whiskers, one per side
    - the sheet's mouth is modelled OPEN: the lower jaw (below the bisector of the open lips, forward of the hinge) is
      rotated shut by --close degrees and baked, so the rest pose is closed and `jaw` keys open it (same convention as
      the thunder serpent). A falloff at the hinge bends the cheeks instead of tearing them
    - decimated to --head-tris before the whiskers are added
  body: decimated to --body-tris
  joined (one 2048 atlas), turned so the head points along glTF -Z (Roblox forward), scaled to --length studs
  armature
    spine_00 (head, rigid) .. spine_19 (tail tip), a chain along the body
    jaw (child of spine_00, hinge at the back of the mouth)
    legFL/FR/BL/BR_0 (upper) and _1 (lower), children of the nearest spine bone (L = dragon's left = -X)
    whiskerL/R_0..2, children of spine_00
  weights: head rigid, body smooth between the two nearest spine bones, legs by distance from the body side,
  whiskers by position along the strand
Outputs
  assets/models/dragon.glb (previewer), assets/meshes/dragon.fbx (Roblox skinned MeshPart), assets/models/dragon.json
  --pose-test OUT.glb: an extra static copy posed by the bones (jaw open, S-curve, legs and whiskers bent) to check
  the weights with lab/model_views.mjs
"""
import argparse
import json
import math
import os
import sys

import bpy  # noqa: I001
import bmesh
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_dragon  # noqa: E402

ROOT = os.path.join(HERE, "..")
NB = 20
# head-space landmarks (dragon_v5_head.glb: snout -Y, Z up, about 1.1 wide)
HINGE = (-0.12, -0.16)                 # (y, z) back of the mouth
BISECT = (-0.970, -0.242)              # direction from the hinge between the open lips (y, z)
JAW_HALF_W = 0.25
WHISKER_PATH = [(0.10, -0.53, -0.06), (0.20, -0.66, -0.10), (0.36, -0.67, -0.28), (0.47, -0.53, -0.55),
                (0.54, -0.31, -0.80), (0.58, -0.06, -1.00)]   # x for the dragon's +X side (mirrored for -X)
WHISKER_R = (0.032, 0.006)


def vert_colors(me, img):
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    col = np.zeros((len(me.vertices), 3))
    cnt = np.zeros(len(me.vertices))
    uv = me.uv_layers.active.data
    for lp in me.loops:
        u, v = uv[lp.index].uv
        col[lp.vertex_index] += px[min(h - 1, max(0, int(v * h))), min(w - 1, max(0, int(u * w))), :3]
        cnt[lp.vertex_index] += 1
    return col / np.maximum(cnt, 1)[:, None], px


def drop_small_islands(bm, min_size):
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    bm.verts.index_update()
    bm.verts.ensure_lookup_table()
    P = np.array([v.co[:] for v in bm.verts])
    E = [(e.verts[0].index, e.verts[1].index) for e in bm.edges]
    _, inv = np.unique(np.round(P / 1e-5).astype(np.int64), axis=0, return_inverse=True)
    inv = inv.ravel()
    order = np.argsort(inv)
    same = [(order[i], order[i + 1]) for i in range(len(order) - 1) if inv[order[i]] == inv[order[i + 1]]]
    pairs = np.array(E + same)
    g = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(len(P), len(P)))
    _, lab = connected_components(g, directed=False)
    sizes = np.bincount(lab)
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in np.where(sizes[lab] < min_size)[0]], context="VERTS")


def decimate(o, tris):
    t0 = sum(len(p.vertices) - 2 for p in o.data.polygons)
    if t0 <= tris:
        return
    bpy.context.view_layer.objects.active = o
    m = o.modifiers.new("dec", "DECIMATE")
    m.ratio = tris / t0
    m.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=m.name)
    for p in o.data.polygons:
        p.use_smooth = True


def catmull(points, n):
    P = [np.array(p, float) for p in points]
    P = [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return np.array(out)


def make_head_hook(a):
    def hook(head):
        me = head.data
        img = build_dragon.tex_of(head)
        col, px = vert_colors(me, img)
        V = np.array([v.co[:] for v in me.vertices])
        hy, hz = HINGE
        dy, dz = BISECT
        up = np.array([dz, -dy]) if -dy > 0 else np.array([-dz, dy])   # perpendicular to the bisector, pointing up (z+)
        rel = np.stack([V[:, 1] - hy, V[:, 2] - hz], 1)
        side = rel @ up                                            # >0 upper jaw side, <0 lower
        along = rel @ np.array([dy, dz])
        blue = (col[:, 2] > col[:, 0] + 0.12) & ~((col[:, 0] > col[:, 2] + 0.1))
        whisker_blue = (col[:, 2] - col[:, 1] > 0.25) & (col[:, 2] > 0.5)   # the strands' saturated blue (scales are teal)
        # ---- 1. cut the Meshy whiskers
        kill = ((V[:, 2] < -0.575) & (V[:, 1] < -0.12) & (np.abs(V[:, 0]) < 0.35)) \
            | ((V[:, 1] < -0.485) & (V[:, 2] < -0.17)) \
            | ((np.abs(side) < 0.06) & (V[:, 1] < -0.28) & blue) \
            | (whisker_blue & (V[:, 1] < -0.2) & (V[:, 2] < -0.05))
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[i] for i in np.where(kill)[0]], context="VERTS")
        drop_small_islands(bm, 300)
        bm.to_mesh(me)
        bm.free()
        # ---- 2. close the jaw: rotate the lower jaw about the hinge (X axis), baked into the rest pose
        V = np.array([v.co[:] for v in me.vertices])
        rel = np.stack([V[:, 1] - hy, V[:, 2] - hz], 1)
        side = rel @ up
        fwd = np.clip((hy - V[:, 1]) / 0.08, 0, 1)                 # 0 at the hinge -> 1 a bit forward
        fwd = fwd * fwd * (3 - 2 * fwd)
        lat = np.clip((JAW_HALF_W + 0.05 - np.abs(V[:, 0])) / 0.05, 0, 1)
        below = np.clip(-side / 0.02, 0, 1)
        wj = fwd * lat * below
        th = -math.radians(a.close) * wj                           # clockwise in (y, z): lower jaw swings up
        c, s = np.cos(th), np.sin(th)
        y2 = hy + rel[:, 0] * c - rel[:, 1] * s
        z2 = hz + rel[:, 0] * s + rel[:, 1] * c
        for i, v in enumerate(me.vertices):
            v.co = (V[i, 0], y2[i], z2[i])
        g = head.vertex_groups.new(name="jawW")
        for i in np.where(wj > 0.001)[0]:
            g.add([int(i)], float(wj[i]), "REPLACE")
        # ---- 3. decimate the head
        decimate(head, a.head_tris)
        # ---- 4. procedural whiskers: tapered 6-sided tubes along a Catmull-Rom path, UVs on a whisker-blue texel
        h_, w_ = px.shape[:2]
        target = np.array([0.16, 0.42, 0.80])
        d = np.linalg.norm(px[..., :3] - target, axis=-1) + (px[..., 3] < 0.5) * 9
        ty, tx = np.unravel_index(np.argmin(d), d.shape)
        uvb = ((tx + 0.5) / w_, (ty + 0.5) / h_)
        bm = bmesh.new()
        bm.from_mesh(me)
        uvl = bm.loops.layers.uv.active
        dl = bm.verts.layers.deform.verify()
        names = {}
        # head space +X ends up as final -X after the 180 deg turn, and -X is the dragon's left
        for side_name, sx in (("whL", 1), ("whR", -1)):
            names[side_name] = head.vertex_groups.new(name=side_name).index
        for side_name, sx in (("whL", 1), ("whR", -1)):
            path = catmull([(sx * x, y, z) for x, y, z in WHISKER_PATH], 6)
            gi = names[side_name]
            rings = []
            n = len(path)
            for k in range(n):
                t = k / (n - 1)
                tan = path[min(k + 1, n - 1)] - path[max(k - 1, 0)]
                tan /= np.linalg.norm(tan)
                ref = np.array([1.0, 0, 0]) if abs(tan[0]) < 0.9 else np.array([0, 0, 1.0])
                u1 = np.cross(tan, ref); u1 /= np.linalg.norm(u1)
                u2 = np.cross(tan, u1)
                r = WHISKER_R[0] + (WHISKER_R[1] - WHISKER_R[0]) * t
                ring = []
                for j in range(6):
                    ang = 2 * math.pi * j / 6
                    vv = bm.verts.new(tuple(path[k] + r * (math.cos(ang) * u1 + math.sin(ang) * u2)))
                    vv[dl][gi] = max(0.001, t)
                    ring.append(vv)
                rings.append(ring)
            for k in range(n - 1):
                for j in range(6):
                    f = bm.faces.new((rings[k][j], rings[k][(j + 1) % 6], rings[k + 1][(j + 1) % 6], rings[k + 1][j]))
                    for lp in f.loops:
                        lp[uvl].uv = uvb
            tip = bm.verts.new(tuple(path[-1] + (path[-1] - path[-2]) * 0.5))
            tip[dl][gi] = 1.0
            for j in range(6):
                f = bm.faces.new((rings[-1][j], rings[-1][(j + 1) % 6], tip))
                for lp in f.loops:
                    lp[uvl].uv = uvb
        bm.to_mesh(me)
        bm.free()
    return hook


def make_body_hook(a):
    def hook(body):
        decimate(body, a.body_tris)
    return hook


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--length", type=float, default=30.0)
    ap.add_argument("--head-scale", type=float, default=0.18)
    ap.add_argument("--head-tris", type=int, default=9500)
    ap.add_argument("--body-tris", type=int, default=8500)
    ap.add_argument("--close", type=float, default=46.0, help="degrees the modelled open jaw is rotated shut")
    ap.add_argument("--pose-test", default="")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

    bpy.ops.wm.read_factory_settings(use_empty=True)
    o, info = build_dragon.assemble(head_scale=a.head_scale, head_hook=make_head_hook(a), body_hook=make_body_hook(a))
    me = o.data
    HM = info["head_matrix"]
    for p in me.polygons:
        p.use_smooth = True

    # ---- turn (head -Y -> +Y = glTF -Z), scale to --length, centre
    V = np.array([v.co[:] for v in me.vertices])
    L0 = V[:, 1].max() - V[:, 1].min()
    k = a.length / L0
    R = Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Scale(k, 4)
    me.transform(R)
    V = np.array([v.co[:] for v in me.vertices])
    T = Matrix.Translation((0, -(V[:, 1].max() + V[:, 1].min()) / 2, -(V[:, 2].max() + V[:, 2].min()) / 2))
    me.transform(T)
    X = T @ R                                                       # assembled -> final
    toF = lambda p: np.array((X @ Vector(p))[:])
    headF = lambda y, z, x=0.0: toF(HM @ Vector((x, y, z)))
    V = np.array([v.co[:] for v in me.vertices])
    ymax, ymin = V[:, 1].max(), V[:, 1].min()
    L = ymax - ymin
    s_of = lambda y: (ymax - y) / L

    # landmarks (final coords)
    hinge = headF(*HINGE)
    chin = headF(HINGE[0] + BISECT[0] * 0.36, HINGE[1] + BISECT[1] * 0.36 - 0.08)
    neck_y = float(toF((0, -0.60, 0))[1])
    s_neck = s_of(neck_y)
    s_head = s_of(hinge[1])

    # body centre line (median z / x of the trunk cross-section, ignoring legs and spines)
    def centre(s, half=0.012):
        m = np.abs(s_of(V[:, 1]) - s) < half
        if not m.any():
            return 0.0, float(np.median(V[:, 2]))
        zz = V[m, 2]
        core = m & (V[:, 2] < np.percentile(zz, 85)) & (V[:, 2] > np.percentile(zz, 10))
        return float(np.median(V[core, 0])) if core.any() else 0.0, float(np.median(V[core, 2])) if core.any() else float(np.median(zz))

    s_b = [s_head] + [s_neck + (0.985 - s_neck) * i / (NB - 2) for i in range(NB - 1)]
    cen = [centre(s) for s in s_b]
    cen[0] = (0.0, float(hinge[2]))

    # legs: wide-and-low clusters along the body (measured from the trunk's centre line, not the local median, which a
    # leg drags sideways)
    xc_body = float(np.median([centre(q)[0] for q in np.linspace(0.3, 0.48, 10)]))
    body_hw = []
    leg_zones = []
    for s0 in np.arange(s_neck, 0.97, 0.01):
        m = np.abs(s_of(V[:, 1]) - s0) < 0.005
        if m.any():
            body_hw.append((s0, float(np.percentile(np.abs(V[m, 0] - xc_body), 98))))
    hw_med = float(np.median([h for _, h in body_hw]))
    wide = [s0 for s0, h in body_hw if h > hw_med * 1.45 and s0 < 0.8]
    zones = []
    for s0 in wide:
        if zones and s0 - zones[-1][1] < 0.025:
            zones[-1][1] = s0
        else:
            zones.append([s0, s0])
    zones = [z for z in zones if z[1] - z[0] > 0.01][:2]
    if len(zones) < 2:
        raise SystemExit(f"leg zones not found: {zones}")
    print("legs at s", [[round(x, 3) for x in z] for z in zones], "body half-width", round(hw_med, 3))

    # ---- armature
    arm_data = bpy.data.armatures.new("DragonRig")
    arm = bpy.data.objects.new("DragonRig", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    y_of = lambda s: ymax - s * L
    prev = None
    for i, s in enumerate(s_b):
        b = arm_data.edit_bones.new(f"spine_{i:02d}")
        b.head = (cen[i][0], y_of(s), cen[i][1])
        nxt = s_b[i + 1] if i + 1 < NB else 1.0
        cn = cen[min(i + 1, NB - 1)]
        b.tail = (cn[0], y_of(nxt), cn[1])
        b.roll = 0
        if prev:
            b.parent = prev
            b.use_connect = True
        prev = b
    eb = arm_data.edit_bones
    j = eb.new("jaw")
    j.head = tuple(hinge)
    j.tail = tuple(chin)
    j.roll = 0
    j.parent = eb["spine_00"]
    legs = {}
    for zi, (za, zb) in enumerate(zones):
        sc = (za + zb) / 2
        parent = min(range(1, NB), key=lambda i: abs(s_b[i] - sc))
        xc, zc = xc_body, centre(sc)[1]
        m = (np.abs(s_of(V[:, 1]) - sc) < (zb - za) / 2 + 0.01)
        for side, sx in (("L", -1), ("R", 1)):
            mm = m & (sx * (V[:, 0] - xc) > hw_med * 1.05)
            if not mm.any():
                raise SystemExit(f"no leg verts zone {zi} side {side} xc {xc:.3f} x-range {V[m, 0].min():.3f} {V[m, 0].max():.3f} n {m.sum()}")
            P = V[mm]
            far = P[np.argsort(sx * (P[:, 0] - xc))[-max(5, len(P) // 20):]].mean(0)       # foot
            shoulder = np.array([xc + sx * hw_med * 0.9, P[:, 1].mean(), zc - 0.15 * (zc - P[:, 2].min())])
            knee = shoulder * 0.45 + far * 0.55 + np.array([0, 0, 0.08 * L / 30])
            nm = f"leg{'F' if zi == 0 else 'B'}{side}"
            b0 = eb.new(nm + "_0"); b0.head, b0.tail = tuple(shoulder), tuple(knee); b0.parent = eb[f"spine_{parent:02d}"]; b0.roll = 0
            b1 = eb.new(nm + "_1"); b1.head, b1.tail = tuple(knee), tuple(far); b1.parent = b0; b1.use_connect = True; b1.roll = 0
            legs[nm] = (sc, (zb - za) / 2 + 0.01, xc, sx, shoulder, knee, far)
    wh_bones = {}
    for side, grp in (("L", "whL"), ("R", "whR")):
        gi = o.vertex_groups[grp].index
        pts = [(v.co[:], g.weight) for v in me.vertices for g in v.groups if g.group == gi]
        P = np.array([p for p, _ in pts]); t = np.array([w for _, w in pts])
        knots = [P[np.abs(t - q).argmin()] for q in (0.0, 0.33, 0.66, 1.0)]
        prevb = eb["spine_00"]
        for bi in range(3):
            b = eb.new(f"whisker{side}_{bi}")
            b.head, b.tail = tuple(knots[bi]), tuple(knots[bi + 1])
            b.parent = prevb
            if bi:
                b.use_connect = True
            b.roll = 0
            prevb = b
        wh_bones[grp] = (gi, knots)
    bpy.ops.object.mode_set(mode="OBJECT")

    # ---- weights
    bones = [f"spine_{i:02d}" for i in range(NB)] + ["jaw"] + [f"{n}_{q}" for n in legs for q in (0, 1)] + \
        [f"whisker{s}_{i}" for s in "LR" for i in range(3)]
    G = {n: o.vertex_groups.new(name=n) for n in bones}
    jaw_gi = o.vertex_groups["jawW"].index
    co = np.array([v.co[:] for v in me.vertices])
    for vi, v in enumerate(me.vertices):
        p = co[vi]
        gw = {g.group: g.weight for g in v.groups}
        W = {}
        whisker = [(grp, gw[gi]) for grp, (gi, _) in wh_bones.items() if gi in gw]
        if whisker:
            grp, t = whisker[0]
            side = "L" if grp == "whL" else "R"
            f = t * 3
            if t < 0.06:
                W["spine_00"] = 1.0
            else:
                i0 = int(min(2, f)); r = f - i0
                W[f"whisker{side}_{i0}"] = 1 - r * 0.5 if i0 < 2 else 1.0
                if i0 < 2:
                    W[f"whisker{side}_{i0 + 1}"] = r * 0.5
        else:
            s = s_of(p[1])
            if s < s_neck:
                wj = gw.get(jaw_gi, 0.0)
                if wj > 0:
                    W["jaw"] = wj
                if wj < 1:
                    W["spine_00"] = 1 - wj
            else:
                f = (s - s_neck) / (0.985 - s_neck) * (NB - 2) + 1
                i0 = int(min(NB - 2, max(1, math.floor(f))))
                r = min(1.0, max(0.0, f - i0))
                W[f"spine_{i0:02d}"] = W.get(f"spine_{i0:02d}", 0) + 1 - r
                W[f"spine_{i0 + 1:02d}"] = W.get(f"spine_{i0 + 1:02d}", 0) + r
                for nm, (sc, half, xc, sx, sh, kn, ft) in legs.items():
                    if abs(s - sc) > half + 0.004:
                        continue
                    out = sx * (p[0] - xc)
                    reach = sx * (ft[0] - xc)
                    q = (out - hw_med * 0.85) / max(1e-6, reach - hw_med * 0.85)
                    if q <= 0:
                        continue
                    q = min(1.0, q)
                    leg_w = min(1.0, q / 0.25)
                    kq = sx * (kn[0] - xc)
                    kt = (out - kq) / max(1e-6, reach - kq)
                    lower = min(1.0, max(0.0, 0.5 + kt / 0.3))
                    for key in list(W):
                        W[key] *= 1 - leg_w
                    W[nm + "_0"] = leg_w * (1 - lower)
                    W[nm + "_1"] = leg_w * lower
        tot = sum(W.values()) or 1.0
        for n, w in W.items():
            if w > 1e-4:
                G[n].add([vi], w / tot, "REPLACE")
    for gname in ("jawW", "whL", "whR"):
        o.vertex_groups.remove(o.vertex_groups[gname])
    mod = o.modifiers.new("arm", "ARMATURE")
    mod.object = arm
    o.parent = arm

    # ---- export
    os.makedirs(os.path.join(ROOT, "assets", "models"), exist_ok=True)
    glb = os.path.join(ROOT, "assets", "models", "dragon.glb")
    fbx = os.path.join(ROOT, "assets", "meshes", "dragon.fbx")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_skins=True, export_animations=False)
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, add_leaf_bones=False, bake_anim=False, path_mode="COPY",
                             embed_textures=True, axis_forward="-Z", axis_up="Y")
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    info_out = {"length_studs": a.length, "tris": tris, "bones": bones, "spine_s": s_b, "neck_s": s_neck,
                "jaw_close_deg": a.close, "legs": {n: {"s": v[0]} for n, v in legs.items()},
                "note": "rest pose = jaw closed; jaw keys open it (positive = open)"}
    json.dump(info_out, open(os.path.join(ROOT, "assets", "models", "dragon.json"), "w"), indent=1)
    print("RIG", json.dumps({k: info_out[k] for k in ("tris", "length_studs")}), "bones", len(bones))

    if a.pose_test:
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="POSE")
        pb = arm.pose.bones
        pb["jaw"].rotation_mode = "XYZ"
        pb["jaw"].rotation_euler = (math.radians(35), 0, 0)
        for i in range(1, NB):
            pb[f"spine_{i:02d}"].rotation_mode = "XYZ"
            pb[f"spine_{i:02d}"].rotation_euler = (0, 0, math.radians(14 * math.sin(i * 0.7)))
        for n in legs:
            pb[n + "_0"].rotation_mode = pb[n + "_1"].rotation_mode = "XYZ"
            pb[n + "_0"].rotation_euler = (math.radians(30), 0, 0)
            pb[n + "_1"].rotation_euler = (math.radians(-40), 0, 0)
        for side in "LR":
            for i in range(3):
                pb[f"whisker{side}_{i}"].rotation_mode = "XYZ"
                pb[f"whisker{side}_{i}"].rotation_euler = (math.radians(25), 0, 0)
        bpy.ops.object.mode_set(mode="OBJECT")
        dg = bpy.context.evaluated_depsgraph_get()
        posed = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        po = bpy.data.objects.new("Posed", posed)
        bpy.context.scene.collection.objects.link(po)
        bpy.ops.object.select_all(action="DESELECT")
        po.select_set(True)
        bpy.ops.export_scene.gltf(filepath=a.pose_test, export_format="GLB", use_selection=True)
        print("posed", a.pose_test)


if __name__ == "__main__":
    main()
