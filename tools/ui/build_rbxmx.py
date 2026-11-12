"""Build ui/FishingUI.rbxmx (static Roblox UI, no scripts) and ui/asset_map.json.

    python3 tools/ui/build_rbxmx.py [ui]

The layout is a tree of N(...) nodes. build_preview.py renders the same tree to HTML,
so the preview screenshots show exactly this layout.
Every image instance gets Image = rbxassetid://0 plus an "AssetFile" attribute naming its PNG
(relative to ui/); asset_map.json lists PNG -> instance paths.
"""
import base64
import hashlib
import json
import os
import struct
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fishdata as fd  # noqa: E402

PLACEHOLDER = "rbxassetid://0"


# ---------------------------------------------------------------- typed values
class UDim2(tuple):
    def __new__(cls, xs, xo, ys, yo): return super().__new__(cls, (xs, xo, ys, yo))


class UDim(tuple):
    def __new__(cls, s, o): return super().__new__(cls, (s, o))


class Vec2(tuple):
    def __new__(cls, x, y): return super().__new__(cls, (x, y))


class Rect(tuple):
    def __new__(cls, x0, y0, x1, y1): return super().__new__(cls, (x0, y0, x1, y1))


class Color(tuple):
    def __new__(cls, hexcol):
        r, g, b = fd.hex2rgb(hexcol)
        return super().__new__(cls, (r / 255, g / 255, b / 255))


class Token:
    def __init__(self, value, label): self.value, self.label = value, label


class Font:
    def __init__(self, family): self.family = family


class ColorSeq(list):
    pass


class NumSeq(list):
    pass


class Content(str):
    pass


INT_PROPS = {"BorderSizePixel", "ZIndex", "LayoutOrder", "ScrollBarThickness", "DisplayOrder"}

# enum tokens
SLICE, FIT = Token(1, "Slice"), Token(3, "Fit")
BORDER, CONTEXTUAL = Token(1, "Border"), Token(0, "Contextual")
SORT_LAYOUT = Token(2, "LayoutOrder")
HORIZONTAL, VERTICAL = Token(0, "Horizontal"), Token(1, "Vertical")
H_CENTER, H_LEFT = Token(0, "Center"), Token(1, "Left")
V_CENTER = Token(0, "Center")
X_LEFT, X_CENTER = Token(0, "Left"), Token(2, "Center")
Y_CENTER = Token(1, "Center")
LUCKY, FREDOKA = Font("LuckiestGuy"), Font("FredokaOne")


class N:
    def __init__(self, cls, name, props=None, children=(), attrs=None):
        self.cls, self.name = cls, name
        self.props = dict(props or {})
        self.children = list(children)
        self.attrs = dict(attrs or {})

    def add(self, *kids):
        self.children.extend(kids)
        return self


# ---------------------------------------------------------------- style helpers
def corner(px=12, scale=0.0):
    return N("UICorner", "UICorner", {"CornerRadius": UDim(scale, px)})


def stroke(th=4, col=fd.OUTLINE, mode=BORDER):
    return N("UIStroke", "UIStroke", {"Color": Color(col), "Thickness": float(th), "ApplyStrokeMode": mode,
                                      "LineJoinMode": Token(0, "Round"), "Transparency": 0.0})


def gradient(c0, c1, rot=90.0):
    return N("UIGradient", "UIGradient", {"Color": ColorSeq([(0, c0), (1, c1)]), "Rotation": float(rot)})


def padding(t, l=None, r=None, b=None):
    l, r, b = (t if v is None else v for v in (l, r, b))
    return N("UIPadding", "UIPadding", {"PaddingTop": UDim(0, t), "PaddingLeft": UDim(0, l),
                                        "PaddingRight": UDim(0, r), "PaddingBottom": UDim(0, b)})


def aspect(r=1.0):
    return N("UIAspectRatioConstraint", "UIAspectRatioConstraint", {"AspectRatio": float(r)})


