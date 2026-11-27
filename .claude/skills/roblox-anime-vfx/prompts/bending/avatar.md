Build the AVATAR: the one player per server who bends all four elements. Read `prompts/bending/_shared.md` first, and
build this AFTER the four element families exist (the Avatar borrows their matter, never recolours one kit).

## Rules (lore)
- One Avatar at a time. When the Avatar dies, the next one is a player of the **next element in the cycle Fire ->
  Air -> Water -> Earth** (opt-in candidates with high mastery, or a weighted roll).
- The Avatar starts with their native element and unlocks the others **in cycle order** by finding teachers (quests).
- **Avatar State:** glowing eyes, enormous power, multiple elements at once (the orbiting four-element sphere).
- **Killed while in the Avatar State = the cycle ends** for the season (no Avatar until the reset).
- **Energybending** (lion-turtle quest, legendary): take bending away or give it back.

## Mechanic: element switching
The Avatar has the moves of each unlocked element's BASE class (not sub-classes), switched with a stance key
(1-4). Switching mid-combo is the Avatar's skill expression: combos that cross elements (an earth column launch into
an air palm into a fire kick). Passive **Past Lives**: each switch within 2 s of the last refunds a little cooldown.
Meter: **Avatar State** fills from damage dealt and taken.

## Moves
- **Element stances 1-4:** the base class kits from water/earth/fire/air (built in those sessions, unchanged).
- **Avatar-only moves (shared across stances):**
  - **Elemental Convergence (Z in any stance after 2 elements):** a combo strike that uses the current and the
    previous element together (e.g. water + fire = a steam burst; earth + air = a dust storm; per pair, lore combos).
    Lead: the two elements colliding.
  - **Spirit Bond:** a short spirit-world dash (through a thin spirit ribbon) to an ally or a spirit portal.
- **Avatar State (F with a full meter):** glowing eyes, the orbiting sphere of four elements around the Avatar; for a
  few seconds every move is its huge version and the Avatar floats. Ends with an all-element burst. Lead: the four-
  element sphere (a water ring, rocks, fire, air streaks orbiting on different axes) + the glow.
- **Energybending (legendary, F after the lion-turtle quest; long cooldown):** grab a target and strip their bending
  for 20 s (Outlaws: longer). Lead: a beam of pure light connecting the two, a cosmic swirl, the target's element
  colour draining out.

## Matter
Reuse every family's matter. New: `four_sphere` (orbiting element ring set), `avatar_glow` (eye/body glow),
`energy_beam` (a pure white-gold-violet light beam), `cosmic_swirl` (a slow galaxy-like spiral, loop),
`spirit_ribbon` (the dash ribbon).

## Order of work
Element switching (reuse base kits) -> Convergence pairs (6 pairs) -> Avatar State -> Energybending -> second pass ->
export (`--merge`).
