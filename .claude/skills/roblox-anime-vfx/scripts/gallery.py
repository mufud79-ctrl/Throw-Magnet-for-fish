"""Build a texture-review gallery page (HTML) from the library, for approval rounds.

    /tmp/bpyenv/bin/python gallery.py OUT_DIR

Writes OUT_DIR/index.html and OUT_DIR/files.json (published path -> source file), ready to publish as an
artifact with `files`. Run vfx_textures.py and texture_preview.py first.
"""
import os, sys, json, html, inspect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vfx_textures as v

GROUPS = [("Fire", ["fire_burst", "flame_lick", "aura_wisp", "embers"]), ("Smoke & dust", ["smoke_puff", "dust_burst"]),
          ("Flash & light", ["star_flash", "god_rays", "orb_glow", "flecks"]),
          ("Energy", ["slash", "shock_ring", "wind_arcs", "beam_strip", "speedlines"]),
          ("Quake & lightning", ["crack_glow", "glass_shatter", "lightning"]),
          ("Mesh strips", ["slash_strip", "energy_strip", "edge_strip", "wind_strip"]),
          ("Hero silhouettes (Figma image gen)", ["dragon_head", "phoenix_wing", "giant_fist", "water_shark", "palm_strike"])]
KIND = {"layered": "4 stacked layers", "shaded": "1 shaded texture", "white": "1 white texture", "strip": "1 shaded mesh strip"}
GRID = {0: "strip / full-screen", 1: "single image", 2: "2×2 sheet", 4: "4×4 flipbook, 16 frames"}
CSS = """
/* Layout: a dark VFX-lab light table; cards in a responsive grid so effects glow like they do in game */
:root { --bg:#0f1117; --panel:#171a23; --line:#262b38; --fg:#e8eaf2; --muted:#9aa1b5; --accent:#ff9a2e;
  --display:"Chakra Petch", "Segoe UI", system-ui, sans-serif; --body:"Inter", system-ui, sans-serif;
  --mono:"JetBrains Mono", ui-monospace, monospace; color-scheme:dark; }
body { background:var(--bg); color:var(--fg); font-family:var(--body); line-height:1.5; }
.wrap { max-width:1180px; margin:0 auto; padding-block:28px 64px; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); }
h1 { font-family:var(--display); font-size:2rem; margin:0 0 6px; letter-spacing:.02em; text-wrap:balance; }
.lede { color:var(--muted); max-width:68ch; margin:0 0 14px; }
nav { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:28px; }
nav a { font-family:var(--mono); font-size:.78rem; color:var(--fg); text-decoration:none; border:1px solid var(--line); border-radius:4px; padding:3px 8px; }
nav a:hover, nav a:focus-visible { border-color:var(--accent); color:var(--accent); outline:none; }
h2 { font-family:var(--display); font-size:1.15rem; text-transform:uppercase; letter-spacing:.12em; color:var(--accent); margin:36px 0 14px; }
.cards { display:grid; grid-template-columns:repeat(auto-fill, minmax(min(100%, 360px), 1fr)); gap:16px; }
.tex { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px; display:flex; flex-direction:column; gap:10px; min-width:0; }
.tex header { display:flex; flex-wrap:wrap; align-items:baseline; justify-content:space-between; gap:4px 12px; }
h3 { font-family:var(--mono); font-size:1.05rem; margin:0; color:var(--fg); }
.meta { margin:0; font-size:.78rem; color:var(--muted); letter-spacing:.03em; }
.new { font-family:var(--mono); font-size:.7rem; color:var(--bg); background:var(--accent); border-radius:3px; padding:1px 6px; margin-left:8px; vertical-align:middle; }
.doc { margin:0; font-size:.88rem; color:var(--muted); }
.views { display:flex; flex-wrap:wrap; gap:10px; }
figure { margin:0; display:flex; flex-direction:column; gap:4px; min-width:0; }
figure img { display:block; width:100%; height:auto; border-radius:5px; background:#14161d; }
.anim { flex:1 1 150px; } .sheet { flex:2 1 180px; }
figcaption { font-size:.72rem; color:var(--muted); font-family:var(--mono); overflow-wrap:anywhere; }
details summary { cursor:pointer; font-size:.8rem; color:var(--muted); }
details summary:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
.raws { display:grid; grid-template-columns:repeat(auto-fill, minmax(110px, 1fr)); gap:8px; margin-top:8px; }
.raw img { background:repeating-conic-gradient(#1d212c 0 25%, #12141b 0 50%) 0 0/16px 16px; }
"""


def build(out, lede, updated=()):
    A = os.path.abspath(os.path.join(v.HERE, "..", "assets"))
    files, secs = {}, []
    for gname, names in GROUPS:
        cards = []
        for nm in names:
            fn, kind, grid, _, _ = v.LIB[nm]
            doc = " ".join(inspect.getdoc(fn).split("\n\n")[0].split())
            prev = f"previews/{nm}.png"; files[prev] = os.path.join(A, prev)
            anim = ""
            if grid == 4:
                g = f"previews/{nm}.gif"; files[g] = os.path.join(A, g)
                anim = f'<figure class="anim"><img src="{g}" alt="{nm} flipbook playing" loading="lazy"><figcaption>Playing</figcaption></figure>'
            raws = [f"{nm}_{L}.png" for L in ("glow", "rim", "mid", "core")] if kind == "layered" else [f"{nm}.png"]
            rawhtml = ""
            for r in raws:
                files["textures/" + r] = os.path.join(A, "textures", r)
                rawhtml += f'<figure class="raw"><img src="textures/{r}" alt="{r}" loading="lazy"><figcaption>{r}</figcaption></figure>'
            badge = '<span class="new">updated</span>' if nm in updated else ""
            cards.append(f'<article class="tex" id="{nm}"><header><h3>{nm}{badge}</h3><p class="meta">{GRID[grid]} · {KIND[kind]}</p></header>'
                         f'<p class="doc">{html.escape(doc)}</p><div class="views">{anim}<figure class="sheet"><img src="{prev}" alt="{nm} tinted preview" loading="lazy">'
                         f'<figcaption>Tinted preview{" (all frames)" if grid > 1 else ""}</figcaption></figure></div>'
                         f'<details><summary>Raw files ({len(raws)})</summary><div class="raws">{rawhtml}</div></details></article>')
        secs.append(f'<section><h2>{gname}</h2><div class="cards">{"".join(cards)}</div></section>')
    nav = " ".join(f'<a href="#{n}">{n}</a>' for _, ns in GROUPS for n in ns)
    page = ('<title>Anime VFX Textures</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400&display=swap">\n'
            f'<style>{CSS}</style>\n<div class="wrap">\n<h1>Anime VFX Textures</h1>\n<p class="lede">{lede}</p>\n'
            f'<nav aria-label="Textures">{nav}</nav>\n{"".join(secs)}\n</div>')
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "index.html"), "w").write(page)
    json.dump(files, open(os.path.join(out, "files.json"), "w"), indent=0)
    return files


if __name__ == "__main__":
    out = sys.argv[1]
    upd = sys.argv[2].split(",") if len(sys.argv) > 2 else ()
    lede = ("Painted texture library, for approval. Each card shows the texture tinted and stacked the way Roblox will layer it. "
            "Flipbooks also play over a daylight backdrop. Open \"Raw files\" to see the white PNGs that get uploaded.")
    build(out, lede, upd)
