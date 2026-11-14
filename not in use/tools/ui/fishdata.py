"""Shared data for the UI tools: the 50 fish, rarity palette and water areas.

Plain Python (no bpy), so both the Blender render scripts and the PIL/XML tools import it.
Water areas follow the game's 10 zones (models/Zones/).
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
    "Minnow": "Pond",
    "Goldfish": "Pond",
    "Bluegill": "Pond",
    "Guppy": "Pond",
    "Koi": "Pond",
    "Perch": "River",
    "Carp": "River",
    "Catfish": "River",
    "LargemouthBass": "River",
    "RainbowTrout": "River",
    "Salmon": "River",
    "Pike": "River",
    "Sturgeon": "River",
    "Mudskipper": "Swamp",
    "Piranha": "Swamp",
    "ElectricEel": "Swamp",
    "AlligatorGar": "Swamp",
    "Arapaima": "Swamp",
    "Clownfish": "Coral Reef",
    "BlueTang": "Coral Reef",
    "Pufferfish": "Coral Reef",
    "Angelfish": "Coral Reef",
    "Seahorse": "Coral Reef",
    "Flounder": "Coral Reef",
    "Lionfish": "Coral Reef",
    "MorayEel": "Coral Reef",
    "MantaRay": "Coral Reef",
    "Sardine": "Open Ocean",
    "HammerheadShark": "Open Ocean",
    "GreatWhiteShark": "Open Ocean",
    "Sailfish": "Open Ocean",
    "Icefish": "Frozen Sea",
    "GreenlandShark": "Frozen Sea",
    "CrystalPike": "Frozen Sea",
    "AuroraRay": "Frozen Sea",
    "Lanternfish": "Deep Abyss",
    "Anglerfish": "Deep Abyss",
    "Blobfish": "Deep Abyss",
    "Oarfish": "Deep Abyss",
    "GhostShark": "Deep Abyss",
    "Megalodon": "Deep Abyss",
    "MagmaEel": "Volcanic Vent",
    "EmberKoi": "Volcanic Vent",
    "HydraEel": "Volcanic Vent",
    "Coelacanth": "Sunken Ruins",
    "GoldenArowana": "Sunken Ruins",
    "SeaSerpent": "Sunken Ruins",
    "DragonKoi": "Sunken Ruins",
    "SeraphFish": "Starfall Lake",
    "StarfallWhaleShark": "Starfall Lake",
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
