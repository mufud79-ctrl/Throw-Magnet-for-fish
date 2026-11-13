"""Preview renderer for TFFA models: Roblox-like bright lighting, ground shadow, and the thick black silhouette
outline the game's thumbnails use. Writes <out>/previews/<name>_<label>.png."""
import os, math
import bpy
import numpy as np
from mathutils import Vector

SKY_TOP, SKY_BOT = np.array([0.36, 0.66, 0.98]), np.array([0.78, 0.90, 1.0])

def _setup(sc, res):
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"
    sc.cycles.samples = int(os.environ.get("TFFA_SAMPLES", 40)); sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    w = bpy.data.worlds.new("W"); sc.world = w
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.62, 0.74, 0.92, 1); bg.inputs[1].default_value = 0.6

def render(model, views, res=(1000, 1000), outline=7):
    sc = bpy.context.scene; _setup(sc, res)
    objs = model.objs
    co = np.array([o.matrix_world @ v.co for o in objs for v in o.data.vertices])
    lo, hi = co.min(0), co.max(0); ctr = Vector(((lo + hi) / 2).tolist()); rad = float(np.linalg.norm(hi - lo)) / 2
    # ground shadow catcher
    bpy.ops.mesh.primitive_plane_add(size=rad * 12, location=(ctr.x, ctr.y, 0))
    gp = bpy.context.active_object; gp.is_shadow_catcher = True
    # sun from upper-front-left of the animal, soft
    sd = bpy.data.lights.new("Sun", "SUN"); sd.energy = 3.3; sd.angle = math.radians(12)
    so = bpy.data.objects.new("Sun", sd); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(40), 0, math.radians(200))
    cd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    tg = bpy.data.objects.new("T", None); sc.collection.objects.link(tg); tg.location = ctr
    cam.constraints.new("TRACK_TO").target = tg
    os.makedirs(os.path.join(model.out, "previews"), exist_ok=True)
    for v in views:
        label, az, el, lens = v[:4]; variant = v[4] if len(v) > 4 else None
        if variant == "plain": variant = None
        _variant(model, variant, lo, hi)
        a, e = math.radians(az), math.radians(el)
        d = Vector((-math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))
        cd.lens = lens; fov = 2 * math.atan(18 / lens)
        c_, r_ = ctr, rad
        if len(v) > 5 and v[5]:                     # close-up: (x, y, z, radius) in build coordinates
            c_ = model.xform @ Vector(v[5][:3]); r_ = v[5][3]
        tg.location = c_
        dist = r_ / math.sin(fov / 2) * 1.02
        cam.location = c_ + d * dist
        so.rotation_euler = (math.radians(42), 0, math.atan2(d.y, d.x) + math.radians(90 - 35))
        path = os.path.join(model.out, "previews", f"{model.name}_{label}.png")
        sc.render.filepath = path; bpy.ops.render.render(write_still=True)
        post(path, outline)
        print("RENDER", path)

RAINBOW = [(0.0, (0.95, 0.25, 0.85)), (0.18, (0.35, 0.3, 1.0)), (0.34, (0.2, 0.85, 1.0)), (0.5, (0.3, 0.95, 0.35)),
           (0.66, (1.0, 0.92, 0.15)), (0.82, (1.0, 0.55, 0.1)), (1.0, (1.0, 0.12, 0.1))]

