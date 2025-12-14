from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from components.stats.stat_modifier import StatModifier
from components.stats.stat_mod_types import StatModType
from components.stats.character_stat import CharacterStat

if TYPE_CHECKING:
    from entity import Actor
    from components.stats.stat_types import StatTypes


def build_composite_stat(
    *,
    actor: Actor,
    base_value: float | int = 0,
    name: str,
    stat_mods: Dict[StatTypes, StatModifier | List[StatModifier]],
    source: object,
) -> CharacterStat:
    """
    Build a composite CharacterStat from per-stat modifiers.

    For each StatType:
        - Pull the actor's stat
        - Apply modifiers to a derived CharacterStat
        - Fold the result into a single aggregate CharacterStat

    This is used for armor defense, derived scaling stats, etc.
    """
    composite = CharacterStat(base_value=base_value, name=name)
    stats = actor.fighter.stats

    for stat_type, modifiers in stat_mods.items():
        if not isinstance(modifiers, list):
            modifiers = [modifiers]

        base_stat = stats.get_stat(stat_type)
        derived = CharacterStat(base_value=base_stat, name=name)

        for mod in modifiers:
            derived.add_modifier(mod)

        composite.add_modifier(
            StatModifier(
                value=derived,
                mod_type=StatModType.FLAT,
                source=source,
            )
        )

    return composite
