"""Export each animation clip as its own FBX (rig + one take) for Roblox's Animation Editor import.
python export_anims.py  -> animations/<Clip>.fbx"""
import bpy, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fishanim import SHARED, LENGTH
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF = {c: "Common/Carp" for c in SHARED}
REF.update({"Eel_Idle": "Rare/MorayEel", "Eel_Swim": "Rare/MorayEel", "Ray_Idle": "Epic/MantaRay", "Ray_Swim": "Epic/MantaRay",
            "Angler_Idle": "Epic/Anglerfish", "Hydra_Idle": "Secret/HydraEel"})
out = os.path.join(root, "animations"); os.makedirs(out, exist_ok=True)
for clip, ref in REF.items():
    name = ref.split("/")[-1]
    bpy.ops.wm.open_mainfile(filepath=os.path.join(root, "models", ref, name + ".blend"))
    arm = bpy.data.objects[f"{name}_Rig"]; act = bpy.data.actions[clip]
    arm.animation_data.action = act
    if act.slots: arm.animation_data.action_slot = act.slots[0]
    sc = bpy.context.scene; sc.frame_start, sc.frame_end = 0, LENGTH[clip]; sc.render.fps = 30
    bpy.ops.object.select_all(action="DESELECT")
    for o in bpy.data.objects:
        if o.type in ("ARMATURE", "MESH"): o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=os.path.join(out, clip + ".fbx"), use_selection=True, add_leaf_bones=False,
                             bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                             bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0, path_mode="STRIP")
    print("EXPORTED", clip)
