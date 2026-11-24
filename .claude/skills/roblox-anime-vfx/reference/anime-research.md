# Anime VFX research guide

> Compiled by a research subagent. Page fetches were blocked by the network policy, so facts tagged **[src]** come from search-result excerpts of the listed pages. Everything else is standard 2D-FX / real-time VFX practice turned into starting numbers. Tune by eye.

## 0. What makes it "generic mobile VFX" (avoid all of these)
1. Soft radial gradients and Perlin-noise blobs with no hard edge. Anime FX are **cel shapes**: hard edges, 2 to 4 flat value bands, at most one soft glow layer.
2. Everything is additive, so there is no dark value anywhere. Anime FX always include a dark ink or shadow band, or dark smoke. Riot's style guide also stresses value control. It tells artists to avoid absolute extremes across whole assets so the hierarchy stays readable **[src]**.
3. Linear timing and linear fades. Riot calls linear timing curves "harmful". Use a short anticipation, a hard impact, then an eased dissipation **[src]**.
4. Smooth 60 fps interpolation. Anime FX change drawing on 2s or 3s, and that stepped motion is a large part of the look.
5. Every particle uses the same synced flipbook. Hashimoto's explosions are "each unique, never cycled" and interact with each other **[src]**.

---

## 1. Shape language (silhouette rules)

**General**
1. **Thick-to-thin everywhere.** Every tongue, smoke lobe and slash runs from a thick body to a thin, sharp tip. Tips end in a point, never a round cap.
2. **Convex lobes, concave cusps.** Outer contours are chains of round bulges that meet at sharp inward points (cusps). Draw the cusps as hard V notches. This single rule separates anime smoke and fire from noise blobs.
3. **Size hierarchy of 1 : 3 : many.** Use one dominant mass, 2 to 4 medium masses, and 6 to 15 small bits. Never draw equal-sized blobs.
4. **S and C curves.** Fire tongues are S-curves. Slash and shockwave arcs are C-curves. Avoid straight segments longer than about 15% of the shape length.
5. **Negative-space cuts.** Punch 1 to 3 hard-edged holes or slits into big masses, mostly near the dissipating side. Holes grow over frames until the shape breaks into chunks.
6. **Pinch-off.** Tips neck down and detach into separate droplets that keep flying, shrink and vanish. Spawn 1 to 2 detached bits per tongue per 2 drawings.
7. **Angular debris.** Rocks and rubble are faceted polygons with 3 to 6 sides and a 2-tone fill, following the "cubic debris" tradition named after Yutaka Nakamura **[src]**. Never use round pebbles.
8. Nakamura-style fire and smoke are "simple color spreads", nearly minimalist, with the power coming from big shape changes, not detail **[src]**. Tomohiro Shinoda's smoke (Mob Psycho 100) is "smooth but not round" **[src]**. Long smooth contours that never become circles are the target.

**Fire**
9. The base is a wide, bulbous mass. 3 to 7 tongues rise from it, each leaning in the motion or wind direction. The 2 or 3 longest tongues are 1.5 to 2.5 times the height of the body.
10. The inner core shape repeats the outer silhouette at about 50 to 60% scale, shifted toward the base. It is not concentric. Demon Slayer flames add ukiyo-e curl tips: tongues end in tight spiral hooks.

**Smoke**
11. Clusters of 3 to 8 lobes with cusps between them. Use 2-tone cel shading: a light side and a shadow side split by a **hard terminator**. The shadow covers 40 to 60% of each lobe on the side away from the light. An optional thin rim of bright light (1 to 3% of lobe radius) sits on the lit edge.

**Sparks**
12. Sparks are elongated diamonds or needles, 4:1 to 10:1, pointing along velocity. Add 4-point star glints on a few.

---

