"""Thunder Serpent: Meshy GLB -> game-ready rigged model with an opening mouth.

    /tmp/bpyenv/bin/python scripts/rig_serpent.py [--length 18] [--tris 8000]

Steps
  1. import the raw Meshy model (assets/source_art/meshy/thunder_serpent.glb), turn it so the head points along
     glTF -Z (Roblox forward), scale to --length studs, decimate to ~--tris triangles (the 2048 texture keeps detail)
  2. mouth: the lower jaw (head region below the mouth line, forward of the hinge) is weighted to a `jaw` bone;
     a dark palate + mouth floor and 4 upper / 4 lower fangs are added inside the head (hidden when closed). Their
     UVs point at a dark-indigo and a white texel of the existing texture, so it stays ONE mesh with ONE texture
     (a Roblox MeshPart takes a single TextureID)
  3. armature: spine_00 (head) .. spine_13 (tail tip) as a chain + jaw (child of spine_00); smooth weights blended
     between the two nearest spine bones along the body
  4. export assets/models/thunder_serpent.glb (previewer) and assets/meshes/thunder_serpent.fbx (Roblox skinned
     MeshPart) + a JSON with rest bone data
"""
import argparse
import json
import math
import os
import sys

import bpy  # noqa: I001 (bpy must load before bmesh)
import bmesh
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SRC = os.path.join(ROOT, "assets", "source_art", "meshy", "thunder_serpent.glb")
NB = 14                     # spine bones
S_HEAD = 0.06               # spine_00 origin (fraction of length from the snout)
S_HINGE = 0.10              # jaw hinge
S_NECK = 0.125              # end of the rigid head
MOUTH_Z = -0.045 / 0.307    # mouth line as a fraction of body height (raw model: z -0.045 of 0.307)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--length", type=float, default=18.0)
    ap.add_argument("--tris", type=int, default=8000)
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=SRC)
    o = [x for x in bpy.context.scene.objects if x.type == "MESH"][0]
    for x in list(bpy.context.scene.objects):
        if x is not o:
            bpy.data.objects.remove(x, do_unlink=True)
    o.parent = None
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    # raw: head at Blender -Y. Turn 180 about Z -> head at +Y (= glTF -Z), scale to length, centre on the body
    me = o.data
    V = np.array([o.matrix_world @ v.co for v in me.vertices])
    L0 = V[:, 1].max() - V[:, 1].min()
    k = a.length / L0
    M = Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Scale(k, 4)
    me.transform(o.matrix_world)
    o.matrix_world = Matrix.Identity(4)
    me.transform(M)
    V = np.array([v.co[:] for v in me.vertices])
    me.transform(Matrix.Translation((-V[:, 0].mean(), -(V[:, 1].max() + V[:, 1].min()) / 2, -(V[:, 2].max() + V[:, 2].min()) / 2)))

    # decimate
    tris0 = sum(len(p.vertices) - 2 for p in me.polygons)
    dm = o.modifiers.new("dec", "DECIMATE")
    dm.ratio = min(1.0, a.tris / tris0)
    bpy.ops.object.modifier_apply(modifier=dm.name)
    me = o.data

    V = np.array([v.co[:] for v in me.vertices])
    ymax, ymin = V[:, 1].max(), V[:, 1].min()
    L = ymax - ymin
    H = V[:, 2].max() - V[:, 2].min()
    zmid = (V[:, 2].max() + V[:, 2].min()) / 2
    s_of = lambda y: (ymax - y) / L
    y_of = lambda s: ymax - s * L
    mouth_z = zmid + MOUTH_Z * H

    # texel picks for the interior: darkest blue-ish and brightest texel of the texture
    img = next(n.image for m in me.materials for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    lum = px[..., :3].mean(-1)
    blue = px[..., 2] - px[..., 0]
    alpha = px[..., 3] > 0.5
    indigo = np.array([0.165, 0.102, 0.604])                       # #2a1a9a (8-bit image pixels are sRGB values)
    dark_score = np.where(alpha, np.linalg.norm(px[..., :3] - indigo, axis=-1), 9)
    dy, dx = np.unravel_index(np.argmin(dark_score), dark_score.shape)
    wy, wx = np.unravel_index(np.argmax(np.where(alpha, lum, -1)), lum.shape)
    uv_dark = ((dx + 0.5) / w, (dy + 0.5) / h)
    uv_white = ((wx + 0.5) / w, (wy + 0.5) / h)
    print("mouth texel", [round(float(v), 3) for v in px[dy, dx, :3]], "fang texel", [round(float(v), 3) for v in px[wy, wx, :3]])

    # ---- cut the mouth: faces in the mouth region go to the jaw (below the line) or the head; the edges between
    # the two groups are split so the lips separate instead of stretching a skin curtain across the opening
    bm = bmesh.new()
    bm.from_mesh(me)
    jaw_faces = set()
    for f in bm.faces:
        c = f.calc_center_median()
        if s_of(c.y) < S_HINGE and c.z < mouth_z:
            jaw_faces.add(f)
    cut = [e for e in bm.edges if len(e.link_faces) == 2 and ((e.link_faces[0] in jaw_faces) != (e.link_faces[1] in jaw_faces))]
    bmesh.ops.split_edges(bm, edges=cut)
    bm.verts.index_update()
    jaw_main = {v.index for f in jaw_faces for v in f.verts}
    bm.to_mesh(me)
    bm.free()
    V = np.array([v.co[:] for v in me.vertices])

    # ---- mouth interior (bmesh, appended to the same mesh)
    bm = bmesh.new()
    bm.from_mesh(me)
    uvl = bm.loops.layers.uv.active
    jaw_verts, head_int = set(), set()

    def width_at(s):
        m = np.abs(s_of(V[:, 1]) - s) < 0.01
        return (V[m, 0].max() - V[m, 0].min()) if m.any() else 0.2

    def quad_strip(z, s0, s1, up, tag):
        n = 6
        for side in (0, 1):                                        # double-sided: each side has its own verts
            rows = []
            for i in range(n + 1):
                s = s0 + (s1 - s0) * i / n
                hw = width_at(s) * 0.44
                rows.append([bm.verts.new((-hw, y_of(s), z)), bm.verts.new((hw, y_of(s), z))])
            for i in range(n):
                a_, b_, c_, d_ = rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]
                face = bm.faces.new((a_, b_, c_, d_) if side == 0 else (d_, c_, b_, a_))
                for lp in face.loops:
                    lp[uvl].uv = uv_dark
            for r in rows:
                tag.update(r)

    def fang(x, s, z, length, down, tag):
        tip_z = z + (-length if down else length)
        for side in (0, 1):
            base = [bm.verts.new((x + dx_, y_of(s) + dy_, z)) for dx_, dy_ in ((-0.12, -0.12), (0.12, -0.12), (0.12, 0.12), (-0.12, 0.12))]
            tip = bm.verts.new((x, y_of(s), tip_z))
            for i in range(4):
                face = bm.faces.new((base[i], base[(i + 1) % 4], tip) if side == 0 else (tip, base[(i + 1) % 4], base[i]))
                for lp in face.loops:
                    lp[uvl].uv = uv_white
            tag.update(base + [tip])

    gap = H * 0.015
    quad_strip(mouth_z + gap, 0.015, S_HINGE, False, head_int)       # palate
    quad_strip(mouth_z - gap, 0.015, S_HINGE, True, jaw_verts)       # mouth floor
    for sx in (-1, 1):
        for s, ln in ((0.025, H * 0.16), (0.055, H * 0.12)):
            hw = width_at(s) * 0.3
            fang(sx * hw, s, mouth_z + gap, ln, True, head_int)       # upper fangs hang down
            fang(sx * hw * 0.9, s + 0.012, mouth_z - gap, ln * 0.8, False, jaw_verts)   # lower fangs point up
    bm.verts.index_update()
    jaw_verts_index = {v.index for v in jaw_verts}
    bm.to_mesh(me)
    n_main = len(V)
    bm.free()

    # ---- armature
    arm_data = bpy.data.armatures.new("SerpentRig")
    arm = bpy.data.objects.new("SerpentRig", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    s_b = [S_HEAD + (0.985 - S_HEAD) * i / (NB - 1) for i in range(NB)]
    zc = [float(np.median(V[np.abs(s_of(V[:, 1]) - s) < 0.02, 2])) if (np.abs(s_of(V[:, 1]) - s) < 0.02).any() else zmid for s in s_b]
    prev = None
    for i, s in enumerate(s_b):
        b = arm_data.edit_bones.new(f"spine_{i:02d}")
        b.head = (0, y_of(s), zc[i])
        nxt = s_b[i + 1] if i + 1 < NB else 1.0
        b.tail = (0, y_of(nxt), zc[min(i + 1, NB - 1)])
        b.roll = 0
        if prev:
            b.parent = prev
            b.use_connect = True
        prev = b
    j = arm_data.edit_bones.new("jaw")
    j.head = (0, y_of(S_HINGE), mouth_z)
    j.tail = (0, y_of(0.01), mouth_z)
    j.roll = 0
    j.parent = arm_data.edit_bones["spine_00"]
    bpy.ops.object.mode_set(mode="OBJECT")

    # ---- weights
    groups = {n: o.vertex_groups.new(name=n) for n in [f"spine_{i:02d}" for i in range(NB)] + ["jaw"]}
    co = np.array([v.co[:] for v in me.vertices])
    for vi, p in enumerate(co):
        s = s_of(p[1])
        if vi >= n_main:                                            # interior pieces: rigid
            groups["jaw" if vi in jaw_verts_index else "spine_00"].add([vi], 1.0, "REPLACE")
            continue
        if s < S_NECK:
            if vi in jaw_main:
                wj = min(1.0, max(0.0, (S_HINGE - s) / 0.012))       # only the hinge corners blend into the head
                if wj > 0:
                    groups["jaw"].add([vi], wj, "REPLACE")
                if wj < 1:
                    groups["spine_00"].add([vi], 1 - wj, "REPLACE")
            else:
                groups["spine_00"].add([vi], 1.0, "REPLACE")
            continue
        f = (s - S_HEAD) / (0.985 - S_HEAD) * (NB - 1)
        i0 = int(min(NB - 2, max(0, math.floor(f))))
        t = min(1.0, max(0.0, f - i0))
        groups[f"spine_{i0:02d}"].add([vi], 1 - t, "REPLACE")
        groups[f"spine_{i0 + 1:02d}"].add([vi], t, "REPLACE")
    mod = o.modifiers.new("arm", "ARMATURE")
    mod.object = arm
    o.parent = arm

    # ---- export
    os.makedirs(os.path.join(ROOT, "assets", "models"), exist_ok=True)
    glb = os.path.join(ROOT, "assets", "models", "thunder_serpent.glb")
    fbx = os.path.join(ROOT, "assets", "meshes", "thunder_serpent.fbx")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_skins=True, export_animations=False)
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, add_leaf_bones=False, bake_anim=False, path_mode="COPY", embed_textures=True,
                             axis_forward="-Z", axis_up="Y")
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    info = {"length_studs": a.length, "tris": tris, "bones": [f"spine_{i:02d}" for i in range(NB)] + ["jaw"],
            "spine_s": s_b, "hinge_s": S_HINGE, "uv_dark": uv_dark, "uv_white": uv_white}
    json.dump(info, open(os.path.join(ROOT, "assets", "models", "thunder_serpent.json"), "w"), indent=1)
    print(json.dumps(info))


if __name__ == "__main__":
    main()
