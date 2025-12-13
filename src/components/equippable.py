from __future__ import annotations

from typing import TYPE_CHECKING, Tuple, Dict, List, Optional

from components.base_component import BaseComponent
from components.equipment_types import EquipmentTypes

from components.stats.stat_modifier import StatModifier
from components.stats.stat_mod_types import StatModType
from components.stats.character_stat import CharacterStat

if TYPE_CHECKING:
    from entity import Item, Actor
    from components.stats.stat_types import StatTypes
    from components.stats.damage_types import DamageTypes


class Equippable(BaseComponent):
    parent: Item

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
        self.bonuses = bonuses

    def init_hook(self) -> None:
        """Set the source of all StatModifiers to self.parent."""
        for mods in self.bonuses.values():
            if not isinstance(mods, list):
                mods = [mods]  # wrap single modifier in list
            for mod in mods:
                mod.source = self.parent  # assign the Item as the source

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

    def get_defense(self, actor: Actor) -> Optional[CharacterStat]:
        """
        Build the CharacterStat for this armor's defense from the modifiers dict.
        """
        if self.defense_mods is None:
            return None

        defense = CharacterStat(base_value=0, name="DEFENSE")

        stats = actor.fighter.stats
        for stat_type, modifiers in self.defense_mods.items():
            if not isinstance(modifiers, list):
                modifiers = [modifiers]
            stat = stats.get_stat(stat_type)
            cstat = CharacterStat(base_value=stat, name="DEFENSE")

            for mod in modifiers:
                cstat.add_modifier(mod)

            defense.add_modifier(
                StatModifier(value=cstat, mod_type=StatModType.FLAT, source="DEFENSE")
            )
        return defense


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
