"""Head studies (no body) for user feedback: 4 lion heads (Chimera) + 4 horse heads (Pegasus / Unicorn), TFFA kit.

usage: /tmp/bpyenv/bin/python tools/blender/tffa_head_studies.py [Name ...] [--sheet]
Writes models/TFFA/HeadStudies/<Name>/ and HeadStudies_overview.png (rows: lions, horses; 3/4 + side per head)."""
import os, sys, subprocess, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tffa-animal-models", "scripts"))
OUT = os.path.join(ROOT, "models", "TFFA", "HeadStudies")
ARGS = sys.argv[1:]

FUR, MANE, MANE2, CREAMY, LNOSE = (0.87, 0.64, 0.31), (0.59, 0.27, 0.13), (0.73, 0.38, 0.16), (0.96, 0.89, 0.71), (0.24, 0.13, 0.12)
WH, PINKM, HMANE, HNOSE = (0.96, 0.96, 0.98), (1.0, 0.89, 0.94), (1.0, 0.59, 0.78), (0.42, 0.28, 0.32)
VIEWS = [("hero", 35, 8, 50), ("side", 90, 4, 50)]


def lion_base(m, V, ear=True):
    """Neck stub + skull shared by the lion studies; returns nothing (parts go straight on m)."""
    m.box("Neck", (-1.5, 0, 1.6), (2.0, 2.2, 2.4), FUR, top=(0.9, 0.9))
    if ear:
        for s in (1, -1):
            m.box(f"Ear{s}", (-0.35, s * 1.15, 4.35), (0.55, 0.6, 0.6), FUR, top=(0.7, 0.8))
            m.box(f"EarIn{s}", (-0.06, s * 1.15, 4.32), (0.1, 0.36, 0.36), V["dk"](FUR, 0.6), studs=False)


def L1_ManeCollar(m, K):
    """Square head framed by a big mane collar with radiating tufts; snarling open jaw."""
    lion_base(m, K)
    m.box("ManeCollar", (-0.75, 0, 3.0), (1.3, 4.6, 4.2), MANE, top=(0.8, 0.78), bot=(0.85, 0.8))
    for k in range(10):
        a = 2 * math.pi * (k + 0.5) / 10; y, z = math.cos(a), math.sin(a)
        m.box(f"Tuft{k}", (-0.75, y * 2.35, 3.0 + z * 2.15), (1.0, 1.0, 1.0), MANE2 if k % 2 else MANE, rot=K["Rx"](a), top=(0.6, 0.6))
    m.box("Head", (0.15, 0, 3.05), (2.3, 2.6, 2.3), FUR, top=(0.9, 0.9))
    m.box("Muzzle", (1.55, 0, 2.65), (0.95, 1.75, 0.95), CREAMY, top=(0.9, 0.92))
    m.box("Nose", (2.06, 0, 3.0), (0.16, 0.75, 0.42), LNOSE, bot=(0.9, 0.45), studs=False)
    m.box("Bridge", (1.25, 0, 3.32), (1.1, 0.8, 0.3), K["dk"](FUR, 0.85), studs=False)
    with m.frame(pivot=(0.6, 0, 2.2), rot=K["Ry"](0.38)):          # open lower jaw
        m.box("Jaw", (1.3, 0, 1.95), (1.4, 1.55, 0.45), CREAMY)
        m.box("Tongue", (1.25, 0, 2.2), (1.0, 1.0, 0.14), K["TONGUE"], studs=False)
        m.teeth("ToothB", (1.95, -0.55, 2.15), (1.95, 0.55, 2.15), 4, 0.3, 0.1, down=False, fangs=(0, 3))
    m.box("Mouth", (1.35, 0, 2.05), (0.9, 1.4, 0.55), K["MOUTH"], studs=False)
    m.teeth("ToothT", (2.0, -0.62, 2.2), (2.0, 0.62, 2.2), 5, 0.3, 0.1, fangs=(0, 4))
    m.eyes((1.27, 0.6, 3.5), size=(0.7, 0.6), pupil=0.62, look=(0.3, -0.1), angry=0.42, brow_col=K["dk"](MANE, 0.7), brow_h=0.4, brow_up=0.66, depth=0.16)


