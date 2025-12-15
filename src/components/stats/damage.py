from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, TYPE_CHECKING

from components.stats.damage_types import DamageTypes
from components.stats.character_stat import CharacterStat
from combat_types import CombatTypes


if TYPE_CHECKING:
    from entity import Actor


@dataclass
class Damage:
    _values: Dict[
        DamageTypes, float | CharacterStat
    ]  # can accept float or CharacterStat, only outputs float

    def __post_init__(self) -> None:
        self.values = self._values

    @property
    def values(self) -> Dict[DamageTypes, float]:
        return self._values

    @values.setter
    def values(self, raw: Dict[DamageTypes, float | CharacterStat]) -> None:
        normalized: Dict[DamageTypes, float] = {}

        for damtype in DamageTypes:
            damval = raw.get(damtype, 0)
            if isinstance(damval, CharacterStat):
                damval = damval.value
            normalized[damtype] = damval
        self._values = normalized

    @property
    def totalled_damage(self) -> float:
        total = 0
        for _, damval in self.values.items():
            total += damval

        return total

    def add(self, damage: Damage) -> Damage:
        summed_damage: Dict[DamageTypes, float] = {}

        for damtype in DamageTypes:
            summed_damage[damtype] = self.values[damtype] + damage.values[damtype]

        return Damage(summed_damage)

    def calculate_final_damage(self, attacker: Actor, defender: Actor) -> Damage:
        results = Damage(self.values)
        results = results.apply_boosts(attacker)
        results = results.apply_resistances(defender)
        return results

    def apply_boosts(self, attacker: Actor) -> Damage:
        stats = attacker.fighter.stats
        result: Dict[DamageTypes, float] = {}
        for damtype, damval in self.values.items():
            damage_amp = stats.damage_amps.multiplier(damage_type=damtype)
            damage_mastery = stats.damage_masteries.multiplier(
                damage_type=damtype, combat_type=CombatTypes.DAMAGE
            )
            result[damtype] = damval * damage_amp * damage_mastery

        return Damage(result)

    def apply_resistances(self, defender: Actor) -> Damage:
        result = {}
        stats = defender.fighter.stats
        for damtype, damval in self.values.items():
            damage_resist = stats.damage_resists.multiplier(damage_type=damtype)
            damage_mastery = stats.damage_masteries.multiplier(
                damage_type=damtype, combat_type=CombatTypes.RESIST
            )
            result[damtype] = damval * damage_resist * damage_mastery

        return Damage(result)
