from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from components.stats.stat_modifier import StatModifier
from components.stats.stat_mod_types import StatModType
from components.stats.stat_types import StatTypes


import consts
from base_enum import BaseEnum


class ArmorTypes(str, BaseEnum):
    # no speed penalty, no defense (uses naked defense)
    UNARMORED = "unarmored"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    ULTRAHEAVY = "ultraheavy"


class ArmorTags(str, BaseEnum):
    UNARMORED = "unarmored"
    LIGHTWEIGHT = "lightweight"
    HEAVYWEIGHT = "heavyweight"


@dataclass(frozen=True)
class ArmorDefinition:
    path: Path
    tags: set[ArmorTags]


DEFAULT_ARMOR_PATH = (
    consts.BASE_PATH
    / Path("components")
    / Path("items")
    / Path("armor")
    / Path("defaults")
)

ARMORS: dict[ArmorTypes, ArmorDefinition] = {
    ArmorTypes.UNARMORED: ArmorDefinition(
        path=DEFAULT_ARMOR_PATH / "unarmored.json", tags=ArmorTags.UNARMORED
    ),
    ArmorTypes.LIGHT: ArmorDefinition(
        path=DEFAULT_ARMOR_PATH / "light.json", tags=ArmorTags.LIGHTWEIGHT
    ),
    ArmorTypes.MEDIUM: ArmorDefinition(
        path=DEFAULT_ARMOR_PATH / "medium.json", tags=ArmorTags.LIGHTWEIGHT
    ),
    ArmorTypes.HEAVY: ArmorDefinition(
        path=DEFAULT_ARMOR_PATH / "heavy.json", tags=ArmorTags.HEAVYWEIGHT
    ),
    ArmorTypes.ULTRAHEAVY: ArmorDefinition(
        path=DEFAULT_ARMOR_PATH / "ultraheavy.json", tags=ArmorTags.HEAVYWEIGHT
    ),
}
