"""
damagetypes.py

Defines the `DamageType` enumeration used to categorize all valid sources of damage
within the game. This provides a consistent and type-safe way to reference damage types
across various combat and stat-related systems, including amplification, resistance,
immunity, and more.
"""

from enum import Enum


class DamageTypes(str, Enum):
    """Enumeration of all damage types used in the game's combat system.

    This enum is used to provide a unified reference point for defining and checking
    damage interactions, such as resistances, immunities, and bonuses.

    Values:
        PHYSICAL: Category representing Bludgeoning, Piercing, Slashing, and Sonic damage
            BLUDGEONING: Crushing damage (e.g., hammers, falling rocks).
            PIERCING: Damage from sharp thrusting weapons (e.g., spears, arrows).
            SLASHING: Damage from slicing weapons (e.g., swords, claws).
            SONIC: Vibrational or sound-based damage.
        ELEMENTAL:
            FIRE: Heat-based elemental damage.
            ICE: Cold-based elemental damage.
            ELECTRIC: Lightning-based elemental damage.
            ACID: Corrosion-based elemental damage.
        POISON: Toxic damage from venom or substances.

        ARCANE: Pure magical force or energy.
        ASTRAL: Damage tied to spiritual or cosmic realms.
        PSYCHIC: Mind-affecting damage (e.g., fear, hallucinations).
        SACRED: Holy or divine energy damage.
        PROFANE: Unholy or desecrating energy damage.
        ELDRITCH: Esoteric or forbidden magic-based damage, typically tied with otherworld-ness.
    """

    BLUDGEONING = "Bludgeoning"
    PIERCING = "Piercing"
    SLASHING = "Slashing"
    SONIC = "Sonic"
    FIRE = "Fire"
    ICE = "Ice"
    ELECTRIC = "Electric"
    ACID = "Acid"
    POISON = "Poison"
    ARCANE = "Arcane"
    ASTRAL = "Astral"
    PSYCHIC = "Psychic"
    SACRED = "Sacred"
    PROFANE = "Profane"
    ELDRITCH = "Eldritch"
