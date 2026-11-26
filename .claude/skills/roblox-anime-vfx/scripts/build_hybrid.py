"""Dragon hybrid (the BASE form, DESIGN.md "Revision v5"): horns, a tail and a few scales on the player's own R15 body,
all kitbashed from the full-form dragon so they match it exactly and share its one texture atlas.

    /tmp/bpyenv/bin/python scripts/build_hybrid.py

Pieces (each authored around the centre of the R15 part it welds to; studs; Roblox frame: Y up, facing -Z)
  dragon_hybrid_head   the dragon's horns + back pair (from the head mesh) + two skin-scale patches on the sides of the
                       head. Rigid, welded to Head.
  dragon_hybrid_torso  skin-scale patches on both sides of the torso. Rigid, welded to UpperTorso.
  dragon_hybrid_tail   the last ~35% of the dragon's tail with the curl fan, ~4.6 studs, from the back of the hips,
                       angled back and down. Skinned, bones tail_0 .. tail_6. Welded to LowerTorso.
Inputs: build_dragon.assemble() (the Meshy v5 head + body joined, one 2048 atlas).
Outputs: assets/models/<piece>.glb (previewer `attach` layers), assets/meshes/<piece>.fbx (Roblox, into
AnimeVFX.Models), assets/models/dragon_hybrid.json.
"""
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
from rig_dragon import decimate  # noqa: E402

ROOT = os.path.join(HERE, "..")
# Blender authoring frame for the pieces: forward +Y, up +Z, right +X (exports to glTF/Roblox -Z forward, Y up)
HEAD_HALF = 0.6            # blocky R15 head ~1.2 studs
TORSO_HALF = (1.0, 0.8, 0.5)   # UpperTorso 2 x 1.6 x 1 (x, height, depth)
TAIL_LEN = 4.6
NT = 7


def colors(me, img):
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    col = np.zeros((len(me.vertices), 3))
    cnt = np.zeros(len(me.vertices))
    uv = me.uv_layers.active.data
    for lp in me.loops:
        u, v = uv[lp.index].uv
        col[lp.vertex_index] += px[min(h - 1, max(0, int(v * h))), min(w - 1, max(0, int(u * w))), :3]
        cnt[lp.vertex_index] += 1
    return col / np.maximum(cnt, 1)[:, None]


def extract(src, keep_mask, name):
    """Copy of `src` with only faces whose vertices are all in keep_mask."""
    o = src.copy()
    o.data = src.data.copy()
    o.name = o.data.name = name
    bpy.context.scene.collection.objects.link(o)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not all(keep_mask[v.index] for v in f.verts)], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(o.data)
    bm.free()
    for g in list(o.vertex_groups):
        o.vertex_groups.remove(g)
    return o


def transform(o, M):
    o.data.transform(M)
    o.data.update()


def verts(o):
    return np.array([v.co[:] for v in o.data.vertices])


def mirror_x(o, name):
    m = o.copy()
    m.data = o.data.copy()
    m.name = m.data.name = name
    bpy.context.scene.collection.objects.link(m)
    m.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
    m.data.flip_normals()
    return m


def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = o.data.name = name
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def scale_patch(src, name, y0, y1, z0, z1, size, flatten=0.35):
    """A curved plate of skin scales cut from the side of the body (assembled coords, side facing +X), recentred,
    curvature reduced, scaled so its larger side is `size` studs; returned facing +X with its centre at the origin."""
    V = verts(src)
    keep = (V[:, 1] > y0) & (V[:, 1] < y1) & (V[:, 2] > z0) & (V[:, 2] < z1) & (V[:, 0] > 0.035)
    p = extract(src, keep, name)
    P = verts(p)
    c = P.mean(0)
    P = P - c
    P[:, 0] *= flatten
    ext = max(np.ptp(P[:, 1]), np.ptp(P[:, 2]))
    P *= size / ext
    P[:, 0] -= P[:, 0].min()                    # inner face sits on x = 0 (the avatar surface)
    for i, v in enumerate(p.data.vertices):
        v.co = P[i]
    p.data.update()
    return p


