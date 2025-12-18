from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Mapping
from pathlib import Path
import json

import consts
from components import ai
from components.fighter import Fighter
from components.level import Level
from components.inventory import Inventory
from components.equipment import Equipment
from entity import Item, Actor
from components.items.equippable import Equippable, ArmorEquippable, WeaponEquippable
from components.items.weapons.default_weapons import (
    load_default_weapon_args,
    create_attack_dict,
    create_damage_dict,
)
from components.stats.weapon_range import WeaponRange
from components.items.weapons.weapon_types import WeaponTypes
from components.items.armor.armor_types import ArmorTypes
from components.items.armor.default_armors import (
    load_default_armor_args,
    create_defense_dict,
)
from components.stats.stat_types import StatTypes
from components.stats.damage_types import DamageTypes
from components.stats.stat_mod_types import StatModType
from components.stats.stat_modifier import StatModifier
from components.equipment_types import EquipmentTypes

if TYPE_CHECKING:
    pass

BASE_DATA_PATH = consts.BASE_PATH / Path("entity_data")


def load_entity(entity_name: str) -> Item | Actor:
    path = BASE_DATA_PATH / Path(f"{entity_name}.json")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    data: Dict
    entity_type: str = data["entity_type"]
    char: str = data["char"]
    color: tuple = tuple(data["color"])
    name: str = data["name"]
    weight: float = data.get("weight", None)
    if entity_type.lower() == "item":
        item_components = load_item_components(data)
        item_args = {"char": char, "color": color, "name": name, "weight": weight}
        for component_name, component_obj in item_components.items():
            if component_name == "weight":
                if weight is None:
                    item_args[component_name] = component_obj
            else:
                item_args[component_name] = component_obj
        return Item(**item_args)
    if entity_type.lower() == "actor":
        actor_args = load_actor(data)
        actor_args["char"] = char
        actor_args["color"] = color
        actor_args["name"] = name
        return Actor(**actor_args)


def load_item_components(data: Dict) -> Dict:
    equippable_dict = data.get("equippable", None)
    if equippable_dict is not None:
        return load_equippable(data)
    consumable_dict = data.get("consumable", None)
    if consumable_dict is not None:
        pass


def load_equippable(data: Dict) -> Dict:
    match data.get("equippable_type", None):
        case "armor":
            return load_armor(data)
        case "weapon":
            return load_weapon(data)
        case _:
            return load_normal_equippable(data)


def load_weapon(data: Dict) -> Dict:
    equippable_data = data.get("equippable")
    base = equippable_data.get("base_weapon", None)
    if base is not None:
        base: WeaponTypes = WeaponTypes.enum_from_string(base)
        base = load_default_weapon_args(base)

    bonuses_data = equippable_data.get("bonuses", None)
    bonuses: Dict = {}
    if bonuses_data is not None:
        for bonus in bonuses_data:
            bonus: Dict
            stat_type = StatTypes.enum_from_string(bonus.get("stat"))
            damage_type = bonus.get("damage_type", None)
            if damage_type is not None:
                damage_type = DamageTypes.enum_from_string(damage_type)
            value = bonus.get("value")
            mod_type = StatModType.enum_from_string(bonus.get("mod_type"))
            stat_modifier = StatModifier(
                value=value, mod_type=mod_type, source="WILL_BE_REWRITTEN"
            )
            if damage_type is not None:
                bonuses[(stat_type, damage_type)] = stat_modifier
            else:
                bonuses[stat_type] = stat_modifier
    base["equippable_args"]["bonuses"] = bonuses
    weight = base.get("weight", None)
    if data.get("weight", None) is not None:
        weight = data.get("weight")
    equippable_args = base["equippable_args"]
    return {"weight": weight, "equippable": WeaponEquippable(**equippable_args)}


