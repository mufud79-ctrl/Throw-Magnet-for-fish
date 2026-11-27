Build the AIR family of the bending game: Airbending (base), Flight, Spiritual Projection and the Outlaw technique
Suffocation. Read `prompts/bending/_shared.md` first.

## Element rules (lore)
Style: Baguazhang (circle-walking, evasion; never meet force head-on). Learned from the sky bison. Spiritual and
detached; strongest when moving and in open space. Air is invisible: it must be shown through what it moves.

## Family mechanic: momentum
Every air class builds **Momentum** (0-100) by moving (running, gliding, dodging); Momentum raises damage, range and
knockback. Standing still bleeds it. Air can't block head-on: its defence is dodging and redirecting.

## Visualising the invisible (the family's whole look)
Air reads through: white/pale streak lines, swirl lines, crescent outlines, distortion rings, and the DUST, LEAVES and
DEBRIS it throws around. Keep it light: pale blue-white with a soft grey-blue dark accent; never a solid white blob.
Matter: `air_crescent` (outline crescent with motion lines, cel), `swirl_lines` (spiralling streaks, loop),
`air_ring` (a distortion ring with a thin bright edge), `gust_streaks` (straight wind lines), `vortex_column`
(spiralling streak column, loop), `leaf_scatter`, `dust_kick` (smooth dust puff), `cloud_puff` (soft cel cloud),
`scooter_ball` (a spinning ball of swirl lines, loop), `spirit_form` (a translucent glowing silhouette outline),
`vacuum_lines` (inward-collapsing lines). Reuse: `gust_lines`, `wind_arcs`, `haze_soft`, `anime_glint`, `dust_veil`.

---
## 1. Airbending (base): "Gale", the momentum fighter
Identity: fast, evasive, knockback king. Passive **Tailwind**: Momentum boosts damage and knockback; a perfect dodge
fills it. Movement: **Air Scooter** (ride a spinning ball of air; fast, low).
- **M1 Wind String:** 4 hits: two air palms, a spinning sweep, a kick that blasts the target away. Lead: small air
  rings per hit, a dust kick on the finisher.
- **Z Air Palm:** a compressed blast of air (big knockback). Lead: an air ring + gust streaks + kicked-up dust where
  it passes.
- **X Wind Crescent:** throw a crescent of air that slices. Lead: the outline crescent with motion lines.
- **C Updraft:** a column of air launches the target upward. Lead: swirl lines spiralling up, dust and leaves lifted.
- **V Cyclone Guard:** spin a wall of wind around you that deflects projectiles back at an angle (redirect, not
  block). Lead: a swirl-line sphere; deflected projectiles curving away.
- **F Tempest (ultimate):** a huge cyclone that pulls enemies in, spins them and throws them out. Lead: the vortex
  column with debris orbiting.

## 2. Flight: "Unbound", aerial combat (legendary: detachment trial)
Identity: the only class that truly fights in the sky; earthbenders can't reach you; fragile. Lore: requires letting
go of every earthly attachment. Unlock trial: give up your gear/cosmetics for a period. Passive **Weightless**: no
fall damage; Momentum doesn't drain while airborne. Movement: **Free Flight** (a timed flight state; recharges on
the ground).
- **M1 Sky String:** 4 hits usable mid-air; the finisher spikes the target down. Lead: air rings in mid-air.
- **Z Dive Strike:** dive from the sky onto a target. Lead: a streaking dive + an air ring burst on landing.
- **X Downdraft:** slam a column of air down from above. Lead: vacuum-like lines pressing down + a dust ring.
- **C Sky Lift:** grab a target into the air with you briefly (they're out of their element). Lead: swirl lines
  carrying them up.
- **V Cloud Veil:** wrap yourself in cloud to hide in the sky. Lead: soft cel clouds forming.
- **F Heavenfall (ultimate):** rise high, then dive and explode in an air shockwave. Lead: the climb, the dive, the
  shockwave dome.

## 3. Spiritual Projection: "Wanderer", scout and support (rare gift)
Identity: information and utility; the body is vulnerable while the spirit roams. Passive **Spirit Sight**: you see
spirits and projected players. Movement: **Spirit Walk** (project your spirit: fast, intangible, can't attack; your
body stands still).
- **M1 Breeze String:** 4 light air hits (low damage).
- **Z Project:** leave your body as a glowing spirit for 8 s (scout); return early with the key. Lead: the spirit
  silhouette stepping out of the body.
- **X Spirit Mark:** while projected, mark an enemy; your team sees them for 10 s. Lead: a glowing mark.
- **C Spirit Call:** while projected, deliver a gust that knocks an enemy (small) or warns allies. Lead: a soft spirit
  gust.
- **V Return Shield:** returning to your body releases a shield ring for nearby allies. Lead: a ring of soft light.
- **F Spirit Host (ultimate):** your spirit grows huge and towers over the area for a moment, knocking enemies back
  and revealing everyone. Lead: the giant translucent spirit.

## 4. Suffocation: "Breathless" (OUTLAW technique, dark)
Not a class: a single forbidden move an Air player can learn on the Outlaw path (it makes you Wanted).
- **Breathless:** a channelled technique that pulls the air out of a target's lungs (slows, then stuns at the end;
  interrupted by any hit). Lead: inward-collapsing vacuum lines around the target's head; the target clutching.

## Order of work
Matter -> Airbending -> Flight -> Spiritual Projection -> Breathless -> second pass (three different reads: streaks and
dust, the sky, a glowing spirit) -> export (`--merge`).
