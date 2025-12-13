from base_enum import BaseEnum


class StatTypes(str, BaseEnum):
    # extend as needed
    STRENGTH = "Strength"
    DEXTERITY = "Dexterity"
    CONSTITUTION = "Constitution"
    INTELLIGENCE = "Intelligence"
    CUNNING = "Cunning"
    WILLPOWER = "Willpower"
    HP = "HP"
    HP_REGEN = "HP Regen"
    ENERGY = "Energy"
    ENERGY_REGEN = "Energy Regen"
    MANA = "Mana"
    MANA_REGEN = "Mana Regen"
    CARRYING_CAPACITY = "Carrying Capacity"
    ENCUMBRANCE = "Encumbrance"
    DAMAGE_RESISTS = "Damage Resists"
    DAMAGE_AMPS = "Damage Amps"
    DAMAGE_MASTERIES = "Damage Masteries"
