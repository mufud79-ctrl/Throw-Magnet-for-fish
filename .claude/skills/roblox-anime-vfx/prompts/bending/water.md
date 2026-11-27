Build the WATER family of the bending game: Waterbending (base), Ice, Healing, Plantbending, Bloodbending and Spirit
Purification. Read `prompts/bending/_shared.md` first; it overrides nothing here but applies to everything.

## Element rules (lore)
Style: Tai Chi (push and pull, redirect, never stop flowing). Learned from the Moon. Stronger at night, peak at full
moon, **no bending during a lunar eclipse**. Needs a source: oceans, rivers, snow, water skins, plants; masters can
pull water out of the air or plants (slowly). Weak in deserts.

## Family mechanic: the carried supply
Every water class holds a visible **supply** (a body of water orbiting the player, 0-100). Moves spend it; it refills
from nearby sources fast, from the air slowly. The supply is the family's signature on screen: it should always be
visible and reshape into each move. (Plant uses plant water instead; Blood uses none.)

## Matter to paint (water family)
`water_ribbon` (layered strip, foam edge, tileable U), `water_crest` (curling wave lip, 4x4), `foam_burst` (white foam
splash, cel), `water_orb` (wobbling sphere of water, loop), `droplet_spray` (sharp drops), `ice_shard` (faceted,
single + 4x4 form-in), `ice_spire` (tall crystal), `frost_bloom` (frost spreading on the ground, flat), `rime_crack`
(ice crack decal), `mist_sheet` (smooth fog), `heal_glow` (soft water glow wrapping a limb, loop), `vine_whip`
(plant strip), `thorn_burst`, `leaf_scatter`, `blood_vein` (dark-red vein pulse, flat on a target), `aurora_band`
(spirit ribbon, loop). Reuse: `haze_soft`, `anime_glint`, `ink_shards`, `needle_bold`, `impact_crater`.

---
## 1. Waterbending (base): "Tide", the flow fighter
Identity: combo-extender and controller; never stops moving. Passive **Flow**: chaining moves without pausing refunds
supply. Movement: **Wave Ride** (ride a short wave forward).
- **M1 Current String:** 4 hits: two water jabs, a sweeping arc, a splash-kick finisher (knockback). Lead: a short
  water arc per hit; the finisher drops a foam splash.
- **Z Lashline:** a long water whip, 2 hits (out-slash, back-slash) that can extend a combo. Lead: one sweeping water
  ribbon with a foam edge; droplets fling off the tip.
- **X Undertow:** a stream snakes out, grabs the target and yanks them to you. Lead: a coiling stream that wraps and
  snaps back; a foam ring on the grab.
- **C Breaker:** raise a wave and ride it forward; it knocks down everyone in its path. Lead: a curling wave crest;
  spray trails off the lip; it collapses into foam at the end.
- **V Water Shell:** the supply wraps you as a sphere that absorbs one projectile and flings it back. Lead: a wobbling
  water orb with a bright rim; on absorb it ripples and bulges toward the attacker.
- **F Grand Tide (ultimate):** pull a towering wave up from the supply/sources and crash it across an area. Lead: the
  wall of water rising (anticipation hang at its peak) and the crash (foam explosion, flood that drains).

## 2. Ice: "Glacier", zone control
Identity: freezes the fight in place; builds lasting ice terrain. Passive **Rime**: hits stack Chill (slows); 5 stacks =
encased for 1.5 s. Movement: **Ice Slide** (lays an ice strip and skates it).
- **M1 Frost String:** 4 hits of ice-tipped strikes; each applies Chill. Lead: small shard bursts per hit.
- **Z Shardfall:** a volley of 6 ice daggers in a tight fan. Lead: faceted daggers forming in the air (form-in) then
  firing; they stick and shatter.
- **X Rime Wall:** a thick ice wall that blocks and can be shattered (shards fly). Lead: the wall growing up in
  facets; frost blooms on the ground at its base.
- **C Frostbind:** frost races along the ground to a target and freezes their feet (root). Lead: a frost-bloom line
  on the ground ending in ice clamping up the legs.
- **V Glacier Spike:** a cluster of ice spikes erupts under the target and launches them. Lead: spires bursting up in
  a wave; ice dust.
- **F Whiteout (ultimate):** a field of ice spires grows across an area; enemies inside are slowed and take Chill;
  ends with the field shattering outward. Lead: the spire field + the shatter.

