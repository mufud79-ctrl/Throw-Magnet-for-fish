"""Generate game/ShowcaseBuilder.lua (one self-contained command-bar script) from the manifest.

    python3 tools/roblox/gen_showcase.py

Reads game/manifest.json and game/asset_ids.json (optional; models without an ID are cloned
from ServerStorage.ShowcaseImports in Studio) and fills tools/roblox/showcase_template.lua.
Also writes game/CheckUploads.lua, which reports what Roblox built from each uploaded asset
(MeshParts, textures, Bones, _Glow part). Re-run after every upload batch so the new IDs are baked in.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / "game"
TEMPLATE = Path(__file__).with_name("showcase_template.lua")
OUT = GAME / "ShowcaseBuilder.lua"
CHECK_TEMPLATE = Path(__file__).with_name("check_template.lua")
CHECK_OUT = GAME / "CheckUploads.lua"
OUTLINE = "#1B1530"   # ui/README.md: outline colour used everywhere

# key, sign title, floor colour, fish-style pedestal, yaw (deg) so the side profile faces the walkway
DISTRICTS = [
    ("Fish", "FISH", "#2B5FA8", True, -90),
    ("Bait", "BAITS", "#C46A1E", True, -90),
    ("Gym", "GYM", "#4A5160", False, 0),
    ("Zone", "ZONE PROPS", "#1C8574", False, 0),
]


def pretty(group):
    """'04_NeonSport' -> '04 Neon Sport', '07_DeepAbyss' -> '07 Deep Abyss'."""
    num, _, word = group.partition("_")
    return f"{num} {re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', word)}"


def mix(hex_, t, to="#FFFFFF"):
    a = [int(hex_[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(to[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def readable(hex_):
    """Text colour for the tag's small line: the rarity colour, or white if it's too dark to read."""
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return hex_ if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.25 else "#FFFFFF"


def lua(v, ind=""):
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v)          # JSON string escapes are valid Luau
    if isinstance(v, list):
        if not v:
            return "{}"
        inner = ind + "\t"
        return "{\n" + "".join(f"{inner}{lua(x, inner)},\n" for x in v) + ind + "}"
    if isinstance(v, dict):
        if all(not isinstance(x, (list, dict)) for x in v.values()):   # short records on one line
            return "{ " + ", ".join(f"{k} = {lua(x)}" for k, x in v.items()) + " }"
        inner = ind + "\t"
        return "{\n" + "".join(f"{inner}{k} = {lua(x, inner)},\n" for k, x in v.items()) + ind + "}"
    raise TypeError(type(v))


def main():
    man = json.loads((GAME / "manifest.json").read_text())
    ids_path = GAME / "asset_ids.json"
    ids = json.loads(ids_path.read_text()) if ids_path.exists() else {}
    rcol, rorder = man["rarityColors"], man["rarityOrder"]

    def item(m, sub, sub_color):
        return {"n": m["name"], "g": m["group"], "id": int(ids.get(m["name"], 0)), "glow": m["glow"],
                "src": str(Path(m["fbx"]).parent.as_posix()) + "/", "sub": sub, "subColor": sub_color}

    districts = []
    for key, title, color, pedestal, yaw in DISTRICTS:
        models = sorted((m for m in man["models"] if m["category"] == key),
                        key=lambda m: (rorder.index(m["group"]) if m["group"] in rorder else 0, m["group"], m["order"]))
        rows = []
        if key in ("Fish", "Bait"):          # one row per rarity, tinted with its colour
            for r in rorder:
                ms = [m for m in models if m["group"] == r]
                if ms:
                    rows.append({"key": r, "label": r.upper(), "color": rcol[r],
                                 "items": [item(m, r, readable(rcol[r])) for m in ms]})
        elif key == "Gym":                   # one row of the 15 tiers in order
            rows.append({"key": "Tiers", "label": "TIERS 01-15", "color": mix(color, 0.35),
                         "items": [item(m, pretty(m["group"]), "#FFD25A") for m in models]})
        else:                                # one row per zone
            for g in sorted({m["group"] for m in models}):
                rows.append({"key": g, "label": pretty(g), "color": mix(color, 0.35),
                             "items": [item(m, pretty(g), "#8CF0E0") for m in models if m["group"] == g]})
        districts.append({"key": key, "title": title, "color": color, "pedestal": pedestal,
                          "yaw": yaw, "rows": rows})

    data = {"outline": OUTLINE, "districts": districts}
    src = TEMPLATE.read_text().replace("__DATA__", lua(data))
    OUT.write_text(src)
    check = [{"n": m["name"], "id": int(ids[m["name"]]), "rigged": m["rigged"], "glow": m["glow"] is not None}
             for m in man["models"] if m["name"] in ids]
    CHECK_OUT.write_text(CHECK_TEMPLATE.read_text().replace("__CHECK__", lua(check)))
    n = sum(len(r["items"]) for d in districts for r in d["rows"])
    with_id = sum(1 for d in districts for r in d["rows"] for i in r["items"] if i["id"])
    print(f"{OUT.relative_to(ROOT)}: {n} models, {with_id} with asset IDs, "
          f"{n - with_id} from ServerStorage.ShowcaseImports ({len(src) // 1024} KB); "
          f"{CHECK_OUT.relative_to(ROOT)}: {len(check)} uploaded assets")


if __name__ == "__main__":
    main()
