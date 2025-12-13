from enum import Enum


class CombatTypes(str, Enum):
    DAMAGE = "Attack"
    RESIST = "Resist"
