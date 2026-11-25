"""Dragon v5: join the Meshy long body and the separate full-res head into one mesh with one texture.

    /tmp/bpyenv/bin/python scripts/build_dragon.py [--head-scale 0.18] [--cut -0.66] [--leg-shift 0.10]

Inputs (Meshy multi-image-to-3D, Blender coords after glTF import: length along Y, head toward -Y, Z up)
  assets/source_art/meshy/dragon_v5_body.glb   long serpentine body from dragon_sheet_v5_long.png (its head is a
                                               placeholder and gets cut off)
  assets/source_art/meshy/dragon_v5_head.glb   head bust from dragon_head_sheet_v5.png (snout -Y, mane at +Y)
Steps
  0. slide the front legs back (they sat under the mane) to open a short neck
  1. delete the body's placeholder head (everything ahead of --cut on Y)
  2. scale the head so its core (no horns or whiskers) is ~2.2x the body thickness and seat it so the back of the
     mane swallows the neck stub (no visible seam)
  3. pack both textures into one 2048 atlas (body left half, head right half) and remap UVs: a Roblox MeshPart takes
     a single TextureID
Output: assets/source_art/meshy/dragon_v5_assembled.glb (unrigged, full res; rig_dragon.py decimates and rigs it)
"""
import argparse
import os
import sys

import bpy  # noqa: I001
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(HERE, "..", "assets", "source_art", "meshy")


def load(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    mesh = [o for o in new if o.type == "MESH"][0]
    for o in new:
        if o is not mesh:
            bpy.data.objects.remove(o, do_unlink=True)
    mesh.data.transform(mesh.matrix_world)
    mesh.parent = None
    mesh.matrix_world = Matrix.Identity(4)
    return mesh


def tex_of(o):
    return next(n.image for m in o.data.materials for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image)


def assemble(head_scale=0.18, cut=-0.66, overlap=0.07, leg_shift=0.10, head_hook=None, body_hook=None):
    """Build the joined mesh in the current (empty) scene. head_hook(head_obj) runs in the head's own coordinates
    before it is scaled and seated (rig_dragon.py uses it for the jaw, whiskers and vertex groups). Returns
    (object, info) where info["head_matrix"] maps head-space points into the joined mesh."""
    from types import SimpleNamespace
    a = SimpleNamespace(head_scale=head_scale, cut=cut, overlap=overlap, leg_shift=leg_shift)
    body = load(os.path.join(M, "dragon_v5_body.glb"))
    head = load(os.path.join(M, "dragon_v5_head.glb"))
    if head_hook:
        head_hook(head)

    # 0. the front legs sit right under the mane on the sheet: slide them back to open a short neck (falloff on |x| so
    # the shoulder blends into the body instead of tearing)
    me = body.data
    B = np.array([v.co[:] for v in me.vertices])
    ax = np.abs(B[:, 0])
    w = np.clip((ax - 0.05) / 0.025, 0, 1) * ((B[:, 1] > -0.72) & (B[:, 1] < -0.48) & (B[:, 2] < 0.0))
    B[:, 1] += a.leg_shift * w
    for i, v in enumerate(me.vertices):
        v.co = B[i]

    # 1. cut the placeholder head off the body
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(body.data)
    # cut, plus the placeholder's mane/horn remnants that stick up above the neck just behind the cut
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < a.cut or (v.co.y < a.cut + 0.14 and v.co.z > 0.07)], context="VERTS")
    # drop loose islands (horn tips, mane curls left floating by the cut). glTF import splits vertices on UV seams, so
    # islands are found on edges PLUS links between vertices at the same position
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    bm.verts.index_update()
    bm.verts.ensure_lookup_table()
    P = np.array([v.co[:] for v in bm.verts])
    E = [(e.verts[0].index, e.verts[1].index) for e in bm.edges]
    key = np.round(P / 1e-5).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.ravel()
    order = np.argsort(inv)
    same = [(order[i], order[i + 1]) for i in range(len(order) - 1) if inv[order[i]] == inv[order[i + 1]]]
    pairs = np.array(E + same) if (E or same) else np.zeros((0, 2), int)
    g = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(len(P), len(P)))
    nc, lab = connected_components(g, directed=False)
    sizes = np.bincount(lab)
    small = [bm.verts[i] for i in np.where(sizes[lab] < 400)[0]]
    bmesh.ops.delete(bm, geom=small, context="VERTS")
    bm.to_mesh(body.data)
    bm.free()
    if body_hook:
        body_hook(body)
    B = np.array([v.co[:] for v in body.data.vertices])
    trunk = (B[:, 1] > a.cut + 0.12) & (B[:, 1] < a.cut + 0.3)
    body_zc = float((B[trunk, 2].min() + B[trunk, 2].max()) / 2)

    # 2. scale + seat the head: its back (+Y) overlaps the neck stub, its neck centre lines up with the body centre
    H = np.array([v.co[:] for v in head.data.vertices])
    s = a.head_scale
    head_back = H[:, 1].max() * s
    neck_z = -0.15 * s                                  # neck centre in the head bust (behind the jaw, inside the mane)
    off = (0.0, a.cut + a.overlap * s / 0.25 - head_back, body_zc - neck_z)
    head_matrix = Matrix.Translation(off) @ Matrix.Scale(s, 4)
    head.data.transform(head_matrix)

    # 3. one atlas: body -> left half, head -> right half
    tb, th = tex_of(body), tex_of(head)
    W = 2048
    def px(img):
        w, h = img.size
        return np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    def half(p):                                        # squash to (W, W/2) columns by area-averaging pairs
        p = p[:, : (p.shape[1] // 2) * 2]
        return (p[:, 0::2] + p[:, 1::2]) / 2
    pb, ph = px(tb), px(th)
    if pb.shape[0] != W:
        raise SystemExit("expected 2048 textures")
    atlas = np.concatenate([half(pb), half(ph)], axis=1)
    img = bpy.data.images.new("dragon_v5_atlas", W, W, alpha=True)
    img.pixels = atlas.ravel()
    img.file_format = "PNG"
    for o, u0 in ((body, 0.0), (head, 0.5)):
        uv = o.data.uv_layers.active.data
        for lp in uv:
            lp.uv = (u0 + lp.uv[0] * 0.5, lp.uv[1])
    mat = body.data.materials[0]
    node = next(n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE")
    node.image = img
    head.data.materials.clear()
    head.data.materials.append(mat)

    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    head.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    body.name = body.data.name = "Dragon"
    img.pack()
    return body, {"head_matrix": head_matrix, "body_zc": body_zc, "atlas": img}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head-scale", type=float, default=0.18)
    ap.add_argument("--cut", type=float, default=-0.66)
    ap.add_argument("--overlap", type=float, default=0.07)
    ap.add_argument("--leg-shift", type=float, default=0.10)
    ap.add_argument("--out", default=os.path.join(M, "dragon_v5_assembled.glb"))
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    body, _ = assemble(a.head_scale, a.cut, a.overlap, a.leg_shift)
    out = a.out
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="AUTO")
    V = np.array([v.co[:] for v in body.data.vertices])
    print("assembled", out, "verts", len(V), "size", (V.max(0) - V.min(0)).round(3), "tris",
          sum(len(p.vertices) - 2 for p in body.data.polygons))


if __name__ == "__main__":
    main()
