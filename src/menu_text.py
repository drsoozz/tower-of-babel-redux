from dataclasses import dataclass
from typing import Optional

from components.stats.stat_types import StatTypes
from components.stats.damage_types import DamageTypes
from components.stats.combat_stat_types import (
    WeaponStatTypes,
    ArmorStatTypes,
    CritStatTypes,
    SpeedStatTypes,
)
from entity import Item


@dataclass
class StatRow:
    key: Optional[StatTypes]  # None = spacer / header
    label: str  # already padded
    value: str
    selectable: bool  # can cursor land here?


@dataclass
class InventoryRow:
    item: Optional[Item]
    letter: Optional[str]
    name: Optional[str]
    selectable: bool


@dataclass(frozen=True)
class StatDescriptor:
    key: StatTypes
    label: str = ""
    description: str = ""
    formula: str = ""


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
        "500% CON",
    ),
    StatDescriptor(
        StatTypes.HP_REGEN,
        "HIT POINT REGENERATION",
        "How quickly you regenerate your HP.",
        "0.04% CON + 0.01% WIL PER 100 INITIATIVE",
    ),
    StatDescriptor(
        StatTypes.ENERGY,
        "ENERGY",
        "A representation of your pool of physical energy.",
        "25% STR + 25% DEX + 50% CON",
    ),
    StatDescriptor(
        StatTypes.ENERGY_REGEN,
        "ENERGY REGENERATION",
        "How quickly you regenerate your ENERGY.",
        "4% CON + 1% WIL PER 100 INITIATIVE",
    ),
    StatDescriptor(
        StatTypes.MANA,
        "MANA",
        "A representation of your pool of mental energy.",
        "250% INT",
    ),
    StatDescriptor(
        StatTypes.MANA_REGEN,
        "MANA REGENERATION",
        "How quickly you regenerate your MANA",
        "0.4% INT + 0.1% WIL PER 100 INITIATIVE",
    ),
    StatDescriptor(
        StatTypes.CARRYING_CAPACITY,
        "CARRYING CAPACITY",
        "How many lbs you can carry at any given time.",
        "1000% STR",
    ),
    StatDescriptor(
        StatTypes.ENCUMBRANCE,
        "ENCUMBRANCE",
        "How many lbs you can have equipped at any given time.",
        "250% STR",
    ),
]

DAMAGE_STAT_DESCRIPTIONS: list[StatDescriptor] = [
    StatDescriptor(
        StatTypes.DAMAGE_RESISTS,
        "RESISTANCE",
        "How much incoming damage of a certain type you resist.",
        None,
    ),
    StatDescriptor(
        StatTypes.DAMAGE_AMPS,
        "AMPLIFICATION",
        "How much your outgoing damage of a certain type is amplified.",
        None,
    ),
    StatDescriptor(
        StatTypes.DAMAGE_MASTERIES,
        "MASTERY",
        [
            "A measurement of your proficiency with a damage type.",
            "* Exponentially reduces all incoming damage of that type.",
            "* Exponentially increases all outgoing damage of that type.",
        ],
        ["", "INCOMING: damage * 0.99^mastery", "OUTGOING: damage * 1.01^mastery"],
    ),
]

DAMAGE_TYPE_ABBREVIATIONS: dict[DamageTypes, str] = {
    DamageTypes.BLUDGEONING: "BLUDG",
    DamageTypes.PIERCING: "PIERC",
    DamageTypes.SLASHING: "SLASH",
    DamageTypes.SONIC: "SONIC",
    DamageTypes.FIRE: "FIRE ",
    DamageTypes.ICE: "ICE  ",
    DamageTypes.ELECTRIC: "ELEC ",
    DamageTypes.ACID: "ACID ",
    DamageTypes.POISON: "POISN",
    DamageTypes.ARCANE: "ARCN ",
    DamageTypes.ASTRAL: "ASTRL",
    DamageTypes.PSYCHIC: "PSY  ",
    DamageTypes.SACRED: "SACRD",
    DamageTypes.PROFANE: "PROFN",
    DamageTypes.ELDRITCH: "ELDCH",
}
STAT_TYPE_NAMES: dict[StatTypes, str] = {
    StatTypes.STRENGTH: "STR",
    StatTypes.DEXTERITY: "DEX",
    StatTypes.CONSTITUTION: "CON",
    StatTypes.INTELLIGENCE: "INT",
    StatTypes.CUNNING: "CUN",
    StatTypes.WILLPOWER: "WIL",
    StatTypes.DAMAGE_AMPS: "AMP.",
    StatTypes.DAMAGE_RESISTS: "RESIST",
    StatTypes.DAMAGE_MASTERIES: "MASTERY",
}

