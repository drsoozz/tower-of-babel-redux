from enum import auto, Enum


class StatModType(Enum):
    FLAT = auto()
    PERCENT_ADD = auto()
    PERCENT_MULT = auto()
    FLAT_RIGID = auto()
    FUNC = auto()
