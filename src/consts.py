from pathlib import Path

from components.stats.stat_types import StatTypes
from components.stats.stat_modifier import StatModifier
from components.stats.stat_mod_types import StatModType
from components.stats.damage_types import DamageTypes
from components.stats.weapon_range import WeaponRange
from components.equipment_types import EquipmentTypes

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
    EquipmentTypes.HEAD: {
        StatTypes.DEXTERITY: StatModifier(
            value=0.25, mod_type=StatModType.PERCENT_MULT, source="BASE"
        )
    },
    EquipmentTypes.TORSO: {
        StatTypes.DEXTERITY: StatModifier(
            value=0.25, mod_type=StatModType.PERCENT_MULT, source="BASE"
        )
    },
    EquipmentTypes.LEGS: {
        StatTypes.DEXTERITY: StatModifier(
            value=0.25, mod_type=StatModType.PERCENT_MULT, source="BASE"
        )
    },
    EquipmentTypes.FEET: {
        StatTypes.DEXTERITY: StatModifier(
            value=0.25, mod_type=StatModType.PERCENT_MULT, source="BASE"
        )
    },
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
DEFAULT_UNARMED_WEAPON_RANGE = WeaponRange(max_range=None)

DEFAULT_UNARMED_ATTACK_INIT_COST = MAX_INIT / 2
