from __future__ import annotations

from typing import Optional, TYPE_CHECKING, List, Tuple

from components.base_component import BaseComponent
from components.equipment_types import EquipmentTypes

if TYPE_CHECKING:
    from entity import Actor, Item


class Equipment(BaseComponent):
    """
    Component that manages an Actor's equipped items, supporting
    multi-slot items (e.g., two-handed weapons) and dual-wield logic.

    Attributes:
        slots (dict[EquipmentTypes, Optional[Item]]): Maps each equipment slot
            to the Item currently occupying it, or None if empty.

    Methods:
        item_is_equipped(item): Check if a specific item is currently equipped.
        occupied_slots(item): Return all slots an item occupies.
        find_slot_for_item(item): Determine which slot(s) an item should occupy,
            accounting for dual-wield rules for single-handed items.
        equip_to_slot(item, add_message): Equip an item in the appropriate slot(s),
            unequipping any conflicting items.
        unequip_from_slot(slot, add_message): Unequip the item from the given slot
            and all other slots it occupies.
        toggle_equip(item, add_message): Toggle equipping/unequipping an item.
    """

    parent: Actor

    def __init__(self):
        """
        Initialize all equipment slots to None.
        """
        self.slots: dict[EquipmentTypes, Optional[Item]] = {
            slot: None for slot in EquipmentTypes
        }

    @property
    def is_two_handing(self) -> bool:
        """
        Return True if the actor is currently two-handing a weapon.

        Two-handing is defined as the same item occupying both MAIN_HAND
        and OFF_HAND, and that item explicitly declaring both slots.
        """
        main = self.slots.get(EquipmentTypes.MAIN_HAND)
        off = self.slots.get(EquipmentTypes.OFF_HAND)

        if main is None or off is None:
            return False

        if main is not off:
            return False

        # Sanity check: item actually declares both slots
        occupied = self.occupied_slots(main)
        return (
            EquipmentTypes.MAIN_HAND in occupied and EquipmentTypes.OFF_HAND in occupied
        )

    @property
    def is_dual_wielding(self) -> bool:
        """
        Return True if the actor is dual-wielding.

        Dual-wielding is defined as MAIN_HAND and OFF_HAND both being occupied
        by different items, and neither item being two-handed.
        """
        main = self.slots.get(EquipmentTypes.MAIN_HAND)
        off = self.slots.get(EquipmentTypes.OFF_HAND)

        if main is None or off is None:
            return False

        if main is off:
            return False  # same item => two-handing, not dual-wielding

        main_slots = self.occupied_slots(main)
        off_slots = self.occupied_slots(off)

        return main_slots == (EquipmentTypes.MAIN_HAND,) and off_slots == (
            EquipmentTypes.OFF_HAND,
        )

    def item_is_equipped(self, item: Item) -> bool:
        """
        Check if a specific item is currently equipped in any slot.

        Args:
            item (Item): The item to check.

        Returns:
            bool: True if the item is equipped, False otherwise.
        """
        return item in self.slots.values()

    def unequip_message(self, item_name: str) -> None:
        """Send a message to the player indicating an item was removed."""
        self.parent.gamemap.engine.message_log.add_message(
            f"You remove the {item_name}."
        )

    def equip_message(self, item_name: str) -> None:
        """Send a message to the player indicating an item was equipped."""
        self.parent.gamemap.engine.message_log.add_message(
            f"You equip the {item_name}."
        )

    def occupied_slots(self, item: Item) -> Tuple[EquipmentTypes, ...]:
        """
        Return all slots this item occupies.

        The item's equippable component defines its intended slots via
        `equipment_type`, which can be a single EquipmentTypes or a tuple/list
        of multiple EquipmentTypes.

        Examples:
            - One-handed weapon: (EquipmentTypes.MAIN_HAND,)
            - Two-handed weapon: (EquipmentTypes.MAIN_HAND, EquipmentTypes.OFF_HAND)

        Args:
            item (Item): The item to query.

        Returns:
            Tuple[EquipmentTypes, ...]: All slots the item occupies.
        """
        if not item.equippable:
            return ()

        et = item.equippable.equipment_type
        if isinstance(et, EquipmentTypes):
            return (et,)
        if isinstance(et, (tuple, list)):
            return tuple(et)
        else:
            raise TypeError(f"Invalid equipment_type for {item}: {et}")

    def find_slot_for_item(self, item: Item) -> Tuple[EquipmentTypes, ...]:
        """
        Determine which slot(s) the item should occupy when equipped.

        Multi-slot items (e.g., two-handed weapons) always occupy all their declared
        slots. Single-slot items that normally go in MAIN_HAND may occupy OFF_HAND
        if MAIN_HAND is occupied (dual-wield logic).

        Args:
            item (Item): The item to equip.

        Returns:
            Tuple[EquipmentTypes, ...]: The actual slot(s) the item will occupy.
        """
        occupied = self.occupied_slots(item)

        # Multi-slot items always occupy their declared slots
        if len(occupied) > 1:
            return occupied

        # Single-slot item logic
        slot = occupied[0]
        if slot == EquipmentTypes.MAIN_HAND:
            # Prefer MAIN_HAND if free, else use OFF_HAND if available
            if self.slots[EquipmentTypes.MAIN_HAND] is None:
                return (EquipmentTypes.MAIN_HAND,)
            elif self.slots[EquipmentTypes.OFF_HAND] is None:
                return (EquipmentTypes.OFF_HAND,)
        return occupied

    def equip_to_slot(self, item: Item, add_message: bool = True) -> None:
        """
        Equip an item to its determined slot(s), unequipping any conflicting items.

        Args:
            item (Item): The item to equip.
            add_message (bool): Whether to show a message to the player.
        """
        # Trigger any on-equip logic
        item.equippable.equip(self.parent)

        slots_needed = self.find_slot_for_item(item)

        # Unequip anything occupying the slots needed
        for slot in slots_needed:
            if self.slots.get(slot) is not None:
                self.unequip_from_slot(slot, add_message)

        # Assign the item to all its slots
        for slot in slots_needed:
            self.slots[slot] = item

        if add_message:
            self.equip_message(item.name)

    def unequip_from_slot(self, slot: EquipmentTypes, add_message: bool = True) -> None:
        """
        Unequip the item from the specified slot and all other slots it occupies.

        Args:
            slot (EquipmentTypes): The slot to unequip.
            add_message (bool): Whether to show a message to the player.
        """
        current_item = self.slots.get(slot)
        if current_item is None:
            return

        # Trigger any on-unequip logic
        current_item.equippable.unequip(self.parent)

        # Remove the item from all slots it occupies
        for occupied in self.occupied_slots(current_item):
            self.slots[occupied] = None

        if add_message:
            self.unequip_message(current_item.name)

    def toggle_equip(self, equippable_item: Item, add_message: bool = True) -> None:
        """
        Equip or unequip the given item depending on whether it is already equipped.

        Uses dual-wield logic to determine the correct slot(s) for single-handed items.

        Args:
            equippable_item (Item): The item to toggle.
            add_message (bool): Whether to show messages to the player.
        """
        if not equippable_item.equippable:
            return

        slots_needed = self.find_slot_for_item(equippable_item)

        # If the item is already equipped in all required slots, unequip it
        if all(self.slots.get(slot) == equippable_item for slot in slots_needed):
            for slot in slots_needed:
                self.unequip_from_slot(slot, add_message)
        else:
            # Otherwise, equip it in the determined slot(s)
            self.equip_to_slot(equippable_item, add_message)
