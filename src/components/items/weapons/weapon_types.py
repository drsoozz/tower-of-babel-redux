from dataclasses import dataclass
from pathlib import Path

import consts
from base_enum import BaseEnum


class WeaponTypes(str, BaseEnum):
    """
    Enum for all weapon types
    """

    # 25 init
    DAGGER = "dagger"
    SHORTSWORD = "shortsword"
    HANDAXE = "handaxe"

    # 50 init
    SWORD = "sword"
    MACE = "mace"
    SCIMITAR = "scimitar"
    RAPIER = "rapier"
    PARTIZAN = "partizan"

    # 75 init
    LONGSWORD = "longsword"
    WARHAMMER = "warhammer"
    CLUB = "club"
    AXE = "axe"
    SPEAR = "spear"
    SCYTHE = "scythe"
    GLAIVE = "glaive"

    # 100 init
    GREATSWORD = "greatsword"
    GREATCLUB = "greatclub"
    MAUL = "maul"
    GREATAXE = "greataxe"
    GREATSPEAR = "greatspear"
    HALBERD = "halberd"
    POLEAXE = "poleaxe"
    WARSCYTHE = "warscythe"

    # 125 init
    GREATHAMMER = "greathammer"
    GREATSCYTHE = "greatscythe"


class WeaponTags(str, BaseEnum):
    DAGGER = "dagger"
    SWORD = "sword"
    AXE = "axe"
    BLUNT = "blunt"
    POLEARM = "polearm"
    SCYTHE = "scythe"
    ONE_HANDED = "one-handed"
    TWO_HANDED = "two-handed"


@dataclass(frozen=True)
class WeaponDefinition:
    path: Path
    tags: set[WeaponTags]


DEFAULT_WEAPON_PATH = (
    consts.BASE_PATH
    / Path("components")
    / Path("items")
    / Path("weapons")
    / Path("defaults")
)

WEAPONS: dict[WeaponTypes, WeaponDefinition] = {
    WeaponTypes.AXE: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "axe.json",
        tags={WeaponTags.AXE, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.CLUB: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "club.json",
        tags={WeaponTags.BLUNT, WeaponTags.ONE_HANDED},
    ),
    WeaponTypes.DAGGER: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "dagger.json",
        tags={WeaponTags.DAGGER, WeaponTags.ONE_HANDED},
    ),
    WeaponTypes.GLAIVE: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "glaive.json",
        tags={WeaponTags.POLEARM, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.GREATAXE: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "greataxe.json",
        tags={WeaponTags.AXE, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.GREATHAMMER: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "greathammer.json",
        tags={WeaponTags.BLUNT, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.GREATSCYTHE: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "greatscythe.json",
        tags={WeaponTags.SCYTHE, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.GREATSPEAR: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "greatspear.json",
        tags={WeaponTags.POLEARM, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.GREATSWORD: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "greatsword.json",
        tags={WeaponTags.SWORD, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.HALBERD: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "halberd.json",
        tags={WeaponTags.POLEARM, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.HANDAXE: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "handaxe.json",
        tags={WeaponTags.AXE, WeaponTags.ONE_HANDED},
    ),
    WeaponTypes.LONGSWORD: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "longsword.json",
        tags={WeaponTags.SWORD, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.MACE: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "mace.json",
        tags={WeaponTags.BLUNT, WeaponTags.ONE_HANDED},
    ),
    WeaponTypes.MAUL: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "maul.json",
        tags={WeaponTags.BLUNT, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.PARTIZAN: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "partizan.json",
        tags={WeaponTags.POLEARM, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.POLEAXE: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "poleaxe.json",
        tags={WeaponTags.POLEARM, WeaponTags.AXE, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.RAPIER: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "rapier.json",
        tags={WeaponTags.SWORD, WeaponTags.ONE_HANDED},
    ),
    WeaponTypes.SCYTHE: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "scythe.json",
        tags={WeaponTags.SCYTHE, WeaponTags.TWO_HANDED},
    ),
    WeaponTypes.SHORTSWORD: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "shortsword.json",
        tags={WeaponTags.DAGGER, WeaponTags.SWORD, WeaponTags.ONE_HANDED},
    ),
    WeaponTypes.SPEAR: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "spear.json",
        tags={WeaponTags.POLEARM, WeaponTags.ONE_HANDED},
    ),
    WeaponTypes.SWORD: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "sword.json",
        tags={WeaponTags.SWORD, WeaponTags.ONE_HANDED},
    ),
    WeaponTypes.WARHAMMER: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "warhammer.json",
        tags={WeaponTags.BLUNT, WeaponTags.ONE_HANDED},
    ),
    WeaponTypes.WARSCYTHE: WeaponDefinition(
        path=DEFAULT_WEAPON_PATH / "warscythe.json",
        tags={WeaponTags.SCYTHE, WeaponTags.TWO_HANDED},
    ),
}
