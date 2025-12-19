from enum import auto

from base_enum import BaseEnum


class RarityTypes(str, BaseEnum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"
