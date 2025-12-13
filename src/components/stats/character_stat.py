from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from components.stats.stat_mod_types import StatModType
from components.stats.stat_modifier import StatModifier

if TYPE_CHECKING:
    from components.stats.stats import Stats


class CharacterStat:

    def __init__(self, *, base_value: int | float | CharacterStat, name: str):
        self.raw_base_value = base_value
        self.is_complex = not isinstance(self.raw_base_value, (int, float))
        self._value = self.base_value
        self.stat_modifiers: List[StatModifier | CharacterStat] = []  # empty
        self.is_dirty = True  # True means that self._value needs to be recalculated (is not up to date)
        self.name = name
        self.dependents: list[CharacterStat] = []
        if self.is_complex:
            self.raw_base_value.dependents.append(self)
        self.get_dirty()

    # when any add/remove method is called, self.is_dirty needs to be set to True
    def add_modifier(self, stat_mod: StatModifier) -> None:
        self.stat_modifiers.append(stat_mod)
        if isinstance(stat_mod.raw_value, CharacterStat):
            stat_mod.raw_value.dependents.append(self)
        self.get_dirty()

    def remove_modifier(self, stat_mod: StatModifier) -> None:
        self.stat_modifiers.remove(stat_mod)
        self.get_dirty()

    def remove_all_from_source(self, source: object) -> None:
        original_len = len(self.stat_modifiers)
        self.stat_modifiers = [
            mod for mod in self.stat_modifiers if mod.source != source
        ]

        if len(self.stat_modifiers) != original_len:
            self.get_dirty()

    @property
    def base_value(self) -> float:
        if self.is_complex:
            return self.raw_base_value.value
        return self.raw_base_value

    @property
    def value(self) -> float:
        if self.check_if_dirty():
            self._calculate_value()
        return self._value

    @property
    def preview_value(self) -> float:
        # for leveling up!
        modification = StatModifier(
            value=1, mod_type=StatModType.FLAT, source="LEVEL_UP_PREVIEW"
        )
        self.add_modifier(modification)
        new_value = self.value
        self.remove_modifier(modification)
        return new_value

    def _calculate_value(self) -> None:
        flat = self.base_value
        percent_add = 0
        percent_mult = 1
        flat_rigid = 0

        for mod in self.stat_modifiers:
            match mod.mod_type:
                case StatModType.FLAT:
                    flat += mod.value
                case StatModType.PERCENT_ADD:
                    percent_add += mod.value
                case StatModType.PERCENT_MULT:
                    percent_mult *= mod.value
                case StatModType.FLAT_RIGID:
                    flat_rigid += mod.value
                case StatModType.FUNC:
                    flat += mod.value()
                case _ as unexpected:
                    raise ValueError(f"Unhandled StatModType: {unexpected!r}")
        self._value = float((flat * (1 + percent_add)) * percent_mult + flat_rigid)
        self.get_clean()  # new self._value is up to date. does not need to eb recalculated until self.stat_modifiers is edited

    def get_dirty(self) -> None:
        self.is_dirty = True
        for dep in self.dependents:
            dep.get_dirty()

    def get_clean(self) -> None:
        self.is_dirty = False

    def check_if_dirty(self) -> bool:
        if isinstance(self.raw_base_value, CharacterStat):
            if self.raw_base_value.check_if_dirty():
                return True
        return self.is_dirty or any(mod.is_dirty for mod in self.stat_modifiers)


class CappedStat(CharacterStat):

    def __init__(
        self,
        *,
        base_value: int | float | CharacterStat,
        name: str,
        upper_cap: Optional[int | float | CharacterStat],
        lower_cap: Optional[int | float | CharacterStat],
    ):
        super().__init__(base_value=base_value, name=name)

        self.raw_upper_cap = upper_cap
        self.raw_lower_cap = lower_cap

        self.upper_cap_is_complex = isinstance(upper_cap, CharacterStat)
        self.lower_cap_is_complex = isinstance(lower_cap, CharacterStat)

        if self.upper_cap_is_complex:
            upper_cap.dependents.append(self)
        if self.lower_cap_is_complex:
            lower_cap.dependents.append(self)

        self.get_dirty()

    @property
    def upper_cap(self) -> Optional[float]:
        if self.raw_upper_cap is None:
            return None
        if self.upper_cap_is_complex:
            return self.raw_upper_cap.value
        return self.raw_upper_cap

    @property
    def lower_cap(self) -> Optional[float]:
        if self.raw_lower_cap is None:
            return None
        if self.lower_cap_is_complex:
            return self.raw_lower_cap.value
        return self.raw_lower_cap

    @property
    def value(self) -> float:
        value = super().value
        value = max(self.lower_cap, value) if self.lower_cap is not None else value
        value = min(self.upper_cap, value) if self.upper_cap is not None else value
        return value
