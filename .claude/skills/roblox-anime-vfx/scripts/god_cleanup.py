"""Clean up the Meshy thunder god for Roblox: merge, split into Body / Cape / Mane, decimate each part.

    /tmp/bpyenv/bin/python god_cleanup.py [--src GLB] [--out DIR] [--body 18000 --cape 4000 --mane 6000]

The raw Meshy model (assets/source_art/meshy/thunder_god.glb) is one fused mesh: 1.36M tris, one 2048 texture,
cape and mane fused to the body, 1,916 "loose parts" that are only UV seams. Steps:
  1. merge by distance (1e-5): welds the seams, the mesh becomes one connected part; UVs are per-loop so they survive
  2. classify every face by its texture colour (sampled at the face's UV centroid) + position:
       cape = red, below the shoulder pads (z < 0.45), not the front of the sash
       mane = white, above the waist and behind the face (or the side locks / top fringe); excludes the chest
              tattoos, the sash and the eyes
     then smooth the labels by vertex majority (4 passes) and keep the largest connected piece per class
  3. split into three meshes and decimate each (Collapse, X symmetry) to its triangle budget
Writes OUT/thunder_god_clean.blend and .glb (Blender Z-up, faces -Y, 1.9 units tall, centred at the origin).
The cape is cut where it tucks under the shoulder pads; god_rig.py pins its top row to UpperTorso so the seam
never opens.
"""
import os
import sys
import argparse
import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
import bpy
import bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
ROBLOX_TRI_CAP = 20000
PARTS = ["Body", "Cape", "Mane"]


def face_arrays(me):
    nf = len(me.polygons)
    cent = np.zeros(nf * 3)
    me.polygons.foreach_get("center", cent)
    tri = np.zeros(nf * 3, int)
    me.polygons.foreach_get("vertices", tri)
    uv = np.zeros(len(me.loops) * 2)
    me.uv_layers.active.data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    ls = np.zeros(nf, int)
    me.polygons.foreach_get("loop_start", ls)
    fuv = (uv[ls] + uv[ls + 1] + uv[ls + 2]) / 3
    img = [n for n in me.materials[0].node_tree.nodes if n.type == "TEX_IMAGE"][0].image
    W, H = img.size
    px = np.array(img.pixels[:], np.float32).reshape(H, W, 4)
    xi = np.clip((fuv[:, 0] % 1) * W, 0, W - 1).astype(int)
    yi = np.clip((fuv[:, 1] % 1) * H, 0, H - 1).astype(int)
    return cent.reshape(-1, 3), tri.reshape(-1, 3), px[yi, xi, :3]


def classify(cent, tri, col, nv):
    x, y, z = cent.T
    r, g, b = col.T
    mx, mn = col.max(1), col.min(1)
    sat = (mx - mn) / (mx + 1e-6)
    red = (r > g * 1.6) & (r > b * 1.3) & (sat > 0.35)
    white = (mn > 0.55) & (sat < 0.22)
    sash = (np.abs(x) < 0.25) & (z > -0.10) & (z < 0.17) & (y < 0.03)
    cape_top = (z >= 0.45) & (z < 0.60) & (y > 0.06) & (np.abs(x) < 0.30)
    cape = red & (((z < 0.45) & ~sash) | cape_top)
    mane = white & (z > 0.18) & ((y > -0.02) | (z > 0.82) | ((z > 0.60) & (np.abs(x) > 0.075)))
    nf = len(tri)
    lab = np.zeros(nf, int)
    lab[cape] = 1
    lab[mane] = 2
    A = sp.csr_matrix((np.ones(nf * 3), (np.repeat(np.arange(nf), 3), tri.ravel())), shape=(nf, nv))
    for _ in range(4):
        oh = np.zeros((nf, 3))
        oh[np.arange(nf), lab] = 1
        lab = (A @ (A.T @ oh)).argmax(1)
    for k in (1, 2):
        fk = np.where(lab == k)[0]
        t = tri[fk]
        rows = np.concatenate([t[:, 0], t[:, 1], t[:, 2]])
        cols = np.concatenate([t[:, 1], t[:, 2], t[:, 0]])
        G = sp.coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(nv, nv))
        _, cl = connected_components(G, directed=False)
        fc = cl[t[:, 0]]
        keep = fc == np.bincount(fc).argmax()
        lab[fk[~keep]] = 0
    return lab


