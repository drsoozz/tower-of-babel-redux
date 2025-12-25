from base_enum import BaseEnum


class EquipmentTypes(str, BaseEnum):
    """Represents different types of equippable item slots on a character.

    These slots are used to assign gear to specific parts of a character's body
    or inventory layout. The enum values are also used for internal logic like
    validation, UI display, and inventory management.

    Combat Slots:
        MAIN_HAND: Slot for primary weapons.
        OFF_HAND: Slot for shields, secondary weapons, or focus items.

    Armor Slots:
        HEAD: Helmets, crowns, or hoods.
        FACE: Masks, visors, or eyewear.
        TORSO: Chest armor, robes, or vests.
        BACK: Capes, cloaks, wings, or quivers.
        ARMS: Armguards, bracers, or sleeves.
        WAIST: Belts or girdles.
        LEGS: Greaves, pants, or legplates.
        FEET: Boots, sabatons, or footwraps.

    Accessory Slots:
        NECKLACE: Amulets or necklaces.
        RING1, RING2: Finger rings (left/right or multiple).
        EARRING1, EARRING2: Ear accessories.
        ACCESSORY1-4: Flexible trinket slots for charms, talismans, relics, etc.
    """

    # weapon slots
    MAIN_HAND = "main-hand"
    OFF_HAND = "off-hand"

    # armor slots
    HEAD = "head"
    TORSO = "torso"
    LEGS = "legs"
    FEET = "feet"

    # clothing accessories
    FACE = "face"
    BACK = "back"
    ARMS = "arms"
    WAIST = "waist"

    NECKLACE = "necklace"

    # earrings
    EARRING_1 = "earring 1"
    EARRING_2 = "earring 2"

    # rings
    RING_1 = "ring 1"
    RING_2 = "ring 2"

    # accessories
    ACCESSORY_1 = "accessory 1"
    ACCESSORY_2 = "accessory 2"
    ACCESSORY_3 = "accessory 3"
    ACCESSORY_4 = "accessory 4"
    ESSENCE = "essence"