def L2_Sunburst(m, K):
    """Rounder head inside a sunburst of mane spikes; closed mouth, whisker pads, fangs over the lip."""
    lion_base(m, K, ear=False)
    m.box("ManeDisk", (-0.7, 0, 3.0), (1.1, 3.4, 3.4), MANE, top=(0.85, 0.85))
    for k in range(14):
        a = 2 * math.pi * k / 14; y, z = math.cos(a), math.sin(a); L = 3.0 if k % 2 else 2.5
        m.spike(f"Ray{k}", (-0.7, y * 1.3, 3.0 + z * 1.3), (-1.0, y * L, 3.0 + z * L), 0.6, MANE2 if k % 2 else MANE, sides=4)
    for s in (1, -1):
        m.box(f"Ear{s}", (-0.2, s * 1.05, 4.15), (0.5, 0.55, 0.55), FUR, top=(0.7, 0.8))
    m.box("Head", (0.2, 0, 3.0), (2.2, 2.5, 2.2), FUR, top=(0.86, 0.88), bot=(0.9, 0.92))
    for s in (1, -1):
        m.box(f"Pad{s}", (1.55, s * 0.42, 2.6), (0.8, 0.85, 0.75), CREAMY, top=(0.85, 0.9))
    m.box("Chin", (1.3, 0, 2.05), (0.8, 0.9, 0.45), CREAMY)
    m.box("Nose", (1.98, 0, 2.98), (0.18, 0.72, 0.42), LNOSE, bot=(0.9, 0.45), studs=False)
    m.box("Bridge", (1.3, 0, 3.25), (1.0, 0.7, 0.35), K["dk"](FUR, 0.85), studs=False)
    for s in (1, -1):
        m.spike(f"Fang{s}", (1.92, s * 0.33, 2.32), (1.95, s * 0.33, 1.85), 0.1, K["TOOTH"], flat=0.35)
    m.eyes((1.12, 0.6, 3.45), size=(0.7, 0.55), pupil=0.66, look=(0.35, -0.1), angry=0.35, brow_col=K["dk"](MANE, 0.7), brow_h=0.42, brow_up=0.66, depth=0.16)


def L3_Roar(m, K):
    """Full roar: heavy mane hood falling over the brow, upper head tipped up, jaw dropped wide, big fangs."""
    lion_base(m, K, ear=False)
    m.box("ManeBack", (-0.9, 0, 2.9), (1.6, 4.0, 4.2), MANE, top=(0.75, 0.75), bot=(0.8, 0.8))
    for k in range(5):
        y = (k - 2) * 0.62
        m.box(f"Hood{k}", (0.25 - abs(k - 2) * 0.15, y, 4.4 - abs(k - 2) * 0.12), (1.9, 0.75, 0.7), MANE2 if k % 2 else MANE, rot=K["Ry"](-0.25), top=(0.7, 0.8))
    for s in (1, -1):
        for j in range(3):
            m.box(f"SideMane{s}{j}", (-0.2 - j * 0.15, s * (1.55 + j * 0.15), 3.6 - j * 1.0), (1.4, 0.6, 1.1), MANE2 if j % 2 else MANE, rot=K["Rx"](s * 0.2))
    with m.frame(pivot=(0.4, 0, 2.6), rot=K["Ry"](-0.18)):          # upper head tipped up
        m.box("Head", (0.15, 0, 3.15), (2.2, 2.5, 1.9), FUR, top=(0.9, 0.9))
        m.box("Muzzle", (1.5, 0, 2.85), (1.0, 1.7, 0.75), CREAMY, top=(0.9, 0.92))
        m.box("Nose", (2.02, 0, 3.12), (0.16, 0.72, 0.4), LNOSE, bot=(0.9, 0.45), studs=False)
        for k in range(3): m.box(f"Wrinkle{k}", (1.2 + k * 0.22, 0, 3.32 - k * 0.04), (0.12, 0.85, 0.12), K["dk"](FUR, 0.75), studs=False)
        m.box("MouthTop", (1.35, 0, 2.45), (1.0, 1.4, 0.12), K["MOUTH"], studs=False)
        m.teeth("ToothT", (1.95, -0.6, 2.5), (1.95, 0.6, 2.5), 5, 0.32, 0.11, fangs=(0, 4))
        m.eyes((1.22, 0.62, 3.55), size=(0.72, 0.42), pupil=0.85, look=(0.4, 0), angry=0.5, brow_col=K["dk"](MANE, 0.7), brow_h=0.5, brow_up=0.7, depth=0.16)
    with m.frame(pivot=(0.4, 0, 2.3), rot=K["Ry"](0.55)):           # dropped jaw
        m.box("Jaw", (1.2, 0, 1.95), (1.5, 1.5, 0.5), CREAMY)
        m.box("MouthIn", (1.15, 0, 2.25), (1.3, 1.3, 0.14), K["MOUTH"], studs=False)
        m.box("Tongue", (1.2, 0, 2.3), (1.0, 0.9, 0.16), K["TONGUE"], studs=False)
        m.teeth("ToothB", (1.85, -0.55, 2.2), (1.85, 0.55, 2.2), 4, 0.3, 0.1, down=False, fangs=(0, 3))


