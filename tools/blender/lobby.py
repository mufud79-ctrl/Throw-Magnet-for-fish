"""Cannon Tame lobby props: leaderboards (one design, three colourways) and a gated ranch. TFFA style, static.

usage: /tmp/bpyenv/bin/python tools/blender/lobby.py [names ...] [--no-render]
names: LeaderboardGold LeaderboardPurple LeaderboardTeal Ranch
Writes models/CannonTame/Lobby/<Name>/. Shares the helpers and static export of shops.py.
Build space +X = the front (faces Roblox -Z after export), 1 unit = 1 stud, pivot at the ground centre.
"""
import os, sys, math, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import shops
from shops import prism, text, lantern, group, done_static
OUT = os.path.join(shops.ROOT, "models", "CannonTame", "Lobby")
VIEWS = [("hero", 35, 14, 50), ("front", 0, 6, 50), ("side", 90, 6, 50), ("back", 160, 18, 50)]


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


def star(m, name, c, size, col, glow=False):
    """Chunky 4-point star facing +X."""
    from mathutils import Vector
    c = Vector(c)
    m.box(name + "C", c, (0.16, size * 0.55, size * 0.55), col, rot=shops_Rx(math.pi / 4), studs=False, glow=glow)
    for k, d in enumerate(((0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))):
        m.spike(f"{name}{k}", c, c + Vector(d) * size, size * 0.32, col, glow=glow)


def shops_Rx(a):
    from mathutils import Matrix
    return Matrix.Rotation(a, 3, "X")


# ============================================================================== Leaderboard (one design, recoloured)
SCHEMES = {
    "Gold":   dict(frame=(255, 196, 46), frame_d=(214, 140, 24), accent=(40, 110, 255), screen=(22, 28, 58), glow=(255, 226, 130)),
    "Purple": dict(frame=(150, 84, 232), frame_d=(100, 52, 170), accent=(255, 110, 200), screen=(30, 18, 52), glow=(255, 150, 240)),
    "Teal":   dict(frame=(40, 192, 172), frame_d=(24, 132, 122), accent=(255, 150, 40), screen=(14, 40, 46), glow=(140, 255, 226)),
}