def load_armor(data: Dict) -> Dict:
    base = data.get("base_armor", None)
    if base is not None:
        base = ArmorTypes.enum_from_string(base)
        base = load_default_armor_args(base)

    base_bonuses = base.get("equippable_args", {}).get(
        "bonuses", {}
    )  # just global speed stuff (from the base's json)
    bonuses_data = data.get("bonuses", {})  # stuff from the actual item json

    bonuses: Dict = base_bonuses
    if bonuses_data is not None:
        for bonus in bonuses_data:
            bonus: Dict
            stat_type = StatTypes.enum_from_string(bonus.get("stat"))
            if stat_type == StatTypes.GLOBAL_SPEED:
                # special case of pre-existing modifier because all armor has a global speed mod
                _old = bonuses[stat_type]
                bonuses[stat_type] = [_old]
                stat_modifier = StatModifier(
                    value=value, mod_type=mod_type, source="WILL_BE_REWRITTEN"
                )
                bonuses[stat_type].append(stat_modifier)
                continue

            damage_type = bonus.get("damage_type", None)
            if damage_type is not None:
                damage_type = DamageTypes.enum_from_string(damage_type)
            value = bonus.get("value")
            mod_type = StatModType.enum_from_string(bonus.get("mod_type"))
            stat_modifier = StatModifier(
                value=value, mod_type=mod_type, source="WILL_BE_REWRITTEN"
            )
            if damage_type is not None:
                bonuses[(stat_type, damage_type)] = stat_modifier
            else:
                bonuses[stat_type] = stat_modifier

    slots = data.get("slots")
    base["equippable_args"]["bonuses"] = bonuses
    base_weight = base.get("base_weight", None)

    weight = data.get("weight", None)
    if weight is not None:
        weight = base_weight
    else:
        match slots:
            case EquipmentTypes.HEAD:
                weight = base_weight * consts.HEAD_WEIGHT_MODIFIER
            case EquipmentTypes.TORSO:
                weight = base_weight * consts.TORSO_WEIGHT_MODIFIER
            case EquipmentTypes.LEGS:
                weight = base_weight * consts.LEGS_WEIGHT_MODIFIER
            case EquipmentTypes.FEET:
                weight = base_weight * consts.FEET_WEIGHT_MODIFIER
            case _:
                print("!?!?!")

    equippable_args = base["equippable_args"]
    equippable_args["equipment_type"] = EquipmentTypes.enum_from_string(slots)
    return {"weight": weight, "equippable": ArmorEquippable(**equippable_args)}


def load_normal_equippable(data: Dict) -> Dict:
    equippable_data = data.get("equippable")
    slots = equippable_data.get("slots")
    if isinstance(slots, list):
        slots = tuple(slots)
    weight = data.get("weight")

    bonuses_data = equippable_data.get("bonuses", {})  # stuff from the actual item json

    bonuses: Dict = {}
    if bonuses_data != {}:
        for bonus in bonuses_data:
            bonus: Dict
            stat_type = StatTypes.enum_from_string(bonus.get("stat"))
            damage_type = bonus.get("damage_type", None)
            if damage_type is not None:
                damage_type = DamageTypes.enum_from_string(damage_type)
            value = bonus.get("value")
            mod_type = StatModType.enum_from_string(bonus.get("mod_type"))
            stat_modifier = StatModifier(
                value=value, mod_type=mod_type, source="WILL_BE_REWRITTEN"
            )
            if damage_type is not None:
                bonuses[(stat_type, damage_type)] = stat_modifier
            else:
                bonuses[stat_type] = stat_modifier

    equippable_args = {}
    equippable_args["bonuses"] = bonuses
    equippable_args["equipment_type"] = slots
    return {"weight": weight, "equippable": Equippable(**equippable_args)}


def load_actor(data: Dict) -> Dict:
    ai_cls = load_ai_module(data)
    fighter = load_fighter_module(data)
    inventory = load_inventory_module(data)
    level = load_level_module(data)
    args = {
        "ai_cls": ai_cls,
        "fighter": fighter,
        "inventory": inventory,
        "level": level,
        "equipment": Equipment(),
    }
    return args


def load_ai_module(data: Dict) -> ai.BaseAI:
    type_of_ai = data.get("ai_cls")
    ai_cls = getattr(ai, type_of_ai)
    return ai_cls


