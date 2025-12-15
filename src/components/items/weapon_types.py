from base_enum import BaseEnum


class WeaponTypes(str, BaseEnum):
    """
    Enum for all weapon types
    """

    # 25 init
    DAGGER = "Dagger"
    SHORTSWORD = "Shortsword"

    # 50 init
    SWORD = "Sword"
    MACE = "MACE"
    HANDAXE = "HANDAXE"
    SCIMITAR = "Scimitar"
    RAPIER = "Rapier"
    PARTIZAN = "Partizan"

    # 75 init
    LONGSWORD = "Longsword"
    WARHAMMER = "Warhammer"
    CLUB = "CLUB"
    AXE = "AXE"
    SPEAR = "SPEAR"
    SCYTHE = "SCYTHE"
    GLAIVE = "Glaive"

    # 100 init
    GREATSWORD = "Greatsword"
    GREATCLUB = "Greatclub"
    MAUL = "Maul"
    GREATAXE = "Greataxe"
    GREATSPEAR = "Greatspear"
    HALBERD = "Halberd"
    POLEAXE = "Poleaxe"
    WARSCYTHE = "Warscythe"

    # 125 init
    GREATHAMMER = "Greathammer"
    GREATSCYTHE = "Greatscythe"


class WeaponTags(str, BaseEnum):
    DAGGER = "Dagger"
    SWORD = "Sword"
    AXE = "Axe"
    BLUNT = "Blunt"
    POLEARM = "Polearm"
    SCYTHE = "Scythe"
    ONE_HANDED = "One-Handed"
    TWO_HANDED = "Two-Handed"


WEAPON_TYPE_TO_GROUPS: dict[WeaponTypes, set[WeaponTags]] = {
    WeaponTypes.AXE: {WeaponTags.AXE, WeaponTags.TWO_HANDED},
    WeaponTypes.CLUB: {WeaponTags.BLUNT, WeaponTags.ONE_HANDED},
    WeaponTypes.DAGGER: {WeaponTags.DAGGER, WeaponTags.ONE_HANDED},
    WeaponTypes.GLAIVE: {WeaponTags.POLEARM, WeaponTags.TWO_HANDED},
    WeaponTypes.GREATAXE: {WeaponTags.AXE, WeaponTags.TWO_HANDED},
    WeaponTypes.GREATHAMMER: {WeaponTags.BLUNT, WeaponTags.TWO_HANDED},
    WeaponTypes.GREATSCYTHE: {WeaponTags.SCYTHE, WeaponTags.TWO_HANDED},
    WeaponTypes.GREATSPEAR: {WeaponTags.POLEARM, WeaponTags.TWO_HANDED},
    WeaponTypes.GREATSWORD: {WeaponTags.SWORD, WeaponTags.TWO_HANDED},
    WeaponTypes.HALBERD: {WeaponTags.POLEARM, WeaponTags.TWO_HANDED},
    WeaponTypes.HANDAXE: {WeaponTags.AXE, WeaponTags.ONE_HANDED},
    WeaponTypes.LONGSWORD: {WeaponTags.SWORD, WeaponTags.TWO_HANDED},
    WeaponTypes.MACE: {WeaponTags.BLUNT, WeaponTags.ONE_HANDED},
    WeaponTypes.MAUL: {WeaponTags.BLUNT, WeaponTags.TWO_HANDED},
    WeaponTypes.PARTIZAN: {WeaponTags.POLEARM, WeaponTags.TWO_HANDED},
    WeaponTypes.POLEAXE: {
        WeaponTags.POLEARM,
        WeaponTags.AXE,
        WeaponTags.TWO_HANDED,
    },
    WeaponTypes.RAPIER: {WeaponTags.SWORD, WeaponTags.ONE_HANDED},
    WeaponTypes.SCYTHE: {WeaponTags.SCYTHE, WeaponTags.TWO_HANDED},
    WeaponTypes.SHORTSWORD: {
        WeaponTags.DAGGER,
        WeaponTags.SWORD,
        WeaponTags.ONE_HANDED,
    },
    WeaponTypes.SPEAR: {WeaponTags.POLEARM, WeaponTags.ONE_HANDED},
    WeaponTypes.SWORD: {WeaponTags.SWORD, WeaponTags.ONE_HANDED},
    WeaponTypes.WARHAMMER: {WeaponTags.BLUNT, WeaponTags.ONE_HANDED},
    WeaponTypes.WARSCYTHE: {WeaponTags.SCYTHE, WeaponTags.TWO_HANDED},
}
