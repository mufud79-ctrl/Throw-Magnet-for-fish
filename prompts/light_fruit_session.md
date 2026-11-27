# Session prompt: Light fruit (moveset + VFX)

Paste everything below the line into a new Claude Code session.

---

You're building the **Light fruit** moveset and its VFX. It follows the Dragon fruit work. Everything we learned on Dragon applies from the very first render, so don't relearn it through review rounds.

## Step 0: the Wisteria reference (do this first, before designing anything)
I mentioned a light-sword look from **Wisteria** as a reference. The last session couldn't identify it: a search found no light-sword character or style in Wisteria, only the general game overview and the "Sword of Light" gear. **Don't guess.**
1. Ask me for a **video link** (YouTube or clip) or the **exact character or skill name**.
2. If it's a video, pull 6–10 frames at the key moments (wind-up, the main shape, impact, fade) and put them in `prompts/refs/light/`.
3. Write down in 3–5 bullets what the reference does: the main shape, colour ramp, timing and what's left on screen afterwards. Show me that summary and wait for my OK before you design anything.

## Rules carried over from Dragon (follow them from render one)
1. **Anime shape style.** Bold, clean, readable shapes with hard silhouettes and smooth colour ramps. Nothing noisy, photoreal or particle-soup.
2. **One main shape per move.** Every move has one dominant form (a lance, a ring, a pillar) that reads in a single frame. Everything else supports it and stays smaller and dimmer.
3. **A smooth outside haze.** The main shape sits inside a soft, smooth outer glow or haze that fades out evenly. No hard edge, no banding and no visible card edges.
4. **Less clutter.** Cut secondary sparks, streaks and debris until the main shape is obvious. When in doubt, remove it.
5. **A real crater.** Ground impacts leave an actual crater mesh (a depressed bowl with a raised, broken rim and debris chunks), not a flat decal or a ring on the floor.
6. **Gameplay camera only.** Review every move from the real gameplay camera (third-person, over the shoulder, at normal distance). No hero, close-up or cinematic angles for sign-off.
7. **60 fps.** Author and preview at 60 fps. Timing is judged at 60.
8. **Texture mistakes to avoid:** *TODO, fill in from the Dragon session's notes.* The list was agreed there but isn't in this repo. Ask me for it if you can't find it.
9. **Export only with `--merge`.** Every export goes through the exporter with `--merge`; never export unmerged. *TODO: name the script. The Dragon exporter isn't in this repo, so ask me where it lives if it's missing.*

## The ultimate: "you become light" (confirmed concept)
- The avatar turns into a **glowing white-gold silhouette**, a solid bright body with a smooth outer haze (rule 3), not a mesh full of particles.
- It **blinks between targets at light speed**: each blink is an instant reposition with a thin, short-lived light trail along the path, then a hit flash on the target. Chain several targets, keeping the rhythm readable at 60 fps.
- It ends in a **burst of rays** from the final position: one radial ray burst as the main shape, then a fast fade back to the normal avatar.

## The other five moves (PROPOSALS: confirm with me before building)
These names and concepts are suggestions. Show me the list and get my OK or changes first.

| Move | Main shape | Idea |
|---|---|---|
| **Photon Lance** | a long light spear | throw a single piercing lance of light in a straight line |
| **Flashstep** | a short light streak | a quick dash: vanish, then reappear a short distance ahead with a flash |
| **Prism Volley** | a fan of light shards | fire a spread of prism shards that split the light into a white-gold edge |
| **Sunfall** | a vertical light pillar | call down a pillar of light that leaves a **real crater** (rule 5) |
| **Mirror Halo** | a ring of light | a ring around the player that reflects or blocks, then pulses outward |

## Workflow
- Step 0 first, then confirm the five moves, then build the ultimate, then the rest one at a time.
- One render per move from the gameplay camera at 60 fps. At most one fix round per move.
- Commit and push after each move.
