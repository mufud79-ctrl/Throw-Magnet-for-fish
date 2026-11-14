"""Cannon Tame cannons: 14 upgrade tiers in the TFFA style (skill: .claude/skills/tffa-animal-models).

usage: /tmp/bpyenv/bin/python tools/blender/cannons.py [tier numbers ...] [--no-render] [--sheet]
Writes models/CannonTame/Cannons/<NN>_<Theme>/<Theme>Cannon/. One process per cannon (the kit resets Blender).

Build space (same as the animals): +X = the way the cannon fires, +Y = its left, +Z = up, ground at z = 0, 1 unit = 1 stud.
Export faces Roblox forward (-Z), pivot at the ground centre.

Rig (one skinned mesh + optional _Glow mesh):
  Body   - carriage / pedestal (everything not in another bone)
  Barrel - pivots on the trunnion axle; rotate this bone to aim (X = pitch, Y = yaw in the bone's axes)
  Muzzle - empty bone at the mouth of the bore, child of Barrel: spawn projectiles at Muzzle.WorldPosition
  Wing_L/R, Halo, Ring - decorative extras on high tiers
Clips: Idle (loop) and Fire (one-shot recoil: barrel kicks up and slides back, then settles).

Tiers: studded look for the early, "natural" cannons; faceted look (no studs, gradients, Neon glow) for the late ones.
"""
import os, sys, math, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SKILL = os.path.join(ROOT, ".claude", "skills", "tffa-animal-models")
OUT = os.path.join(ROOT, "models", "CannonTame", "Cannons")

# 14 tiers, each cooler than the last. Builders are filled in as tiers get modelled.
ROSTER = ["Wooden", "Iron", "Stone", "Bamboo", "Copper", "Candy", "Golden",
          "Frost", "Lava", "Toxic", "Cyber", "Dragon", "Galaxy", "Celestial"]

VIEWS = [("hero", 40, 14, 50), ("side", 90, 4, 50), ("front", 0, 8, 50), ("back", 150, 22, 50)]


def main():
    args = sys.argv[1:]
    if "--sheet-only" in args:
        sheet(); return
    if "--one" in args:
        build_one(int(args[args.index("--one") + 1])); return
    tiers = [int(a) for a in args if a.isdigit()] or [i + 1 for i in range(len(ROSTER)) if (i + 1) in BUILDERS]
    flags = [a for a in args if a == "--no-render"]
    for t in tiers:
        print(f"=== {t:02d} {ROSTER[t - 1]}", flush=True)
        r = subprocess.run([sys.executable, __file__, "--one", str(t)] + flags, capture_output=True, text=True)
        keep = [l for l in r.stdout.splitlines() if l.startswith(("TRIS", "DONE", "CLIPS", "Traceback"))]
        print("\n".join(keep) or r.stdout[-2000:], r.stderr[-3000:] if r.returncode else "")
    if "--sheet" in args: subprocess.run(["python3", __file__, "--sheet-only"])   # Pillow lives in the system python


# ============================================================================== kit glue (only imported in --one runs)
def kit():
    sys.argv = sys.argv[:1] + [a for a in sys.argv[1:] if a == "--no-render"]
    sys.path.insert(0, os.path.join(SKILL, "scripts"))
    import tffa_kit, tffa_anim
    tffa_anim.add_clips = cannon_clips          # done() asks tffa_anim for clips: cannons get Idle + Fire
    return tffa_kit


