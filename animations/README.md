# Fish animations

Every fish model is now rigged with the **same skeleton and bone names**:

```
Root ─┬─ Head ── Jaw
      ├─ Spine1 ── Spine2 ── Spine3 ── Spine4 ── Tail
      ├─ Pect_L
      └─ Pect_R
(+ Lure on the Anglerfish, + Neck_L / Neck_R on the Hydra Eel)
```

Roblox plays animations by bone name, so **each clip only needs uploading once**. That one AnimationId then works on every fish of any size.
The clips only rotate bones; they never move them, so a fish's size doesn't matter.

## Clips (30 fps, all loop)

| Clip | Frames | Use |
|---|---|---|
| `Idle` | 60 | hovering in place: gentle sway, fin paddle, slow jaw "breathing" |
| `Swim` | 30 | normal swimming |
| `Sprint` | 16 | fleeing or dashing, fins tucked |
| `Hooked` | 24 | struggling on the magnet: violent thrash, jaw snapping |
| `Flop` | 36 | landed out of water: curl, snap, gasp |
| `Showcase` | 90 | catch reveal: one full turn with a proud swim |
| `Eel_Idle`, `Eel_Swim` | 72, 36 | stronger S-wave for eels and serpents |
| `Ray_Idle`, `Ray_Swim` | 72, 48 | wing flapping for rays |
| `Angler_Idle` | 60 | Idle plus the swinging lure |
| `Hydra_Idle` | 60 | eel idle plus both extra heads weaving |

## Which fish use which clips

`Sprint`, `Hooked`, `Flop` and `Showcase` work for **every** fish. Use the Idle/Swim column below:

| Fish | Idle / Swim |
|---|---|
| All other fish (40) | `Idle` / `Swim` |
| ElectricEel, MorayEel, Oarfish, MagmaEel, SeaSerpent | `Eel_Idle` / `Eel_Swim` |
| HydraEel | `Hydra_Idle` / `Eel_Swim` |
| MantaRay, AuroraRay | `Ray_Idle` / `Ray_Swim` |
| Anglerfish | `Angler_Idle` / `Swim` |

## Setting it up in Roblox Studio

1. Import a fish's `.glb` (or `.fbx`) with the **3D Importer**. Rigged models import with their bones.
   If the model has no `AnimationController` with an `Animator` inside it, add one.
2. Open the **Animation Editor** and select the fish.
3. Click **⋯ → Import → From FBX Animation** and pick a file from this folder (e.g. `Swim.fbx`).
4. Turn on **Looping**, then **Publish to Roblox** to get the AnimationId.
5. Repeat for each clip (12 in total). Every fish then uses those same AnimationIds.

Fish with glowing parts have a `<Fish>_Glow` mesh skinned to the same rig.
**Not yet tested in Studio:** check that the glow MeshPart follows the bones on import.

The `.blend` file for each fish also holds its clips as Blender actions, for previewing or tweaking.
To change or add clips, edit `tools/blender/fishanim.py`, rebuild the fish, and run `tools/blender/export_anims.py`.
