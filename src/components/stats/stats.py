from __future__ import annotations

from typing import TYPE_CHECKING, overload, Dict, Optional, Tuple, List
from copy import deepcopy

import consts
from components.stats.character_stat import CharacterStat
from components.stats.stat_modifier import StatModifier
from components.stats.stat_mod_types import StatModType
from components.stats.resource import Resource
from components.stats.stat_types import StatTypes
from components.stats.damage_types import DamageTypes
from components.stats.damage import Damage
from components.stats.initiative import Initiative
from components.stats.damage_stats import ResistStats, DamageAmpStats, MasteryStats
from components.equipment_types import EquipmentTypes
from components.items.equippable import ArmorEquippable, WeaponEquippable

if TYPE_CHECKING:
    from components.fighter import Fighter
    from components.stats.character_stat import CappedStat
    from components.stats.weapon_range import WeaponRange

_STAT_BUILD_TABLE = {
    StatTypes.HP: (
        StatTypes.HP.normalized,
        Resource,
        "_create_hp",
    ),
    StatTypes.ENERGY: (
        StatTypes.ENERGY.normalized,
        Resource,
        "_create_energy",
    ),
    StatTypes.MANA: (
        StatTypes.MANA.normalized,
        Resource,
        "_create_mana",
    ),
    StatTypes.CARRYING_CAPACITY: (
        StatTypes.CARRYING_CAPACITY.normalized,
        Resource,
        "_create_carrying_capacity",
    ),
    StatTypes.ENCUMBRANCE: (
        StatTypes.ENCUMBRANCE.normalized,
        Resource,
        "_create_encumbrance",
    ),
    StatTypes.HP_REGEN: (
        StatTypes.HP_REGEN.normalized,
        CharacterStat,
        "_create_health_regen",
    ),
    StatTypes.ENERGY_REGEN: (
        StatTypes.ENERGY_REGEN.normalized,
        CharacterStat,
        "_create_energy_regen",
    ),
    StatTypes.MANA_REGEN: (
        StatTypes.MANA_REGEN.normalized,
        CharacterStat,
        "_create_mana_regen",
    ),
}


