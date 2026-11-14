"""Cannon Tame shops: lobby stalls in the TFFA cannon style (skill: .claude/skills/tffa-animal-models).

usage: /tmp/bpyenv/bin/python tools/blender/shops.py [names ...] [--no-render]
Writes models/CannonTame/Shops/<Name>/. One process per shop (the kit resets Blender).

Static props: one mesh (+ <Name>_Glow for lamps/sparkles, set Material = Neon), no rig. 1 unit = 1 stud, sized for an
R15 avatar (about 5 studs tall): counter top at 3.7 studs. Build space +X = the customer side; the export turns it to
face Roblox -Z (same as the cannons), pivot at the ground centre.
"""
import os, sys, math, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SKILL = os.path.join(ROOT, ".claude", "skills", "tffa-animal-models")
OUT = os.path.join(ROOT, "models", "CannonTame", "Shops")
VIEWS = [("hero", 35, 16, 50), ("front", 0, 8, 50), ("side", 90, 8, 50), ("back", 160, 20, 50)]

# 3x5 pixel font (5 wide for N); "$" is 3x7
FONT = {
    "A": [".#.", "#.#", "###", "#.#", "#.#"], "C": ["###", "#..", "#..", "#..", "###"], "E": ["###", "#..", "##.", "#..", "###"],
    "H": ["#.#", "#.#", "###", "#.#", "#.#"], "L": ["#..", "#..", "#..", "#..", "###"], "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#"],
    "O": ["###", "#.#", "#.#", "#.#", "###"], "P": ["###", "#.#", "###", "#..", "#.."], "R": ["##.", "#.#", "##.", "#.#", "#.#"], "S": ["###", "#..", "###", "..#", "###"],
    "$": [".#.", "###", "#..", "###", "..#", "###", ".#."],
}


def main():
    args = sys.argv[1:]
    if "--one" in args:
        build_one(args[args.index("--one") + 1]); return
    names = [a for a in args if not a.startswith("--")] or list(BUILDERS)
    flags = [a for a in args if a == "--no-render"]
    for n in names:
        print(f"=== {n}", flush=True)
        r = subprocess.run([sys.executable, __file__, "--one", n] + flags, capture_output=True, text=True)
        keep = [l for l in r.stdout.splitlines() if l.startswith(("TRIS", "DONE", "Traceback"))]
        print("\n".join(keep) or r.stdout[-2000:], r.stderr[-3000:] if r.returncode else "")


def kit():
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a == "--no-render"]
    sys.path.insert(0, os.path.join(SKILL, "scripts"))
    import tffa_kit
    return tffa_kit


