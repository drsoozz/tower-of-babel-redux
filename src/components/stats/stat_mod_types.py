from enum import auto
from base_enum import BaseEnum


class StatModType(BaseEnum):
    FLAT = auto()
    PERCENT_ADD = auto()
    PERCENT_MULT = auto()
    FLAT_RIGID = auto()
    FUNC = auto()
