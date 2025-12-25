from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []

    def add(self, item: Item, add_message: bool = True) -> None:
        """Adds an item to the inventory"""

        new_weight = item.weight + self.parent.fighter.stats.carrying_capacity.value
        if new_weight > self.parent.fighter.stats.carrying_capacity.max_value:
            self.engine.message_log.add_message(f"{item.name} is too heavy to pick up.")
            return

        if item in self.engine.game_map.entities:
            self.engine.game_map.entities.remove(item)
        item.parent = self
        self.items.append(item)
        self.parent.fighter.stats.carrying_capacity.modify(item.weight)

        if add_message:
            self.engine.message_log.add_message(f"You picked up the {item.name}!")

    def drop(self, item: Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map, at the player's current location.
        """
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)

        self.parent.fighter.stats.carrying_capacity.modify(-item.weight)

        self.engine.message_log.add_message(f"You dropped the {item.name}.")

    def delete(self, item: Item, message: str = None) -> None:
        """Deletes an item permanently."""
        self.items.remove(item)

        if message is not None:
            self.engine.message_log.add_message(message)