def L4_King(m, K):
    """Long noble face, tiered mane: crown on top, side panels falling below the jaw to the chest; closed mouth."""
    m.box("Neck", (-1.5, 0, 1.4), (2.0, 2.2, 2.6), FUR, top=(0.9, 0.9))
    m.box("ManeBack", (-0.85, 0, 2.7), (1.5, 3.6, 4.4), MANE, top=(0.8, 0.85), bot=(0.9, 0.8))
    for k in range(4):
        m.box(f"Crown{k}", (-0.3 - k * 0.15, (k - 1.5) * 0.85, 4.55 + (0.15 if k in (1, 2) else 0)), (1.3, 0.85, 0.9), MANE2 if k % 2 else MANE, top=(0.6, 0.7))
    for s in (1, -1):
        for j in range(3):
            m.box(f"Panel{s}{j}", (0.15 - j * 0.1, s * 1.45, 3.4 - j * 1.05), (1.5, 0.55, 1.15), MANE2 if j % 2 else MANE, bot=(0.85, 0.85))
        m.box(f"Ear{s}", (-0.3, s * 1.0, 4.45), (0.5, 0.5, 0.5), FUR, top=(0.7, 0.8))
    m.box("Beard", (0.6, 0, 1.1), (1.2, 2.0, 1.6), MANE, top=(1.0, 1.0), bot=(0.6, 0.6))
    m.box("Head", (0.25, 0, 3.0), (2.2, 2.3, 2.5), FUR, top=(0.88, 0.9))
    m.box("Bridge", (1.25, 0, 3.4), (0.9, 0.75, 0.55), K["dk"](FUR, 0.9))
    for s in (1, -1):
        m.box(f"Pad{s}", (1.65, s * 0.4, 2.5), (0.8, 0.8, 0.7), CREAMY, top=(0.85, 0.9))
    m.box("Chin", (1.35, 0, 1.95), (0.7, 0.8, 0.4), CREAMY)
    m.box("Nose", (2.08, 0, 2.9), (0.18, 0.7, 0.42), LNOSE, bot=(0.9, 0.45), studs=False)
    m.box("MouthLine", (2.0, 0, 2.18), (0.08, 0.9, 0.07), K["dk"](CREAMY, 0.5), studs=False)
    m.eyes((1.37, 0.58, 3.55), size=(0.66, 0.52), pupil=0.68, look=(0.35, -0.1), angry=0.28, brow_col=K["dk"](MANE, 0.65), brow_h=0.42, brow_up=0.66, depth=0.16)


def horse_neck(m, K, w=1.3):
    m.seg("Neck", (-2.6, 0, 0.4), (-0.8, 0, 3.0), w * 1.1, w * 0.9, WH, d0=2.4, d1=1.7)
    for k in range(5):
        t = k / 4; p = (-2.75 + 1.8 * t - 0.3, 0, 1.3 + 2.4 * t)
        m.box(f"Mane{k}", p, (0.9, 0.55, 0.9), HMANE, rot=K["Ry"](-0.6), top=(0.6, 0.8))
        for s in (1, -1):
            m.box(f"ManeSide{k}{s}", (p[0] + 0.25, s * 0.6, p[2] - 0.5), (0.65, 0.2, 1.1), HMANE, rot=K["Ry"](-0.5), bot=(0.6, 0.8), studs=False)