COMBAT_TEXT_DESCRIPTIONS: list[StatDescriptor] = [
    StatDescriptor(
        WeaponStatTypes.ATTACK,
        "ATTACK RATING",
        "A measure of your ability to hit your attacks.",
        ["", "CHANCE FOR AN ATTACK TO HIT = (ATTACK - DEFENSE) * 2.5%"],
    ),
    StatDescriptor(
        WeaponStatTypes.DAMAGE,
        "DAMAGE",
        "How much damage you do when you hit an attack.",
    ),
    StatDescriptor(
        WeaponStatTypes.RANGE, "WEAPON RANGE", "How far your weapon can attack from."
    ),
    StatDescriptor(
        WeaponStatTypes.COST,
        "INITIATIVE COST",
        ["How much initiative it costs", "to make an attack with your weapon."],
    ),
    StatDescriptor(
        CritStatTypes.CRITICAL_CHANCE,
        "CRITICAL CHANCE",
        [
            "The chance that any attack you make will become a",
            "critical attack. Critical attacks never miss a target.",
        ],
        ["(100 - 95*[0.99^{CUN - 10}])%"],
    ),
    StatDescriptor(
        CritStatTypes.CRITICAL_MULTIPLIER,
        "CRITICAL MULTIPLIER",
        [
            "Critical attacks have their damage multiplied by",
            "your CRITICAL MULTIPLIER.",
        ],
        ["1 + 2.5% INT + 2.5% CUN"],
    ),
    StatDescriptor(
        ArmorStatTypes.HEAD,
        "DEFENSE (HEAD)",
        "A measure of your ability to avoid attacks.",
        ["", "CHANCE FOR AN ATTACK TO HIT = (ATTACK - DEFENSE) * 2.5%"],
    ),
    StatDescriptor(
        ArmorStatTypes.TORSO,
        "DEFENSE (TORSO)",
        "A measure of your ability to avoid attacks.",
        ["", "CHANCE FOR AN ATTACK TO HIT = (ATTACK - DEFENSE) * 2.5%"],
    ),
    StatDescriptor(
        ArmorStatTypes.LEGS,
        "DEFENSE (LEGS)",
        "A measure of your ability to avoid attacks.",
        ["", "CHANCE FOR AN ATTACK TO HIT = (ATTACK - DEFENSE) * 2.5%"],
    ),
    StatDescriptor(
        ArmorStatTypes.FEET,
        "DEFENSE (FEET)",
        "A measure of your ability to avoid attacks.",
        ["", "CHANCE FOR AN ATTACK TO HIT = (ATTACK - DEFENSE) * 2.5%"],
    ),
    StatDescriptor(
        ArmorStatTypes.OFF_HAND,
        "DEFENSE (OFF-HAND)",
        "A measure of your ability to avoid attacks.",
        ["", "CHANCE FOR AN ATTACK TO HIT = (ATTACK - DEFENSE) * 2.5%"],
    ),
    StatDescriptor(
        ArmorStatTypes.TOTAL,
        "DEFENSE (TOTAL)",
        "A measure of your ability to avoid attacks.",
        ["", "CHANCE FOR AN ATTACK TO HIT = (ATTACK - DEFENSE) * 2.5%"],
    ),
    StatDescriptor(
        SpeedStatTypes.GLOBAL_SPEED,
        "GLOBAL SPEED",
        [
            "The amount by which the INITIATIVE cost of all actions",
            "you take is reduced.",
        ],
    ),
    StatDescriptor(
        SpeedStatTypes.MOVEMENT_SPEED,
        "MOVEMENT SPEED",
        ["The amount by which the INITIATIVE cost of your", "movement is reduced."],
    ),
    StatDescriptor(
        SpeedStatTypes.ATTACK_SPEED,
        "ATTACK SPEED",
        ["The amount by which the INITIATIVE cost of your", "attacks are reduced."],
    ),
    StatDescriptor(
        SpeedStatTypes.CASTING_SPEED,
        "CASTING SPEED",
        ["The amount by which the INITIATIVE cost of your", "spells are reduced."],
    ),
]
