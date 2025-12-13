from enum import auto
from base_enum import BaseEnum


class RenderOrder(BaseEnum):
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()
