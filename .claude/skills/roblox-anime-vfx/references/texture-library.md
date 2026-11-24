# Texture library

Greyscale/white textures; colour comes from the emitter. Layered = `<name>_glow/_rim/_mid/_core.png` (one emitter per
layer, identical motion). Shaded = one PNG whose grey value is painted light/shadow. Flipbooks: set FlipbookLayout and
FlipbookMode = OneShot (Loop for looping ones); variant sheets (embers, chips, drops, flecks): FlipbookStartRandom = true,
FlipbookFramerate ~0.01.

| Texture | Kind | Layout | What it is |
|---|---|---|---|
| `fire_burst` | layered | Grid4x4 | Billowing anime explosion fire: a cluster of lobes blooms out fast, rolls upward with painted volume (lit top-left, hot core), the top tears into tongues, then the mass breaks up and burns out. Layered. |
| `flame_lick` | layered | Grid4x4 | Looping column of rising flame tongues (burning ground, fire pillars, fists on fire). The noise scrolls exactly one period, so FlipbookMode = Loop is seamless. Layered. |
| `aura_wisp` | layered | Grid4x4 | Thin rising aura wisps (haki, awakening, charge-ups). Loop. Layered. |
| `smoke_puff` | shaded | Grid4x4 | White anime cloud puff: cauliflower of round lobes, painted 3-tone shading (lit / mid / cool shadow), expands, then dissolves into holes. Shaded. |
| `dust_burst` | shaded | Grid4x4 | Ground dust thrown out sideways and up from an impact: low wide mass of lumpy lobes with a flat base, rolling outward. Shaded. |
| `star_flash` | layered | Grid4x4 | Sharp multi-spike impact star: snaps open in 2 frames, spikes thin and retract, core fades. Layered. |
| `god_rays` | layered | Grid4x4 | Radial streaks shooting out of an impact (world-space rays). Rays extend fast, then thin and fade. Layered. Use Orientation = FacingCamera for a sunburst or VelocityPerpendicular for a flat fan. |
| `orb_glow` | layered | Grid4x4 | Churning anime energy ball (loop): white-hot core, swirling streaks inside the body, a bright rim, and short flame-like tongues licking off the edge. Angle-periodic noise rolls one full period, so FlipbookMode = Loop is seamless. Layered. |
| `flecks` | shaded | Grid2x2 | 2x2 sheet of painted sparks, each with a hot centre and a soft painted halo: (1) uneven 4-point glint, (2) needle spark with a smear trail, (3) faceted light chip (lit / shadow face, rim highlight), (4) crystal shard with a tip glint. Shaded (grey value = painted tone). FlipbookLayout Grid2x2 + FlipbookStartRandom to mix them in one emitter. |
| `embers` | shaded | Grid4x4 | 16 painted ember flakes (use FlipbookStartRandom): torn, irregular outlines from warped ellipses with a pointed tail, a glowing hot centre, a charred darker edge on one side and, on some, a fold line splitting two facets. Faint baked halo. Shaded. |
| `shock_ring` | layered | single | Painted shockwave ring: crisp bright inner edge, streaky energy feathering outward. Layered. |
| `wind_arcs` | white | Grid2x2 | 2x2 sheet of white wind arcs (swirls around ice/air moves, dash wind). Single white. |
| `slash` | layered | Grid4x4 | Painted crescent slash. The blade front travels along the arc over 4 frames (thick, white-hot, pointed), the trail behind it thins to a hairline, then the trail erodes from the swing start toward the front with a ragged dissolve. Layered. Final pose: front at the right (angle 0), trail sweeping counter-clockwise over the top; rotate/mirror the particle to aim it. |
| `crack_glow` | layered | single | Glowing ground/air fissures radiating from a centre with branches and loose fragments. Layered. Quake ground cracks, magma vents, glass-shatter cores. |
| `glass_shatter` | layered | single | Shattered-air pane (quake punch): radial cracks + broken concentric rings, faint pane facets with refraction highlights. Layered. |
| `lightning` | layered | Grid4x4 | Anime lightning strike: three forked bolts draw in from the centre over 2 frames, hold the SAME paths while flickering (tiny vertex jitter, brightness pulses, branches popping on and off), then break apart from the tips and fade. Layered. |
| `beam_strip` | layered | strip / screen | Tileable beam/trail strip (u along the beam, v across): hot core line, streaky energy body. 1024x256 output. Layered. Use with Beam.TextureMode = Wrap and TextureSpeed for flow. |
| `speedlines` | white | strip / screen | Full-screen anime speed lines converging on an empty centre. Single white, alpha only. 1024 px. |
| `slash_strip` | strip | strip / screen | For crescent shells: u = head (0) -> tail (1), v = outer edge (0) -> inner edge (1). White-hot leading rim, painted body falling off inward with streaks, ragged inner feather, tail breaking up. 1024x256. Shaded. |
| `energy_strip` | strip | strip / screen | Tileable (in u) streaky energy for rings, spheres, tubes and swirls: soft at both v edges, flowing filaments along u. Scroll it (shell 'scroll') for motion. 1024x256. Shaded. |
| `edge_strip` | strip | strip / screen | Tileable shockwave band: crisp hot edge at v=0, streaky fade to nothing at v=1. 1024x256. Shaded. |
| `wind_strip` | white | strip / screen | Tileable wispy wind filaments for tornado swirls and dash sleeves. 1024x256. White. |
| `dragon_head` | layered | single | Roaring energy dragon head, side profile facing right (Figma image generation, repainted into layers). Layered. |
| `phoenix_wing` | layered | single | Spread phoenix wing of flame feathers, root at the left (Figma image generation). Layered. |
| `giant_fist` | layered | single | Giant energy fist punching right with a flame trail (Figma image generation). Layered. |
| `water_shark` | layered | single | Charging shark of splashing water, facing right (Figma image generation). Layered. |
| `palm_strike` | layered | single | Giant open palm strike with a radiating ring (Figma image generation). Layered. |
| `magma_splash` | layered | Grid4x4 | Molten crown: thick globby jets flung up out of a bulging pool, tips tearing into globs, a cracked crust creeping over the mass as it cools and sags. Layered (hot inside, cooling crust outside). |
| `lava_drops` | shaded | Grid4x4 | 16 molten globs (FlipbookStartRandom): smooth blobs glowing from the centre, laced with dark cooling veins. Shaded. |
| `light_burst` | layered | Grid4x4 | Radiant light explosion: hot core, a dense fan of sharp rays of mixed length, a thin expanding ring and a few glints riding the rays. Layered. |
| `shock_ripple` | layered | Grid4x4 | Quake air ripples: three thin, broken concentric rings launched one after another, each with a crisp leading edge and a streaky trailing fade. Layered. |
| `ice_burst` | layered | Grid4x4 | Faceted ice shards bursting from a frost core: shards shoot out (lit / shadow halves = painted facets, bright edges), then crack into fragments that drift and fade. Layered. |
| `frost_mist` | shaded | Grid4x4 | Curling cold mist: soft wisps swirled by a domain warp that winds tighter toward the centre, expanding and thinning out. Shaded (soft alpha, cool highlights). |
| `ice_chips` | shaded | Grid4x4 | 16 crystal chips (FlipbookStartRandom): faceted shards with a lit and a shadow face and a bright edge. Shaded. |
| `void_smoke` | layered | Grid4x4 | Inky void tendrils: spiral arms of ragged smoke unwinding outward from a dense centre, then shredding into wisps. Layered (paint the core dark and the fringe glowing with the kit colours). |
| `void_orb` | layered | Grid4x4 | Black-hole accretion (loop): spiral arms draining into a bright event-horizon ring, hollow centre (pair with a black Neon sphere). Angle-periodic, seamless loop. Layered. |
| `electric_burst` | layered | Grid4x4 | Electric discharge: short jagged arcs fire out of a flash in all directions, re-strike along similar paths every two frames, then flicker out. Layered. |
| `haki_burst` | layered | Grid4x4 | Conqueror-style ink burst: thick ragged spikes splash out in two frames, then thin, retract and break into droplets, with thin crackles around. Layered (kit paints core black, middle red). |
| `blade_cuts` | layered | Grid4x4 | Crossing sword cuts: 4 razor lines slash across the centre one after another (each drawn end to end in a frame), then split into two parallel halves that drift apart and fade. Layered. |
| `water_splash` | layered | Grid4x4 | Water splash: a fan of slim jets bursts up out of a churned base, tips breaking into strings of droplets that arc and fall; bright streaks run along the water. Layered. |
| `spray_puff` | shaded | Grid4x4 | Water spray: a soft round mist burst threaded with fine droplets, expanding and fading out from the middle. Shaded (bright mist, subtle cool shading). |
| `water_drops` | shaded | Grid4x4 | 16 water droplets (FlipbookStartRandom): round and teardrop shapes, darker refraction rim and a sharp highlight. Shaded. |
| `thunder_bolt_v2` | cel | Grid4x4 | Anime cel lightning (Enel reference): sky-to-ground jagged trunk, 30-60 deg kinks with micro-jags, tapered pointed barbs and two forks; draws in along the trunk over 2 frames, re-strikes, cools (core thins first, outline lingers). Explicit hard-edged layers: core white line, mid flat body, rim filled outline (tint indigo, alpha), glow tight halo. |
| `thunder_burst_v2` | cel | Grid4x4 | Cel impact: uneven anime star flash + 8 jagged barbed bolts out in 2 frames, re-strike, cool from the tips. No shock ring. Lay it flat (VelocityPerpendicular) for a ground starburst. |
| `thunder_arc_v2` | cel | Grid4x4 | Cel crackle bush (loop): 4 short barbed arcs around the centre, new paths every 2 frames. |
| `thunder_strip_v2_1..4` | cel | strip | Tileable cel ribbons (u wraps, no width seam): jagged barbed trunk + short fishbone forks, all inside v 0.1..0.9 (nothing chopped at the ribbon edge). Swap every 0.05 s. |
