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


# ============================================================================== shared bits for the middle tiers
def spoke_wheel(m, name, c, r, t, rim, hub, spokes=8, tyre=None, studs=False):
    """Big spoked wheel in the XZ plane at centre c (axle along Y): faceted rim ring, block spokes, hub."""
    from mathutils import Vector
    c = Vector(c)
    ring(m, name + "Rim", c, (0, 1, 0), r - t * 0.5, t, rim, n=16, depth=t * 1.1)
    if tyre: ring(m, name + "Tyre", c, (0, 1, 0), r - t * 0.12, t * 0.35, tyre, n=16, depth=t * 1.25)
    for k in range(spokes):
        a = 2 * math.pi * k / spokes + math.pi / spokes
        d = Vector((math.cos(a), 0, math.sin(a)))
        m.seg(f"{name}Spoke{k}", c + d * 0.15, c + d * (r - t * 0.6), t * 0.55, t * 0.42, rim, studs=studs, chamfer=0.15)
    prism(m, name + "Hub", c - Vector((0, t * 0.9, 0)), c + Vector((0, t * 0.9, 0)), t * 1.25, t * 1.25, hub, chamfer=0.2)


def star(m, name, c, n, u, size, col, glow=True, points=4, r=None):
    """Flat star (4 or 8 points) in the plane spanned by u and n x u, facing n."""
    from mathutils import Vector
    c, n, u = Vector(c), Vector(n).normalized(), Vector(u).normalized(); v = n.cross(u)
    for k in range(points):
        a = 2 * math.pi * k / points
        d = u * math.cos(a) + v * math.sin(a)
        L = size if k % 2 == 0 or points == 4 else size * 0.6
        m.spike(f"{name}{k}", c, c + d * L, r or size * 0.28, col, sides=4, glow=glow)


def barrel_ctx(m, K, T, elev):
    """Enter the Barrel bone + its elevation frame (use: with barrel_ctx(...): ...)."""
    import contextlib
    @contextlib.contextmanager
    def cm():
        with m.bone("Barrel", T), m.frame(pivot=T, rot=K.Ry(-elev)): yield
    return cm()


# ============================================================================== tier 02: Iron (studded field gun)
def build_iron(K, out):
    from mathutils import Vector
    rgb = K.rgb
    GUN, GUN_D = rgb(70, 74, 90), rgb(48, 50, 62)
    RED, RED_D = rgb(200, 52, 42), rgb(150, 36, 32)
    BRASS, BORE, TYRE = rgb(236, 180, 66), rgb(24, 22, 26), rgb(46, 44, 48)
    m = K.Model("IronCannon", out, stud=0.28, chamfer=0.18, jitter=0.05)
    m.gait = {"recoil": 0.35}
    T = Vector((0.35, 0, 2.05))
    with m.bone("Body", (0, 0, 1.2)):
        for s in (1, -1):                                    # two big spoked field wheels
            spoke_wheel(m, f"W{s}", (0.3, s * 1.12, 1.18), 1.18, 0.24, RED_D, BRASS, spokes=10, tyre=TYRE)
        m.box("Axle", (0.3, 0, 1.18), (0.34, 2.3, 0.34), GUN_D, studs=False)
        for s in (1, -1):
            m.box(f"Cheek{s}", (0.25, s * 0.5, 1.6), (1.25, 0.26, 1.0), RED)
            m.box(f"Cap{s}", (T.x, s * 0.5, T.z + 0.05), (0.5, 0.32, 0.22), GUN_D, studs=False)
            m.seg(f"Trail{s}", (0.0, s * 0.48, 1.35), (-2.3, s * 0.2, 0.32), 0.3, 0.26, RED, d0=0.62, d1=0.42)
        m.box("TrailEnd", (-2.45, 0, 0.26), (0.6, 0.78, 0.5), RED_D)
        m.box("Spade", (-2.78, 0, 0.18), (0.16, 0.86, 0.36), GUN_D, studs=False)
        m.box("Transom", (-1.0, 0, 0.92), (0.36, 0.86, 0.3), RED_D)
        m.box("AmmoBox", (-1.2, 0, 1.18), (0.9, 0.62, 0.42), RED_D)
        m.box("AmmoLid", (-1.2, 0, 1.42), (0.96, 0.68, 0.1), BRASS, studs=False)
    with barrel_ctx(m, K, T, 0.2):
        X = lambda dx: T.x + dx
        kw = dict(chamfer=0.22)
        m.seg("Breech", (X(-1.75), 0, T.z), (X(-0.7), 0, T.z), 1.08, 1.14, GUN, **kw)
        m.seg("Chase", (X(-0.8), 0, T.z), (X(2.05), 0, T.z), 1.0, 0.76, GUN, **kw)
        m.seg("Swell", (X(1.95), 0, T.z), (X(2.45), 0, T.z), 0.76, 1.02, GUN, **kw)
        for nm, x0, x1, w in (("Ring0", -1.68, -1.45, 1.14), ("Ring1", -0.78, -0.56, 1.04), ("Ring2", 0.95, 1.12, 0.88)):
            r = octa(w) + 0.06; prism(m, nm, (X(x0), 0, T.z), (X(x1), 0, T.z), r, r, BRASS, chamfer=0.2)
        r = octa(1.02) + 0.07; prism(m, "Lip", (X(2.3), 0, T.z), (X(2.52), 0, T.z), r, r, BRASS, chamfer=0.2)
        prism(m, "Bore", (X(2.3), 0, T.z), (X(2.54), 0, T.z), 0.36, 0.36, BORE, chamfer=0.0)
        prism(m, "Cascabel", (X(-2.05), 0, T.z), (X(-1.72), 0, T.z), 0.18, 0.22, GUN_D)
        m.ball("Knob", (X(-2.15), 0, T.z), 0.25, BRASS, segs=(8, 6))
        prism(m, "Trunnion", (T.x, -0.7, T.z), (T.x, 0.7, T.z), 0.17, 0.17, GUN_D)
        for s in (1, -1):                                     # dolphin handles on top
            m.seg(f"Handle{s}", (X(-0.25), s * 0.22, T.z + 0.5), (X(0.25), s * 0.22, T.z + 0.5), 0.12, 0.12, BRASS, d0=0.22, d1=0.22, studs=False)
        with m.bone("Muzzle", (X(2.54), 0, T.z)): pass
    m.done(views=VIEWS)