def export(objs, name, sel_extra=()):
    bpy.ops.object.select_all(action="DESELECT")
    for o in list(objs) + list(sel_extra):
        o.select_set(True)
    glb = os.path.join(ROOT, "assets", "models", f"{name}.glb")
    fbx = os.path.join(ROOT, "assets", "meshes", f"{name}.fbx")
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_skins=True, export_animations=False)
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, add_leaf_bones=False, bake_anim=False, path_mode="COPY",
                             embed_textures=True, axis_forward="-Z", axis_up="Y")
    tris = sum(len(p.vertices) - 2 for o in objs if o.type == "MESH" for p in o.data.polygons)
    return tris


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    src, info = build_dragon.assemble()
    HM = info["head_matrix"]
    me = src.data
    col = colors(me, info["atlas"])
    V = verts(src)
    HMi = HM.inverted()
    head_s = info["head_matrix"].to_scale()[0]
    uvside = np.zeros(len(V))
    uv = me.uv_layers.active.data
    for lp in me.loops:
        uvside[lp.vertex_index] = max(uvside[lp.vertex_index], uv[lp.index].uv[0])
    is_head = uvside >= 0.5                                         # head verts live in the atlas's right half
    Hs = np.array([(HMi @ Vector(p))[:] for p in V])                # head-space coords (snout -Y, Z up)
    cream = (col[:, 0] > 0.55) & (col[:, 1] > 0.5) & (col[:, 0] > col[:, 2] + 0.08)

    # ---- horns: cream verts above the brow on the head (head space z > 0.3)
    horn_keep = is_head & cream & (Hs[:, 2] > 0.30)
    horns = extract(src, horn_keep, "horns")
    from rig_dragon import drop_small_islands
    bm = bmesh.new()
    bm.from_mesh(horns.data)
    drop_small_islands(bm, 250)                                    # brow spikes / teeth caught by the colour test
    bm.to_mesh(horns.data)
    bm.free()
    # head space -> authoring frame: turn 180 about Z (snout -Y -> forward +Y), scale so the horn roots straddle the
    # R15 head, lift the roots to the head's top
    HV = np.array([(HMi @ v.co)[:] for v in horns.data.vertices])
    root_z = np.percentile(HV[:, 2], 4)
    k_h = 2.9
    M = Matrix.Translation((0, -0.05, HEAD_HALF - 0.22)) @ Matrix.Scale(k_h, 4) @ Matrix.Rotation(math.pi, 4, "Z") @ \
        Matrix.Translation((0, 0.12, -root_z)) @ HMi
    transform(horns, M)
    decimate(horns, 2400)

    # ---- head-side scales (left/right)
    sh_r = scale_patch(src, "scaleHeadR", -0.32, -0.22, -0.07, 0.035, 0.75)
    transform(sh_r, Matrix.Translation((HEAD_HALF + 0.005, -0.08, -0.05)) @ Matrix.Rotation(math.radians(-8), 4, "Y"))
    sh_l = mirror_x(sh_r, "scaleHeadL")
    head_piece = join([horns, sh_r, sh_l], "dragon_hybrid_head")

    # ---- torso scales: on the front and back corners of the torso, wrapping its sides (R15 arms hang over the sides
    # themselves, so plates there never show)
    plates = []
    for nm, (x, y, z), face, size in (("FrontR", (0.62, 0.0, -0.18), 90, 0.95), ("FrontR2", (0.78, 0.0, 0.42), 90, 0.55),
                                      ("BackR", (0.6, 0.0, -0.05), -90, 1.0), ("BackR2", (0.8, 0.0, 0.5), -90, 0.5)):
        pl = scale_patch(src, "scaleTorso" + nm, -0.20, -0.06, -0.08, 0.04, size) if size > 0.7 else \
            scale_patch(src, "scaleTorso" + nm, 0.24, 0.32, -0.07, 0.03, size)
        yy = (TORSO_HALF[2] + 0.005) * (1 if face > 0 else -1)
        transform(pl, Matrix.Translation((x, yy, z)) @ Matrix.Rotation(math.radians(face), 4, "Z"))
        plates += [pl, mirror_x(pl, "scaleTorso" + nm.replace("R", "L"))]
    torso_piece = join(plates, "dragon_hybrid_torso")

    # ---- tail: body y > 0.30 (assembled coords: tail toward +Y), root at the back of the hips, angled back and down
    tail_keep = (~is_head) & (V[:, 1] > 0.30)
    tail = extract(src, tail_keep, "dragon_hybrid_tail")
    TV = verts(tail)
    y0 = TV[:, 1].min()
    root_c = TV[TV[:, 1] < y0 + 0.02].mean(0)
    L0 = TV[:, 1].max() - y0
    k_t = TAIL_LEN / L0
    droop = math.radians(32)          # +X rotation tips the -Y tail down
    Mt = Matrix.Translation((0, -0.42, -0.05)) @ Matrix.Rotation(droop, 4, "X") @ Matrix.Scale(k_t, 4) @ \
        Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation((-root_c[0], -root_c[1], -root_c[2]))
    transform(tail, Mt)
    decimate(tail, 3000)
    for p in tail.data.polygons:
        p.use_smooth = True
    TV = verts(tail)
    # bones along the tail's centre line
    dirv = np.array([0, -math.cos(droop), -math.sin(droop)])     # back (-Y) and down
    s = TV @ dirv
    s0, s1 = s.min(), s.max()
    arm_data = bpy.data.armatures.new("HybridTailRig")
    arm = bpy.data.objects.new("HybridTailRig", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    knots = []
    for i in range(NT + 1):
        q = s0 + (s1 - s0) * (i / NT) * 0.97
        m = np.abs(s - q) < (s1 - s0) / NT * 0.5
        knots.append(TV[m].mean(0) if m.any() else np.array([0, 0, 0]) + dirv * q)
    prev = None
    for i in range(NT):
        b = arm_data.edit_bones.new(f"tail_{i}")
        b.head, b.tail = tuple(knots[i]), tuple(knots[i + 1])
        b.roll = 0
        if prev:
            b.parent = prev
            b.use_connect = True
        prev = b
    bpy.ops.object.mode_set(mode="OBJECT")
    G = [tail.vertex_groups.new(name=f"tail_{i}") for i in range(NT)]
    for vi, p in enumerate(TV):
        f = (p @ dirv - s0) / ((s1 - s0) * 0.97) * NT - 0.5
        i0 = int(min(NT - 2, max(0, math.floor(f))))
        r = min(1.0, max(0.0, f - i0))
        if f < 0:
            G[0].add([vi], 1.0, "REPLACE")
            continue
        G[i0].add([vi], 1 - r, "REPLACE")
        G[i0 + 1].add([vi], r, "REPLACE")
    mod = tail.modifiers.new("arm", "ARMATURE")
    mod.object = arm
    tail.parent = arm

    os.makedirs(os.path.join(ROOT, "assets", "models"), exist_ok=True)
    out = {}
    out["dragon_hybrid_head"] = {"part": "head", "tris": export([head_piece], "dragon_hybrid_head")}
    out["dragon_hybrid_torso"] = {"part": "torso", "tris": export([torso_piece], "dragon_hybrid_torso")}
    out["dragon_hybrid_tail"] = {"part": "hips", "tris": export([tail], "dragon_hybrid_tail", [arm]),
                                 "bones": [f"tail_{i}" for i in range(NT)], "length_studs": TAIL_LEN}
    json.dump({"pieces": out, "note": "authored around each R15 part's centre; attach offset 0. Shares the dragon atlas.",
               "head_scale_from_dragon": head_s}, open(os.path.join(ROOT, "assets", "models", "dragon_hybrid.json"), "w"), indent=1)
    print("HYBRID", json.dumps(out))


if __name__ == "__main__":
    main()
