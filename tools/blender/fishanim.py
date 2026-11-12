"""Animation clip library. Clips only rotate bones, so they work on every fish rig (same bone names).

Shared (all fish): Idle, Swim, Sprint, Hooked, Flop, Showcase
Unique families:   Eel_Idle, Eel_Swim (eels/serpents), Ray_Idle, Ray_Swim (rays),
                   Angler_Idle (lure), Hydra_Idle (extra heads)
"""
import bpy, math
from mathutils import Quaternion

D = math.radians
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
SPINE = ["Spine1", "Spine2", "Spine3", "Spine4", "Tail"]
SHARED = ["Idle", "Swim", "Sprint", "Hooked", "Flop", "Showcase"]
FAMILY = {"fish": [], "eel": ["Eel_Idle", "Eel_Swim"], "ray": ["Ray_Idle", "Ray_Swim"],
          "angler": ["Angler_Idle"], "hydra": ["Eel_Idle", "Eel_Swim", "Hydra_Idle"]}

def merge(*ds):
    out = {}
    for d in ds:
        for k, q in d.items(): out[k] = out[k] @ q if k in out else q
    return out
def wave(w, amps, ph, head, axis=Z):
    d = {b: Quaternion(axis, D(amps[i]) * math.sin(w - ph * (i + 1))) for i, b in enumerate(SPINE)}
    d["Head"] = Quaternion(axis, D(head) * math.sin(w)); return d
def pect(w, amp, tuck=0.0):
    a = D(amp) * math.sin(w)
    return {"Pect_L": Quaternion(Z, D(tuck)) @ Quaternion(X, a), "Pect_R": Quaternion(Z, -D(tuck)) @ Quaternion(X, a)}
def jaw(amount): return {"Jaw": Quaternion(X, D(amount))}          # + closes the (modelled-open) jaw
def root(yaw=0.0, pitch=0.0): return {"Root": Quaternion(Y, yaw) @ Quaternion(X, pitch)}

def flop_curve(fr):
    if fr < 5: return math.sin(fr / 5 * math.pi / 2)
    if fr < 11: return 1.0
    if fr < 22: return 1 - 1.5 * (fr - 11) / 11
    return -0.5 * (1 - (fr - 22) / 14)

def clip(name, fr, T):
    w = 2 * math.pi * fr / T
    if name == "Idle":   return merge(wave(w, [1.5, 2, 2.5, 3, 4], 0.8, 1.5), pect(2 * w, 14), jaw(4 * (0.5 + 0.5 * math.sin(w))), root(pitch=D(2) * math.sin(w)))
    if name == "Swim":   return merge(wave(w, [3, 4, 5, 7, 10], 0.9, 3), pect(w, 22, 10), jaw(2 * (0.5 + 0.5 * math.sin(w))))
    if name == "Sprint": return merge(wave(w, [4, 6, 8, 10, 14], 1.0, 4), pect(2 * w, 8, 45))
    if name == "Hooked":
        sp = {b: Quaternion(Z, D(6 + i) * math.sin(w + 0.35 * i) + D(3) * math.sin(3 * w + i)) for i, b in enumerate(SPINE)}
        return merge(sp, {"Head": Quaternion(Z, -D(10) * math.sin(w + 0.4))}, pect(3 * w, 35), jaw(20 * (0.5 + 0.5 * math.sin(4 * w))),
                     root(D(12) * math.sin(w) + D(5) * math.sin(3 * w + 1), D(7) * math.sin(2 * w + 0.5)))
    if name == "Flop":
        cv = flop_curve(fr)
        sp = {b: Quaternion(Z, -cv * D(6 + 1.5 * i)) for i, b in enumerate(SPINE)}
        return merge(sp, {"Head": Quaternion(Z, cv * D(14))}, pect(6 * w, 25), jaw(14 * max(cv, 0)))
    if name == "Showcase": return merge(wave(w, [2, 3, 4, 5, 7], 0.9, 2), pect(2 * w, 18), root(w, D(8) * math.sin(w)))
    if name == "Eel_Idle": return merge(wave(w, [5, 5, 5, 5, 6], 1.2, 4), pect(2 * w, 12))
    if name == "Eel_Swim": return merge(wave(w, [10, 10, 10, 11, 12], 1.35, 6), pect(w, 18), jaw(3 * (0.5 + 0.5 * math.sin(w))))
    if name == "Ray_Idle": return merge(pect(w, 14), wave(w, [1, 2, 3, 4, 8], 0.7, 1, X), wave(w, [0, 0, 1, 2, 6], 0.9, 0))
    if name == "Ray_Swim": return merge(pect(w, 38), wave(w, [2, 3, 4, 5, 10], 0.7, 2, X), wave(w, [0, 0, 1, 3, 10], 0.9, 0))
    if name == "Angler_Idle": return merge(clip("Idle", fr, T), {"Lure": Quaternion(Z, D(18) * math.sin(w)) @ Quaternion(X, D(10) * math.sin(2 * w))})
    if name == "Hydra_Idle":
        return merge(clip("Eel_Idle", fr, T), {"Head": Quaternion(Z, D(6) * math.sin(w + 1)),
                     "Neck_L": Quaternion(Z, D(15) * math.sin(w)) @ Quaternion(X, D(10) * math.sin(2 * w + 1)),
                     "Neck_R": Quaternion(Z, D(15) * math.sin(w + 2)) @ Quaternion(X, D(10) * math.sin(2 * w + 2.5))})
    raise KeyError(name)

LENGTH = {"Idle": 60, "Swim": 30, "Sprint": 16, "Hooked": 24, "Flop": 36, "Showcase": 90,
          "Eel_Idle": 72, "Eel_Swim": 36, "Ray_Idle": 72, "Ray_Swim": 48, "Angler_Idle": 60, "Hydra_Idle": 60}

def make_action(arm, name):
    T = LENGTH[name]
    act = bpy.data.actions.new(name); act.use_fake_user = True; act["frames"] = T
    arm.animation_data_create(); arm.animation_data.action = act
    for pb in arm.pose.bones: pb.rotation_mode = "QUATERNION"
    for fr in range(T + 1):
        pose = clip(name, fr % T, T)
        for pb in arm.pose.bones:
            pb.rotation_quaternion = pose.get(pb.name, Quaternion())
            pb.keyframe_insert("rotation_quaternion", frame=fr)
    return act

def add_actions(arm, family="fish"):
    acts = [make_action(arm, n) for n in SHARED + FAMILY[family]]
    arm.animation_data.action = None
    for pb in arm.pose.bones: pb.rotation_quaternion = Quaternion()
    return acts
