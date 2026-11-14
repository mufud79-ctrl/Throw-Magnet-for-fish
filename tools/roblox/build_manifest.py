"""Scan models/ and write game/manifest.json: one entry per showcase model.

    python3 tools/roblox/build_manifest.py

Sources of truth (nothing is retyped here):
  * fish order inside a rarity: tools/ui/fishdata.py FISH (the Fish Index order)
  * bait order:                 the BAITS list in tools/blender/baits.py (read as text, no bpy)
  * zone prop order:            the ZONES list in tools/blender/zones_blocky.py (read as text)
  * glow colours:               the three glow tables in models/README.md
  * rarity colours:             the "Main" column of the rarity table in ui/README.md
Folders that exist on disk but are missing from an order list are appended alphabetically,
so a new model still shows up. Skipped: models/CannonTame/ and models/Gym/_Archive_Benches/.
"""
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "models"
OUT = ROOT / "game" / "manifest.json"
sys.path.insert(0, str(ROOT / "tools" / "ui"))
from fishdata import FISH, RARITIES  # noqa: E402

EXPECTED = {"Fish": 50, "Bait": 15, "Gym": 15, "Zone": 60}
HEX = re.compile(r"`(#[0-9A-Fa-f]{6})`")


def table_rows(md, header_start):
    """Yield the cell lists of the markdown table whose header row starts with `header_start`."""
    lines = md.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("|") and ln.strip("| ").startswith(header_start):
            for row in lines[i + 2:]:
                if not row.startswith("|"):
                    return
                yield [c.strip() for c in row.strip().strip("|").split("|")]
    return


def parse_glows():
    """name -> '#RRGGBB' from the fish/bait, gym and zone tables in models/README.md."""
    md = (MODELS / "README.md").read_text()
    glow = {}
    for cells in table_rows(md, "Fish | Glow parts"):            # "SeraphFish" / "PhantomJelly (bait)"
        glow[cells[0].split(" (")[0]] = HEX.search(cells[-1]).group(1).upper()
    for cells in table_rows(md, "Tier | Glow parts"):            # "06 Crystal" -> CrystalDumbbell
        glow[cells[0].split()[1] + "Dumbbell"] = HEX.search(cells[-1]).group(1).upper()
    for cells in table_rows(md, "Zone | Prop with glow"):        # "03_Swamp | BogGlowBulbs"
        glow[cells[1]] = HEX.search(cells[-1]).group(1).upper()
    return glow


def parse_rarity_colors():
    md = (ROOT / "ui" / "README.md").read_text()
    cols = {c[0]: HEX.search(c[1]).group(1).upper() for c in table_rows(md, "Rarity | Main")}
    missing = [r for r in RARITIES if r not in cols]
    if missing:
        sys.exit(f"ui/README.md rarity table is missing {missing}")
    return {r: cols[r] for r in RARITIES}


def source_order(path, list_name):
    """Quoted names in the first `("Name", ...` tuples of a list literal, in source order."""
    src = path.read_text()
    m = re.search(rf"^{list_name}\s*=\s*\[(.*?)^\]", src, re.S | re.M) or \
        re.search(rf"^{list_name}\s*=\s*\[(.*?)\]\s*$", src, re.S | re.M)
    if not m:
        sys.exit(f"could not find {list_name} in {path}")
    return re.findall(r'\(\s*"(\w+)"\s*,', m.group(1))


def ordered(names, preferred):
    rank = {n: i for i, n in enumerate(preferred)}
    return sorted(names, key=lambda n: (rank.get(n, len(rank)), n))


def glb_info(glb):
    """(mesh node names, has skin) from the GLB's JSON chunk."""
    data = glb.read_bytes()
    n = struct.unpack("<I", data[12:16])[0]
    j = json.loads(data[20:20 + n])
    meshes = [nd.get("name") for nd in j.get("nodes", []) if "mesh" in nd]
    return meshes, bool(j.get("skins"))


def entry(folder, category, group, order, glows):
    name = folder.name
    fbx, glb = folder / f"{name}.fbx", folder / f"{name}.glb"
    for f in (fbx, glb):
        if not f.exists():
            sys.exit(f"missing {f.relative_to(ROOT)}")
    meshes, rigged = glb_info(glb)
    has_glow_mesh = f"{name}_Glow" in meshes
    glow = glows.get(name)
    if has_glow_mesh != (glow is not None):
        print(f"  WARNING {name}: glow mesh={has_glow_mesh} but README colour={glow}")
    return {
        "name": name, "category": category, "group": group, "order": order,
        "fbx": fbx.relative_to(ROOT).as_posix(), "glb": glb.relative_to(ROOT).as_posix(),
        "glow": glow, "meshes": meshes, "rigged": rigged,
    }


def subdirs(p):
    return [d for d in p.iterdir() if d.is_dir() and not d.name.startswith(("_", "."))] if p.is_dir() else []


def main():
    glows = parse_glows()
    out = []

    for rarity in RARITIES:                                       # Fish
        names = [d.name for d in subdirs(MODELS / rarity)]
        for i, n in enumerate(ordered(names, FISH.get(rarity, []))):
            out.append(entry(MODELS / rarity / n, "Fish", rarity, i + 1, glows))

    bait_order = source_order(ROOT / "tools/blender/baits.py", "BAITS")
    for rarity in RARITIES:                                       # Baits
        names = [d.name for d in subdirs(MODELS / "Baits" / rarity)]
        for i, n in enumerate(ordered(names, bait_order)):
            out.append(entry(MODELS / "Baits" / rarity / n, "Bait", rarity, i + 1, glows))

    for tier in sorted(subdirs(MODELS / "Gym"), key=lambda d: d.name):   # Gym, 01..15
        for i, d in enumerate(sorted(subdirs(tier), key=lambda d: d.name)):
            out.append(entry(d, "Gym", tier.name, i + 1, glows))

    prop_order = source_order(ROOT / "tools/blender/zones_blocky.py", "ZONES")
    for zone in sorted(subdirs(MODELS / "Zones"), key=lambda d: d.name):  # Zones, 01..10
        names = [d.name for d in subdirs(zone)]
        for i, n in enumerate(ordered(names, prop_order)):
            out.append(entry(zone / n, "Zone", zone.name, i + 1, glows))

    names = [e["name"] for e in out]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        sys.exit(f"duplicate model names (asset_ids.json is keyed by name): {sorted(dupes)}")
    unused = sorted(set(glows) - set(names))
    if unused:
        print(f"  WARNING glow colours with no model: {unused}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "rarityOrder": RARITIES,
        "rarityColors": parse_rarity_colors(),
        "models": out,
    }
    OUT.write_text(json.dumps(manifest, indent=1) + "\n")

    ok = True
    for cat, want in EXPECTED.items():
        got = sum(e["category"] == cat for e in out)
        ok &= got == want
        print(f"{cat:5s} {got:3d}  (expected {want}){'' if got == want else '  <-- MISMATCH'}")
    print(f"total {len(out)}, {sum(e['glow'] is not None for e in out)} with glow -> {OUT.relative_to(ROOT)}")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
