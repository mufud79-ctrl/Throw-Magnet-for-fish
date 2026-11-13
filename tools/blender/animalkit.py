"""Archetype builders for Cannon Tame animals (blocky Roblox-part style, T-Rex rules):
studs on big parts, smooth face details, readable silhouettes, cute or angry eyes."""
import math
import numpy as np
from mathutils import Vector, Matrix
from blocky import *
from fishkit import V

def Rz(a): return Matrix.Rotation(a, 3, "Z")
def Ry(a): return Matrix.Rotation(a, 3, "Y")
def Rx(a): return Matrix.Rotation(a, 3, "X")
def dk(c, k=0.7): return tuple(x * k for x in c)
def lt(c, k=0.4): return tuple(x + (1 - x) * k for x in c)
def lerp(a, b, t): return a + (b - a) * t

# ------------------------------------------------------------------ shared face / parts
def eyes(f, hc, hl, hw, hh, angry=False, iris=YELLOW, brow=None, size=1.0, fwd=0.22, up=0.18):
    e = min(hh, hl) * 0.3 * size
    for sy in (1, -1):
        p = hc + V(hl * fwd, sy * (hw / 2 + 0.03), hh * up)
        if angry:
            f.block(f"Socket{sy}", p, (e * 1.5, 0.05, e * 1.15), BLACK, studs=False)
            f.block(f"Iris{sy}", p + V(0, sy * 0.02, 0), (e * 1.05, 0.05, e * 0.85), iris, studs=False)
            f.block(f"Pupil{sy}", p + V(e * 0.06, sy * 0.045, 0), (e * 0.28, 0.04, e * 0.8), BLACK, studs=False)
            f.block(f"Brow{sy}", p + V(0, -sy * 0.05, e * 0.8), (e * 2.0, e * 0.6 + 0.12, e * 0.45), brow or BLACK, Ry(0.34), studs=False)
        else:
            f.block(f"Eye{sy}", p, (e * 0.8, 0.05, e * 1.05), BLACK, studs=False)
            f.block(f"Glint{sy}", p + V(-e * 0.12, sy * 0.035, e * 0.22), (e * 0.26, 0.04, e * 0.26), WHITE, studs=False)

def ears(f, kind, hc, hl, hw, hh, col):
    if not kind: return
    for sy in (1, -1):
        b = hc + V(-hl * 0.15, sy * hw * 0.32, hh / 2)
        if kind == "point": f.block(f"Ear{sy}", b + V(0, 0, hh * 0.25), (hh * 0.3, 0.16, hh * 0.55), col, Rx(-sy * 0.25), studs=False)
        elif kind == "round": f.block(f"Ear{sy}", b + V(0, 0, hh * 0.12), (hh * 0.36, 0.16, hh * 0.34), col, studs=False)
        elif kind == "long": f.block(f"Ear{sy}", b + V(-0.05, 0, hh * 0.6), (hh * 0.3, 0.16, hh * 1.2), col, Rx(-sy * 0.15), studs=False)
        elif kind == "floppy": f.block(f"Ear{sy}", hc + V(-hl * 0.1, sy * (hw / 2 + 0.08), hh * 0.05), (hh * 0.35, 0.14, hh * 0.65), col, Rx(sy * 0.3), studs=False)
        elif kind == "big": f.block(f"Ear{sy}", hc + V(-hl * 0.25, sy * (hw / 2 + 0.1), 0), (hl * 0.65, 0.16, hh * 1.15), col, Rz(sy * 0.35), studs=False)
        elif kind == "tiny": f.block(f"Ear{sy}", b + V(0, 0, hh * 0.08), (hh * 0.22, 0.14, hh * 0.22), col, studs=False)
        elif kind == "fennec": f.block(f"Ear{sy}", b + V(0, sy * 0.15, hh * 0.5), (hh * 0.45, 0.16, hh * 1.0), col, Rx(-sy * 0.35), studs=False)

