"""Cannon Tame animal roster rebuilt in the TFFA style (skill: .claude/skills/tffa-animal-models).

usage: /tmp/bpyenv/bin/python tools/blender/tffa_zoo.py [Zone or Animal names ...] [--no-render] [--sheet]
Writes models/CannonTame/Animals/<Zone>/<Name>/ (replacing old contents). Gorilla, TRex, Cow and Phoenix come from the
hand-reviewed example scripts; everything else from archetype specs below. --sheet makes one contact sheet per zone."""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SKILL = os.path.join(ROOT, ".claude", "skills", "tffa-animal-models")
sys.path.insert(0, os.path.join(SKILL, "scripts"))
ARGS = sys.argv[1:]
sys.argv = sys.argv[:1] + [a for a in ARGS if a == "--no-render"]
from tffa_archetypes import *

Q, B, A = quad, bird, ape
EX = "example"      # built by examples/<file>.py
ZONES = [
 ("01_Farm", [
   ("Chicken", B, dict(body=(1.6, 1.4, 1.5), leg=0.6, head=1.0, c1=WHITE, beak_c=YELLOW, leg_c=ORANGE, wing_c=rgb(232, 232, 236), x=[comb()])),
   ("Duck", B, dict(body=(1.9, 1.4, 1.2), leg=0.45, head=1.0, c1=rgb(160, 136, 108), head_c=rgb(40, 140, 80), beak=(0.48, 0.66, 0.22), beak_top=(0.9, 0.95), beak_c=ORANGE, belly=rgb(214, 200, 176), wing_c=rgb(120, 100, 80))),
   ("Pig", Q, dict(body=(2.6, 1.9, 1.7), legs=(0.7, 0.55), head=(1.3, 1.6, 1.3), neck=(0, 0.5), c1=PINKC, snout=(0.4, 0.9, 0.65), snout_c=rgb(255, 140, 165), nose_c=rgb(200, 80, 105), ears="floppy", tail="curly")),
   ("Sheep", Q, dict(body=(2.4, 1.9, 1.7), legs=(0.9, 0.45), head=(1.0, 1.05, 1.1), neck=(0.1, 0.6), c1=WHITE, leg_c=DGREY, head_c=DGREY, snout_c=DGREY, nose_c=BLACK, ears="floppy", ear_c=DGREY, tail="short", x=[wool()])),
   ("Goat", Q, dict(body=(2.4, 1.4, 1.5), legs=(1.0, 0.45), head=(1.1, 1.0, 1.0), neck=(0.5, 0.9), c1=rgb(236, 230, 214), ears="floppy", tail="short", feet=DGREY, snout_c=rgb(220, 210, 190), x=[horns("goat", rgb(170, 150, 120)), beard(rgb(200, 190, 170))])),
   ("Cow", EX, "cow"),
   ("Horse", Q, dict(body=(3.0, 1.75, 1.75), legs=(1.6, 0.56), head=(1.8, 1.05, 1.05), neck=(1.3, 1.0), c1=BROWN, snout=(0.75, 0.9, 0.8), snout_c=rgb(172, 124, 88), nostrils=True, nose_c=DBROWN, ears="point", tail="tuft", tail_c=rgb(58, 38, 28), tail_tip=rgb(58, 38, 28), feet=DBROWN, side_eyes=True, x=[mane_back(rgb(58, 38, 28))])),
 ]),
 ("02_Forest", [
   ("Squirrel", Q, dict(body=(1.4, 1.0, 1.0), legs=(0.45, 0.32), head=(0.95, 0.95, 0.9), neck=(0.1, 0.8), c1=rgb(200, 104, 50), belly=CREAM, ears="point", tail="up", snout=(0.25, 0.5, 0.35), snout_c=CREAM)),
   ("Rabbit", Q, dict(gait=dict(hop=True), body=(1.5, 1.1, 1.1), legs=(0.4, 0.38), head=(1.0, 1.0, 0.95), neck=(0.1, 0.8), c1=rgb(206, 186, 164), belly=WHITE, ears="long", tail="short", tail_c=WHITE, snout=(0.25, 0.55, 0.4), snout_c=WHITE, nose_c=PINKC)),
   ("Hedgehog", Q, dict(body=(1.4, 1.1, 0.9), legs=(0.25, 0.28), head=(0.75, 0.75, 0.65), neck=(0, 0.3), c1=rgb(230, 200, 160), snout=(0.4, 0.35, 0.3), ears="tiny", x=[hedgehog_spikes(rgb(110, 80, 55))])),
   ("Fox", Q, dict(body=(2.0, 0.95, 1.0), legs=(0.75, 0.32), head=(1.0, 1.05, 0.9), neck=(0.2, 0.7), c1=rgb(236, 120, 40), belly=WHITE, snout=(0.55, 0.5, 0.4), snout_c=WHITE, ears="point", tail="bushy", feet=DBROWN)),
   ("Raccoon", Q, dict(body=(1.8, 1.2, 1.1), legs=(0.5, 0.38), head=(1.0, 1.15, 0.9), neck=(0.1, 0.6), c1=GREY, snout=(0.35, 0.5, 0.35), snout_c=WHITE, ears="round", tail="bushy", tail_tip=DGREY, x=[mask(rgb(40, 40, 46))])),
   ("Owl", B, dict(body=(1.3, 1.3, 1.8), leg=0.3, head=1.35, c1=BROWN, belly=CREAM, beak=(0.25, 0.28, 0.32), beak_c=YELLOW, eye=1.45, upright=True, iris=rgb(255, 214, 60), x=[tufts(BROWN)])),
   ("BrownBear", Q, dict(body=(3.0, 2.2, 2.2), legs=(1.0, 0.8), head=(1.5, 1.7, 1.45), neck=(0.2, 0.4), c1=BROWN, snout=(0.6, 0.95, 0.7), snout_c=TAN2, ears="round", tail="short", angry=True)),
 ]),
 ("03_Savanna", [
   ("Meerkat", A, dict(torso=(0.8, 0.65, 1.4), leg=0.4, head=0.75, c1=rgb(212, 180, 128), arm=0.6, arm_w=0.2, lean=0.05, ears="tiny", tail="long", x=[eye_patches(DBROWN)])),
   ("Warthog", Q, dict(body=(2.4, 1.4, 1.4), legs=(0.7, 0.45), head=(1.4, 1.35, 1.2), neck=(0, 0.3), c1=rgb(136, 112, 96), snout=(0.5, 0.95, 0.6), ears="point", tail="tuft", angry=True, x=[tusks("up"), mane_back(DBROWN, 6)])),
   ("Zebra", Q, dict(body=(2.8, 1.3, 1.6), legs=(1.5, 0.48), head=(1.5, 0.95, 0.95), neck=(1.1, 1.0), c1=WHITE, pattern="stripes", pat_c=rgb(36, 36, 42), pat_n=6, snout=(0.5, 0.8, 0.65), snout_c=DGREY, ears="point", tail="tuft", tail_tip=BLACK, feet=BLACK, side_eyes=True, x=[mane_back(BLACK)])),
   ("Ostrich", B, dict(fly=False, body=(2.0, 1.6, 1.4), leg=2.0, neck=1.6, head=0.75, c1=rgb(40, 40, 46), neck_c=rgb(226, 182, 172), head_c=rgb(226, 182, 172), leg_c=rgb(226, 182, 172), beak=(0.4, 0.35, 0.22), beak_c=TAN, wing_c=WHITE, tail_c=WHITE)),
   ("Hyena", Q, dict(body=(2.2, 1.25, 1.4), legs=(0.9, 0.45), head=(1.2, 1.15, 1.0), neck=(0.3, 0.5), c1=rgb(196, 164, 112), pattern="spots", pat_c=DBROWN, snout=(0.5, 0.65, 0.5), snout_c=DBROWN, ears="round", tail="tuft", angry=True, x=[mane_back(DBROWN, 4)])),
   ("Giraffe", Q, dict(body=(2.4, 1.4, 1.7), legs=(2.0, 0.48), head=(1.2, 0.9, 0.85), neck=(3.0, 1.2), c1=rgb(242, 190, 80), pattern="spots", pat_c=rgb(160, 96, 42), pat_n=6, snout=(0.45, 0.7, 0.6), snout_c=rgb(230, 200, 150), ears="point", tail="tuft", tail_tip=DBROWN, feet=DBROWN, x=[horns("ossicone", rgb(230, 180, 80)), mane_back(rgb(160, 96, 42), 6)])),
   ("Rhino", Q, dict(body=(3.2, 2.0, 2.0), legs=(0.9, 0.8), head=(1.6, 1.4, 1.2), neck=(0.1, 0.2), c1=GREY, snout=(0.9, 1.15, 0.9), ears="point", tail="short", angry=True, x=[horns("rhino")])),
 ]),
 ("04_Jungle", [
   ("Frog", EX, "dartfrog"),   # hero build (reference analysis in the script)
   # v1: ("Frog", frog, dict(c1=rgb(90, 196, 70), belly=rgb(236, 230, 120))),
   ("Toucan", EX, "toucan"),   # hero build
   # v1: ("Toucan", B, dict(body=(1.4, 1.15, 1.5), leg=0.5, head=1.05, c1=rgb(36, 36, 42), belly=YELLOW, beak=(1.5, 0.65, 0.6), beak_c=ORANGE, wing_c=rgb(30, 30, 36), x=[bill_tip()])),
   ("Monkey", EX, "capuchin"),   # hero build
   # v1: ("Monkey", A, dict(torso=(1.0, 0.85, 1.3), leg=0.6, head=1.05, c1=BROWN, face_c=NOUGAT, ears="round", ear_c=NOUGAT, tail="long")),
   ("Sloth", EX, "sloth"),   # hero build
   # v1: ("Sloth", A, dict(torso=(1.4, 1.1, 1.5), leg=0.45, head=1.05, lean=0.1, c1=rgb(176, 154, 122), face_c=CREAM, x=[eye_patches(DBROWN)])),
   ("Panther", Q, dict(body=(3.8, 1.7, 1.55), legs=(1.65, 0.64), head=(1.55, 1.55, 1.0), neck=(0.6, 0.22), c1=rgb(52, 48, 68), snout=(1.0, 1.0, 0.72), snout_c=rgb(54, 52, 70), nose_c=rgb(18, 18, 24), feet=rgb(30, 28, 40), ears="cat", tail="long", tail_w=1.7, tail_c=rgb(40, 38, 52), angry=True, snarl=True, iris=rgb(205, 250, 60), brow=rgb(16, 16, 22), head_scale=1.3, muscular=True, front_back=0.07, x=[])),
   ("Crocodile", Q, dict(body=(3.4, 1.9, 1.15), legs=(0.45, 0.55), sprawl=0.3, head=(1.5, 1.65, 0.95), neck=(0, 0.1), c1=rgb(72, 128, 62), belly=CREAM, snout=(1.9, 1.3, 0.62), snout_c=rgb(82, 140, 70), tail="thick", angry=True, head_scale=1.35, eye=1.5, side_eyes=True, x=[spine_spikes(rgb(52, 92, 46), 7), jaw_teeth(7)])),
   ("Gorilla", EX, "silverback"),   # hero build on the reviewed TFFA gorilla (examples/gorilla.py stays the style reference)
 ]),
 ("05_Arctic", [
   ("Penguin", EX, "penguin"),   # hero build (reference analysis in the script)
   # v1: ("Penguin", B, dict(fly=False, body=(1.4, 1.4, 2.0), leg=0.25, head=1.15, c1=rgb(36, 40, 56), belly=WHITE, beak=(0.42, 0.34, 0.22), beak_c=ORANGE, upright=True, wing=0.5, wing_c=rgb(30, 34, 48))),
   ("ArcticFox", EX, "arcticfox"),   # hero build (reference analysis in the script)
   # v1: ("ArcticFox", Q, dict(body=(2.0, 0.95, 1.0), legs=(0.7, 0.32), head=(1.0, 1.05, 0.9), neck=(0.2, 0.7), c1=WHITE, snout=(0.5, 0.5, 0.4), ears="point", tail="bushy", tail_tip=LBLUE, iris=LBLUE)),
   ("Seal", EX, "seal"),   # hero build (reference analysis in the script)
   # v1: ("Seal", seal, dict(c1=rgb(156, 166, 178))),
   ("SnowOwl", EX, "snowowl"),   # hero build (reference analysis in the script)
   # v1: ("SnowOwl", B, dict(body=(1.3, 1.3, 1.8), leg=0.3, head=1.35, c1=WHITE, belly=SNOW, beak=(0.25, 0.28, 0.32), beak_c=DGREY, eye=1.45, upright=True, iris=rgb(255, 214, 60), x=[tufts(WHITE)])),
   ("Husky", EX, "husky"),   # hero build (reference analysis in the script)
   # v1: ("Husky", Q, dict(body=(2.3, 1.2, 1.4), legs=(1.0, 0.48), head=(1.2, 1.15, 1.1), neck=(0.3, 0.6), c1=GREY, belly=WHITE, snout=(0.5, 0.65, 0.5), snout_c=WHITE, ears="point", tail="up", tail_c=GREY, iris=LBLUE)),
   ("Walrus", EX, "walrus"),   # hero build (reference analysis in the script)
   # v1: ("Walrus", seal, dict(c1=rgb(160, 106, 74), s=1.4, angry=True, x=[tusks("walrus"), whiskers()])),
   ("PolarBear", EX, "polarbear"),   # hero build (reference analysis in the script)
   # v1: ("PolarBear", Q, dict(body=(3.2, 2.3, 2.3), legs=(1.0, 0.85), head=(1.6, 1.7, 1.45), neck=(0.3, 0.4), c1=WHITE, snout=(0.6, 0.95, 0.7), ears="round", tail="short", angry=True, iris=LBLUE)),
 ]),
 ("06_Desert", [
   ("Lizard", Q, dict(body=(2.0, 0.95, 0.6), legs=(0.3, 0.32), sprawl=0.25, head=(0.9, 0.85, 0.6), neck=(0, 0.2), c1=rgb(186, 176, 92), pattern="spots", pat_c=rgb(124, 112, 52), snout=(0.5, 0.65, 0.35), tail="long", head_scale=1.2)),
   ("Scorpion", scorpion, dict(c1=rgb(64, 52, 52), c2=rgb(150, 64, 40))),
   ("FennecFox", Q, dict(body=(1.8, 0.95, 1.0), legs=(0.7, 0.32), head=(1.0, 1.05, 0.9), neck=(0.2, 0.7), c1=SAND, belly=WHITE, snout=(0.5, 0.5, 0.4), snout_c=WHITE, ears="fennec", tail="bushy", tail_tip=BLACK)),
   ("Rattlesnake", snake, dict(c1=rgb(196, 164, 100), c2=rgb(112, 80, 50))),
   ("Camel", Q, dict(body=(2.8, 1.4, 1.6), legs=(1.9, 0.48), head=(1.3, 0.9, 0.8), neck=(1.6, 1.0), c1=TAN2, snout=(0.5, 0.75, 0.6), snout_c=rgb(190, 150, 100), ears="tiny", tail="tuft", side_eyes=True, x=[hump(2)])),
   ("Vulture", B, dict(body=(1.8, 1.45, 1.4), leg=0.6, neck=0.4, head=0.75, c1=rgb(72, 56, 46), neck_c=rgb(232, 150, 140), head_c=rgb(232, 150, 140), beak=(0.45, 0.32, 0.32), beak_c=LGREY, angry=True, x=[ruff()])),
   ("SphinxCat", Q, dict(body=(2.1, 1.2, 1.3), legs=(0.85, 0.42), head=(1.1, 1.15, 1.0), neck=(0.3, 0.7), c1=rgb(234, 192, 162), snout=(0.35, 0.6, 0.45), ears="fennec", tail="long", iris=rgb(130, 230, 120), x=[headdress()])),
 ]),
 ("07_IceAge", [
   ("WoollyHare", Q, dict(gait=dict(hop=True), body=(1.7, 1.3, 1.3), legs=(0.4, 0.42), head=(1.1, 1.05, 1.0), neck=(0.1, 0.8), c1=CREAM, ears="long", tail="short", snout=(0.25, 0.55, 0.4), snout_c=WHITE, nose_c=PINKC, x=[wool(SNOW)])),
   ("GiantBeaver", Q, dict(body=(2.5, 1.6, 1.4), legs=(0.5, 0.52), head=(1.2, 1.35, 1.1), neck=(0.1, 0.4), c1=rgb(124, 82, 52), snout=(0.4, 0.85, 0.55), snout_c=rgb(156, 112, 76), ears="tiny", tail="flat", tail_tip=rgb(72, 62, 56), x=[buck_teeth(rgb(245, 190, 80))])),
   ("GiantSloth", A, dict(torso=(2.4, 1.8, 2.6), leg=0.9, head=1.4, lean=0.2, c1=rgb(164, 122, 82), face_c=TAN2, arm_w=0.6)),
   ("Glyptodon", Q, dict(body=(2.9, 2.4, 1.4), legs=(0.55, 0.6), head=(1.0, 1.05, 0.85), neck=(0, 0.2), c1=rgb(124, 102, 82), ears="tiny", tail="thick", x=[shell(rgb(166, 134, 92), rgb(112, 86, 60))])),
   ("WoollyRhino", Q, dict(body=(3.4, 2.1, 2.1), legs=(0.9, 0.8), head=(1.6, 1.4, 1.2), neck=(0.1, 0.2), c1=rgb(146, 102, 62), snout=(0.9, 1.15, 0.9), ears="point", tail="short", angry=True, x=[horns("rhino"), fur_coat(rgb(156, 108, 62))])),
   ("Sabertooth", Q, dict(body=(2.7, 1.4, 1.5), legs=(1.0, 0.52), head=(1.3, 1.25, 1.1), neck=(0.3, 0.5), c1=rgb(216, 164, 92), pattern="stripes", pat_c=rgb(156, 102, 50), pat_n=4, snout=(0.45, 0.75, 0.55), snout_c=CREAM, ears="round", tail="short", angry=True, x=[fangs()])),
   ("Mammoth", Q, dict(body=(3.8, 2.6, 2.6), legs=(1.5, 0.95), head=(2.0, 2.1, 2.0), neck=(0, 0.3), c1=rgb(118, 64, 36), snout=(0.5, 0.95, 0.9), snout_c=rgb(104, 56, 32), ears="tiny", ear_c=rgb(92, 50, 28), tail="tuft", tail_tip=rgb(70, 38, 22), head_scale=1.3, fierce=True, muscular=True, x=[shaggy(rgb(118, 64, 36), rgb(90, 48, 27)), tusks("mammoth"), trunk(rgb(110, 60, 34))])),
 ]),
 ("08_DinoLand", [
   ("Compy", theropod, dict(s=0.32, c1=rgb(154, 206, 72), c2=rgb(92, 144, 50))),
   ("Parasaurolophus", Q, dict(body=(3.4, 2.0, 2.2), legs=(1.4, 0.75), head=(1.3, 1.05, 1.0), neck=(1.5, 0.9), c1=rgb(72, 166, 154), pattern="stripes", pat_c=rgb(42, 112, 112), snout=(0.9, 0.85, 0.45), snout_c=rgb(206, 186, 124), tail="thick", side_eyes=True, x=[crest(rgb(236, 142, 60))])),
   ("Triceratops", Q, dict(body=(3.6, 2.6, 2.4), legs=(1.1, 0.9), head=(1.8, 1.9, 1.6), neck=(0, 0.2), c1=rgb(206, 122, 60), snout=(0.6, 0.95, 0.7), tail="thick", side_eyes=True, head_scale=1.2, x=[frill(rgb(246, 184, 70))])),
   ("Stegosaurus", Q, dict(body=(3.8, 2.2, 2.4), legs=(1.2, 0.9), head=(1.1, 0.95, 0.8), neck=(0.8, 0.0), c1=rgb(112, 156, 82), belly=CREAM, snout=(0.5, 0.65, 0.45), tail="thick", side_eyes=True, x=[plates(rgb(236, 122, 60))])),
   ("Ankylosaurus", Q, dict(body=(3.8, 2.8, 1.6), legs=(0.7, 0.9), head=(1.4, 1.7, 1.0), neck=(0, 0.1), c1=rgb(146, 124, 72), snout=(0.4, 1.05, 0.6), tail="thick", angry=True, x=[shell(rgb(124, 102, 62), rgb(92, 76, 46), spikes=True), club_tail(rgb(102, 86, 56))])),
   ("TRex", EX, "trex"),
   ("Spinosaurus", theropod, dict(s=1.1, snout=1.5, c1=rgb(62, 114, 146), c2=rgb(36, 72, 98), x=[sail(rgb(226, 92, 60))])),
 ]),
 ("09_Volcano", [
   ("MagmaSlug", EX, "magmaslug"),   # hero build (reference analysis in the script)
   # v1: ("MagmaSlug", blob, dict(c1=rgb(64, 48, 48), size=(3.0, 1.6, 1.2), stalks=True, glow=rgb(255, 120, 30), x=[glow_bits(rgb(255, 120, 30), 6, 4, "top", 0.4)])),
   ("FireSalamander", EX, "firesalamander"),   # hero build (reference analysis in the script)
   # v1: ("FireSalamander", Q, dict(body=(2.2, 1.0, 0.65), legs=(0.32, 0.34), sprawl=0.25, head=(1.0, 0.95, 0.6), neck=(0, 0.2), c1=rgb(44, 40, 46), snout=(0.4, 0.75, 0.35), tail="long", head_scale=1.2, glow=rgb(255, 140, 30), x=[glow_bits(rgb(255, 140, 30), 10, 5, "body", 0.35)])),
   ("EmberWolf", EX, "emberwolf"),   # hero build (reference analysis in the script)
   # v1: ("EmberWolf", Q, dict(body=(2.5, 1.2, 1.4), legs=(1.0, 0.48), head=(1.2, 1.15, 1.0), neck=(0.3, 0.6), c1=rgb(58, 52, 56), snout=(0.5, 0.65, 0.5), ears="point", tail="long", angry=True, iris=rgb(255, 150, 40), glow=rgb(255, 120, 30), x=[flame_mane(rgb(255, 120, 30))])),
   ("ObsidianGolem", EX, "obsidiangolem"),   # hero build (reference analysis in the script)
   # v1: ("ObsidianGolem", golem, dict(c1=rgb(44, 36, 56), c2=rgb(74, 52, 106), glowc=rgb(200, 90, 255), glow=rgb(200, 90, 255))),
   ("LavaDrake", dragon, dict(s=0.85, studded=True, muscular=True, c1=rgb(150, 30, 24), c2=rgb(64, 20, 18), mem=rgb(104, 24, 20), belly=rgb(255, 150, 40), seg=rgb(255, 110, 20), belly_glow=True, knob=rgb(255, 150, 40), horn=rgb(44, 32, 32), eye=rgb(255, 170, 50), eye_glow=True, spikes=rgb(44, 30, 30), glow=rgb(255, 110, 20))),
   ("LavaRex", EX, "lavarex"),   # hero build (reference analysis in the script)
   # v1: ("LavaRex", theropod, dict(s=1.05, c1=rgb(58, 46, 46), c2=rgb(32, 26, 30), belly=rgb(255, 146, 44), iris=rgb(255, 130, 30), eye_glow=True, glow=rgb(255, 110, 20), x=[rex_cracks(rgb(255, 110, 20))])),
   ("Phoenix", EX, "phoenix"),
 ]),
 ("10_MythicIsles", [
   ("Jackalope", Q, dict(gait=dict(hop=True), body=(1.6, 1.15, 1.15), legs=(0.42, 0.4), head=(1.0, 1.05, 0.95), neck=(0.1, 0.8), c1=rgb(196, 154, 112), belly=WHITE, ears="long", tail="short", tail_c=WHITE, snout=(0.25, 0.55, 0.4), snout_c=WHITE, nose_c=PINKC, fierce=True, x=[horns("jackalope", rgb(236, 214, 172)), buck_teeth()])),
   ("Griffin", Q, dict(body=(2.8, 1.6, 1.6), legs=(1.0, 0.56), head=(1.2, 1.15, 1.1), neck=(0.6, 0.8), c1=rgb(216, 164, 92), head_c=WHITE, neck_c=WHITE, snout=(0.55, 0.55, 0.45), snout_c=YELLOW, nose_c=YELLOW, tail="tuft", tail_tip=rgb(150, 104, 62), angry=True, fierce=True, muscular=True, head_scale=1.5, x=[wings(rgb(150, 104, 62), 0.55, False, rgb(250, 230, 200), kind="feather", wide=1.7, spread=0.8), talons(), beak_head()])),
   ("Pegasus", Q, dict(equine=True, head_kit="horse_wedge", head_k=0.74, body=(3.0, 1.45, 1.6), legs=(1.6, 0.5), head=(1.3, 0.95, 1.0), neck=(1.3, 1.0), c1=WHITE, snout_c=rgb(242, 232, 242), mane_c=LBLUE, tail="flow", tail_c=LBLUE, tail_tip=rgb(110, 170, 240), feet=GOLD, x=[mane_back(LBLUE), wings(rgb(236, 240, 255), 0.55, False, LBLUE, kind="feather", wide=1.7, spread=0.8)])),
   ("Unicorn", Q, dict(equine=True, head_kit="horse_wedge", head_k=0.74, body=(3.0, 1.45, 1.6), legs=(1.6, 0.5), head=(1.3, 0.95, 1.0), neck=(1.3, 1.0), c1=WHITE, snout_c=rgb(255, 230, 245), mane_c=PINK, horn=GOLD, tail="flow", tail_c=PINK, tail_tip=LAVENDER, feet=GOLD, glow=rgb(255, 220, 120), x=[mane_back(PINK)])),
   ("Chimera", EX, "chimera"),   # custom build from the user reference; v1 (quad + chimera_bits) archived in models/CannonTame/Animals/_Archive/Chimera_v1
   # v1: ("Chimera", Q, dict(head_kit="lion_sunburst", head_k=0.62, snarl=True, body=(3.4, 1.75, 1.7), legs=(1.35, 0.66), head=(1.5, 1.5, 1.0), neck=(0.5, -0.12), c1=rgb(196, 140, 82), mane=rgb(120, 62, 34), mane2=rgb(156, 86, 42), snout_c=rgb(232, 204, 156), nose_c=rgb(50, 30, 26), iris=rgb(255, 140, 30), eye_glow=True, glow=rgb(255, 140, 30), tail=None, muscular=True, front_back=0.07, x=[chimera_bits(), talons()])),
   ("Kraken", EX, "kraken"),   # custom hero build from the user reference; v1 archived in models/CannonTame/Animals/_Archive/Kraken_v1
   # v1: ("Kraken", kraken, dict(c1=rgb(150, 28, 52), c2=rgb(84, 16, 34), sucker=rgb(236, 150, 150), iris=rgb(255, 214, 60))),
   ("CelestialDragon", dragon, dict(s=0.85, studded=True, muscular=True, c1=rgb(238, 240, 255), c2=rgb(150, 170, 220), mem=rgb(150, 200, 255), belly=GOLD, seg=rgb(214, 150, 30), knob=rgb(120, 230, 255), horn=GOLD, eye=CYAN, eye_glow=True, spikes=rgb(120, 230, 255), glow=rgb(120, 230, 255))),
 ]),
 ("11_Space", [      # hero builds (reference analysis in each script's docstring); v1 one-line specs kept below as comments
   ("MoonBunny", EX, "moonbunny"),
   ("AlienBlob", EX, "alienblob"),
   ("SpaceCat", EX, "spacecat"),
   ("AstroDog", EX, "astrodog"),
   ("StarWhale", EX, "starwhale"),
   ("GalaxyDragon", EX, "galaxydragon"),
   ("BlackHoleBeast", EX, "blackholebeast"),
 ]),
# v1  ("11_Space", [
# v1    ("MoonBunny", Q, dict(gait=dict(hop=True), body=(1.6, 1.2, 1.2), legs=(0.45, 0.4), head=(1.1, 1.05, 1.0), neck=(0.1, 0.8), c1=rgb(206, 210, 226), pattern="spots", pat_c=rgb(152, 158, 180), pat_n=3, ears="long", tail="short", tail_c=WHITE, snout=(0.25, 0.55, 0.4), snout_c=WHITE, nose_c=PINKC, glow=rgb(255, 240, 150), x=[crescent(rgb(255, 240, 150))])),
# v1    ("AlienBlob", blob, dict(c1=rgb(112, 232, 92), size=(2.4, 2.2, 2.0), eye_y=(0.45, 0.0, -0.45), glow=rgb(200, 255, 120), x=[glow_bits(rgb(200, 255, 120), 4, 9, "top", 0.3)])),
# v1    ("SpaceCat", Q, dict(body=(2.1, 1.2, 1.3), legs=(0.85, 0.45), head=(1.2, 1.2, 1.05), neck=(0.3, 0.7), c1=rgb(74, 52, 124), snout=(0.35, 0.6, 0.45), snout_c=rgb(110, 84, 160), ears="point", tail="long", iris=CYAN, glow=rgb(150, 220, 255), x=[glow_bits(rgb(150, 220, 255), 10, 11, "body", 0.22), astro(rgb(224, 224, 238), rgb(120, 200, 255))])),
# v1    ("AstroDog", Q, dict(body=(2.3, 1.3, 1.4), legs=(0.9, 0.48), head=(1.2, 1.15, 1.1), neck=(0.3, 0.6), c1=WHITE, snout=(0.5, 0.65, 0.5), snout_c=rgb(242, 222, 202), ears="floppy", ear_c=rgb(206, 144, 92), tail="short", glow=CYAN, x=[astro()])),
# v1    ("StarWhale", whale, dict(c1=rgb(44, 44, 116), belly=rgb(124, 112, 206), glow=rgb(255, 240, 180), x=[glow_bits(rgb(255, 240, 180), 14, 21, "body", 0.3), glow_bits(rgb(255, 240, 180), 8, 22, "top", 0.3)])),
# v1    ("GalaxyDragon", Q, dict(body=(3.2, 1.8, 1.8), legs=(1.2, 0.72), head=(1.5, 1.25, 1.1), neck=(1.6, 0.8), c1=rgb(64, 32, 116), belly=rgb(42, 164, 206), snout=(0.9, 0.9, 0.65), tail="dragon", tail_tip=MAGENTA, angry=True, iris=MAGENTA, side_eyes=True, glow=rgb(255, 120, 230),
# v1         x=[horns("goat", rgb(204, 164, 255)), wings(rgb(64, 32, 116), 1.2, False, rgb(124, 62, 206)), spine_spikes(rgb(255, 120, 230), 6, True), glow_bits(rgb(255, 240, 200), 10, 31, "body", 0.2)])),
# v1    ("BlackHoleBeast", Q, dict(body=(2.7, 1.4, 1.6), legs=(1.0, 0.52), head=(1.3, 1.25, 1.1), neck=(0.3, 0.5), c1=rgb(30, 26, 40), snout=(0.5, 0.7, 0.5), snout_c=rgb(46, 40, 60), ears="point", tail="long", angry=True, iris=rgb(210, 110, 255), glow=rgb(200, 90, 255),
# v1         x=[hole_ring(rgb(200, 90, 255)), spine_spikes(rgb(124, 52, 206), 6, True)])),
# v1  ]),
]

