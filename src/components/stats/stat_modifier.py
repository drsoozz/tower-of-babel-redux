from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
from types import FunctionType

from components.stats.stat_mod_types import StatModType

if TYPE_CHECKING:
    from components.stats.character_stat import CharacterStat


class StatModifier:
    def __init__(
        self,
        *,
        value: float | int | CharacterStat | callable,
        mod_type: StatModType,
        source: object,
        depends_on: Optional[List[CharacterStat]] = None,
    ):
        self.raw_value = value
        self.mod_type = mod_type
        self.source = source
        self.is_complex = not isinstance(self.raw_value, (int, float))
        if not isinstance(depends_on, list):
            depends_on = [depends_on]
        if depends_on is None:
            depends_on = []
        self.depends_on = depends_on

    @property
    def is_dirty(self) -> bool:
        if isinstance(self.raw_value, FunctionType):
            return any(dep.check_if_dirty() for dep in self.depends_on)
        if self.is_complex:
            self.raw_value: CharacterStat
            return self.raw_value.check_if_dirty()
        # Primitive values never get dirty
        return False

    @property
    def value(self) -> float:
        if self.is_complex:
            if isinstance(self.raw_value, FunctionType):
                return self.raw_value(*(dep for dep in self.depends_on))
            return float(self.raw_value.value)
        return float(self.raw_value)
