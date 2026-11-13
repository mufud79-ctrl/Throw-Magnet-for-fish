# Figma prompt: Throw Magnet for Fish UI

Paste everything below the line into Figma (or a Claude session with the Figma MCP).

---

Create a Figma design file for the UI of **"Throw Magnet for Fish"**, a Roblox idle/fishing game. The game takes place underwater. The player throws a magnet down a canyon of 10 zones, catches fish, and puts them on a ranch where they earn cash every second. Build every screen as a real frame with **auto layout, components and variables**, so it can be rebuilt 1:1 as Roblox ScreenGuis (Frame, TextLabel, ImageLabel, UICorner, UIStroke, UIGradient).

## Canvas
- One page per group: **Foundations**, **Components**, **HUD**, **Windows**, **Popups**, **World UI**.
- Screens on 1920×1080 frames, shown over a blurred underwater game screenshot placeholder (blue-teal haze, sandy studded floor).
- Also make a 1280×720 version of the HUD to check scaling.

## Visual style (chunky Roblox simulator look)
- **Fonts:** "Luckiest Guy" for titles, big numbers and buttons. "Fredoka One" for body and labels. All text white with a **thick black outline** (stroke about 3–4 px, outside), except coloured values.
- **Window shell:** near-black body `#121219`, corner radius 24, a 6 px black outer stroke and a soft drop shadow. The **header bar** is a coloured gradient with faint diagonal light stripes and the window title in Luckiest Guy at the left. The **close button** at top-right is a red rounded square `#E0252B` with a white X and a black stroke.
- **Header colours by window:** Shop = orange→yellow `#FF9A1A → #FFD23F`. My Fish / Index / Welcome = magenta `#E81CC8 → #C43BE0`. Sell = red `#FF2E2E → #FF5A4A`. Gift = sky blue `#4FB8FF → #2E8BFF`. Odds = purple `#7A2FE0 → #A35BFF`. Settings = dark grey `#3A3D46 → #2A2C33`.
- **Buttons:** chunky rounded rectangles (radius 14) with a 3D bottom lip (a darker 6 px band underneath), black stroke, white Luckiest Guy text with outline, and a glossy diagonal highlight. Variants: **Green** `#5BE81E`, **Orange** `#FFB21A`, **Blue** `#2E9BFF`, **Red** `#F02B2B`, **Grey** `#4A4D57`. States: default, hover (brighter), pressed (lip collapsed), disabled.
- **Inner cards / rows:** `#1E1F27` with radius 16, or a white 3 px stroke for list rows. **Section pills** are a dark navy `#2C3142` capsule with a centred white title and thin grey lines extending to both sides.
- **Value tags:** small capsules on top of cards: "Good Value" blue, "Better Value" pink, "Great Value" orange, "Most Value" with a rainbow gradient border.
- **Money** is always green `#7CFF4F` Luckiest Guy with a green cash-stack icon. **Robux prices** use the Robux hexagon icon and a white number.
- **Rarity palette** (tile backgrounds and name colours). Each has a main colour and a top→bottom gradient:
  Common `#B4BCC8` (`#DDE2EA→#8A94A4`), Uncommon `#5BD15B` (`#8EEF6E→#2DA83A`), Rare `#3FA3FF` (`#72CBFF→#1E6FE0`), Epic `#A35BFF` (`#C88EFF→#7A2FE0`), Legendary `#FFB020` (`#FFE04D→#FF8A00`), Mythic `#FF4F7A` (`#FF86A6→#E01E4F`), Secret `#1C1C24` with a red accent `#FF2A2A`, Divine `#FFF1C4` (`#FFFFFF→#FFD45E`), Celestial `#8A4DFF→#3FE6FF` (diagonal).
- **Fish tiles:** a rounded square with the rarity gradient and soft vertical stripes, the fish thumbnail centred. **Locked** fish show a black silhouette and "???".
- **Icons:** cash stack, Robux hexagon, flexed arm (Strength), gear, fish, book (Index), red shopping basket (Shop), gift box, four-leaf clover (Luck), padlock, magnet. Use placeholders where needed and name each layer after its icon.

## Foundations page
Colour variables (everything above), text styles (Title 48, Header 36, Button 32, Body 22, Small 16) and an effects style for the outline and shadow.

## Components page
Window shell (header colour as a variant), close button, button (5 colours × 4 states), section pill, value tag, Robux price button, fish tile (9 rarities plus locked), list row, progress bar (green fill on a dark track with centred "x/y" text), slider, toggle (ON green / OFF red, white knob), capacity pill, search field and hotbar slot.

## HUD page (always on screen)
- **Left, vertically stacked:** two square HUD buttons, about 140 px, dark rounded with an icon and a big outlined label: **Index** (blue book) and **Shop** (red basket).
- **Right middle:** **My Fish** button (orange fish/paw-style icon, label "Fish").
- **Bottom-left counters:** a flexed-arm icon with the Strength number in big blue outlined text (`968`) and a small grey gear/upgrade button, and below it a cash icon with the money in big green outlined text (`$1.05T`).
- **Top centre:** a player card: circular avatar headshot with a gold ring, the username, and the total `$207M/s` in green underneath.
- **Bottom centre:** a 10-slot hotbar (1–0), translucent dark slots with the number in the corner.