def build_leaderboard(K, out, scheme):
    from mathutils import Vector
    rgb = K.rgb; S = {k: rgb(*v) for k, v in SCHEMES[scheme].items()}
    FRAME, FRAME_D, ACC, SCREEN, GLOW = S["frame"], S["frame_d"], S["accent"], S["screen"], S["glow"]
    STONE, STONE_D, WHITE = rgb(186, 186, 192), rgb(136, 136, 144), rgb(250, 250, 252)
    GOLD, GOLD_D, SILVER, BRONZE = rgb(255, 204, 52), rgb(220, 150, 30), rgb(206, 214, 226), rgb(212, 130, 70)
    m = K.Model(f"Leaderboard{scheme}", out, stud=1.0, chamfer=0.12, jitter=0.05)
    ns = dict(studs=False)
    # plinth
    m.box("Plinth", (0, 0, 0.4), (3.0, 12.0, 0.8), STONE)
    m.box("PlinthStep", (1.9, 0, 0.2), (0.9, 10.0, 0.4), STONE_D)
    # pillars with caps
    for s in (1, -1):
        m.box(f"PillarBase{s}", (0, s * 5.2, 1.1), (1.9, 1.9, 0.6), FRAME_D)
        m.box(f"Pillar{s}", (0, s * 5.2, 5.6), (1.4, 1.4, 8.6), FRAME)
        m.box(f"PillarBand{s}", (0, s * 5.2, 4.0), (1.5, 1.5, 0.35), ACC, **ns)
        m.box(f"PillarCap{s}", (0, s * 5.2, 10.1), (1.8, 1.8, 0.5), FRAME_D)
        m.ball(f"PillarOrb{s}", (0, s * 5.2, 10.75), 0.5, ACC, segs=(8, 6))
    # board frame + screen (the screen is its own MeshPart for a SurfaceGui)
    m.box("Frame", (0, 0, 6.0), (0.8, 9.2, 7.8), FRAME)
    m.box("FrameBack", (-0.45, 0, 6.0), (0.12, 8.4, 7.0), ACC, **ns)
    with group(m, "Screen"):
        m.box("Screen", (0.44, 0, 5.8), (0.1, 7.6, 6.4), SCREEN, studs=False, chamfer=0.0)
    for k, (z, col) in enumerate(((8.4, GOLD), (7.5, SILVER), (6.6, BRONZE))):          # podium medals beside rows 1-3
        prism(m, f"Medal{k}", (0.4, -4.18, z), (0.58, -4.18, z), 0.3, 0.3, col, sides=10, chamfer=0.25)
    for y in [i * 0.95 - 3.8 for i in range(9)]:                                         # marquee bulbs
        m.ball(f"Bulb{y:.2f}", (0.48, y, 9.72), 0.13, GLOW, segs=(6, 4), glow=True)
    # header crest: banner plate, stars, trophy
    m.box("Crest", (0, 0, 10.75), (0.9, 7.2, 1.5), FRAME_D)
    m.box("Banner", (0.47, 0, 10.75), (0.06, 6.6, 1.0), ACC, **ns)
    for s in (1, -1):
        star(m, f"Star{s}", (0.6, s * 2.4, 10.75), 0.55, WHITE)
        star(m, f"StarS{s}", (0.6, s * 1.35, 10.95), 0.3, WHITE)
    c = Vector((0.1, 0, 11.5))
    m.box("TrophyBase", c + Vector((0, 0, 0.2)), (1.1, 1.4, 0.4), FRAME_D)
    prism(m, "TrophyStem", c + Vector((0, 0, 0.4)), c + Vector((0, 0, 0.9)), 0.18, 0.18, GOLD)
    prism(m, "TrophyCup", c + Vector((0, 0, 0.85)), c + Vector((0, 0, 2.0)), 0.42, 0.85, GOLD, sides=10)
    prism(m, "TrophyLip", c + Vector((0, 0, 1.95)), c + Vector((0, 0, 2.12)), 0.9, 0.9, GOLD_D, sides=10)
    for s in (1, -1):
        m.box(f"TrophyHandle{s}", c + Vector((0, s * 0.95, 1.5)), (0.18, 0.22, 0.7), GOLD, **ns)
        m.box(f"TrophyHandleT{s}", c + Vector((0, s * 0.82, 1.85)), (0.18, 0.4, 0.16), GOLD, **ns)
    star(m, "TrophyStar", c + Vector((0.5, 0, 1.4)), 0.32, WHITE)
    done_static(m, GLOW, VIEWS)


