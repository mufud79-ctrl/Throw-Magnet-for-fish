"""Shared data for the UI tools: the 50 fish, rarity palette and water areas.

Plain Python (no bpy), so both the Blender render scripts and the PIL/XML tools import it.
Water areas are placeholders chosen to fit each fish; rename them to match the real map.
"""
import re

RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic", "Secret", "Divine", "Celestial"]

# name -> (main, gradient top, gradient bottom, accent)  all hex
PALETTE = {
    "Common":    ("#B4BCC8", "#DDE2EA", "#8A94A4", "#FFFFFF"),
    "Uncommon":  ("#5BD15B", "#8EEF6E", "#2DA83A", "#D8FFC8"),
    "Rare":      ("#3FA3FF", "#72CBFF", "#1E6FE0", "#D2EEFF"),
    "Epic":      ("#A35BFF", "#C88EFF", "#7A2FE0", "#EBD8FF"),
    "Legendary": ("#FFB020", "#FFE04D", "#FF8A00", "#FFF4C0"),
    "Mythic":    ("#FF4F7A", "#FF86A6", "#E01E4F", "#FFD6E0"),
    "Secret":    ("#1C1C24", "#3A3A48", "#0C0C12", "#FF2A2A"),
    "Divine":    ("#FFF1C4", "#FFFFFF", "#FFD45E", "#FFC22E"),
    "Celestial": ("#8A4DFF", "#8A4DFF", "#3FE6FF", "#FFFFFF"),
}
OUTLINE = "#1B1530"          # the dark outline used everywhere

FISH = {
    "Common": ["Minnow", "Goldfish", "Bluegill", "Guppy", "Perch", "Carp", "Catfish", "Sardine", "Clownfish", "BlueTang"],
    "Uncommon": ["Koi", "LargemouthBass", "RainbowTrout", "Salmon", "Mudskipper", "Pufferfish", "Angelfish", "Flounder", "Seahorse"],
    "Rare": ["Pike", "Sturgeon", "Piranha", "ElectricEel", "Lionfish", "MorayEel", "Icefish", "Lanternfish"],
    "Epic": ["AlligatorGar", "Arapaima", "MantaRay", "HammerheadShark", "GreenlandShark", "Anglerfish", "Blobfish"],
    "Legendary": ["GreatWhiteShark", "Sailfish", "CrystalPike", "Oarfish", "MagmaEel", "Coelacanth"],
    "Mythic": ["AuroraRay", "GhostShark", "EmberKoi", "GoldenArowana"],
    "Secret": ["Megalodon", "HydraEel", "SeaSerpent"],
    "Divine": ["DragonKoi", "SeraphFish"],
    "Celestial": ["StarfallWhaleShark"],
}

AREA = {
    "Minnow": "Starter Pond", "Goldfish": "Starter Pond", "Guppy": "Starter Pond", "Bluegill": "Starter Pond",
    "Perch": "Willow River", "Carp": "Willow River", "Catfish": "Murky Swamp", "Sardine": "Open Ocean",
    "Clownfish": "Coral Reef", "BlueTang": "Coral Reef",
    "Koi": "Starter Pond", "LargemouthBass": "Willow River", "RainbowTrout": "Willow River", "Salmon": "Willow River",
    "Mudskipper": "Murky Swamp", "Pufferfish": "Coral Reef", "Angelfish": "Coral Reef", "Flounder": "Open Ocean",
    "Seahorse": "Coral Reef",
    "Pike": "Frozen Lake", "Sturgeon": "Willow River", "Piranha": "Murky Swamp", "ElectricEel": "Murky Swamp",
    "Lionfish": "Coral Reef", "MorayEel": "Coral Reef", "Icefish": "Frozen Lake", "Lanternfish": "Deep Trench",
    "AlligatorGar": "Murky Swamp", "Arapaima": "Murky Swamp", "MantaRay": "Open Ocean", "HammerheadShark": "Open Ocean",
    "GreenlandShark": "Frozen Lake", "Anglerfish": "Deep Trench", "Blobfish": "Deep Trench",
    "GreatWhiteShark": "Open Ocean", "Sailfish": "Open Ocean", "CrystalPike": "Frozen Lake", "Oarfish": "Deep Trench",
    "MagmaEel": "Volcano Vents", "Coelacanth": "Deep Trench",
    "AuroraRay": "Frozen Lake", "GhostShark": "Shipwreck Cove", "EmberKoi": "Volcano Vents", "GoldenArowana": "Sky Lagoon",
    "Megalodon": "Abyss", "HydraEel": "Abyss", "SeaSerpent": "Abyss",
    "DragonKoi": "Sky Lagoon", "SeraphFish": "Sky Lagoon",
    "StarfallWhaleShark": "Cosmic Rift",
}

# Fish shown as discovered in the static layout / preview (12, matching the "12/50" counter)
DISCOVERED = ["Minnow", "Goldfish", "Guppy", "Clownfish", "Perch", "Koi", "Pufferfish", "Salmon",
              "Lionfish", "Piranha", "MantaRay", "Sailfish"]
SELECTED = "Lionfish"
EQUIPPED = "Goldfish"


def all_fish():
    """[(name, rarity)] in index order."""
    return [(n, r) for r in RARITIES for n in FISH[r]]


def display(name):
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


assert len(all_fish()) == 50 and all(n in AREA for n, _ in all_fish())
