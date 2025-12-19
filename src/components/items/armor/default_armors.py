from __future__ import annotations

from typing import Dict, List
from base_enum import BaseEnum
from pathlib import Path
import json

import consts

from components.items.armor.armor_types import ArmorTypes, ARMORS
from components.equipment_types import EquipmentTypes
from components.stats.stat_modifier import StatModifier
from components.stats.stat_types import StatTypes
from components.stats.stat_mod_types import StatModType
from components.stats.damage_types import DamageTypes
from components.stats.weapon_range import WeaponRange


def create_defense_dict(
    defense_dict: Dict[StatTypes | str, float],
) -> Dict[StatTypes, StatModifier]:
    final_dict = {}

    for stat, val in defense_dict.items():
        if isinstance(stat, str):
            stat = StatTypes.enum_from_string(stat)
        stat: StatTypes
        final_dict[stat] = StatModifier(
            value=val, mod_type=StatModType.PERCENT_MULT, source="SELF"
        )
    return final_dict


def load_default_armor_args(armor: ArmorTypes) -> Dict:
    armor_def = ARMORS[armor]
    path = armor_def.path
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    data: Dict
    defense_dict = data.get("defense")
    if defense_dict is not None:
        defense_dict = create_defense_dict(data.get("defense"))

    base_weight = data.get("base_weight")

    if data.get("speed_penalty") is not None:
        bonuses = {
            StatTypes.GLOBAL_SPEED: StatModifier(
                value=1 - data.get("speed_penalty"),
                mod_type=StatModType.PERCENT_MULT,
                source="SELF",
            )
        }
    else:
        bonuses = {}

    final_dict = {
        "base_weight": base_weight,
        "equippable_args": {
            "bonuses": bonuses,
            "defense_mods": defense_dict,
        },
    }
    return final_dict
