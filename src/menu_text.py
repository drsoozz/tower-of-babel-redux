from pathlib import Path
from dataclasses import dataclass
from typing import Callable

from components.stats.stat_types import StatTypes
from components.stats.stat_modifier import StatModifier
from components.stats.stat_mod_types import StatModType
from components.stats.damage_types import DamageTypes
from components.stats.weapon_range import WeaponRange
from components.equipment_types import EquipmentTypes
from components.loot.rarity_types import RarityTypes


@dataclass
class StatRow:
    label: str
    value: str
    descriptor_index: int | None  # None = spacer / non-selectable


@dataclass(frozen=True)
class StatDescriptor:
    key: StatTypes
    label: str
    description: str
    formula: str


BASE_STAT_DESCRIPTIONS: list[StatDescriptor] = [
    StatDescriptor(
        StatTypes.STRENGTH, "STRENGTH", "A measure of how strong you are.", ""
    ),
    StatDescriptor(
        StatTypes.DEXTERITY, "DEXTERITY", "A measure of how agile you are.", ""
    ),
    StatDescriptor(
        StatTypes.CONSTITUTION,
        "CONSTITUTION",
        "A measure of how physically resilient you are.",
        "",
    ),
    StatDescriptor(
        StatTypes.INTELLIGENCE, "INTELLIGENCE", "A measure of how smart you are.", ""
    ),
    StatDescriptor(
        StatTypes.CUNNING, "CUNNING", "A measure of how quick-witted you are.", ""
    ),
    StatDescriptor(
        StatTypes.WILLPOWER,
        "WILLPOWER",
        "A measure of how mentally resilient you are.",
        "",
    ),
    StatDescriptor(
        StatTypes.HP,
        "HIT POINTS",
        "How much damage you can take before dying.",
        "BASE: 500% CON",
    ),
    StatDescriptor(
        StatTypes.HP_REGEN,
        "HIT POINT REGENERATION",
        "How quickly you regenerate your HP.",
        "BASE: 0.04% CON + 0.01% WIL PER 100 INITIATIVE",
    ),
    StatDescriptor(
        StatTypes.ENERGY,
        "ENERGY",
        "A representation of your pool of physical energy.",
        "BASE: 25% STR + 25% DEX + 50% CON",
    ),
    StatDescriptor(
        StatTypes.ENERGY_REGEN,
        "ENERGY REGENERATION",
        "How quickly you regenerate your ENERGY.",
        "BASE: 4% CON + 1% WIL PER 100 INITIATIVE",
    ),
    StatDescriptor(
        StatTypes.MANA,
        "MANA",
        "A representation of your pool of mental energy.",
        "BASE: 250% INT",
    ),
    StatDescriptor(
        StatTypes.MANA_REGEN,
        "MANA REGENERATION",
        "How quickly you regenerate your MANA",
        "BASE: 0.4% INT + 0.1% WIL PER 100 INITIATIVE",
    ),
    StatDescriptor(
        StatTypes.CARRYING_CAPACITY,
        "CARRYING CAPACITY",
        "How many lbs you can carry at any given time.",
        "BASE: 1000% STR",
    ),
    StatDescriptor(
        StatTypes.ENCUMBRANCE,
        "ENCUMBRANCE",
        "How many lbs you can have equipped at any given time.",
        "BASE: 250% STR",
    ),
]
