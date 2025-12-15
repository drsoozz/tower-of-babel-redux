from __future__ import annotations

from typing import TYPE_CHECKING, Tuple, Dict, List, Optional


import consts

from components.base_component import BaseComponent
from components.equipment_types import EquipmentTypes
from components.stats.stat_modifier import StatModifier
from components.stats.character_stat import CharacterStat
from components.stats.stat_types import StatTypes
from components.stats.stat_mod_types import StatModType
from components.stats.damage_types import DamageTypes
from components.stats.build_composite_stat import build_composite_stat
from components.stats.weapon_range import WeaponRange
from components.stats.damage import Damage

if TYPE_CHECKING:
    from entity import Item, Actor


class Equippable(BaseComponent):
    parent: Item

    # overwritten by subclasses, not really used here
    VALID_EQUIPMENT_TYPES = list(EquipmentTypes) + [
        (EquipmentTypes.MAIN_HAND, EquipmentTypes.OFF_HAND)
    ]

    def __init__(
        self,
        equipment_type: EquipmentTypes | Tuple[EquipmentTypes, ...],
        bonuses: Optional[
            Dict[
                StatTypes | Tuple[StatTypes, DamageTypes],
                StatModifier | List[StatModifier],
            ]
        ] = None,
    ):
        self.equipment_type = equipment_type
        self.bonuses = bonuses or {}

    def init_hook(self) -> None:
        """Set the source of all StatModifiers to self.parent."""
        self.make_all_sources_self(self.bonuses)

    def make_all_sources_self(self, dict_to_fix: Dict) -> None:
        for mods in dict_to_fix.values():
            if isinstance(mods, dict):
                self.make_all_sources_self(mods)
                continue
            if not isinstance(mods, list):
                mods = [mods]
            for mod in mods:
                mod.source = self.parent

    def equip(self, actor: Actor) -> None:
        if self.bonuses is not None:
            return
        stats = actor.fighter.stats
        for stat_type, modifiers in self.bonuses.items():
            if not isinstance(modifiers, list):
                modifiers = [modifiers]
            stat = stats.get_stat(stat_type)
            for mod in modifiers:
                stat.add_modifier(mod)

    def unequip(self, actor: Actor) -> None:
        if self.bonuses is not None:
            return
        stats = actor.fighter.stats
        for stat_type in self.bonuses:
            stat = stats.get_stat(stat_type)
            stat.remove_all_from_source(self.parent)


class WeaponEquippable(Equippable):
    VALID_EQUIPMENT_TYPES = [
        EquipmentTypes.MAIN_HAND,
        EquipmentTypes.OFF_HAND,
        (EquipmentTypes.MAIN_HAND, EquipmentTypes.OFF_HAND),
    ]

    def __init__(
        self,
        equipment_type: EquipmentTypes | Tuple[EquipmentTypes],
        bonuses: Optional[
            Dict[
                StatTypes | Tuple[StatTypes, DamageTypes],
                StatModifier | List[StatModifier],
            ]
        ] = None,
        attack_mods: Optional[
            Dict[StatTypes, StatModifier | List[StatModifier]]
        ] = None,
        damage_mods: Optional[
            Dict[DamageTypes, Dict[StatTypes, StatModifier | List[StatModifier]]]
        ] = None,
        weapon_range: Optional[WeaponRange] = None,
        attack_init_cost: float = consts.MAX_INIT / 2,  # 50 init,
    ):
        if equipment_type not in self.VALID_EQUIPMENT_TYPES:
            raise ValueError(
                f"Invalid armor slot: {equipment_type.value}. Must be one of {[slot.value for slot in self.VALID_EQUIPMENT_TYPES]}"
            )
        super().__init__(equipment_type, bonuses)
        self.attack_mods = attack_mods or {}
        self.damage_mods = damage_mods or {}
        self.attack_init_cost = attack_init_cost or {}
        self.weapon_range = weapon_range or WeaponRange(max_range=None)

    def init_hook(self) -> None:
        """Set the source of all StatModifiers to self.parent."""
        self.make_all_sources_self(self.bonuses)
        self.make_all_sources_self(self.attack_mods)
        self.make_all_sources_self(self.damage_mods)

    def get_attack(self, actor: Actor) -> Optional[CharacterStat]:
        if not self.attack_mods:
            return None

        return build_composite_stat(
            actor=actor,
            base_value=0,
            name="ATTACK",
            stat_mods=self.attack_mods,
            source=self,
        )

    def get_damage(self, actor: Actor) -> Damage:
        if not self.damage_mods:
            return None

        final_damage_dict = {}
        for damtype, damdict in self.damage_mods.items():
            final_damage_dict[damtype] = build_composite_stat(
                actor=actor, base_value=0, name="DAMAGE", stat_mods=damdict, source=self
            ).value

        return Damage(final_damage_dict)

    def get_attack_init_cost(self, actor: Actor) -> Optional[CharacterStat]:
        return self.attack_init_cost