# ============================================================================== tier 13: Galaxy (faceted, violet glow)
def build_galaxy(K, out):
    from mathutils import Vector
    rgb = K.rgb
    SPACE, SPACE_L = rgb(44, 26, 104), rgb(108, 60, 200)
    LILAC, VOID = rgb(196, 160, 255), rgb(16, 10, 30)
    GL = rgb(214, 120, 255)
    m = K.Model("GalaxyCannon", out, stud=0.4, chamfer=0.16, faceted=True)
    m.gait = {"float": True, "recoil": 0.45}
    T = Vector((0.15, 0, 3.4))
    ns = dict(studs=False)
    with m.bone("Body", (0, 0, 1.2)):
        # hovering planet with a tilted Saturn ring and three moons
        m.ball("Planet", (0, 0, 1.4), 1.3, SPACE, segs=(12, 8))
        m.ball("PlanetCap", (0, 0, 1.78), (1.15, 1.15, 0.85), SPACE_L, segs=(12, 6))
        ring(m, "Saturn", (0, 0, 1.35), (0.35, 0.15, 1), 2.1, 0.48, LILAC, n=20, depth=0.1)
        ring(m, "SaturnGlow", (0, 0, 1.35), (0.35, 0.15, 1), 1.7, 0.12, GL, n=20, depth=0.12, glow=True)
        for k, (a, r_) in enumerate(((0.4, 0.2), (2.5, 0.16), (4.3, 0.24))):
            m.ball(f"Moon{k}", (2.1 * math.cos(a), 2.1 * math.sin(a), 1.35 - 0.7 * math.cos(a)), r_ * 1.3, rgb(236, 228, 255), segs=(6, 4))
        prism(m, "Column", (0, 0, 2.4), (0, 0, 2.85), 0.5, 0.42, SPACE)
        prism(m, "Collar", (0, 0, 2.75), (0, 0, 2.95), 0.78, 0.78, LILAC)
        for s in (1, -1):                                       # crescent-moon yoke arms
            m.seg(f"Arm{s}", (T.x - 0.2, s * 0.55, 2.85), (T.x, s * 1.0, T.z), 0.34, 0.32, LILAC, d0=0.7, d1=0.55, **ns)
            m.seg(f"ArmTip{s}", (T.x, s * 1.0, T.z), (T.x + 0.1, s * 0.85, T.z + 0.75), 0.3, 0.12, LILAC, d0=0.5, d1=0.18, **ns)
            star(m, f"CapStar{s}", (T.x, s * 1.2, T.z), (0, s, 0), (0, 0, 1), 0.36, GL)
        for k, p in enumerate(((1.4, 1.4, 2.6), (-1.5, -1.2, 2.3), (-0.6, 1.6, 3.4), (1.0, -1.7, 3.0))):
            star(m, f"Twinkle{k}", p, (0, 0, 1) if k % 2 else (1, 0, 0), (1, 0, 1) if k % 2 else (0, 1, 1), 0.26, GL)
    with barrel_ctx(m, K, T, 0.2):
        X = lambda dx: T.x + dx
        P = lambda dx, dz=0: (X(dx), 0, T.z + dz)
        G = (rgb(26, 14, 64), SPACE, SPACE_L)
        prism(m, "Breech", P(-2.1), P(-0.85), 0.95, 0.9, SPACE, grad=G)
        prism(m, "Chase", P(-1.0), P(3.0), 0.8, 0.62, SPACE, grad=G)
        for nm, x0, x1, r in (("Band0", -0.95, -0.65, 0.94), ("Band1", 0.9, 1.12, 0.78), ("Band2", 2.1, 2.3, 0.72)):
            prism(m, nm, P(x0), P(x1), r, r, LILAC)
        prism(m, "Trunnion", (T.x, -0.95, T.z), (T.x, 0.95, T.z), 0.24, 0.24, LILAC)
        for k, a in enumerate((math.pi / 2, math.pi / 2 + 2.2, math.pi / 2 - 2.2)):     # swept rocket fins
            rd = Vector((0, math.cos(a), math.sin(a)))
            m.slab(f"Fin{k}", [(-0.9, 0), (0.7, 0), (-0.35, 0.8), (-1.25, 0.95)], 0.14, LILAC,
                   origin=Vector(P(-1.3)) + rd * 0.8, xaxis=(1, 0, 0), yaxis=rd)
        star(m, "BackStar", P(-2.15), (-1, 0, 0), (0, 0, 1), 0.95, GL, points=8, r=0.22)
        for k, (dx, a) in enumerate(((-0.1, 1.0), (0.5, -0.4), (1.6, 2.2), (2.6, 0.3), (-1.6, 2.9))):
            rd = Vector((0, math.cos(a), math.sin(a)))
            star(m, f"Dust{k}", Vector(P(dx)) + rd * 0.74, rd, (1, 0, 0), 0.16, GL)
        # black-hole muzzle: dark flare, void core, spinning accretion disc
        prism(m, "Flare", P(2.9), P(3.55), 0.66, 1.05, VOID)
        prism(m, "Lip", P(3.5), P(3.72), 1.1, 1.06, LILAC)
        prism(m, "Void", P(3.4), P(3.73), 0.74, 0.74, VOID, chamfer=0.0)
        prism(m, "Core", P(3.2), P(3.8), 0.48, 0.48, GL, glow=True, chamfer=0.0)
        with m.bone("Halo", P(3.65)):
            ring(m, "Accretion", P(3.7), (1, 0, 0), 1.3, 0.24, GL, n=16, glow=True, depth=0.08)
            ring(m, "Accretion2", P(3.62), (1, 0, 0), 1.6, 0.08, LILAC, n=16, depth=0.06)
        with m.bone("Muzzle", P(3.76)): pass
    m.done(views=VIEWS, glow_color=GL)


# ============================================================================== tier 03: Stone (studded idol on rollers)
def build_stone(K, out):
    from mathutils import Vector
    rgb = K.rgb
    STONE, STONE_D, STONE_L = rgb(156, 158, 166), rgb(112, 114, 124), rgb(196, 196, 200)
    MOSS, MOSS_D, BORE = rgb(104, 182, 62), rgb(72, 140, 46), rgb(30, 26, 30)
    m = K.Model("StoneCannon", out, stud=0.28, chamfer=0.18, jitter=0.07)
    m.gait = {"recoil": 0.3}
    T = Vector((0.25, 0, 2.0))
    with m.bone("Body", (0, 0, 1.0)):
        for x in (-1.15, 0.0, 1.15):                                  # stone rollers
            prism(m, f"Roller{x}", (x, -0.95, 0.33), (x, 0.95, 0.33), 0.34, 0.34, STONE_D, chamfer=0.2)
        m.box("Slab", (0, 0, 0.84), (3.3, 1.65, 0.44), STONE)
        m.box("SlabMoss", (-0.6, 0.15, 1.08), (1.5, 1.2, 0.1), MOSS, studs="top")
        for s in (1, -1):
            m.box(f"Pillar{s}", (T.x, s * 0.64, 1.47), (0.86, 0.38, 1.0), STONE_D)
            m.box(f"PillarCap{s}", (T.x, s * 0.64, T.z + 0.02), (0.98, 0.46, 0.18), STONE_L, studs=False)
            m.box(f"MossDrip{s}", (T.x - 0.2, s * 0.84, 1.75), (0.36, 0.06, 0.4), MOSS_D, studs=False)
        for k, p in enumerate(((-1.25, 0.35, 1.32), (-1.25, -0.32, 1.32), (-1.25, 0.02, 1.72))):     # ammo pile
            m.ball(f"Ammo{k}", p, 0.27, STONE_D, segs=(8, 6))
    with barrel_ctx(m, K, T, 0.12):
        X = lambda dx: T.x + dx
        m.box("Breech", (X(-1.45), 0, T.z), (1.0, 1.28, 1.28), STONE_D)
        m.seg("Chase", (X(-1.0), 0, T.z), (X(1.4), 0, T.z), 1.14, 1.0, STONE, chamfer=0.16)
        for x in (-0.55, 0.65):
            m.box(f"Band{x}", (X(x), 0, T.z), (0.24, 1.26, 1.2), STONE_D, studs=False)
        m.box("Head", (X(1.82), 0, T.z + 0.05), (0.95, 1.55, 1.55), STONE)
        m.box("HeadMoss", (X(1.78), 0, T.z + 0.86), (1.0, 1.6, 0.14), MOSS, studs="top")
        for s in (1, -1): m.box(f"Drip{s}", (X(1.6), s * 0.76, T.z + 0.62), (0.3, 0.12, 0.42), MOSS_D, studs=False)
        m.box("Mouth", (X(2.29), 0, T.z - 0.33), (0.1, 0.84, 0.44), BORE, studs=False)
        m.box("Lip", (X(2.31), 0, T.z - 0.6), (0.14, 0.96, 0.12), STONE_L, studs=False)
        for k in range(4):                                         # chunky stone teeth
            m.box(f"Tooth{k}", (X(2.33), -0.3 + k * 0.2, T.z - 0.17), (0.08, 0.14, 0.14), STONE_L, studs=False)
        m.box("Nose", (X(2.36), 0, T.z + 0.08), (0.22, 0.3, 0.3), STONE_D, studs=False, top=(0.7, 0.8))
        m.eyes((X(2.3), 0.38, T.z + 0.4), facing=(1, 0, 0), size=(0.44, 0.34), pupil=0.62, look=(0.2, -0.1), angry=0.35,
               brow_col=STONE_D, white=rgb(236, 232, 214), depth=0.12)
        prism(m, "Trunnion", (T.x, -0.86, T.z), (T.x, 0.86, T.z), 0.2, 0.2, STONE_D)
        with m.bone("Muzzle", (X(2.34), 0, T.z - 0.33)): pass
    m.done(views=VIEWS)