# ============================================================================== helpers
def prism(m, name, a, b, r0, r1, col, sides=8, chamfer=0.14, glow=False):
    """N-sided prism/frustum from a to b, chamfered cap rims (same as cannons.py)."""
    import bmesh
    from mathutils import Vector
    a, b = Vector(a), Vector(b); ax = (b - a).normalized()
    up = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = ax.cross(up).normalized(); w = ax.cross(u).normalized()
    bm = bmesh.new(); rings = []
    ang = [math.pi / sides + 2 * math.pi * k / sides for k in range(sides)]
    for p, r in ((a, r0), (b, r1)):
        rings.append([bm.verts.new(p + (u * math.cos(t) + w * math.sin(t)) * r) for t in ang])
    for k in range(sides):
        bm.faces.new([rings[0][k], rings[0][(k + 1) % sides], rings[1][(k + 1) % sides], rings[1][k]])
    caps = [bm.faces.new(list(reversed(rings[0]))), bm.faces.new(rings[1])]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if chamfer > 0:
        rim = [e for e in bm.edges if any(f in caps for f in e.link_faces)]
        bmesh.ops.bevel(bm, geom=rim, offset=chamfer * min(min(r0, r1), (b - a).length), segments=1, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    uvl = bm.loops.layers.uv.new("UVMap"); pc = m._plain(col)
    for f in bm.faces:
        for l in f.loops: l[uvl].uv = pc
    return m._obj(name, bm, glow)


def text(m, name, s, center, px, col, depth=0.22, glow=False, back=False, chamfer=0.12):
    """Pixel-block lettering on a +X-facing surface (back=True: a -X-facing one), centred at `center`, reading left
    to right for whoever faces it."""
    from mathutils import Vector
    c = Vector(center)
    widths = [len(FONT[ch][0]) for ch in s]
    total = sum(widths) + (len(s) - 1)
    if back: s, widths = s[::-1], widths[::-1]
    y = c.y - total * px / 2
    for i, ch in enumerate(s):
        rows = FONT[ch]; top = c.z + len(rows) * px / 2
        for r, row in enumerate(rows):
            for k, on in enumerate(row[::-1] if back else row):
                if on == "#":
                    m.box(f"{name}{i}{r}{k}", (c.x, y + (k + 0.5) * px, top - (r + 0.5) * px), (depth, px * 0.94, px * 0.94), col,
                          studs=False, chamfer=chamfer, glow=glow)
        y += (widths[i] + 1) * px


def sparkle(m, name, c, size, col):
    """4-point glowing sparkle facing +X."""
    from mathutils import Vector
    c = Vector(c)
    for k, d in enumerate(((0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))):
        m.spike(f"{name}{k}", c, c + Vector(d) * size, size * 0.3, col, glow=True)


def awning(m, K, name, x0, x1, z0, z1, width, cols, n):
    """Striped sloped awning from the back (x0, z0) down to the front (x1, z1), with a scalloped front edge."""
    from mathutils import Vector
    L = math.hypot(x1 - x0, z1 - z0); ang = math.atan2(z0 - z1, x1 - x0)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2; w = width / n
    for k in range(n):
        y = -width / 2 + w * (k + 0.5); col = cols[k % 2]
        m.box(f"{name}{k}", (cx, y, cz), (L, w, 0.35), col, rot=K.Ry(ang))
        m.box(f"{name}Flap{k}", (x1 + 0.05, y, z1 - 0.45), (0.22, w * 0.9, 0.8), col, bot=(1, 0.35), studs=False)


def lantern(m, name, c, glow_col, iron):
    from mathutils import Vector
    c = Vector(c)
    m.box(name + "Cap", c + Vector((0, 0, 0.45)), (0.62, 0.62, 0.18), iron, studs=False)
    m.box(name, c, (0.48, 0.48, 0.7), glow_col, studs=False, glow=True)
    m.box(name + "Base", c - Vector((0, 0, 0.42)), (0.56, 0.56, 0.14), iron, studs=False)


def mini_cannon(m, name, c, scale, barrel, carriage, trim, bore):
    """Small display cannon (shelf goods / rooftop landmark): carriage block, two wheels, tilted barrel."""
    from mathutils import Vector
    c = Vector(c); s = scale
    m.box(name + "Cart", c + Vector((0, 0, 0.35 * s)), (1.2 * s, 0.8 * s, 0.4 * s), carriage, studs=False)
    for y in (1, -1):
        for x in (0.38, -0.38):
            prism(m, f"{name}Wheel{y}{x}", c + Vector((x * s, y * 0.38 * s, 0.25 * s)), c + Vector((x * s, y * 0.55 * s, 0.25 * s)),
                  0.26 * s, 0.26 * s, carriage, chamfer=0.2)
    a = c + Vector((-0.6 * s, 0, 0.62 * s)); b = c + Vector((0.75 * s, 0, 1.0 * s))
    prism(m, name + "Barrel", a, b, 0.34 * s, 0.27 * s, barrel)
    d = (b - a).normalized()
    prism(m, name + "Lip", b - d * 0.12 * s, b + d * 0.06 * s, 0.34 * s, 0.34 * s, trim)
    prism(m, name + "Bore", b, b + d * 0.08 * s, 0.17 * s, 0.17 * s, bore, chamfer=0.0)
    m.ball(name + "Knob", a - d * 0.12 * s, 0.14 * s, trim, segs=(6, 4))


def balls(m, name, c, r, col):
    """Cannonball pyramid: 4 + 1."""
    from mathutils import Vector
    c = Vector(c)
    for k, (dx, dy) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
        m.ball(f"{name}{k}", c + Vector((dx * r, dy * r, r)), r, col, segs=(8, 6))
    m.ball(f"{name}Top", c + Vector((0, 0, r * 2.4)), r, col, segs=(8, 6))


def group(m, name):
    """Context manager: parts made inside are exported as their own mesh <Name>_<name> (gate doors, screens...)."""
    import contextlib
    @contextlib.contextmanager
    def cm():
        n0 = len(m.parts); yield
        if not hasattr(m, "groups"): m.groups = {}
        m.groups.setdefault(name, []).extend(m.parts[n0:]); del m.parts[n0:]
    return cm()


def done_static(m, glow_color=None, views=None):
    """Like Model.done() without the rig: bake atlas, join, export GLB/FBX/.blend, render previews."""
    import bpy
    import numpy as np
    from mathutils import Matrix, Vector
    m.tex = m._save_png(m._atlas(), f"{m.name}_Texture"); m.detail = m._save_png(m._detail(), f"{m.name}_Detail")
    body = m._join(m.parts, m.name); objs = [body]
    extra = [m._join(lst, f"{m.name}_{g}") for g, lst in getattr(m, "groups", {}).items()]
    objs += extra
    glow = m._join(m.glow, f"{m.name}_Glow") if m.glow else None
    if glow: objs.append(glow)
    co = np.array([v.co[:] for o in objs for v in o.data.vertices]); lo, hi = co.min(0), co.max(0)
    shift = Matrix.Translation(Vector((-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2])))
    R = Matrix.Rotation(math.radians(90), 4, "Z")
    for o in objs:
        o.data.transform(R @ shift); o.location = (0, 0, 0); o.vertex_groups.clear()
    mat = bpy.data.materials.new(f"{m.name}_Mat")
    bsdf = mat.node_tree.nodes["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.6
    tn = mat.node_tree.nodes.new("ShaderNodeTexImage"); tn.image = m.tex; tn.interpolation = "Closest"
    mat.node_tree.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
    for o in [body] + extra: o.data.materials.append(mat)
    if glow:
        gc = glow_color or (1, 1, 1); gm = bpy.data.materials.new(f"{m.name}_Glow_Neon")
        gb = gm.node_tree.nodes["Principled BSDF"]
        gb.inputs["Base Color"].default_value = (*[x ** 2.2 for x in gc], 1)
        gb.inputs["Emission Color"].default_value = (*[x ** 2.2 for x in gc], 1)
        gb.inputs["Emission Strength"].default_value = 2.0
        glow.data.materials.append(gm)
    m.xform = R @ shift; m.objs = objs
    tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs}
    d = body.dimensions
    print(f"TRIS {tris}  SIZE (studs) W {d.x:.1f} x D {d.y:.1f} x H {d.z:.1f}")
    for n_, t in tris.items(): assert t < 20000, f"{n_} has {t} triangles (Roblox limit 20k)"
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    base = os.path.join(m.out, m.name)
    bpy.ops.export_scene.gltf(filepath=base + ".glb", export_format="GLB", use_selection=True, export_animations=False, export_skins=False)
    bpy.ops.export_scene.fbx(filepath=base + ".fbx", use_selection=True, path_mode="COPY", embed_textures=True,
                             mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False)
    bpy.ops.wm.save_as_mainfile(filepath=base + ".blend")
    if m.render_on:
        import tffa_render
        tffa_render.render(m, views or VIEWS)
    print("DONE", base)


