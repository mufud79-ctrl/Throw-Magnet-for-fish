#!/bin/bash
# Renders every god animation twice (plain + effects) into assets/previews/god_mode/anim/. Run from lab/.
set -e
A=../assets/previews/god_mode/anim; G=../assets/meshes/thunder_god/anim
r(){ node anim_render.mjs "$@" 2>&1 | tail -1; }
# plain (character framing)
r $G/idle.glb $A/idle_front34 --size 640x800 --yaw 22 --period 3.2 --zoom 1.08
r $G/idle.glb $A/idle_orbit --size 640x800 --yaw 0 --orbit 360 --loops 2 --period 3.2
r $G/idle.glb $A/idle_hands --size 900x640 --yaw 12 --pitch 4 --target 0.0,0.22,0.12 --dist 2.15 --period 3.2
r $G/cast.glb $A/cast --size 640x800 --yaw -55
r $G/drum_barrage.glb $A/drum_barrage --size 640x800 --yaw 35
r $G/drum_barrage.glb $A/drum_barrage_hands --size 900x700 --yaw 35 --pitch 4 --target 0.0,0.45,0.0 --dist 1.9
r $G/heavens_palm.glb $A/heavens_palm --size 640x800 --yaw -58 --zoom 1.0
r $G/thunder_gods_wrath.glb $A/thunder_gods_wrath --size 640x800 --yaw 35 --frame-at 3.3 --zoom 0.84
r $G/thunder_gods_wrath.glb $A/wrath_hands --size 900x700 --yaw 35 --pitch 2 --target 0.0,0.95,0.0 --dist 2.3
r $G/transform.glb $A/transform --size 800x800 --yaw 28 --pitch 12 --frame-at 3.4 --zoom 0.72
# effects (wider framing so targets, pillars and the sky are in shot)
r $G/idle.glb $A/idle_front34_vfx --vfx $G/idle.vfx.json --size 640x800 --yaw 22 --period 3.2 --zoom 1.08
r $G/idle.glb $A/idle_orbit_vfx --vfx $G/idle.vfx.json --size 640x800 --yaw 0 --orbit 360 --loops 2 --period 3.2
r $G/idle.glb $A/idle_hands_vfx --vfx $G/idle.vfx.json --size 900x640 --yaw 12 --pitch 4 --target 0.0,0.22,0.12 --dist 2.15 --period 3.2
r $G/cast.glb $A/cast_vfx --vfx $G/cast.vfx.json --size 640x800 --yaw -42 --pitch 9 --target 0.15,0.25,2.6 --dist 9.5
r $G/drum_barrage.glb $A/drum_barrage_vfx --vfx $G/drum_barrage.vfx.json --size 640x800 --yaw 24 --pitch 14 --target 0.0,0.0,2.3 --dist 11.5
r $G/drum_barrage.glb $A/drum_barrage_hands_vfx --vfx $G/drum_barrage.vfx.json --size 900x700 --yaw 35 --pitch 4 --target 0.0,0.45,0.0 --dist 1.9
r $G/heavens_palm.glb $A/heavens_palm_vfx --vfx $G/heavens_palm.vfx.json --size 640x800 --yaw -66 --pitch 8 --target 0.0,0.9,2.3 --dist 12
r $G/thunder_gods_wrath.glb $A/thunder_gods_wrath_vfx --vfx $G/thunder_gods_wrath.vfx.json --size 640x800 --yaw 30 --pitch 12 --target 0.0,1.0,2.0 --dist 13.5
r $G/thunder_gods_wrath.glb $A/wrath_hands_vfx --vfx $G/thunder_gods_wrath.vfx.json --size 900x700 --yaw 35 --pitch 2 --target 0.0,0.95,0.0 --dist 2.3
r $G/transform.glb $A/transform_vfx --vfx $G/transform.vfx.json --size 800x800 --yaw 25 --pitch 10 --target 0.0,1.0,0.0 --dist 11.5
