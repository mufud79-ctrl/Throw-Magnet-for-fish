"""Render a bench with a blocky R15-size stand-in (about 5.2 studs tall) in a seated preacher-curl pose.
python fit_check.py <bench .blend> <out.png>"""
import bpy, sys, math
from mathutils import Vector, Matrix
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
sc = bpy.context.scene
bench = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("_Glow")][0]
co = [bench.matrix_world @ v.co for v in bench.data.vertices]
# bench faces +Y after export rotation: seat at the -Y end, arm pad toward +Y
import numpy as np
P = np.array([v[:] for v in co]); zmin = P[:, 2].min(); ymin, ymax = P[:, 1].min(), P[:, 1].max()
back = P[(P[:, 1] < ymin + 0.4 * (ymax - ymin)) & (np.abs(P[:, 0]) < 1.0)]
seat_top = back[:, 2].max(); y_seat = back[back[:, 2] > seat_top - 0.08][:, 1].mean()
front = P[(P[:, 1] > y_seat + 0.6) & (np.abs(P[:, 0]) < 1.1) & (P[:, 2] > seat_top + 0.3)]
pad_top = front[:, 2].max(); y_pad = front[front[:, 2] > pad_top - 0.15][:, 1].mean()
mat = bpy.data.materials.new("Dummy")
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.6, 0.2, 1)
import bmesh
def seg(name, a, b, w, d=None):
    a, b = Vector(a), Vector(b); me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(mat)
    o.location = (a + b) / 2; o.rotation_mode = "QUATERNION"; o.rotation_quaternion = (b - a).to_track_quat("Z", "Y")
    o.scale = (w, d or w, (b - a).length)
hip = Vector((0, y_seat - 0.15, seat_top + 0.05))
seg("Torso", hip, hip + Vector((0, 0.25, 2.1)), 2.0, 1.0)
seg("Head", hip + Vector((0, 0.3, 2.2)), hip + Vector((0, 0.35, 3.4)), 1.2)
for sx in (-0.5, 0.5):
    knee = Vector((sx, hip.y + 1.6, seat_top + 0.35))
    seg(f"Thigh{sx}", Vector((sx, hip.y, seat_top + 0.45)), knee, 0.9)
    seg(f"Shin{sx}", knee, Vector((sx, knee.y + 0.1, zmin)), 0.85)
for sx in (-1.5, 1.5):
    sh = hip + Vector((sx, 0.25, 1.85)); elbow = Vector((sx * 0.8, y_pad + 0.15, pad_top + 0.25))
    seg(f"UpperArm{sx}", sh, elbow, 0.85); seg(f"Forearm{sx}", elbow, elbow + Vector((0, 0.55, 1.1)), 0.8)
print("seat_top", round(seat_top - zmin, 2), "pad_top", round(pad_top - zmin, 2), "seat_y", round(y_seat, 2), "pad_y", round(y_pad, 2))
for o in [o for o in sc.objects if o.type in ("CAMERA",)]: bpy.data.objects.remove(o)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.location = Vector((16, -0.3, 1.6)); tgt = Vector((0, -0.3, 1.6)); cam.data.lens = 50
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.use_denoising = True
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sun.data.energy = 4; sun.rotation_euler = (0.7, 0.2, 0.9); sc.collection.objects.link(sun)
if sc.world is None: sc.world = bpy.data.worlds.new("W")
sc.world.color = (0.45, 0.55, 0.68)
sc.render.resolution_x, sc.render.resolution_y = 700, 600; sc.cycles.samples = 12
sc.render.filepath = sys.argv[2]; bpy.ops.render.render(write_still=True)
print("seat_top", round(seat_top, 2), "dims", [round(x, 2) for x in bench.dimensions])
