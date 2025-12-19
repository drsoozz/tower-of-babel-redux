from __future__ import annotations

from typing import Dict, List
from base_enum import BaseEnum
from pathlib import Path
import json

import consts

from components.items.weapons.weapon_types import WeaponTypes, WEAPONS
from components.equipment_types import EquipmentTypes
from components.stats.stat_modifier import StatModifier
from components.stats.stat_types import StatTypes
from components.stats.stat_mod_types import StatModType
from components.stats.damage_types import DamageTypes
from components.stats.weapon_range import WeaponRange


def create_attack_dict(
    attack_dict: Dict[StatTypes | str, float],
) -> Dict[StatTypes, StatModifier]:
    # assuming that the floats are all percent mults

    final_dict = {}

    for stat, val in attack_dict.items():
        if isinstance(stat, str):
            stat = StatTypes.enum_from_string(stat)
        final_dict[stat] = StatModifier(
            value=val, mod_type=StatModType.PERCENT_MULT, source="SELF"
        )
    return final_dict


def create_damage_dict(
    damage_dict: Dict[DamageTypes, Dict[StatTypes, float]],
) -> Dict[DamageTypes, Dict[StatTypes, StatModifier]]:

    final_dict = {}

    for damtype, damval in damage_dict.items():
        if isinstance(damtype, str):
            damtype = DamageTypes.enum_from_string(damtype)
        final_dict[damtype] = create_attack_dict(damval)
    return final_dict


def load_default_weapon_args(weapon: WeaponTypes) -> Dict:
    weapon_def = WEAPONS[weapon]
    path = weapon_def.path
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    data: Dict
    attack_dict = create_attack_dict(data.get("attack"))
    damage_dict = create_damage_dict(data.get("damage"))
    atttack_init_cost = int(data["init_cost"] * consts.MAX_INIT)
    _weapon_range = data.get("weapon_range", None)
    weapon_range = WeaponRange(_weapon_range)
    _equipment_type = tuple(data.get("slots"))
    equipment_type: List = []
    for etype in _equipment_type:
        if etype == "main":
            equipment_type.append(EquipmentTypes.MAIN_HAND)
        if etype == "off":
            equipment_type.append(EquipmentTypes.OFF_HAND)
    equipment_type = (
        tuple(equipment_type) if len(equipment_type) > 1 else equipment_type[0]
    )
    weight = data.get("weight", None)

    final_dict = {
        "weight": weight,
        "equippable_args": {
            "equipment_type": equipment_type,
            "bonuses": {},
            "attack_mods": attack_dict,
            "damage_mods": damage_dict,
            "weapon_range": weapon_range,
            "attack_init_cost": atttack_init_cost,
        },
    }
    print(weapon)
    print(final_dict)
    return final_dict