def tail(f, kind, L, H, z0, col, tip=None):
    if not kind: return
    b = V(-L / 2, 0, z0 + H * 0.2)
    if kind == "short": f.block("Tail", b + V(-0.15, 0, 0), (0.45, 0.35, 0.35), col, studs=False)
    elif kind == "long":
        for k, (l, s) in enumerate(((1.1, 0.5), (1.0, 0.38), (0.9, 0.28))): f.block(f"Tail{k}", b + V(-0.45 - 0.9 * k, 0, -0.25 * k), (l, s, s), col, Ry(0.3), studs=False)
    elif kind == "bushy":
        f.block("Tail", b + V(-0.6, 0, 0.3), (1.6, 0.9, 0.9), col, Ry(0.5)); f.block("TailTip", b + V(-1.35, 0, 0.75), (0.6, 0.85, 0.85), tip or WHITE, Ry(0.5), studs=False)
    elif kind == "up":
        f.block("Tail", b + V(-0.4, 0, 0.7), (0.9, 1.0, 1.8), col, Ry(-0.25)); f.block("TailTop", b + V(-0.05, 0, 1.75), (0.9, 1.0, 0.9), col, Ry(0.5))
    elif kind == "tuft":
        f.block("Tail", b + V(-0.55, 0, -0.45), (0.2, 0.2, 1.4), col, Ry(-0.7), studs=False); f.block("Tuft", b + V(-1.05, 0, -0.95), (0.4, 0.4, 0.5), tip or dk(col), studs=False)
    elif kind == "curly": f.block("Tail", b + V(-0.12, 0, 0.1), (0.3, 0.2, 0.3), col, Ry(0.6), studs=False)
    elif kind == "flat": f.block("Tail", b + V(-0.8, 0, -0.5), (1.6, 1.0, 0.18), tip or dk(col), studs=False)
    elif kind == "thick":
        for k, (l, s) in enumerate(((1.6, 1.1), (1.5, 0.8), (1.4, 0.55), (1.0, 0.35))): f.block(f"Tail{k}", b + V(-0.7 - 1.35 * k, 0, -0.35 - 0.12 * k), (l, s, s * 0.85), col)
    elif kind == "dragon":
        for k, (l, s) in enumerate(((1.6, 1.0), (1.5, 0.75), (1.4, 0.55), (1.2, 0.38))): f.block(f"Tail{k}", b + V(-0.7 - 1.35 * k, 0, -0.1 - 0.25 * k), (l, s, s), col, Ry(0.15))
        f.wedge("TailSpade", b + V(-6.2, 0, -1.1), (0.8, 0.3, 0.9), tip or dk(col), Rz(math.pi))

def pattern(f, kind, L, W, H, lh, z0, col, n=5, seed=1):
    if not kind: return
    rng = np.random.default_rng(seed)
    if kind == "stripes":
        for k in range(n): f.block(f"Stripe{k}", V(-L / 2 + L * (k + 0.7) / (n + 0.4), 0, z0 + H * 0.12), (0.28, W + 0.06, H * 0.8), col, studs=False)
    elif kind == "spots":
        for k in range(n * 2):
            x = rng.uniform(-L / 2 + 0.4, L / 2 - 0.4); z = rng.uniform(z0 - H * 0.2, z0 + H * 0.35); sy = 1 if k % 2 else -1
            f.block(f"Spot{k}", V(x, sy * (W / 2 + 0.02), z), (rng.uniform(0.35, 0.6), 0.06, rng.uniform(0.3, 0.5)), col, studs=False)
        for k in range(n): f.block(f"SpotT{k}", V(rng.uniform(-L / 2 + 0.4, L / 2 - 0.4), rng.uniform(-W / 3, W / 3), z0 + H / 2 + 0.02), (0.5, 0.45, 0.06), col, studs=False)
    elif kind == "patches":
        for k in range(4):
            sy = 1 if k % 2 else -1; f.block(f"Patch{k}", V(rng.uniform(-L / 3, L / 3), sy * (W / 2 + 0.02), z0 + rng.uniform(-H * 0.1, H * 0.2)), (L * 0.32, 0.06, H * 0.55), col, studs=False)
        f.block("PatchTop", V(rng.uniform(-L / 4, L / 4), 0, z0 + H / 2 + 0.02), (L * 0.35, W * 0.6, 0.06), col, studs=False)
    elif kind == "saddle": f.block("Saddle", V(0, 0, z0 + H / 2 + 0.02), (L * 0.7, W * 0.75, 0.08), col, studs=False)
    elif kind == "mask": pass