def gui(pos=UDim2(0, 0, 0, 0), size=UDim2(1, 0, 1, 0), anchor=Vec2(0, 0), bg=None, bgt=1.0, z=1, **kw):
    p = {"AnchorPoint": anchor, "Position": pos, "Size": size, "BorderSizePixel": 0, "ZIndex": z,
         "BackgroundColor3": Color(bg or "#FFFFFF"), "BackgroundTransparency": float(bgt if bg is None else kw.pop("bgt2", 0.0))}
    p.update(kw)
    return p


def frame(name, kids=(), **kw):
    return N("Frame", name, gui(**kw), kids)


def image(name, png, cls="ImageLabel", scale=FIT, slice_rect=None, slice_scale=1.0, kids=(), attrs=None, tint=None, **kw):
    p = gui(**kw)
    p.update({"Image": Content(PLACEHOLDER), "ScaleType": scale, "ImageTransparency": 0.0,
              "ImageColor3": Color(tint or "#FFFFFF")})
    if slice_rect:
        p.update({"SliceCenter": Rect(*slice_rect), "SliceScale": float(slice_scale)})
    if cls == "ImageButton":
        p["AutoButtonColor"] = True
    a = {"AssetFile": png}
    a.update(attrs or {})
    return N(cls, name, p, kids, a)


def text(name, txt, font=FREDOKA, color="#FFFFFF", outline=0.0, cls="TextLabel", xalign=X_CENTER, kids=(), **kw):
    """outline > 0 adds a contextual UIStroke (outlines the glyphs); otherwise TextStroke is used."""
    p = gui(**kw)
    p.update({"Text": txt, "FontFace": font, "TextColor3": Color(color), "TextScaled": True, "TextWrapped": True,
              "TextSize": 24.0, "TextXAlignment": xalign, "TextYAlignment": Y_CENTER,
              "TextStrokeColor3": Color(fd.OUTLINE), "TextStrokeTransparency": 1.0 if outline else 0.0})
    if cls == "TextButton":
        p["AutoButtonColor"] = True
    k = list(kids)
    if outline:
        k.append(stroke(outline, mode=CONTEXTUAL))
    return N(cls, name, p, k)


BTN_SLICE, BTN_SLICE_RECT = 1.0, (40, 40, 88, 82)
SLOT_SLICE_RECT = (28, 28, 68, 68)


# ---------------------------------------------------------------- HUD
def hud_button(name, label, frame_png, order, inner):
    b = image(name, frame_png, cls="ImageButton", scale=SLICE, slice_rect=BTN_SLICE_RECT, slice_scale=BTN_SLICE,
              size=UDim2(0, 104, 0, 104), LayoutOrder=order)
    b.add(*inner)
    b.add(text("Label", label, font=LUCKY, outline=3, anchor=Vec2(0.5, 1), pos=UDim2(0.5, 0, 1, 10),
               size=UDim2(1.15, 0, 0, 30), z=5))
    return b


