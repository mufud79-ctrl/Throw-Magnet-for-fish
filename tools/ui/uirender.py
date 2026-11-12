"""bpy helpers shared by render_thumbs.py and render_icons.py.

Cheap Cycles CPU renders with a transparent film, three sun lights and an
orthographic camera that is fitted to the visible meshes.
"""
import math
import bpy
from mathutils import Vector


def scene_setup(size, samples=20, threads=3):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.render.threads_mode = "FIXED"
    sc.render.threads = threads
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("UIWorld")
    sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.62, 0.72, 0.86, 1)
    bg.inputs[1].default_value = 0.85
    return sc


def sun(name, to_light, strength, color=(1, 1, 1)):
    sc = bpy.context.scene
    ld = bpy.data.lights.new(name, "SUN")
    ld.energy = strength
    ld.color = color
    ld.angle = math.radians(8)
    ob = bpy.data.objects.new(name, ld)
    sc.collection.objects.link(ob)
    ob.rotation_euler = (-Vector(to_light).normalized()).to_track_quat("-Z", "Y").to_euler()
    return ob


def default_lights(cam_dir):
    """Key from above/camera side, cool fill, warm rim from behind."""
    cd = Vector(cam_dir).normalized()
    side = cd.cross(Vector((0, 0, 1))).normalized()
    sun("Key", cd * 0.7 + Vector((0, 0, 1.0)) - side * 0.35, 3.6)
    sun("Fill", cd + side * 0.9 - Vector((0, 0, 0.2)), 1.1, (0.85, 0.92, 1.0))
    sun("Rim", -cd + Vector((0, 0, 0.7)), 3.0, (1.0, 0.95, 0.85))


def visible_verts(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in objs:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ob.matrix_world
        pts.extend(mw @ v.co for v in me.vertices)
        ev.to_mesh_clear()
    return pts


def ortho_camera(objs, cam_dir, margin=1.14, up=Vector((0, 0, 1))):
    """Orthographic camera looking along -cam_dir, framed to fill the square render."""
    sc = bpy.context.scene
    d = Vector(cam_dir).normalized()
    right = (-d).cross(up).normalized()
    upv = right.cross(-d).normalized()
    pts = visible_verts(objs)
    xs = [p.dot(right) for p in pts]
    ys = [p.dot(upv) for p in pts]
    zs = [p.dot(d) for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    ext = max(max(xs) - min(xs), max(ys) - min(ys))
    cam_d = bpy.data.cameras.new("UICam")
    cam_d.type = "ORTHO"
    cam_d.ortho_scale = ext * margin
    cam_d.clip_start = 0.01
    cam_d.clip_end = (max(zs) - min(zs)) + 100
    cam = bpy.data.objects.new("UICam", cam_d)
    sc.collection.objects.link(cam)
    cam.location = right * cx + upv * cy + d * (max(zs) + 50)
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    return cam


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
