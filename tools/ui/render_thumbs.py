"""Render raw transparent fish thumbnails (step 1 of 2; postprocess.py adds outlines).

    /tmp/claude-0/bpyenv/bin/python tools/ui/render_thumbs.py RAW_DIR [Name ...]

Writes RAW_DIR/<Name>.png (256x256 RGBA). Same 3/4 side angle for every fish,
orthographic camera fitted so the fish fills the frame.
"""
import os
import sys
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import fishdata  # noqa: E402
import uirender  # noqa: E402

CAM_DIR = (8.0, 4.2, 3.2)   # fish heads point +Y, so this is a 3/4 side view facing right
# flat fish read better from above; Angelfish is a tall disc that needs a squarer side view
CAM_OVERRIDE = {"MantaRay": (3.0, 2.0, 8.0), "AuroraRay": (3.0, 2.0, 8.0), "Flounder": (3.0, 2.5, 8.0),
                "Angelfish": (8.0, 1.2, 1.4)}


def render_fish(name, rarity, out, size=256, cam_dir=CAM_DIR, samples=20, margin=1.14):
    blend = os.path.join(ROOT, "models", rarity, name, f"{name}.blend")
    bpy.ops.wm.open_mainfile(filepath=blend)
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    for o in bpy.data.objects:
        if o.type not in {"MESH", "ARMATURE"}:
            o.hide_render = True
    uirender.scene_setup(size, samples=samples)
    uirender.default_lights(cam_dir)
    uirender.ortho_camera(meshes, cam_dir, margin=margin)
    uirender.render(out)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    raw = argv[0]
    names = set(argv[1:])
    os.makedirs(raw, exist_ok=True)
    for name, rarity in fishdata.all_fish():
        if names and name not in names:
            continue
        render_fish(name, rarity, os.path.join(raw, f"{name}.png"), cam_dir=CAM_OVERRIDE.get(name, CAM_DIR))
        print("THUMB", name)


if __name__ == "__main__":
    main()