def _variant(model, variant, lo, hi):
    """Preview-only material overrides (mutations): 'rainbow' = diagonal world-space rainbow (red at head/top)."""
    mat = model.objs[0].data.materials[0]; nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]
    tex = [n for n in nt.nodes if n.type == "TEX_IMAGE"][0]
    for l in list(bsdf.inputs["Base Color"].links): nt.links.remove(l)
    old = [n for n in nt.nodes if n.name.startswith("VAR_")]
    for n in old: nt.nodes.remove(n)
    if not variant:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.6; return
    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.name = "VAR_tc"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.name = "VAR_sep"; nt.links.new(tc.outputs["Object"], sep.inputs[0])
    ma = nt.nodes.new("ShaderNodeMath"); ma.name = "VAR_a"; ma.operation = "MULTIPLY_ADD"
    ma.inputs[1].default_value = 0.55 / (hi[1] - lo[1]); ma.inputs[2].default_value = -lo[1] * 0.55 / (hi[1] - lo[1])
    nt.links.new(sep.outputs["Y"], ma.inputs[0])
    mb = nt.nodes.new("ShaderNodeMath"); mb.name = "VAR_b"; mb.operation = "MULTIPLY_ADD"; mb.inputs[1].default_value = 0.6 / hi[2]
    nt.links.new(sep.outputs["Z"], mb.inputs[0]); nt.links.new(ma.outputs[0], mb.inputs[2])
    rp = nt.nodes.new("ShaderNodeValToRGB"); rp.name = "VAR_ramp"; el = rp.color_ramp.elements
    lin = lambda c: (*[x ** 2.2 for x in c], 1)
    el[0].position, el[0].color = RAINBOW[0][0], lin(RAINBOW[0][1]); el[1].position, el[1].color = RAINBOW[-1][0], lin(RAINBOW[-1][1])
    for pos, c in RAINBOW[1:-1]: e = el.new(pos); e.color = lin(c)
    nt.links.new(mb.outputs[0], rp.inputs[0])
    # keep stud shading (detail map, 0.5 = flat) and the fixed colours (detail alpha 0: eyes, teeth, brows)
    dt = nt.nodes.new("ShaderNodeTexImage"); dt.name = "VAR_detail"; dt.image = model.detail; dt.interpolation = "Closest"
    dt.image.colorspace_settings.name = "Non-Color"
    dt.inputs[0].default_value = (0, 0, 0)
    uvn = nt.nodes.new("ShaderNodeUVMap"); uvn.name = "VAR_uv"; nt.links.new(uvn.outputs[0], dt.inputs[0])
    sc2 = nt.nodes.new("ShaderNodeMath"); sc2.name = "VAR_s2"; sc2.operation = "MULTIPLY"; sc2.inputs[1].default_value = 2.0
    nt.links.new(dt.outputs["Color"], sc2.inputs[0])
    mx = nt.nodes.new("ShaderNodeMix"); mx.name = "VAR_mul"; mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"
    mx.inputs["Factor"].default_value = 1.0
    nt.links.new(rp.outputs["Color"], mx.inputs["A"]); nt.links.new(sc2.outputs[0], mx.inputs["B"])
    keep = nt.nodes.new("ShaderNodeMix"); keep.name = "VAR_keep"; keep.data_type = "RGBA"
    nt.links.new(dt.outputs["Alpha"], keep.inputs["Factor"]); nt.links.new(tex.outputs["Color"], keep.inputs["A"])
    nt.links.new(mx.outputs["Result"], keep.inputs["B"])
    nt.links.new(keep.outputs["Result"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.3

def post(path, r):
    """Composite: sky gradient + shadow + thick black outline around the model silhouette."""
    im = bpy.data.images.load(path); w, h = im.size
    px = np.array(im.pixels[:], np.float32).reshape(h, w, 4); bpy.data.images.remove(im)
    rgb, a = px[..., :3], px[..., 3]
    mask = (a > 0.97).astype(np.float32)
    # shadow-catcher alpha (premultiplied black) where not model
    shadow = np.where(mask > 0, 0, a)
    t = np.linspace(0, 1, h)[:, None, None]
    bg = SKY_BOT * (1 - t) + SKY_TOP * t; bg = np.repeat(bg, w, axis=1)
    out = bg * (1 - shadow[..., None] * 0.55)
    pad = np.pad(mask, r); dil = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r: dil = np.maximum(dil, pad[r + dy:r + dy + h, r + dx:r + dx + w])
    out = out * (1 - dil[..., None]) + np.array([0.02, 0.02, 0.03]) * dil[..., None]
    am = np.clip(a, 0, 1)[..., None] * mask[..., None]
    out = out * (1 - am) + rgb * am
    o = bpy.data.images.new("o", w, h, alpha=False)
    o.pixels.foreach_set(np.concatenate([np.clip(out, 0, 1), np.ones((h, w, 1))], 2).astype(np.float32).ravel())
    o.filepath_raw = path; o.file_format = "PNG"; o.save(); bpy.data.images.remove(o)
