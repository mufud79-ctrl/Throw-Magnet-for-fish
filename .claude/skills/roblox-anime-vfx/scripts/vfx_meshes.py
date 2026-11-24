"""VFX mesh kit, built in Blender (headless, bpy as a module).

    /tmp/bpyenv/bin/python vfx_meshes.py [name ...] [--no-render]

Writes for every mesh, into assets/meshes/:
  <name>.fbx   upload to Roblox (Studio 3D Importer / Asset Manager), then use the id in a SpecialMesh
               (MeshType = FileMesh) so scripts can tween Scale, or as a MeshPart.
  <name>.obj   same geometry for other tools
  <name>.json  positions / normals / uvs / indices for the headless previewer
and _meshes.png, a contact sheet render.

Conventions (match the texture library):
  * 1 Blender unit = 1 stud, Y is up in Roblox (exported with Y up). Every mesh fits a ~2-stud box
    centred on its pivot, so SpecialMesh.Scale reads as "radius in studs".
  * Strokes (crescents, rings, swirls, tubes): UV u runs ALONG the stroke (0 = head), v ACROSS it
    (0 = outer / leading edge). A strip texture (slash_strip, energy_strip) maps straight on.
  * Shells are double-sided in geometry (a flipped copy), because SpecialMesh FileMesh is single-sided
    and MeshPart.DoubleSided cannot be set from scripts.
  * Budgets are in POLYGONS (faces; the kit is built from quads). Roblox caps an uploaded mesh at 20,000
    triangles (a quad counts as two), so VFX shells stay at <= 2,500 polys and hero meshes (Meshy,
    retopologised to quads with QuadriFlow) at <= 4,000 polys. POLY_BUDGET enforces it.
"""
import os
import sys
import math
import json
import argparse
import numpy as np
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "meshes")
TAU = 2 * math.pi
POLY_BUDGET = 2500          # per VFX shell (hero meshes: 4000, see retopo_hero)
ROBLOX_TRI_CAP = 20000      # Roblox upload limit, a quad = 2 triangles


# ---------------------------------------------------------------- geometry helpers (Blender Z-up while building)
def grid_surface(f, nu, nv, closed_u=False):
    """f(u, v) -> (x, y, z). Returns verts, faces (quads), uvs per face-corner."""
    us = np.linspace(0, 1, nu + 1)
    vs = np.linspace(0, 1, nv + 1)
    V = [f(u, v) for v in vs for u in us]
    idx = lambda i, j: j * (nu + 1) + i
    F, UV = [], []
    for j in range(nv):
        for i in range(nu):
            F.append((idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)))
            UV.append([(us[i], 1 - vs[j]), (us[i + 1], 1 - vs[j]), (us[i + 1], 1 - vs[j + 1]), (us[i], 1 - vs[j + 1])])
    return V, F, UV


def double_sided(V, F, UV):
    n = len(V)
    V2 = V + V
    F2 = F + [tuple(reversed([k + n for k in f])) for f in F]
    UV2 = UV + [list(reversed(c)) for c in UV]
    return V2, F2, UV2


def merge(*parts):
    V, F, UV = [], [], []
    for pv, pf, puv in parts:
        o = len(V)
        V += pv
        F += [tuple(k + o for k in f) for f in pf]
        UV += puv
    return V, F, UV


def make_object(name, V, F, UV, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(map(float, v)) for v in V], [], [tuple(f) for f in F])
    uvl = me.uv_layers.new(name="UVMap")
    k = 0
    for poly, corners in zip(me.polygons, UV):
        for li, c in zip(poly.loop_indices, corners):
            uvl.data[li].uv = c
        k += 1
    me.validate()
    me.update()
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


# ---------------------------------------------------------------- mesh recipes (Z up)
def crescent(sweep_deg=220, r_out=1.0, r_in=0.62, cone=0.12, head_point=0.08, tail_taper=0.9, nu=72, nv=6):
    """Slash shell: an arc band that is pointed at both ends, fat just behind the head, coned slightly
    so it reads in 3D. Head at angle 0 (+X), sweeping counter-clockwise (toward +Y)."""
    sw = math.radians(sweep_deg)

    def f(u, v):
        w = min(1.0, u / head_point) ** 0.6 * (1 - u) ** tail_taper
        ro = r_out
        ri = r_out - (r_out - r_in) * w
        r = ro + (ri - ro) * v
        a = u * sw
        return (math.cos(a) * r, math.sin(a) * r, cone * (1 - v) * w - cone * 0.5)
    return double_sided(*grid_surface(f, nu, nv))


