# Assets pipeline

## Painting (photocraft)
Textures are painted on float images at 2x and downsampled with Lanczos (`scripts/photocraft.py`):
metaball lobes and domain-warped noise for organic forms; heightfield lighting for painted volume; levels for
crisp-but-soft edges; directional/radial smudge; strokes painted as straight strips then bent with a polar warp;
distance-from-edge gradients for painted fire/magma (thin rim, body, hot core). Intensity images split into
four white layers (`split`): glow (blurred, additive), rim, mid, core. Shaded textures keep greyscale value as
painted light/shadow (smoke, dust, mist, drops). Always paint greyscale; colour belongs to the emitter.

Adding a texture: write a recipe in `vfx_textures.py` returning frames (layered) or (alphas, values) (shaded),
register it in `LIB` with kind, grid and a preview palette, run it + `texture_preview.py`, look at the frames,
then show the user via `gallery.py`.

## Meshes (Blender, bpy)
`scripts/vfx_meshes.py` builds shells from parametric surfaces: crescents (pointed both ends, coned), rings,
sphere/dome, tubes, swirls, faceted spikes, curved claws and clusters, wave curl, torus, disc, fang blade.
UV u runs along the stroke, v across, matching the strip textures. Double-sided in geometry. Budget in polys.

## Meshy (organic hero meshes)
Text-to-3D preview only (geometry; ~20 credits each per the CLI planner), then `scripts/retopo_hero.py`:
join -> voxel remesh solved for a target polycount (watertight, all quads; QuadriFlow is an async job and never
finishes in headless bpy) -> centre, fit a 2-stud box -> smart UV -> FBX/OBJ/JSON. Current heroes: dragon_head,
giant_fist, phoenix_bird (~3,200 polys each). Facing is set per move with `rot`.

## Figma image generation (painted silhouettes)
For shapes procedural painting does badly (creatures, hands): prompt for "hand-painted 2D anime special effect
sprite ... monochrome greyscale, isolated on pure black". Results may come back with a transparent background;
`art()` in `vfx_textures.py` uses brightness x alpha either way and splits into layers. Current: dragon_head,
phoenix_wing, giant_fist, water_shark, palm_strike. Download the PNG immediately (links expire in 7 days).
