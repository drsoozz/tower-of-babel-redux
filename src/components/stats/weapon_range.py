from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WeaponRange:
    _max_range: Optional[int] = None  # None → melee

    @property
    def max_range(self) -> int:
        if self._max_range is None or self._max_range < 1:
            return 1
        return self._max_range

    @property
    def is_melee(self) -> bool:
        return self.max_range is None

    @property
    def is_ranged(self) -> bool:
        return self.max_range is not None
