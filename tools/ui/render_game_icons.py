"""Render the raw game icons and shop art (step 1 of 2; postprocess.py gameicons adds outlines).

    $PY tools/ui/render_game_icons.py RAW_DIR [name ...]

Small icons render at 512x512, shop art at 1024x1024, all on a transparent background, in the same
Cycles look as render_icons.py. Every icon is built from bpy primitives, curves and metaballs.
Names are listed in ICONS at the bottom.
"""
import math
import os
import sys
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import uirender  # noqa: E402
from render_icons import mat, finish_obj, cube, cyl, sphere, torus, empty_scene  # noqa: E402
from render_thumbs import render_fish  # noqa: E402

FONT = os.path.join(HERE, "fonts", "LuckiestGuy.ttf")
FRONT = (0.18, -1.0, 0.16)          # near-front view for flat glyphs
PI = math.pi
RAINBOW = ["#FF3B3B", "#FF9A1A", "#FFE23F", "#4CE24C", "#2EA8FF", "#8A4DFF", "#FF4FD8"]


# ------------------------------------------------------------------ helpers
def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def glow_mat(name, hexcol, strength=1.5, rough=0.3):
    m = mat(name, hexcol, rough)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Emission Color"].default_value = b.inputs["Base Color"].default_value
    b.inputs["Emission Strength"].default_value = strength
    return m


def attr_mat(name, rough=0.4, metal=0.0):
    """Material whose base colour comes from the 'Col' colour attribute."""
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    a = nt.nodes.new("ShaderNodeAttribute")
    a.attribute_name = "Col"
    nt.links.new(a.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def lin(hexcol):
    h = hexcol.lstrip("#")
    return [(int(h[i:i + 2], 16) / 255) ** 2.2 for i in (0, 2, 4)]


def chaikin(pts, it=2):
    for _ in range(it):
        out = []
        for i, p in enumerate(pts):
            q = pts[(i + 1) % len(pts)]
            out += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]), (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
        pts = out
    return pts


def ngon(n, r, start=PI / 2, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(start + 2 * PI * k / n), cy + r * math.sin(start + 2 * PI * k / n)) for k in range(n)]


def face_rot(cam):
    """Euler that turns a curve's local +Z toward the camera (local +Y stays roughly up)."""
    return Vector(cam).normalized().to_track_quat("Z", "Y").to_euler()


