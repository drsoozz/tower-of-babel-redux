from __future__ import annotations

import lzma
import pickle
from typing import TYPE_CHECKING, Iterator, List
from functools import cached_property

from tcod.console import Console
from tcod.map import compute_fov

from actions import WaitAction
import color
import consts
import exceptions
from message_log import MessageLog
import render_functions

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap, GameWorld
    from entity import Entity


class Engine:
    game_map: GameMap
    game_world: GameWorld

    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player

    def handle_enemy_turns(self) -> Iterator[Entity]:
        while True:
            yield None

            if not self.player.is_alive:
                return

            sorted_entities = self.game_map.sorted_actors_by_initiative
            if len(sorted_entities) == 0:
                return
            min_diff = (
                consts.MAX_INIT
                - sorted_entities[0].fighter.stats.initiative.initiative.value
            )
            list_of_diffs = [
                consts.MAX_INIT - actor.fighter.stats.initiative.initiative.value
                for actor in sorted_entities
            ]
            # if the smallest difference is larger than zero, than regenerate everyone
            # regenerate() increases the init by min_diff and regens hp, energy, and mana, as according
            # to the actor's respective regen values

            if min_diff > 0:
                for entity in sorted_entities:
                    entity.fighter.stats.regenerate(min_diff)

            # consequently, sorted_entities[0] is now at max initiative (can take its turn)

            # if the max initiative actor, who was also the very top of the order
            # (order was not changed), is the player, then skip all of this
            # as it isn't the enemys' turns yet, it's the player's turn!
            if sorted_entities[0] == self.player:
                return

            # make a list of all entities that have max init (or more) and are before the player
            turn_order = []
            for entity in sorted_entities:
                if entity == self.player:
                    break
                if (
                    entity.fighter.stats.initiative.initiative.value + max(0, min_diff)
                    >= consts.MAX_INIT
                ):
                    turn_order.append(entity)
            print(sorted_entities[0].name)

            if not turn_order:
                # No enemy reached max, but player wasn’t the top either
                # This should consume time, not skip the enemy turn phase.
                yield None
                return

            # iterate the normal hnadle_enemy_turns over that list
            yield from self._handle_enemy_turns(turn_order=turn_order)

    def _handle_enemy_turns(self, turn_order: List[Actor]) -> Iterator[Entity]:

        for entity in turn_order:
            if entity.ai:
                try:
                    entity.ai.perform()
                except (
                    exceptions.Impossible
                ):  # Ignore impossible action exceptions from AI.
                    WaitAction(entity).perform()
                    print("!")
                yield entity

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
            light_walls=True,
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        self.game_map.render(console)

        render_functions.render_gui_frame(console=console, y=(self.game_map.height + 1))

        self.message_log.render(
            console=console,
            x=self.game_map.width - 40,
            y=self.ui_start_y,
            width=40,
            height=self.ui_height,
        )

        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.stats.hp.value,
            maximum_value=self.player.fighter.stats.hp.max_value,
            x=1,
            y=(self.ui_start_y),
            bar_empty=color.bar_hp_empty,
            bar_filled=color.bar_hp,
            bar_text=color.bar_hp_text,
            bar_title="HP: ",
        )

        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.stats.energy.value,
            maximum_value=self.player.fighter.stats.energy.max_value,
            x=1,
            y=(self.ui_start_y + 1),
            bar_empty=color.bar_energy_empty,
            bar_filled=color.bar_energy,
            bar_text=color.bar_energy_text,
            bar_title="EGY:",
        )

        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.stats.mana.value,
            maximum_value=self.player.fighter.stats.mana.max_value,
            x=1,
            y=(self.ui_start_y + 2),
            bar_empty=color.bar_mana_empty,
            bar_filled=color.bar_mana,
            bar_text=color.bar_mana_text,
            bar_title="MNA:",
        )

        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.stats.initiative.initiative.value
            / consts.TRUE_INIT_FACTOR,
            maximum_value=consts.MAX_INIT / consts.TRUE_INIT_FACTOR,
            x=1,
            y=(self.ui_start_y + 3),
            bar_empty=color.bar_initiative_empty,
            bar_filled=color.bar_initiative,
            bar_text=color.bar_initiative_text,
            bar_title="INI:",
        )

        render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            x=self.game_map.width - 47,
            y=self.ui_start_y,
        )

        render_functions.render_names_at_mouse_location(
            console=console,
            x=self.game_map.width - 40,
            y=self.game_map.height + 2,
            engine=self,
        )

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)

    @cached_property
    def ui_start_y(self) -> int:
        return self.game_map.height + 2

    @cached_property
    def ui_end_y(self) -> int:
        return consts.SCREEN_HEIGHT

    @cached_property
    def ui_height(self) -> int:
        return self.ui_end_y - self.ui_start_y