def hud():
    icon = lambda png, s=0.84, y=0.44: image("Icon", png, anchor=Vec2(0.5, 0.5), pos=UDim2(0.5, 0, y, 0),
                                             size=UDim2(s, 0, s, 0), z=3)
    eq_rarity = dict((n, r) for n, r in fd.all_fish())[fd.EQUIPPED]
    fish_btn = hud_button("FishButton", "FISH", "frames/button_blue.png", 1, [
        image("Slot", f"frames/slot_{eq_rarity}.png", scale=SLICE, slice_rect=SLOT_SLICE_RECT, slice_scale=0.6,
              anchor=Vec2(0.5, 0.5), pos=UDim2(0.5, 0, 0.45, 0), size=UDim2(0.7, 0, 0.7, 0), z=2),
        image("Icon", "icons/fish.png", anchor=Vec2(0.5, 0.5), pos=UDim2(0.5, 0, 0.44, 0), size=UDim2(0.82, 0, 0.82, 0),
              z=3, attrs={"Note": "swap to the equipped fish thumbnail at runtime"}),
        frame("EquippedBadge", [corner(0, 0.5), stroke(3), gradient("#8EEF6E", "#2DA83A"),
                                text("Text", "EQUIPPED", outline=2, pos=UDim2(0, 0, 0, 0), size=UDim2(1, 0, 1, 0), z=7,
                                     kids=[padding(3, 6)])],
              anchor=Vec2(0.5, 0.5), pos=UDim2(0.5, 0, 0, 0), size=UDim2(0, 88, 0, 24), bg="#FFFFFF", z=6,
              Rotation=-7.0),
    ])
    fish_btn.attrs.update({"EquippedFish": fd.EQUIPPED})
    shop_btn = hud_button("ShopButton", "SHOP", "frames/button_green.png", 2, [icon("icons/shop.png")])
    index_btn = hud_button("IndexButton", "INDEX", "frames/button_orange.png", 3, [icon("icons/index.png")])
    index_btn.attrs.update({"Opens": "IndexWindow"})
    return frame("HUDButtons", [
        N("UIListLayout", "UIListLayout", {"Padding": UDim(0, 24), "FillDirection": VERTICAL, "SortOrder": SORT_LAYOUT,
                                           "HorizontalAlignment": H_CENTER, "VerticalAlignment": V_CENTER}),
        fish_btn, shop_btn, index_btn,
    ], anchor=Vec2(0, 0.5), pos=UDim2(0, 22, 0.5, 0), size=UDim2(0, 112, 0, 380))


# ---------------------------------------------------------------- Index window
def tab(name, label, order, c0, c1, selected=False, rot=90.0):
    t = text(f"Tab_{name}", label, cls="TextButton", color=fd.OUTLINE if selected else "#FFFFFF",
             size=UDim2(0.094, 0, 1, 0), bg="#FFFFFF", LayoutOrder=order,
             kids=[corner(10), stroke(4 if selected else 3), gradient(c0, c1, rot), padding(5, 2)])
    if selected:
        t.props["TextStrokeTransparency"] = 1.0
    t.attrs = {"Filter": name, "Selected": selected}
    return t


def slot(i, name, rarity):
    found = name in fd.DISCOVERED
    sel = name == fd.SELECTED
    png = f"thumbnails/{name}.png" if found else f"thumbnails/{name}_locked.png"
    s = image(name, f"frames/slot_{rarity}.png", cls="ImageButton", scale=SLICE, slice_rect=SLOT_SLICE_RECT,
              slice_scale=0.8, LayoutOrder=i + 1, tint=None if found else "#A9AEBB",
              attrs={"FishName": name, "DisplayName": fd.display(name), "Rarity": rarity,
                     "WaterArea": fd.AREA[name], "Discovered": found})
    s.add(image("Thumbnail", png, anchor=Vec2(0.5, 0.5), pos=UDim2(0.5, 0, 0.42, 0), size=UDim2(0.96, 0, 0.78, 0), z=2,
                kids=[aspect(1)], attrs={"Unlocked": f"thumbnails/{name}.png", "Locked": f"thumbnails/{name}_locked.png"}))
    s.add(text("NameLabel", fd.display(name), color="#FFFFFF" if found else "#C9CEDA", anchor=Vec2(0.5, 1),
               pos=UDim2(0.5, 0, 1, -6), size=UDim2(0.9, 0, 0.2, 0), z=3))
    if not found:
        s.add(image("LockIcon", "icons/lock.png", anchor=Vec2(1, 0), pos=UDim2(1, -5, 0, 5), size=UDim2(0, 24, 0, 24), z=4))
    if sel:
        s.add(corner(16), stroke(4, "#FFE14D"))
    return s


