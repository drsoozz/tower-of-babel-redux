from enum import auto
from base_enum import BaseEnum


class StatModType(str, BaseEnum):
    FLAT = "flat"
    PERCENT_ADD = "percent add"
    PERCENT_MULT = "percent mult"
    FLAT_RIGID = "flat rigid"
    FUNC = "func"
