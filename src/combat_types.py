from base_enum import BaseEnum


class CombatTypes(str, BaseEnum):
    DAMAGE = "Attack"
    RESIST = "Resist"