def quad(f, P):
    L, W, H = P["body"]; lh, lw = P["legs"]; C1 = P["c1"]; C2 = P.get("c2", dk(C1)); BEL = P.get("belly"); sprawl = P.get("sprawl", 0.0)
    z0 = lh + H / 2
    f.block("Body", V(0, 0, z0), (L, W, H), C1)
    if BEL: f.block("Belly", V(0, 0, lh + H * 0.2), (L * 0.86, W + 0.06, H * 0.4), BEL, studs=False)
    feet = P.get("feet")
    for sx in (1, -1):
        for sy in (1, -1):
            x = sx * (L / 2 - lw / 2 - 0.15); y = sy * (W / 2 - lw / 2 + sprawl)
            f.block(f"Leg{sx}{sy}", V(x, y, (lh + 0.25) / 2), (lw, lw, lh + 0.25), P.get("leg_c", C1))
            if feet:
                fh = min(0.35, lh * 0.25); f.block(f"Foot{sx}{sy}", V(x + 0.05, y, fh / 2), (lw + 0.1, lw + 0.1, fh), feet, studs=False)
    nl, nt = P.get("neck", (0.4, 0.7)); hl, hw, hh = P["head"]
    base = V(L / 2 - 0.35, 0, lh + H * 0.68); d = V(math.cos(nt), 0, math.sin(nt))
    if nl > 0: f.block("Neck", base + d * (nl / 2), (nl + 0.6, hw * 0.72, hh * 0.72), P.get("neck_c", C1), Ry(-nt))
    hc = base + d * nl + V(hl * 0.3, 0, hh * 0.15)
    f.block("Head", hc, (hl, hw, hh), P.get("head_c", C1))
    sl, sw, sh = P.get("snout", (hl * 0.35, hw * 0.6, hh * 0.5)); sc = hc + V(hl / 2 + sl / 2 - 0.05, 0, -hh * 0.18)
    if sl > 0:
        f.block("Snout", sc, (sl, sw, sh), P.get("snout_c", C1), studs=False)
        f.block("Nose", sc + V(sl / 2, 0, sh * 0.22), (0.08, sw * 0.45, sh * 0.32), P.get("nose_c", BLACK), studs=False)
    eyes(f, hc, hl, hw, hh, P.get("angry", False), P.get("iris", YELLOW), C2, P.get("eye", 1.0))
    ears(f, P.get("ears"), hc, hl, hw, hh, P.get("ear_c", C1))
    tail(f, P.get("tail"), L, H, z0, P.get("tail_c", C1), P.get("tail_tip"))
    pattern(f, P.get("pattern"), L, W, H, lh, z0, P.get("pat_c", C2), P.get("pat_n", 5))
    if P.get("mane"): f.block("Mane", hc + V(-hl * 0.45, 0, 0), (hl * 0.55, hw * 1.45, hh * 1.45), P["mane"])
    c = dict(L=L, W=W, H=H, lh=lh, lw=lw, z0=z0, hc=hc, hl=hl, hw=hw, hh=hh, sc=sc, sl=sl, sw=sw, sh=sh, C1=C1, C2=C2)
    for fn in P.get("x", []): fn(f, c)
    return c

def bird(f, P):
    L, W, H = P["body"]; lh = P.get("leg", 0.8); C1 = P["c1"]; C2 = P.get("c2", dk(C1)); up = P.get("upright", False)
    z0 = lh + H / 2
    f.block("Body", V(0, 0, z0), (L, W, H), C1, None if up else Ry(-0.12))
    if P.get("belly"): f.block("Belly", V(L * 0.22, 0, z0 - H * 0.08), (L * 0.6, W * 0.92, H * 0.7), P["belly"], studs=False)
    hs = P["head"]; nk = P.get("neck", 0)
    hc = V(L * (0.12 if up else 0.42), 0, z0 + H / 2 + hs * 0.35 + nk)
    if nk > 0: f.block("Neck", V(L * 0.4, 0, z0 + H / 2 + nk / 2), (hs * 0.55, hs * 0.55, nk + 0.3), P.get("neck_c", C1))
    f.block("Head", hc, (hs, hs * 0.95, hs), P.get("head_c", C1))
    bl, bw, bh = P.get("beak", (hs * 0.4, hs * 0.3, hs * 0.25))
    f.block("Beak", hc + V(hs / 2 + bl / 2 - 0.03, 0, -hs * 0.1), (bl, bw, bh), P.get("beak_c", ORANGE), studs=False)
    eyes(f, hc, hs, hs * 0.95, hs, P.get("angry", False), P.get("iris", YELLOW), C2, P.get("eye", 1.0), fwd=0.15, up=0.15)
    wl = P.get("wing", 0.7)
    if P.get("spread"):
        for sy in (1, -1):
            for k in range(3):
                f.block(f"Wing{sy}{k}", V(-L * 0.05 - 0.35 * k, sy * (W / 2 + 0.9 + 0.6 * k), z0 + H * 0.4 + 0.4 * k), (L * 0.55 - 0.15 * k, 1.6, 0.18), P.get("wing_c", C2), Rx(-sy * 0.35), glow=P.get("wing_glow", False), studs=False)
    else:
        for sy in (1, -1): f.block(f"Wing{sy}", V(-L * 0.05, sy * (W / 2 + 0.09), z0 + H * 0.05), (L * wl, 0.18, H * 0.65), P.get("wing_c", C2), Rx(sy * 0.08), studs=False)
    f.block("TailFeathers", V(-L / 2 - L * 0.12, 0, z0 + H * 0.15 + (0 if up else 0.1)), (L * 0.35, W * 0.6, H * 0.22), P.get("tail_c", C2), Ry(-0.45 if not up else 0.3), glow=P.get("tail_glow", False), studs=False)
    for sy in (1, -1):
        f.block(f"Leg{sy}", V(0, sy * W * 0.22, lh / 2 + 0.05), (0.2, 0.2, lh + 0.1), P.get("leg_c", ORANGE), studs=False)
        f.block(f"Foot{sy}", V(0.2, sy * W * 0.22, 0.06), (0.6, 0.35, 0.12), P.get("leg_c", ORANGE), studs=False)
    c = dict(L=L, W=W, H=H, z0=z0, hc=hc, hs=hs, C1=C1, C2=C2)
    for fn in P.get("x", []): fn(f, c)
    return c