def index_window():
    fish = fd.all_fish()
    found = sum(1 for n, _ in fish if n in fd.DISCOVERED)
    sel_r = dict(fish)[fd.SELECTED]
    pal = fd.PALETTE

    title = frame("TitleBar", [
        corner(16), stroke(5), gradient("#FFD34D", "#FF8A1A"),
        image("Icon", "icons/index.png", anchor=Vec2(0, 0.5), pos=UDim2(0.005, 0, 0.45, 0), size=UDim2(0.12, 0, 1.45, 0),
              z=3, kids=[aspect(1)]),
        text("Title", "FISH INDEX", font=LUCKY, outline=3.5, xalign=X_LEFT, anchor=Vec2(0, 0.5),
             pos=UDim2(0.12, 0, 0.5, 0), size=UDim2(0.36, 0, 0.72, 0), z=3),
        frame("Counter", [
            corner(0, 0.5), stroke(3),
            frame("Fill", [corner(0, 0.5), gradient("#8EEF6E", "#2DA83A")], size=UDim2(found / len(fish), 0, 1, 0),
                  bg="#FFFFFF", z=2),
            text("Text", f"{found}/{len(fish)} Discovered", outline=2, size=UDim2(1, 0, 1, 0), z=3, kids=[padding(5, 10)]),
        ], anchor=Vec2(0, 0.5), pos=UDim2(0.49, 0, 0.5, 0), size=UDim2(0.37, 0, 0.6, 0), bg=fd.OUTLINE, bgt2=0.25),
        image("CloseButton", "icons/close.png", cls="ImageButton", anchor=Vec2(1, 0.5), pos=UDim2(1, 8, 0.5, 0),
              size=UDim2(0.11, 0, 1.3, 0), z=4, kids=[aspect(1)], attrs={"Closes": "IndexWindow"}),
    ], pos=UDim2(0.015, 0, 0.03, 0), size=UDim2(0.97, 0, 0.13, 0), bg="#FFFFFF", z=2)

    tabs = frame("Tabs", [
        N("UIListLayout", "UIListLayout", {"Padding": UDim(0.0066, 0), "FillDirection": HORIZONTAL, "SortOrder": SORT_LAYOUT,
                                           "HorizontalAlignment": H_LEFT, "VerticalAlignment": V_CENTER}),
        tab("All", "All", 0, "#FFFFFF", "#C9D6E6", selected=True),
    ] + [tab(r, r, i + 1, pal[r][1], pal[r][2], rot=0.0 if r == "Celestial" else 90.0)
         for i, r in enumerate(fd.RARITIES)],
        pos=UDim2(0.015, 0, 0.195, 0), size=UDim2(0.97, 0, 0.07, 0))

    grid = N("ScrollingFrame", "Grid", gui(pos=UDim2(0.015, 0, 0.3, 0), size=UDim2(0.6, 0, 0.67, 0), bg="#E4F2FF", z=2,
                                           CanvasSize=UDim2(0, 0, 0, 0), AutomaticCanvasSize=Token(2, "Y"),
                                           ScrollingDirection=Token(2, "Y"), ScrollBarThickness=8,
                                           ScrollBarImageColor3=Color(fd.OUTLINE), VerticalScrollBarInset=Token(1, "ScrollBar"),
                                           ClipsDescendants=True, Active=True), [
        corner(14), stroke(4), padding(10),
        N("UIGridLayout", "UIGridLayout", {"CellSize": UDim2(0, 82, 0, 100), "CellPadding": UDim2(0, 8, 0, 8),
                                           "SortOrder": SORT_LAYOUT, "FillDirection": HORIZONTAL,
                                           "HorizontalAlignment": H_CENTER, "VerticalAlignment": Token(1, "Top")}),
    ] + [slot(i, n, r) for i, (n, r) in enumerate(fish)])

    details = frame("Details", [
        corner(14), stroke(4), padding(10), gradient("#FFFFFF", "#FFEFD0"),
        image("ThumbFrame", f"frames/slot_{sel_r}.png", scale=SLICE, slice_rect=SLOT_SLICE_RECT, slice_scale=1.0,
              size=UDim2(1, 0, 0.5, 0), z=2, kids=[
                  image("BigThumbnail", f"thumbnails/{fd.SELECTED}.png", anchor=Vec2(0.5, 0.5), pos=UDim2(0.5, 0, 0.5, 0),
                        size=UDim2(0.92, 0, 0.92, 0), z=3)]),
        text("FishName", fd.display(fd.SELECTED), font=LUCKY, outline=3, pos=UDim2(0, 0, 0.52, 0),
             size=UDim2(1, 0, 0.13, 0), z=2),
        frame("RarityPill", [corner(0, 0.5), stroke(3), gradient(pal[sel_r][1], pal[sel_r][2]),
                             text("Text", sel_r.upper(), outline=2, size=UDim2(1, 0, 1, 0), z=3, kids=[padding(3, 8)])],
              anchor=Vec2(0.5, 0), pos=UDim2(0.5, 0, 0.665, 0), size=UDim2(0.55, 0, 0.1, 0), bg="#FFFFFF", z=2),
        frame("WaterArea", [corner(12), stroke(3), gradient("#CDEBFF", "#9ED2FF"), padding(4, 8),
                            text("Heading", "WATER AREA", color="#2A5E9E", size=UDim2(1, 0, 0.4, 0), z=3),
                            text("Value", fd.AREA[fd.SELECTED], outline=2, pos=UDim2(0, 0, 0.4, 0),
                                 size=UDim2(1, 0, 0.6, 0), z=3)],
              pos=UDim2(0, 0, 0.8, 0), size=UDim2(1, 0, 0.2, 0), bg="#FFFFFF", z=2),
    ], pos=UDim2(0.63, 0, 0.3, 0), size=UDim2(0.355, 0, 0.67, 0), bg="#FFFFFF", z=2)
    details.attrs = {"SelectedFish": fd.SELECTED}

    panel = frame("Panel", [corner(22), stroke(6), gradient("#5BC0FF", "#2A72DD"), title, tabs, grid, details],
                  bg="#FFFFFF", z=2)
    shadow = frame("Shadow", [corner(22)], pos=UDim2(0, 0, 0, 10), bg="#000000", bgt2=0.6, z=1)
    win = frame("IndexWindow", [aspect(1.62), shadow, panel], anchor=Vec2(0.5, 0.5), pos=UDim2(0.5, 0, 0.5, 0),
                size=UDim2(0.66, 0, 0.82, 0), z=5)
    win.attrs = {"StartsHidden": True}
    return win