def ring(r_in=0.55, r_out=1.0, cone=0.0, nu=64, nv=4):
    """Full ring band (flat shockwave, or coned splash ring when cone > 0). u around, v outer->inner."""
    def f(u, v):
        a = u * TAU
        r = r_out + (r_in - r_out) * v
        return (math.cos(a) * r, math.sin(a) * r, cone * (1 - v))
    return double_sided(*grid_surface(f, nu, nv))


def sphere(nu=32, nv=16, hemi=False):
    """UV sphere shell (u around, v pole to pole). hemi = dome (upper half)."""
    top = 0.5 if hemi else 1.0

    def f(u, v):
        th = (1 - v * top) * math.pi          # v=0 north pole
        th = math.pi - (v * top) * math.pi
        a = u * TAU
        return (math.cos(a) * math.sin(th), math.sin(a) * math.sin(th), -math.cos(th))
    return double_sided(*grid_surface(f, nu, nv))


def tube(r0=1.0, r1=1.0, h=2.0, nu=40, nv=6):
    """Open cylinder / cone tube (pillars, beam sleeves, tornado walls). u around, v bottom->top."""
    def f(u, v):
        a = u * TAU
        r = r0 + (r1 - r0) * v
        return (math.cos(a) * r, math.sin(a) * r, -h / 2 + h * v)
    return double_sided(*grid_surface(f, nu, nv))


def swirl(turns=2.5, r0=0.25, r1=1.0, h=2.0, width=0.35, nu=160, nv=4):
    """Rising spiral ribbon that widens toward the top (tornado, vortex, charge-up). u along the ribbon."""
    def f(u, v):
        a = u * turns * TAU
        r = r0 + (r1 - r0) * u
        z = -h / 2 + h * u
        w = width * (0.3 + 0.7 * u) * math.sin(math.pi * min(1, u * 1.15)) ** 0.5
        return (math.cos(a) * r, math.sin(a) * r, z + (v - 0.5) * w)
    return double_sided(*grid_surface(f, nu, nv))


def spike(sides=6, h=2.0, r=0.32, bend=0.0, twist=0.0, nv=8):
    """Faceted crystal spike (ice, earth, light spears): flat facets, sharp tip, optional bend."""
    V, F, UV = [], [], []
    rings = []
    for j in range(nv + 1):
        t = j / nv
        rad = r * (1 - t) ** 0.85
        cx = bend * (t ** 2)
        ring_ = []
        for i in range(sides):
            a = i / sides * TAU + twist * t
            ring_.append(len(V))
            V.append((cx + math.cos(a) * rad, math.sin(a) * rad, -h / 2 + h * t))
        rings.append(ring_)
    for j in range(nv):
        for i in range(sides):
            a, b = rings[j][i], rings[j][(i + 1) % sides]
            c, d = rings[j + 1][(i + 1) % sides], rings[j + 1][i]
            F.append((a, b, c, d))
            UV.append([(i / sides, j / nv), ((i + 1) / sides, j / nv), ((i + 1) / sides, (j + 1) / nv), (i / sides, (j + 1) / nv)])
    base = len(V)
    V.append((0, 0, -h / 2))
    for i in range(sides):
        F.append((rings[0][(i + 1) % sides], rings[0][i], base))
        UV.append([(0.5, 0), (0.5, 0), (0.5, 0)])
    return V, F, UV


def claw(h=2.0, r=0.3, curl=0.9, sides=7, nv=14):
    """Curved horn / claw spike (ice claws, bone spikes): tapered tube swept along an arc."""
    V, F, UV = [], [], []
    rings = []
    for j in range(nv + 1):
        t = j / nv
        ang = curl * t * 1.3
        cx = (1 - math.cos(ang)) / max(curl * 1.3, 1e-3) * h * 0.55
        cz = math.sin(ang) / max(curl * 1.3, 1e-3) * h * 0.55 - h / 2
        tx, tz = math.sin(ang), math.cos(ang)
        rad = r * (1 - t) ** 0.9 + 0.004
        ring_ = []
        for i in range(sides):
            a = i / sides * TAU
            ox, oy = math.cos(a) * rad, math.sin(a) * rad
            ring_.append(len(V))
            V.append((cx + ox * tz, oy, cz - ox * tx))
        rings.append(ring_)
    for j in range(nv):
        for i in range(sides):
            a, b = rings[j][i], rings[j][(i + 1) % sides]
            c, d = rings[j + 1][(i + 1) % sides], rings[j + 1][i]
            F.append((a, b, c, d))
            UV.append([(i / sides, j / nv), ((i + 1) / sides, j / nv), ((i + 1) / sides, (j + 1) / nv), (i / sides, (j + 1) / nv)])
    return V, F, UV


