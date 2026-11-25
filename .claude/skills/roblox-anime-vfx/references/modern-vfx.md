# Modern Roblox anime VFX (TSB / JJS / Type Soul bar)

Learned the hard way on the thunder fruit. The user's verdict on the first pass was "lame and dated, like 2015"
and on this pass "so much better". These rules are why. Study real frames first
(`../vfx-reference-frames` skill), then build.

## What "modern" looks like (from real TSB / JJS / Type Soul frames)
- **Glowing lines are bright, saturated and bloomy, with NO crisp dark outlines.** A dark outline around energy is
  the 2015 Flash-cartoon tell. Contrast comes from a soft halo, from the world dimming, and from dark *matter*
  (smoke, debris, burn marks). Never from outlining the glow.
- **The world dims and cools while the move plays** (Type Soul bankai goes near-monochrome), so the effect is the
  brightest thing on screen. Apply it as a grade (ColorCorrection) with a ramp in and a ramp out.
- **Hierarchy: BIG -> medium -> small.** Every hit has one big shape (shockwave ring, impact sheet, pillar,
  dome), a few medium ones (flare/glint, spark burst, impact flash) and many small ones (straight light streaks,
  sparks, chips). Thin detail alone looks cheap; one blob alone looks lazy.
- **Mass.** Shaded grey cel smoke (3 hard tone bands, eroding away), a radial dust ring that hugs the ground,
  rocks and crater slabs, and a mark left behind (crack, scorch, frost) that *animates* (spreads, then cools).
- **Straight light streaks** fly out of every impact: VelocityParallel needles with high speed and heavy drag.
- **One flash per beat.** A big flash lasts 1-2 frames, then breaks up into colour. Never a long white-out.
- **Clean geometric shapes** (rings, sigils, needles, thick glowing lines with a white core) beat squiggles.
- **Fades, not pops.** Things thin, break up (noise erosion) and cool through the colour script.

## Layer conventions for layered/cel textures (glow / rim / mid / core)
| layer | role | LightEmission | colour | notes |
|---|---|---|---|---|
| glow | soft halo | 0.75 | element hue | ~68% transparent; wide soft blur in the texture |
| rim | saturated outer body | **0.3** | saturated element hue | low LE so the colour *covers* bright sand and stays saturated |
| mid | body | 0.45 | lighter hue | |
| core | hot line | 1 | white | thin; it is the only white |

Bloom ~0.5. Push the halo with wide soft blur painted into the texture (tight halo + wide bloom), not with more
additive layers. `lab/thunder/kit.py` `_modernize()` applies this automatically in `write()`. Copy the pattern.

## Failure modes (each one happened)
1. **Additive on bright sand turns white.** Fully additive (LE 1) blue over tan sand reads as white. Keep body
   layers at low LE so the hue covers the ground.
2. **White sources stack under bloom.** A flare, an impact flash, a burst texture, a Neon flash shell and sparks
   all at once make a white blob that lasts 5+ frames. Pick one flash per beat; cut the rest.
3. **A navy/dark "backing" under glow reads as dirty smoke.** Use a translucent hue halo instead.
4. **ParticleEmitter `Shape: Disc` emits along its normal (UP)**, so a "dust ring" made with Disc rises as a puff
   above the head. Radial ground rings need `Shape: Cylinder`, `ShapeStyle: Surface`, `ShapeInOut: Outward`.
5. **ForceField fresnel spheres flood white over sand.** Use them only as a ~0.2 s dim rim flash (brightness
   0.4, transparency 0.2 -> 1), or not at all.
6. **Plain mesh rings read as vector hoops.** Use a flipbook ring with a hot leading edge and noise breakup.
7. **Desaturating the whole grade kills the effect's colour too.** Dim brightness, add contrast, tint cool;
   barely touch saturation.
8. **Flat white cel smoke reads as stickers.** It needs 3 tone bands at high contrast (shadow ~0.3 -> lit 1.0).
9. **Lightning with many barbs and micro-jags reads as scribbles.** Use a bold trunk, 1-2 forks, few barbs,
   thick-thin width pulse and a wide soft halo.
10. **Switching style mid-fruit.** One visual language per fruit. A move's identity comes from its *shape and
    mechanic*, not a new rendering style. (Flat filled "anime" plasma inside a stroke-based fruit was rejected.)

## Toolkit pattern (per fruit)
Start each fruit with `lab/<fruit>/kit.py`, copied from `lab/thunder/kit.py`, then swap in the fruit's palette and
colour scripts (HOT/COOL per layer). Helpers worth keeping:
- **flipbooks:** `impact_v3`, `shockwave`, `spark_burst`, `flare`, `swirl`, `crack` (animated mark)
- **mass:** `smoke3`, `dust_ring`, `rocks` (crater + fling)
- **small:** `streaks`, `sparks`
- **structure:** `trail_stack`, `plane_stack`, `emit_stack`, `arc_jump`, `light`, `write` (applies modern
  conventions + world-dim grade)

Re-tint the generic sheets (`shockwave_v3`, `spark_burst_v3`, `flare_v3`, `spark_streak`, `smoke_cel_v3`) per
element. Paint element-specific sheets (the matter itself) new.

## Review checklist (run on every strip before showing)
- Is any frame mostly white for more than 2 frames? (cut flashes)
- Is there one BIG shape, some medium, many small at each hit?
- Is there mass (smoke, dust ring on the ground, debris, a mark that animates)?
- Is the effect's colour saturated, or did it go pale/white?
- Any dark outline around glow? Any dirty grey smudge? Any vector hoop?
- Does every move still read as its own mechanic (silhouette), in the fruit's one style?
- Do all five animation rules show (anticipation, squash/stretch, follow-through, timing/hit-stop, arcs)?
