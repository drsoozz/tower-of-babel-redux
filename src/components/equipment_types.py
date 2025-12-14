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

    MAIN_HAND = "Main-hand"
    OFF_HAND = "Off-hand"
    HEAD = "Head"
    FACE = "Face"
    TORSO = "Torso"
    BACK = "Back"
    ARMS = "Arms"
    WAIST = "Waist"
    LEGS = "Legs"
    FEET = "Feet"
    NECKLACE = "Necklace"
    RING_1 = "Ring 1"
    RING_2 = "Ring 2"
    EARRING_1 = "Earring 1"
    EARRING_2 = "Earring 2"
    ACCESSORY_1 = "Accessory 1"
    ACCESSORY_2 = "Accessory 2"
    ACCESSORY_3 = "Accessory 3"
    ACCESSORY_4 = "Accessory 4"