# ============================================================================== tier 12: Dragon (faceted, fire glow)
def build_dragon(K, out):
    """Design ideas from the user reference (12_Dragon/DragonCannon_reference.webp), built in the cannon family's language:
    octagonal banded barrel = dragon body (cream belly plate, big spine spikes, curled tail), a tapered wedge head with
    the jaws wide open around a big fireball bore, swept-back horns, narrow glowing eyes; black/gold stepped carriage."""
    from mathutils import Vector
    rgb, Ry = K.rgb, K.Ry
    RED, RED_D = rgb(188, 22, 32), rgb(130, 12, 24)        # the zoo RedDragon palette
    BELLY, HORN = rgb(214, 166, 206), K.HORN
    BLACK2, GOLD = rgb(30, 28, 36), rgb(236, 186, 70)
    GLD = rgb(255, 92, 12)
    m = K.Model("DragonCannon", out, stud=0.4, chamfer=0.16, faceted=True)
    m.gait = {"recoil": 0.4}
    T = Vector((-0.1, 0, 2.35))

    def wedge(name, x0, x1, back, front, col, ch=0.14):
        """Block from x0 to x1 whose cross-section changes from back=(w, z0, z1) to front=(w, z0, z1)."""
        (wb, b0, b1), (wf, f0, f1) = back, front
        C = [(x0, -wb / 2, b0), (x1, -wf / 2, f0), (x1, wf / 2, f0), (x0, wb / 2, b0),
             (x0, -wb / 2, b1), (x1, -wf / 2, f1), (x1, wf / 2, f1), (x0, wb / 2, b1)]
        m.hexa(name, C, col, chamfer=ch)

    with m.bone("Body", (0, 0, 1.0)):
        # stepped black carriage with gold trim (gold plate behind a slightly smaller black plate)
        m.box("Bed", (-0.45, 0, 0.82), (3.3, 1.5, 0.5), BLACK2)
        for s in (1, -1):
            for nm, (x0, x1, z0, z1) in (("F", (-0.65, 0.75, 0.62, 2.2)), ("M", (-1.55, -0.55, 0.62, 1.78)),
                                         ("B", (-2.15, -1.45, 0.62, 1.42))):
                cx, cz, L, H = (x0 + x1) / 2, (z0 + z1) / 2, x1 - x0, z1 - z0
                m.box(f"Trim{nm}{s}", (cx, s * 0.86, cz), (L + 0.12, 0.2, H + 0.12), GOLD)
                m.box(f"Cheek{nm}{s}", (cx, s * 0.9, cz), (L - 0.04, 0.2, H - 0.04), BLACK2)
            m.box(f"Cap{s}", (T.x, s * 0.9, T.z + 0.02), (0.6, 0.34, 0.3), GOLD)
            m.slab(f"Emblem{s}", [(0, 0), (-0.32, 0.46), (-0.8, 0.6), (-0.68, 0.25), (-0.98, 0.14), (-0.72, -0.08),
                                   (-0.9, -0.28), (-0.44, -0.17)], 0.08, RED, origin=(-0.62, s * 1.02, 1.1), xaxis=(1.5, 0, 0), yaxis=(0, 0, 1))
        # chunky black wheels, gold hub, slim gold spokes
        for x in (-1.6, 0.55):
            m.box(f"Axle{x}", (x, 0, 0.58), (0.3, 2.4, 0.3), BLACK2)
            for s in (1, -1):
                c = Vector((x, s * 1.2, 0.58))
                prism(m, f"Wheel{x}{s}", c - Vector((0, 0.19, 0)), c + Vector((0, 0.19, 0)), 0.58, 0.58, BLACK2, sides=12, chamfer=0.22)
                prism(m, f"Hub{x}{s}", c, c + Vector((0, s * 0.25, 0)), 0.2, 0.17, BLACK2)
                prism(m, f"HubCap{x}{s}", c + Vector((0, s * 0.22, 0)), c + Vector((0, s * 0.29, 0)), 0.09, 0.09, GOLD)
                for k in range(10):
                    a = 2 * math.pi * k / 10; d = Vector((math.cos(a), 0, math.sin(a)))
                    m.spike(f"Spoke{x}{s}{k}", c + d * 0.48 + Vector((0, s * 0.19, 0)), c + d * 0.28 + Vector((0, s * 0.19, 0)), 0.06, GOLD, flat=0.5)

    with barrel_ctx(m, K, T, 0.08):
        X = lambda dx: T.x + dx
        P = lambda dx, dz=0, y=0: (X(dx), y, T.z + dz)
        R0 = 0.92
        # body barrel + belly plate + bands + big spine spikes
        prism(m, "BodyRear", P(-2.15), P(-0.4), 0.8, R0, RED)
        prism(m, "BodyFront", P(-0.5), P(1.55), R0, 0.88, RED)
        wedge("Belly", X(-2.0), X(1.5), (0.9, T.z - 0.95, T.z - 0.3), (0.9, T.z - 0.92, T.z - 0.3), BELLY)
        m.hexa("BellyTop", [(X(-2.0), -0.5, T.z - 0.62), (X(1.5), -0.5, T.z - 0.62), (X(1.5), 0.5, T.z - 0.62), (X(-2.0), 0.5, T.z - 0.62),
                            (X(-2.0), -0.86, T.z - 0.3), (X(1.5), -0.86, T.z - 0.3), (X(1.5), 0.86, T.z - 0.3), (X(-2.0), 0.86, T.z - 0.3)],
               BELLY, chamfer=0.1)
        for x in (-1.25, 0.2):
            r = R0 + 0.06; prism(m, f"Band{x}", P(x - 0.12), P(x + 0.12), r, r, RED_D)
        prism(m, "Collar", P(-2.22), P(-2.02), 0.86, 0.86, GOLD)
        for i, (x, h) in enumerate(((1.0, 0.56), (0.5, 0.56), (0.0, 0.54), (-0.5, 0.5), (-1.0, 0.46), (-1.5, 0.42), (-1.95, 0.36))):
            b = Vector(P(x, R0 - 0.08))
            m.spike(f"Spine{i}", b, b + Vector((-0.22, 0, h)), 0.2, HORN, flat=0.35)
        # tail curling up behind the breech, cream underside, spike tip
        m.chain("Tail", [P(-2.0, -0.15), P(-2.75, 0.0), P(-3.2, 0.55), P(-3.15, 1.3)], [1.05, 0.76, 0.52, 0.3], RED, chamfer=0.2)
        m.spike("TailSpike", P(-2.85, 0.38), P(-3.2, 0.85), 0.16, HORN, flat=0.35)
        m.seg("TailBelly", P(-2.25, -0.5), P(-2.95, -0.4), 0.62, 0.42, BELLY, chamfer=0.2)
        m.spike("TailTip", P(-3.15, 1.25), P(-3.0, 1.75), 0.18, HORN, flat=0.4)

        # ---- head: the zoo RedDragon's head (examples/dragon.py), jaw opened around a fireball bore.
        # Coordinates below are the RedDragon's own; the outer frame drops that head onto the front of the barrel.
        HP = Vector((1.5, 0, 9.2))                     # RedDragon head pivot (after its own scale/move frame)
        k = 0.8
        with m.frame(pivot=HP, scale=k, move=Vector(P(1.4, 0.55 - 0.875 * k)) - HP), \
             m.frame(pivot=(1.5, 0, 8.2), scale=1.25, move=(0, 0, 1.0)):
            m.box("Head", (2.0, 0, 8.9), (2.0, 2.0, 1.5), RED, top=(0.75, 0.8))
            m.box("Snout", (3.3, 0, 8.7), (1.7, 1.4, 0.85), RED, top=(0.75, 0.8), bot=(1, 0.85))
            m.box("Roof", (3.0, 0, 8.28), (1.7, 1.15, 0.1), K.MOUTH)
            m.box("Throat", (2.2, 0, 8.0), (0.8, 1.3, 1.0), K.MOUTH)
            for s in (1, -1):
                for j, x in enumerate((2.5, 3.0, 3.5, 3.95)):
                    m.spike(f"Tooth{s}{j}", (x, s * 0.55, 8.3), (x, s * 0.53, 7.9 - 0.12 * (j == 3)), 0.13, K.TOOTH, flat=0.4)
                m.spike(f"Horn{s}", (1.6, s * 0.6, 9.5), (0.9, s * 1.2, 11.0), 0.32, HORN, sides=5)
                for j in range(4):                                     # frill crown around the face
                    m.spike(f"Frill{s}{j}", (1.6 - j * 0.15, s * 0.9, 9.4 - j * 0.4), (1.4 - j * 0.2, s * (1.55 - j * 0.08), 9.6 - j * 0.5), 0.26, RED)
                m.box(f"Nostril{s}", (4.15, s * 0.3, 8.9), (0.1, 0.2, 0.12), RED_D, chamfer=0.05)
            m.spike("Crest", (2.2, 0, 9.55), (1.7, 0, 10.4), 0.28, RED)
            m.eyes((2.85, 0.6, 9.25), facing=(1, 0.8, 0.2), size=(0.55, 0.32), pupil=0.75, look=(0.5, 0), angry=0.45,
                   white=rgb(255, 214, 60), brow_col=RED_D, brow_h=0.5, brow_up=0.75, depth=0.14)
            with m.frame(pivot=(2.0, 0, 8.2), rot=Ry(0.5)):            # jaw dropped open
                m.box("Jaw", (2.9, 0, 7.95), (1.9, 1.25, 0.45), RED)
                m.box("JawFloor", (2.9, 0, 8.2), (1.6, 1.0, 0.08), K.MOUTH)
                m.box("Chin", (2.8, 0, 7.75), (1.6, 0.9, 0.1), BELLY)
                for s in (1, -1):
                    for j, x in enumerate((2.6, 3.1, 3.6)):
                        m.spike(f"LTooth{s}{j}", (x, s * 0.5, 8.15), (x, s * 0.48, 8.5), 0.12, K.TOOTH, flat=0.4)
            m.ball("Fireball", (2.75, 0, 8.1), 0.62, GLD, segs=(10, 8), glow=True)
            with m.bone("Muzzle", (3.3, 0, 8.1)): pass
        prism(m, "Trunnion", (T.x, -0.92, T.z), (T.x, 0.92, T.z), 0.2, 0.2, BLACK2)
    m.done(views=VIEWS + [("ref", 56, 12, 90)], glow_color=GLD)