# ============================================================================== Ranch (open fenced pen with a gate)
def build_ranch(K, out):
    from mathutils import Vector
    rgb = K.rgb
    WOOD, WOOD_D, WOOD_DD = rgb(212, 150, 86), rgb(156, 98, 56), rgb(108, 66, 40)
    RED, CREAM, IVORY, IRON = rgb(200, 52, 44), rgb(250, 240, 222), rgb(248, 240, 220), rgb(72, 76, 92)
    DIRT, GRASS, HAY, HAY_D = rgb(176, 126, 80), rgb(96, 178, 70), rgb(240, 202, 84), rgb(196, 156, 52)
    WATER, LAMP = rgb(70, 160, 240), rgb(255, 204, 100)
    m = K.Model("Ranch", out, stud=1.0, chamfer=0.12, jitter=0.05)
    ns = dict(studs=False)
    L, W, gate = 28.0, 24.0, 4.2                 # pen length (x), width (y), half gate opening
    hx, hy = L / 2, W / 2
    # fence: posts every ~3.5 studs, two rails per side, gap in the front for the gate
    placed = set()
    def posts(a, b, n):
        a, b = Vector(a), Vector(b)
        for i in range(n + 1):
            p = a.lerp(b, i / n); key = (round(p.x, 2), round(p.y, 2))
            if key in placed: continue
            placed.add(key)
            m.box(f"Post{p.x:.1f}_{p.y:.1f}", (p.x, p.y, 2.1), (0.7, 0.7, 4.0), WOOD_D)
            m.box(f"PostCap{p.x:.1f}_{p.y:.1f}", (p.x, p.y, 4.2), (0.85, 0.85, 0.25), WOOD_DD, **ns)
    def rails(name, a, b):
        a, b = Vector(a), Vector(b); c = (a + b) / 2; d = b - a
        size = (abs(d.x) + 0.3, abs(d.y) + 0.3, 0.5)
        for z in (1.7, 3.2):
            m.box(f"{name}{z}", (c.x, c.y, z), (max(size[0], 0.3), max(size[1], 0.3), 0.5), WOOD)
    placed.update({(round(hx, 2), round(s_ * (gate + 0.6), 2)) for s_ in (1, -1)})      # gate posts are built below
    posts((-hx, -hy, 0), (hx, -hy, 0), 8); posts((-hx, hy, 0), (hx, hy, 0), 8)
    posts((-hx, -hy, 0), (-hx, hy, 0), 7)
    posts((hx, -hy, 0), (hx, -gate - 0.6, 0), 2); posts((hx, gate + 0.6, 0), (hx, hy, 0), 2)
    rails("RailL", (-hx, hy, 0), (hx, hy, 0)); rails("RailR", (-hx, -hy, 0), (hx, -hy, 0))
    rails("RailB", (-hx, -hy, 0), (-hx, hy, 0))
    rails("RailFL", (hx, gate + 0.6, 0), (hx, hy, 0)); rails("RailFR", (hx, -hy, 0), (hx, -gate - 0.6, 0))
    for s in (1, -1):                                     # gate posts: fence height, a bit chunkier
        m.box(f"GatePost{s}", (hx, s * (gate + 0.6), 2.25), (0.95, 0.95, 4.3), WOOD_DD)
        m.box(f"GatePostCap{s}", (hx, s * (gate + 0.6), 4.5), (1.15, 1.15, 0.3), WOOD_D, **ns)
    # gate doors (separate meshes so they can swing; hinges at the arch posts)
    for s, gname in ((1, "GateL"), (-1, "GateR")):
        with group(m, gname):
            y0, y1 = s * (gate - 0.05), s * 0.12          # hinge side -> middle
            yc, wy = (y0 + y1) / 2, abs(y1 - y0)
            for z in (1.0, 2.2, 3.4):
                m.box(f"{gname}Bar{z}", (hx, yc, z), (0.35, wy, 0.42), WOOD)
            for y in (y0 - s * 0.15, y1 + s * 0.15):
                m.box(f"{gname}Stile{y:.2f}", (hx, y, 2.2), (0.42, 0.42, 3.4), WOOD_D)
            d = Vector((0, y1 - y0, 2.4)); c = Vector((hx, yc, 2.2))
            m.box(f"{gname}Brace", c, (0.3, 0.38, d.length), WOOD_D, rot=d.to_track_quat("Z", "X").to_matrix(), **ns)
            for z in (1.0, 3.4):
                m.box(f"{gname}Hinge{z}", (hx + 0.1, y0, z), (0.5, 0.5, 0.2), IRON, **ns)
    done_static(m, None, [("hero", 30, 26, 35), ("front", 0, 10, 40), ("side", 90, 14, 40), ("top", 20, 70, 35)])


BUILDERS = {"LeaderboardGold": lambda K, o: build_leaderboard(K, o, "Gold"),
            "LeaderboardPurple": lambda K, o: build_leaderboard(K, o, "Purple"),
            "LeaderboardTeal": lambda K, o: build_leaderboard(K, o, "Teal"),
            "Ranch": build_ranch}


def build_one(name):
    K = shops.kit()
    BUILDERS[name](K, os.path.join(OUT, name))


if __name__ == "__main__":
    main()