## Windows page
1. **Shop** (orange header, blue **GIFT!** button with a present icon next to the close button). The body scrolls; show the full long frame:
   - **Featured: "ENCHANTED CLAM"** card (purple, sparkles, "New!" rainbow tag, ODDS button). A big clam/pearl illustration on the left, and a row of 6 fish odds tiles, each with % above (40, 27, 18, 10, 4, 1) and an income multiplier chip (110%…1200%). The 1% tile has a rainbow border. Below: Buy x1 / x3 / x10 green Robux buttons (79 / 199 / 649).
   - **"RAINBOW CLAM"** card with a LIMITED tag, rainbow background, "Opens a random Rainbow Giant fish!" and Buy x1 / x3 (99 / 249).
   - **Packs:** 4 green cash pack cards (stacks of cash growing bigger; +$31.1B / +$187B / +$373B / +$1.12T; 24 / 59 / 79 / 199 Robux), then 3 orange **Strength** pack cards (flexed arms; +50 / +125 / +180 Strength).
   - **Bait packs:** 4 purple cards of rainbow bait with ODDS (+3 / +10 / +35 / +60; 27 / 69 / 299 / 499).
   - **Gamepasses:** 2 wide cards, **x2 Cash** (blue, "Double cash from every fish!", 99) and **x2 Strength** (purple, "Double strength from every curl!", 149).
   - **Free Item:** a "Free Fish!" card ("Claim your free Goldfish!", `$200/s`). Show both the **Claim** state and the **Claimed!** state.
2. **My Fish** (magenta header, capacity pill "10/10" with a fish icon, close). Section header "ON YOUR RANCH 10/10". Scrolling list rows: a fish tile on the left; on the right a mutation line (e.g. **DIAMOND**, **GOLD**, in rarity-ish colour), the fish name in its rarity colour, a size tag (**BIG**) and income `$129M/s` in green; and two stacked buttons, **PICK UP** (blue) and **SELL** (red). Footer: a wide orange **EQUIP BEST** button.
3. **Fish Index** (magenta header). The body scrolls by **zone**. Each zone section has a tall coloured zone card on the left (zone name in big outlined text and a small blocky underwater diorama placeholder), a grid of fish tiles on the right (discovered = thumbnail and name; undiscovered = silhouette and "???"), and a progress bar "2/5" under the grid. Show Pond, River and Swamp. Footer bar: blue book icon and "Discovered: 12/50" with a green progress fill.
   Zones in order: Pond, River, Swamp, Coral Reef, Open Ocean, Frozen Sea, Deep Abyss, Volcanic Vent, Sunken Ruins, Starfall Lake.
4. **Sell Fish** (red header). Top card: "BACKPACK VALUE" with a cash icon and `$0`, and a grey **SELL ALL** button (green when there is something to sell). Body: the empty state "NO FISH IN BACKPACK", plus a filled variant listing fish rows with a value and a small sell button each.
5. **Settings** (grey header). Rows: **Music** slider (100%), **SFX** slider (100%), **Show Others' Fish** toggle (OFF), **Show Your Fish** toggle (ON).
6. **Inventory**: a translucent dark panel (no header colour) titled "Inventory", with a search field at top and the empty state "No other items" in the middle. Show it above the hotbar.

## Popups page
1. **Welcome Back!** (magenta header): "While you were away your fish earned", a dark green glowing card with a big cash icon and `$506B` in huge green text, "Away for 20h 20m", and two buttons: **CLAIM** (green) and **2X ⬡49** (orange).
2. **Clam Odds** (purple header, close): a scrolling list of rows (circular fish icon, name in rarity colour, income chip `550%`, chance `4%` on the right). The rarest row has a rainbow border. Footnote: "Every fish hatches plain: no mutation, normal size. Its % is what it earns compared with your best fish. Luck does not change these chances."
3. **Gift** (blue header, over the dimmed Shop): "Who do you want to gift?" and rows of players (round avatar, display name, @username, blue **GIFT** button).
4. **Catch banner** (top of screen, no window): a wide teal→green gradient banner with a black outline. "YOU CAUGHT" in small cream text, the fish name big in gold gradient text ("LARGE GOLD MEGALODON"), then "1 in 220". A big four-leaf clover overlaps the left edge, and a tilted "INSANE LUCK!" sticker sits at top-right. Variants: Lucky / Insane Luck / Mythic Luck in rising colours.
5. **Throw meter** (during a throw): a tall vertical capsule meter split into 6 segments, green at the top fading to yellow, orange and red at the bottom, with a white pill slider and a "+9" label next to it. "TAP TO THROW!" in huge outlined text under the meter.
6. **Luck boost offer** (top-right during a throw): a purple card with a rainbow edge, a big clover, "100x LUCK", a Robux price pill (9) and a blue **DETAILS** button.

## World UI page (BillboardGui / SurfaceGui designs)
- **Fish name tag** above each fish: a mutation line (small, coloured), the fish name in its rarity colour, a size tag, and `$15.6M/s` in green. Compact, outlined, no background.
- **Ranch upgrade sign** (a wooden studded sign in the world): a fish icon with "10 > 12" (the new number in green) and a green pill "▲ $40M".
- **Curl station label:** the price `$90B` in big green text, "+2,048 XP / rep" in blue, and a small down-arrow.
- **Leaderboards** (3 tall boards): **MOST FISH**, **TOP MONEY**, **LUCKIEST CATCH**. Each has a coloured header, a subtitle, 10 rows (rank badge, avatar, name, score) and the footer "Updates every minute".
- **Stall signs:** "BAIT SHOP" (blue/white) and "SELL" (red/white) in chunky outlined letters.
- **Zone signs** for the canyon: the zone number and name (e.g. "ZONE 4 · CORAL REEF") on a rounded plank with that zone's colour.

Keep everything original to this game: fish, clams, magnets and the underwater zones. Do not copy any other game's logo or art.