# ============================================================================== tier 04: Bamboo (studded bundle launcher)
def build_bamboo(K, out):
    from mathutils import Vector
    rgb = K.rgb
    dk = K.dk
    BAMB, BAMB_D, NODE = rgb(160, 210, 76), rgb(108, 160, 50), rgb(124, 176, 54)
    ROPE, MAT, LEAF = rgb(220, 184, 120), rgb(206, 164, 98), rgb(64, 184, 64)
    INNER, BORE, COCO = rgb(244, 230, 172), rgb(40, 32, 26), rgb(116, 74, 44)
    m = K.Model("BambooCannon", out, stud=0.27, chamfer=0.18, jitter=0.05)
    m.gait = {"recoil": 0.3}
    T = Vector((0.3, 0, 2.15))
    with m.bone("Body", (0, 0, 1.0)):
        for x in (-1.1, 1.1):
            for y in (-0.72, 0.72):
                prism(m, f"Leg{x}{y}", (x, y, 0.0), (x, y, 0.62), 0.16, 0.16, BAMB_D, chamfer=0.15)
            m.seg(f"Cross{x}", (x, -0.95, 0.5), (x, 0.95, 0.5), 0.24, 0.24, BAMB_D, chamfer=0.22, studs=False)
        m.box("Mat", (0, 0, 0.72), (2.9, 1.85, 0.26), MAT)
        for k in range(5):
            m.box(f"Weave{k}", (-1.15 + k * 0.58, 0, 0.86), (0.2, 1.88, 0.04), dk(MAT, 0.85), studs=False, chamfer=0.1)
        for s in (1, -1):                                        # A-frame poles lashed at the trunnion
            m.seg(f"PoleA{s}", (T.x - 0.75, s * 0.74, 0.8), (T.x + 0.15, s * 0.74, T.z + 0.4), 0.2, 0.18, BAMB_D, chamfer=0.22, studs=False)
            m.seg(f"PoleB{s}", (T.x + 0.75, s * 0.74, 0.8), (T.x - 0.15, s * 0.74, T.z + 0.4), 0.2, 0.18, BAMB_D, chamfer=0.22, studs=False)
            m.box(f"Lash{s}", (T.x, s * 0.74, T.z + 0.05), (0.38, 0.32, 0.4), ROPE, studs=False)
        for k, p in enumerate(((-1.0, 0.45, 1.08), (-1.0, -0.25, 1.08), (-1.15, 0.12, 1.45))):
            m.ball(f"Coconut{k}", p, 0.24, COCO, segs=(8, 6))
    with barrel_ctx(m, K, T, 0.15):
        X = lambda dx: T.x + dx
        P = lambda dx, dz=0, y=0: (X(dx), y, T.z + dz)
        kw = dict(chamfer=0.22)
        m.seg("Tube", P(-1.85), P(2.2), 1.0, 1.0, BAMB, **kw)
        for x in (-1.88, -0.3, 1.05, 2.12):
            r = octa(1.0) + 0.05; prism(m, f"Node{x}", P(x - 0.08), P(x + 0.08), r, r, NODE, chamfer=0.2)
        prism(m, "Inner", P(2.18), P(2.25), octa(0.82), octa(0.82), INNER, chamfer=0.0)
        prism(m, "Bore", P(2.2), P(2.27), 0.34, 0.34, BORE, chamfer=0.0)
        for s in (1, -1):                                        # two side tubes in the bundle
            m.seg(f"Side{s}", P(-1.2, -0.2, s * 0.64), P(1.45, -0.2, s * 0.64), 0.44, 0.44, BAMB_D, **kw)
            prism(m, f"SideIn{s}", P(1.43, -0.2, s * 0.64), P(1.5, -0.2, s * 0.64), octa(0.34), octa(0.34), INNER, chamfer=0.0)
            prism(m, f"SideBore{s}", P(1.45, -0.2, s * 0.64), P(1.52, -0.2, s * 0.64), 0.12, 0.12, BORE, chamfer=0.0)
        for x in (-0.85, 0.62):
            m.box(f"Rope{x}", P(x, -0.06), (0.24, 1.78, 1.18), ROPE, studs=False)
        for s in (1, -1):                                        # leaves sprouting from the front node
            m.slab(f"Leaf{s}", [(0, 0), (0.2, 0.35), (0.04, 1.05), (-0.18, 0.4)], 0.06, LEAF, origin=P(1.05, 0.48, s * 0.15),
                   xaxis=(1, 0, 0), yaxis=(-0.45, s * 0.55, 0.7))
        m.slab("Leaf0", [(0, 0), (0.16, 0.3), (0.03, 0.8), (-0.15, 0.32)], 0.06, dk(LEAF, 0.85), origin=P(-0.3, 0.48, 0.1),
               xaxis=(1, 0, 0), yaxis=(-0.7, 0.1, 0.7))
        m.seg("Trunnion", (T.x, -0.9, T.z), (T.x, 0.9, T.z), 0.3, 0.3, BAMB_D, chamfer=0.22, studs=False)
        with m.bone("Muzzle", P(2.27)): pass
    m.done(views=VIEWS)