def build_tree():
    return N("ScreenGui", "FishingUI", {"ResetOnSpawn": False, "ZIndexBehavior": Token(1, "Sibling"),
                                         "IgnoreGuiInset": False, "DisplayOrder": 0, "Enabled": True},
             [hud(), index_window()])


# ---------------------------------------------------------------- rbxmx writer
def attr_blob(attrs):
    out = struct.pack("<I", len(attrs))
    for k, v in attrs.items():
        kb = k.encode()
        out += struct.pack("<I", len(kb)) + kb
        if isinstance(v, bool):
            out += b"\x03" + (b"\x01" if v else b"\x00")
        else:
            vb = str(v).encode()
            out += b"\x02" + struct.pack("<I", len(vb)) + vb
    return base64.b64encode(out).decode()


def fmt(x):
    s = f"{float(x):.6g}"
    return s


def prop_xml(k, v):
    if k in INT_PROPS:
        return f'<int name="{k}">{int(v)}</int>'
    if isinstance(v, bool):
        return f'<bool name="{k}">{"true" if v else "false"}</bool>'
    if isinstance(v, Token):
        return f'<token name="{k}">{v.value}</token>'
    if isinstance(v, UDim2):
        return f'<UDim2 name="{k}"><XS>{fmt(v[0])}</XS><XO>{int(v[1])}</XO><YS>{fmt(v[2])}</YS><YO>{int(v[3])}</YO></UDim2>'
    if isinstance(v, UDim):
        return f'<UDim name="{k}"><S>{fmt(v[0])}</S><O>{int(v[1])}</O></UDim>'
    if isinstance(v, Vec2):
        return f'<Vector2 name="{k}"><X>{fmt(v[0])}</X><Y>{fmt(v[1])}</Y></Vector2>'
    if isinstance(v, Rect):
        return (f'<Rect2D name="{k}"><min><X>{fmt(v[0])}</X><Y>{fmt(v[1])}</Y></min>'
                f'<max><X>{fmt(v[2])}</X><Y>{fmt(v[3])}</Y></max></Rect2D>')
    if isinstance(v, Color):
        return f'<Color3 name="{k}"><R>{fmt(v[0])}</R><G>{fmt(v[1])}</G><B>{fmt(v[2])}</B></Color3>'
    if isinstance(v, Font):
        return (f'<Font name="{k}"><Family><url>rbxasset://fonts/families/{v.family}.json</url></Family>'
                f'<Weight>400</Weight><Style>Normal</Style></Font>')
    if isinstance(v, ColorSeq):
        parts = []
        for t, h in v:
            c = Color(h)
            parts.append(f"{fmt(t)} {fmt(c[0])} {fmt(c[1])} {fmt(c[2])} 0")
        return f'<ColorSequence name="{k}">{" ".join(parts)} </ColorSequence>'
    if isinstance(v, NumSeq):
        return f'<NumberSequence name="{k}">{" ".join(f"{fmt(t)} {fmt(x)} 0" for t, x in v)} </NumberSequence>'
    if isinstance(v, Content):
        return f'<Content name="{k}"><url>{escape(v)}</url></Content>'
    if isinstance(v, str):
        return f'<string name="{k}">{escape(v)}</string>'
    if isinstance(v, (int, float)):
        return f'<float name="{k}">{fmt(v)}</float>'
    raise TypeError(k, v)


