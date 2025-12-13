from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, TYPE_CHECKING

from components.stats.damage_types import DamageTypes
from combat_types import CombatTypes

if TYPE_CHECKING:
    from entity import Actor


@dataclass
class Damage:
    values: Dict[DamageTypes, float]

    def add(self, damage_type: DamageTypes, amount: float) -> None:
        self.values[damage_type] = self.values.get(damage_type, 0) + amount

    def apply_boosts(self, attacker: Actor) -> Dict[DamageTypes, float]:
        stats = attacker.fighter.stats
        result: Dict[DamageTypes, float] = {}
        for damtype, damval in self.values.items():
            damage_amp = stats.damage_amps.multiplier(damage_type=damtype)
            damage_mastery = stats.damage_masteries.multiplier(
                damage_type=damtype, combat_type=CombatTypes.DAMAGE
            )
            result[damtype] = damval * damage_amp * damage_mastery

        return result

    def apply_resistances(
        self, scaled_damage: Dict[DamageTypes, float], defender: Actor
    ) -> Dict[DamageTypes, float]:
        result = {}
        stats = defender.fighter.stats
        for damtype, damval in scaled_damage.items():
            damage_resist = stats.damage_resists.multiplier(damage_type=damtype)
            damage_mastery = stats.damage_masteries.multiplier(
                damage_type=damtype, combat_type=CombatTypes.RESIST
            )
            result[damtype] = damval * damage_resist * damage_mastery

        return result

    def sum_damage_dict(self, damage_dict: Dict[DamageTypes, float]) -> float:
        # Note: THIS DOES NOT ACCOUNT FOR RESISTANCES/AMPS/MASTERIES! you need to use
        # self.apply_boosts and self.apply_resistances to do that!
        total = 0
        for _, damval in damage_dict.items():
            total += damval

        return total