## 2. Timing and animation (24 fps base)
1. **Drawings per second.** Draw fast impacts and the first explosion frames on 1s (24/s). Draw most FX on 2s (12/s). Draw smoke and slow auras on 3s (8/s). For a flipbook, author at **12 drawings per second** and play at FlipbookFramerate about 12. Use 8 for smoke.
2. **Stepping.** Keep stepped frames. Never cross-fade between frames.
3. **Explosion beats (at 12 fps):**

   | Beat | Frames | Seconds |
   |---|---|---|
   | Flash / impact frame | 1 to 2 | |
   | Starburst | 1 to 2 | |
   | Fireball expansion (ease-out: about 80% of max size by 30% of the phase) | 3 to 5 | |
   | Hold / boil at full size | 2 to 4 | |
   | Smoke takeover and breakup | 6 to 10 | |
   | Total | 16 drawings, fits a 4x4 sheet | about 1.3 |

4. **Slash beats:** 0 to 1 anticipation glint frames, then 1 frame appear at **full length** (no growing in), then 1 to 2 hold frames, then 3 to 6 dissipation frames. That totals 6 to 9 drawings, or about 0.5 to 0.75 s. Slashes are at full shape for only 1 or 2 frames **[src]**.
5. **Offset layers by one drawing.** Hashimoto animates two background explosions on twos so that one moves while the other holds **[src]**. Give each layer and emitter a different start frame and framerate.
6. **Follow-through and overlap.** Tongue tips lag the body by 1 to 2 drawings. Detached bits keep momentum and decelerate. Smoke inherits the fireball's outward velocity and then turns upward (advection).
7. **Smears.** A smear is a single drawing that links two poses in as few frames as possible **[src]**. Use one smear frame (stretched and multiplied shape) at the fastest moment, never two in a row.
8. **Inflation.** Explosions should "inflate, as if each explosion gave rise to a new explosion within itself" **[src]**. Spawn new lobes inside or at the edge of existing ones every 2 drawings, instead of scaling one shape up.
9. **Debris and dust land late.** Key them a few frames after contact, so the hit reads first **[src]**.

---

## 3. "Life" for held elements (beams, auras, held slashes, glows)
1. **Boil.** Redraw the same shape every 2 drawings with ±3 to 6% contour jitter, so lobes shift and cusps move. In flipbook terms, a looping held glow needs at least 4 unique frames, and 6 to 8 is better, played on 2s. Never use one static sprite with a pulsing scale.
2. **Flicker.** Change core brightness by ±10 to 20% every 2 to 3 drawings, in steps and not as a sine wave. On a beam, add a 1-frame full-white flash every 8 to 16 drawings.
3. **Secondary emitters** on any held effect longer than 0.5 s:
   - **Sparks:** 10 to 30 per second, 0.15 to 0.4 s life.
   - **Glints:** 4-point stars, 2 to 6 per second, 2 to 3 frames each, peaking on frame 1.
   - **Crackle:** short branching lightning, 3 to 8 segments, 1 to 3 per second. Each bolt lives 2 to 4 drawings and is redrawn every drawing, never moved. "Kutsuna lightning" is an established anime-FX term **[src]**.
   - **Wisps:** small flame bits peeling off the aura edge, 4 to 10 per second, rising and pinching off.
4. **Pulse.** Make the held mass scale-punch by +8 to 15% on beat accents, such as each damage tick, with a 1-drawing overshoot.
5. **Edge breakup on beams.** The outer silhouette carries traveling notches or chevrons that scroll along the beam at 1 to 3 beam-widths per second. The core stays straight.

---

## 4. Color and value structure
1. **Four layers, from outside in:**

   | Layer | Look | Coverage |
   |---|---|---|
   | Glow | Soft, low alpha (0.2 to 0.4) | 1.3 to 1.8 times the shape size |
   | Rim / ink | Darkest, most saturated hue, or black / dark ink | |
   | Mid | Main hue | 40 to 60% of area |
   | Core | Near-white, with a slight hue tint | 10 to 25% of area |

   Use hard steps between rim, mid and core. Only the glow is soft.
