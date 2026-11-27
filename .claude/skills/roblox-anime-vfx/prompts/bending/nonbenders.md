Build the NON-BENDER classes: Chi-blocker, Weapon Master and Engineer. Read `prompts/bending/_shared.md` first. Non-
benders must be a real choice: they counter benders and get the biggest bonuses during eclipses (when benders lose
bending).

## Rules (lore)
Chi-blocking: precise pressure-point strikes that temporarily disable a bender's bending and limbs. Weapon masters:
swords, fans, boomerangs, bows. Engineers (the later, industrial era): electrified gloves, grapples, glider suits.
No bending, no element glow: their effects are physical (impacts, motion smears, sparks, dust) plus a small accent
colour per class.

## Matter
`strike_pop` (a sharp small impact star, cel), `chi_node` (a glowing point on a body that dims when blocked),
`limb_numb` (a fading tint on a limb), `blade_smear` (a crisp sword arc), `fan_gust` (non-bending fan swipe lines),
`boomerang_trail`, `arrow_streak`, `shock_arc` (small electric arcs), `grapple_line` (cable strip), `glider_trail`.
Reuse: `anime_slash`, `ink_shards`, `speed_burst`, `anime_glint`, `dust_burst`.

---
## 1. Chi-blocker: "Pressure Point", the bending shutdown
Identity: fast, close-range, acrobatic; every hit stacks **Chi-block** on the target; at 5 stacks the target loses
bending for 3 s (and that limb's moves are disabled). Passive **Flow Break**: hits on a target mid-cast interrupt it.
Movement: **Cartwheel** (an evasive acrobatic dash).
- **M1 Jab String:** 4 rapid finger-strikes (each +1 stack). Lead: small strike pops on chi points.
- **Z Nerve Strike:** a 3-hit flurry on one target (+3 stacks). Lead: three pops racing up an arm.
- **X Leg Lock:** strike the legs: the target is slowed. Lead: pops + a fading limb tint.
- **C Vault:** flip over a target and strike from behind. Lead: a smear arc of the flip + a back strike pop.
- **V Feint:** a fake that baits a counter, then a punish. Lead: a ghosted afterimage.
- **F Full Shutdown (ultimate):** a long flurry that sets the target to max stacks (bending gone for 5 s). Lead: a
  sequence of pops tracing the chi paths, then all nodes dimming.

## 2. Weapon Master: "Steel", the duelist
Identity: parries and reach; picks one weapon set (dual broadswords, war fans, boomerang + sword, bow). Passive
**Parry**: a timed block reflects melee and stuns. Movement: **Step-in** (a lunge).
- **M1 Blade String:** 4 weapon strikes (per weapon set). Lead: crisp blade smears.
- **Z Riposte:** a parry stance; on a hit, counter-slash. Lead: a spark clash + a fast smear.
- **X Whirl:** spinning slashes around you. Lead: a ring of smears.
- **C Return Blade / Fan Gust / Volley:** the weapon set's ranged move (boomerang that returns, a fan swipe that
  pushes, an arrow volley). Lead: the thrown weapon's trail.
- **V Disarm:** knock an enemy's weapon/gear away (debuff). Lead: a sharp clang star.
- **F Thousand Cuts (ultimate):** a dash through a group with a flurry of slashes that land a beat later. Lead: the
  dash line + the delayed cuts popping.

## 3. Engineer: "Gearwright", gadgets (later-era tech)
Identity: tools that hard-counter specific elements. Passive **Prepared**: gadgets recharge faster during eclipses and
storms. Movement: **Grapple Line** (fire a grapple and reel to a point).
- **M1 Glove String:** 4 hits with a shock glove (a small stun chance). Lead: small shock arcs.
- **Z Shock Glove:** a charged punch that stuns (strong vs water-soaked targets). Lead: arcs wrapping the fist + a
  pop.
- **X Bola:** a thrown bola that tangles the legs. Lead: the spinning bola + the wrap.
- **C Smoke Bomb:** a smoke cloud that blinds and hides you. Lead: a smooth grey cloud.
- **V Glider Suit:** deploy a glider for aerial movement. Lead: the glider trail.
- **F Mech Walker (ultimate, short):** summon and pilot a small walker for a few seconds (big punches, a flame or
  shock arm). Lead: the walker landing + its punches.

## Order of work
Matter -> Chi-blocker -> Weapon Master (one weapon set first: dual broadswords) -> Engineer -> second pass -> export
(`--merge`).
