---
name: bending-game-design
description: Design a lore-accurate elemental bending Roblox game (the four elements of the animated bending world, not the blue-people movie): elements, sub-skills (healing, plant, blood, metal, lava, sand, seismic sense, lightning, redirection, combustion, dragon fire, flight, projection), fighting styles, rarity and unlocks, celestial events, the Avatar cycle, non-bender paths and move lists. Use when planning classes, sub-elements, progression, balance, events or moves for the bending game, or when checking whether a mechanic is canon.
---

# Bending game design (lore-accurate)

The game: players bend one element of the four-nations bending world. Four elements alone are too thin to play, so
the depth comes from **sub-skills, styles, the sky and terrain, non-bender paths, and a single Avatar per server**
while every rule stays true to the lore.

## Read first
- `references/lore.md`: the canon rules (one element per person, sub-skills and their limits, celestial cycles,
  the Avatar cycle Fire -> Air -> Water -> Earth, energybending, non-benders, combos). **Check every mechanic
  against it.** If a fact isn't there and you aren't sure it's canon, say so and don't invent it.
- `references/systems.md`: the build system (Element + Style + Sub-skill + Path), unlock rarity, slots, live
  events, the Avatar, non-benders, co-op combos.
- `references/movesets.md`: a starting move catalogue per style and sub-skill, each with a lead shape for VFX.

## Hard rules
1. **One element per player.** Only the Avatar bends more than one. Sub-skills never cross elements.
2. **Lore limits are features:** full-moon bloodbending, eclipses removing bending, no platinum for metalbenders,
   earth needs ground contact, water needs a source, flight needs detachment, combustion backfires when
   interrupted, lightning needs a calm channel.
3. **Rare things stay rare:** lavabending, combustionbending, psychic bloodbending, spiritual projection, flight,
   dragon fire. Common sub-skills (healing, metal, sand, seismic, lightning, redirection, plant) are reachable by
   everyone through play.
4. **Forbidden techniques live on the Outlaw path** (bloodbending, suffocation): learnable, with consequences.
5. **IP:** keep show titles, character names, logos, nation insignias and named techniques out of the shipped
   game. Name your own nations, styles, teachers, places and moves. Tell the user plainly that a fan game in
   someone else's world can still be taken down.

## Workflow
1. Agree the build system with the user (`systems.md`), then the roster of styles and sub-skills per element.
2. Write `lab/bending/DESIGN.md`: per element, the styles, sub-skills, each move (mechanic, lead shape, beat
   sheet, counters) and the event/terrain rules.
3. Hand each move to the `bending-vfx` skill for its effect (it builds on `roblox-anime-vfx`).
4. Keep a balance table: damage, cooldown, range, source requirement, counters, per move.