HAND_CUT = 0.60       # |x| where the hands are cut off (inside the wrist cuffs)
HAND_OVERLAP = 0.012  # the hand piece starts this much before the cut, hidden in the cuff


def keep_faces(src, keep_fn, name):
    me = src.data.copy()
    me.name = name
    bm = bmesh.new()
    bm.from_mesh(me)
    mw = src.matrix_world
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not keep_fn(mw @ f.calc_center_median(), f.index)], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.matrix_world = src.matrix_world
    return ob


def decimate(ob, tris):
    mod = ob.modifiers.new("Dec", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = min(1.0, tris / max(len(ob.data.polygons), 1))
    mod.use_symmetry = True
    mod.symmetry_axis = "X"
    with bpy.context.temp_override(object=ob, active_object=ob):
        bpy.ops.object.modifier_apply(modifier="Dec")


def replace_hands(src, lab, body, hand_tris):
    """Rebuild the body as (body minus hands, decimated to budget - hand_tris) + (hands from the full-detail
    source, decimated to hand_tris), so the fingers keep enough geometry to bend."""
    total = len(body.data.polygons)
    bpy.data.objects.remove(body)
    rest = keep_faces(src, lambda c, i: lab[i] == 0 and abs(c.x) < HAND_CUT, "Body")
    hands = keep_faces(src, lambda c, i: lab[i] == 0 and abs(c.x) > HAND_CUT - HAND_OVERLAP, "Hands")
    decimate(rest, total - hand_tris)
    decimate(hands, hand_tris)
    with bpy.context.temp_override(active_object=rest, selected_editable_objects=[rest, hands]):
        bpy.ops.object.join()
    for p in rest.data.polygons:
        p.use_smooth = True
    hand = sum(1 for p in rest.data.polygons if abs((rest.matrix_world @ p.center).x) > HAND_CUT)
    print("Body (hands rebuilt) tris", len(rest.data.polygons), "hand tris (both)", hand)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(ROOT, "assets", "source_art", "meshy", "thunder_god.glb"))
    ap.add_argument("--out", default=os.path.join(ROOT, "assets", "meshes", "thunder_god"))
    ap.add_argument("--body", type=int, default=18000)
    ap.add_argument("--cape", type=int, default=4000)
    ap.add_argument("--mane", type=int, default=6000)
    ap.add_argument("--hands", type=int, default=2000, help="tris for both hands, decimated separately (0 = off)")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    target = {"Body": a.body, "Cape": a.cape, "Mane": a.mane}
    assert all(v <= ROBLOX_TRI_CAP for v in target.values())
    os.makedirs(a.out, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=a.src)
    src = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    bm = bmesh.new()
    bm.from_mesh(src.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bm.to_mesh(src.data)
    bm.free()
    cent, tri, col = face_arrays(src.data)
    lab = classify(cent, tri, col, len(src.data.vertices))
    print("faces per part", dict(zip(PARTS, np.bincount(lab, minlength=3).tolist())))

    for k, name in enumerate(PARTS):
        me = src.data.copy()
        me.name = name
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if lab[f.index] != k], context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(ob)
        ob.matrix_world = src.matrix_world
        mod = ob.modifiers.new("Dec", "DECIMATE")
        mod.decimate_type = "COLLAPSE"
        mod.ratio = target[name] / len(me.polygons)
        mod.use_symmetry = True
        mod.symmetry_axis = "X"
        with bpy.context.temp_override(object=ob, active_object=ob):
            bpy.ops.object.modifier_apply(modifier="Dec")
        for p in ob.data.polygons:
            p.use_smooth = True
        hand = sum(1 for p in ob.data.polygons if abs((ob.matrix_world @ p.center).x) > 0.585)
        print(name, "tris", len(ob.data.polygons), "hand tris (both)", hand)
    if a.hands:
        replace_hands(src, lab, bpy.data.objects["Body"], a.hands)
    bpy.data.objects.remove(src)
    for o in bpy.context.scene.objects:          # bake the import transform so the parts sit in clean space
        o.select_set(True)
    with bpy.context.temp_override(selected_editable_objects=list(bpy.context.scene.objects)):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(a.out, "thunder_god_clean.blend"))
    bpy.ops.export_scene.gltf(filepath=os.path.join(a.out, "thunder_god_clean.glb"), export_format="GLB")


if __name__ == "__main__":
    main()
