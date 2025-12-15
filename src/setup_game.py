"""Handle the loading and initialization of game sessions."""

from __future__ import annotations

import copy
import lzma
import pickle
import traceback
from typing import Optional
from pathlib import Path

import tcod

import color
import consts
from engine import Engine
import entity_factories
from game_map import GameWorld
import input_handlers


def new_game() -> Engine:
    """Return a brand new game session as an Engine instance."""

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)

    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=consts.MAP_WIDTH,
        map_height=consts.MAP_HEIGHT,
    )

    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text.rgb
    )

    greathammer = copy.deepcopy(entity_factories.great_hammer)
    greathammer.parent = player.inventory
    player.inventory.items.append(greathammer)
    player.equipment.toggle_equip(greathammer, add_message=False)

    return engine


def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


def check_if_save_file_exists(filename: str) -> bool:
    return Path(filename).is_file()


class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the main menu on a background image."""

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "TOWER OF BABEL",
            fg=color.menu_title.rgb,
            alignment=tcod.libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By drsooz",
            fg=color.menu_title.rgb,
            alignment=tcod.libtcodpy.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            ["[N] Play a new game", "[C] Continue last game", "[X] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text.rgb,
                bg=color.black.rgb,
                alignment=tcod.libtcodpy.CENTER,
                bg_blend=tcod.libtcodpy.BKGND_ALPHA(64),
            )

    def _handle_key(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.KeySym.X, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        if event.sym == tcod.event.KeySym.C:
            try:
                return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()  # Print to stderr.
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.KeySym.N:
            if check_if_save_file_exists("savegame.sav"):
                return input_handlers.AreYouSureToDeleteSave(self)
            else:
                return input_handlers.MainGameEventHandler(new_game())

        return None