# ============================================================================== tier 11: Cyber (faceted railgun, pink glow)
def build_cyber(K, out):
    from mathutils import Vector
    rgb = K.rgb
    DARK, PANEL, WHITE2 = rgb(36, 38, 52), rgb(84, 90, 110), rgb(232, 236, 246)
    GLC = rgb(255, 60, 180)
    m = K.Model("CyberCannon", out, stud=0.4, chamfer=0.14, faceted=True)
    m.gait = {"recoil": 0.45}
    T = Vector((0.0, 0, 2.75))
    with m.bone("Body", (0, 0, 1.3)):
        for k in range(3):                                       # three mech legs
            a = math.radians(60 + 120 * k); c, s_ = math.cos(a), math.sin(a)
            hip, knee, foot = Vector((0.5 * c, 0.5 * s_, 1.3)), Vector((1.45 * c, 1.45 * s_, 1.25)), Vector((1.85 * c, 1.85 * s_, 0.18))
            m.seg(f"Thigh{k}", hip, knee, 0.36, 0.3, PANEL, chamfer=0.2)
            m.seg(f"Shin{k}", knee, foot, 0.3, 0.22, DARK, chamfer=0.2)
            m.box(f"Knee{k}", knee, (0.36, 0.36, 0.36), WHITE2, rot=K.Rz(a))
            m.box(f"KneeLight{k}", knee + Vector((0, 0, 0.2)), (0.16, 0.16, 0.06), GLC, rot=K.Rz(a), glow=True)
            m.box(f"Foot{k}", foot - Vector((0, 0, 0.08)), (0.6, 0.42, 0.2), DARK, rot=K.Rz(a), top=(0.7, 0.8))
        prism(m, "Hub", (0, 0, 0.95), (0, 0, 1.6), 0.75, 0.85, DARK, sides=6)
        ring(m, "HubLight", (0, 0, 1.3), (0, 0, 1), 0.86, 0.08, GLC, n=6, glow=True, depth=0.1)
        prism(m, "Turret", (0, 0, 1.55), (0, 0, 1.95), 1.0, 0.92, PANEL, sides=6)
        prism(m, "TurretTop", (0, 0, 1.9), (0, 0, 2.05), 0.8, 0.8, WHITE2, sides=6)
        for s in (1, -1):
            m.box(f"Yoke{s}", (T.x - 0.1, s * 0.86, 2.4), (1.0, 0.24, 1.0), PANEL, top=(0.7, 1), shift=(0.12, 0))
            m.box(f"YokeLight{s}", (T.x - 0.1, s * 0.99, 2.35), (0.6, 0.04, 0.1), GLC, glow=True, chamfer=0.0)
    with barrel_ctx(m, K, T, 0.15):
        X = lambda dx: T.x + dx
        P = lambda dx, dz=0, y=0: (X(dx), y, T.z + dz)
        prism(m, "Core", P(-1.3), P(2.5), 0.42, 0.42, DARK, sides=6)
        m.box("Breech", P(-1.45), (1.25, 1.3, 1.05), PANEL, top=(0.8, 0.9))
        m.box("BreechTop", P(-1.45, 0.56), (0.9, 0.9, 0.12), WHITE2)
        for k in range(3): m.box(f"Vent{k}", P(-1.75 + k * 0.3, 0.64), (0.12, 0.6, 0.06), DARK, chamfer=0.1)
        m.box("BackScreen", P(-2.09), (0.06, 0.8, 0.5), GLC, glow=True, chamfer=0.0)
        for sz in (1, -1):                                       # the two rails
            m.box(f"Rail{sz}", P(1.3, sz * 0.56), (3.9, 0.56, 0.26), DARK)
            m.box(f"RailEdge{sz}", P(1.2, sz * 0.7), (3.4, 0.6, 0.06), WHITE2)
            m.box(f"RailGlow{sz}", P(1.45, sz * 0.4), (3.3, 0.2, 0.06), GLC, glow=True, chamfer=0.0)
            m.spike(f"RailTip{sz}", P(3.25, sz * 0.56), P(3.75, sz * 0.48), 0.2, DARK, flat=0.6)
        for x in (0.25, 0.85, 1.45, 2.05):
            ring(m, f"Coil{x}", P(x), (1, 0, 0), 0.5, 0.1, GLC, n=6, glow=True, depth=0.12)
        m.ball("Charge", P(2.95), 0.26, GLC, segs=(6, 4), glow=True)
        for s in (1, -1):                                        # swept side fins + side screen
            m.slab(f"Fin{s}", [(-0.8, 0), (0.6, 0), (-0.2, 0.55), (-1.15, 0.6)], 0.1, WHITE2, origin=P(-1.0, 0, s * 0.64),
                   xaxis=(1, 0, 0), yaxis=(0, s, -0.25))
            m.box(f"SidePanel{s}", P(-1.4, 0, s * 0.66), (0.7, 0.04, 0.36), GLC, glow=True, chamfer=0.0)
        prism(m, "Trunnion", (T.x, -0.8, T.z), (T.x, 0.8, T.z), 0.22, 0.22, WHITE2, sides=6)
        with m.bone("Muzzle", P(3.1)): pass
    m.done(views=VIEWS, glow_color=GLC)


def gear(m, K, name, c, r, t, col, hub, teeth=12, axis_y=True):
    """Cog wheel in the XZ plane (axle along Y): faceted disc, square teeth round the rim, hub."""
    from mathutils import Vector
    c = Vector(c); h = Vector((0, t / 2, 0))
    prism(m, name + "Disc", c - h, c + h, r * 0.84, r * 0.84, col, sides=16, chamfer=0.18)
    for k in range(teeth):
        a = 2 * math.pi * k / teeth
        m.box(f"{name}T{k}", c + Vector((math.cos(a), 0, math.sin(a))) * r * 0.9, (r * 0.26, t * 0.92, r * 0.24), col,
              rot=K.Ry(-a), studs=False, chamfer=0.12)
    prism(m, name + "Hub", c - h * 1.5, c + h * 1.5, r * 0.3, r * 0.3, hub, chamfer=0.2)
    prism(m, name + "Inner", c - h * 1.05, c + h * 1.05, r * 0.6, r * 0.6, hub, sides=16, chamfer=0.1)


# ============================================================================== tier 05: Copper (studded steam cannon)
def build_copper(K, out):
    from mathutils import Vector
    rgb = K.rgb
    COP, COP_D, COP_L = rgb(224, 124, 64), rgb(162, 80, 42), rgb(246, 166, 100)
    PATINA, BRASS = rgb(70, 196, 164), rgb(242, 192, 76)
    IRON, IRON_D, BORE = rgb(84, 78, 82), rgb(54, 50, 54), rgb(30, 24, 26)
    FACE, NEEDLE, VALVE = rgb(248, 242, 228), rgb(210, 40, 36), rgb(206, 52, 42)
    m = K.Model("CopperCannon", out, stud=0.28, chamfer=0.18, jitter=0.05)
    m.gait = {"recoil": 0.35}
    T = Vector((0.45, 0, 2.45))
    ns = dict(studs=False)
    with m.bone("Body", (0, 0, 1.1)):
        m.box("Bed", (-0.6, 0, 0.8), (4.4, 1.4, 0.44), IRON)
        m.box("BedTrim", (-0.6, 0, 1.06), (4.5, 1.5, 0.1), BRASS, **ns)
        m.box("Axle", (0.55, 0, 1.05), (0.32, 2.4, 0.32), IRON_D, **ns)
        m.box("RearAxle", (-2.2, 0, 0.38), (0.26, 1.7, 0.26), IRON_D, **ns)
        for s in (1, -1):
            gear(m, K, f"Gear{s}", (0.55, s * 1.1, 1.05), 1.05, 0.3, COP_D, BRASS, teeth=12)
            prism(m, f"Roller{s}", (-2.2, s * 0.62, 0.38), (-2.2, s * 0.98, 0.38), 0.38, 0.38, IRON_D, chamfer=0.2)
            prism(m, f"RollerHub{s}", (-2.2, s * 0.95, 0.38), (-2.2, s * 1.04, 0.38), 0.15, 0.13, BRASS, chamfer=0.25)
            m.box(f"Cheek{s}", (T.x - 0.05, s * 0.66, 1.8), (1.35, 0.28, 1.25), COP, top=(0.72, 1))
            m.box(f"Strap{s}", (T.x, s * 0.66, T.z + 0.04), (0.5, 0.34, 0.22), BRASS, **ns)
            for x, z in ((T.x - 0.5, 1.4), (T.x + 0.4, 1.4), (T.x - 0.2, 2.0)):
                m.box(f"Rivet{s}{x}{z}", (x, s * 0.81, z), (0.13, 0.06, 0.13), BRASS, chamfer=0.1, **ns)
        # steam boiler at the back: copper drum, brass bands, smokestack, pressure gauge and valve wheel
        B = Vector((-2.4, 0, 0))
        prism(m, "Boiler", B + Vector((0, 0, 1.08)), B + Vector((0, 0, 2.35)), 0.62, 0.62, COP, sides=10)
        for z in (1.25, 2.12):
            prism(m, f"BoilerBand{z}", B + Vector((0, 0, z)), B + Vector((0, 0, z + 0.14)), 0.67, 0.67, BRASS, sides=10)
        prism(m, "PatinaBand", B + Vector((0, 0, 1.6)), B + Vector((0, 0, 1.72)), 0.65, 0.65, PATINA, sides=10)
        prism(m, "Dome", B + Vector((0, 0, 2.33)), B + Vector((0, 0, 2.62)), 0.62, 0.38, COP_D, sides=10)
        prism(m, "Stack", B + Vector((0, 0, 2.55)), B + Vector((0, 0, 3.35)), 0.17, 0.21, IRON_D)
        prism(m, "StackLip", B + Vector((0, 0, 3.3)), B + Vector((0, 0, 3.48)), 0.3, 0.3, BRASS)
        for s in (1, -1):
            g = B + Vector((0, s * 0.6, 1.92))
            prism(m, f"Gauge{s}", g, g + Vector((0, s * 0.14, 0)), 0.26, 0.26, BRASS, sides=12)
            prism(m, f"GaugeFace{s}", g + Vector((0, s * 0.1, 0)), g + Vector((0, s * 0.17, 0)), 0.2, 0.2, FACE, sides=12, chamfer=0.0)
            m.box(f"Needle{s}", g + Vector((0.04, s * 0.18, 0.05)), (0.04, 0.03, 0.2), NEEDLE, rot=K.Ry(0.6), chamfer=0.0, **ns)
        v = B + Vector((-0.66, 0, 1.45))
        ring(m, "Valve", v, (1, 0, 0), 0.22, 0.07, VALVE, n=8, depth=0.07)
        m.box("ValveBarA", v, (0.05, 0.42, 0.06), VALVE, chamfer=0.0, **ns)
        m.box("ValveBarB", v, (0.05, 0.06, 0.42), VALVE, chamfer=0.0, **ns)
        m.seg("Pipe", B + Vector((0.55, 0.0, 1.95)), (-1.25, 0, 1.12), 0.2, 0.2, BRASS, chamfer=0.22, **ns)
    with barrel_ctx(m, K, T, 0.14):
        X = lambda dx: T.x + dx
        P = lambda dx, dz=0, y=0: (X(dx), y, T.z + dz)
        kw = dict(chamfer=0.22)
        m.seg("Breech", P(-1.9), P(-0.8), 1.14, 1.2, COP, **kw)
        m.seg("Chase", P(-0.9), P(2.0), 1.06, 0.84, COP, **kw)
        m.seg("Bell", P(1.9), P(2.6), 0.84, 1.24, COP_L, **kw)
        for nm, x0, x1, w in (("Ring0", -1.86, -1.62, 1.2), ("Ring1", -0.86, -0.62, 1.1), ("Ring2", 0.82, 1.02, 0.96)):
            r = octa(w) + 0.07; prism(m, nm, P(x0), P(x1), r, r, BRASS, chamfer=0.2)
        r = octa(1.02) + 0.04; prism(m, "Patina", P(0.05), P(0.3), r, r, PATINA, chamfer=0.2)
        r = octa(1.24) + 0.07; prism(m, "Lip", P(2.5), P(2.72), r, r, BRASS, chamfer=0.2)
        prism(m, "Bore", P(2.5), P(2.74), 0.44, 0.44, BORE, chamfer=0.0)
        prism(m, "Cascabel", P(-2.2), P(-1.88), 0.2, 0.24, COP_D)
        m.ball("Knob", P(-2.3), 0.26, BRASS, segs=(8, 6))
        prism(m, "Trunnion", (T.x, -0.95, T.z), (T.x, 0.95, T.z), 0.18, 0.18, IRON_D)
        for k, x in enumerate((-1.5, -1.12)):                       # twin steam vents with valve caps
            prism(m, f"Vent{k}", P(x, 0.5), P(x, 0.98), 0.11, 0.11, BRASS)
            prism(m, f"VentCap{k}", P(x, 0.95), P(x, 1.06), 0.19, 0.19, VALVE)
        for k, x in enumerate((-0.35, 0.45, 1.4)):                  # rivet row along the top
            m.box(f"TopRivet{k}", P(x, 0.47 - 0.05 * k), (0.14, 0.14, 0.08), BRASS, chamfer=0.1, **ns)
        with m.bone("Muzzle", P(2.74)): pass
    m.done(views=VIEWS)


