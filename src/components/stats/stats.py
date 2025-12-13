from __future__ import annotations

from typing import TYPE_CHECKING, overload, Dict, Optional, Tuple

import consts
from components.stats.character_stat import CharacterStat
from components.stats.stat_modifier import StatModifier
from components.stats.stat_mod_types import StatModType
from components.stats.resource import Resource
from components.stats.stat_types import StatTypes
from components.stats.damage_types import DamageTypes
from components.stats.initiative import Initiative
from components.stats.damage_stats import ResistStats, DamageAmpStats, MasteryStats
from components.equipment_types import EquipmentTypes

if TYPE_CHECKING:
    from components.fighter import Fighter
    from components.stats.character_stat import CappedStat


class Stats:
    def __init__(
        self,
        *,
        base_stats: Dict[StatTypes, int | float],
        damage_resists: Optional[Dict[DamageTypes, float]],
        damage_amps: Optional[Dict[DamageTypes, float]],
        damage_masteries: Dict[DamageTypes, float],
        parent: Fighter,
    ):
        self.parent = parent
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
        try:
            self.hp = Resource(
                base_value=base_stats[StatTypes.HP],
                name=StatTypes.HP.value,
            )
        except (KeyError, TypeError):
            self.hp = self._create_hp()
        try:
            self.energy = Resource(
                base_value=base_stats[StatTypes.ENERGY], name=StatTypes.ENERGY.value
            )
        except (KeyError, TypeError):
            self.energy = self._create_energy()

        try:
            self.mana = Resource(
                base_value=base_stats[StatTypes.MANA], name=StatTypes.MANA.value
            )
        except (KeyError, TypeError):
            self.mana = self._create_mana()

        try:
            self.carrying_capacity = Resource(
                base_value=base_stats[StatTypes.CARRYING_CAPACITY],
                name=StatTypes.CARRYING_CAPACITY.value,
            )
        except (KeyError, TypeError):
            self.carrying_capacity = self._create_carrying_capacity()

        try:
            self.encumbrance = Resource(
                base_value=base_stats[StatTypes.ENCUMBRANCE],
                name=StatTypes.ENCUMBRANCE.value,
            )
        except (KeyError, TypeError):
            self.encumbrance = self._create_encumbrance()

        try:
            self.hp_regen = CharacterStat(
                base_value=base_stats[StatTypes.HP_REGEN], name=StatTypes.HP_REGEN.value
            )
        except (KeyError, TypeError):
            self.hp_regen = self._create_health_regen()

        try:
            self.energy_regen = CharacterStat(
                base_value=base_stats[StatTypes.ENERGY_REGEN],
                name=StatTypes.ENERGY_REGEN.value,
            )
        except (KeyError, TypeError):
            self.energy_regen = self._create_energy_regen()

        try:
            self.mana_regen = CharacterStat(
                base_value=base_stats[StatTypes.MANA_REGEN],
                name=StatTypes.MANA_REGEN.value,
            )
        except (KeyError, TypeError):
            self.mana_regen = self._create_mana_regen()

        self.initiative = Initiative(self)
        self.damage_resists = ResistStats(damage_types=damage_resists, parent=self)
        self.damage_amps = DamageAmpStats(damage_types=damage_amps, parent=self)
        self.damage_masteries = MasteryStats(damage_types=damage_masteries, parent=self)

        self.naked_head_defense = self._create_naked_defense()
        self.naked_torso_defense = self._create_naked_defense()
        self.naked_legs_defense = self._create_naked_defense()
        self.naked_feet_defense = self._create_naked_defense()

        self.unarmed_attack = self._create_naked_attack()
        self.unarmed_damage = self._create_naked_damage()
        self.unarmed_init_cost = consts.MAX_INIT // 4
        self.unarmed_attack_range = None  # melee

    @property
    def attack(self) -> float:
        return self.unarmed_attack.value

    @property
    def damage(self) -> float:
        return self.unarmed_damage.value

    @property
    def init_cost(self) -> int:
        return self.unarmed_init_cost

    @property
    def attack_range(self) -> int | None:
        return self.attack_range

    @property
    def head_defense(self) -> float:
        item = self.parent.parent.equipment.slots.get(EquipmentTypes.HEAD)
        if item is None:
            return self.naked_head_defense.value
        item_defense = item.equippable.get_defense(self.parent.parent)
        if item_defense is None:
            return self.naked_head_defense.value
        return item_defense.value

    @property
    def torso_defense(self) -> float:
        item = self.parent.parent.equipment.slots.get(EquipmentTypes.TORSO)
        if item is None:
            return self.naked_torso_defense.value
        item_defense = item.equippable.get_defense(self.parent.parent)
        if item_defense is None:
            return self.naked_torso_defense.value
        return item_defense.value

    @property
    def legs_defense(self) -> float:
        item = self.parent.parent.equipment.slots.get(EquipmentTypes.LEGS)
        if item is None:
            return self.naked_legs_defense.value
        item_defense = item.equippable.get_defense(self.parent.parent)
        if item_defense is None:
            return self.naked_legs_defense.value
        return item_defense.value

    @property
    def feet_defense(self) -> float:
        item = self.parent.parent.equipment.slots.get(EquipmentTypes.FEET)
        if item is None:
            return self.naked_feet_defense.value
        item_defense = item.equippable.get_defense(self.parent.parent)
        if item_defense is None:
            return self.naked_feet_defense.value
        return item_defense.value

    @property
    def total_defense(self) -> float:
        return (
            self.head_defense
            + self.torso_defense
            + self.legs_defense
            + self.feet_defense
        )

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
    def get_stat(self, stat: Tuple[StatTypes, DamageTypes]) -> CappedStat: ...

    def get_stat(
        self, stat: StatTypes | Tuple[StatTypes, DamageTypes]
    ) -> CharacterStat | CappedStat:
        if isinstance(stat, StatTypes):
            stat_obj = getattr(self, stat.normalized)
            if isinstance(stat_obj, Resource):
                return stat_obj.max
            return stat_obj

        damage_stat_type, damage_type = stat
        return getattr(
            getattr(self, damage_stat_type.normalized),
            damage_type.normalized,
        )

    # ################# #
    # STAT CONSTRUCTORS #
    # ################# #

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
            StatModifier(
                value=_cc_str, mod_type=StatModType.PERCENT_MULT, source="BASE"
            )
        )

        carrying_capacity.minimize()

        return carrying_capacity

    def _create_encumbrance(self) -> Resource:
        # encumbrance (maximum weight of equipped items) is 50% of carrying capacity
        encumbrance = Resource(base_value=0, name=StatTypes.ENCUMBRANCE.value)

        _enc_cc = CharacterStat(
            base_value=self.carrying_capacity.max_value, name="BASE"
        )
        _enc_cc.add_modifier(
            StatModifier(value=0.5, mod_type=StatModType.PERCENT_MULT, source="BASE")
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
