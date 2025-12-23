# this is used for the character stats screen!!!

from base_enum import BaseEnum


class WeaponStatTypes(str, BaseEnum):
    ATTACK = "attack"
    DAMAGE = "damage"
    RANGE = "range"
    COST = "cost"


class ArmorStatTypes(str, BaseEnum):
    HEAD = "head"
    TORSO = "torso"
    LEGS = "legs"
    FEET = "feet"
    OFF_HAND = "off-hand"
    TOTAL = "total"


class SpeedStatTypes(str, BaseEnum):
    GLOBAL_SPEED = "glob. speed"
    MOVEMENT_SPEED = "mvmt. speed"
    ATTACK_SPEED = "atk. speed"
    CASTING_SPEED = "cast. speed"


class CritStatTypes(str, BaseEnum):
    CRITICAL_CHANCE = "crit. chance"
    CRITICAL_MULTIPLIER = "crit. mult."
