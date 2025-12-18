from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, List

import color
import consts
from components.base_component import BaseComponent
from render_order import RenderOrder
from components.stats.stats import Stats
from components.stats.stat_modifier import StatModifier
from components.stats.stat_mod_types import StatModType
from components.stats.damage_types import DamageTypes
from components.equipment_types import EquipmentTypes
from components.stats.weapon_range import WeaponRange

if TYPE_CHECKING:
    from entity import Actor
    from components.stats.stat_types import StatTypes


class Fighter(BaseComponent):
    parent: Actor

    def __init__(
        self,
        base_stats: Dict[StatTypes, int | float],
        damage_resists: Optional[Dict[DamageTypes, float]],
        damage_amps: Optional[Dict[DamageTypes, float]],
        damage_masteries: Dict[DamageTypes, float],
        natural_defense_dict: Optional[
            Dict[EquipmentTypes, Dict[StatTypes, StatModifier | List[StatModifier]]]
        ] = None,
        natural_weapon_attack_dict: Optional[
            Dict[StatTypes, StatModifier | List[StatModifier]]
        ] = None,
        natural_weapon_damage_dict: Optional[
            Dict[DamageTypes, Dict[StatTypes, StatModifier | List[StatModifier]]]
        ] = None,
        natural_weapon_range: Optional[WeaponRange] = None,
        natural_weapon_attack_init_cost: Optional[
            int
        ] = consts.DEFAULT_UNARMED_ATTACK_INIT_COST,
    ):

        self.stats = Stats(
            base_stats=base_stats,
            damage_resists=damage_resists,
            damage_amps=damage_amps,
            damage_masteries=damage_masteries,
            natural_defense_dict=natural_defense_dict,
            natural_weapon_attack_dict=natural_weapon_attack_dict,
            natural_weapon_damage_dict=natural_weapon_damage_dict,
            natural_weapon_range=natural_weapon_range,
            natural_weapon_attack_init_cost=natural_weapon_attack_init_cost,
            parent=self,
        )

    def init_hook(self) -> None:
        if self.parent.name == "Player":
            self.stats.hp.max.add_modifier(
                StatModifier(value=5, mod_type=StatModType.FLAT, source="BASE")
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
