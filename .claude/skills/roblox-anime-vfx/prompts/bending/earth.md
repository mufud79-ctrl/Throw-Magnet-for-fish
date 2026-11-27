Build the EARTH family of the bending game: Earthbending (base), Metalbending, Sandbending, Lavabending and Seismic
Sense. Read `prompts/bending/_shared.md` first.

## Element rules (lore)
Style: Hung Gar (rooted stances, power from the ground); the seismic master's style is Southern Praying Mantis.
Learned from the badgermoles. Neutral jing: wait, listen, strike at the right moment. **Must touch the ground to
bend**: weak in the air, on ships and on wooden floors. Metalbenders can't bend refined metal (platinum).

## Family mechanic: the arena is yours
Earth moves leave **solid props in the world** (boulders, pillars, walls, slabs) that persist for a while and can be
reused: thrown, kicked, stood on, hidden behind. Earth is the only family that reshapes the map. Each class uses props
differently: the base class builds and throws them, metal anchors cables to them, sand erodes them, lava melts them,
and seismic reads through them.

## Matter to paint (earth family)
`rock_chunk` meshes (3-4 boulder variants, cel-shaded, lit top / dark underside), `pillar` mesh (octagonal rock
column with strata), `slab` mesh, `earth_crack` (radial crack decal), `dust_burst` (cel dust, smooth), `debris_chips`,
`strata_wave` (rolling earth ridge, layered), `metal_cable` (strip with a bright edge), `metal_plate` mesh,
`spark_spray` (metal sparks), `sand_stream` (strip, flowing grains), `sand_devil` (spiral sand column), `sand_veil`
(smooth sand haze), `lava_flow` (molten strip with a dark crust edge), `crust_crack` (cooling crust decal),
`magma_glob`, `seismic_ring` (thin pulse ring on the ground), `echo_outline` (white silhouette outline of a revealed
player). Reuse: `impact_crater`, `haze_soft`, `ink_shards`, `anime_glint`, `molten_crack`, `dust_veil`.

---
## 1. Earthbending (base): "Bedrock", the builder-brawler
Identity: heavy, slow, unstoppable; controls space with props. Passive **Rooted**: while grounded, take less
knockback; airborne = weaker. Movement: **Earth Surf** (ride a moving ridge of earth).
- **M1 Stone String:** 4 hits: two stone-fist jabs, a stomp that kicks up a small rock, a kick that launches that
  rock. Lead: chunks of stone on each hit; the stomp crack.
- **Z Rock Pull:** stomp, rip a boulder out of the ground, hold it (can walk), throw it. Lead: the boulder tearing out
  of a crack (dust, debris), the throw arc, the shatter.
- **X Rising Column:** a pillar shoots up under the target and launches them; the pillar stays as a prop. Lead: the
  pillar punching up with a strata crack ring.
- **C Bulwark:** raise a wall in front of you (blocks projectiles; can be pushed forward as a ram). Lead: the wall
  rising in layers; dust skirt.
- **V Faultline:** stomp; a crack races forward along the ground and erupts in a line of jagged slabs. Lead: the
  crack line, then slabs bursting up in sequence.
- **F Mountainfall (ultimate):** a ring of huge pillars bursts up around the area, then you slam and they collapse
  inward onto the centre. Lead: the pillar ring + the collapse.

## 2. Metalbending: "Ironline", grapple and armour-breaker
Identity: mobile, precise, punishes armour. Passive **Impurity Sense**: enemies wearing bendable metal gear take
extra damage from you; **refined (platinum) gear is immune** (a real counter item). Movement: **Cable Swing** (shoot a
cable to a surface and swing/zip).
- **M1 Cable String:** 4 hits with metal-wrapped fists; the finisher whips a short cable. Lead: metal glints and
  sparks on contact.
- **Z Cable Lash:** a metal cable shoots out: on an enemy it pulls them in, on a surface it zips you there. Lead: the
  cable strip (bright edge) snapping taut; sparks on latch.
