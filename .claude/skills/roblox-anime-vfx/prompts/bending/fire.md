Build the FIRE family of the bending game: Firebending (base), Lightning, Redirection, Combustion and Dragon Fire.
Read `prompts/bending/_shared.md` first.

## Element rules (lore)
Style: Northern Shaolin (fast, aggressive kicks and punches); breath is the source of the fire. Learned from the
dragons (fire as life and energy, not only rage). Stronger by day, **massively amplified while the comet passes**,
**no bending during a solar eclipse**. Lightning needs a calm mind ("cold-blooded fire").

## Family mechanic: heat
Every fire class builds **Heat** (0-100) by landing hits; Heat raises damage and changes move versions (a Heat 100 move
is bigger). Heat drains when you stop attacking, so fire is punished for backing off. Lightning is the exception: it
cools you (calm), see below.

## Matter (the Dragon fruit's fire is the starting point: reuse it, but each class needs its own lead matter)
Reuse: `flame_billow`, `flame_tongue`, `flame_strip_1..4`, `fire_crescent`, `anime_flame_spike`, `fire_wisp`,
`flame_flicker`, `heat_haze`, `molten_crack`, `fire_scorch`, `impact_crater`, `embers`, the thunder fruit's
`thunder_bolt_v2`, `thunder_arc_v2`, `lichtenberg`, `plasma_orb`. New: `fire_fist` (a short punch-flare, cel),
`kick_arc` (a fire crescent from a kick, thinner and faster than fire_crescent), `jet_flame` (feet/hand jet strip),
`lightning_fork` (branching bolt that forks in two), `static_mark` (a crackling mark on a target, loop),
`redirect_path` (a lightning trail that bends through a body silhouette), `third_eye_beam` (a thin, dense combustion
beam), `combustion_blast` (a tight spherical explosion with a shock ring), `true_flame` (rainbow-banded fire strip:
red-orange-gold-green-blue-violet; the dragons' "true colours"), `sun_glyph` (a sun-shaped mark, flat).

---
## 1. Firebending (base): "Blaze", the rushdown fighter
Identity: in your face; snowballing pressure. Passive **Stoke**: each hit +Heat; at 100 Heat your next move is
empowered. Movement: **Jet Dash** (a short jet-propelled dash).
- **M1 Flame String:** 4 hits: jab, jab, spinning kick (fire arc), forward punch blast. Lead: short fire-fists and
  one kick arc.
- **Z Flare Bolt:** a fire blast from the fist; at high Heat it fires two. Lead: a fat flame bolt with a torn tail.
- **X Arc Kick:** a fire crescent from a jumping kick that travels forward. Lead: a sharp kick crescent, crimson edge,
  gold body.
- **C Fire Whip:** a long fire whip, 2 lashes. Lead: a flame ribbon cracking at the tip.
- **V Wildfire Wall:** a line of fire on the ground that blocks and burns. Lead: a fused flame curtain (one wall, not
  candles).
- **F Inferno Pillar (ultimate):** a column of fire erupts under the target and spreads outward in a ring. Lead: the
  column + the spreading ring.

## 2. Lightning: "Stormheart", the sniper
Identity: precision burst from range; must stand still to channel ("calm mind"); hits interrupt the channel. Passive
**Calm**: lightning moves REDUCE your Heat; the lower your Heat, the faster you channel. Wet targets (hit by water)
take bonus damage (water conducts). Movement: **Static Step** (a short blink with a crackle; no fire).
- **M1 Spark String:** 4 quick jabs with crackling sparks (low damage, apply Static).
- **Z Arc Shot:** a short channel (0.5 s: the two-finger draw, energy separating) then a fast straight bolt. Lead:
  the bolt + the circular arm motion in anticipation.
- **X Fork:** lightning that chains between up to 3 nearby enemies. Lead: a forking bolt.
- **C Static Mark:** mark a target; your next lightning on them crits. Lead: a crackling mark on the target.
- **V Overload:** detonate every Static stack on enemies near you. Lead: small arc bursts on each marked enemy.
- **F Storm Fork (ultimate):** a long channel, then a massive branching strike from above onto an area. Lead: the
  sky-to-ground fork + lichtenberg scorch on the ground.

## 3. Redirection: "Return", the counter fighter
Identity: punishes fire and lightning users; weak in matchups without them. Passive **Through the Stomach**: a
successful redirect makes your next move free and faster. Movement: **Flow Step** (a circular step that briefly
reduces damage).
- **M1 Palm String:** 4 open-palm strikes with small flame flicks (deliberately not aggressive).
- **Z Return Current:** a timing window: catch an incoming lightning or fire attack and send it back. The animation
  traces the energy through the arm, down to the stomach, and out the other arm. Lead: the energy path through the
  body silhouette, then the return bolt.
- **X Deflect:** bat away a fire projectile at an angle (smaller window, no return). Lead: a flame swatted aside.
- **C Heat Sink:** absorb nearby fire (puts out enemy fire walls; never lava, which is earth) and gain Heat. Lead: flames
  pulled into your palms.
- **V Counter Palm:** a short-range palm blast that's empowered after a successful redirect. Lead: a palm flare.
- **F Grand Return (ultimate):** a long window where EVERY fire or lightning attack that hits you is stored, then
  released as one blast. Lead: stored energy swirling around you, the release.

## 4. Combustion: "Mindfire", artillery (very rare innate gift)
Identity: long-range explosive artillery fired from the forehead (third-eye mark); must keep breathing steady.
Passive **Backfire**: being hit while casting makes the blast explode on YOU. Movement: none fast (slow and planted).
- **M1 Concussive String:** 4 short-range forehead pops (small explosions) at melee range. Lead: tiny combustion pops.
- **Z Mind Flare:** a thin beam from the forehead to a point, exploding there. Lead: the dense thin beam + the blast.
- **X Cluster:** three smaller blasts in a spread. Lead: three thin beams + three pops.
- **C Detonation Line:** a line of explosions marching forward along the ground. Lead: the marching blasts.
- **V Mine:** place a delayed blast at a point (it ticks, then blows). Lead: a pulsing mark + the blast.
- **F Sky Mortar (ultimate):** fire upward; a rain of combustion blasts falls on an area. Lead: the upward beam + the
  falling blasts.

## 5. Dragon Fire: "True Flame", legendary (sun-warrior ruins quest + a dragon trial)
Identity: the original, purest fire; supportive and spiritual as well as strong. Passive **Inner Fire**: your Heat
never drains below 30, and allies near you gain a little Heat. Movement: **Dragon Step** (a flowing, dance-like
dash).
- **M1 Dance String:** 4 flowing strikes that leave rainbow-edged fire trails (Dancing Dragon form motions).
- **Z True Flame:** a breath of rainbow-coloured fire (the dragons' true colours). Lead: the rainbow-banded torrent.
- **X Sun Mark:** a sun glyph under allies that buffs their damage. Lead: the glyph + rising rainbow flames.
- **C Dragon Coil:** a spiralling ring of true fire around you that pushes enemies out. Lead: the coil.
- **V Twin Dance:** a synced combo when another Dragon Fire player is near: both fire a joined spiral. Lead: two
  intertwined rainbow spirals.
- **F Rainbow Inferno (ultimate):** a vast column of rainbow fire roaring up from the ground and then outward. Lead:
  the rainbow column.

## Order of work
Matter -> Firebending -> Lightning -> Redirection -> Combustion -> Dragon Fire -> second pass (five different reads:
rushdown fists, bolts, a counter, beams+explosions, rainbow fire) -> export (`--merge`).
