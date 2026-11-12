"""Render a few frames of a clip on a fish into a strip (for checking).
python anim_preview.py <Rarity/Name> <Clip> <out.png> [frames]"""
import bpy, sys, os, math
import numpy as np
from mathutils import Vector
path, clip, out = sys.argv[1:4]; n = int(sys.argv[4]) if len(sys.argv) > 4 else 6
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
name = path.split("/")[-1]
bpy.ops.wm.open_mainfile(filepath=os.path.join(root, "models", path, name + ".blend"))
sc = bpy.context.scene; arm = bpy.data.objects[f"{name}_Rig"]; act = bpy.data.actions[clip]
arm.animation_data.action = act
if hasattr(arm.animation_data, "action_slot") and act.slots: arm.animation_data.action_slot = act.slots[0]
fish = bpy.data.objects[name]; d = max(fish.dimensions)
for o in list(sc.objects):
    if o.type in ("CAMERA", "LIGHT"): bpy.data.objects.remove(o)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
VIEW = os.environ.get("VIEW", "hero")
cam.location = (Vector((0.001, 0, 1)) if VIEW == "top" else Vector((1, 0.001, 0.05)) if VIEW == "side" else Vector((0.9, 0.7, 1.1))).normalized() * d * 1.9
cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
sun = bpy.data.objects.new("S", bpy.data.lights.new("S", "SUN")); sun.data.energy = 4; sun.rotation_euler = (0.6, 0.2, 0.8); sc.collection.objects.link(sun)
sc.render.engine = "CYCLES"; sc.cycles.samples = 6; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 420, 300
T = act["frames"]; tiles = []
for i in range(n):
    sc.frame_set(int(i * T / n)); sc.render.filepath = f"/tmp/claude-0/af_{i}.png"; bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(sc.render.filepath); tiles.append(np.array(im.pixels[:], np.float32).reshape(300, 420, 4))
strip = np.concatenate(tiles, axis=1); img = bpy.data.images.new("strip", 420 * n, 300)
img.pixels.foreach_set(strip.ravel()); img.filepath_raw = out; img.file_format = "PNG"; img.save()
