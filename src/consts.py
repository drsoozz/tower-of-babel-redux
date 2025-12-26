from pathlib import Path

from components.stats.stat_types import StatTypes
from components.stats.stat_modifier import StatModifier
from components.stats.stat_mod_types import StatModType
from components.stats.damage_types import DamageTypes
from components.stats.weapon_range import WeaponRange
from components.equipment_types import EquipmentTypes
from components.loot.rarity_types import RarityTypes

BASE_PATH = Path("src")
TILESET_PATH = Path(BASE_PATH, "tilesets", "Dullard_Exponent_12x12.png")
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 72
MAP_WIDTH = SCREEN_WIDTH
MAP_HEIGHT = int(SCREEN_HEIGHT * 0.9)

# to convert from how initiative is stored to how it is used everywhere else
# it is stored in a weird way to attempt to prevent floating point errors
TRUE_INIT_FACTOR = int(1e4)
# factor to divide by when going from initiative to multiplier to regen value
MAX_INIT = int(1e6)

UPPER_RESIST_CAP = 0.75

DEFAULT_DEFENSE_DICT = {
    StatTypes.DEXTERITY: StatModifier(
        value=0.25, mod_type=StatModType.PERCENT_MULT, source="BASE"
    )
}

DEFAULT_SHIELD_DICT = {
    StatTypes.DEXTERITY: StatModifier(
        value=0, mod_type=StatModType.PERCENT_MULT, source="BASE"
    )
}

# unarmed strike
DEFAULT_UNARMED_ATTACK_DICT = {
    StatTypes.STRENGTH: StatModifier(
        value=0.20, mod_type=StatModType.PERCENT_MULT, source="BASE"
    ),
    StatTypes.DEXTERITY: StatModifier(
        value=0.80, mod_type=StatModType.PERCENT_MULT, source="BASE"
    ),
}

DEFAULT_UNARMED_DAMAGE_DICT = {
    DamageTypes.BLUDGEONING: {
        StatTypes.STRENGTH: StatModifier(
            value=0.45, mod_type=StatModType.PERCENT_MULT, source="BASE"
        ),
        StatTypes.DEXTERITY: StatModifier(
            value=0.10, mod_type=StatModType.PERCENT_MULT, source="BASE"
        ),
    }
}
DEFAULT_UNARMED_WEAPON_RANGE = WeaponRange(_max_range=None)

DEFAULT_UNARMED_ATTACK_INIT_COST = MAX_INIT / 2


HEAD_WEIGHT_MODIFIER = 0.5
TORSO_WEIGHT_MODIFIER = 3
LEGS_WEIGHT_MODIFIER = 1.5
FEET_WEIGHT_MODIFIER = 1

EXP_BASE = 1

SOUL_COIN_REWARD_BASE = 10
SOUL_COIN_REWARD_LEVEL_FACTOR = 10
SOUL_COIN_REWARD_LEVEL_EXPONENT = 1.43713005
SOUL_COIN_REWARD_VARIANCE = 0.25

ESSENCE_RARITY_TABLE = {
    RarityTypes.COMMON: 1 / 320,
    RarityTypes.UNCOMMON: 1 / 160,
    RarityTypes.RARE: 1 / 80,
    RarityTypes.VERY_RARE: 1 / 40,
    RarityTypes.LEGENDARY: 1 / 20,
    RarityTypes.MYTHICAL: 1 / 10,
}

ITEM_RARITY_TABLE = {
    RarityTypes.COMMON: 1 / 100,
    RarityTypes.UNCOMMON: 1 / 50,
    RarityTypes.RARE: 1 / 25,
    RarityTypes.VERY_RARE: 1 / 12,
    RarityTypes.LEGENDARY: 1 / 6,
    RarityTypes.MYTHICAL: 1 / 3,
}