def ape(f, P):
    """Upright/knuckle-walking body: torso, head with muzzle, long arms to the ground, short legs."""
    W, D, H = P["torso"]; lh = P.get("leg", 1.2); C1 = P["c1"]; C2 = P.get("c2", dk(C1)); lean = P.get("lean", 0.35)
    z0 = lh + H / 2
    f.block("Torso", V(0, 0, z0), (D, W, H), C1, Ry(-lean))
    if P.get("belly"): f.block("Chest", V(D * 0.35, 0, z0 - H * 0.05), (0.2, W * 0.75, H * 0.7), P["belly"], Ry(-lean), studs=False)
    hs = P["head"]; hc = V(math.sin(lean) * H * 0.5 + 0.2, 0, z0 + H / 2 + hs * 0.35)
    f.block("Head", hc, (hs, hs, hs), P.get("head_c", C1))
    f.block("Muzzle", hc + V(hs / 2, 0, -hs * 0.2), (hs * 0.35, hs * 0.7, hs * 0.45), P.get("face_c", lt(C1)), studs=False)
    f.block("Nose", hc + V(hs / 2 + 0.18, 0, -hs * 0.08), (0.06, hs * 0.3, hs * 0.14), BLACK, studs=False)
    eyes(f, hc, hs, hs, hs, P.get("angry", False), P.get("iris", YELLOW), C2, P.get("eye", 1.0), fwd=0.4, up=0.15)
    ears(f, P.get("ears"), hc, hs, hs, hs, P.get("ear_c", C1))
    al = P.get("arm", H + lh * 0.8); aw = P.get("arm_w", W * 0.28)
    for sy in (1, -1):
        sh_ = V(math.sin(lean) * H * 0.45, sy * (W / 2 + aw / 2), z0 + H * 0.35)
        hand = V(sh_.x + al * 0.35, sy * (W / 2 + aw / 2 + 0.1), 0.25)
        dvec = hand - sh_; f.block(f"Arm{sy}", (sh_ + hand) / 2, (aw, aw, dvec.length), C1, dvec.to_track_quat("Z", "X").to_matrix())
        f.block(f"Hand{sy}", hand, (aw * 1.2, aw * 1.2, 0.4), P.get("hand_c", C2), studs=False)
        f.block(f"Leg{sy}", V(-0.3, sy * W * 0.28, (lh + 0.3) / 2), (aw * 1.1, aw * 1.1, lh + 0.3), C1)
        f.block(f"Foot{sy}", V(0.0, sy * W * 0.28, 0.15), (aw * 1.6, aw * 1.2, 0.3), P.get("hand_c", C2), studs=False)
    if P.get("tail"): tail(f, P["tail"], D * 1.2, H * 0.5, lh + H * 0.2, P.get("tail_c", C1), P.get("tail_tip"))
    c = dict(W=W, D=D, H=H, z0=z0, hc=hc, hs=hs, C1=C1, C2=C2, lh=lh)
    for fn in P.get("x", []): fn(f, c)
    return c

