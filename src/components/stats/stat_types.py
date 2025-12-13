from enum import Enum


class StatTypes(str, Enum):
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
    DEFENSE = "Defense"
