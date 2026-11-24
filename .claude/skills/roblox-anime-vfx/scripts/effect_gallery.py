"""Build the effects review page: every rendered move as a video card, filterable by element.

    python3 effect_gallery.py OUT_DIR [--renders ../lab/out]

Writes OUT_DIR/index.html and OUT_DIR/files.json (published path -> source file) for publishing as an artifact.
"""
import os
import sys
import json
import glob
import html
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ELEMENTS = ["Flame", "Magma", "Light", "Quake", "Ice", "Dark", "Thunder", "Haki", "Blade", "Water"]
SWATCH = {"Flame": "#ff7a2a", "Magma": "#e2401a", "Light": "#ffcf3a", "Quake": "#2fe0b4", "Ice": "#6cc4ff", "Dark": "#9a5cff",
          "Thunder": "#4a9cff", "Haki": "#ff2a48", "Blade": "#8fc4ff", "Water": "#2a9cff"}
ARCH = {"projectile": "Projectile", "beam": "Beam", "slam": "Slam", "eruption": "Eruption", "slash": "Slash combo", "dash": "Dash",
        "barrage": "Barrage", "aura": "Aura / power-up", "vortex": "Vortex", "finisher": "Finisher"}

CSS = """
/* Layout: dark arcade-cabinet wall of move cards; element chips filter; videos play when on screen */
:root { --bg:#0e1016; --panel:#161922; --line:#262b38; --fg:#eceef5; --muted:#9aa1b5; --accent:#ffb02a;
  --display:"Chakra Petch","Segoe UI",system-ui,sans-serif; --body:"Inter",system-ui,sans-serif; --mono:"JetBrains Mono",ui-monospace,monospace;
  color-scheme:dark; }
body { background:var(--bg); color:var(--fg); font-family:var(--body); line-height:1.5; }
.wrap { max-width:1280px; margin:0 auto; padding-block:28px 64px; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); }
h1 { font-family:var(--display); font-size:2rem; margin:0 0 6px; letter-spacing:.02em; text-wrap:balance; }
.lede { color:var(--muted); max-width:72ch; margin:0 0 16px; }
.rules { display:flex; flex-wrap:wrap; gap:8px; margin:0 0 18px; padding:0; list-style:none; }
.rules li { font-size:.8rem; border:1px solid var(--line); border-radius:4px; padding:3px 8px; color:var(--muted); }
.rules b { color:var(--fg); font-weight:600; }
.filters { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:22px; }
.filters button { font:600 .82rem var(--display); letter-spacing:.06em; text-transform:uppercase; color:var(--fg); background:var(--panel);
  border:1px solid var(--line); border-radius:4px; padding:5px 10px; cursor:pointer; display:flex; align-items:center; gap:6px; }
.filters button[aria-pressed="true"] { border-color:var(--accent); color:var(--accent); }
.filters button:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
.dot { width:9px; height:9px; border-radius:50%; display:inline-block; }
h2 { font-family:var(--display); font-size:1.1rem; text-transform:uppercase; letter-spacing:.12em; margin:30px 0 12px; display:flex; align-items:center; gap:8px; }
.grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(min(100%, 290px), 1fr)); gap:14px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:7px; overflow:hidden; min-width:0; display:flex; flex-direction:column; }
.card video { display:block; width:100%; aspect-ratio:16/9; height:auto; background:#000; max-width:100%; }
.meta { padding:9px 12px 11px; display:flex; justify-content:space-between; align-items:baseline; gap:8px; flex-wrap:wrap; }
.title { font-weight:600; }
.arch { font-size:.74rem; color:var(--muted); font-family:var(--mono); }
.name { font-size:.7rem; color:var(--muted); font-family:var(--mono); padding:0 12px 10px; overflow-wrap:anywhere; }
@media (prefers-reduced-motion: reduce) { .card video { } }
"""

JS = """
const vids = [...document.querySelectorAll('video')];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const io = new IntersectionObserver((es) => es.forEach((e) => {
  const v = e.target;
  if (e.isIntersecting && !reduce) { v.play().catch(() => {}); } else { v.pause(); }
}), { threshold: 0.35 });
vids.forEach((v) => io.observe(v));
const buttons = [...document.querySelectorAll('.filters button')];
function show(el) {
  buttons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.el === el)));
  document.querySelectorAll('section[data-el]').forEach((s) => { s.hidden = el !== 'All' && s.dataset.el !== el; });
  try { localStorage.setItem('vfx-filter', el); } catch (e) {}
}
buttons.forEach((b) => b.addEventListener('click', () => show(b.dataset.el)));
let start = 'All'; try { start = localStorage.getItem('vfx-filter') || 'All'; } catch (e) {}
show(start);
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--renders", default=os.path.join(HERE, "..", "lab", "out"))
    ap.add_argument("--effects", default=os.path.join(HERE, "..", "lab", "effects"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    specs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(a.effects, "*.json")))]
    files, secs = {}, []
    for el in ELEMENTS:
        cards = []
        for s in [x for x in specs if x["element"] == el]:
            n = s["name"]
            mp4, poster = os.path.join(a.renders, n + ".mp4"), os.path.join(a.renders, n + "_poster.jpg")
            if not os.path.exists(mp4):
                continue
            files[f"v/{n}.mp4"] = os.path.abspath(mp4)
            files[f"p/{n}.jpg"] = os.path.abspath(poster)
            cards.append(f'<article class="card"><video src="v/{n}.mp4" poster="p/{n}.jpg" muted loop playsinline preload="none" '
                         f'aria-label="{html.escape(s["title"])} preview"></video><div class="meta"><span class="title">{html.escape(s["title"])}</span>'
                         f'<span class="arch">{ARCH[s["archetype"]]}</span></div><div class="name">{n}</div></article>')
        secs.append(f'<section data-el="{el}"><h2><span class="dot" style="background:{SWATCH[el]}"></span>{el}</h2><div class="grid">{"".join(cards)}</div></section>')
    btns = '<button type="button" data-el="All" aria-pressed="true">All 100</button>' + "".join(
        f'<button type="button" data-el="{e}" aria-pressed="false"><span class="dot" style="background:{SWATCH[e]}"></span>{e}</button>' for e in ELEMENTS)
    page = ('<title>RELL-Style Move Library</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700&family=Inter:wght@400;600&family=JetBrains+Mono&display=swap">\n'
            f'<style>{CSS}</style>\n<div class="wrap">\n<h1>RELL-Style Move Library</h1>\n'
            '<p class="lede">100 anime moves, 10 elements by 10 move types, rendered headlessly from the same data the Roblox runtime plays. '
            'Each element uses its own painted greyscale textures, tinted per move. Videos play when they scroll into view.</p>\n'
            '<ul class="rules"><li><b>Anticipation</b> wind-up, inward charge, orb pinch</li><li><b>Squash &amp; stretch</b> stretched projectiles, squashing hits</li>'
            '<li><b>Follow-through</b> lagging trails, burst flies on, caster settles</li><li><b>Timing</b> hit-stop on every hit</li>'
            '<li><b>Arcs</b> curved paths, falling sparks, arcing numbers</li></ul>\n'
            f'<div class="filters" role="group" aria-label="Filter by element">{btns}</div>\n{"".join(secs)}\n</div>\n<script>{JS}</script>')
    open(os.path.join(a.out, "index.html"), "w").write(page)
    json.dump(files, open(os.path.join(a.out, "files.json"), "w"))
    total = sum(os.path.getsize(p) for p in files.values())
    print(f"{len(files) // 2} cards, {len(files)} files, {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
