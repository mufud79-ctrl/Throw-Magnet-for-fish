# The five animation rules, in data and in Roblox

| Rule | In the spec (scripts/effects.py) | In Roblox (templates/.../AnimeVFX) |
|---|---|---|
| 1 Anticipation | `charge()`: aura on the caster, inward particles (Sphere shape, Inward), orb that grows then pinches (Size keys 0.2 -> 1 -> 0.6 -> 0.85) and snaps to the hand. `pose_throw()` / per-archetype `pose`: lean back, arm cocked, body squash. | Particles/shells play as authored. `spec.pose` is the beat guide for your AnimationTracks (wind-up -> release -> overshoot -> settle). |
| 2 Squash & stretch | Projectile core: `Orientation = VelocityParallel`, small Speed along travel, `Squash = 0.9` (stretch). Hits: `SQUASH_HIT` on burst stacks (squash -0.45 -> stretch 0.28 -> 0). Shells: non-uniform scale keys (flat, then tall). Targets: `spec.hits` (previewer squashes the dummy). | `ParticleEmitter.Squash` NumberSequence; SpecialMesh.Scale per axis. Target squash belongs in a hit-reaction animation: use `opts.onHit`. |
| 3 Follow-through | `follow_through()`: sparks fired Front along the travel direction, a secondary burst carried forward (moving attachment, ease out), smoke with sideways acceleration. Trails emit backwards with drag. Caster pose overshoots then settles. | Same data. |
| 4 Timing | `hit()` appends `spec.hitstop {t, dur}` (0.03 multi-hit ticks, 0.06-0.1 hits, 0.11-0.16 finishers). Impact frames sit at the hit time. | Runtime holds effect time, sets every emitter `TimeScale = 0`, pauses caster/target AnimationTracks (`AdjustSpeed(0)`), keeps shaking, shows impact frames during the freeze. |
| 5 Arcs | `move.arc` on projectiles (and barrages, alternating sides), gravity on sparks (`Acceleration` -30..-45), ballistic debris, damage numbers `vel` + gravity. | Attachment paths use the same arc formula; debris and numbers are computed (not physics) so every client matches. |

Hit-stop length scales with hit weight; multi-hit beams/barrages use tiny stops (0.03-0.04) or they feel sticky.
Impact frames (invert/mono/white) flash for 2-3 frames at the start of the freeze; never longer.
