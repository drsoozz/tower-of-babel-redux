from __future__ import annotations

from typing import TYPE_CHECKING
import random

import consts
from components.stats.stat_mod_types import StatModType
from components.stats.stat_modifier import StatModifier
from components.stats.character_stat import CharacterStat
from components.stats.resource import InitiativeResource

if TYPE_CHECKING:
    from components.stats.stats import Stats


class Initiative:

    def __init__(self, parent: Stats):
        self.parent = parent

        self.initiative = InitiativeResource(base_value=consts.MAX_INIT, name="BASE")
        self.initiative.value = random.randint(0, consts.MAX_INIT - 1)

        self.global_speed = CharacterStat(base_value=1, name="BASE")
        self.attack_speed = CharacterStat(base_value=1, name="BASE")
        self.casting_speed = CharacterStat(base_value=1, name="BASE")
        self.movement_speed = CharacterStat(base_value=1, name="BASE")

        _dex_speed = CharacterStat(base_value=self.parent.dexterity, name="BASE")
        _dex_speed.add_modifier(
            StatModifier(value=0.005, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )
        _stat_mod = StatModifier(
            value=_dex_speed, mod_type=StatModType.FLAT, source="BASE"
        )

        self.global_speed.add_modifier(_stat_mod)
        self.attack_speed.add_modifier(_stat_mod)
        self.casting_speed.add_modifier(_stat_mod)
        self.movement_speed.add_modifier(_stat_mod)

    @property
    def attack_multiplier(self) -> float:
        return 1 / self.global_speed.value / self.attack_speed.value

    @property
    def casting_multiplier(self) -> float:
        return 1 / self.global_speed.value / self.casting_speed.value

    @property
    def movement_multiplier(self) -> float:
        return 1 / self.global_speed.value / self.movement_speed.value
