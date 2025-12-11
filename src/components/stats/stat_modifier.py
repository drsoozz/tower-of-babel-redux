from __future__ import annotations

from typing import TYPE_CHECKING

from components.stats.stat_mod_types import StatModType

if TYPE_CHECKING:
    from components.stats.character_stat import CharacterStat


class StatModifier:
    def __init__(
        self,
        *,
        value: float | int | CharacterStat,
        mod_type: StatModType,
        source: object,
    ):
        self.raw_value = value
        self.mod_type = mod_type
        self.source = source
        self.is_complex = not isinstance(self.raw_value, (int, float))

    @property
    def is_dirty(self) -> bool:
        if self.is_complex:
            self.raw_value: CharacterStat
            return self.raw_value.check_if_dirty()
        return False

    @property
    def value(self) -> float:
        return float(self.raw_value.value) if self.is_complex else float(self.raw_value)