def H1_Wedge(m, K):
    """Classic: skull block at the poll, long tapering face pitched nose-down, deep cheek, soft muzzle tip, side eyes."""
    horse_neck(m, K)
    with m.frame(pivot=(-0.6, 0, 3.2), rot=K["Ry"](0.55)):
        m.box("Skull", (0.0, 0, 3.35), (1.7, 1.5, 1.5), WH, top=(0.9, 0.9))
        m.box("Cheek", (-0.1, 0, 2.65), (1.4, 1.45, 0.9), WH, bot=(0.75, 0.85))
        m.box("Face", (1.4, 0, 3.15), (1.6, 1.2, 1.25), WH, top=(0.86, 0.88), bot=(0.95, 0.95))
        m.box("Muzzle", (2.35, 0, 3.05), (0.65, 1.3, 1.15), PINKM, top=(0.9, 0.9))
        for s in (1, -1):
            m.box(f"Nostril{s}", (2.68, s * 0.32, 3.2), (0.08, 0.2, 0.26), HNOSE, studs=False)
            m.box(f"Ear{s}", (-0.35, s * 0.45, 4.35), (0.35, 0.3, 0.8), WH, top=(0.3, 0.5))
        m.box("MouthLine", (2.66, 0, 2.78), (0.06, 0.8, 0.06), K["dk"](PINKM, 0.6), studs=False)
        m.box("Forelock", (0.35, 0, 4.15), (0.8, 0.6, 0.45), HMANE, top=(0.6, 0.8), studs=False)
        m.eyes((0.35, 0.77, 3.55), facing=(0.3, 1, 0), size=(0.62, 0.56), pupil=0.66, look=(0.35, 0), angry=0.05, brow_col=K["dk"](WH, 0.7), brow_h=0.3, brow_up=0.62, depth=0.14)


def H2_Cartoon(m, K):
    """Cartoon: shorter rounder head, eyes set forward (3/4 facing) and big, wide round muzzle, swept forelock."""
    horse_neck(m, K)
    with m.frame(pivot=(-0.6, 0, 3.2), rot=K["Ry"](0.3)):
        m.box("Skull", (0.2, 0, 3.4), (2.0, 1.8, 1.8), WH, top=(0.88, 0.9))
        m.box("Face", (1.35, 0, 3.05), (1.2, 1.45, 1.3), WH, top=(0.88, 0.9))
        m.box("Muzzle", (2.1, 0, 2.85), (0.8, 1.65, 1.2), PINKM, top=(0.88, 0.9), bot=(0.92, 0.95))
        for s in (1, -1):
            m.box(f"Nostril{s}", (2.5, s * 0.4, 3.0), (0.08, 0.22, 0.26), HNOSE, studs=False)
            m.box(f"Ear{s}", (-0.25, s * 0.6, 4.55), (0.4, 0.35, 0.9), WH, top=(0.3, 0.5), rot=K["Rx"](s * 0.15))
        m.box("Smile", (2.5, 0, 2.55), (0.06, 0.9, 0.07), K["dk"](PINKM, 0.55), studs=False)
        m.box("Forelock", (0.75, 0.25, 4.25), (1.1, 0.95, 0.5), HMANE, rot=K["Rx"](-0.35), top=(0.6, 0.8), studs=False)
        m.eyes((0.95, 0.72, 3.65), facing=(0.75, 0.66, 0), size=(0.82, 0.78), pupil=0.62, look=(0.3, 0), angry=-0.05, brow_col=K["dk"](WH, 0.7), brow_h=0.28, brow_up=0.64, depth=0.15)


def H3_Warhorse(m, K):
    """Fierce: long slim face pitched down, ridge down the nose, flared nostrils, angry side eyes, spiky crest mane."""
    m.seg("Neck", (-2.6, 0, 0.4), (-0.8, 0, 3.0), 1.45, 1.2, WH, d0=2.5, d1=1.75)
    for k in range(6):
        t = k / 5; p = (-2.9 + 1.9 * t, 0, 1.6 + 2.4 * t)
        m.spike(f"Crest{k}", p, (p[0] - 0.7, 0, p[2] + 0.9), 0.4, HMANE, flat=0.4)
    with m.frame(pivot=(-0.6, 0, 3.2), rot=K["Ry"](0.6)):
        m.box("Skull", (0.0, 0, 3.35), (1.6, 1.45, 1.45), WH, top=(0.9, 0.9))
        m.box("Cheek", (-0.05, 0, 2.65), (1.5, 1.5, 1.0), WH, bot=(0.7, 0.85))
        m.box("Face", (1.45, 0, 3.2), (1.8, 1.05, 1.1), WH, top=(0.82, 0.86), bot=(0.95, 0.95))
        m.box("Ridge", (1.3, 0, 3.78), (1.6, 0.4, 0.14), K["dk"](WH, 0.85), studs=False)
        m.box("Muzzle", (2.5, 0, 3.08), (0.6, 1.15, 1.05), PINKM, top=(0.9, 0.9))
        for s in (1, -1):
            m.box(f"Nostril{s}", (2.78, s * 0.3, 3.25), (0.1, 0.24, 0.34), HNOSE, studs=False, rot=K["Rx"](s * 0.3))
            m.box(f"Ear{s}", (-0.4, s * 0.42, 4.35), (0.3, 0.26, 0.85), WH, top=(0.2, 0.4), rot=K["Ry"](-0.35))
        m.eyes((0.4, 0.74, 3.6), facing=(0.35, 1, 0), size=(0.6, 0.42), pupil=0.85, look=(0.5, 0), angry=0.45, brow_col=K["dk"](WH, 0.55), brow_h=0.42, brow_up=0.66, depth=0.14)


