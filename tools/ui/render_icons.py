"""Render raw 512x512 HUD icons (step 1 of 2; postprocess.py icons adds outlines).

    /tmp/claude-0/bpyenv/bin/python tools/ui/render_icons.py RAW_DIR

icon_fish.png  : the Goldfish model, hero 3/4 angle
icon_shop.png  : stylised coin sack with "$" and coin stacks (bpy primitives)
icon_index.png : chunky book with a gold fish emblem (bpy primitives)
"""
import math
import os
import sys
import bpy
from mathutils import Euler, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import uirender  # noqa: E402
from render_thumbs import render_fish  # noqa: E402

SIZE = 512


def mat(name, hexcol, rough=0.45, metal=0.0):
    m = bpy.data.materials.new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    h = hexcol.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    b.inputs["Base Color"].default_value = (*[x ** 2.2 for x in srgb], 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def finish_obj(ob, m, bevel=0.0, smooth=True):
    ob.data.materials.append(m)
    if bevel:
        bm = ob.modifiers.new("Bevel", "BEVEL")
        bm.width = bevel
        bm.segments = 3
    if smooth and ob.type == "MESH":
        for p in ob.data.polygons:
            p.use_smooth = True
    return ob


def cube(loc, size, m, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.active_object
    ob.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return finish_obj(ob, m, bevel, smooth=False)


def cyl(loc, r, depth, m, rot=(0, 0, 0), verts=48, bevel=0.0, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=depth, location=loc, rotation=rot)
    return finish_obj(bpy.context.active_object, m, bevel, smooth=False)


def sphere(loc, scale, m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1, location=loc)
    ob = bpy.context.active_object
    ob.scale = scale
    return finish_obj(ob, m)


def torus(loc, R, r, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=48, minor_segments=16,
                                     location=loc, rotation=rot)
    return finish_obj(bpy.context.active_object, m)


def text(body, loc, size, m, rot=(math.radians(90), 0, 0), extrude=0.05):
    cu = bpy.data.curves.new("Txt", "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = 0.015
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new("Txt", cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    cu.materials.append(m)
    return ob


def empty_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def coin_stack(x, y, n, gold, z0, r=0.34, h=0.115, jitter=0.03):
    obs = []
    for i in range(n):
        dx = jitter * math.sin(i * 2.1)
        dy = jitter * math.cos(i * 1.7)
        obs.append(cyl((x + dx, y + dy, z0 + h / 2 + i * h), r, h * 0.92, gold, bevel=0.025))
    return obs


def shop_icon(out):
    empty_scene()
    sack = mat("Sack", "#E0A75E", 0.7)
    rope = mat("Rope", "#B5452E", 0.6)
    gold = mat("Gold", "#FFC531", 0.3, 0.35)
    gold2 = mat("Gold2", "#FFB000", 0.3, 0.35)
    obs = []
    bag = sphere((0, 0, 0), (0.95, 0.85, 0.9), sack)
    for v in bag.data.vertices:          # pinch the top into a neck, flatten the base
        z = v.co.z
        f = 1 - 0.62 * max(z, 0) ** 1.6
        v.co.x *= f
        v.co.y *= f
        if z < -0.78:
            v.co.z = -0.78 - (z + 0.78) * 0.15
    obs.append(bag)
    obs.append(cyl((0, 0, 0.86), 0.33, 0.22, sack))
    obs.append(torus((0, 0, 0.84), 0.36, 0.085, rope))
    obs.append(cyl((0, 0, 1.08), 0.26, 0.32, sack, r2=0.55))
    obs.append(sphere((0, 0, 1.24), (0.5, 0.5, 0.08), sack))
    obs.append(text("$", (0, -0.84, -0.06), 1.0, gold, extrude=0.07))
    base = -0.73
    obs += coin_stack(1.05, -0.25, 5, gold, base)
    obs += coin_stack(-1.0, -0.35, 3, gold, base)
    rot = (math.radians(72), 0, math.radians(-15))
    c = Vector((-0.45, -1.0, base + 0.33))
    n = Euler(rot).to_matrix() @ Vector((0, 0, 1))
    obs.append(cyl(c, 0.34, 0.11, gold2, rot=rot, bevel=0.025))
    obs.append(text("$", c + n * 0.06, 0.42, gold, rot=rot, extrude=0.02))
    cam = (0.35, -1.0, 0.42)
    uirender.scene_setup(SIZE, samples=24)
    uirender.default_lights(cam)
    uirender.ortho_camera(obs, cam, margin=1.12)
    uirender.render(out)


def index_icon(out):
    empty_scene()
    cover = mat("Cover", "#2F7BEA", 0.5)
    pages = mat("Pages", "#FFF2D2", 0.8)
    gold = mat("Gold", "#FFC531", 0.3, 0.35)
    ribbon = mat("Ribbon", "#E2304A", 0.6)
    dark = mat("Dark", "#1B1530", 0.4)
    obs = [
        cube((0, 0.21, 0), (1.06, 0.1, 1.38), cover, 0.045),
        cube((0, -0.21, 0), (1.06, 0.1, 1.38), cover, 0.045),
        cube((-0.5, 0, 0), (0.16, 0.52, 1.38), cover, 0.07),
        cube((0.02, 0, 0), (0.96, 0.34, 1.28), pages, 0.02),
        cube((0.3, 0.0, -0.78), (0.1, 0.03, 0.4), ribbon, 0.01),
    ]
    for i in range(4):   # page lines on the fore-edge
        obs.append(cube((0.505, 0, -0.45 + i * 0.3), (0.01, 0.3, 0.02), mat(f"Line{i}", "#E6D2A8", 0.8), 0))
    # gold corner caps on the front cover
    for sx in (1, -1):
        for sz in (1, -1):
            if sx < 0:
                continue
            obs.append(cube((0.47 * sx, -0.27, 0.63 * sz), (0.16, 0.04, 0.16), gold, 0.03))
    yf = -0.28
    obs.append(cube((0.03, yf, 0.5), (0.6, 0.04, 0.13), gold, 0.03))      # title plate
    ex, ez = 0.03, -0.08   # fish emblem in a gold ring
    obs.append(torus((ex, yf, ez), 0.4, 0.045, gold, rot=(math.radians(90), 0, 0)))
    obs.append(sphere((ex + 0.06, yf - 0.01, ez), (0.2, 0.05, 0.135), gold))
    obs.append(cyl((ex - 0.2, yf - 0.01, ez), 0.14, 0.05, gold, rot=(math.radians(90), 0, 0), verts=3))
    obs.append(cyl((ex + 0.02, yf - 0.01, ez + 0.14), 0.07, 0.04, gold, rot=(math.radians(90), 0, math.radians(0)), verts=3))
    obs.append(sphere((ex + 0.16, yf - 0.06, ez + 0.03), (0.032, 0.02, 0.032), dark))
    cam = (0.55, -1.0, 0.38)
    uirender.scene_setup(SIZE, samples=24)
    uirender.default_lights(cam)
    root = bpy.data.objects.new("Root", None)
    bpy.context.scene.collection.objects.link(root)
    for o in obs:
        o.parent = root
    root.rotation_euler = (0, math.radians(-5), math.radians(-12))
    bpy.context.view_layer.update()
    uirender.ortho_camera(obs, cam, margin=1.12)
    uirender.render(out)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    raw = argv[0]
    os.makedirs(raw, exist_ok=True)
    render_fish("Goldfish", "Common", os.path.join(raw, "icon_fish.png"), size=SIZE, cam_dir=(6.0, 5.2, 2.8),
                samples=24, margin=1.1)
    shop_icon(os.path.join(raw, "icon_shop.png"))
    index_icon(os.path.join(raw, "icon_index.png"))
    print("ICONS DONE")


if __name__ == "__main__":
    main()
