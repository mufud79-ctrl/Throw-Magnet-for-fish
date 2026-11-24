# Drawing recipes (vfx/engine/paint.js, brush engine)

Textures are painted headless with Canvas2D brush marks, like layering in Photoshop. The
preview and the uploaded PNG are identical, and layered drawings split into 4 white sheets.

## Marks (cell space x,y in [-1,1], y up)

| Mark | Use |
|---|---|
| `ribbon(pts, widths, opts)` | tapered stroke along a polyline: strands, ink crescents, rays, lines, needles |
| `poly(pts, opts)` | filled shape: blades, teeth, stars |
| `dot(x, y, r, opts)` | bubbles, glint cores, screentone dots |
| `arcPts`, `linePts`, `taper(n, w, peak, sharpness)` | centrelines and width profiles |
| `halftone(x0, y0, x1, y1, step, rf)` | manga screentone dots, radius from `rf` |

Flags: `hot` (also drawn into core at `coreW`), `coreOnly`, `glowOnly` (halo source only),
`noRim`, `a` (alpha).

Kinds: `layered` (marks → glow/rim/mid/core), `single` (white mask, optional `halo` blur),
`pixels` (soft media fn → [value, alpha]), `pixelLayers` (scalar field → 4 layers by thresholds;
used for the fire flash).

## Recipes that match the references

| Element | Recipe |
|---|---|
| Energy crescent (`strandArc`) | white body band at the cutting edge (hot) + 46–60 strands whose radial depth `q` is dense near the edge, spirals inward (`spin`), random spans, widths 0.004–0.02; flecks peel off; tail recedes over the frames |
| Black ink crescent (`inkArc`) | one ribbon whose width peaks at 0.075 toward the head, needle tips, reverse hook at the head, 3–4 inward barbs |
| Serrated blade (`sawFan`) | crescent polygon with an alternating outer radius (teeth); white tooth polys (`coreOnly`) + screentone band |
| Vortex (`swirl`) | 14–30 spiral arcs at random radii with tapered widths, rotated per frame; the same function draws the ground swirl and the ring slash |
| Glint / flare | crisp tapered rays + small core dot, with a small `glowOnly` dot and `halo` blur (keep it small or it becomes a white ball) |
| Fire flash | fbm-spiked radial field via `pixelLayers`; keep the glow threshold above −0.3 so it never reaches the cell edge (a square silhouette means it did) |
| Mist / dust | fbm density in `pixels`, filling ~85% of the cell, value-shaded for dust |

## Review

`node paint.mjs [defs]` writes the PNGs plus `_preview_<def>.png`. Compose several previews into
one board with PIL and compare against frames from the reference video.