def trexlike(f, P):
    """Theropod built like the style-guide T-Rex (scaled by P['s'])."""
    s = P.get("s", 1.0); G1, G2, BEL = P["c1"], P.get("c2", dk(P["c1"])), P.get("belly", rgb(218, 198, 140))
    S = lambda x, y, z: V(x * s, y * s, z * s); Z = lambda *a: tuple(v * s for v in a)
    f.block("Body", S(0.6, 0, 4.7), Z(4.4, 2.8, 2.8), G1, Ry(-0.08))
    f.block("Chest", S(2.6, 0, 4.95), Z(1.9, 2.5, 2.5), G1, Ry(-0.25))
    f.block("Belly", S(1.0, 0, 3.32), Z(3.6, 2.4, 0.5), BEL, Ry(-0.08), studs=False)
    f.block("Neck", S(3.55, 0, 5.85), Z(1.7, 2.1, 2.1), G1, Ry(-0.6))
    sn = P.get("snout", 1.0)
    f.block("Cranium", S(4.8, 0, 6.75), Z(1.9, 2.5, 2.0), G1)
    f.block("Cheeks", S(4.6, 0, 5.95), Z(1.4, 2.8, 1.2), G1)
    f.block("Snout", S(5.4 + 1.35 * sn, 0, 6.6), Z(2.7 * sn, 1.9, 1.3), G1, Ry(0.05))
    f.block("Lip", S(5.3 + 1.35 * sn, 0, 5.98), Z(2.8 * sn, 1.96, 0.2), G2, studs=False)
    f.block("Mouth", S(5.1 + 1.3 * sn, 0, 5.62), Z(2.9 * sn, 1.7, 0.6), rgb(130, 36, 40), studs=False)
    hinge = S(4.6, 0, 5.55); X = Matrix.Translation(hinge) @ Ry(0.3).to_4x4() @ Matrix.Translation(-hinge)
    f.block("Jaw", X @ S(4.6 + 1.6 * sn, 0, 5.2), Z(3.2 * sn, 1.8, 0.62), G1, Ry(0.3))
    for sy in (-1, 1):
        for k in range(int(5 * sn) + 1):
            top = S(5.15 + 0.46 * k, sy * 0.8, 5.9); f.cyl(f"ToothU{sy}{k}", top, top - V(0, 0, 0.42 * s), 0.15 * s, rgb(248, 240, 220), 4, r1=0.0)
        for k in range(int(4 * sn) + 1):
            base = S(5.3 + 0.46 * k, sy * 0.7, 5.5); f.cyl(f"ToothL{sy}{k}", X @ base, X @ (base + V(0, 0, 0.36 * s)), 0.14 * s, rgb(248, 240, 220), 4, r1=0.0)
        f.block(f"Socket{sy}", S(5.15, sy * 1.26, 7.05), Z(0.85, 0.05, 0.62), dk(G2, 0.6), studs=False)
        f.block(f"Eye{sy}", S(5.2, sy * 1.29, 7.03), Z(0.56, 0.05, 0.46), P.get("iris", rgb(255, 160, 30)), studs=False, glow=P.get("eye_glow", False))
        f.block(f"Pupil{sy}", S(5.24, sy * 1.315, 7.03), Z(0.14, 0.04, 0.42), BLACK, studs=False)
        f.block(f"Brow{sy}", S(5.25, sy * 1.12, 7.45), Z(1.35, 0.55, 0.36), G2, Ry(0.34) @ Rx(sy * 0.12), studs=False)
        f.block(f"UpperArm{sy}", S(3.05, sy * 1.35, 4.25), Z(0.8, 0.35, 0.35), G1, Ry(0.8), studs=False)
        f.block(f"Forearm{sy}", S(3.45, sy * 1.35, 3.95), Z(0.6, 0.3, 0.3), G1, Ry(-0.3), studs=False)
        f.block(f"Thigh{sy}", S(-0.2, sy * 1.6, 3.7), Z(2.3, 1.2, 2.7), G1, Ry(0.25))
        f.block(f"Shin{sy}", S(-0.5, sy * 1.6, 1.6), Z(1.0, 1.0, 2.5), G1, Ry(-0.3))
        f.block(f"Foot{sy}", S(0.35, sy * 1.6, 0.25), Z(2.0, 1.25, 0.5), G2)
    for k, (x, z, L_, s_) in enumerate([(-2.6, 4.8, 2.4, 2.4), (-4.6, 4.65, 2.2, 1.8), (-6.4, 4.45, 2.0, 1.35), (-8.0, 4.25, 1.8, 0.9), (-9.3, 4.05, 1.3, 0.55)]):
        f.block(f"Tail{k}", S(x, 0, z), Z(L_, s_, s_), G1)
        if k < 4: f.block(f"Band{k}", S(x, 0, z + s_ * 0.12), Z(0.5, s_ + 0.06, s_ * 0.78), G2)
    c = dict(s=s, S=S, Z=Z, G1=G1, G2=G2)
    for fn in P.get("x", []): fn(f, c)
    return c