def sheet(zone):
    from tffa_kit import bpy
    import numpy as np
    folder = os.path.join(ROOT, "models", "CannonTame", "Animals", zone)
    tiles = []
    for name in sorted(os.listdir(folder)):
        p = os.path.join(folder, name, "previews", f"{name}_hero.png")
        if os.path.exists(p):
            im = bpy.data.images.load(p); w, h = im.size
            tiles.append(np.array(im.pixels[:], np.float32).reshape(h, w, 4)[::2, ::2])
    if not tiles: return
    th, tw = tiles[0].shape[:2]; cols = 4; rows = (len(tiles) + cols - 1) // cols
    out = np.ones((rows * th, cols * tw, 4), np.float32)
    for i, t in enumerate(tiles):
        r, cc = divmod(i, cols); r = rows - 1 - r; out[r * th:(r + 1) * th, cc * tw:(cc + 1) * tw] = t
    im = bpy.data.images.new("sheet", cols * tw, rows * th); im.pixels.foreach_set(out.ravel())
    im.filepath_raw = os.path.join(folder, f"{zone}_overview.png"); im.file_format = "PNG"; im.save()
    print("SHEET", im.filepath_raw)
    strips = []                                   # animation review: every animal's clip rows, downscaled
    for name in sorted(os.listdir(folder)):
        p = os.path.join(folder, name, "previews", f"{name}_anim.png")
        if os.path.exists(p):
            im = bpy.data.images.load(p); w, h = im.size
            a = np.array(im.pixels[:], np.float32).reshape(h, w, 4)[::3, ::3]
            pad = np.ones((a.shape[0], 1680 // 3 + 1 - a.shape[1] if a.shape[1] < 1680 // 3 + 1 else 0, 4), np.float32)
            strips.append(np.concatenate([a, pad], 1) if pad.shape[1] else a)
    if strips:
        W = max(x.shape[1] for x in strips)
        strips = [np.concatenate([x, np.ones((x.shape[0], W - x.shape[1], 4), np.float32)], 1) if x.shape[1] < W else x for x in strips]
        out = np.concatenate(strips[::-1], 0)
        im = bpy.data.images.new("asheet", out.shape[1], out.shape[0]); im.pixels.foreach_set(out.ravel())
        im.filepath_raw = os.path.join(folder, f"{zone}_anim_overview.png"); im.file_format = "PNG"; im.save()

if __name__ == "__main__":
    want = [a for a in ARGS if not a.startswith("--")]
    for zone, animals in ZONES:
        for name, arch, P in animals:
            if want and zone not in want and name not in want: continue
            out = os.path.join(ROOT, "models", "CannonTame", "Animals", zone, name)
            print("BUILD", zone, name, flush=True)
            if arch == EX:
                import shutil
                if os.path.isdir(out): shutil.rmtree(out)
                cmd = [sys.executable, os.path.join(SKILL, "examples", f"{P}.py"), out] + (["--no-render"] if "--no-render" in ARGS else [])
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
            elif "--child" in ARGS:
                try:
                    build(name, arch, P, out, views=[("hero", 40, 12, 45), ("front", 0, 8, 45), ("side", 90, 4, 45)])
                except Exception as e:
                    import traceback; traceback.print_exc(); print("FAILED", name, e)
            else:     # one Blender process per animal: renders leak memory, a whole zone in one process got OOM-killed
                cmd = [sys.executable, os.path.abspath(__file__), name, "--child"] + [a for a in ARGS if a == "--no-render"]
                r = subprocess.run(cmd, capture_output=True, text=True)
                print("\n".join(l for l in r.stdout.splitlines() if l.startswith(("CLIPS", "FAILED", "TRIS"))), flush=True)
                if r.returncode: print("FAILED", name, r.returncode, r.stderr[-800:], flush=True)
        if "--sheet" in ARGS and "--child" not in ARGS and (not want or zone in want or any(n in want for n, _, _ in animals)):
            sheet(zone)