def claw_cluster(n=5, seed=3):
    """Burst of curved claws erupting from one point (ice/bone eruption)."""
    rng = np.random.default_rng(seed)
    parts = []
    for k in range(n):
        V, F, UV = claw(h=rng.uniform(1.4, 2.0), r=rng.uniform(0.18, 0.3), curl=rng.uniform(0.5, 1.1))
        yaw = k / n * TAU + rng.uniform(-0.3, 0.3)
        tilt = rng.uniform(0.15, 0.5)
        out = []
        for x, y, z in V:
            z2 = z + 1.0
            # tilt outward around Y then yaw around Z
            x1 = x * math.cos(tilt) + z2 * math.sin(tilt)
            z1 = -x * math.sin(tilt) + z2 * math.cos(tilt)
            out.append((x1 * math.cos(yaw) - y * math.sin(yaw), x1 * math.sin(yaw) + y * math.cos(yaw), z1 - 1.0))
        parts.append((out, F, UV))
    return merge(*parts)


def spike_cluster(n=7, seed=5):
    """Crystal cluster: faceted spikes fanning out of the ground."""
    rng = np.random.default_rng(seed)
    parts = []
    for k in range(n):
        h = rng.uniform(1.0, 2.0) if k else 2.0
        V, F, UV = spike(sides=int(rng.integers(5, 8)), h=h, r=rng.uniform(0.16, 0.3) * (1.3 if k == 0 else 1))
        yaw = rng.uniform(0, TAU)
        tilt = 0 if k == 0 else rng.uniform(0.25, 0.75)
        out = []
        for x, y, z in V:
            z2 = z + h / 2
            x1 = x * math.cos(tilt) + z2 * math.sin(tilt)
            z1 = -x * math.sin(tilt) + z2 * math.cos(tilt)
            out.append((x1 * math.cos(yaw) - y * math.sin(yaw), x1 * math.sin(yaw) + y * math.cos(yaw), z1 - 1.0))
        parts.append((out, F, UV))
    return merge(*parts)


def wave_curl(nu=32, nv=16):
    """Curling wave sheet (water/sand/shadow waves): rises, curls forward, tapers at both sides.
    u across the width, v from the base up over the lip."""
    def f(u, v):
        x = (u - 0.5) * 2.0
        env = math.sin(math.pi * u) ** 0.6
        ang = v * math.pi * 1.25
        rad = 0.9 * env + 0.05
        y = math.sin(ang) * rad * 0.9
        z = -1.0 + (1 - math.cos(ang)) * rad
        return (x, y - 0.3, z)
    return double_sided(*grid_surface(f, nu, nv))


def torus(R=1.0, r=0.05, nu=64, nv=8):
    def f(u, v):
        a, b = u * TAU, v * TAU
        return ((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))
    return grid_surface(f, nu, nv)


def disc(nu=48, nv=6):
    """Flat disc, polar UV (u around, v rim->centre) for ground glows and auras."""
    def f(u, v):
        a = u * TAU
        r = 1 - v * 0.999
        return (math.cos(a) * r, math.sin(a) * r, 0.0)
    return double_sided(*grid_surface(f, nu, nv))


def fang_wave(sweep_deg=120, nu=60, nv=8):
    """Tall standing crescent blade (flying slash / air blade projectile): crescent in the XZ plane with
    a thick spine that thins to a sharp edge."""
    sw = math.radians(sweep_deg)

    def f(u, v):
        a = -sw / 2 + u * sw
        w = math.sin(math.pi * u) ** 0.7
        r = 1.0 - 0.35 * w * v
        return (math.sin(a) * r * 0.55 + 0.1 * w * (1 - v), (v - 0.5) * 0.06 * w, math.cos(a) * r - 0.5)
    return double_sided(*grid_surface(f, nu, nv))


RECIPES = {
    "crescent_wide":  lambda: crescent(220, 1.0, 0.6, 0.14),
    "crescent_thin":  lambda: crescent(170, 1.0, 0.82, 0.08, tail_taper=1.1),
    "crescent_full":  lambda: crescent(330, 1.0, 0.7, 0.18, tail_taper=1.3),
    "ring_flat":      lambda: ring(0.55, 1.0, 0.0),
    "ring_thin":      lambda: ring(0.86, 1.0, 0.0),
    "ring_cone":      lambda: ring(0.35, 1.0, 0.45),
    "sphere":         lambda: sphere(),
    "dome":           lambda: sphere(32, 8, hemi=True),
    "tube":           lambda: tube(1.0, 1.0, 2.0),
    "cone_tube":      lambda: tube(1.0, 0.25, 2.0),
    "swirl":          lambda: swirl(nu=140),
    "swirl_tight":    lambda: swirl(4.0, 0.5, 0.7, 2.0, 0.22, nu=150),
    "spike":          lambda: spike(6, 2.0, 0.32),
    "spike_bent":     lambda: spike(6, 2.0, 0.3, bend=0.35, twist=0.4),
    "claw":           lambda: claw(),
    "claw_cluster":   lambda: claw_cluster(),
    "spike_cluster":  lambda: spike_cluster(),
    "wave_curl":      lambda: wave_curl(),
    "torus":          lambda: torus(),
    "disc":           lambda: disc(),
    "fang_wave":      lambda: fang_wave(),
}


