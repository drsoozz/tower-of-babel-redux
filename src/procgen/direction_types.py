from enum import Enum


class DirectionTypes(Enum):
    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)

    @classmethod
    def from_tuple(cls, t: tuple[int, int]) -> "DirectionTypes":
        for member in cls:
            if member.value == t:
                return member
        raise ValueError(f"No DirectionTypes member with value {t}")

    @property
    def opposite(self) -> "DirectionTypes":
        dx, dy = self.value
        return DirectionTypes.from_tuple((-dx, -dy))