def prism(m, name, a, b, r0, r1, col, sides=8, chamfer=0.14, glow=False, grad=None, spin=0.0):
    """N-sided prism/frustum from a to b (barrel hoops, wheels, hubs, pedestals). Flat faces at the axis' sides and
    top; only the two cap rims are chamfered, so 8 sides read as a chunky faceted cylinder."""
    import bmesh
    from mathutils import Vector
    a, b = Vector(a), Vector(b); ax = (b - a).normalized()
    up = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = ax.cross(up).normalized(); w = ax.cross(u).normalized()
    bm = bmesh.new(); rings = []
    ang = [spin + math.pi / sides + 2 * math.pi * k / sides for k in range(sides)]
    for p, r in ((a, r0), (b, r1)):
        rings.append([bm.verts.new(p + (u * math.cos(t) + w * math.sin(t)) * r) for t in ang])
    for k in range(sides):
        bm.faces.new([rings[0][k], rings[0][(k + 1) % sides], rings[1][(k + 1) % sides], rings[1][k]])
    caps = [bm.faces.new(list(reversed(rings[0]))), bm.faces.new(rings[1])]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if chamfer > 0:
        rim = [e for e in bm.edges if any(f in caps for f in e.link_faces)]
        off = chamfer * min(min(r0, r1), (b - a).length)
        bmesh.ops.bevel(bm, geom=rim, offset=off, segments=1, profile=0.5, affect="EDGES", clamp_overlap=True)
    return _paint(m, name, bm, col, glow, grad)