class ArmorEquippable(Equippable):
    VALID_EQUIPMENT_TYPES = [
        EquipmentTypes.HEAD,
        EquipmentTypes.TORSO,
        EquipmentTypes.LEGS,
        EquipmentTypes.FEET,
    ]

    def __init__(
        self,
        equipment_type: EquipmentTypes,
        bonuses: Optional[
            Dict[
                StatTypes | Tuple[StatTypes, DamageTypes],
                StatModifier | List[StatModifier],
            ]
        ] = None,
        defense_mods: Dict[StatTypes, StatModifier | List[StatModifier]] = None,
    ):
        if equipment_type not in self.VALID_EQUIPMENT_TYPES:
            raise ValueError(
                f"Invalid armor slot: {equipment_type.value}. Must be one of {[slot.value for slot in self.VALID_EQUIPMENT_TYPES]}"
            )
        super().__init__(equipment_type, bonuses)
        self.defense_mods = defense_mods or {}

    def init_hook(self) -> None:
        """Set the source of all StatModifiers to self.parent."""
        self.make_all_sources_self(self.bonuses)
        self.make_all_sources_self(self.defense_mods)

    def get_defense(self, actor: Actor) -> Optional[CharacterStat]:
        """
        Build the CharacterStat for this armor's defense from the modifiers dict.
        """
        if not self.defense_mods:
            return None

        return build_composite_stat(
            actor=actor,
            base_value=0,
            name="DEFENSE",
            stat_mods=self.defense_mods,
            source=self,
        )


class GreatHammer(WeaponEquippable):
    def __init__(self):
        super().__init__(
            equipment_type=(EquipmentTypes.MAIN_HAND, EquipmentTypes.OFF_HAND),
            bonuses={
                StatTypes.STRENGTH: StatModifier(
                    value=2, mod_type=StatModType.FLAT, source="SELF"
                )
            },
            attack_mods={
                StatTypes.STRENGTH: StatModifier(
                    value=0.5, mod_type=StatModType.PERCENT_MULT, source="SELF"
                ),
                StatTypes.DEXTERITY: StatModifier(
                    value=0.5, mod_type=StatModType.PERCENT_MULT, source="SELF"
                ),
            },
            damage_mods={
                DamageTypes.BLUDGEONING: {
                    StatTypes.STRENGTH: StatModifier(
                        value=0.8, mod_type=StatModType.PERCENT_MULT, source="SELF"
                    ),
                    StatTypes.DEXTERITY: StatModifier(
                        value=0.05, mod_type=StatModType.PERCENT_MULT, source="SELF"
                    ),
                }
            },
            weapon_range=WeaponRange(),
            attack_init_cost=consts.MAX_INIT * (3 / 4),
        )


"""
class Dagger(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentTypes.WEAPON, power_bonus=2)


class Sword(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentTypes.WEAPON, power_bonus=4)


class LeatherArmor(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentTypes.ARMOR, defense_bonus=1)


class ChainMail(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentTypes.ARMOR, defense_bonus=3)
"""
