from __future__ import annotations

from typing import Dict, Optional, TYPE_CHECKING

import consts
from combat_types import CombatTypes
from components.stats.character_stat import CappedStat
from components.stats.damage_types import DamageTypes
from components.stats.stat_modifier import StatModifier
from components.stats.stat_mod_types import StatModType
from components.stats.stat_types import StatTypes

if TYPE_CHECKING:
    from components.stats.stats import Stats


class BaseDamageStats:

    def __init__(
        self,
        *,
        damage_types: Dict[DamageTypes, float],
        upper_cap: Optional[float],
        parent: Stats,
    ):
        self.parent = parent

        # lots of damage types
        self.damage_types = DamageTypes

        self.bludgeoning = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.bludgeoning.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.BLUDGEONING],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.BLUDGEONING] >= upper_cap:
                self.bludgeoning.raw_upper_cap = None
        except (KeyError, TypeError):
            pass
        self.piercing = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.piercing.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.PIERCING],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.PIERCING] >= upper_cap:
                self.piercing.raw_upper_cap = None
        except (KeyError, TypeError):
            pass
        self.slashing = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.slashing.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.SLASHING],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.SLASHING] >= upper_cap:
                self.slashing.raw_upper_cap = None
        except (KeyError, TypeError):
            pass
        self.sonic = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.sonic.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.SONIC],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.SONIC] >= upper_cap:
                self.sonic.raw_upper_cap = None
        except (KeyError, TypeError):
            pass

        self.fire = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.fire.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.FIRE],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.FIRE] >= upper_cap:
                self.fire.raw_upper_cap = None
        except (KeyError, TypeError):
            pass

        self.ice = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.ice.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.ICE],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.ICE] >= upper_cap:
                self.ice.raw_upper_cap = None
        except (KeyError, TypeError):
            pass

        self.electric = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.electric.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.ELECTRIC],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.ELECTRIC] >= upper_cap:
                self.electric.raw_upper_cap = None
        except (KeyError, TypeError):
            pass

        self.acid = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.acid.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.ACID],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.ACID] >= upper_cap:
                self.acid.raw_upper_cap = None
        except (KeyError, TypeError):
            pass

        self.poison = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.poison.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.POISON],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.POISON] >= upper_cap:
                self.poison.raw_upper_cap = None
        except (KeyError, TypeError):
            pass

        self.arcane = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.arcane.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.ARCANE],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.ARCANE] >= upper_cap:
                self.arcane.raw_upper_cap = None
        except (KeyError, TypeError):
            pass

        self.astral = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.astral.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.ASTRAL],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.ASTRAL] >= upper_cap:
                self.astral.raw_upper_cap = None
        except (KeyError, TypeError):
            pass

        self.psychic = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.psychic.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.PSYCHIC],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.PSYCHIC] >= upper_cap:
                self.psychic.raw_upper_cap = None
        except (KeyError, TypeError):
            pass

        self.sacred = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.sacred.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.SACRED],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.SACRED] >= upper_cap:
                self.sacred.raw_upper_cap = None
        except (KeyError, TypeError):
            pass

        self.profane = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.profane.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.PROFANE],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.PROFANE] >= upper_cap:
                self.profane.raw_upper_cap = None
        except (KeyError, TypeError):
            pass

        self.eldritch = CappedStat(
            base_value=0, name="BASE", upper_cap=upper_cap, lower_cap=None
        )
        try:
            self.eldritch.add_modifier(
                StatModifier(
                    value=damage_types[DamageTypes.ELDRITCH],
                    mod_type=StatModType.FLAT,
                    source="BASE",
                )
            )
            if damage_types[DamageTypes.ELDRITCH] >= upper_cap:
                self.eldritch.raw_upper_cap = None
        except (KeyError, TypeError):
            pass

    def multiplier(self, damage_type: DamageTypes = None) -> float:
        raise NotImplementedError()

    def get_stat(self, damage_type: DamageTypes) -> CappedStat:
        return getattr(self, damage_type.normalized)


class ResistStats(BaseDamageStats):
    def __init__(self, *, damage_types: Dict[DamageTypes, float], parent: Stats):
        super().__init__(
            damage_types=damage_types, parent=parent, upper_cap=consts.UPPER_RESIST_CAP
        )

    def multiplier(self, damage_type: DamageTypes = None) -> float:
        if damage_type is None:
            raise ValueError("Not given multiplier type")

        attr: CappedStat
        attr = getattr(self, damage_type.value.lower())
        return 1 - attr.value


class DamageAmpStats(BaseDamageStats):

    def __init__(self, *, damage_types: Dict[DamageTypes, float], parent: Stats):
        super().__init__(damage_types=damage_types, upper_cap=None, parent=parent)

    def multiplier(self, damage_type: DamageTypes = None) -> float:
        if damage_type is None:
            raise ValueError("Not given multiplier type")

        attr: CappedStat
        attr = getattr(self, damage_type.value.lower())
        return 1 + attr.value


class MasteryStats(BaseDamageStats):

    def __init__(self, *, damage_types: Dict[DamageTypes, float], parent: Stats):
        super().__init__(damage_types=damage_types, upper_cap=None, parent=parent)

    def multiplier(self, damage_type: DamageTypes, combat_type: CombatTypes) -> float:
        if damage_type is None:
            raise ValueError("Not given multiplier type")

        attr: CappedStat
        attr = getattr(self, damage_type.value.lower())
        if combat_type == CombatTypes.DAMAGE:
            return pow(1.01, attr.value)
        if combat_type == CombatTypes.RESIST:
            return pow(0.99, attr.value)
