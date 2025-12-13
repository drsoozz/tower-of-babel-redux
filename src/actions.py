from __future__ import annotations

import time
from typing import Optional, Tuple, TYPE_CHECKING
import random

import color
import consts
from combat_types import CombatTypes
import exceptions
from components.stats.damage_types import DamageTypes
from render_functions import round_for_display


if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


class Action:
    def __init__(self, entity: Actor) -> None:
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()

    def apply_cost(self, cost: int | float = 0) -> None:
        self.entity.fighter.stats.initiative.initiative.modify(
            amount=-int(cost), sudo=True
        )


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                self.apply_cost()
                return

        raise exceptions.Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(
        self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        if self.item.consumable:
            self.item.consumable.activate(self)
            self.apply_cost()


class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)
        self.entity.inventory.drop(self.item)
        self.apply_cost()


class EquipAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)
        self.apply_cost()


class WaitAction(Action):
    def perform(
        self,
        from_error: bool = False,
        looped_wait: bool = False,
        time_to_wait: int = consts.MAX_INIT // 2,
    ) -> None:
        if looped_wait:
            pass
        elif self.entity == self.engine.player:
            time.sleep(0.05)

        if from_error:
            self.apply_cost(consts.MAX_INIT // 5)
        else:
            self.apply_cost(time_to_wait)


class QueryWaitAction(WaitAction):
    def perform(self, from_error=False, looped_wait=True):
        super().perform(from_error, looped_wait)


class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.upstairs_location:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                "You ascend the staircase.", color.ascend.rgb
            )
            self.apply_cost()
        else:
            raise exceptions.Impossible("There are no stairs here.")


class ActionWithDirection(Action):

    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class AttackAction(Action):
    def __init__(self, attacker: Actor, defender: Actor):
        super().__init__(attacker)
        self.attacker = attacker
        self.defender = defender

    def perform(self) -> None:
        self.engine.message_log.add_blank()

        # attack rating (higher means more likely to hit)
        attack = self.attacker.fighter.stats.attack

        # defense rating (higher means less likely to hit)
        defense = self.defender.fighter.stats.total_defense

        chance = 0.5 + (attack - defense) * 0.025

        attack_desc = f"{self.attacker.name.capitalize()} attacks {self.defender.name.capitalize()}."
        self.engine.message_log.add_message(attack_desc)

        roll = random.random()
        if roll < max(0.05, chance):
            # how much raw damage will be given if it is successful
            damage = self.attacker.fighter.stats.damage.apply_boosts(self.attacker)

            # amount of damage actually received (between 0 and 1)
            final_damage = self.attacker.fighter.stats.damage.apply_resistances(
                scaled_damage=damage, defender=self.defender
            )

            summed_damage = self.attacker.fighter.stats.damage.sum_damage_dict(
                final_damage
            )

            print(self.attacker.name, self.attacker.fighter.stats.attack_init_cost)

            if summed_damage > 0:
                for damtype, damval in final_damage.items():
                    damtype: DamageTypes
                    self.engine.message_log.add_message(
                        f"The attack does {round_for_display(damval)} {damtype.value.upper()} damage."
                    )
                    self.defender.fighter.hp -= damval
            else:
                self.engine.message_log.add_message("The attack does no damage.")

            # print(attack, defense, chance, roll, damage, resist, final_damage)
        else:
            self.engine.message_log.add_message("The attack missed!")
        self.apply_cost(
            self.attacker.fighter.stats.attack_init_cost
        )  # already accounts for speed multipliers


class MeleeAction(ActionWithDirection):

    # TODO: eventually redo this when adding more than just base stats

    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        AttackAction(attacker=self.entity, defender=target).perform()


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            raise exceptions.Impossible("That way is blocked.")

        self.entity.move(self.dx, self.dy)
        if self.entity == self.engine.player:
            time.sleep(0.001)
        self.apply_cost(5e5 * self.entity.fighter.stats.initiative.movement_multiplier)


class BumpAction(ActionWithDirection):

    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        return MovementAction(self.entity, self.dx, self.dy).perform()
