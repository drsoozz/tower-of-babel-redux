from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WeaponRange:
    max_range: Optional[int] = None  # None → melee

    @property
    def is_melee(self) -> bool:
        return self.max_range is None

    @property
    def is_ranged(self) -> bool:
        return self.max_range is not None