## 3. Healing: "Spring", support
Identity: the team's lifeline; low damage. Passive **Mender's Touch**: healing others charges the ultimate. Movement:
**Stream Step** (short dash on a water stream).
- **M1 Palm String:** 4 light water-palm hits; the 4th heals the nearest ally a little. Lead: soft water palms.
- **Z Mending Flow:** channel glowing water onto an ally (heal over time while channelling). Lead: glowing water
  wrapping the ally's limb and pulsing along chi lines.
- **X Tide Pool:** place a healing pool on the ground (heal zone, 6 s). Lead: a calm glowing pool with slow ripples.
- **C Chi Mend:** cleanse: remove stuns, slows and chi-block from an ally. Lead: a quick ring of light water that
  flushes dark specks out of the target.
- **V Restore:** revive a downed ally (long cast, interruptible). Lead: water lifting off the ground around them into
  a rising glow column.
- **F Spirit Spring (ultimate, unlocked by the sacred-oasis quest):** a large healing burst + shields for allies in
  range. Lead: a bright spring erupting with spirit-glow water arcing to each ally.

## 4. Plantbending: "Mire", summoner and terrain (swamps and forests)
Identity: fights through plants; only at full strength near plants (cracks in stone sprout weak vines elsewhere).
Passive **Overgrowth**: moves leave plant patches that slow enemies. Movement: **Vine Swing** (grapple to a tree or
vine patch).
- **M1 Bramble String:** 4 vine lashes; the finisher trips. Lead: green vine whips with leaf scatter.
- **Z Thornroot:** roots burst from the ground under a target and snare them. Lead: roots spiralling up and
  clamping; thorns.
- **X Kelp Drag:** a long vine grabs and drags the target along the ground. Lead: a vine whip that latches and reels.
- **C Bramble Wall:** a wall of thorny growth that damages anyone touching it. Lead: thorny vines weaving into a
  wall.
- **V Spore Burst:** a swamp-gas cloud from the plants (blinds); lore-flavour of swamp mist. Lead: a smooth green fog
  burst with drifting leaves.
- **F Swamp Colossus (ultimate):** gather plants and water into a giant body and pilot it for a short time (big slow
  slams). Lead: the body assembling from vines and water, glowing eyes in the canopy.

## 5. Bloodbending: "Marionette" (OUTLAW path, full moon only)
Identity: controls enemy bodies; no visible water at all. Gated: only usable on full-moon nights (psychic
bloodbending, a legendary-rare gift, works any time with long cooldowns). Using it marks you **Wanted**.
Passive **Grip**: targets you've held move slower for a few seconds. Movement: none special (walks; menacing).
- **M1 Pressure String:** 4 unarmed hits that make the target stagger as if pulled. Lead: the victim's forced
  flinches; a dark-red pulse on contact.
- **Z Puppet Hold:** freeze a target in place (channel). Lead: the target's body seizing, arms pulled out; dark-red
  veins pulse on them; the caster's hand clawed.
- **X Marionette Walk:** force the held target to walk where you aim. Lead: the target's jerky forced steps; a faint
  red thread-glow between hand and target.
- **C Pin:** slam the target into the ground. Lead: the body yanked down; a dust crater; red pulse.
- **V Turncoat:** force the target to throw one attack at their own ally. Lead: the target's own move fired the
  wrong way, their body outlined dark red.
- **F Dominion (ultimate):** control everyone in range for a moment and throw them together. Lead: every enemy
  seized at once, the moonlight on the caster, the slam.

## 6. Spirit Purification: "Aurora", anti-control (polar-north spiritual gift)
Identity: counters control and spirits; mid damage. Passive **Clear Mind**: immune to the first control effect every
20 s. Movement: **Spirit Drift** (glide a short way on a spirit ribbon).
- **M1 Spirit String:** 4 hits with water carrying a faint aurora glow. Lead: water strikes with aurora edges.
- **Z Purify:** a wave that removes buffs from enemies and debuffs from allies; breaks bloodbending holds. Lead: an
  aurora ring sweeping out.
- **X Spirit Lance:** a spear of spirit-charged water. Lead: a glowing water lance with an aurora trail.
- **C Calm:** pacify a spirit enemy / silence a player briefly. Lead: soft rings settling over the target.
- **V Tidal Light:** a spirit-water pillar that heals allies a little and burns spirits. Lead: an aurora column.
- **F Northern Lights (ultimate):** the sky ripples with aurora bands over an area; enemies inside can't use control
  effects; allies cleansed. Lead: the aurora sky over the zone.

## Order of work
Matter -> Waterbending (6 moves) -> Ice -> Healing -> Plant -> Blood -> Spirit -> second pass (side by side: six classes,
six different reads) -> export (`--merge`).