# ============================================================================== tier 10: Toxic (faceted sludge launcher, lime glow)
def build_toxic(K, out):
    from mathutils import Vector
    rgb, Ry = K.rgb, K.Ry
    HAZ, BLK = rgb(252, 206, 36), rgb(34, 36, 40)
    GUN, GUN_L = rgb(66, 74, 70), rgb(110, 120, 110)
    DRUM = rgb(62, 150, 52)
    GL = rgb(70, 255, 40)
    m = K.Model("ToxicCannon", out, stud=0.4, chamfer=0.14, faceted=True)
    m.gait = {"recoil": 0.42}
    T = Vector((0.2, 0, 2.75))
    ns = dict(studs=False)
    with m.bone("Body", (0, 0, 1.2)):
        for s in (1, -1):                                         # tank treads
            m.box(f"Track{s}", (0, s * 1.08, 0.46), (3.7, 0.64, 0.92), BLK, bot=(0.8, 1))
            for k, x in enumerate((-1.25, -0.42, 0.42, 1.25)):
                prism(m, f"Wheel{s}{k}", (x, s * 1.36, 0.46), (x, s * 1.46, 0.46), 0.3, 0.27, GUN_L)
                prism(m, f"WheelHub{s}{k}", (x, s * 1.44, 0.46), (x, s * 1.5, 0.46), 0.11, 0.1, HAZ)
            for k in range(8):
                m.box(f"Tread{s}{k}", (-1.6 + k * 0.46, s * 1.08, 0.93), (0.14, 0.66, 0.06), GUN, chamfer=0.1)
        m.box("Deck", (0, 0, 1.08), (3.3, 2.0, 0.4), GUN)
        for s in (1, -1):                                         # hazard stripes down both deck sides
            m.box(f"Hazard{s}", (0, s * 1.0, 1.08), (3.2, 0.06, 0.3), HAZ, chamfer=0.0)
            for k in range(7):
                m.box(f"HazStripe{s}{k}", (-1.35 + k * 0.45, s * 1.03, 1.08), (0.13, 0.04, 0.33), BLK, rot=Ry(0.6), chamfer=0.0)
        prism(m, "Turret", (0, 0, 1.28), (0, 0, 1.68), 1.0, 0.9, GUN_L)
        ring(m, "TurretGlow", (0, 0, 1.48), (0, 0, 1), 0.98, 0.06, GL, n=8, glow=True, depth=0.08)
        for s in (1, -1):
            m.box(f"Yoke{s}", (T.x - 0.1, s * 0.72, 2.2), (0.95, 0.24, 1.1), HAZ, top=(0.7, 1))
            for k in (-1, 1):
                m.box(f"YokeStripe{s}{k}", (T.x - 0.1 + k * 0.22, s * 0.85, 2.05), (0.12, 0.03, 0.6), BLK, rot=Ry(0.6), chamfer=0.0)
        for k, (x, y) in enumerate(((1.15, 0.6), (1.15, -0.6), (-1.2, 0.55))):   # leaking waste drums
            z0, z1 = 1.28, 1.96 if k < 2 else 2.0
            prism(m, f"Drum{k}", (x, y, z0), (x, y, z1), 0.36, 0.36, DRUM, sides=10)
            for z in (z0 + 0.14, z1 - 0.2):
                prism(m, f"DrumRib{k}{z}", (x, y, z), (x, y, z + 0.07), 0.39, 0.39, HAZ, sides=10, chamfer=0.0)
            prism(m, f"Goo{k}", (x, y, z1 - 0.04), (x, y, z1 + 0.05), 0.28, 0.28, GL, sides=10, glow=True, chamfer=0.0)
            d = Vector((x, y, 0)) + Vector((0.36 if x > 0 else -0.36, 0, z1 - 0.02))
            m.spike(f"Drip{k}", d, d - Vector((0, 0, 0.45)), 0.08, GL, glow=True)
        m.ball("Puddle", (1.6, 0.6, 0.02), (0.5, 0.36, 0.04), GL, segs=(8, 3), glow=True)
    with barrel_ctx(m, K, T, 0.17):
        X = lambda dx: T.x + dx
        P = lambda dx, dz=0, y=0: (X(dx), y, T.z + dz)
        prism(m, "Core", P(-1.6), P(2.4), 0.52, 0.46, GUN)
        m.box("Breech", P(-1.5), (1.2, 1.25, 1.15), GUN_L, top=(0.85, 0.9))
        m.box("BackPlate", P(-2.12), (0.06, 0.8, 0.6), HAZ, chamfer=0.0)
        m.box("BackStripe", P(-2.16), (0.04, 0.12, 0.7), BLK, rot=K.Rx(0.6), chamfer=0.0)
        # glowing sludge canister on the breech: glass cylinder, black caps, cage bars, bubbles
        c = Vector(P(-1.45))
        prism(m, "TankBase", c + Vector((0, 0, 0.52)), c + Vector((0, 0, 0.7)), 0.5, 0.5, BLK, sides=8)
        prism(m, "Tank", c + Vector((0, 0, 0.66)), c + Vector((0, 0, 1.46)), 0.42, 0.42, GL, sides=8, glow=True, chamfer=0.0)
        prism(m, "TankCap", c + Vector((0, 0, 1.42)), c + Vector((0, 0, 1.62)), 0.5, 0.44, BLK, sides=8)
        prism(m, "CapValve", c + Vector((0, 0, 1.6)), c + Vector((0, 0, 1.74)), 0.16, 0.16, HAZ)
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            m.box(f"Cage{k}", c + Vector((0.46 * math.cos(a), 0.46 * math.sin(a), 1.06)), (0.08, 0.08, 0.82), BLK, chamfer=0.1)
        m.ball("Bubble0", c + Vector((0.1, 0.12, 1.98)), 0.11, GL, segs=(6, 4), glow=True)
        m.ball("Bubble1", c + Vector((-0.1, -0.08, 2.28)), 0.07, GL, segs=(6, 4), glow=True)
        m.seg("Feed", c + Vector((0.3, 0, 1.0)), P(-0.35, 0.42), 0.2, 0.16, GL, glow=True, chamfer=0.2)
        for nm, x0, x1, r in (("Collar0", -0.8, -0.56, 0.62), ("Collar1", 0.95, 1.17, 0.58)):
            prism(m, nm, P(x0), P(x1), r, r, HAZ)
        for x in (0.2, 1.75):
            ring(m, f"Seam{x}", P(x), (1, 0, 0), 0.5, 0.08, GL, n=8, glow=True, depth=0.12)
        for s in (1, -1):                                        # swept hazard fins
            m.slab(f"Fin{s}", [(-0.8, 0), (0.6, 0), (-0.2, 0.5), (-1.1, 0.55)], 0.1, HAZ, origin=P(-0.3, 0, s * 0.46),
                   xaxis=(1, 0, 0), yaxis=(0, s, -0.2))
        # nozzle muzzle full of sludge, dripping
        prism(m, "Nozzle", P(2.3), P(2.9), 0.52, 0.84, BLK)
        prism(m, "Lip", P(2.85), P(3.05), 0.9, 0.9, HAZ)
        prism(m, "Sludge", P(2.7), P(3.07), 0.62, 0.62, GL, glow=True, chamfer=0.0)
        for k, (y, L) in enumerate(((0.38, 0.5), (-0.32, 0.36), (0.02, 0.66))):
            b = Vector(P(2.97, -0.66 if abs(y) < 0.1 else -0.55, y))
            m.spike(f"MDrip{k}", b, b - Vector((0, 0, L)), 0.09, GL, glow=True)
        prism(m, "Trunnion", (T.x, -0.95, T.z), (T.x, 0.95, T.z), 0.22, 0.22, GUN_L)
        with m.bone("Muzzle", P(3.07)): pass
    m.done(views=VIEWS, glow_color=GL)