# ============================================================================== Cannon Shop
def build_cannon_shop(K, out):
    rgb = K.rgb
    WOOD, WOOD_D, WOOD_DD = rgb(220, 154, 86), rgb(156, 96, 54), rgb(106, 64, 38)
    RED, CREAM, GOLD = rgb(214, 52, 44), rgb(250, 240, 222), rgb(255, 196, 46)
    IRON, BALL, SIGN, BORE = rgb(72, 76, 92), rgb(50, 52, 62), rgb(92, 52, 34), rgb(28, 22, 24)
    LAMP = rgb(255, 204, 100)
    m = K.Model("CannonShop", out, stud=1.0, chamfer=0.12, jitter=0.05)
    ns = dict(studs=False)
    # deck, step, walls, posts
    m.box("Deck", (0, 0, 0.3), (9.0, 15.0, 0.6), WOOD_D)
    m.box("Step", (5.0, 0, 0.15), (1.2, 7.0, 0.3), WOOD_DD)
    m.box("BackWall", (-4.0, 0, 4.6), (0.8, 14.4, 8.0), WOOD)
    for k in range(-3, 4):
        m.box(f"Plank{k}", (-3.58, k * 2.0, 4.6), (0.06, 0.16, 7.8), WOOD_D, chamfer=0.0, **ns)
    for s in (1, -1):
        m.box(f"SideWall{s}", (-1.25, s * 7.0, 2.1), (5.5, 0.7, 3.0), WOOD)
        m.box(f"SideRail{s}", (-1.25, s * 7.0, 3.7), (5.7, 0.9, 0.25), WOOD_DD, **ns)
        m.box(f"PostF{s}", (3.9, s * 6.9, 4.9), (0.8, 0.8, 8.6), WOOD_DD)
        m.box(f"PostB{s}", (-4.0, s * 6.9, 4.9), (0.9, 0.9, 8.6), WOOD_DD)
        lantern(m, f"Lamp{s}", (4.45, s * 6.9, 6.4), LAMP, IRON)
    # counter
    m.box("Counter", (2.6, 0, 2.0), (1.6, 11.0, 2.8), RED)
    m.box("CounterTop", (2.6, 0, 3.55), (2.2, 11.6, 0.3), WOOD)
    m.box("CounterTrim", (3.42, 0, 3.15), (0.08, 11.0, 0.25), GOLD, **ns)
    for y in (-3.6, 0.0, 3.6):
        m.box(f"Panel{y}", (3.43, y, 1.95), (0.08, 3.0, 1.8), WOOD_DD, **ns)
        m.ball(f"PanelBall{y}", (3.5, y, 1.95), 0.55, BALL, segs=(8, 6))
        m.box(f"PanelFuse{y}", (3.65, y + 0.25, 2.55), (0.1, 0.1, 0.35), CREAM, rot=K.Rx(-0.5), **ns)
    for s in (1, -1):
        balls(m, f"Pile{s}", (2.6, s * 4.6, 3.7), 0.3, BALL)
    # back-wall shelves of display cannons (each a different tier colour)
    tiers = [(WOOD, WOOD_DD, IRON), (IRON, rgb(150, 36, 32), GOLD), (rgb(156, 158, 166), rgb(112, 114, 124), rgb(104, 182, 62)),
             (rgb(224, 124, 64), IRON, GOLD), (rgb(255, 118, 170), rgb(124, 72, 44), CREAM), (GOLD, rgb(150, 44, 40), rgb(236, 32, 60))]
    for row, z in enumerate((4.2, 5.6)):
        m.box(f"Shelf{row}", (-3.2, 0, z), (1.0, 11.0, 0.22), WOOD_DD)
        for i, y in enumerate((-3.6, 0.0, 3.6)):
            b, c, t = tiers[row * 3 + i]
            mini_cannon(m, f"Mini{row}{i}", (-3.15, y, z + 0.11), 0.8, b, c, t, BORE)
    for k, (x, y) in enumerate(((-2.4, 5.9), (-2.4, -5.9), (-1.2, 6.0))):           # powder kegs
        prism(m, f"Keg{k}", (x, y, 0.6), (x, y, 2.0), 0.55, 0.55, WOOD, sides=10)
        for z in (0.85, 1.75):
            prism(m, f"KegHoop{k}{z}", (x, y, z), (x, y, z + 0.1), 0.58, 0.58, IRON, sides=10, chamfer=0.0)
    # striped awning
    awning(m, K, "Awning", -4.4, 4.8, 9.2, 7.4, 15.0, (RED, CREAM), 10)
    # sign board with lettering, gold frame, rooftop cannon
    m.box("Sign", (-3.9, 0, 11.3), (0.6, 10.0, 3.0), SIGN)
    for z in (12.85, 9.75):
        m.box(f"SignFrame{z}", (-3.9, 0, z), (0.7, 10.4, 0.3), GOLD, **ns)
    for s in (1, -1):
        m.box(f"SignFrameS{s}", (-3.9, s * 5.1, 11.3), (0.7, 0.3, 3.4), GOLD, **ns)
        m.box(f"SignPost{s}", (-3.9, s * 3.5, 9.4), (0.4, 0.4, 1.0), WOOD_DD, **ns)
    text(m, "Txt", "CANNONS", (-3.52, 0, 11.3), 0.26, CREAM)
    text(m, "TxtB", "CANNONS", (-4.28, 0, 11.3), 0.26, CREAM, back=True, chamfer=0.0)
    for z in (2.0, 7.2):
        m.box(f"BackTrim{z}", (-4.44, 0, z), (0.1, 14.4, 0.35), WOOD_DD, **ns)
    mini_cannon(m, "Roof", (-3.9, 0, 12.95), 2.4, IRON, WOOD_D, GOLD, BORE)
    done_static(m, LAMP, VIEWS)