def curve2d(outlines, m, extrude=0.08, bevel=0.05, loc=(0, 0, 0), rot=(PI / 2, 0, 0), res=4, offset=None, scale=1.0):
    """Puffy extruded 2D shape. Nested outlines become holes. Local XY is the drawing plane."""
    cu = bpy.data.curves.new("Shape", "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.extrude = extrude
    cu.bevel_depth = bevel
    cu.bevel_resolution = res
    cu.offset = -bevel * 0.7 if offset is None else offset
    for pts in outlines:
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for p, (x, y) in zip(sp.points, pts):
            p.co = (x * scale, y * scale, 0, 1)
        sp.use_cyclic_u = True
        sp.use_smooth = True
    cu.materials.append(m)
    ob = link(bpy.data.objects.new("Shape", cu))
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def tube(pts, r, m, closed=False):
    cu = bpy.data.curves.new("Tube", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, v in zip(sp.points, pts):
        p.co = (*v, 1)
    sp.use_cyclic_u = closed
    sp.use_smooth = True
    cu.materials.append(m)
    return link(bpy.data.objects.new("Tube", cu))


def text3d(body, m, size=1.0, loc=(0, 0, 0), rot=(PI / 2, 0, 0), extrude=0.08, back=None, back_off=0.06):
    """Luckiest Guy text, optionally with a fattened dark copy behind it (cartoon outline)."""
    font = bpy.data.fonts.load(FONT, check_existing=True)
    obs = []
    for layer, (mm, off, dz) in enumerate([(m, 0.0, 0.0)] + ([(back, back_off, -0.05)] if back else [])):
        cu = bpy.data.curves.new("Txt", "FONT")
        cu.body, cu.font, cu.size = body, font, size
        cu.extrude, cu.bevel_depth, cu.offset = extrude, 0.015, off
        cu.align_x, cu.align_y = "CENTER", "CENTER"
        cu.materials.append(mm)
        ob = link(bpy.data.objects.new("Txt", cu))
        ob.rotation_euler = rot
        n = ob.rotation_euler.to_matrix() @ Vector((0, 0, 1))
        ob.location = Vector(loc) + n * dz
        obs.append(ob)
    return obs


def parent_all(obs, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
    root = link(bpy.data.objects.new("Root", None))
    for o in obs:
        if o.parent is None:
            o.parent = root
    root.location, root.rotation_euler, root.scale = loc, rot, (scale,) * 3
    bpy.context.view_layer.update()
    return root


def half_torus(R, r, m, keep="top"):
    """Torus in the XZ plane, cut in half (keep the top or bottom arc)."""
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=48, minor_segments=16, rotation=(PI / 2, 0, 0))
    ob = bpy.context.active_object
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    kill = [v for v in bm.verts if (v.co.y < -1e-4 if keep == "top" else v.co.y > 1e-4)]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    bm.to_mesh(ob.data)
    bm.free()
    bpy.ops.object.transform_apply(rotation=True)
    return finish_obj(ob, m)


def mound(n, spread, height, seed):
    """Positions for a heap: wide at the bottom, peaked in the middle."""
    rng = np.random.default_rng(seed)
    pts = []
    for i in range(n):
        f = math.sqrt((i + 0.5) / n)
        a = i * 2.39996 + rng.uniform(-0.3, 0.3)
        r = spread * f
        pts.append((r * math.cos(a) * 1.25, r * math.sin(a) * 0.8, height * (1 - f ** 1.6) + rng.uniform(0, 0.05)))
    return sorted(pts, key=lambda p: p[2]), rng


# ------------------------------------------------------------------ reusable models
def cash_stack(loc=(0, 0, 0), rot=(0, 0, 0), s=1.0, bills=4):
    g1, g2 = mat("BillA", "#3CCB52", 0.55), mat("BillB", "#2AA442", 0.55)
    dk, lt = mat("BillInk", "#1F8A37", 0.6), mat("BillSeal", "#7DF08C", 0.5)
    band = mat("Band", "#FFB21A", 0.45)
    h, obs = 0.13, []
    for i in range(bills):
        obs.append(cube((0.015 * math.sin(i * 2.3), 0.012 * math.cos(i * 1.9), h / 2 + i * h), (1.5, 0.74, h * 0.86), g1 if i % 2 else g2, 0.03))
    top = bills * h
    obs.append(cube((0, 0, top + 0.002), (1.22, 0.52, 0.02), dk, 0.006))
    obs.append(cube((0, 0, top + 0.012), (1.12, 0.44, 0.02), g1, 0.006))
    obs.append(cyl((0, 0, top + 0.03), 0.16, 0.03, lt, verts=32))
    obs.append(cube((0, 0, top / 2 + 0.01), (0.34, 0.79, top + 0.06), band, 0.025))
    parent_all(obs, loc, rot, s)
    return obs


def coin(loc, rot=(0, 0, 0), s=1.0):
    gold, gold2 = mat("Coin", "#FFC531", 0.3, 0.4), mat("CoinIn", "#F0A800", 0.35, 0.4)
    obs = [cyl((0, 0, 0), 0.26, 0.075, gold, verts=40, bevel=0.015), cyl((0, 0, 0.03), 0.19, 0.03, gold2, verts=40)]
    parent_all(obs, loc, rot, s)
    return obs


_ARM = {}


def arm_mesh(m):
    """Flexed arm as one blended metaball, converted to a mesh (cached so piles can share the data)."""
    if "data" in _ARM and _ARM["data"].name in bpy.data.meshes:
        ob = link(bpy.data.objects.new("Arm", _ARM["data"]))
        return ob
    mb = bpy.data.metaballs.new("ArmBall")
    mb.resolution = mb.render_resolution = 0.035
    mb.threshold = 0.6

    def capsule(a, b, r):
        a, b = Vector(a), Vector(b)
        e = mb.elements.new(type="CAPSULE")
        e.co, e.radius = (a + b) / 2, r
        e.size_x = (b - a).length / 2
        e.rotation = Vector((1, 0, 0)).rotation_difference((b - a).normalized())

    def ell(c, r, sx, sy, sz):
        e = mb.elements.new(type="ELLIPSOID")
        e.co, e.radius = c, r
        e.size_x, e.size_y, e.size_z = sx, sy, sz

    capsule((-1.15, 0, -0.78), (0.5, 0, -0.7), 0.52)        # upper arm
    ell((-0.25, 0, -0.38), 0.62, 0.95, 0.62, 0.62)          # bicep bulge
    ell((0.62, 0, -0.62), 0.5, 0.9, 0.8, 0.85)              # elbow
    capsule((0.62, 0, -0.45), (0.45, 0, 0.42), 0.46)         # forearm
    ell((0.28, 0, 0.72), 0.55, 1.0, 0.8, 0.82)               # fist
    capsule((0.0, -0.12, 0.62), (-0.05, -0.12, 0.92), 0.2)   # thumb knuckle
    ob = link(bpy.data.objects.new("ArmBall", mb))
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.convert(target="MESH")
    ob = bpy.context.active_object
    for p in ob.data.polygons:
        p.use_smooth = True
    ob.data.materials.append(m)
    _ARM["data"] = ob.data
    return ob


def arm(loc=(0, 0, 0), rot=(0, 0, 0), s=1.0):
    ob = arm_mesh(mat("ArmGold", "#FFC531", 0.35, 0.25))
    ob.location, ob.rotation_euler, ob.scale = loc, rot, (s,) * 3
    return [ob]


def worm(loc=(0, 0, 0), rot=(0, 0, 0), s=1.0, n=13, phase=0.0, eyes=True):
    """Gummy rainbow worm: a chain of beads along a wiggle, each bead a rainbow colour."""
    mats = [mat(f"Rb{i}", c, 0.25) for i, c in enumerate(RAINBOW)]
    obs = []
    for i in range(n):
        t = i / (n - 1)
        x = -1.1 + 2.2 * t
        z = 0.32 * math.sin(2.6 * PI * t + phase)
        y = 0.12 * math.cos(2.0 * PI * t + phase)
        r = 0.2 + 0.08 * math.sin(PI * min(1, t * 1.15))
        obs.append(sphere((x, y, z), (r, r, r), mats[i % len(mats)]))
    if eyes:
        hx = 1.1
        hz = 0.32 * math.sin(2.6 * PI + phase)
        hy = 0.12 * math.cos(2.0 * PI + phase)
        white, black = mat("EyeW", "#FFFFFF", 0.3), mat("EyeB", "#14121C", 0.2)
        for dy in (-0.09, 0.09):
            obs.append(sphere((hx + 0.05, hy + dy - 0.06, hz + 0.1), (0.08, 0.08, 0.08), white))
            obs.append(sphere((hx + 0.1, hy + dy - 0.12, hz + 0.11), (0.04, 0.04, 0.04), black))
    parent_all(obs, loc, rot, s)
    return obs


def heart(s=1.0, n=90):
    pts = []
    for k in range(n):
        t = 2 * PI * k / n
        x = 16 * math.sin(t) ** 3 / 17
        y = (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 17
        pts.append((x * s, (y + 1.0) * s))         # tip at the origin, lobes up
    return pts


def star4(r=1.0, inner=0.32, n=120, p=3.2):
    pts = []
    for k in range(n):
        t = 2 * PI * k / n
        c, s_ = math.cos(t), math.sin(t)
        x = math.copysign(abs(c) ** p, c)
        y = math.copysign(abs(s_) ** p, s_)
        rr = r * (1 - inner) * 1.0 + 0.0
        pts.append((x * r + c * inner * 0.0, y * r))
    return pts


def sparkle(loc, s, cam, col="#FFF1A0", strength=2.0):
    return [curve2d([star4()], glow_mat("Sparkle", col, strength), extrude=0.03, bevel=0.04, loc=loc, rot=face_rot(cam), scale=s)]


def shell(sign, opening, colors, trim, R=1.0, ridges=11, inner_hex="#E9D8FF"):
    """Scallop half-shell hinged at the origin, fanning toward +Y. sign=+1 domes up (lid), -1 down (base)."""
    na, nr, a0, a1 = 132, 28, math.radians(18), math.radians(162)
    verts, cols, faces = [], [], []
    for i in range(nr + 1):
        r = i / nr
        for j in range(na + 1):
            u = j / na
            a = a0 + (a1 - a0) * u
            rib = abs(math.cos(ridges * PI * u))
            rr = R * r * (1 + 0.045 * rib)
            dome = 0.36 * R * (r ** 0.5) * (1 - r ** 2) ** 0.55 * (math.sin(PI * u) ** 0.4)
            z = sign * (dome + 0.05 * R * r * rib ** 2)
            verts.append((rr * math.cos(a), rr * math.sin(a), z))
            cols.append(colors[min(int(u * ridges), ridges - 1) % len(colors)])
    W = na + 1
    for i in range(nr):
        for j in range(na):
            f = (i * W + j, i * W + j + 1, (i + 1) * W + j + 1, (i + 1) * W + j)
            faces.append(f if sign > 0 else f[::-1])
    me = bpy.data.meshes.new("Shell")
    me.from_pydata(verts, [], faces)
    ca = me.color_attributes.new("Col", "FLOAT_COLOR", "POINT")
    for k, c in enumerate(cols):
        ca.data[k].color = (*lin(c), 1)
    me.materials.append(attr_mat("ShellMat", 0.35))
    me.materials.append(mat("ShellIn", inner_hex, 0.3))
    for p in me.polygons:
        p.use_smooth = True
    ob = link(bpy.data.objects.new("Shell", me))
    sol = ob.modifiers.new("Solid", "SOLIDIFY")
    sol.thickness, sol.offset, sol.material_offset = 0.05, -1, 1
    edge = [Vector(verts[nr * W + j]) for j in range(0, na + 1, 2)]
    rim = tube([tuple(v) for v in edge], 0.035, trim)
    hinge = Vector((0, 0, 0))
    for o in (ob, rim):
        o.rotation_euler = (opening, 0, 0)
    return [ob, rim]


# ------------------------------------------------------------------ core icons
def icon_cash():
    return cash_stack(rot=(0, 0, math.radians(-25))), (0.75, -1.0, 0.85)


def icon_robux():
    white = mat("Robux", "#F4F6FA", 0.35)
    outer = chaikin(ngon(6, 1.0), 2)
    hole = chaikin(ngon(6, 0.7), 2)[::-1]
    sq = chaikin([(-0.34, -0.34), (0.34, -0.34), (0.34, 0.34), (-0.34, 0.34)], 2)
    sq_hole = chaikin([(-0.15, -0.15), (-0.15, 0.15), (0.15, 0.15), (0.15, -0.15)], 2)
    return [curve2d([outer, hole], white, 0.1, 0.06), curve2d([sq, sq_hole], white, 0.1, 0.06)], FRONT


def icon_strength():
    return arm(rot=(0, 0, math.radians(-8))), (0.25, -1.0, 0.12)


def icon_clover():
    leaf, light, stem = mat("Leaf", "#2FBF3A", 0.45), mat("LeafHi", "#6BE86B", 0.45), mat("Stem", "#1F9A2C", 0.5)
    obs = []
    for k in range(4):
        a = PI / 4 + k * PI / 2
        rot2 = lambda p: (p[0] * math.cos(a - PI / 2) - p[1] * math.sin(a - PI / 2), p[0] * math.sin(a - PI / 2) + p[1] * math.cos(a - PI / 2))
        h = [rot2((x, y + 0.06)) for x, y in heart(0.62)]
        hi = [rot2((x * 0.55, y * 0.55 + 0.33)) for x, y in heart(0.62)]
        obs.append(curve2d([h], leaf, 0.06, 0.07))
        obs.append(curve2d([hi], light, 0.02, 0.03, loc=(0, -0.11, 0)))
    obs.append(tube([(0.05, 0.02, -0.1), (0.22, 0.02, -0.55), (0.42, 0.02, -0.92), (0.66, 0.02, -1.15)], 0.075, stem))
    return obs, FRONT


def icon_close():
    white = mat("CloseW", "#F7F8FB", 0.35)
    obs = []
    for a in (PI / 4, -PI / 4):
        bpy.ops.mesh.primitive_cube_add(size=1, rotation=(0, a, 0))
        ob = bpy.context.active_object
        ob.scale = (2.0, 0.52, 0.52)
        obs.append(finish_obj(ob, white, 0.2, smooth=False))
        ob.modifiers["Bevel"].segments = 5
    return obs, FRONT


def icon_fish(out):
    render_fish("Goldfish", "Common", out, size=512, cam_dir=(6.0, 5.2, 2.8), samples=24, margin=1.1)


# ------------------------------------------------------------------ HUD / window icons
def icon_book(out):
    import render_icons
    render_icons.index_icon(out)


def icon_basket():
    red, rim, dark, grey = mat("Basket", "#E8333A", 0.45), mat("BasketRim", "#FF5A5F", 0.4), mat("Slot", "#8E1520", 0.6), mat("Handle", "#AEB6C6", 0.3, 0.5)
    obs = [cyl((0, 0, 0), 0.72, 0.9, red, rot=(0, 0, PI / 4), verts=4, r2=0.98)]
    obs[0].modifiers.new("Bevel", "BEVEL").width = 0.06
    bpy.ops.mesh.primitive_torus_add(major_radius=0.98, minor_radius=0.09, major_segments=4, minor_segments=12, location=(0, 0, 0.45), rotation=(0, 0, PI / 4))
    obs.append(finish_obj(bpy.context.active_object, rim))
    tilt = math.atan((0.98 - 0.72) * math.cos(PI / 4) / 0.9)
    for row, z in enumerate((-0.18, 0.15)):
        hs = 0.51 + (0.69 - 0.51) * (z + 0.45) / 0.9
        for c in (-0.3, 0.0, 0.3):
            obs.append(cube((c, -hs - 0.005, z), (0.13, 0.04, 0.22), dark, 0.03))
            obs[-1].rotation_euler = (-tilt, 0, 0)
            obs.append(cube((hs + 0.005, c, z), (0.04, 0.13, 0.22), dark, 0.03))
            obs[-1].rotation_euler = (0, -tilt, 0)
    h = half_torus(0.62, 0.075, grey)
    h.location = (0, 0, 0.5)
    h.scale = (1, 1, 1.05)
    obs.append(h)
    return obs, (0.6, -1.0, 0.55)


def icon_gift():
    red, red2, yel = mat("Box", "#F0304A", 0.45), mat("Lid", "#FF4A5E", 0.45), mat("Ribbon", "#FFD23F", 0.35)
    obs = [cube((0, 0, 0), (1.2, 1.2, 1.0), red, 0.05), cube((0, 0, 0.6), (1.34, 1.34, 0.3), red2, 0.05),
           cube((0, 0, 0), (0.26, 1.23, 1.0), yel, 0.02), cube((0, 0, 0), (1.23, 0.26, 1.0), yel, 0.02),
           cube((0, 0, 0.6), (0.28, 1.37, 0.32), yel, 0.02), cube((0, 0, 0.6), (1.37, 0.28, 0.32), yel, 0.02)]
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.09, major_segments=40, minor_segments=14,
                                         location=(sx * 0.3, 0, 0.98), rotation=(PI / 2, sx * 0.55, 0))
        ob = bpy.context.active_object
        ob.scale = (1.0, 1.0, 0.62)
        obs.append(finish_obj(ob, yel))
    obs.append(sphere((0, 0, 0.85), (0.15, 0.15, 0.13), yel))
    return obs, (0.6, -1.0, 0.55)


def icon_gear():
    steel = mat("Gear", "#B5BECE", 0.3, 0.6)
    N, pts = 8, []
    for k in range(400):
        a = 2 * PI * k / 400
        t = (a * N / (2 * PI)) % 1
        f = min(1, max(0, (0.5 - abs(t - 0.5) - 0.12) / 0.08))
        r = 0.78 + 0.24 * f
        pts.append((r * math.cos(a), r * math.sin(a)))
    hole = ngon(48, 0.3)[::-1]
    obs = [curve2d([chaikin(pts, 1), hole], steel, 0.14, 0.05)]
    hub = mat("GearHub", "#8A93A6", 0.3, 0.6)
    obs.append(curve2d([ngon(48, 0.52), ngon(48, 0.3)[::-1]], hub, 0.2, 0.04))
    return obs, (0.35, -1.0, 0.35)


def icon_backpack():
    body, dark, strap, yel = mat("Pack", "#E8892B", 0.5), mat("PackDk", "#C26A1A", 0.5), mat("Strap", "#7A4212", 0.55), mat("Buckle", "#FFD23F", 0.35, 0.3)
    obs = [cube((0, 0, 0), (1.05, 0.62, 1.25), body, 0.22), cube((0, -0.02, 0.48), (1.08, 0.66, 0.42), dark, 0.18),
           cube((0, -0.36, -0.22), (0.72, 0.2, 0.55), body, 0.1), cube((0, -0.4, -0.02), (0.74, 0.16, 0.18), dark, 0.07),
           cube((0, -0.475, -0.1), (0.5, 0.02, 0.035), yel, 0.01)]
    for sx in (-0.26, 0.26):
        obs.append(cube((sx, -0.335, 0.3), (0.12, 0.05, 0.42), strap, 0.02))
        obs.append(cube((sx, -0.36, 0.12), (0.16, 0.04, 0.1), yel, 0.02))
    t = half_torus(0.18, 0.05, strap)
    t.location = (0, 0, 0.68)
    obs.append(t)
    return obs, (0.55, -1.0, 0.4)


def icon_magnifier():
    rim, lens, hi, handle = mat("Rim", "#C9D1DE", 0.25, 0.7), mat("Lens", "#8EE3FF", 0.08), mat("Glint", "#FFFFFF", 0.2), mat("Handle", "#C2412E", 0.45)
    obs = [torus((0, 0, 0.15), 0.55, 0.11, rim, rot=(PI / 2, 0, 0)), cyl((0, 0, 0.15), 0.5, 0.06, lens, rot=(PI / 2, 0, 0))]
    obs.append(cube((-0.16, -0.05, 0.33), (0.32, 0.02, 0.08), hi, 0.03))
    obs[-1].rotation_euler = (0, PI / 4, 0)
    d = Vector((math.cos(-PI / 4), 0, math.sin(-PI / 4)))
    a = Vector((0, 0, 0.15)) + d * 0.62
    obs.append(cyl(a + d * 0.08, 0.1, 0.18, rim, rot=(0, PI / 2 + PI / 4, 0)))
    obs.append(cyl(a + d * 0.55, 0.13, 0.75, handle, rot=(0, PI / 2 + PI / 4, 0), bevel=0.04))
    return obs, (0.25, -1.0, 0.2)


def icon_padlock():
    gold, steel, dark = mat("LockBody", "#FFC531", 0.3, 0.35), mat("Shackle", "#C2CAD8", 0.25, 0.7), mat("Keyhole", "#3A2A10", 0.5)
    obs = [cube((0, 0, 0), (1.1, 0.5, 0.88), gold, 0.12)]
    t = half_torus(0.36, 0.1, steel)
    t.location = (0, 0, 0.72)
    obs.append(t)
    for sx in (-0.36, 0.36):
        obs.append(cyl((sx, 0, 0.55), 0.1, 0.36, steel))
    obs.append(cyl((0, -0.25, 0.08), 0.11, 0.04, dark, rot=(PI / 2, 0, 0)))
    obs.append(cube((0, -0.25, -0.1), (0.1, 0.04, 0.26), dark, 0.02))
    return obs, (0.35, -1.0, 0.3)


# ------------------------------------------------------------------ shop art (1024)
def art_clam(rainbow=False):
    cam = (0.25, 1.0, 0.8)
    if rainbow:
        cols, trim, inner = RAINBOW, mat("TrimW", "#FFFFFF", 0.3), "#FFF3FB"
    else:
        cols, trim, inner = ["#7A2FE0", "#A35BFF"], mat("TrimG", "#FFC531", 0.3, 0.6), "#E3CCFF"
    obs = shell(-1, 0.0, cols, trim, inner_hex=inner) + shell(1, math.radians(58), cols, trim, inner_hex=inner)
    pearl = glow_mat("Pearl", "#FFF0FA" if rainbow else "#D9FBFF", 0.6, 0.08)
    obs.append(sphere((0, 0.48, 0.2), (0.27, 0.27, 0.27), pearl))
    if not rainbow:
        gem = glow_mat("Gem", "#3FE6FF", 1.2, 0.1)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.17)
        g = bpy.context.active_object
        g.scale = (1, 0.7, 1.3)
        g.location = Vector((0, 0.16, 0.36))
        g.rotation_euler = (math.radians(58), 0, 0)
        obs.append(finish_obj(g, gem, smooth=False))
    for (x, z, s) in [(-1.05, 0.95, 0.2), (1.0, 1.2, 0.14), (0.95, 0.15, 0.1), (-0.75, -0.1, 0.09)]:
        obs += sparkle((x, 0.6, z), s, cam, "#FFFFFF" if rainbow else "#FFF1A0")
    return obs, cam


def art_cash_pile(level):
    n = [3, 6, 11, 18][level]
    pos, rng = mound(n, [0.9, 1.4, 1.9, 2.4][level], [0.15, 0.45, 0.8, 1.1][level], 10 + level)
    obs = []
    for (x, y, z) in pos:
        obs += cash_stack((x, y, z), (rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), rng.uniform(-0.8, 0.8)), 0.8, bills=int(rng.integers(2, 5)))
    for k in range([2, 6, 12, 20][level]):
        a = rng.uniform(0, 2 * PI)
        r = rng.uniform(0.7, 1.0) * [1.2, 1.7, 2.2, 2.7][level]
        obs += coin((r * math.cos(a) * 1.1, r * math.sin(a) * 0.75, rng.uniform(0.0, 0.3)), (rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), 0), 1.0)
    return obs, (0.6, -1.0, 0.7)