# ============================================================================== tier 06: Candy (studded sweets cannon)
def build_candy(K, out):
    from mathutils import Vector
    rgb = K.rgb
    PINK, PINK_L, CREAM = rgb(255, 118, 170), rgb(255, 186, 214), rgb(252, 246, 240)
    CHOC, CHOC_D, DOUGH = rgb(124, 72, 44), rgb(88, 50, 32), rgb(232, 170, 98)
    CHERRY, STEM, MINT, LEMON, SKY = rgb(222, 30, 52), rgb(96, 150, 50), rgb(80, 214, 160), rgb(255, 222, 70), rgb(96, 170, 255)
    BORE = rgb(70, 30, 40)
    SPR = (LEMON, SKY, MINT, CREAM, CHERRY)
    m = K.Model("CandyCannon", out, stud=0.27, chamfer=0.18, jitter=0.05)
    m.gait = {"recoil": 0.35}
    T = Vector((0.4, 0, 2.3))
    ns = dict(studs=False)
    with m.bone("Body", (0, 0, 1.0)):
        m.box("Bar", (0, 0, 0.95), (3.3, 1.5, 0.44), CHOC)            # chocolate-bar bed
        for k in range(5):
            m.box(f"BarGroove{k}", (-1.32 + k * 0.66, 0, 1.18), (0.07, 1.52, 0.05), CHOC_D, chamfer=0.0, **ns)
        for x in (-1.05, 1.05):                                       # frosted donut wheels with sprinkles
            m.box(f"Axle{x}", (x, 0, 0.55), (0.3, 2.0, 0.3), CHOC_D, **ns)
            for s in (1, -1):
                c = Vector((x, s * 0.98, 0.55))
                ring(m, f"Donut{x}{s}", c, (0, 1, 0), 0.36, 0.36, DOUGH, n=12, depth=0.34)
                ring(m, f"Frost{x}{s}", c + Vector((0, s * 0.15, 0)), (0, 1, 0), 0.36, 0.3, PINK, n=12, depth=0.1)
                for k in range(6):
                    a = 2 * math.pi * k / 6 + 0.3 * s
                    m.box(f"Spr{x}{s}{k}", c + Vector((0.36 * math.cos(a), s * 0.21, 0.36 * math.sin(a))), (0.14, 0.04, 0.05),
                          SPR[k % 5], rot=K.Ry(a * 1.7), chamfer=0.0, **ns)
        for s in (1, -1):                                             # chocolate-bar cheeks with raised squares
            m.box(f"Cheek{s}", (T.x - 0.05, s * 0.64, 1.75), (1.4, 0.28, 1.2), CHOC, top=(0.72, 1))
            for i, j in ((0, 0), (1, 0), (0, 1), (1, 1)):
                m.box(f"Square{s}{i}{j}", (T.x - 0.32 + 0.6 * i - 0.12 * j, s * 0.79, 1.42 + 0.48 * j), (0.4, 0.05, 0.38),
                      CHOC_D, chamfer=0.25, **ns)
            m.box(f"Strap{s}", (T.x, s * 0.64, T.z + 0.04), (0.5, 0.34, 0.22), PINK_L, **ns)
        for s, (c0, c1) in ((1, (PINK, CREAM)), (-1, (SKY, LEMON))):  # two lollipops at the back
            b = Vector((-1.5, s * 0.92, 1.1)); top = Vector((-1.5, s * 0.92, 2.55))
            prism(m, f"Stick{s}", b, top - Vector((0, 0, 0.3)), 0.07, 0.07, CREAM, chamfer=0.1)
            h = Vector((0, 0.08, 0))
            prism(m, f"Pop{s}", top - h, top + h, 0.5, 0.5, c1, sides=12, chamfer=0.3)
            ring(m, f"PopSwirl{s}", top, (0, 1, 0), 0.28, 0.14, c0, n=12, depth=0.2)
            prism(m, f"PopCore{s}", top - h * 1.3, top + h * 1.3, 0.1, 0.1, c0, chamfer=0.2)
    with barrel_ctx(m, K, T, 0.14):
        X = lambda dx: T.x + dx
        P = lambda dx, dz=0, y=0: (X(dx), y, T.z + dz)
        kw = dict(chamfer=0.24)
        m.seg("Breech", P(-1.9), P(-0.8), 1.12, 1.18, PINK, **kw)
        m.seg("Chase", P(-0.9), P(2.1), 1.04, 0.86, PINK, **kw)
        m.seg("Swell", P(2.0), P(2.55), 0.86, 1.16, PINK, **kw)
        for k, (x0, w) in enumerate(((-1.75, 1.18), (-1.2, 1.17), (-0.55, 1.08), (0.15, 1.0), (0.85, 0.96), (1.55, 0.9))):
            r = octa(w) + 0.05; prism(m, f"Stripe{k}", P(x0), P(x0 + 0.24), r, r, CREAM, chamfer=0.2)
        r = octa(1.16) + 0.08
        prism(m, "Frosting", P(2.38), P(2.68), r, r, CREAM, chamfer=0.25)
        prism(m, "Bore", P(2.5), P(2.7), 0.42, 0.42, BORE, chamfer=0.0)
        for k, (a, L) in enumerate(((-1.9, 0.26), (-1.25, 0.36), (-0.4, 0.22), (0.5, 0.32), (1.3, 0.24), (2.0, 0.34), (2.7, 0.2))):
            d = Vector((0, math.cos(a), math.sin(a)))
            if d.z > 0.35: continue
            b = Vector(P(2.53)) + d * (r * 0.92)
            m.seg(f"Drip{k}", b + Vector((0, 0, 0.1)), b - Vector((0, 0, L)) + d * 0.04, 0.3, 0.24, CREAM, d0=0.22, d1=0.2, chamfer=0.45, **ns)
        for k in range(10):                                           # sprinkles on the frosting front
            a = 2 * math.pi * k / 10 + 0.2; d = Vector((0, math.cos(a), math.sin(a)))
            m.box(f"FSpr{k}", Vector(P(2.69)) + d * 0.66, (0.04, 0.16, 0.05), SPR[k % 5], rot=K.Rx(a + 0.8), chamfer=0.0, **ns)
        m.ball("Cherry", P(2.42, 0.86), 0.24, CHERRY, segs=(8, 6))
        m.seg("CherryStem", P(2.42, 1.05), P(2.2, 1.45), 0.06, 0.05, STEM, chamfer=0.1, **ns)
        prism(m, "Cascabel", P(-2.2), P(-1.88), 0.2, 0.24, PINK_L)
        m.box("Gumdrop", P(-2.38), (0.46, 0.46, 0.42), MINT, rot=K.Ry(math.pi / 2), top=(0.5, 0.5))
        prism(m, "Trunnion", (T.x, -0.92, T.z), (T.x, 0.92, T.z), 0.18, 0.18, PINK_L)
        with m.bone("Muzzle", P(2.7)): pass
    m.done(views=VIEWS)


