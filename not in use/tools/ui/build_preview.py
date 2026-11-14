"""Render the build_rbxmx.py layout tree to an HTML mock-up and screenshot it.

    python3 tools/ui/build_preview.py [ui] [--fonts DIR_WITH_WOFF2]

Writes ui/preview/mockup.html (open it directly; add #hud to hide the Index window),
then runs tools/ui/screenshot.js (Node + Playwright) for ui/preview/hud.png and index.png.
A tiny layout engine mirrors Roblox rules: UDim2 + AnchorPoint, UIPadding, UIListLayout,
UIGridLayout, UIAspectRatioConstraint (FitWithinMaxSize), UICorner, UIStroke, UIGradient,
9-slice (border-image) and Fit images. TextScaled is fitted in the browser.
"""
import base64
import html
import math
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_rbxmx as B  # noqa: E402
import fishdata as fd  # noqa: E402

W, H = 1280, 720
UI = "ui"


def kid(node, cls):
    return next((c for c in node.children if c.cls == cls), None)


def rgba(col, a=1.0):
    return f"rgba({round(col[0] * 255)},{round(col[1] * 255)},{round(col[2] * 255)},{a:.3f})"


def mul(c, h):
    d = B.Color(h)
    return (c[0] * d[0], c[1] * d[1], c[2] * d[2])


def size_of(node, cw, ch):
    s = node.props.get("Size", B.UDim2(0, 100, 0, 100))
    w, h = s[0] * cw + s[1], s[2] * ch + s[3]
    ar = kid(node, "UIAspectRatioConstraint")
    if ar:
        r = ar.props["AspectRatio"]
        if w / max(h, 1e-6) > r:
            w = h * r
        else:
            h = w / r
    return w, h


def pad_of(node):
    p = kid(node, "UIPadding")
    if not p:
        return 0, 0, 0, 0
    g = lambda k: p.props[k][1]
    return g("PaddingLeft"), g("PaddingTop"), g("PaddingRight"), g("PaddingBottom")


def text_shadow(col, r):
    n = 16 if r > 1.5 else 8
    return ",".join(f"{r * math.cos(2 * math.pi * i / n):.2f}px {r * math.sin(2 * math.pi * i / n):.2f}px 0 {col}"
                    for i in range(n))


def style(node, w, h):
    p, st = node.props, []
    grad, cor, strk = kid(node, "UIGradient"), kid(node, "UICorner"), kid(node, "UIStroke")
    bgt = p.get("BackgroundTransparency", 1.0)
    if bgt < 1:
        bg = p["BackgroundColor3"]
        if grad:
            (t0, c0), (t1, c1) = grad.props["Color"][0], grad.props["Color"][-1]
            ang = grad.props["Rotation"] + 90
            st.append(f"background:linear-gradient({ang}deg,{rgba(mul(bg, c0), 1 - bgt)},{rgba(mul(bg, c1), 1 - bgt)})")
        else:
            st.append(f"background:{rgba(bg, 1 - bgt)}")
    if cor:
        s, o = cor.props["CornerRadius"]
        st.append(f"border-radius:{s * min(w, h) + o:.1f}px")
    if strk and strk.props["ApplyStrokeMode"].value == 1:
        st.append(f"box-shadow:0 0 0 {strk.props['Thickness']}px {rgba(strk.props['Color'])}")
    if "Rotation" in p and p["Rotation"]:
        st.append(f"transform:rotate({p['Rotation']}deg)")
    if "AssetFile" in node.attrs and "Image" in p:
        png = node.attrs["AssetFile"]
        url = f"../{png}"
        if p["ScaleType"].value == 1:
            iw, ih = Image.open(os.path.join(UI, png)).size
            x0, y0, x1, y1 = p["SliceCenter"]
            k = p.get("SliceScale", 1.0)
            sl = [y0, iw - x1, ih - y1, x0]
            # drawn on an inner layer so the border widths don't shift the children
            node._slice = (f"border-style:solid;border-width:{' '.join(f'{v * k:.1f}px' for v in sl)};"
                           f"border-image:url('{url}') {' '.join(str(int(v)) for v in sl)} fill stretch")
        else:
            st.append(f"background-image:url('{url}');background-size:contain;background-repeat:no-repeat;"
                      f"background-position:center")
        tint = p.get("ImageColor3")
        if tint and tint != (1.0, 1.0, 1.0):
            f = f"filter:brightness({sum(tint) / 3:.2f}) saturate(0.8)"
            if getattr(node, "_slice", None):
                node._slice += ";" + f
            else:
                st.append(f)
    if "Text" in p:
        fam = "Luckiest Guy" if p["FontFace"].family == "LuckiestGuy" else "Fredoka One"
        jx = {0: "flex-start", 1: "flex-end", 2: "center"}[p["TextXAlignment"].value]
        st.append(f"display:flex;align-items:center;justify-content:{jx};text-align:{'left' if jx == 'flex-start' else 'center'};"
                  f"font-family:'{fam}';color:{rgba(p['TextColor3'])};line-height:1.05")
        pl, pt, pr, pb = pad_of(node)
        st.append(f"padding:{pt}px {pr}px {pb}px {pl}px")
        if strk and strk.props["ApplyStrokeMode"].value == 0:
            st.append(f"text-shadow:{text_shadow(rgba(strk.props['Color']), strk.props['Thickness'])}")
        elif p.get("TextStrokeTransparency", 1) < 1:
            st.append(f"text-shadow:{text_shadow(rgba(p['TextStrokeColor3']), 1.2)}")
    return st