def art_strength_pile(level):
    n = [3, 6, 10][level]
    pos, rng = mound(n, [0.9, 1.4, 1.9][level], [0.3, 0.6, 1.0][level], 30 + level)
    obs = []
    for (x, y, z) in pos:
        obs += arm((x, y, z + 0.3), (rng.uniform(-0.4, 0.4), rng.uniform(-0.3, 0.3), rng.uniform(-0.6, 0.6)), 0.5)
    return obs, (0.3, -1.0, 0.45)


def art_bait_pile(level):
    n = [2, 4, 7, 11][level]
    pos, rng = mound(n, [0.7, 1.2, 1.7, 2.2][level], [0.1, 0.35, 0.7, 1.0][level], 50 + level)
    obs = []
    for i, (x, y, z) in enumerate(pos):
        obs += worm((x, y, z + 0.2), (rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(-PI, PI)), 0.5, phase=rng.uniform(0, PI), eyes=(i % 2 == 0))
    mats = [mat(f"Pellet{i}", c, 0.25) for i, c in enumerate(RAINBOW)]
    for k in range([3, 8, 14, 22][level]):
        a = rng.uniform(0, 2 * PI)
        r = rng.uniform(0.5, 1.0) * [1.0, 1.5, 2.0, 2.5][level]
        obs.append(sphere((r * math.cos(a) * 1.1, r * math.sin(a) * 0.7, 0.06), (0.09,) * 3, mats[k % len(mats)]))
    return obs, (0.4, -1.0, 0.6)


