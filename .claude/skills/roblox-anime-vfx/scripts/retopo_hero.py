"""Retopologise AI-generated hero meshes (Meshy GLBs) into clean, Roblox-ready quad meshes.

    /tmp/bpyenv/bin/python retopo_hero.py [name ...] [--polys 3500]

Reads assets/source_art/meshy/<name>.glb, then: join parts -> voxel remesh solved to land on a target
POLY count (watertight, all quads) -> centre on the pivot and fit a 2-stud box -> smart UV unwrap (so
energy_strip / edge_strip textures wrap it) -> export assets/meshes/<name>.fbx/.obj/.json like the kit.
Budgets are polygons (quads). Hero meshes stay <= 4,000 polys (8,000 triangles, well under Roblox's
20,000-triangle cap). ROTATE fixes each model's facing so it looks down -Z (Roblox forward) like the caster.
"""
import os
import sys
import math
import argparse
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vfx_meshes import export, OUT  # noqa: E402

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "source_art", "meshy")
MAX_POLYS = 4000
# extra rotation (degrees, Blender XYZ) after import so the model faces Roblox -Z (Blender +Y after export axes)
ROTATE = {"dragon_head": (0, 0, 0), "giant_fist": (0, 0, 0), "phoenix_bird": (0, 0, 0)}


def retopo(name, polys):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(SRC, name + ".glb"))
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    src_polys = len(ob.data.polygons)
    # watertight all-quad shell at the target POLY count: voxel remesh emits quads, and its face count scales
    # with area / voxel_size^2, so solve for the voxel size (QuadriFlow is an async job and never finishes
    # in headless bpy).
    src = ob.data.copy()
    area = sum(p.area for p in src.polygons)
    size = math.sqrt(area / polys)
    for _ in range(6):
        ob.data = src.copy()
        ob.data.remesh_voxel_size = size
        bpy.ops.object.voxel_remesh()
        n = len(ob.data.polygons)
        if 0.82 * polys <= n <= polys:
            break
        size *= math.sqrt(n / (polys * 0.92))
    # orient, centre, fit a 2-stud box
    r = ROTATE.get(name, (0, 0, 0))
    ob.rotation_euler = tuple(math.radians(a) for a in r)
    bpy.ops.object.transform_apply(rotation=True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    ob.location = (0, 0, 0)
    s = 2.0 / max(ob.dimensions)
    ob.scale = (s, s, s)
    bpy.ops.object.transform_apply(location=True, scale=True)
    # UVs for strip textures
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    for p in ob.data.polygons:
        p.use_smooth = True
    ob.name = name
    out_polys = len(ob.data.polygons)
    assert out_polys <= MAX_POLYS, f"{name}: {out_polys} polys over the {MAX_POLYS} hero budget"
    export(ob, name, OUT)
    quads = sum(1 for p in ob.data.polygons if len(p.vertices) == 4)
    print(f"{name}: {src_polys} source polys -> {out_polys} polys ({quads} quads)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--polys", type=int, default=3500)
    a = ap.parse_args(sys.argv[1:])
    for nm in a.names or sorted(ROTATE):
        retopo(nm, a.polys)


if __name__ == "__main__":
    main()