def ring(m, name, center, axis, R, thick, col, n=16, glow=False, depth=None):
    """Faceted torus with a square cross-section (halos, rune rings, collars)."""
    import bmesh
    from mathutils import Vector
    c, ax = Vector(center), Vector(axis).normalized()
    up = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = ax.cross(up).normalized(); w = ax.cross(u).normalized(); d = depth or thick
    bm = bmesh.new(); loops = []
    for k in range(n):
        t = 2 * math.pi * k / n; rad = u * math.cos(t) + w * math.sin(t)
        loops.append([bm.verts.new(c + rad * (R + dr) + ax * dz) for dr, dz in
                      ((-thick / 2, -d / 2), (thick / 2, -d / 2), (thick / 2, d / 2), (-thick / 2, d / 2))])
    for k in range(n):
        A, B = loops[k], loops[(k + 1) % n]
        for j in range(4): bm.faces.new([A[j], A[(j + 1) % 4], B[(j + 1) % 4], B[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _paint(m, name, bm, col, glow, None)


def gem(m, name, center, direction, length, r, col, sides=6, glow=True, back=0.45):
    """Double pyramid crystal: tip along direction, a shorter point behind."""
    from mathutils import Vector
    c, d = Vector(center), Vector(direction).normalized()
    m.spike(name + "F", c, c + d * length, r, col, sides=sides, glow=glow)
    m.spike(name + "B", c, c - d * length * back, r, col, sides=sides, glow=glow)


def _paint(m, name, bm, col, glow, grad):
    uvl = bm.loops.layers.uv.new("UVMap")
    zs = [v.co.z for v in bm.verts]; lo, hi = min(zs), max(zs)
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = m._grad_uv(grad, l.vert.co.z, lo, hi) if grad else m._plain(col)
    return m._obj(name, bm, glow)


def octa(w):
    """Prism radius whose flats sit at half-width w/2 (matches a seg built with chamfer=0.29)."""
    return (w / 2) / math.cos(math.pi / 8)


# ============================================================================== clips
def cannon_clips(arm, model):
    """Idle (72 f loop) and Fire (30 f one-shot). Bone axes (see tffa_kit Model._rig): rot X = pitch (+ nose up),
    Y = yaw, Z = roll about the backward axis; location in units of model height, Z = backward."""
    import tffa_anim
    S = tffa_anim.S
    names = [b.name for b in arm.data.bones]; H = float(arm.get("height", 3.0))
    g = dict(getattr(model, "gait", {}) or {})
    fl = g.get("float", False)
    P = {"Barrel": lambda t: (1.0 * S(t, 0.2), 0.8 * S(t), 0)}
    if fl: P["Body"] = lambda t: ((0.8 * S(t, 0.25), 0, 0.6 * S(t, 0.1)), (0, 0.025 * S(t), 0))
    if "Halo" in names: P["Halo"] = lambda t: (0, 0, -45 * t)            # 8-fold halo: 45 deg per loop is seamless
    if "Ring" in names: P["Ring"] = lambda t: (0, 22.5 * t, 0)           # 16-fold ground ring
    for s, n in ((1, "Wing_L"), (-1, "Wing_R")):
        if n in names: P[n] = (lambda s: lambda t: (0, 0, s * (-3 + 4 * S(t))))(s)
    clips = [_clip(arm, "Idle", 72, P, H)]

    def kick(t):                  # 0 -> 1 fast (3 f), then eases back to rest by 80% of the clip
        if t < 0.1: return math.sin(math.pi / 2 * t / 0.1)
        if t < 0.8: return 0.5 + 0.5 * math.cos(math.pi * (t - 0.1) / 0.7)
        return 0.0
    rec = g.get("recoil", 0.3) / H                      # studs of slide-back
    P = {"Barrel": lambda t: ((7 * kick(t), 0, 0), (0, 0, rec * kick(t))),
         "Body": lambda t: ((-1.2 * kick(t), 0, 0), (0, 0.004 * kick(t), 0.08 * rec * kick(t)))}
    if "Halo" in names: P["Halo"] = lambda t: (0, 0, -45 * t - 90 * kick(t))
    for s, n in ((1, "Wing_L"), (-1, "Wing_R")):
        if n in names: P[n] = (lambda s: lambda t: (0, 0, s * 14 * kick(t)))(s)
    clips.append(_clip(arm, "Fire", 30, P, H))
    return clips


def _clip(arm, name, frames, poses, height):
    """Like tffa_anim._clip but t runs 0..1 inclusive (no wrap), so spins and one-shots key their last frame right."""
    import bpy
    act = bpy.data.actions.new(f"{arm.name}_{name}"); act["clip"] = name; act["frames"] = frames; act.use_fake_user = True
    arm.animation_data_create(); arm.animation_data.action = act
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"; pb.rotation_euler = (0, 0, 0); pb.location = (0, 0, 0)
        for f in (0, frames):
            pb.keyframe_insert("rotation_euler", frame=f); pb.keyframe_insert("location", frame=f)
    for f in range(0, frames + 1, 1 if frames <= 30 else 2):
        t = f / frames
        for bn, fn in poses.items():
            pb = arm.pose.bones.get(bn)
            if pb is None: continue
            r = fn(t); rot = r[0] if isinstance(r[0], tuple) else r
            pb.rotation_euler = tuple(math.radians(a) for a in rot); pb.keyframe_insert("rotation_euler", frame=f)
            if isinstance(r[0], tuple) and len(r) > 1:
                pb.location = tuple(v * height for v in r[1]); pb.keyframe_insert("location", frame=f)
    return act


# ============================================================================== tier 01: Wooden (base, studded)
def build_wooden(K, out):
    from mathutils import Vector
    rgb, Ry = K.rgb, K.Ry
    WOOD, WOOD_D, WOOD_DD = rgb(226, 160, 84), rgb(158, 92, 50), rgb(112, 64, 38)
    CART = rgb(176, 102, 54)
    IRON, IRON_D, BORE = rgb(92, 96, 108), rgb(62, 64, 74), rgb(30, 24, 26)
    m = K.Model("WoodenCannon", out, stud=0.26, chamfer=0.18, jitter=0.06)
    m.gait = {"recoil": 0.3}
    T = Vector((0.5, 0, 2.15))                                   # trunnion axle (barrel pivot)

    with m.bone("Body", (0, 0, 1.0)):
        # wheels: four chunky octagonal trucks, flat face down
        for x in (-1.0, 1.05):
            m.box(f"Axle{x}", (x, 0, 0.56), (0.36, 2.05, 0.36), IRON_D, studs=False)
            for s in (1, -1):
                prism(m, f"Wheel{x}{s}", (x, s * 0.78, 0.56), (x, s * 1.16, 0.56), 0.56, 0.56, WOOD_DD, chamfer=0.22)
                prism(m, f"Hub{x}{s}", (x, s * 1.1, 0.56), (x, s * 1.26, 0.56), 0.2, 0.17, IRON, chamfer=0.25)
        # bed + stepped cheeks (the classic naval carriage staircase)
        m.box("Bed", (0, 0, 0.86), (2.95, 1.3, 0.42), WOOD_D)
        for s in (1, -1):
            y = s * 0.6
            m.box(f"CheekF{s}", (0.82, y, 1.42), (1.1, 0.34, 1.46), CART)
            m.box(f"CheekM{s}", (-0.12, y, 1.2), (0.86, 0.34, 1.02), CART)
            m.box(f"CheekB{s}", (-0.98, y, 1.0), (0.98, 0.34, 0.62), CART)
            m.box(f"Strap{s}", (T.x, y, T.z + 0.06), (0.52, 0.4, 0.22), IRON, studs=False)
            for x, z in ((1.22, 1.9), (0.1, 1.55), (-0.85, 1.18)):          # bolt heads
                m.box(f"Bolt{s}{x}", (x, s * 0.78, z), (0.14, 0.06, 0.14), IRON_D, studs=False, chamfer=0.1)
        # quoin (aiming wedge) under the breech
        m.box("Quoin", (-0.95, 0, 1.2), (0.95, 0.72, 0.32), WOOD_DD, top=(0.55, 1), shift=(-0.2, 0))

    with m.bone("Barrel", T), m.frame(pivot=T, rot=Ry(-0.14)):
        X = lambda dx: T.x + dx
        kw = dict(chamfer=0.22)
        m.seg("Breech", (X(-2.1), 0, T.z), (X(-1.3), 0, T.z), 1.16, 1.22, WOOD, **kw)
        m.seg("Chase", (X(-1.4), 0, T.z), (X(1.6), 0, T.z), 1.22, 1.0, WOOD, **kw)
        m.seg("Swell", (X(1.5), 0, T.z), (X(2.1), 0, T.z), 1.0, 1.14, WOOD, **kw)
        for nm, x0, x1, w in (("Hoop0", -2.0, -1.76, 1.2), ("Hoop1", -0.62, -0.4, 1.17), ("Hoop2", 0.72, 0.92, 1.07),
                              ("Muzzle", 1.86, 2.16, 1.16)):
            r = octa(w) + 0.07
            prism(m, nm, (X(x0), 0, T.z), (X(x1), 0, T.z), r, r, IRON, chamfer=0.2)
        prism(m, "Bore", (X(2.0), 0, T.z), (X(2.18), 0, T.z), 0.4, 0.4, BORE, chamfer=0.0)
        prism(m, "Cascabel", (X(-2.42), 0, T.z), (X(-2.04), 0, T.z), 0.2, 0.24, IRON)
        m.ball("Knob", (X(-2.5), 0, T.z), 0.25, IRON, segs=(8, 6))
        prism(m, "Trunnion", (T.x, -0.82, T.z), (T.x, 0.82, T.z), 0.18, 0.18, IRON)
        m.box("Vent", (X(-1.55), 0, T.z + 0.62), (0.22, 0.22, 0.12), IRON_D, studs=False)
        m.seg("Fuse", (X(-1.55), 0, T.z + 0.64), (X(-1.7), 0, T.z + 0.92), 0.08, 0.06, rgb(40, 34, 30), studs=False)
        with m.bone("Muzzle", (X(2.18), 0, T.z)): pass

    m.done(views=VIEWS)


# ============================================================================== tier 14: Celestial (final, faceted + glow)
def build_celestial(K, out):
    from mathutils import Vector
    rgb, Ry, dk, lt = K.rgb, K.Ry, K.dk, K.lt
    MARBLE, MARBLE_S = rgb(246, 246, 252), rgb(206, 214, 236)
    GOLD, GOLD_D = rgb(255, 198, 52), rgb(222, 148, 30)
    SKY = rgb(150, 206, 255)
    GLOW = rgb(110, 225, 255)
    m = K.Model("CelestialCannon", out, stud=0.4, chamfer=0.16)
    m.gait = {"float": True, "recoil": 0.45}
    T = Vector((0.2, 0, 3.05))
    ns = dict(studs=False)

    with m.bone("Ring", (0, 0, 0.05), parent="Root"):           # rune ring on the ground under the hovering plinth
        ring(m, "GroundRing", (0, 0, 0.05), (0, 0, 1), 2.25, 0.34, GLOW, n=16, glow=True, depth=0.08)
        for k in range(8):
            a = 2 * math.pi * k / 8 + math.pi / 8
            m.box(f"Rune{k}", (2.25 * math.cos(a), 2.25 * math.sin(a), 0.09), (0.22, 0.22, 0.12), GLOW, rot=K.Rz(a + math.pi / 4),
                  studs=False, glow=True)

    with m.bone("Body", (0, 0, 1.0)):
        # hovering plinth: marble tiers with gold trim, a gold crystal point underneath
        m.spike("Keel", (0, 0, 0.62), (0, 0, 0.2), 1.25, GOLD_D, sides=8, rot=math.pi / 8)
        prism(m, "Plinth0", (0, 0, 0.55), (0, 0, 1.0), 1.95, 1.82, MARBLE, grad=(MARBLE_S, MARBLE, MARBLE))
        prism(m, "Trim0", (0, 0, 0.95), (0, 0, 1.12), 2.0, 2.0, GOLD)
        prism(m, "Plinth1", (0, 0, 1.1), (0, 0, 1.45), 1.55, 1.38, MARBLE)
        prism(m, "Collar", (0, 0, 1.42), (0, 0, 1.68), 1.12, 1.04, GOLD)
        for k in range(8):                                        # glowing gem studs around the trim
            a = 2 * math.pi * k / 8 + math.pi / 8
            gem(m, f"TrimGem{k}", (2.04 * math.cos(a), 2.04 * math.sin(a), 1.03), (math.cos(a), math.sin(a), 0), 0.16, 0.1, GLOW, sides=4)
        # yoke: two gold arms up to the trunnions, a gem on each cap
        for s in (1, -1):
            m.seg(f"Arm{s}", (T.x - 0.25, s * 0.78, 1.5), (T.x, s * 1.0, T.z), 0.42, 0.34, GOLD, d0=0.7, d1=0.5, **ns)
            m.box(f"Cap{s}", (T.x, s * 1.04, T.z), (0.72, 0.36, 0.72), GOLD, **ns)
            gem(m, f"CapGem{s}", (T.x, s * 1.24, T.z), (0, s, 0), 0.3, 0.22, GLOW, sides=6)
        # angel wings off the back of each arm: 6 blade feathers, white -> sky -> gold tips
        for s, wn in ((1, "Wing_L"), (-1, "Wing_R")):
            root = Vector((T.x - 0.3, s * 1.12, T.z - 0.15))
            with m.bone(wn, root):
                X = Vector((-1, 0.7 * s, 0)).normalized(); Z = Vector((0, 0.2 * s, 1)).normalized()
                N = X.cross(Z).normalized()
                for k in range(6):
                    th = math.radians(78 - k * 15)
                    d = (X * math.cos(th) + Z * math.sin(th)).normalized(); side = d.cross(N).normalized()
                    L, w = 3.1 - k * 0.27, 0.68 - k * 0.03
                    m.slab(f"Feather{s}{k}", [(-w / 2, 0), (w / 2, 0), (w * 0.5, L * 0.72), (0, L), (-w * 0.42, L * 0.8)], 0.14,
                           MARBLE, origin=root - N * (0.05 * k), xaxis=side, yaxis=d, grad=(SKY, MARBLE, GOLD))
                m.box(f"WingRoot{s}", root, (0.5, 0.4, 0.5), GOLD, **ns)

    with m.bone("Barrel", T), m.frame(pivot=T, rot=Ry(-0.2)):
        X = lambda dx: T.x + dx
        P = lambda dx, dz=0: (X(dx), 0, T.z + dz)
        prism(m, "Breech", P(-2.2), P(-0.85), 0.98, 0.92, GOLD)
        prism(m, "GemSet", P(-2.42), P(-2.15), 0.62, 0.78, GOLD_D)
        gem(m, "CoreGem", P(-2.42), (-1, 0, 0), 0.62, 0.5, GLOW, sides=8, back=0.2)
        prism(m, "Chase", P(-1.0), P(3.2), 0.82, 0.62, MARBLE)
        for nm, x0, x1, r in (("Band0", -0.95, -0.62, 0.95), ("Band1", 1.0, 1.24, 0.8), ("Band2", 2.3, 2.52, 0.74)):
            prism(m, nm, P(x0), P(x1), r, r, GOLD)
        prism(m, "Trunnion", (T.x, -0.95, T.z), (T.x, 0.95, T.z), 0.24, 0.24, GOLD_D)
        # swept dorsal blade fin
        m.slab("Fin", [(-0.9, 0), (1.4, 0), (0.4, 0.55), (-1.25, 0.95)], 0.14, GOLD, origin=P(0.3, 0.72),
               xaxis=(1, 0, 0), yaxis=(0, 0, 1))
        for s in (1, -1):                                           # small side blades, angled down
            m.slab(f"SideFin{s}", [(-0.6, 0), (1.0, 0), (0.2, 0.3), (-0.9, 0.55)], 0.12, GOLD,
                   origin=(X(0.2), s * 0.66, T.z - 0.18), xaxis=(1, 0, 0), yaxis=(0, s * 0.8, -0.6))
        # flared muzzle, glowing bore, crown of spikes
        prism(m, "Flare", P(3.1), P(3.72), 0.66, 1.0, GOLD)
        prism(m, "Lip", P(3.66), P(3.9), 1.06, 1.02, MARBLE)
        prism(m, "Bore", P(3.4), P(3.94), 0.6, 0.6, GLOW, glow=True, chamfer=0.0)
        for k in range(8):
            a = 2 * math.pi * k / 8 + math.pi / 8; rd = Vector((0, math.cos(a), math.sin(a)))
            b = Vector(P(3.82)) + rd * 0.86
            m.spike(f"Crown{k}", b, b + Vector((0.72, 0, 0)) + rd * 0.42, 0.17, GOLD, sides=4)
        with m.bone("Halo", P(2.0)):
            ring(m, "Halo", P(2.0), (1, 0, 0), 1.3, 0.24, GLOW, n=16, glow=True, depth=0.2)
        with m.bone("Muzzle", P(3.94)): pass

    m.done(views=VIEWS, glow_color=GLOW)


BUILDERS = {1: build_wooden, 14: build_celestial}


def build_one(t):
    K = kit()
    out = os.path.join(OUT, f"{t:02d}_{ROSTER[t - 1]}", f"{ROSTER[t - 1]}Cannon")
    BUILDERS[t](K, out)


def sheet():
    """Cannons_overview.png: every built cannon's hero render in tier order (system python + Pillow)."""
    from PIL import Image, ImageDraw
    tiles = []
    for i, th in enumerate(ROSTER, 1):
        p = os.path.join(OUT, f"{i:02d}_{th}", f"{th}Cannon", "previews", f"{th}Cannon_hero.png")
        if os.path.exists(p): tiles.append((f"{i:02d} {th}", Image.open(p).convert("RGB").resize((400, 400))))
    if not tiles: return
    cols = min(4, len(tiles)); rows = (len(tiles) + cols - 1) // cols
    im = Image.new("RGB", (cols * 400, rows * 400), (255, 255, 255)); d = ImageDraw.Draw(im)
    for k, (lab, t) in enumerate(tiles):
        r, c = divmod(k, cols); im.paste(t, (c * 400, r * 400)); d.text((c * 400 + 8, r * 400 + 8), lab, fill=(0, 0, 0))
    im.save(os.path.join(OUT, "Cannons_overview.png")); print("SHEET", os.path.join(OUT, "Cannons_overview.png"))


if __name__ == "__main__":
    main()