2. **Hue-shift outward.** For fire, go from core white-yellow (#FFF6D0) to mid orange (#FF8A1E) to rim red-crimson (#C21A12) to ink or smoke (#2A0A0A to #120808). For blue slashes, go from core white (#FFFFFF) to mid cyan (#6FD8FF) to rim deep blue (#1E4BD8) to ink navy (#0A1440).
3. **Show-specific palettes (from viewing; not documented by the studios):**
   - **JJK (MAPPA):** heavy black. Fire and cursed energy sit on dark, desaturated smoke with a lot of ink. Black Flash is crimson-red lightning around a black core with red rim, often on inverted or desaturated frames. Fire (Sukuna) uses white core, hot orange, then deep crimson, then near-black smoke.
   - **One Piece Wano (Toei):** saturated primaries with **thick black brush-ink outlines**, in an ukiyo-e / kabuki look. Impact frames are often 2 to 3 flat colors (black, white and one accent) or full color inversion, and spread widely online **[src]**.
   - **Demon Slayer (ufotable):** ukiyo-e outlined elements. The Water Breathing visuals take Hokusai's prints as reference and the waves are almost all hand-drawn **[src]**. Fire uses dark red outline, orange body and yellow-white inner swirls, then heavy compositing glow and light wrap on top. Water is a blue body with white foam lines and a navy outline.
   - **Chainsaw Man:** muted and photographic. Desaturated smoke, near-real blood red, and less glow. Rely on value and shape, not saturation.
4. **Impact frame.** Lasts 1 to 3 frames **[src]**. Use a high-contrast black-and-white or inverted-complementary silhouette **[src]**. Common schemes are pure black and white, black with red, or a negative of the scene. In a flipbook, make frame 1 a full-white or full-black shape that fills about 90% of the cell.
5. **Value contrast.** Keep the core-to-ink spread across at least 70% of the luminance range. Smoke shadow should be at least 25% darker than its lit side.

---

## 5. Sword slash anatomy
1. **Profile.** A crescent shaped like a thin moon. The thickest point sits **60 to 75% of the way toward the leading tip**. The leading tip is a sharp, hard point. The trailing end tapers long and thin, like a flag with the trailing end narrower than the leading tip **[src]**. Peak thickness is 6 to 12% of the arc radius. The arc spans 100 to 160 degrees.
2. **Edges.** The outer (cutting) edge is a crisp, hard curve. The inner edge is slightly softer, or broken into streaks.
3. **Interior streaks.** Add 2 to 5 thin lines parallel to the arc inside the body, at different lengths. They start at the tail and stop short of the tip. The trailing third breaks into separated streak lines with gaps between them.
4. **Appearance.** The slash appears at full length in a single drawing. An optional 1-drawing smear precedes it, as a thinner, longer and more transparent arc.
5. **Dissipation, in this order:**
   1. The inner edge eats toward the outer edge, so the slash thins from the inside.
   2. The body splits into 2 or 3 parallel lines.
   3. The lines break into 3 to 6 shards or dashes that drift slightly outward along the tangent.
   4. One thin hairline lingers for 1 to 2 extra drawings.
6. **Extras:**
   - Tip glint: a 4-point star, 2 to 3 frames, at the leading tip on the appear frame.
   - Sparks: 5 to 12 needle sparks thrown tangentially from the leading half.
   - Air lines: 2 to 4 straight speed lines outside the arc.
   - Afterimage: a duplicate arc offset 5 to 10 degrees behind, at 30 to 50% opacity, lasting 1 to 2 drawings.
   - Optional thin dark ink outline on the outer edge, so the slash reads on bright backgrounds.
7. **Fire-sword slash (Rengoku / Tanjiro):**
   - Same crescent, but the outer edge breaks into flame tongues pointing **backward along the swing** (opposite to motion) at 3 to 8 points.
   - The tail becomes curling flame wisps instead of streaks.
   - The core is yellow-white with an orange body and a dark red outline.
   - It dissipates as tongues pinching off, plus ember sparks and a short smoke puff on the last 2 to 3 drawings.
   - Water slash: the same crescent with a wave-crest outer edge (curl hooks) and white foam lines inside.

---

## 6. Explosion anatomy (anime)
1. **Frame 1:** a flash or impact frame. It is a white or black full-cell starburst with 8 to 16 sharp spikes of uneven length. It may be inverted.
2. **Frames 2 to 3:** a hard-edged spiky starburst. The core is white, there is a thin colored rim, and needle spikes radiate outward.
3. **Expansion:** a lumpy dome or sphere made of 5 to 9 lobes that keep spawning sub-lobes (inflation). Flame tongues point outward and radially at the edge. On ground explosions, tongues point up and outward and there is a flat ground ring.
4. **Shape choice:**
   - **Starburst** for hits and airbursts.
   - **Dome** for ground blasts, with a dust skirt (shockwave ring) spreading low and fast at 1.5 to 2 times the dome speed. Akira is the canonical reference **[src]**.
   - **Mushroom** for big finishers only: a dome, then a column, then a cap.
5. **Transition to smoke.** Smoke appears at the **outer edge first** and eats inward, while the fire core shrinks and drops toward the base. Around the middle of the effect, fire covers about 50% of the area. By 75% it is only a few flickering pockets inside dark smoke.
6. **Smoke style.** Dark (desaturated, toward the palette's ink color), 2-tone cel lobes with cusps, and an orange rim-light along the lower or inner edge where the fire lights it. It rises slowly on 3s and breaks apart with negative-space holes. Hashimoto adds a nearly transparent smoke layer on top of self-luminous fire **[src]**.
7. **Debris.** 6 to 20 angular chunks of 3 to 6 sides, thrown on ballistic arcs. Give each chunk a 1-drawing speed-line streak on launch. Optionally add a thin dark smoke trail to the 2 or 3 largest.

---

## 7. Roblox implementation
1. **Grids.** Roblox flipbooks support 2x2, 4x4 and 8x8 grids on textures up to 1024 px. A 4x4 sheet at 1024 gives 16 frames of 256 px each **[src]**. An 8x8 sheet gives 128 px frames, which is too soft for big hero FX. **Use 4x4 at 1024 for hero shapes such as slashes, explosion cores and smoke. Use 8x8 only for small sparks and debris.** A Custom layout (FlipbookSizeX/Y, 1 to 64) exists via a newer beta **[src]**.
2. **Flipbook modes.**
   - OneShot spreads frames evenly over the particle's Lifetime **[src]**. Use it for impacts and slashes, and set Lifetime to frames ÷ 12.
   - Loop with FlipbookFramerate as a NumberRange gives random speed per particle **[src]**. Use it for held boil, with a range such as 10 to 14.
   - Set FlipbookStartRandom = true for held loops, so particles desync.
3. **White textures plus Color.** Author textures in grayscale with the value bands baked in (core 255, mid about 190, rim about 110), then tint with a ColorSequence.
   - A single tint makes a monochrome ramp. For a hue shift from core to rim, either bake color into the texture or split the effect into separate core, mid and rim emitters.
   - The usual approach in anime-style Roblox games is separate emitters per layer, sharing the same flipbook frames at different scales.
4. **LightEmission.**
   - LightEmission 1 is additive, and with a grayscale texture it hides dark regions **[src]**. Use it for core, glow, sparks and slash body.
   - Additive cannot draw dark. **Ink outlines, smoke and impact-frame blacks need LightEmission 0** (normal alpha blend) with real alpha.
   - Set LightInfluence 0 on everything, so scene lighting does not muddy cel colors.
   - Brightness 2 to 5 on core layers, for bloom.
5. **Layer order.** Use ZOffset: smoke and ink at −1 to 0, mid at 0.5, core at 1, glow behind or in front depending on the effect. Tint the glow layer and keep it at 0.2 to 0.4 alpha.
6. **Slashes** are usually not particles.
   - A curved MeshPart (crescent plane or ring segment) with the flipbook frames swapped by script every 1/12 s.
   - A Beam between Attachments, with a crescent texture and TextureMode Stretch.
   - Or a Trail on the blade for the smear.
   - Add particle emitters at the tip for glints and sparks. Use Orientation VelocityParallel for needle sparks, and Squash for stretch.
7. **Impact frames** in Roblox are usually a full-screen black/white UI overlay, or a ColorCorrection set to Contrast/Saturation extremes (or inversion-like), for 1 to 3 rendered frames (about 0.05 s). Add hit-stop and camera shake **[src]**.
8. **Common mistakes:**
   - Soft-airbrushed textures.
   - All layers additive, which washes everything to white.
   - Lifetimes too long (anime hits are under 0.6 s).
   - Smooth Transparency fades instead of shape-driven dissipation drawn in the frames.
   - One emitter instead of 3 to 5 layered ones.
   - Synced flipbooks.
   - 8x8 used for big shapes, which blurs them.
   - Effects with no secondary sparks or glints, so they look dead.
   - Forgetting the 1px-plus transparent padding per cell, which causes neighbor-frame bleed at mip levels. Keep about 4 to 8 px of clear margin inside each 256 px cell.

---

## Sources
Excerpts from search results; direct fetching was blocked.
- https://fullfrontal.moe/?p=2335 (Hashimoto explosions: inflate, unique, alternate on twos, translucent smoke layer)
- https://en.wikipedia.org/wiki/Yutaka_Nakamura and https://skool.com/sakuga-design-club-8919/sakuga-glossary (Nakamura: cubic debris, minimalist color spreads)
- https://blog.sakugabooru.com/2016/09/13/mob-psycho-100-episode-10/ (Shinoda smoke "smooth but not round")
- https://playnoya.pages.dev/posts/this-my-hero-academia-animator-is-worth-keeping-an-eye-on ("Kutsuna lightning")
- https://jasontomlee.itch.io/slashfx/devlog/629732/tutorial-2-slash-shape-fundamentals (crescent, 1 to 2 frame peak, flag-shaped taper)
- https://www.gdquest.com/library/juicy_attack and https://www.bloopanimation.com/the-art-of-smear-frames/ (anticipation, smears)
- https://fictionhorizon.com/25-anime-fights-with-perfect-animation-timing/ (debris keyed after contact)
- https://www.arhfoundation.org/impact-frames-meaning and https://knowyourmeme.com/memes/cultures/impact-frames (impact frames)
- https://nexus.leagueoflegends.com/en-us/2017/10/dev-leagues-vfx-style-guide/ and https://www.vfxapprentice.com/blog/10-league-of-legends-vfx-design-tips (Riot value and timing)
- https://www.animenewsnetwork.com/feature/2019-08-28/interview-demon-slayer-producer-yuma-takahashi/.149177 (hand-drawn water, ukiyo-e)
- https://hitmarker.net/news/hiroshi-kanazawa-animates-2d-style-anime-explosions-made-with-blenders-geometry-nodes-514406 (Akira-style crater explosions)
- https://devforum.roblox.com/t/animated-particles-with-the-particle-flipbooks-beta/1718023, https://devforum.roblox.com/t/particles%E2%80%99-flipbook-release/2029388, https://create.roblox.com/docs/reference/engine/enums/ParticleFlipbookMode, https://create.roblox.com/docs/building-and-visuals/lighting-and-effects/particle-emitters, https://devforum.roblox.com/t/client-beta-optimize-your-particle-animations-with-custom-flipbook-layouts/4005128
- https://devforum.roblox.com/t/stoic-bomb-vfx-recreation-and-personal-workflow-overview/3608056 (Roblox VFX workflow, camera shake)