def load_fighter_module(data: Dict) -> Fighter:
    _fighter_data = data.get("fighter")
    # 1. create base_stats
    _base_stats_data: Dict = _fighter_data.get("base_stats")
    base_stats: Dict[StatTypes, int | float] = {}
    for stype, sval in _base_stats_data.items():
        stype = StatTypes.enum_from_string(stype)
        base_stats[stype] = sval

    # 2. create damage_resists
    _damage_resists_data: Dict = _fighter_data.get("damage_resists", None)
    damage_resists = parse_damage_type_map(_damage_resists_data)

    # 3. create damage_amps
    _damage_amps_data: Dict = _fighter_data.get("damage_amps", None)
    damage_amps = parse_damage_type_map(_damage_amps_data)

    # 4. create damage_masteries
    _damage_masteries_data: Dict = _fighter_data.get("damage_masteries", None)
    damage_masteries = parse_damage_type_map(_damage_masteries_data)

    # 5. create natural_defense_dict
    _defense_data: Dict = _fighter_data.get("natural_defense_dict", None)
    natural_defense_dict = None
    if _defense_data is not None:
        natural_defense_dict = create_defense_dict(_defense_data)

    # 6. create natural_weapon_attack_dict
    _attack_data: Dict = _fighter_data.get("natural_weapon_attack_dict", None)
    natural_weapon_attack_dict = None
    if _attack_data is not None:
        natural_weapon_attack_dict = create_attack_dict(_attack_data)

    # 7. create natural_weapon_damage_dict
    _damage_data: Dict = _fighter_data.get("natural_weapon_damage_dict", None)
    natural_weapon_damage_dict = None
    if _damage_data is not None:
        natural_weapon_damage_dict = create_damage_dict(_damage_data)

    # 8. create natural_weapon_range
    _weapon_range_data: Optional[int] = _fighter_data.get("natural_weapon_range", None)
    natural_weapon_range = WeaponRange(_weapon_range_data)

    # 9. create natural_weapon_attack_init_cost
    _attack_init_cost_data: float = _fighter_data.get(
        "natural_weapon_attack_init_cost", None
    )
    natural_weapon_attack_init_cost = None
    if _attack_init_cost_data is not None:
        natural_weapon_attack_init_cost = int(consts.MAX_INIT * _attack_init_cost_data)

    # 10. create args dict
    args = {
        "base_stats": base_stats,
        "damage_resists": damage_resists,
        "damage_amps": damage_amps,
        "damage_masteries": damage_masteries,
        "natural_defense_dict": natural_defense_dict,
        "natural_weapon_attack_dict": natural_weapon_attack_dict,
        "natural_weapon_damage_dict": natural_weapon_damage_dict,
        "natural_weapon_range": natural_weapon_range,
        "natural_weapon_attack_init_cost": natural_weapon_attack_init_cost,
    }

    # 11. create fighter object
    fighter_object = Fighter(**args)
    return fighter_object


def parse_damage_type_map(
    raw_data: Optional[Mapping[str, float]],
) -> Optional[Dict[DamageTypes, float]]:
    """
    Convert a JSON-loaded damage-type mapping into a DamageTypes-keyed dict.

    Args:
        raw_data:
            A mapping from string damage type names to numeric values
            (as loaded from JSON), or None if the field is absent.

    Returns:
        A dict mapping DamageTypes to float values, or None if raw_data is None.
    """
    if raw_data is None:
        return None

    parsed: Dict[DamageTypes, float] = {}

    for dtype_str, value in raw_data.items():
        dtype = DamageTypes.enum_from_string(dtype_str)
        parsed[dtype] = value

    return parsed


def load_inventory_module(data: Dict) -> Inventory:
    return Inventory(capacity=0)


def load_level_module(data: Dict) -> Level:
    monster_tier = data.get("monster_tier")
    xp_given = get_exp_given_from_monster_tier(monster_tier)
    return Level(xp_given=xp_given)


def get_exp_given_from_monster_tier(monster_tier: int) -> int:
    return monster_tier + consts.EXP_BASE