def item_xml(node, path, lines, depth, amap):
    ref = "RBX" + hashlib.md5(path.encode()).hexdigest().upper()
    ind = "\t" * depth
    lines.append(f'{ind}<Item class="{node.cls}" referent="{ref}">')
    lines.append(f"{ind}\t<Properties>")
    lines.append(f'{ind}\t\t<string name="Name">{escape(node.name)}</string>')
    for k, v in node.props.items():
        lines.append(f"{ind}\t\t{prop_xml(k, v)}")
    if node.attrs:
        lines.append(f'{ind}\t\t<BinaryString name="AttributesSerialize">{attr_blob(node.attrs)}</BinaryString>')
    lines.append(f"{ind}\t</Properties>")
    if "AssetFile" in node.attrs:
        amap.setdefault(node.attrs["AssetFile"], []).append(path)
    names = set()
    for ch in node.children:
        assert (ch.name, ch.cls) not in names or ch.cls.startswith("UI"), f"duplicate {path}.{ch.name}"
        names.add((ch.name, ch.cls))
        item_xml(ch, f"{path}.{ch.name}", lines, depth + 1, amap)
    lines.append(f"{ind}</Item>")


def write(ui):
    tree = build_tree()
    lines = ['<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" '
             'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
             'xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">',
             "\t<External>null</External>", "\t<External>nil</External>"]
    amap = {}
    item_xml(tree, f"StarterGui.{tree.name}", lines, 1, amap)
    lines.append("</roblox>")
    out = os.path.join(ui, "FishingUI.rbxmx")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    # every PNG in ui/ gets a key, even when no static instance uses it (runtime swaps)
    full = {}
    for sub in ("icons", "frames", "thumbnails"):
        d = os.path.join(ui, sub)
        for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if fn.endswith(".png"):
                full[f"{sub}/{fn}"] = sorted(amap.get(f"{sub}/{fn}", []))
    missing = sorted(set(amap) - set(full))
    assert not missing, f"layout references missing PNGs: {missing}"
    with open(os.path.join(ui, "asset_map.json"), "w") as f:
        json.dump(full, f, indent=2)
        f.write("\n")
    root = ET.parse(out).getroot()
    n_items = len(root.findall(".//Item"))
    refs = [e.get("referent") for e in root.iter("Item")]
    assert len(set(refs)) == len(refs), "duplicate referents"
    classes = sorted({e.get("class") for e in root.iter("Item")})
    print(f"wrote {out}: well-formed, {n_items} instances, classes {classes}")
    print(f"asset_map.json: {len(full)} PNGs, {sum(len(v) for v in full.values())} image instances")
    return tree


if __name__ == "__main__":
    write(sys.argv[1] if len(sys.argv) > 1 else "ui")
