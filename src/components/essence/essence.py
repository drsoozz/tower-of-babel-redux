from __future__ import annotations

from typing import Optional, TYPE_CHECKING, List, Tuple

from components.base_component import BaseComponent
from components.equipment_types import EquipmentTypes
from components.items.equippable import EssenceEquippable

if TYPE_CHECKING:
    from entity import Actor, Item


class Essence(BaseComponent):
    """
    For handling essences
    """

    parent: Actor

    def __init__(self):
        self.slots: List[Optional[Item]]

    def init_hook(self) -> None:
        current_level = self.parent.level.current_level
        self.slots = [None] * current_level

    def on_level_up(self) -> None:
        self.slots.append(None)

    def equip(self, item: Item, add_message: bool = True) -> bool:
        # find if the player already has this type of essence equipped
        # (multiple copies of the same essence cannot be equipped)
        for i, slot in enumerate(self.slots):
            if slot == item:
                if add_message:
                    self.already_type_equipped(item.name)
                return False

        for i, slot in enumerate(self.slots):
            if slot is None:
                self.slots[i] = item
                item.equippable.equip(self.parent)

                if add_message:
                    self.equip_message(item.name)
                return True
        if add_message:
            self.all_slots_full(item.name)

    def unequip(self, item: Item, add_message: bool = True) -> None:
        for i, slot in enumerate(self.slots):
            if slot == item:
                item.equippable.unequip(self.parent)
                self.slots[i] = None
                if add_message:
                    self.unequip_message(item.name)

    def equip_message(self, item_name: str) -> None:
        """Send a message to the player indicating an item was equipped."""
        self.parent.gamemap.engine.message_log.add_message(
            f"You infuse yourself with the {item_name}."
        )

    def all_slots_full(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You were unable to equip {item_name} as you do not have a free essence slot."
        )

    def unequip_message(self, item_name: str) -> None:
        """Send a message to the player indicating an item was removed."""
        self.parent.gamemap.engine.message_log.add_message(
            f"The {item_name} is destroyed."
        )

    def already_type_equipped(self, item_name: str) -> None:
        """send a message to the player indicating that this type of essence
        is already equipped (essences are unique)"""
        self.parent.gamemap.engine.message_log.add_message(
            f"You already have {item_name} equipped (you cannot equip the same essence more than once)."
        )