- **X Plate Storm:** tear metal plates from your gear/the ground; they orbit you and slice anyone near. Lead: a ring
  of spinning plates with motion smears.
- **C Crush:** crumple an enemy's metal gear (armour break, damage over time if they wear metal). Lead: their gear
  crumpling inward with sparks.
- **V Rail Spike:** fire a metal spike that pins the target to a wall or the ground. Lead: a fast spike + a pin
  impact.
- **F Iron Cage (ultimate):** wrap the target in a cage of bent metal plates and cables, then crush it shut. Lead:
  plates converging into a cage + the crush.

## 3. Sandbending: "Dune", vision and area denial (desert specialist)
Identity: blinds and buries; strongest in deserts and on sand. Passive **Shifting Sands**: standing on sand grants
damage and speed. Movement: **Dune Sail** (surf a fast stream of sand).
- **M1 Grain String:** 4 sand-blast hits; the finisher leaves a small sand cloud. Lead: sand streams per hit.
- **Z Sandblind:** a cloud of sand that blinds enemies inside (screen effect). Lead: a dense, smooth sand veil
  billowing out.
- **X Quicksand:** turn the ground into a sinking zone. Lead: a swirling sand whirlpool on the ground.
- **C Sandspout:** a moving sand tornado that carries enemies. Lead: a spiral sand column with debris.
- **V Sand Blade:** a compressed blade of sand flung forward (sand is finer than rock: fast, light). Lead: a thin sand
  crescent that dissolves into grains.
- **F Desert Storm (ultimate):** a sandstorm over the area: vision reduced for enemies, sand blades in the wind. Lead:
  the storm wall rolling in.

## 4. Lavabending: "Magma", high-risk terrain damage (rare innate gift)
Identity: melts the map; deadly zones; slow to set up. Passive **Heat Soak**: standing in your lava heals you a
little. Movement: **Lava Wave Ride** (surf a short lava wave; leaves a cooling trail).
- **M1 Molten String:** 4 hits with glowing molten fists; burns. Lead: molten splashes, crust flakes.
- **Z Melt:** turn the ground under a target into a lava pool. Lead: cracks glowing, then the ground slumping into
  lava with a crust edge.
- **X Magma Shot:** a lava glob that splashes. Lead: the glob arc + molten splash.
- **C Harden:** instantly cool all your lava: anyone standing in it is trapped in rock. Lead: lava going dark,
  crusting with steam bursts.
- **V Lava Wave:** a rolling wave of lava. Lead: the molten crest with a dark crust and embers.
- **F Molten Land (ultimate):** an area turns to lava in a spreading crack network; erupting magma spouts. Lead: the
  spreading cracks + spouts.

## 5. Seismic Sense: "Tremor", information and counters
Identity: sees through the ground; reads and punishes. Passive **Earth Sight**: grounded enemies within range are
outlined through walls; **blind to airborne enemies, fuzzy on sand**. Movement: **Ground Read** (an auto-dodge on a
cooldown while standing on earth).
- **M1 Mantis String:** 4 quick, precise hits (praying-mantis style) that interrupt. Lead: small crack pops.
- **Z Tremor Sense:** a stomp pulse that reveals all grounded enemies for 6 s. Lead: a seismic ring spreading across
  the ground; white outlines on revealed players.
- **X Echo Pulse:** a sharp pulse that interrupts casts and reveals invisible/projected players. Lead: a hard thin
  ring + a crack burst.
- **C Read:** a seismic parry: counter the next melee hit within a window. Lead: a ripple under your feet, then a
  rock jab counter.
- **V Pressure Point Stomp:** stomp under a target to trip them (they fall). Lead: the ground jolting under them.
- **F True Sight (ultimate):** your whole team sees every grounded enemy and your counters become automatic for a
  few seconds. Lead: a huge seismic ring and the world briefly drawn as white outlines.

## Order of work
Matter (meshes first: boulders, pillars, slabs) -> Earthbending -> Metal -> Sand -> Lava -> Seismic -> second pass
(five different reads) -> export (`--merge`).