# ---------------------------------------------------------------- export
def to_json(ob, path):
    """Triangulated arrays in Roblox axes (Y up, -Z forward): x, z, -y from Blender."""
    me = ob.data
    me.calc_loop_triangles()
    uvl = me.uv_layers.active.data
    P, N, UV, I = [], [], [], []
    for tri in me.loop_triangles:
        for li in tri.loops:
            vi = me.loops[li].vertex_index
            co = me.vertices[vi].co
            no = me.loops[li].normal if hasattr(me.loops[li], "normal") else tri.normal
            P += [round(co.x, 4), round(co.z, 4), round(-co.y, 4)]
            N += [round(no.x, 3), round(no.z, 3), round(-no.y, 3)]
            uv = uvl[li].uv
            UV += [round(uv.x, 4), round(uv.y, 4)]
            I.append(len(I))
    json.dump({"P": P, "N": N, "UV": UV, "tris": len(I) // 3}, open(path, "w"), separators=(",", ":"))
    return len(I) // 3


def export(ob, name, out):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=os.path.join(out, name + ".fbx"), use_selection=True, axis_forward="-Z", axis_up="Y",
                             apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="FACE", bake_space_transform=True)
    bpy.ops.wm.obj_export(filepath=os.path.join(out, name + ".obj"), export_selected_objects=True, forward_axis="NEGATIVE_Z", up_axis="Y",
                          export_materials=False)
    return to_json(ob, os.path.join(out, name + ".json"))


def render_sheet(objs, out):
    """Workbench contact sheet: each mesh in its own cell, matcap-ish studio shading, UV checker tint."""
    scn = bpy.context.scene
    scn.render.engine = "BLENDER_WORKBENCH"
    scn.display.shading.light = "STUDIO"
    scn.display.shading.color_type = "OBJECT"
    scn.display.shading.show_backface_culling = False
    scn.render.film_transparent = False
    scn.world = bpy.data.worlds.new("w") if scn.world is None else scn.world
    scn.render.resolution_x, scn.render.resolution_y = 320, 320
    cols = 7
    cam_data = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_data)
    scn.collection.objects.link(cam)
    scn.camera = cam
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 3.0
    from PIL import Image, ImageDraw
    tiles = []
    for ob in objs:
        for o in objs:
            o.hide_render = o is not ob
        ob.color = (0.55, 0.85, 1.0, 1.0)
        cam.location = Vector((3.2, -3.6, 2.6))
        direction = Vector((0, 0, 0)) - cam.location
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        p = os.path.join(out, "_tmp_" + ob.name + ".png")
        scn.render.filepath = p
        bpy.ops.render.render(write_still=True)
        tiles.append((ob.name, Image.open(p).convert("RGB")))
        os.remove(p)
    rows = math.ceil(len(tiles) / cols)
    sheet = Image.new("RGB", (cols * 320, rows * 340), (20, 22, 29))
    d = ImageDraw.Draw(sheet)
    for i, (nm, im) in enumerate(tiles):
        x, y = (i % cols) * 320, (i // cols) * 340
        sheet.paste(im, (x, y))
        d.text((x + 8, y + 322), nm, fill=(230, 230, 240))
    sheet.save(os.path.join(out, "_meshes.png"))


def main():
    argv = sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objs = []
    for nm in a.names or list(RECIPES):
        V, F, UV = RECIPES[nm]()
        ob = make_object(nm, V, F, UV, smooth=nm not in ("spike", "spike_bent", "spike_cluster"))
        polys = len(ob.data.polygons)
        tris = export(ob, nm, a.out)
        assert polys <= POLY_BUDGET and tris <= ROBLOX_TRI_CAP, f"{nm}: {polys} polys over budget"
        print(f"{nm}: {polys} polys")
        objs.append(ob)
    if not a.no_render:
        render_sheet(objs, a.out)


if __name__ == "__main__":
    main()