# ============================================================================== Sell Stand
def build_sell_shop(K, out):
    from mathutils import Vector
    rgb = K.rgb
    GREEN, GREEN_D, CREAM = rgb(66, 176, 84), rgb(36, 118, 60), rgb(250, 244, 226)
    GOLD, GOLD_D, GOLD_L = rgb(255, 196, 46), rgb(214, 140, 24), rgb(255, 226, 120)
    STONE, STONE_D, IRON = rgb(178, 178, 184), rgb(128, 128, 136), rgb(72, 76, 92)
    BAG, ROPE, RUBY = rgb(196, 146, 84), rgb(130, 88, 50), rgb(236, 32, 60)
    LAMP, SPARK = rgb(255, 204, 100), rgb(255, 240, 160)
    m = K.Model("SellShop", out, stud=1.0, chamfer=0.12, jitter=0.05)
    ns = dict(studs=False)
    m.box("Deck", (0, 0, 0.3), (8.0, 13.0, 0.6), STONE)
    m.box("Step", (4.5, 0, 0.15), (1.0, 6.0, 0.3), STONE_D)
    m.box("BackWall", (-3.5, 0, 4.3), (0.8, 12.4, 7.4), GREEN_D)
    for s in (1, -1):
        m.box(f"PostF{s}", (3.4, s * 6.0, 4.6), (0.8, 0.8, 8.0), CREAM)
        m.box(f"PostB{s}", (-3.5, s * 6.0, 4.6), (0.9, 0.9, 8.0), CREAM)
        m.box(f"SideWall{s}", (-1.0, s * 6.05, 2.0), (4.4, 0.6, 2.8), GREEN)
        lantern(m, f"Lamp{s}", (3.95, s * 6.0, 6.0), LAMP, IRON)
    # counter with a big coin on the front
    m.box("Counter", (2.4, 0, 2.0), (1.6, 9.5, 2.8), GREEN)
    m.box("CounterTop", (2.4, 0, 3.55), (2.2, 10.0, 0.3), GOLD)
    for y in (-3.3, 3.3):
        m.box(f"Panel{y}", (3.23, y, 1.95), (0.08, 2.2, 1.8), GREEN_D, **ns)
    prism(m, "FrontCoin", (3.2, 0, 1.95), (3.45, 0, 1.95), 1.05, 1.05, GOLD, sides=12, chamfer=0.25)
    text(m, "FrontDollar", "$", (3.5, 0, 1.95), 0.2, GOLD_D, depth=0.12)
    # balance scale (coins vs a ruby), coin stacks, money bags
    sc = Vector((2.4, -2.6, 3.7))
    m.box("ScaleBase", sc + Vector((0, 0, 0.15)), (0.9, 1.1, 0.3), GOLD_D, **ns)
    prism(m, "ScalePole", sc + Vector((0, 0, 0.3)), sc + Vector((0, 0, 1.9)), 0.1, 0.1, GOLD)
    m.box("ScaleBeam", sc + Vector((0, 0, 1.9)), (0.16, 2.4, 0.14), GOLD, rot=Rx_(0.12), **ns)
    for s, dz in ((1, -0.14), (-1, 0.14)):
        top = sc + Vector((0, s * 1.1, 1.9 + dz)); pan = top - Vector((0, 0, 0.95))
        m.seg(f"String{s}", top, pan, 0.04, 0.04, GOLD_D, studs=False)
        prism(m, f"Pan{s}", pan - Vector((0, 0, 0.08)), pan, 0.45, 0.5, GOLD, sides=10, chamfer=0.2)
    for k in range(4):
        prism(m, f"PanCoin{k}", sc + Vector((0, 1.1, 0.88 + 0.07 * k)), sc + Vector((0, 1.1, 0.94 + 0.07 * k)), 0.24, 0.24, GOLD_L, sides=10, chamfer=0.2)
    m.ball("PanRuby", sc + Vector((0, -1.1, 1.3)), 0.24, RUBY, segs=(8, 6))
    for k, (y, n) in enumerate(((0.6, 5), (1.3, 3), (2.0, 7), (2.7, 4), (3.4, 6))):
        for j in range(n):
            z = 3.7 + 0.12 * j
            prism(m, f"Stack{k}{j}", (2.4 + 0.02 * (j % 2), y, z), (2.4, y, z + 0.1), 0.28, 0.28, GOLD if j % 2 else GOLD_L, sides=10, chamfer=0.2)
    for k, (x, y, r) in enumerate(((4.7, 4.6, 0.65), (4.9, -4.7, 0.55), (-2.4, 5.0, 0.6))):
        z = r if x > 4 else 0.6 + r
        m.ball(f"Bag{k}", (x, y, z), (r, r, r * 0.95), BAG, segs=(8, 6))
        m.box(f"BagTie{k}", (x, y, z + r * 0.9), (r * 0.6, r * 0.6, r * 0.2), ROPE, **ns)
        m.box(f"BagTuft{k}", (x, y, z + r * 1.15), (r * 0.5, r * 0.5, r * 0.35), BAG, top=(1.4, 1.4), **ns)
        text(m, f"BagDollar{k}", "$", (x + r * 0.95, y, z), r * 0.16, GREEN_D, depth=0.1)
    for k, (x, y) in enumerate(((-2.5, -4.6), (-2.2, 3.4))):                        # gold piles at the back
        m.ball(f"GoldPile{k}", (x, y, 0.6), (1.0, 0.9, 0.55), GOLD, segs=(8, 5))
        for j in range(5):
            a = j * 1.3
            prism(m, f"PileCoin{k}{j}", (x + 0.6 * math.cos(a), y + 0.5 * math.sin(a), 0.9 + 0.12 * (j % 2)),
                  (x + 0.6 * math.cos(a), y + 0.5 * math.sin(a), 1.0 + 0.12 * (j % 2)), 0.22, 0.22, GOLD_L, sides=10, chamfer=0.2)
    awning(m, K, "Awning", -3.9, 4.3, 8.6, 7.0, 13.0, (GREEN, CREAM), 9)
    # sign + giant coin on top
    m.box("Sign", (-3.4, 0, 10.3), (0.6, 7.0, 2.6), GREEN_D)
    for z in (11.65, 8.95):
        m.box(f"SignFrame{z}", (-3.4, 0, z), (0.7, 7.4, 0.3), GOLD, **ns)
    for s in (1, -1):
        m.box(f"SignFrameS{s}", (-3.4, s * 3.6, 10.3), (0.7, 0.3, 3.0), GOLD, **ns)
        m.box(f"SignPost{s}", (-3.4, s * 2.6, 8.6), (0.4, 0.4, 0.8), CREAM, **ns)
    text(m, "Txt", "SELL", (-3.02, 0, 10.3), 0.4, GOLD_L)
    text(m, "TxtB", "SELL", (-3.78, 0, 10.3), 0.4, GOLD_L, back=True, chamfer=0.0)
    for z in (1.8, 6.6):
        m.box(f"BackTrim{z}", (-3.94, 0, z), (0.1, 12.4, 0.35), GOLD, **ns)
    cc = Vector((-3.4, 0, 13.4))
    prism(m, "BigCoin", cc - Vector((0.3, 0, 0)), cc + Vector((0.3, 0, 0)), 1.42, 1.42, GOLD, sides=14, chamfer=0.2)
    prism(m, "BigCoinRim", cc - Vector((0.2, 0, 0)), cc + Vector((0.2, 0, 0)), 1.64, 1.64, GOLD_D, sides=14, chamfer=0.25)
    text(m, "BigDollar", "$", cc + Vector((0.34, 0, 0)), 0.3, GOLD_D, depth=0.14)
    text(m, "BigDollarB", "$", cc - Vector((0.34, 0, 0)), 0.3, GOLD_D, depth=0.14, back=True, chamfer=0.0)
    m.box("CoinStand", (-3.4, 0, 11.95), (0.5, 0.8, 0.5), GOLD_D, **ns)
    sparkle(m, "Spark0", cc + Vector((0.4, 1.4, 1.0)), 0.45, SPARK)
    sparkle(m, "Spark1", cc + Vector((0.4, -1.55, -0.6)), 0.32, SPARK)
    done_static(m, SPARK, VIEWS)


def Rx_(a):
    from mathutils import Matrix
    return Matrix.Rotation(a, 3, "X")


BUILDERS = {"CannonShop": build_cannon_shop, "SellShop": build_sell_shop}


def build_one(name):
    K = kit()
    BUILDERS[name](K, os.path.join(OUT, name))


if __name__ == "__main__":
    main()
