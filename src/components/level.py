from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from components.stats.stat_types import StatTypes
from components.stats.stat_modifier import StatModifier
from components.stats.stat_mod_types import StatModType

if TYPE_CHECKING:
    from entity import Actor


class Level(BaseComponent):
    parent: Actor

    def __init__(
        self,
        current_level: int = 1,
        current_xp: int = 0,
        level_up_base: int = 1,
        level_up_factor: int = 2,
        xp_given: int = 0,
    ):
        self.current_level = current_level
        self.current_xp = current_xp
        self.level_up_base = level_up_base
        self.level_up_factor = level_up_factor
        self.xp_given = xp_given

    @property
    def experience_to_next_level(self) -> int:
        L = self.current_level
        return int(self.level_up_base + self.level_up_factor * ((L + 1) * (L + 2)) / 2)

    @property
    def requires_level_up(self) -> bool:
        return self.current_xp > self.experience_to_next_level

    def add_xp(self, xp: int) -> None:
        if xp == 0 or self.level_up_base == 0:
            return

        self.current_xp += xp

        self.engine.message_log.add_message(f"You gain {xp} experience points.")

        if self.requires_level_up:
            self.engine.message_log.add_message(
                f"You advance to level {self.current_level + 1}!"
            )

    def increase_level(self) -> None:
        self.current_xp -= self.experience_to_next_level

        self.current_level += 1

    def increase_stat(self, stat: StatTypes) -> None:
        self.increase_level()

        stats_object = self.parent.fighter.stats
        level_up_mod = StatModifier(
            value=1, mod_type=StatModType.FLAT, source=f"LEVEL_UP_{self.current_level}"
        )
        match stat:
            case StatTypes.STRENGTH:
                stats_object.strength.add_modifier(level_up_mod)
            case StatTypes.DEXTERITY:
                stats_object.dexterity.add_modifier(level_up_mod)
            case StatTypes.CONSTITUTION:
                stats_object.constitution.add_modifier(level_up_mod)
            case StatTypes.INTELLIGENCE:
                stats_object.intelligence.add_modifier(level_up_mod)
            case StatTypes.CUNNING:
                stats_object.cunning.add_modifier(level_up_mod)
            case StatTypes.WILLPOWER:
                stats_object.willpower.add_modifier(level_up_mod)
            case _:
                raise ValueError(
                    "I literally have no fucking clue how this error occured..."
                )
        self.engine.message_log.add_message(f"Your {stat.value} increases!")