def art_bait():
    return worm(rot=(0, 0, math.radians(-12))), (0.35, -1.0, 0.45)


def art_sparkle():
    return sparkle((0, 0, 0), 1.0, FRONT, "#FFF1A0", 1.2) + sparkle((0.95, -0.05, 0.85), 0.32, FRONT, "#FFFFFF", 1.2), FRONT


def art_x2(kind):
    cam = (0.45, -1.0, 0.45)
    obs = cash_stack(rot=(0, 0, math.radians(-25))) if kind == "cash" else arm(rot=(0, 0, math.radians(-8)))
    col = "#7CFF4F" if kind == "cash" else "#FFD23F"
    obs += text3d("x2", mat("X2", col, 0.35), 1.15, loc=(0.75, -1.0, -0.35), rot=face_rot(cam), extrude=0.1,
                  back=mat("X2Back", "#1B1530", 0.5), back_off=0.07)
    return obs, cam


# ------------------------------------------------------------------ small glyphs
def glyph_arrow_down():
    pts = [(-0.22, 1.0), (0.22, 1.0), (0.22, 0.12), (0.62, 0.12), (0, -0.85), (-0.62, 0.12), (-0.22, 0.12)]
    return [curve2d([chaikin(pts, 2)], mat("ArrowW", "#F7F8FB", 0.35), 0.08, 0.06)], FRONT