def emit(node, x, y, w, h, out):
    p = node.props
    if p.get("Visible", True) is False:
        return
    st = [f"left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;height:{h:.1f}px;z-index:{p.get('ZIndex', 1)}"] + style(node, w, h)
    scroll = node.cls == "ScrollingFrame"
    if scroll:
        st.append("overflow:hidden")
    attrs = ' data-fit="1"' if "Text" in p else ""
    out.append(f'<div class="g" data-name="{html.escape(node.name)}" style="{";".join(st)}"{attrs}>')
    if getattr(node, "_slice", None):
        out.append(f'<div class="g" style="left:0;top:0;width:100%;height:100%;z-index:0;{node._slice}"></div>')
    if "Text" in p:
        out.append(f"<span>{html.escape(p['Text'])}</span>")
    pl, pt, pr, pb = pad_of(node)
    cx, cy, cw, ch = pl, pt, w - pl - pr, h - pt - pb
    if scroll:
        cw -= p.get("ScrollBarThickness", 0)
    kids = [c for c in node.children if not c.cls.startswith("UI")]
    lst, grid = kid(node, "UIListLayout"), kid(node, "UIGridLayout")
    if lst or grid:
        kids.sort(key=lambda c: c.props.get("LayoutOrder", 0))
    content_bottom = 0
    if lst:
        vert = lst.props["FillDirection"].value == 1
        pad = lst.props["Padding"][0] * (ch if vert else cw) + lst.props["Padding"][1]
        sizes = [size_of(c, cw, ch) for c in kids]
        if vert:
            tot = sum(s[1] for s in sizes) + pad * (len(sizes) - 1)
            yy = cy + (ch - tot) / 2
            for c, (cw_, ch_) in zip(kids, sizes):
                emit(c, cx + (cw - cw_) / 2, yy, cw_, ch_, out)
                yy += ch_ + pad
        else:
            xx = cx
            for c, (cw_, ch_) in zip(kids, sizes):
                emit(c, xx, cy + (ch - ch_) / 2, cw_, ch_, out)
                xx += cw_ + pad
    elif grid:
        cs, cp = grid.props["CellSize"], grid.props["CellPadding"]
        gw, gh = cs[0] * cw + cs[1], cs[2] * ch + cs[3]
        px, py = cp[0] * cw + cp[1], cp[2] * ch + cp[3]
        cols = max(1, int((cw + px) // (gw + px)))
        x0 = cx + (cw - (cols * gw + (cols - 1) * px)) / 2
        for i, c in enumerate(kids):
            r, k = divmod(i, cols)
            emit(c, x0 + k * (gw + px), cy + r * (gh + py), gw, gh, out)
        rows = (len(kids) + cols - 1) // cols
        content_bottom = cy + rows * (gh + py) - py + pb
    else:
        for c in kids:
            cw_, ch_ = size_of(c, cw, ch)
            pos, an = c.props.get("Position", B.UDim2(0, 0, 0, 0)), c.props.get("AnchorPoint", B.Vec2(0, 0))
            emit(c, cx + pos[0] * cw + pos[1] - an[0] * cw_, cy + pos[2] * ch + pos[3] - an[1] * ch_, cw_, ch_, out)
    if scroll and content_bottom > h:
        th = p.get("ScrollBarThickness", 8)
        bar = h * h / content_bottom
        out.append(f'<div class="g" style="right:2px;top:4px;width:{th}px;height:{bar:.0f}px;border-radius:{th}px;'
                   f'background:{rgba(p["ScrollBarImageColor3"], 0.8)};z-index:50"></div>')
    out.append("</div>")


def font_css(fonts):
    css = []
    for fam, fn in (("Fredoka One", "FredokaOne.woff2"), ("Luckiest Guy", "LuckiestGuy.woff2")):
        path = os.path.join(fonts or "", fn)
        if fonts and os.path.exists(path):
            b64 = base64.b64encode(open(path, "rb").read()).decode()
            css.append(f"@font-face{{font-family:'{fam}';src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    if not css:
        return '<link href="https://fonts.googleapis.com/css2?family=Fredoka+One&family=Luckiest+Guy&display=block" rel="stylesheet">'
    return "<style>" + "".join(css) + "</style>"


FIT_JS = """
function fitAll(){
  document.querySelectorAll('[data-fit]').forEach(el=>{
    let lo=4, hi=Math.max(6, el.clientHeight);
    while(hi-lo>0.5){ const m=(lo+hi)/2; el.style.fontSize=m+'px';
      (el.scrollWidth<=el.clientWidth+0.5 && el.scrollHeight<=el.clientHeight+0.5) ? lo=m : hi=m; }
    el.style.fontSize=lo+'px';
  });
  document.body.dataset.ready='1';
}
function applyHash(){ const w=document.querySelector('[data-name="IndexWindow"]');
  if(w) w.style.display = location.hash==='#hud' ? 'none' : ''; }
window.addEventListener('hashchange', applyHash);
document.fonts.ready.then(()=>{ applyHash(); fitAll(); });
"""


def build(ui, fonts):
    tree = B.build_tree()
    out = []
    for c in tree.children:
        cw_, ch_ = size_of(c, W, H)
        pos, an = c.props["Position"], c.props["AnchorPoint"]
        emit(c, pos[0] * W + pos[1] - an[0] * cw_, pos[2] * H + pos[3] - an[1] * ch_, cw_, ch_, out)
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>Fishing UI mock-up</title>
{font_css(fonts)}
<style>
html,body{{margin:0;background:#1A6FC4}}
#screen{{position:relative;width:{W}px;height:{H}px;overflow:hidden;
 background:
  radial-gradient(ellipse 340px 60px at 300px 180px, rgba(255,255,255,.18), transparent 70%),
  radial-gradient(ellipse 420px 70px at 980px 520px, rgba(255,255,255,.14), transparent 70%),
  radial-gradient(ellipse 260px 40px at 760px 120px, rgba(255,255,255,.16), transparent 70%),
  repeating-linear-gradient(170deg, rgba(255,255,255,0) 0 46px, rgba(255,255,255,.07) 46px 52px),
  linear-gradient(180deg,#69D6FF 0%,#2E9BE8 45%,#1764B8 100%)}}
.g{{position:absolute;box-sizing:border-box}}
.g span{{display:block}}
</style></head><body><div id="screen">
<!-- generated from tools/ui/build_rbxmx.py by tools/ui/build_preview.py -->
{chr(10).join(out)}
</div><script>{FIT_JS}</script></body></html>"""
    d = os.path.join(ui, "preview")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "mockup.html")
    with open(path, "w") as f:
        f.write(page)
    print("wrote", path)
    return path


if __name__ == "__main__":
    args = sys.argv[1:]
    fonts = None
    if "--fonts" in args:
        i = args.index("--fonts")
        fonts = args[i + 1]
        del args[i:i + 2]
    UI = args[0] if args else "ui"
    page = build(UI, fonts)
    subprocess.run(["node", os.path.join(HERE, "screenshot.js"), os.path.abspath(page),
                    os.path.abspath(os.path.join(UI, "preview"))], check=True)