# ============================================================================== tier 09: Lava (faceted volcano, magma glow)
def build_lava(K, out):
    from mathutils import Vector
    rgb, Ry, Rz, lerp = K.rgb, K.Ry, K.Rz, K.lerp
    BAS, BAS_D, BAS_L = rgb(58, 46, 50), rgb(34, 26, 32), rgb(96, 74, 70)
    HOT = rgb(170, 52, 28)
    GL = rgb(255, 84, 0)
    m = K.Model("LavaCannon", out, stud=0.4, chamfer=0.16, faceted=True)
    m.gait = {"recoil": 0.45}
    T = Vector((0.25, 0, 3.0))
    ns = dict(studs=False)
    with m.bone("Body", (0, 0, 1.2)):
        # mini volcano: basalt cone, crater lip, lava rivers down the sides, magma pool and rocks round the foot
        prism(m, "Cone", (0, 0, 0.0), (0, 0, 1.9), 2.05, 1.05, BAS, sides=8, grad=(BAS_D, BAS, BAS_L))
        prism(m, "Crater", (0, 0, 1.82), (0, 0, 2.12), 1.18, 1.26, BAS_L, sides=8)
        prism(m, "Magma", (0, 0, 2.0), (0, 0, 2.16), 0.95, 0.95, GL, sides=8, glow=True, chamfer=0.0)
        for k, a in enumerate((0.45, 1.75, 3.4, 4.6, 5.6)):
            def pt(t, wob=0.0):
                r = lerp(1.0, 1.98, t) + 0.05; aa = a + wob
                return Vector((r * math.cos(aa), r * math.sin(aa), lerp(1.9, 0.05, t)))
            pts = [pt(0), pt(0.4, 0.12), pt(0.75, -0.05), pt(1.0, 0.1)]
            for i in range(3):
                m.seg(f"Flow{k}{i}", pts[i], pts[i + 1], 0.34 - 0.03 * i + 0.06 * i, 0.3 + 0.06 * i, GL, d0=0.1, d1=0.1, glow=True, chamfer=0.2)
        for k, (a, t, sz) in enumerate(((1.1, 0.45, 0.62), (2.55, 0.62, 0.55), (4.0, 0.35, 0.58), (5.15, 0.6, 0.5), (0.0, 0.7, 0.48))):
            r = lerp(1.0, 1.98, t) * 0.97
            m.box(f"Ledge{k}", (r * math.cos(a), r * math.sin(a), lerp(1.9, 0.05, t)), (sz, sz * 0.9, sz * 0.55), BAS_L,
                  rot=Rz(a) @ Ry(0.45), top=(0.75, 0.8))
        ring(m, "Pool", (0, 0, 0.03), (0, 0, 1), 2.15, 0.42, GL, n=8, glow=True, depth=0.06)
        for k, (a, sz) in enumerate(((0.9, 0.55), (2.6, 0.48), (3.9, 0.6), (5.1, 0.45), (6.0, 0.4))):
            m.box(f"Rock{k}", (2.25 * math.cos(a), 2.25 * math.sin(a), sz * 0.35), (sz, sz * 0.85, sz * 0.75), BAS_D,
                  rot=Rz(a * 2.3) @ Ry(0.2))
        for s in (1, -1):                                             # obsidian yoke pillars
            m.box(f"Pillar{s}", (T.x - 0.05, s * 0.78, 2.5), (0.85, 0.3, 1.1), BAS_D, top=(0.7, 1))
            m.spike(f"PillarSpike{s}", (T.x - 0.05, s * 0.86, 3.0), (T.x - 0.25, s * 1.0, 3.75), 0.2, BAS_D)
            m.box(f"PillarCrack{s}", (T.x - 0.05, s * 0.94, 2.45), (0.06, 0.04, 0.6), GL, rot=K.Rx(0) @ Ry(0.35), glow=True, chamfer=0.0)
        for k, p in enumerate(((0.9, 0.6, 3.1), (-0.8, -0.5, 2.85), (-0.3, 0.9, 3.5))):
            m.ball(f"Ember{k}", p, 0.08 + 0.03 * (k % 2), GL, segs=(6, 4), glow=True)
    with barrel_ctx(m, K, T, 0.18):
        X = lambda dx: T.x + dx
        P = lambda dx, dz=0, y=0: (X(dx), y, T.z + dz)
        G = (BAS_D, BAS, HOT)
        prism(m, "Breech", P(-2.0), P(-0.8), 0.95, 0.9, BAS, grad=G)
        prism(m, "Chase", P(-0.95), P(2.6), 0.82, 0.64, BAS, grad=G)
        for nm, x0, x1, r in (("Band0", -0.95, -0.66, 0.95), ("Band1", 0.75, 0.98, 0.8), ("Band2", 1.9, 2.1, 0.74)):
            prism(m, nm, P(x0), P(x1), r, r, BAS_L)
        for x in (-1.55, 0.2, 1.45):
            ring(m, f"Seam{x}", P(x), (1, 0, 0), 0.82 - 0.06 * (x > 0) - 0.04 * (x > 1), 0.08, GL, n=8, glow=True, depth=0.1)
        for k, (x, a, s) in enumerate(((-0.4, 0.5, 1), (0.55, -0.6, 1), (-0.2, -0.4, -1), (1.2, 0.45, -1), (-1.3, 0.3, 1), (-1.4, -0.5, -1))):
            fl = (0.88 if x < -0.8 else 0.72 - 0.035 * x) * math.cos(math.pi / 8)
            m.box(f"Crack{k}", P(x, 0.0, s * fl), (0.62, 0.05, 0.08), GL, rot=Ry(a), glow=True, chamfer=0.0)
        for k, x in enumerate((-1.5, -0.6, 0.35)):                     # swept obsidian spines on top
            b = Vector(P(x, 0.7 - 0.05 * k))
            m.spike(f"Spine{k}", b - Vector((0.25, 0, 0)), b + Vector((-0.55, 0, 0.7 - 0.12 * k)), 0.24, BAS_D, flat=0.55)
        for k in range(3):                                             # glowing vents on the breech
            m.box(f"Vent{k}", P(-1.75 + 0.3 * k, 0.86), (0.12, 0.7, 0.05), GL, glow=True, chamfer=0.0)
        prism(m, "BackCore", P(-2.25), P(-1.95), 0.55, 0.7, BAS_D)
        prism(m, "BackGlow", P(-2.3), P(-2.2), 0.36, 0.36, GL, glow=True, chamfer=0.0)
        # crater muzzle: rough flare, magma bore, obsidian teeth round the lip
        prism(m, "Flare", P(2.5), P(3.15), 0.66, 1.05, BAS_D)
        prism(m, "Lip", P(3.08), P(3.3), 1.1, 1.0, BAS)
        prism(m, "Bore", P(2.95), P(3.32), 0.68, 0.68, GL, glow=True, chamfer=0.0)
        for k in range(8):
            a = 2 * math.pi * k / 8; rd = Vector((0, math.cos(a), math.sin(a)))
            b = Vector(P(3.2)) + rd * 0.95
            m.spike(f"Tooth{k}", b, b + Vector((0.5, 0, 0)) + rd * 0.2, 0.16, BAS_D)
        m.ball("Fireblob", P(3.45, 0.2, 0.15), 0.12, GL, segs=(6, 4), glow=True)
        prism(m, "Trunnion", (T.x, -1.0, T.z), (T.x, 1.0, T.z), 0.22, 0.22, BAS_L)
        with m.bone("Muzzle", P(3.32)): pass
    m.done(views=VIEWS, glow_color=GL)


BUILDERS = {1: build_wooden, 2: build_iron, 3: build_stone, 4: build_bamboo, 5: build_copper, 6: build_candy, 9: build_lava, 10: build_toxic,
            11: build_cyber, 12: build_dragon, 13: build_galaxy, 14: build_celestial}


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
