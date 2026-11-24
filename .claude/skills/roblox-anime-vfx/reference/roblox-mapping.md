# Spec ↔ Roblox mapping and emulator fidelity

## Spec format

```js
const { stack, steps, flicker } = G.VFXSpec;
G.VFX_EFFECTS.MyEffect = {
  name: 'MyEffect', version: 1, duration: 2.6,          // seconds; cleanup at duration + 0.25
  stage: { camera: [x,y,z], target: [x,y,z],            // viewer only: framing, dummy, sword swing
           dummy: { pos, face, sword: 'steel'|'fire'|null }, swing: [[t, deg], ...] },
  beats: [[t, 'label'], ...],                           // scrubber ticks + chips
  lights: [{ name, position, Color, Range, Brightness: [[t, v], ...] }],
  impactFrames: [{ t, dur, Brightness, Contrast, Saturation, TintColor?, Void?, Highlight?: { FillColor } }],
  shakes: [{ t, dur, amp, freq }],
  layers: [
    ...stack({ name, role, ref, position, rotation?, emits,          // hero: 4 aligned emitters
               props: { Texture: 'fx_blast', FlipbookLayout, FlipbookMode: 'OneShot', Lifetime: [L, L], Size, ... } },
             { glow: { Color, Transparency: steps(flicker(0.45, 0.12, 9, 3), 1) }, rim: { Color }, mid: { Color }, core: { Color, Brightness } }),
    { name, role, ref, position: [x,y,z], rotation: [rx,ry,rz],  // degrees, CFrame.Angles order
      part: { Size: [x,y,z] }, emits: [[t, count]], rate: [[t0, t1, perSecond]], props: { ... } },
  ],
};
```

Value shorthand: NumberSequence `[[t, v, env], ...]` (t from 0 to 1, at most 20 keys);
NumberRange `[min, max]`; ColorSequence `[[t, '#hex'], ...]` or `'#hex'`; Vector2/3 arrays;
enums as strings (`'VelocityParallel'`).

## Emulator fidelity

| Feature | Status |
|---|---|
| Size / Transparency / Squash sequences with envelopes | exact eval (envelope random per particle) |
| Color sequence × texture × Brightness | exact |
| LightEmission | exact model: alpha blend → additive (`a·(1-LE)` dest factor) |
| LightInfluence | approximated by a scene light level (dusk 0.55, day 1) |
| Lifetime, Speed, Rotation, RotSpeed, Acceleration | exact |
| Drag | modeled as velocity halving every `1/Drag` s. Verify feel in Studio |
| Shapes: Box, Sphere (+ShapePartial cap around EmissionDirection), Cylinder (Y axis, radial), Disc (XZ) | close. Check Cylinder axis in Studio |
| ShapeStyle / ShapeInOut | exact |
| SpreadAngle | approximate distribution |
| Orientation: all 4 modes | exact geometry |
| Flipbook: layouts, OneShot/Loop/PingPong/Random, Framerate, StartRandom | exact frame order (L→R, T→B) |
| Squash | approximate curve (positive = taller and thinner) |
| ZOffset | moves the quad toward the camera + sorts emitters, like Roblox |
| Sorting within an emitter | back-to-front, like Roblox |
| Bloom | approximates Lighting.BloomEffect (Intensity ~1, Threshold ~1, Size 24) |
| ColorCorrection | exact formula as used here (brightness, contrast, saturation, tint) |
| Void + Highlights | emulated as background swap + unlit dummy fill |
| Part rotation (`rotation`) | exact (Euler XYZ = CFrame.Angles); in-plane angle of VelocityPerpendicular quads may differ, so check in Studio |
| Not emulated | Beams, Trails, MeshParts/tweens, wind, LockedToPart on moving parts, VelocityInheritance |

## Studio-side notes

- **Textures:** 1024² PNGs (flipbooks must be square, power of two). Bulk Import in Asset
  Manager, then copy each id into the `TEXTURES` table in the `.lua`.
- **Where to call it:** put the module in ReplicatedStorage. The server fires a RemoteEvent; each
  client calls `require(module).Play(CFrame.new(pos))`. This keeps particles smooth and lets
  impact frames and shake run.
- **Void sphere:** a SpecialMesh sphere with negative Scale renders inside-out, which gives a
  solid backdrop during B/W frames. If a game already uses Atmosphere/Sky tricks, swap to those.
- **Performance:** the reference effect peaks around 250 particles. Keep any effect under ~400
  live particles for mobile. Bigger, fewer particles are both cheaper and more anime.
- **Lighting:** the Future lighting tech makes PointLights cast on terrain. The `BlastLight`
  peaks at Brightness 9 for one frame; lower it if your map uses strong Bloom.
