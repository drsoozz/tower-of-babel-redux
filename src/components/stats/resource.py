from __future__ import annotations

from typing import TYPE_CHECKING

from components.stats.character_stat import CharacterStat

if TYPE_CHECKING:
    from components.stats.stats import Stats
    from entity import Actor
    from components.fighter import Fighter


class Resource:
    def __init__(self, base_value: float | CharacterStat, name: str):
        self.name = name

        self.max: CharacterStat
        if isinstance(base_value, (int, float)):
            self.max = CharacterStat(base_value=base_value, name=name)
        elif isinstance(base_value, CharacterStat):
            self.max = CharacterStat(base_value=base_value.value, name=name)
        else:
            raise ValueError(f"Unexpected base_value type: {base_value!r}")

        self._value = self.max_value

    @property
    def max_value(self) -> float:
        return self.max.value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value

    def modify(self, amount: float, sudo: bool = False) -> float:
        # sudo allows stuff like "Overhealing" and having negative hp
        if sudo:
            new_value = self.value + amount
        else:
            new_value = max(0, min(self.value + amount, self.max_value))

        amount_modified = new_value - self.value

        self.value = new_value

        return amount_modified

    def maximize(self) -> None:
        self.value = self.max_value

    def minimize(self) -> None:
        self.value = 0


# subclass of Resource used for HP. calls the Fighter.die() method when hp reaches 0
# CURRENTLY UNUSED, IS HANDLED IN Fighter
class HPResource(Resource):
    def __init__(
        self, base_value: float | CharacterStat, name: str, fighter_parent: Fighter
    ):

        self.fighter_parent = fighter_parent
        super().__init__(base_value=base_value, name=name)

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value