def H4_Chunky(m, K):
    """TFFA chunky (cow-example proportions): big box head, long same-width snout, raised side-eye sockets."""
    horse_neck(m, K, w=1.5)
    with m.frame(pivot=(-0.6, 0, 3.2), rot=K["Ry"](0.35)):
        m.box("Head", (0.3, 0, 3.4), (2.2, 1.9, 1.9), WH, top=(0.9, 0.9))
        m.box("Snout", (1.9, 0, 3.05), (1.4, 1.7, 1.3), WH, top=(0.9, 0.92))
        m.box("Muzzle", (2.75, 0, 2.95), (0.5, 1.75, 1.25), PINKM, top=(0.92, 0.94))
        for s in (1, -1):
            m.box(f"Socket{s}", (0.7, s * 0.95, 3.75), (0.85, 0.3, 0.8), WH)
            m.box(f"Nostril{s}", (3.02, s * 0.42, 3.1), (0.08, 0.26, 0.3), HNOSE, studs=False)
            m.box(f"Ear{s}", (-0.3, s * 0.6, 4.6), (0.4, 0.35, 0.8), WH, top=(0.3, 0.5))
        m.box("Forelock", (0.6, 0, 4.4), (0.9, 0.7, 0.4), HMANE, top=(0.6, 0.8), studs=False)
        m.eyes((0.75, 1.11, 3.8), facing=(0.25, 1, 0), size=(0.62, 0.6), pupil=0.66, look=(0.3, 0), angry=0.08, brow_col=K["dk"](WH, 0.7), brow_h=0.3, brow_up=0.62, depth=0.14)


STUDIES = [L1_ManeCollar, L2_Sunburst, L3_Roar, L4_King, H1_Wedge, H2_Cartoon, H3_Warhorse, H4_Chunky]


def build_one(fn):
    from tffa_kit import Model, Rx, Ry, dk, MOUTH, TONGUE, TOOTH
    name = fn.__name__
    m = Model(name, os.path.join(OUT, name), stud=0.42, chamfer=0.16)
    K = dict(Rx=Rx, Ry=Ry, dk=dk, MOUTH=MOUTH, TONGUE=TONGUE, TOOTH=TOOTH)
    with m.bone("Head", (-0.6, 0, 3.0)):
        fn(m, K)
    m.done(views=VIEWS)


def sheet():
    from PIL import Image, ImageDraw
    T = 360; out = Image.new("RGB", (T * 8, T * 2), "white"); d = ImageDraw.Draw(out)
    for i, fn in enumerate(STUDIES):
        r, c = divmod(i, 4)
        for j, (v, *_r) in enumerate(VIEWS):
            p = os.path.join(OUT, fn.__name__, "previews", f"{fn.__name__}_{v}.png")
            if os.path.exists(p): out.paste(Image.open(p).convert("RGB").resize((T, T)), ((c * 2 + j) * T, r * T))
        d.rectangle([c * 2 * T + 6, r * T + 6, c * 2 * T + 200, r * T + 34], fill="white")
        d.text((c * 2 * T + 12, r * T + 12), fn.__name__, fill="black")
    out.save(os.path.join(OUT, "HeadStudies_overview.png")); print("SHEET", os.path.join(OUT, "HeadStudies_overview.png"))


if __name__ == "__main__":
    want = [a for a in ARGS if not a.startswith("--")]
    if "--child" in ARGS:
        build_one(next(f for f in STUDIES if f.__name__ == want[0])); sys.exit()
    for fn in STUDIES:
        if want and fn.__name__ not in want: continue
        print("BUILD", fn.__name__, flush=True)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), fn.__name__, "--child"], capture_output=True, text=True)
        if r.returncode: print("FAILED", fn.__name__, r.stderr[-1500:], flush=True)
    if "--sheet" in ARGS: sheet()
