# Anime VFX style notes

What makes effects in fight anime look the way they do, and how each trait maps to a Roblox
ParticleEmitter setting. These are style observations for original effects, not frame copies.

## Shared traits (all series)

| Trait | What it looks like | Roblox translation |
|---|---|---|
| Hard cel shading | 3–5 flat color steps, no soft gradients | texture `bands()` with `aa()` steps; Color multiplies the baked ramp |
| Ink rims | dark red/black outline on fire and smoke | baked rim in texture + `ink_spike` backing layer at negative ZOffset |
| Smears | stretched shapes along motion | `Orientation` VelocityParallel with long thin textures |
| Holds | the blast freezes at full size for a few frames | high `Drag` (5–9) + Size plateau keypoint |
| Animating on 2s/3s | 12 or 8 drawings per second | `FlipbookMode` Random or Loop at `FlipbookFramerate` 8–12 |
| Impact frames | 1–3 frames of inverted or threshold colors | ColorCorrection (Saturation -1, Contrast 6–10) + void + Highlights |
| Speed lines | radial white spikes on the hit | `speedline` texture, Speed 150+, Lifetime < 0.2 |
| Debris + dust | chunky rocks, low dust skirt | `rock` with gravity Acceleration, Cylinder-surface dust |

## Jujutsu Kaisen (MAPPA)

- **Look:** high-contrast, often near-black backgrounds; fire goes white-hot core → saturated
  orange → deep crimson with black ink inside the flames (Jogo, Sukuna's flame arrow).
- **Impact frames:** signature black/white or black/red frames with the silhouette inverted. Use
  2–3 frames: white flash → B/W threshold with white Highlight → red-tinted threshold with
  black Highlight.
- **Shape language:** sharp, aggressive spikes; flames as long tapered tongues with S-curves.
- **Cursed energy auras** (for later effects): dark blue/black wisps with a light rim, drifting
  upward with FlipbookMode Random @ 8–12 fps; use LightEmission 0 for the dark core and an
  additive rim layer.
- **Camera:** heavy shake, very short; often zoom punch (could map to FOV tween).

## One Piece (Toei, Wano-era style)

- **Look:** brighter, more saturated, warmer palette; thicker outlines; more "comic" shapes.
- **Fire (Ace-style fist flames):** rounded billowing tongues with bold dark-red outlines, yellow
  interior bands, and big starbursts on contact.
- **Impact star:** multi-point white starburst with an orange edge, often with a colored ring
  around it. That is the `starburst` texture.
- **Haki-style lightning** (later effects): black-red forked bolts, best done with Beams + jagged
  textures and flickering `Transparency` via Random flipbooks.
- **Woodblock smoke:** curly cloud lumps with spiral cuts. A future `smoke_curl` texture could
  use polar noise for spirals.

## Demon Slayer (ufotable)

- **Look:** ukiyo-e inspired water and flame; strong flowing ribbons, painted gradients inside
  hard outlines.
- **Translation:** Beams and Trails with ribbon textures are better than particles here; the
  emulator does not yet support Beams. Add a `Beam` layer type to `sim.js` + `luau.js` first.

## Color ramps (fire)

| Step | JJK | One Piece |
|---|---|---|
| core | `#fffbe8` | `#ffffff` |
| hot | `#ffe45a` | `#fff35c` |
| mid | `#ffa51e` | `#ffb01e` |
| cool | `#ff5a0a` | `#ff6a00` |
| edge | `#c81e0a` | `#e0300a` |
| ink | `#3d0604` | `#5a0a04` |

## Timing references (60 fps)

- Anticipation: 12–18 frames.
- Impact frames: 2 + 3 + 3 frames.
- Main bloom to full size: 6–10 frames.
- Hold: 10–20 frames.
- Dissipation: 40–90 frames.