def glyph_triangle_up():
    pts = [(-0.85, -0.6), (0.85, -0.6), (0, 0.8)]
    return [curve2d([chaikin(pts, 3)], mat("TriW", "#F7F8FB", 0.35), 0.08, 0.06)], FRONT


def glyph_magnet():
    red, steel = mat("Magnet", "#E8333A", 0.4), mat("Tip", "#D4DAE5", 0.25, 0.7)
    pts = [(-0.55, 0, 0.75), (-0.55, 0, 0.0)]
    pts += [(-0.55 * math.cos(t), 0, -0.55 * math.sin(t)) for t in np.linspace(0, PI, 24)[1:-1]]
    pts += [(0.55, 0, 0.0), (0.55, 0, 0.75)]
    obs = [tube(pts, 0.25, red)]
    for sx in (-0.55, 0.55):
        obs.append(cyl((sx, 0, 0.95), 0.27, 0.4, steel, bevel=0.04))
    parent_all(obs, rot=(0, math.radians(-25), 0))
    return obs, (0.3, -1.0, 0.25)


# name -> (builder, size, samples). Builders either return (objects, cam) or take an output path themselves.
ICONS = {
    "cash": (icon_cash, 512), "robux": (icon_robux, 512), "strength": (icon_strength, 512), "fish": (icon_fish, 512),
    "clover": (icon_clover, 512), "close": (icon_close, 512),
    "book": (icon_book, 512), "basket": (icon_basket, 512), "gift": (icon_gift, 512), "gear": (icon_gear, 512),
    "backpack": (icon_backpack, 512), "magnifier": (icon_magnifier, 512), "padlock": (icon_padlock, 512),
    "clam_enchanted": (lambda: art_clam(False), 1024), "clam_rainbow": (lambda: art_clam(True), 1024),
    **{f"cash_pile_{i + 1}": ((lambda i=i: art_cash_pile(i)), 1024) for i in range(4)},
    **{f"strength_pile_{i + 1}": ((lambda i=i: art_strength_pile(i)), 1024) for i in range(3)},
    **{f"bait_pile_{i + 1}": ((lambda i=i: art_bait_pile(i)), 1024) for i in range(4)},
    "bait_rainbow": (art_bait, 1024), "sparkle": (art_sparkle, 1024),
    "x2_cash": (lambda: art_x2("cash"), 1024), "x2_strength": (lambda: art_x2("strength"), 1024),
    "arrow_down": (glyph_arrow_down, 512), "triangle_up": (glyph_triangle_up, 512), "magnet": (glyph_magnet, 512),
}
TAKES_PATH = {"fish", "book"}


def shot(name, out, size_override=None):
    fn, size = ICONS[name]
    size = size_override or size
    if name in TAKES_PATH:
        fn(out)
        return
    empty_scene()
    _ARM.clear()
    obs, cam = fn()
    obs = [o for o in obs if o.type in {"MESH", "CURVE", "FONT"}]
    uirender.scene_setup(size, samples=24 if size <= 512 else 32, threads=4)
    uirender.default_lights(cam)
    uirender.ortho_camera(obs, cam, margin=1.1)
    uirender.render(out)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    raw = argv[0]
    small = "--small" in argv
    names = [a for a in argv[1:] if not a.startswith("--")] or list(ICONS)
    os.makedirs(raw, exist_ok=True)
    for n in names:
        shot(n, os.path.join(raw, f"{n}.png"), 256 if small else None)
        print("ICON", n, flush=True)


if __name__ == "__main__":
    main()
