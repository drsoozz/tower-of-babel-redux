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

        print(type(self._dex_speed_scaling))
        _dex_speed = CharacterStat(base_value=self.parent.dexterity, name="BASE")

        _dex_scaling = StatModifier(
            value=self._dex_speed_scaling,
            mod_type=StatModType.FUNC,
            source="BASE",
            depends_on=[_dex_speed],
        )

        self.global_speed.add_modifier(_dex_scaling)

    @property
    def attack_multiplier(self) -> float:
        return 1 / self.global_speed.value / self.attack_speed.value

    @property
    def casting_multiplier(self) -> float:
        return 1 / self.global_speed.value / self.casting_speed.value

    @property
    def movement_multiplier(self) -> float:
        return 1 / self.global_speed.value / self.movement_speed.value

    def _dex_speed_scaling(self, dex: CharacterStat) -> float:
        """
        whenever passing a function into the stat system something like this is NECESSARY
        so that the engine can be pickled. otherwise, picking WILL fail
        """
        return 1 - pow(0.995, dex.value)
