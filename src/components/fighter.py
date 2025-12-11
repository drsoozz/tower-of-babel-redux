from __future__ import annotations

from typing import TYPE_CHECKING, Dict

import color
from components.base_component import BaseComponent
from render_order import RenderOrder
from components.stats.stats import Stats
from components.stats.stat_modifier import StatModifier
from components.stats.stat_mod_types import StatModType

if TYPE_CHECKING:
    from entity import Actor
    from components.stats.stat_types import StatTypes


class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, base_stats: Dict[StatTypes, int | float]):

        self.stats = Stats(base_stats=base_stats)
        self.stats.parent = self

    def init_hook(self) -> None:
        if self.parent.name == "Player":
            self.stats.hp.max.add_modifier(
                StatModifier(value=10, mod_type=StatModType.FLAT, source="BASE")
            )
            self.stats.hp.maximize()

    @property
    def hp(self) -> int:
        return self.stats.hp.value

    @hp.setter
    def hp(self, value: int) -> None:
        self.stats.hp.value = value
        if self.stats.hp.value <= 0 and self.parent.ai:
            self.die()

    def heal(self, amount: float) -> float:
        return self.stats.hp.modify(amount)

    def take_damage(self, amount: float) -> float:
        return self.stats.hp.modify(amount)

    """
    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

    @property
    def defense(self) -> int:
        return self.base_defense + self.defense_bonus

    @property
    def power(self) -> int:
        return self.base_power + self.power_bonus

    @property
    def defense_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.defense_bonus
        else:
            return 0

    @property
    def power_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.power_bonus
        else:
            return 0"""

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = color.player_die.rgb
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_color = color.enemy_die.rgb

        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None

        self.engine.player.level.add_xp(self.parent.level.xp_given)

        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)