class Stats:

    def __init__(
        self,
        *,
        parent: Fighter,
        base_stats: Dict[StatTypes, int | float],
        damage_resists: Optional[Dict[DamageTypes, float]],
        damage_amps: Optional[Dict[DamageTypes, float]],
        damage_masteries: Optional[Dict[DamageTypes, float]],
        natural_defense_dict: Optional[
            Dict[StatTypes, StatModifier | List[StatModifier]]
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
        self.parent = parent

        # fixing dicts (these ahve to be done like this cause otherwise you get Pylint W0102 (dangerous default argument))
        if natural_defense_dict is None:
            natural_defense_dict = deepcopy(consts.DEFAULT_DEFENSE_DICT)
        if natural_weapon_attack_dict is None:
            natural_weapon_attack_dict = deepcopy(consts.DEFAULT_UNARMED_ATTACK_DICT)
        if natural_weapon_damage_dict is None:
            natural_weapon_damage_dict = deepcopy(consts.DEFAULT_UNARMED_DAMAGE_DICT)
        if natural_weapon_range is None:
            natural_weapon_range = deepcopy(consts.DEFAULT_UNARMED_WEAPON_RANGE)

        self.strength = CharacterStat(
            base_value=base_stats[StatTypes.STRENGTH], name=StatTypes.STRENGTH.value
        )

        self.dexterity = CharacterStat(
            base_value=base_stats[StatTypes.DEXTERITY], name=StatTypes.DEXTERITY.value
        )

        self.constitution = CharacterStat(
            base_value=base_stats[StatTypes.CONSTITUTION],
            name=StatTypes.CONSTITUTION.value,
        )

        self.intelligence = CharacterStat(
            base_value=base_stats[StatTypes.INTELLIGENCE],
            name=StatTypes.INTELLIGENCE.value,
        )

        self.cunning = CharacterStat(
            base_value=base_stats[StatTypes.CUNNING], name=StatTypes.CUNNING.value
        )

        self.willpower = CharacterStat(
            base_value=base_stats[StatTypes.WILLPOWER], name=StatTypes.WILLPOWER.value
        )

        # if base_stats gives an hp, use it. if not, create hp the normal way
        # providing an hp value in base_stats is a way to overrride the typical hp calculation
        # same with the rest!

        self.hp: Resource
        self.energy: Resource
        self.mana: Resource
        self.carrying_capacity: Resource
        self.encumbrance: Resource
        self.hp_regen: CharacterStat
        self.energy_regen: CharacterStat
        self.mana_regen: CharacterStat
        # actually making the stats
        for stat_type, (attr, ctor, factory_name) in _STAT_BUILD_TABLE.items():
            self._build_optional_stat(
                base_stats=base_stats,
                stat_type=stat_type,
                attr_name=attr,
                ctor=ctor,
                default_factory_name=factory_name,
            )

        self.initiative = Initiative(self)
        self.damage_resists = ResistStats(damage_types=damage_resists, parent=self)
        self.damage_amps = DamageAmpStats(damage_types=damage_amps, parent=self)
        self.damage_masteries = MasteryStats(damage_types=damage_masteries, parent=self)

        self.naked_head_defense = ArmorEquippable(
            equipment_type=EquipmentTypes.HEAD,
            defense_mods=natural_defense_dict,
        )
        self.naked_torso_defense = ArmorEquippable(
            equipment_type=EquipmentTypes.TORSO,
            defense_mods=natural_defense_dict,
        )
        self.naked_legs_defense = ArmorEquippable(
            equipment_type=EquipmentTypes.LEGS,
            defense_mods=natural_defense_dict,
        )
        self.naked_feet_defense = ArmorEquippable(
            equipment_type=EquipmentTypes.FEET,
            defense_mods=natural_defense_dict,
        )

        self.unarmed_weapon = WeaponEquippable(
            equipment_type=(EquipmentTypes.MAIN_HAND, EquipmentTypes.OFF_HAND),
            attack_mods=natural_weapon_attack_dict,
            damage_mods=natural_weapon_damage_dict,
            weapon_range=natural_weapon_range,
            attack_init_cost=natural_weapon_attack_init_cost,
        )

        self.flat_weapon_attack = CharacterStat(base_value=0, name="BASE")
        self.flat_weapon_damage: Dict[DamageTypes, CharacterStat] = {}
        for damtype in DamageTypes:
            self.flat_weapon_damage[damtype] = CharacterStat(base_value=0, name="BASE")
        self.flat_armor_defense = CharacterStat(base_value=0, name="BASE")

    @property
    def attack(self) -> List[float]:
        weapon = self._resolve_weapon(self.unarmed_weapon)
        attacks: List[float] = []

        for wp in weapon:
            attack = (
                wp.get_attack(self.parent.parent).value + self.flat_weapon_attack.value
            )
            attacks.append(attack)
        return attacks

    @property
    def damage(self) -> List[Damage]:

        weapon = self._resolve_weapon(self.unarmed_weapon)
        damages: List[Damage] = []

        for wp in weapon:
            damage = wp.get_damage(self.parent.parent)
            damage = damage.add(Damage(self.flat_weapon_damage))
            damages.append(damage)
        return damages

    @property
    def attack_init_cost(self) -> List[int | float]:
        weapon = self._resolve_weapon(self.unarmed_weapon)
        attack_init_costs = []

        for wp in weapon:
            attack_init_cost = (
                wp.get_attack_init_cost(actor=self.parent.parent)
                * self.initiative.attack_multiplier
            )
            attack_init_costs.append(attack_init_cost)
        return attack_init_costs

    @property
    def attack_range(self) -> List[WeaponRange]:
        weapon = self._resolve_weapon(self.unarmed_weapon)
        if not isinstance(weapon, tuple):
            weapon = tuple(weapon)
        weapon: tuple[WeaponEquippable]

        lowest_attack_range = WeaponRange(9999)
        for wp in weapon:
            weapon_range = wp.weapon_range
            if weapon_range.max_range < lowest_attack_range.max_range:
                lowest_attack_range = weapon_range

        attack_range: List[WeaponRange] = []
        for _ in len(weapon):
            attack_range.append(lowest_attack_range)

        return attack_range

    @property
    def head_defense(self) -> CharacterStat:
        return self._resolve_slot_defense(
            slot=EquipmentTypes.HEAD, naked_defense=self.naked_head_defense
        )

    @property
    def torso_defense(self) -> CharacterStat:
        return self._resolve_slot_defense(
            slot=EquipmentTypes.TORSO, naked_defense=self.naked_torso_defense
        )

    @property
    def legs_defense(self) -> CharacterStat:
        return self._resolve_slot_defense(
            slot=EquipmentTypes.LEGS, naked_defense=self.naked_legs_defense
        )

    @property
    def feet_defense(self) -> CharacterStat:
        return self._resolve_slot_defense(
            slot=EquipmentTypes.FEET, naked_defense=self.naked_feet_defense
        )

    @property
    def total_defense(self) -> float:
        return (
            self.head_defense.value
            + self.torso_defense.value
            + self.legs_defense.value
            + self.feet_defense.value
        )

    def _resolve_weapon(
        self, unarmed_weapon: WeaponEquippable
    ) -> List[WeaponEquippable]:
        actor = self.parent.parent
        equipment = actor.equipment
        main = equipment.slots.get(EquipmentTypes.MAIN_HAND)
        off = equipment.slots.get(EquipmentTypes.OFF_HAND)
        if main is None and off is None:
            return [unarmed_weapon]
        if not equipment.is_dual_wielding or not equipment.is_two_handing:
            if main is not None:
                return [main.equippable]
            return [off.equippable]
        if equipment.is_two_handing:
            return [main.equippable]
        if equipment.is_dual_wielding:
            return [main.equippable, off.equippable]
        raise ValueError(f"Something went terribly wrong")

    def _resolve_slot_defense(
        self,
        slot: EquipmentTypes,
        naked_defense: ArmorEquippable,
    ) -> CharacterStat:
        """
        Resolve defense for a given equipment slot.

        Prefers equipped item defense if present and valid; otherwise falls back
        to the provided naked defense.
        """
        actor = self.parent.parent
        item = actor.equipment.slots.get(slot)

        if item is not None:
            item_defense = item.equippable.get_defense(actor)
            if item_defense is not None:
                return item_defense

        return naked_defense.get_defense(actor)

    def regenerate(self, diff: int) -> None:
        self.initiative.initiative.modify(diff, sudo=True)

        # initiative is stored as a giant int, this scales it down correctly to be a value that is
        # typically between 0 and 1, which it expects. regen is slow!
        time_factor = diff / consts.MAX_INIT
        self.hp.regenerate(time_factor=time_factor, regen=self.hp_regen.value)
        self.energy.regenerate(time_factor=time_factor, regen=self.energy_regen.value)
        self.mana.regenerate(time_factor=time_factor, regen=self.mana_regen.value)

    @overload
    def get_stat(self, stat: StatTypes) -> CharacterStat: ...

    @overload
    def get_stat(
        self, stat: Tuple[StatTypes, DamageTypes]
    ) -> CharacterStat | CappedStat: ...

    def get_stat(
        self, stat: StatTypes | Tuple[StatTypes, DamageTypes]
    ) -> CharacterStat | CappedStat:
        if isinstance(stat, (tuple, list)):
            if stat[0] == StatTypes.FLAT_WEAPON_DAMAGE:
                # 1st element is flat_weapon_damage, second is DamageType
                return self.flat_weapon_damage[stat[1]]
            # else, is either for damage resists/amps/masteries
            damage_stat_type, damage_type = stat
            return getattr(
                getattr(self, damage_stat_type.normalized),
                damage_type.normalized,
            )

        if stat == StatTypes.GLOBAL_SPEED:
            return self.initiative.global_speed
        if stat == StatTypes.ATTACK_SPEED:
            return self.initiative.attack_speed
        if stat == StatTypes.MOVEMENT_SPEED:
            return self.initiative.movement_speed
        if stat == StatTypes.CASTING_SPEED:
            return self.initiative.casting_speed

        stat_obj = getattr(self, stat.normalized)
        if isinstance(stat_obj, Resource):
            # to get the CappedStat from resource, return stat_obj.max, NOT stat_obj
            return stat_obj.max
        return stat_obj

    # ################# #
    # STAT CONSTRUCTORS #
    # ################# #

    def _build_optional_stat(
        self,
        *,
        base_stats: dict,
        stat_type: StatTypes,
        attr_name: str,
        ctor: type,
        default_factory_name: str,
    ) -> None:
        override = None
        if base_stats is not None:
            override = base_stats.get(stat_type)

        if override is not None:
            stat = ctor(base_value=override, name=stat_type.value)
        else:
            stat = getattr(self, default_factory_name)()

        setattr(self, attr_name, stat)

    def _create_hp(self) -> Resource:
        # base hp is 500% con (plus some from levels). base is 10 (at lvl 1)
        hp = Resource(base_value=0, name=StatTypes.HP.value)
        _hp_con = CharacterStat(base_value=self.constitution, name="BASE")
        _hp_con.add_modifier(
            StatModifier(value=5, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )
        hp.max.add_modifier(
            StatModifier(value=_hp_con, mod_type=StatModType.FLAT, source="BASE")
        )
        hp.maximize()

        return hp

    def _create_energy(self) -> Resource:
        # base energy is 10 + 25% str, 25% dex, 50% con
        energy = Resource(base_value=10, name=StatTypes.ENERGY.value)

        _energy_str = CharacterStat(base_value=self.strength, name="BASE")
        _energy_str.add_modifier(
            StatModifier(value=0.25, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )

        _energy_dex = CharacterStat(base_value=self.dexterity, name="BASE")
        _energy_dex.add_modifier(
            StatModifier(value=0.25, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )

        _energy_con = CharacterStat(base_value=self.constitution, name="BASE")
        _energy_con.add_modifier(
            StatModifier(value=0.5, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )

        energy.max.add_modifier(
            StatModifier(value=_energy_str, mod_type=StatModType.FLAT, source="BASE")
        )
        energy.max.add_modifier(
            StatModifier(value=_energy_dex, mod_type=StatModType.FLAT, source="BASE")
        )
        energy.max.add_modifier(
            StatModifier(value=_energy_con, mod_type=StatModType.FLAT, source="BASE")
        )
        energy.maximize()

        return energy

    def _create_mana(self) -> Resource:
        # base mana is 10 + 250% intelligence
        mana = Resource(base_value=10, name=StatTypes.MANA.value)

        _mana_int = CharacterStat(base_value=self.intelligence, name="BASE")
        _mana_int.add_modifier(
            StatModifier(value=2.5, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )

        mana.max.add_modifier(
            StatModifier(value=_mana_int, mod_type=StatModType.FLAT, source="BASE")
        )

        mana.maximize()

        return mana

    def _create_carrying_capacity(self) -> Resource:
        # base carrying capacity is 1000% strength
        carrying_capacity = Resource(
            base_value=0, name=StatTypes.CARRYING_CAPACITY.value
        )

        _cc_str = CharacterStat(base_value=self.strength, name="BASE")
        _cc_str.add_modifier(
            StatModifier(value=10, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )
        carrying_capacity.max.add_modifier(
            StatModifier(value=_cc_str, mod_type=StatModType.FLAT, source="BASE")
        )

        carrying_capacity.minimize()

        return carrying_capacity

    def _create_encumbrance(self) -> Resource:
        # encumbrance (maximum weight of equipped items) is 50% of carrying capacity
        encumbrance = Resource(base_value=0, name=StatTypes.ENCUMBRANCE.value)

        _enc_cc = CharacterStat(
            base_value=self.carrying_capacity.max.value, name="BASE"
        )
        _enc_cc.add_modifier(
            StatModifier(value=0.25, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )

        encumbrance.max.add_modifier(
            StatModifier(value=_enc_cc, mod_type=StatModType.FLAT, source="BASE")
        )

        encumbrance.minimize()

        return encumbrance

    def _create_health_regen(self) -> CharacterStat:
        # hp regen is 4e-4% CON and 1e-4% WIL
        hp_regen = CharacterStat(base_value=0, name=StatTypes.HP_REGEN.value)

        _hp_regen_con = CharacterStat(base_value=self.constitution, name="BASE")
        _hp_regen_con.add_modifier(
            StatModifier(value=4e-4, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )

        hp_regen.add_modifier(
            stat_mod=StatModifier(
                value=_hp_regen_con, mod_type=StatModType.FLAT, source="BASE"
            )
        )

        _hp_regen_willpower = CharacterStat(base_value=self.willpower, name="BASE")
        _hp_regen_willpower.add_modifier(
            StatModifier(value=1e-4, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )

        hp_regen.add_modifier(
            stat_mod=StatModifier(
                value=_hp_regen_willpower, mod_type=StatModType.FLAT, source="BASE"
            )
        )

        #
        # example of adding extra 10% con scaling from an amulet item
        # _amulet = CharacterStat(base_value=self.constitution, name="amulet")
        # _amulet.add_modifier(StatModifier(value=0.1, mod_type=StatModType.PERCENT_MULT, source="amulet"))
        # hp_regen.add_modifier(StatModifier(value=_amulet, mod_type=StatModType.FLAT))

        # ^ the lessen to take away is to never try to MODIFY StatModifiers, thats not best practices
        # instead, make new ones for each object! so much easier

        return hp_regen

    def _create_energy_regen(self) -> CharacterStat:
        # energy regen is 4e-2% CON and 1e-2% WIL
        energy_regen = CharacterStat(base_value=0, name=StatTypes.ENERGY_REGEN)
        _energy_regen_con = CharacterStat(base_value=self.constitution, name="BASE")
        _energy_regen_con.add_modifier(
            StatModifier(value=4e-2, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )

        _energy_regen_wil = CharacterStat(base_value=self.willpower, name="BASE")
        _energy_regen_wil.add_modifier(
            StatModifier(value=1e-2, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )

        energy_regen.add_modifier(
            StatModifier(
                value=_energy_regen_con, mod_type=StatModType.FLAT, source="BASE"
            )
        )
        energy_regen.add_modifier(
            StatModifier(
                value=_energy_regen_wil, mod_type=StatModType.FLAT, source="BASE"
            )
        )

        return energy_regen

    def _create_mana_regen(self) -> CharacterStat:
        # mana regen is 4e-3% INT and 1e-3% WIL
        mana_regen = CharacterStat(base_value=0, name=StatTypes.MANA_REGEN)
        _mana_regen_int = CharacterStat(base_value=self.intelligence, name="BASE")
        _mana_regen_int.add_modifier(
            StatModifier(value=4e-3, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )

        _mana_regen_wil = CharacterStat(base_value=self.willpower, name="BASE")
        _mana_regen_wil.add_modifier(
            StatModifier(value=1e-3, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )

        mana_regen.add_modifier(
            StatModifier(
                value=_mana_regen_int, mod_type=StatModType.FLAT, source="BASE"
            )
        )
        mana_regen.add_modifier(
            StatModifier(
                value=_mana_regen_wil, mod_type=StatModType.FLAT, source="BASE"
            )
        )

        return mana_regen

    def _create_naked_defense(self) -> CharacterStat:
        naked_defense = CharacterStat(base_value=0, name="NAKED_DEFENSE")
        _nd_dex = CharacterStat(base_value=self.dexterity, name="BASE")
        _nd_dex.add_modifier(
            StatModifier(value=0.25, mod_type=StatModType.PERCENT_MULT, source="BASE")
        )

        naked_defense.add_modifier(
            StatModifier(value=_nd_dex, mod_type=StatModType.FLAT, source="BASE")
        )
        return naked_defense

    def _create_naked_attack(self) -> CharacterStat:
        # 25% str, 75% dex
        naked_attack = CharacterStat(base_value=0, name="NAKED_ATTACK")

        _str = CharacterStat(base_value=self.strength, name="BASE")
        _str.add_modifier(
            StatModifier(value=0.25, mod_type=StatModType.PERCENT_MULT, source="Base")
        )

        _dex = CharacterStat(base_value=self.dexterity, name="BASE")
        _dex.add_modifier(
            StatModifier(value=0.75, mod_type=StatModType.PERCENT_MULT, source="Base")
        )

        naked_attack.add_modifier(
            StatModifier(value=_str, mod_type=StatModType.FLAT, source="BASE")
        )
        naked_attack.add_modifier(
            StatModifier(value=_dex, mod_type=StatModType.FLAT, source="BASE")
        )

        return naked_attack

    def _create_naked_damage(self) -> CharacterStat:
        # is a 25 init weapon, so total of 25% damage
        # 20% str, 5% dex
        naked_damage = CharacterStat(base_value=0, name="NAKED_DAMAGE")
        _str = CharacterStat(base_value=self.strength, name="BASE")
        _str.add_modifier(
            StatModifier(value=0.2, mod_type=StatModType.PERCENT_MULT, source="Base")
        )

        _dex = CharacterStat(base_value=self.dexterity, name="BASE")
        _dex.add_modifier(
            StatModifier(value=0.05, mod_type=StatModType.PERCENT_MULT, source="Base")
        )

        naked_damage.add_modifier(
            StatModifier(value=_str, mod_type=StatModType.FLAT, source="BASE")
        )
        naked_damage.add_modifier(
            StatModifier(value=_dex, mod_type=StatModType.FLAT, source="BASE")
        )

        return naked_damage
