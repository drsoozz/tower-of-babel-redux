from __future__ import annotations

from pathlib import Path

from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union, Dict, List
import math

import tcod

import actions
from actions import Action, BumpAction, PickupAction, WaitAction
import color
import consts
import menu_text
from menu_text import StatDescriptor, StatRow, InventoryRow
import exceptions
from entity import Item
from components.stats.stat_types import StatTypes
from components.stats.damage_types import DamageTypes
from components.stats.stat_mod_types import StatModType
from render_functions import round_for_display
import render_functions
from components.stats import combat_stat_types
from components.stats.resource import Resource
from components.equipment_types import EquipmentTypes
from components.items.equippable import WeaponEquippable, ArmorEquippable, Equippable
from components.stats.stat_modifier import StatModifier
from components.wallet.currencies import Currency

if TYPE_CHECKING:
    from engine import Engine
    from components.stats.character_stat import CharacterStat
MOVE_KEYS = {
    # Arrow keys.
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
    # Vi keys.
    tcod.event.KeySym.A: (-1, 0),
    tcod.event.KeySym.X: (0, 1),
    tcod.event.KeySym.W: (0, -1),
    tcod.event.KeySym.D: (1, 0),
    tcod.event.KeySym.Q: (-1, -1),
    tcod.event.KeySym.E: (1, -1),
    tcod.event.KeySym.Z: (-1, 1),
    tcod.event.KeySym.C: (1, 1),
}

WAIT_KEYS = {
    tcod.event.KeySym.PERIOD,
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.CLEAR,
    tcod.event.KeySym.S,
}

CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10,
}

CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN,
    tcod.event.KeySym.KP_ENTER,
}

TILE_WIDTH = 12
TILE_HEIGHT = 12

ActionOrHandler = Union[Action, "BaseEventHandler"]
"""An event handler return value which can trigger an action or switch active handlers.

If a handler is returned then it will become the active handler for future events.
If an action is returned it will be attempted and if it's valid then
MainGameEventHandler will become the active handler.
"""


class BaseEventHandler:

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.handle_event(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."
        return self

    def handle_event(self, event: tcod.event.Event) -> Optional[Action]:
        if isinstance(event, tcod.event.Quit):
            self._handle_quit()
        if isinstance(event, tcod.event.KeyDown):
            return self._handle_key(event)
        return None

    def _handle_quit(self) -> Optional[Action]:
        raise SystemExit()

    def _handle_key(self, event: tcod.event.KeyDown) -> Optional[Action]:
        raise NotImplementedError()

    def on_render(self, console: tcod.Console) -> None:
        raise NotImplementedError()


class PopupMessage(BaseEventHandler):
    """Display a popup text window."""

    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the parent and dim the result, then print the message on top."""
        self.parent.on_render(console)
        console.rgb["fg"] //= 8
        console.rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment=tcod.CENTER,
        )

    def _handle_key(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
        """Any key returns to the parent handler."""
        return self.parent


class AreYouSureToDeleteSave(PopupMessage):
    def __init__(self, parent_handler):
        super().__init__(parent_handler, text="")

    def on_render(self, console):
        self.parent.on_render(console)
        console.rgb["fg"] //= 8
        console.rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "Are you sure you want to delete your save?",
            fg=color.white,
            bg=color.black,
            alignment=tcod.libtcodpy.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(["[Y] Yes", "[N] No"]):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=tcod.libtcodpy.CENTER,
                bg_blend=tcod.libtcodpy.BKGND_ALPHA(64),
            )

    def _handle_key(self, event: tcod.event.KeyDown):
        key = event.sym
        from setup_game import new_game

        if key == tcod.event.KeySym.Y:
            return MainGameEventHandler(new_game())
        if key == tcod.event.KeySym.N:
            return self.parent
        return None


class EventHandler(BaseEventHandler):
    """Base interface for input handlers."""

    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(
        self, event: tcod.event.Event, console: tcod.console.Console = None
    ) -> None:
        """Handle events for input handlers with an engine."""
        action_or_state = self.handle_event(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state, console):
            # A valid action was performed.
            if not self.engine.player.is_alive:
                # The player was killed sometime during or after the action.
                return GameOverEventHandler(self.engine)
            if self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)
            return MainGameEventHandler(self.engine)  # Return to the main handler.
        return self

    def handle_action(
        self, action: Optional[Action], console: tcod.console.Console = None
    ) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn.
        """
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False  # Skip enemy turn on exceptions.
        for _ in self.engine.handle_enemy_turns():
            self.engine.update_fov()
            if console:
                self.on_render(console)
        self.engine.update_fov()
        if console:
            self.on_render(console)
        return True

    def _handle_key(self, event: tcod.event.KeyDown) -> Optional[Action]:
        raise NotImplementedError()

    def on_render(self, console: tcod.console.Console) -> None:
        self.engine.render(console)


class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""

    def __init__(
        self,
        engine,
        frame_width: Optional[int],
        frame_height: Optional[int],
        title: str = None,
        question: str = None,
    ):
        super().__init__(engine)

        self.TITLE = title
        self.QUESTION = question

        if frame_width is None:
            if question is None:
                self.frame_width = 15
            else:
                self.frame_width = len(question) + 4
        else:
            self.frame_width = frame_width

        if frame_height is None:
            self.frame_height = consts.SCREEN_HEIGHT // 2
        else:
            self.frame_height = frame_height

        self.x = (consts.SCREEN_WIDTH - self.frame_width) // 2
        self.y = (consts.SCREEN_HEIGHT - self.frame_height) // 2
        if not isinstance(self.TITLE, str):
            self.title_x = self.x + self.frame_width // 2
        else:
            self.title_x = self.x + self.frame_width // 2 - len(self.TITLE) // 2
        self.text_x = self.x + 2
        self.text_y = self.y + 2

    def _handle_key(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """By default any key exits this input handler."""
        key = event.sym
        if key == tcod.event.KeySym.ESCAPE:
            return self.on_exit()
        return None

    def on_exit(self) -> Optional[ActionOrHandler]:
        """Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        return MainGameEventHandler(self.engine)


class EscapeMenuEventHandler(AskUserEventHandler):
    def __init__(self, engine: Engine):
        TITLE = "MAIN MENU"

        super().__init__(
            engine, frame_width=None, frame_height=None, title=TITLE, question=None
        )

        self.x = 0
        self.y = 0
        self.frame_width = consts.SCREEN_WIDTH
        self.frame_height = consts.SCREEN_HEIGHT
        self.title_x = self.x + self.frame_width // 2 - len(self.TITLE) // 2
        self.title_y = 2
        self.text_x = self.title_x
        self.text_y = self.title_y + 10
        self.menu_width = 24

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        console.draw_frame(
            x=self.x,
            y=self.y,
            width=self.frame_width,
            height=self.frame_height,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )
        console.print(self.title_x, self.y, self.TITLE)

        for i, text in enumerate(["[ESC] Return to game", "[X] Quit to Main Menu"]):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(self.menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=tcod.libtcodpy.CENTER,
                bg_blend=tcod.libtcodpy.BKGND_ALPHA(64),
            )

    def _handle_key(self, event):
        key = event.sym
        if key == tcod.event.KeySym.X:
            raise exceptions.QuitToMainMenu()
        if key == tcod.event.KeySym.ESCAPE:
            return MainGameEventHandler(self.engine)
        return None


class CharacterScreenEventHandler(AskUserEventHandler):

    def __init__(self, engine):
        TITLE = "CHARACTER INFORMATION"
        QUESTION = ""
        frame_width = 50
        frame_height = 25

        super().__init__(
            engine,
            frame_width=frame_width,
            frame_height=frame_height,
            title=TITLE,
            question=QUESTION,
        )

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        console.draw_frame(
            x=self.x,
            y=self.y,
            width=self.frame_width,
            height=self.frame_height,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(self.title_x, self.y, self.TITLE)

        console.print(
            x=self.text_x,
            y=self.text_y,
            text=f"Level: {self.engine.player.level.current_level}",
        )
        console.print(
            x=self.text_x,
            y=self.text_y + 1,
            text=f"XP: {self.engine.player.level.current_xp} / {self.engine.player.level.experience_to_next_level}",
        )

        console.print(
            x=self.text_x,
            y=self.text_y + 3,
            text=f"Strength: {round_for_display(self.engine.player.fighter.stats.strength.value)}",
        )
        console.print(
            x=self.text_x,
            y=self.text_y + 4,
            text=f"Dexterity: {round_for_display(self.engine.player.fighter.stats.dexterity.value)}",
        )
        console.print(
            x=self.text_x,
            y=self.text_y + 5,
            text=f"Constitution: {round_for_display(self.engine.player.fighter.stats.constitution.value)}",
        )
        console.print(
            x=self.text_x,
            y=self.text_y + 6,
            text=f"Intelligence: {round_for_display(self.engine.player.fighter.stats.intelligence.value)}",
        )
        console.print(
            x=self.text_x,
            y=self.text_y + 7,
            text=f"Cunning: {round_for_display(self.engine.player.fighter.stats.cunning.value)}",
        )
        console.print(
            x=self.text_x,
            y=self.text_y + 8,
            text=f"Willpower: {round_for_display(self.engine.player.fighter.stats.willpower.value)}",
        )


class LoopHandler(EventHandler):
    def __init__(self, engine, remaining_time: int, until_full: bool = False):
        super().__init__(engine)
        self.remaining_time = remaining_time
        self.until_full = until_full

        self.quick = True
        # possibly change this to checking if there are any actors within a 10 tile radius?
        # could help with bugs with AI and the quick features lol
        for actor in self.engine.game_map.actors:
            if (
                self.engine.game_map.visible[actor.x, actor.y]
                and actor.is_alive
                and actor != self.engine.player
            ):
                self.quick = False

    def tick(self, console: tcod.console.Console):
        if self.until_full:
            if (
                self.engine.player.fighter.stats.hp.value
                == self.engine.player.fighter.stats.hp.max_value
            ):
                return MainGameEventHandler(self.engine)
        if (
            self.remaining_time is not None and self.remaining_time <= 0
        ) or not self.engine.player.is_alive:
            return MainGameEventHandler(self.engine)

        time_spent = self.perform(quick=self.quick)
        if self.remaining_time is not None:
            self.remaining_time -= time_spent

        if self.quick:
            self.engine.only_handle_player()
        else:
            for _ in self.engine.handle_enemy_turns():
                self.on_render(console)
                self.engine.update_fov()
        self.on_render(console)
        self.engine.update_fov()

        return self

    def perform(self, quick: bool = False):
        raise NotImplementedError()


class LoopedRestHandler(LoopHandler):
    def perform(self, quick: bool = False):

        if quick:
            time_spent = consts.MAX_INIT * 25
        else:
            time_spent = consts.MAX_INIT

        WaitAction(self.engine.player).perform(
            looped_wait=True, time_to_wait=time_spent
        )
        return time_spent

    def _handle_key(self, event):
        key = event.sym
        if key == tcod.event.KeySym.ESCAPE:
            return MainGameEventHandler(self.engine)
        return None


class QueryRestLoopHandler(AskUserEventHandler):

    def __init__(self, engine):
        TITLE = "ADVANCED REST OPTIONS"
        QUESTION = "How long do you want to rest?"
        frame_height = 25
        super().__init__(
            engine,
            frame_width=None,  # default
            frame_height=frame_height,
            title=TITLE,
            question=QUESTION,
        )

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        console.draw_frame(
            x=self.x,
            y=self.y,
            width=self.frame_width,
            height=self.frame_height,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )
        console.print(self.title_x, self.y, self.TITLE)

        console.print(self.x + 2, self.y + 2, text=self.QUESTION)
        console.print(self.x + 2, self.y + 4, text="1) 100 Turns")
        console.print(self.x + 2, self.y + 5, text="2) 500 Turns")
        console.print(self.x + 2, self.y + 6, text="3) 1000 Turns")
        console.print(self.x + 2, self.y + 7, text="4) Until fully healed")

    def _handle_key(self, event):
        key = event.sym
        if key == tcod.event.KeySym.N1:
            n = 100 * consts.MAX_INIT
        elif key == tcod.event.KeySym.N2:
            n = 500 * consts.MAX_INIT
        elif key == tcod.event.KeySym.N3:
            n = 1000 * consts.MAX_INIT
        elif key == tcod.event.KeySym.N4:
            return LoopedRestHandler(self.engine, remaining_time=None, until_full=True)
        else:
            n = None

        if n is not None:
            return LoopedRestHandler(self.engine, remaining_time=n)
        return super()._handle_key(event)


class CharacterInformationHandler(AskUserEventHandler):
    TITLE = "CHARACTER INFORMATION"
    TABS_NAMES = ["INVENTORY", "STATS", "ESSENCES", "SKILLS"]
    TABS_SPACER = "  "
    TABS = TABS_NAMES[0] + TABS_SPACER + TABS_NAMES[1] + TABS_SPACER + TABS_NAMES[2]
    SELECTED_TAB: int
    PALETTE: color.Palette
    SUBTABS: List[str]
    SELECTED_SUBTAB: int

    def __init__(
        self,
        engine,
        selected_tab: int,
        palette: color.Palette,
        subtabs: list[str],
        selected_subtab: int,
    ):
        super().__init__(
            engine, frame_width=None, frame_height=None, title=self.TITLE, question=None
        )
        self.SELECTED_TAB = selected_tab
        self.PALETTE = palette
        self.SUBTABS = subtabs
        self.SELECTED_SUBTAB = selected_subtab

        self.x = 2
        self.y = 2
        self.frame_width = consts.SCREEN_WIDTH - 4
        self.frame_height = consts.SCREEN_HEIGHT - 4
        self.title_x = self.x + 2
        self.title_y = self.y + 2
        self.tabs_x = self.x + 2
        self.tabs_y = self.title_y + 1

        self.subtabs_x = self.tabs_x
        self.subtabs_y = self.tabs_y + 4

        self.text_x = self.x + 2
        self.text_y = self.subtabs_y + 3
        self.menu_width = 24

    def move_tab_cursor(self, delta: int) -> None:
        n = len(self.TABS_NAMES)
        self.SELECTED_TAB = (self.SELECTED_TAB + delta) % n

    def move_subtab_cursor(self, delta: int) -> None:
        n = len(self.SUBTABS)
        self.SELECTED_SUBTAB = (self.SELECTED_SUBTAB + delta) % n

    def on_render(
        self,
        console,
        vertical_split: bool = True,  # if false, make a horizontal split line in the middle of the screen, not a vertical one!
        horizontal_split_y: int = None,
    ):
        super().on_render(console)
        render_functions.render_character_information_screens(
            console=console,
            palette=self.PALETTE,
            x=self.x,
            y=self.y,
            frame_width=self.frame_width,
            frame_height=self.frame_height,
            title=self.TITLE,
            title_x=self.title_x,
            tabs_x=self.tabs_x,
            tabs_y=self.tabs_y,
            selected_tab=self.SELECTED_TAB,
            subtabs_x=self.subtabs_x,
            subtabs_y=self.subtabs_y,
            subtabs=self.SUBTABS,
            selected_subtab=self.SELECTED_SUBTAB,
            text_y=self.text_y,
            vertical_split=vertical_split,
            horizontal_split_y=horizontal_split_y,
        )

    def _handle_key(self, event):
        return super()._handle_key(event)


class CharacterStatsHandler(CharacterInformationHandler):
    SUBTABS = ["BASE", "DAMAGE", "COMBAT"]
    SELECTED_SUBTAB = 0
    SUBTAB_SPACER = "  "
    SELECTED_STAT_INDEX = None
    BASE_STATS_DESCRIPTIONS = menu_text.BASE_STAT_DESCRIPTIONS
    DAMAGE_STAT_DESCRIPTIONS = menu_text.DAMAGE_STAT_DESCRIPTIONS
    COMBAT_STAT_DESCRIPTIONS = menu_text.COMBAT_TEXT_DESCRIPTIONS

    def __init__(self, engine):
        super().__init__(
            engine,
            selected_tab=1,
            palette=color.menu_stats_palette,
            subtabs=self.SUBTABS,
            selected_subtab=self.SELECTED_SUBTAB,
        )

        self.base_stat_rows: list[StatRow] = []
        self._build_base_stat_rows()
        self.damage_stat_rows: list[StatRow] = []
        self._build_damage_stat_rows()
        self.combat_stat_rows: list[StatRow] = []
        self._build_combat_stat_rows()

        # self.combat_stat_rows: list[StatRow] = []
        # self._build_combat_stat_rows()

    def _build_base_stat_rows(self) -> None:
        rows: list[StatRow] = []

        # --- ATTRIBUTES HEADER ---
        rows.append(StatRow(None, "ATTRIBUTES", "", selectable=False))

        for stat_type, (label, value) in zip(
            [
                StatTypes.STRENGTH,
                StatTypes.DEXTERITY,
                StatTypes.CONSTITUTION,
                StatTypes.INTELLIGENCE,
                StatTypes.CUNNING,
                StatTypes.WILLPOWER,
            ],
            self.gather_base_attributes(),
        ):
            rows.append(
                StatRow(
                    key=stat_type,
                    label=label,
                    value=value,
                    selectable=True,
                )
            )

        # spacer
        rows.append(StatRow(None, "", "", selectable=False))

        # --- RESOURCES HEADER ---
        rows.append(StatRow(None, "RESOURCES", "", selectable=False))

        resource_keys = [
            StatTypes.HP,
            StatTypes.HP_REGEN,
            None,
            StatTypes.ENERGY,
            StatTypes.ENERGY_REGEN,
            None,
            StatTypes.MANA,
            StatTypes.MANA_REGEN,
            None,
            StatTypes.CARRYING_CAPACITY,
            StatTypes.ENCUMBRANCE,
        ]

        for key, (label, value) in zip(resource_keys, self.gather_resources()):
            if key is None:
                rows.append(StatRow(None, "", "", selectable=False))
            else:
                rows.append(
                    StatRow(
                        key=key,
                        label=label,
                        value=value,
                        selectable=True,
                    )
                )

        self.base_stat_rows = rows

    def _build_damage_stat_rows(self) -> None:
        # damage stat rows are: (see the following variables)

        rows: list[StatRow] = []

        # spacer
        rows.append(StatRow(None, "", "", selectable=False))

        for stat_type, (label, value) in zip(
            [
                StatTypes.DAMAGE_RESISTS,
                StatTypes.DAMAGE_AMPS,
                StatTypes.DAMAGE_MASTERIES,
            ],
            self.gather_damage_stats(),
        ):
            rows.append(
                StatRow(key=stat_type, label=label, value=value, selectable=True)
            )
            # spacer
            rows.append(StatRow(None, "", "", selectable=False))
            rows.append(StatRow(None, "", "", selectable=False))

        self.damage_stat_rows = rows

    def _build_combat_stat_rows(self) -> None:
        rows: list[StatRow] = []

        # --- WEAPONS ---
        weapon_stat_types = combat_stat_types.WeaponStatTypes

        for stat_type, (label, value) in zip(
            list(weapon_stat_types), self.gather_weapon_stats()
        ):
            rows.append(
                StatRow(key=stat_type, label=label, value=value, selectable=True)
            )

        rows.append(StatRow(None, "", "", selectable=False))

        # --- CRIT STUFF --
        rows.append(StatRow(None, "CRITICAL ATTACKS", "", selectable=False))
        for stat_type, (label, value) in zip(
            list(combat_stat_types.CritStatTypes), self.gather_crit_stats()
        ):
            rows.append(
                StatRow(key=stat_type, label=label, value=value, selectable=True)
            )

        rows.append(StatRow(None, "", "", selectable=False))

        armor_stat_types = combat_stat_types.ArmorStatTypes

        # --- DEFENSE ---
        rows.append(StatRow(None, "DEFENSE", "", selectable=False))
        for stat_type, (label, value) in zip(
            list(armor_stat_types), self.gather_armor_stats()
        ):

            if stat_type == armor_stat_types.TOTAL:
                rows.append(StatRow(None, "", "", selectable=False))
                rows.append(
                    StatRow(key=stat_type, label=label, value=value, selectable=True)
                )
            else:
                rows.append(
                    StatRow(key=stat_type, label=label, value=value, selectable=True)
                )

        rows.append(StatRow(None, "", "", selectable=False))

        # --- SPEEDS ---
        rows.append(StatRow(None, "SPEED", "", selectable=False))

        speed_stat_types = combat_stat_types.SpeedStatTypes

        for stat_type, (label, value) in zip(
            list(speed_stat_types), self.gather_speed_stats()
        ):
            rows.append(
                StatRow(key=stat_type, label=label, value=value, selectable=True)
            )

        self.combat_stat_rows = rows

    def gather_weapon_stats(self) -> List[Tuple[str, str]]:
        """
        Gather weapon stats for UI display.

        Always returns MAIN-HAND and OFF-HAND values.
        Missing weapons are displayed as 'N/A'.
        """
        stats = self.engine.player.fighter.stats
        equipment = self.engine.player.equipment
        weapon_stat_types = combat_stat_types.WeaponStatTypes

        main: Item | None = equipment.slots[EquipmentTypes.MAIN_HAND]
        if main is not None:
            main: WeaponEquippable = main.equippable
        off: Item | None = equipment.slots[EquipmentTypes.OFF_HAND]
        if off is not None:
            off = off.equippable
            if isinstance(off, ArmorEquippable):
                off = None
            off: WeaponEquippable

        def format_range(weapon) -> str:
            if weapon.weapon_range.is_melee:
                return "MELEE"
            return str(round_for_display(weapon.weapon_range.max_range))

        def format_weapon_values(
            weapon: WeaponEquippable | None,
            fallback_index: int,
        ) -> tuple[str, str, str, str]:
            if weapon is None:
                return ("N/A", "N/A", "N/A", "N/A")

            attack = round_for_display(weapon.get_attack(self.engine.player).value)
            damage = round_for_display(
                weapon.get_damage(self.engine.player).totalled_damage
            )
            rng = format_range(weapon)
            cost = round_for_display(
                weapon.get_attack_init_cost(self.engine.player)
                / consts.TRUE_INIT_FACTOR
                * stats.initiative.attack_multiplier
            )

            return (str(attack), str(damage), str(rng), str(cost) + " INIT")

        # --- pull values ---
        main_vals = (
            format_weapon_values(main, 0)
            if main or off
            else (
                str(round_for_display(stats.attack[0])),
                str(round_for_display(stats.damage[0].totalled_damage)),
                (
                    "MELEE"
                    if stats.attack_range[0].is_melee
                    else str(round_for_display(stats.attack_range[0].max_range))
                ),
                str(
                    round_for_display(
                        stats.attack_init_cost[0] / consts.TRUE_INIT_FACTOR
                    )
                )
                + " INIT",
            )
        )

        off_vals = format_weapon_values(off, 1)

        rows: list[tuple[str, list[str]]] = [
            (
                f"{weapon_stat_types.ATTACK.value.upper()}: ",
                [main_vals[0], off_vals[0]],
            ),
            (
                f"{weapon_stat_types.DAMAGE.value.upper()}: ",
                [main_vals[1], off_vals[1]],
            ),
            (f"{weapon_stat_types.RANGE.value.upper()}: ", [main_vals[2], off_vals[2]]),
            (f"{weapon_stat_types.COST.value.upper()}: ", [main_vals[3], off_vals[3]]),
        ]

        return self.pad_weapon_stat_rows(rows)

    def gather_crit_stats(self) -> List[Tuple[str, str]]:
        crit_stat_type = combat_stat_types.CritStatTypes

        rows: list[StatRow] = []

        chance = (
            round_for_display(self.engine.player.fighter.stats.critical_chance.value)
            * 100
        )
        mult = round_for_display(
            self.engine.player.fighter.stats.critical_multiplier.value
        )

        rows.append((f"{crit_stat_type.CRITICAL_CHANCE.value.upper()}: ", f"{chance}%"))
        rows.append(
            (f"{crit_stat_type.CRITICAL_MULTIPLIER.value.upper()}: ", f"{mult}")
        )
        return self.pad_stat_rows(rows)

    def gather_armor_stats(self) -> List[Tuple[str, str]]:
        armor_stat_type = combat_stat_types.ArmorStatTypes
        stats = self.engine.player.fighter.stats

        head = stats.head_defense.value
        torso = stats.torso_defense.value
        legs = stats.legs_defense.value
        feet = stats.feet_defense.value
        off_hand = stats.shield_defense.value
        total = stats.total_defense

        rows: List[Tuple[str, str]] = []
        all_defenses = {
            armor_stat_type.HEAD: head,
            armor_stat_type.TORSO: torso,
            armor_stat_type.LEGS: legs,
            armor_stat_type.FEET: feet,
            armor_stat_type.OFF_HAND: off_hand,
            armor_stat_type.TOTAL: total,
        }
        for dtype, dval in all_defenses.items():
            dval = round_for_display(dval)
            rows.append((f"{dtype.value.upper()}: ", dval))

        return self.pad_stat_rows(rows)

    def gather_speed_stats(self) -> List[Tuple[str, str]]:
        speed_stat_types = combat_stat_types.SpeedStatTypes
        initiative = self.engine.player.fighter.stats.initiative

        global_speed = initiative.global_speed.value
        movement_speed = initiative.movement_speed.value
        attack_speed = initiative.attack_speed.value
        casting_speed = initiative.casting_speed.value

        rows: List[Tuple[str, str]] = []
        all_speeds = {
            speed_stat_types.GLOBAL_SPEED: global_speed,
            speed_stat_types.MOVEMENT_SPEED: movement_speed,
            speed_stat_types.ATTACK_SPEED: attack_speed,
            speed_stat_types.CASTING_SPEED: casting_speed,
        }
        for dtype, dval in all_speeds.items():
            dval = round_for_display(dval)
            rows.append((f"{dtype.value.upper()}: ", dval))

        return self.pad_stat_rows(rows)

    def pad_weapon_stat_rows(
        self,
        rows: List[Tuple[str, List[str]]],
    ) -> List[Tuple[str, str]]:
        """
        Pad weapon stat rows into:
            LABEL | MAIN-HAND | OFF-HAND

        Always assumes exactly two columns.
        """
        if not rows:
            return []

        spacer = "  "

        # --- label padding ---
        max_label_width = max(len(label) for label, _ in rows)
        padded_labels = [label.ljust(max_label_width) for label, _ in rows]

        # --- column widths ---
        main_width = max(len(values[0]) for _, values in rows)
        off_width = max(len(values[1]) for _, values in rows)

        final_rows: list[tuple[str, str]] = []

        for padded_label, (_, values) in zip(padded_labels, rows):
            main_val = values[0].ljust(main_width)
            off_val = values[1].ljust(off_width)
            final_rows.append((padded_label, spacer.join([main_val, off_val])))

        return final_rows

    def gather_damage_stats(self) -> List[Tuple[str, str]]:
        """Gathers damage stats for horizontal UI display."""
        stats = self.engine.player.fighter.stats
        rows: List[Tuple[str, Dict[DamageTypes, str]]] = []

        damage_stats = [
            StatTypes.DAMAGE_RESISTS,
            StatTypes.DAMAGE_AMPS,
            StatTypes.DAMAGE_MASTERIES,
        ]

        labels = {
            StatTypes.DAMAGE_RESISTS: "RESIST.",
            StatTypes.DAMAGE_AMPS: "AMP.",
            StatTypes.DAMAGE_MASTERIES: "MASTERY",
        }

        damage_objects = {
            StatTypes.DAMAGE_RESISTS: stats.damage_resists,
            StatTypes.DAMAGE_AMPS: stats.damage_amps,
            StatTypes.DAMAGE_MASTERIES: stats.damage_masteries,
        }

        for stat_type in damage_stats:
            label = labels[stat_type]
            stat_obj = damage_objects[stat_type]

            value: Dict[DamageTypes, str] = {}
            for dtype in DamageTypes:
                dstat: CharacterStat = getattr(stat_obj, dtype.normalized)
                raw = (
                    dstat.value
                    if stat_type == StatTypes.DAMAGE_MASTERIES
                    else dstat.value * 100
                )
                disp = round_for_display(raw)
                value[dtype] = (
                    f"{disp}" if stat_type == StatTypes.DAMAGE_MASTERIES else f"{disp}%"
                )

            rows.append((label, value))

        return self.pad_damage_rows(rows)

    def move_subtab_cursor(self, delta: int) -> None:
        self.SELECTED_STAT_INDEX = None
        super().move_subtab_cursor(delta)

    def move_stat_cursor(self, delta: int) -> None:
        match self.SELECTED_SUBTAB:
            case 0:
                stat_rows = self.base_stat_rows
            case 1:
                stat_rows = self.damage_stat_rows
            case 2:
                stat_rows = self.combat_stat_rows

        selectable_indices = [i for i, row in enumerate(stat_rows) if row.selectable]

        if not selectable_indices:
            return

        if self.SELECTED_STAT_INDEX is None:
            self.SELECTED_STAT_INDEX = selectable_indices[0 if delta > 0 else -1]
            return

        current_pos = selectable_indices.index(self.SELECTED_STAT_INDEX)
        new_pos = (current_pos + delta) % len(selectable_indices)
        self.SELECTED_STAT_INDEX = selectable_indices[new_pos]

    def render_base_stats(self, console: tcod.console.Console) -> None:
        x = self.text_x
        y = self.text_y + 1

        # Static info (still fine to render directly)
        console.print(
            x, y, f"NAME: {self.engine.player.personal_name}", fg=self.PALETTE.white
        )
        y += 2
        console.print(
            x,
            y,
            f"LEVEL: {self.engine.player.level.current_level}",
            fg=self.PALETTE.white,
        )
        y += 2
        console.print(
            x,
            y,
            f"EXP: {self.engine.player.level.current_xp}/"
            f"{self.engine.player.level.experience_to_next_level}",
            fg=self.PALETTE.white,
        )
        y += 4
        console.print(
            x=x,
            y=y,
            text=f"§: {self.engine.player.wallet.balance(Currency.SOUL_COIN)}",
            fg=self.PALETTE.white,
        )
        y += 2
        console.print(
            x=x,
            y=y,
            text=f"☼: {self.engine.player.wallet.balance(Currency.SPIRIT_ASH)}",
            fg=self.PALETTE.white,
        )

        y += 4

        # Stat list
        for idx, row in enumerate(self.base_stat_rows):
            if row.label == "ATTRIBUTES" or row.label == "RESOURCES":
                console.print(
                    x=x,
                    y=y,
                    text=row.label,
                    fg=self.PALETTE.white,
                    bg=self.PALETTE.dark,
                )
                y += 2
                continue

            if not row.label:
                y += 1
                continue

            selected = idx == self.SELECTED_STAT_INDEX

            fg = self.PALETTE.white if selected else self.PALETTE.light
            bg = self.PALETTE.mid if selected else None

            abbrev = row.label[:3]
            rest = row.label[3:]

            label_color = self.PALETTE.white if selected else self.PALETTE.mid_light
            if row.key in {
                StatTypes.HP,
                StatTypes.HP_REGEN,
                StatTypes.ENERGY,
                StatTypes.ENERGY_REGEN,
                StatTypes.MANA,
                StatTypes.MANA_REGEN,
                StatTypes.CARRYING_CAPACITY,
                StatTypes.ENCUMBRANCE,
            }:
                label_color = self.PALETTE.white if selected else self.PALETTE.mid_light

            abbrev_color = label_color
            if row.key in {
                StatTypes.STRENGTH,
                StatTypes.DEXTERITY,
                StatTypes.CONSTITUTION,
                StatTypes.INTELLIGENCE,
                StatTypes.CUNNING,
                StatTypes.WILLPOWER,
            }:
                abbrev_color = self.PALETTE.white if selected else self.PALETTE.light

            console.print(x + 2, y, abbrev, fg=abbrev_color, bg=bg)
            console.print(x + 2 + len(abbrev), y, rest, fg=label_color, bg=bg)
            console.print(x + 2 + len(row.label), y, row.value, fg=fg, bg=bg)

            y += 2

        self._render_stat_description(console)

    def _render_stat_description(self, console: tcod.console.Console) -> None:

        match self.SELECTED_SUBTAB:
            case 0:
                stat_rows = self.base_stat_rows
                stat_descriptions = self.BASE_STATS_DESCRIPTIONS
                vertical = True
            case 1:
                stat_rows = self.damage_stat_rows
                stat_descriptions = self.DAMAGE_STAT_DESCRIPTIONS
                vertical = False
            case 2:
                stat_rows = self.combat_stat_rows
                stat_descriptions = self.COMBAT_STAT_DESCRIPTIONS
                vertical = True
            case _:
                raise ValueError("literally how")

        if self.SELECTED_STAT_INDEX is None:
            return

        row = stat_rows[self.SELECTED_STAT_INDEX]
        if row.key is None:
            return

        descriptor = next(d for d in stat_descriptions if d.key == row.key)

        if vertical:
            x = self.frame_width // 2 + self.x + 2
            y = self.text_y + 1
        else:
            x = self.text_x
            y = self.frame_height // 2 + self.y + 2

        console.print(x, y, descriptor.label, fg=self.PALETTE.white)
        y += 2
        if isinstance(descriptor.description, list):
            for desc in descriptor.description:
                text = f"{desc}" if desc == descriptor.description[0] else f"  {desc}"
                console.print(x, y, text, fg=self.PALETTE.light)
                y += 2 if desc != descriptor.description[-1] else 4
        else:
            console.print(x, y, descriptor.description, fg=self.PALETTE.light)
            y += 2
        y += 2

        if descriptor.formula:
            if isinstance(descriptor.formula, list):
                for desc in descriptor.formula:
                    text = (
                        f"FORMULA: {desc}"
                        if desc == descriptor.formula[0]
                        else f"  {desc}"
                    )
                    console.print(x, y, text, fg=self.PALETTE.light)
                    y += 2
            else:
                console.print(
                    x, y, f"FORMULA: {descriptor.formula}", fg=self.PALETTE.light
                )

    def render_damage_stats(self, console: tcod.console.Console) -> None:
        x = self.text_x + 2
        y = self.text_y + 1

        # Header row: damage type abbreviations
        header_labels = []
        header_labels.append("       ")
        for dt in DamageTypes:
            header_labels.append(menu_text.DAMAGE_TYPE_ABBREVIATIONS[dt])

        header = "  ".join(header_labels)

        console.print(
            x=x,
            y=y,
            text=header,
            fg=self.PALETTE.white,
        )
        y += 2

        for idx, row in enumerate(self.damage_stat_rows):

            selected = idx == self.SELECTED_STAT_INDEX

            if not row.label:
                y += 1
                continue

            fg = self.PALETTE.white if selected else self.PALETTE.light
            bg = self.PALETTE.mid if selected else None

            console.print(
                x=x,
                y=y,
                text=f"{row.label} ",
                fg=self.PALETTE.white if selected else self.PALETTE.mid_light,
                bg=bg,
            )

            console.print(x=x + len(row.label), y=y, text=f"{row.value}", fg=fg, bg=bg)

            y += 2

        self._render_stat_description(console)

    def render_combat_stats(self, console: tcod.console.Console) -> None:
        x = self.text_x + 2
        y = self.text_y + 1

        # --- header ---
        header = "WEAPONS   " + "MAIN-HAND" + "  " + "OFF-HAND"

        console.print(x, y, header, fg=self.PALETTE.white)
        y += 2

        # --- rows ---
        for idx, row in enumerate(self.combat_stat_rows):
            if not row.label:
                y += 1
                continue

            selected = idx == self.SELECTED_STAT_INDEX

            fg = self.PALETTE.white if selected else self.PALETTE.light
            bg = self.PALETTE.mid if selected else None

            if row.label in {"DEFENSE", "CRITICAL ATTACKS", "SPEED"}:
                fg = self.PALETTE.white
                console.print(x, y, f"{row.label}", fg=self.PALETTE.white)
                y += 2
                continue

            console.print(
                x + 2,
                y,
                f"{row.label}",
                fg=self.PALETTE.white if selected else self.PALETTE.mid_light,
                bg=bg,
            )

            console.print(x + 2 + len(row.label), y, f"{row.value}", fg=fg, bg=bg)
            y += 2

        self._render_stat_description(console)

    def gather_base_attributes(self) -> List[Tuple[str, str]]:
        """
        Gather player base attributes for UI display.

        Each entry is returned as a (label, value) tuple, where `label`
        always ends with ': ' and `value` contains the formatted stat text.
        """
        stats = self.engine.player.fighter.stats
        rows: List[Tuple[str, str]] = []

        base_attributes = [
            StatTypes.STRENGTH,
            StatTypes.DEXTERITY,
            StatTypes.CONSTITUTION,
            StatTypes.INTELLIGENCE,
            StatTypes.CUNNING,
            StatTypes.WILLPOWER,
        ]

        for stat_type in base_attributes:
            label = f"{stat_type.value.upper()}: "
            value = str(round_for_display(stats.get_stat(stat_type).value))
            rows.append((label, value))

        return self.pad_stat_rows(rows)

    def gather_resources(self) -> List[Tuple[str, str]]:
        """
        Gather player resource and regen stats for UI display.

        Each entry is returned as a (label, value) tuple, where `label`
        always ends with ': ' and `value` contains the formatted stat text.
        Empty rows are represented as ('', '').
        """
        stats = self.engine.player.fighter.stats
        rows: List[Tuple[str, str]] = []

        resource_order = [
            StatTypes.HP,
            StatTypes.HP_REGEN,
            None,
            StatTypes.ENERGY,
            StatTypes.ENERGY_REGEN,
            None,
            StatTypes.MANA,
            StatTypes.MANA_REGEN,
            None,
            StatTypes.CARRYING_CAPACITY,
            StatTypes.ENCUMBRANCE,
        ]

        for stat_type in resource_order:
            if stat_type is None:
                rows.append(("", ""))
                continue

            label = (
                f"{stat_type.value.upper()}: "
                if stat_type is not StatTypes.CARRYING_CAPACITY
                else "CARRYING CAP.: "
            )
            stat = getattr(stats, stat_type.normalized)

            # Resource-style stats (current / max)
            if isinstance(stat, Resource):
                current = round_for_display(stat.value)
                maximum = round_for_display(stat.max_value)

                if stat_type in {
                    StatTypes.CARRYING_CAPACITY,
                    StatTypes.ENCUMBRANCE,
                }:
                    value = f"{current}/{maximum} lbs"
                else:
                    value = f"{current}/{maximum}"

            # Regen-style stats (value / 100 initiative)
            else:
                value = f"{round_for_display(stat.value)}/100 INITIATIVE"

            rows.append((label, value))

        return self.pad_stat_rows(rows)

    def pad_stat_rows(
        self,
        rows: Tuple[str, str] | List[Tuple[str, str]],
    ) -> Tuple[str, str] | List[Tuple[str, str]]:
        """
        Pad stat row labels so all values align in the same column.

        Accepts either a single (label, value) tuple or a list of them.
        Empty rows ('', '') are preserved and ignored for width calculation.
        """
        # Normalize to list
        is_single = isinstance(rows, tuple)
        row_list: List[Tuple[str, str]] = [rows] if is_single else list(rows)

        # Compute max label width (ignore empty labels)
        max_label_width = max(
            (len(label) for label, _ in row_list if label),
            default=0,
        )

        padded = [
            (label.ljust(max_label_width), value) if label else ("", "")
            for label, value in row_list
        ]

        return padded[0] if is_single else padded

    def pad_damage_rows(
        self,
        rows: List[Tuple[str, Dict[DamageTypes, str]]],
    ) -> List[Tuple[str, str]]:
        """
        Pad damage stat rows into a single horizontal string per row.

        Columns are LEFT-justified and share widths with headers.
        """
        if not rows:
            return []

        spacer = " "

        damage_types = list(DamageTypes)

        # --- label padding ---
        max_label_width = max(len(label) for label, _ in rows)
        padded_labels = [label.ljust(max_label_width) for label, _ in rows]

        # --- column widths (values vs headers) ---
        col_widths: dict[DamageTypes, int] = {}

        for dtype in damage_types:
            header_width = 6
            value_width = max(len(values[dtype]) for _, values in rows)
            col_widths[dtype] = max(header_width, value_width)

        # --- assemble final rows ---
        final_rows: list[tuple[str, str]] = []

        for (label, values), padded_label in zip(rows, padded_labels):
            cols = [values[dtype].ljust(col_widths[dtype]) for dtype in damage_types]
            final_rows.append((padded_label + "  ", spacer.join(cols)))

        return final_rows

    def on_render(self, console):

        match self.SELECTED_SUBTAB:
            case 0:
                super().on_render(console)
                self.render_base_stats(console)
            case 1:
                super().on_render(
                    console,
                    vertical_split=False,
                    horizontal_split_y=(self.y + self.frame_height) // 2,
                )
                self.render_damage_stats(console)
            case 2:
                super().on_render(console)
                self.render_combat_stats(console)

    def _handle_key(self, event):
        key = event.sym
        modifier = event.mod

        # character information screen traversal
        if key == tcod.event.KeySym.LEFT and modifier & (
            tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT
        ):
            return CharacterInventoryHandler(self.engine)

        if key == tcod.event.KeySym.RIGHT and modifier & (
            tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT
        ):
            # essence screen
            return CharacterEssenceHandler(self.engine)

        # cursor movement
        if key == tcod.event.KeySym.LEFT:
            self.move_subtab_cursor(-1)
        elif key == tcod.event.KeySym.RIGHT:
            self.move_subtab_cursor(1)
        elif key == tcod.event.KeySym.UP:
            self.move_stat_cursor(-1)
        elif key == tcod.event.KeySym.DOWN:
            self.move_stat_cursor(1)
        return super()._handle_key(event)


class CharacterInventoryHandler(CharacterInformationHandler):
    SUBTABS = ["INVENTORY", "EQUIPMENT"]
    SELECTED_SUBTAB = 0
    SUBTAB_SPACER = "  "
    SELECTED_INVENTORY_INDEX = None
    SELECTED_INVENTORY_PAGE = 0
    MAX_INVENTORY_PAGE = None
    INVENTORY_ROWS_LENGTH = 26

    def __init__(self, engine):
        super().__init__(
            engine,
            selected_tab=0,
            palette=color.menu_inventory_palette,
            subtabs=self.SUBTABS,
            selected_subtab=self.SELECTED_SUBTAB,
        )

        self.item_list = []
        self.equipment = {}
        self.inventory_rows: List[InventoryRow] = []
        self.MAX_INVENTORY_PAGE = None
        self.active_inventory_rows: List[InventoryRow] = []
        self.equipment_rows: List[InventoryRow] = []
        self.regenerate_inventory()

        self.item_info_handler = CharacterInventoryItemInformationHandler(
            self.engine, self
        )
        self.item_info_handler.parent = self

    def regenerate_inventory(self) -> None:
        self._build_item_list()
        self._build_equipment()
        self._build_inventory_rows()
        self.MAX_INVENTORY_PAGE = math.floor(
            len(self.item_list) / self.INVENTORY_ROWS_LENGTH
        )
        self._build_active_inventory_rows()
        self._build_equipment_rows()

    def _build_item_list(self) -> None:
        self.item_list = self.engine.player.inventory.items

    def _build_equipment(self) -> None:
        self.equipment = self.engine.player.equipment.slots

    @classmethod
    def add_row_spacer(cls, rows: List[InventoryRow]) -> None:
        rows.append(InventoryRow(item=None, letter=None, name=None, selectable=False))

    def _build_inventory_rows(self) -> List[InventoryRow]:
        rows: List[InventoryRow] = []

        for idx, item in enumerate(self.item_list):
            item: Item
            letter = chr(ord("a") + (idx % 26))
            name = item.name
            if item in self.equipment.values():
                name += " (E)"
            selectable = True
            rows.append(
                InventoryRow(item=item, letter=letter, name=name, selectable=selectable)
            )
        self.inventory_rows = rows

    def _build_active_inventory_rows(self) -> List[InventoryRow]:
        rows: List[InventoryRow]
        if self.SELECTED_INVENTORY_PAGE == self.MAX_INVENTORY_PAGE:
            rows = self.inventory_rows[
                self.INVENTORY_ROWS_LENGTH * self.SELECTED_INVENTORY_PAGE :
            ]
        else:
            rows = self.inventory_rows[
                self.INVENTORY_ROWS_LENGTH
                * self.SELECTED_INVENTORY_PAGE : self.INVENTORY_ROWS_LENGTH
                * (self.SELECTED_INVENTORY_PAGE + 1)
            ]
        self.active_inventory_rows = rows

    def _build_equipment_rows(self) -> List[InventoryRow]:
        rows: List[InventoryRow] = []

        for etype in list(EquipmentTypes):
            if etype == EquipmentTypes.ESSENCE:
                # not in equipment screen, it's in the Essences screen!
                continue
            item = self.equipment.get(etype, None)
            if not isinstance(item, Item):
                item = None
                letter = etype.value.upper()
                name = "N/A"
                selectable = True
            else:
                item: Item
                letter = etype.value.upper()
                name = item.name
                selectable = True
            rows.append(
                InventoryRow(item=item, letter=letter, name=name, selectable=selectable)
            )

            if etype in {
                EquipmentTypes.OFF_HAND,
                EquipmentTypes.FEET,
                EquipmentTypes.WAIST,
                EquipmentTypes.EARRING_2,
                EquipmentTypes.RING_2,
                EquipmentTypes.NECKLACE,
                EquipmentTypes.ACCESSORY_4,
            }:
                self.add_row_spacer(rows)

        self.equipment_rows = rows

    def move_selection_cursor(self, delta: int) -> None:
        match self.SELECTED_SUBTAB:
            case 0:
                self.move_inventory_cursor(delta)
            case 1:
                self.move_equipment_cursor(delta)

    def move_inventory_cursor(self, delta: int) -> None:
        if self.SELECTED_INVENTORY_INDEX is None:
            selectable_indices = [
                i for i, row in enumerate(self.inventory_rows) if row.selectable
            ]
            if not selectable_indices:
                return

            if delta < 0:
                # last item of last page
                self.SELECTED_INVENTORY_PAGE = self.MAX_INVENTORY_PAGE
                self.SELECTED_INVENTORY_INDEX = selectable_indices[-1]
            else:
                self.SELECTED_INVENTORY_INDEX = selectable_indices[0]
            return

        selectable_indices = [
            i for i, row in enumerate(self.active_inventory_rows) if row.selectable
        ]

        if not selectable_indices:
            return

        current_pos = selectable_indices.index(self.SELECTED_INVENTORY_INDEX)
        new_pos = current_pos + delta
        if self.MAX_INVENTORY_PAGE != 0:
            underflow = selectable_indices[0]
            overflow = selectable_indices[-1]
            if new_pos < underflow or new_pos > overflow:
                # 1) update the page
                self.SELECTED_INVENTORY_PAGE = (
                    self.SELECTED_INVENTORY_PAGE + delta
                ) % (self.MAX_INVENTORY_PAGE + 1)

                # 2) regenerate self.active_inventory_rows
                self._build_active_inventory_rows()

                # 3) recreate selectable_indices
                selectable_indices = [
                    i
                    for i, row in enumerate(self.active_inventory_rows)
                    if row.selectable
                ]

                # 4) set index
                self.SELECTED_INVENTORY_INDEX = (
                    selectable_indices[0] if delta > 0 else selectable_indices[-1]
                )
                return
            self.SELECTED_INVENTORY_INDEX = selectable_indices[new_pos]
        else:
            new_pos %= len(selectable_indices)
            self.SELECTED_INVENTORY_INDEX = selectable_indices[new_pos]

    def move_equipment_cursor(self, delta: int) -> None:
        selectable_indices = [
            i for i, row in enumerate(self.equipment_rows) if row.selectable
        ]
        if self.SELECTED_INVENTORY_INDEX is None:
            self.SELECTED_INVENTORY_INDEX = (
                selectable_indices[0] if delta > 0 else selectable_indices[-1]
            )
            return
        current_pos = selectable_indices.index(self.SELECTED_INVENTORY_INDEX)
        new_pos = (current_pos + delta) % len(selectable_indices)
        self.SELECTED_INVENTORY_INDEX = selectable_indices[new_pos]

    def move_subtab_cursor(self, delta: int) -> None:
        self.SELECTED_INVENTORY_INDEX = None
        super().move_subtab_cursor(delta)

    def render_inventory(self, console: tcod.console.Console) -> None:

        x = self.text_x
        y = self.text_y + 1

        for idx, item in enumerate(self.active_inventory_rows):
            if not item.letter:
                y += 1
                continue
            selected = idx == self.SELECTED_INVENTORY_INDEX
            fg = self.PALETTE.white if selected else self.PALETTE.mid_light
            name_fg = (
                self.PALETTE.white
                if selected
                else render_functions.get_item_inventory_color(item.item)
            )
            bg = self.PALETTE.mid_dark if selected else None
            letter_starter = f"{item.letter}) "
            item_name = f"{item.name}"
            console.print(x=x, y=y, text=letter_starter, fg=fg, bg=bg)
            console.print(
                x=x + len(letter_starter), y=y, text=item_name, fg=name_fg, bg=bg
            )
            y += 2

    def render_equipment(self, console: tcod.console.Console) -> None:
        x = self.text_x
        y = self.text_y

        for idx, item in enumerate(self.equipment_rows):
            if not item.letter:
                y += 1
                continue

            selected = idx == self.SELECTED_INVENTORY_INDEX
            fg = self.PALETTE.white if selected else self.PALETTE.mid_light
            item_inv_color = self.PALETTE.light
            if item.item is not None:
                item_inv_color = render_functions.get_item_inventory_color(item.item)

            name_fg = self.PALETTE.white if selected else item_inv_color
            bg = self.PALETTE.mid_dark if selected else None

            title_fg = self.PALETTE.white

            if item.letter == EquipmentTypes.MAIN_HAND.value.upper():
                console.print(x=x, y=y, text="WEAPON SLOTS", fg=title_fg)
                y += 2
            elif item.letter == EquipmentTypes.HEAD.value.upper():
                console.print(x=x, y=y, text="ARMOR SLOTS", fg=title_fg)
                y += 2
            elif item.letter == EquipmentTypes.FACE.value.upper():
                console.print(x=x, y=y, text="MISC. CLOTHING SLOTS", fg=title_fg)
                y += 2
            elif item.letter == EquipmentTypes.NECKLACE.value.upper():
                console.print(x=x, y=y, text="MISC. JEWELRY SLOTS", fg=title_fg)
                y += 2

            equipment_name = f"  {item.letter}: "
            item_name = f"{item.name}"
            console.print(x=x, y=y, text=equipment_name, fg=fg, bg=bg)
            console.print(
                x=x + len(equipment_name), y=y, text=item_name, fg=name_fg, bg=bg
            )
            y += 2

    def on_render(self, console):
        super().on_render(console)
        match self.SELECTED_SUBTAB:
            case 0:
                self.render_inventory(console)
            case 1:
                self.render_equipment(console)
        self.item_info_handler.on_render(console)

    def _handle_key(self, event):
        key = event.sym
        modifier = event.mod

        # character information screens traversal
        if key == tcod.event.KeySym.LEFT and modifier & (
            tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT
        ):
            # skills screen
            pass
        if key == tcod.event.KeySym.RIGHT and modifier & (
            tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT
        ):
            return CharacterStatsHandler(self.engine)

        # cursor movement
        if key == tcod.event.KeySym.LEFT:
            self.move_subtab_cursor(-1)
        elif key == tcod.event.KeySym.RIGHT:
            self.move_subtab_cursor(1)
        elif key == tcod.event.KeySym.UP:
            self.move_selection_cursor(-1)
        elif key == tcod.event.KeySym.DOWN:
            self.move_selection_cursor(1)

        if self.SELECTED_SUBTAB == 0 and self.active_inventory_rows:
            # Handle letter-based inventory selection (a–z)
            if tcod.event.KeySym.A <= key <= tcod.event.KeySym.Z:
                letter = chr(ord("a") + (key - tcod.event.KeySym.A))

                for idx, row in enumerate(self.active_inventory_rows):
                    if row.selectable and row.letter == letter:
                        self.SELECTED_INVENTORY_INDEX = idx
                        break

        if self.SELECTED_INVENTORY_INDEX is not None and self.current_item is not None:
            if key == tcod.event.KeySym.RETURN:
                return CharacterInventoryItemQueryHandler(self.engine, self)
        return super()._handle_key(event)

    @property
    def current_item(self) -> Optional[Item]:
        match self.SELECTED_SUBTAB:
            case 0:
                rows = self.inventory_rows
            case _:
                rows = self.equipment_rows

        current_item = rows[self.SELECTED_INVENTORY_INDEX].item
        return current_item


class CharacterInventoryItemInformationHandler(EventHandler):
    parent: CharacterInventoryHandler

    def __init__(self, engine, parent):
        super().__init__(engine)
        self.item: Optional[Item] = None
        self.x = None
        self.y = None
        self.parent = parent

    @property
    def starting_x(self) -> int:
        return self.parent.frame_width // 2 + self.parent.x + 2

    @property
    def starting_y(self) -> int:
        return self.parent.text_y + 1

    @property
    def max_char_width(self) -> int:
        return (self.parent.x + self.parent.frame_width) - (self.starting_x + 2)

    @property
    def name(self) -> str:
        return self.item.name

    @property
    def description(self) -> List[str]:
        if self.item.description is None:
            return [""]
        return self.wrap_text(self.item.description)

    @property
    def weight(self) -> str:
        return f"{round_for_display(self.item.weight)} lbs"

    @property
    def item_color(self) -> Tuple[int, int, int]:
        return render_functions.get_item_inventory_color(self.item)

    @property
    def palette(self) -> color.Palette:
        return self.parent.PALETTE

    @property
    def slot_info(self) -> Tuple[EquipmentTypes]:
        if not self.item.equippable:
            return None
        etypes = self.item.equippable.equipment_type
        if not isinstance(etypes, tuple):
            return etypes.value.upper()
        type_list = []
        for etype in etypes:
            type_list.append(etype.value.upper())
        return ", ".join(type_list)

    @property
    def bonuses(self) -> Optional[List[str]]:
        if not self.item.equippable:
            return
        bonuses = self.item.equippable.bonuses
        if bonuses == {} or bonuses is None:
            return None
        final_list = []
        special_damage_types = {
            menu_text.STAT_TYPE_NAMES.get(StatTypes.DAMAGE_AMPS).upper(),
            menu_text.STAT_TYPE_NAMES.get(StatTypes.DAMAGE_RESISTS).upper(),
        }
        for stype, modifiers in bonuses.items():
            if not isinstance(modifiers, list):
                modifiers = [modifiers]
            if isinstance(stype, tuple):
                damage_stat_type = stype[0]
                damage_stat_type = menu_text.STAT_TYPE_NAMES.get(
                    damage_stat_type, damage_stat_type.value
                ).upper()
                damage_type = stype[1].value.upper()
                stat_text = f"  {damage_stat_type} ({damage_type}): "
            else:
                damage_stat_type = None

                stat_text = (
                    f"  {menu_text.STAT_TYPE_NAMES.get(stype, stype.value.upper())}: "
                )

            mod_text = []
            for modifier in modifiers:
                match modifier.mod_type:
                    case StatModType.FLAT:
                        starter = "+"
                        ender = ""
                        if damage_stat_type in special_damage_types:
                            ender = "%"
                    case StatModType.FLAT_RIGID:
                        starter = "+"
                        ender = " (rigid)"
                    case StatModType.PERCENT_ADD:
                        starter = "+"
                        ender = "%"
                    case StatModType.PERCENT_MULT:
                        starter = "*"
                        ender = ""
                    case _:
                        print("oh no")
                if damage_stat_type is None:
                    mod_text.append(
                        f"{starter}{round_for_display(modifier.value)}{ender}"
                    )
                else:
                    if damage_stat_type in special_damage_types:
                        mod_text.append(
                            f"{starter}{round_for_display(modifier.value*100)}{ender}"
                        )
                    else:
                        mod_text.append(
                            f"{starter}{round_for_display(modifier.value)}{ender}"
                        )

            if len(mod_text) > 1:
                mod_text = ", ".join(mod_text)
            else:
                mod_text = mod_text[0]
            final_text = f"{stat_text}{mod_text}"
            final_list.append(final_text)

        final_list = None if not final_list else final_list

        return final_list

    @property
    def equipment_tags(self) -> Optional[str]:
        if not isinstance(self.item.equippable, (WeaponEquippable, ArmorEquippable)):
            return None
        tags = self.item.equippable.tags
        final_list = []
        for tag in tags:
            final_list.append(tag.value.upper())
        final_list = ", ".join(final_list)
        return f"{final_list}"

    @property
    def weapon_info(self) -> Optional[List[str]]:
        if not isinstance(self.item.equippable, WeaponEquippable):
            return None
        weapon = self.item.equippable
        attack_mods = weapon.attack_mods
        damage_mods = weapon.damage_mods
        weapon_range = weapon.weapon_range
        attack_init_cost = weapon.attack_init_cost

        final_list = []

        attack_beginning_message = "ATTACK: "
        attack_list = []
        for stype, smod in attack_mods.items():
            stat_text = f"{menu_text.STAT_TYPE_NAMES.get(stype, stype.value.upper())}"
            mod_text = f"{round_for_display(smod.value*100)}% "
            attack_list.append(f"{mod_text}{stat_text}")
        final_list.append(attack_beginning_message + ", ".join(attack_list))

        final_list.append("DAMAGE:")
        damage_list = []
        for dtype, dmod in damage_mods.items():
            damage_type_text = f"  {dtype.value.upper()}: "
            for stype, smod in dmod.items():
                stat_text = (
                    f"{menu_text.STAT_TYPE_NAMES.get(stype, stype.value.upper())}"
                )
                mod_text = f"{round_for_display(smod.value*100)}% "
                damage_list.append(f"{mod_text}{stat_text}")
            final_list.append(f"{damage_type_text}" + ", ".join(damage_list))

        weapon_range_text = (
            weapon_range.max_range if not weapon_range.is_melee else "MELEE"
        )
        weapon_range_text = "RANGE: " + weapon_range_text
        final_list.append(f"{weapon_range_text}")

        attack_init_cost_text = (
            f"COST: {round_for_display(attack_init_cost/consts.TRUE_INIT_FACTOR)} INIT"
        )
        final_list.append(attack_init_cost_text)
        return final_list

    @property
    def armor_info(self) -> Optional[List[str]]:
        if not isinstance(self.item.equippable, ArmorEquippable):
            return None
        armor = self.item.equippable
        defense_mods = armor.defense_mods

        final_list = []

        defense_beginning_message = "DEFENSE: "
        defense_list = []
        for stype, smod in defense_mods.items():
            stat_text = f"{menu_text.STAT_TYPE_NAMES.get(stype, stype.value.upper())}"
            mod_text = f"{round_for_display(smod.value*100)}% "
            defense_list.append(f"{mod_text}{stat_text}")
        final_list.append(defense_beginning_message + ", ".join(defense_list))

        return final_list

    def wrap_text(self, text: str) -> List[str]:
        """
        Wrap a string into lines that do not exceed self.max_char_width.
        Lines after the first are indented by two spaces.

        Args:
            text: The input string to wrap.

        Returns:
            A list of wrapped and indented lines.
        """
        words = text.split()
        lines: list[str] = []

        current_line: list[str] = []
        current_length = 0
        is_first_line = True

        for word in words:
            max_width = (
                self.max_char_width if is_first_line else self.max_char_width - 2
            )

            additional_length = len(word) if not current_line else len(word) + 1

            if current_length + additional_length > max_width:
                line = " ".join(current_line)
                if not is_first_line:
                    line = "  " + line

                lines.append(line)

                current_line = [word]
                current_length = len(word)
                is_first_line = False
            else:
                current_line.append(word)
                current_length += additional_length

        if current_line:
            line = " ".join(current_line)
            if not is_first_line:
                line = "  " + line
            lines.append(line)
        return lines

    def on_render(self, console: tcod.console.Console):
        if self.parent.SELECTED_INVENTORY_INDEX is None:
            return

        match self.parent.SELECTED_SUBTAB:
            case 0:
                rows = self.parent.inventory_rows
            case _:
                rows = self.parent.equipment_rows

        self.item = rows[self.parent.SELECTED_INVENTORY_INDEX].item

        if self.item is None:
            return

        self.x = self.starting_x
        self.y = self.starting_y

        self.render_name(console)

        self.render_description(console)

        if self.item.consumable:
            self.render_consumable(console)
        elif self.item.equippable:
            self.render_equippable(console)

    def render_name(self, console) -> None:
        console.print(x=self.x, y=self.y, text=self.name, fg=self.item_color)
        self.y += 2

    def render_description(self, console) -> None:
        for line in self.description:
            console.print(x=self.x, y=self.y, text=line, fg=self.palette.light)
            self.y += 2
        self.y += 2

    def render_consumable(self, console) -> None:
        # TODO: eventually, one day...
        pass

    def render_equippable(self, console) -> None:
        slot_text = "SLOT(S): "
        console.print(x=self.x, y=self.y, text=slot_text, fg=self.palette.mid_light)
        console.print(
            x=self.x + len(slot_text),
            y=self.y,
            text=self.slot_info,
            fg=self.palette.light,
        )
        self.y += 2

        if self.equipment_tags is not None:
            tag_text = "TAGS: "
            console.print(x=self.x, y=self.y, text=tag_text, fg=self.palette.mid_light)
            console.print(
                x=self.x + len(tag_text),
                y=self.y,
                text=self.equipment_tags,
                fg=self.palette.light,
            )
            self.y += 2
        self.y += 2

        if self.weapon_info is not None:
            self.weapon_info: list[str]
            console.print(
                x=self.x, y=self.y, text="WEAPON INFO:", fg=self.palette.mid_light
            )
            self.y += 2
            for line in self.weapon_info:
                console.print(x=self.x, y=self.y, text=line, fg=self.palette.light)
                self.y += 2
            self.y += 2

        if self.armor_info is not None:
            self.armor_info: list[str]
            console.print(
                x=self.x, y=self.y, text="ARMOR INFO:", fg=self.palette.mid_light
            )
            self.y += 2
            for line in self.armor_info:
                console.print(x=self.x, y=self.y, text=line, fg=self.palette.light)
                self.y += 2
            self.y += 2

        if self.bonuses is not None:
            self.bonuses: list[str]
            console.print(
                x=self.x, y=self.y, text="BONUSES:", fg=self.palette.mid_light
            )
            self.y += 2
            for bonus in self.bonuses:
                console.print(x=self.x, y=self.y, text=bonus, fg=self.palette.light)
                self.y += 2

    def _handle_key(self, event):
        return super()._handle_key(event)


class CharacterInventoryItemQueryHandler(AskUserEventHandler):
    def __init__(self, engine, parent: CharacterInventoryHandler):
        self.parent = parent
        super().__init__(
            engine,
            self.parent.frame_width - 105,
            self.parent.frame_height - 61,
            "ITEM ACTIONS",
            None,
        )
        self.item = None
        if self.parent.SELECTED_INVENTORY_INDEX is None:
            return

        match self.parent.SELECTED_SUBTAB:
            case 0:
                rows = self.parent.inventory_rows
            case _:
                rows = self.parent.equipment_rows

        self.item = rows[self.parent.SELECTED_INVENTORY_INDEX].item
        self.palette = self.parent.PALETTE

    def on_render(self, console: tcod.console.Console) -> None:
        self.parent.on_render(console)
        if self.item is not None:
            console.draw_frame(
                x=self.x,
                y=self.y,
                width=self.frame_width,
                height=self.frame_height,
                clear=True,
                fg=self.palette.light,
                bg=self.palette.dark,
            )
            console.print(self.text_x, self.y, self.TITLE)
            use_text = ""
            if self.item.consumable:
                use_text = "CONSUME"
            elif self.item.equippable:
                is_equipped = self.engine.player.equipment.item_is_equipped(self.item)
                if is_equipped:
                    use_text = "UNEQUIP"
                else:
                    use_text = "EQUIP"
                if self.item.equippable.is_essence:
                    use_text = "INFUSE"
            console.print(self.text_x, self.text_y, text=f"[E] {use_text}")
            console.print(self.text_x, self.text_y + 2, text="[D] DROP")

    def use_item(self) -> Action:
        item = self.item
        if item.consumable:
            # Return the action for the selected item.
            self.handle_action(item.consumable.get_action(self.engine.player))
            self.parent.regenerate_inventory()
            return self.parent
        elif item.equippable:
            if item.equippable.is_essence:
                self.handle_action(actions.EquipEssenceAction(self.engine.player, item))
                self.parent.regenerate_inventory()
                return self.parent
            self.handle_action(actions.EquipAction(self.engine.player, item))
            self.parent.regenerate_inventory()
            return self.parent
        else:
            return self.parent

    def drop_item(self) -> Action:
        self.handle_action(actions.DropItem(self.engine.player, self.item))
        self.parent.regenerate_inventory()
        return self.parent

    def _handle_key(self, event):
        key = event.sym
        if key == tcod.event.KeySym.ESCAPE:
            return self.parent
        if key == tcod.event.KeySym.E:
            return self.use_item()
        if key == tcod.event.KeySym.D:
            return self.drop_item()
        return super()._handle_key(event)


class CharacterEssenceHandler(CharacterInventoryHandler):
    SUBTABS = ["IMBUED ESSENCES"]
    SELECTED_SUBTAB = 0
    SUBTAB_SPACER = "  "
    SELECTED_INVENTORY_INDEX = None
    SELECTED_INVENTORY_PAGE = 0
    MAX_INVENTORY_PAGE = None
    INVENTORY_ROWS_LENGTH = 26

    def __init__(self, engine):
        super().__init__(
            engine,
        )

        self.SELECTED_TAB = 2
        self.PALETTE = color.menu_essence_palette
        self.SUBTABS = ["IMBUED ESSENCES"]
        self.SELECTED_SUBTAB = 0

        self.item_list = []
        self.inventory_rows: List[InventoryRow] = []
        self.MAX_INVENTORY_PAGE = None
        self.active_inventory_rows: List[InventoryRow] = []
        self.regenerate_inventory()

        self.item_info_handler = CharacterInventoryItemInformationHandler(
            self.engine, self
        )
        self.item_info_handler.parent = self

    def regenerate_inventory(self) -> None:
        self._build_item_list()
        self._build_inventory_rows()
        self.MAX_INVENTORY_PAGE = math.floor(
            len(self.item_list) / self.INVENTORY_ROWS_LENGTH
        )
        self._build_active_inventory_rows()

    def _build_inventory_rows(self) -> List[InventoryRow]:
        rows: List[InventoryRow] = []

        for idx, item in enumerate(self.item_list):
            item: Optional[Item]
            letter = f"LEVEL {idx}: "
            if item:
                name = item.name
            else:
                name = None
            selectable = True
            rows.append(
                InventoryRow(item=item, letter=letter, name=name, selectable=selectable)
            )
        self.inventory_rows = rows

    def _build_item_list(self) -> None:
        self.item_list = self.engine.player.essence.slots

    def move_selection_cursor(self, delta: int) -> None:
        match self.SELECTED_SUBTAB:
            case 0:
                self.move_inventory_cursor(delta)

    def render_inventory(self, console: tcod.console.Console) -> None:

        x = self.text_x
        y = self.text_y + 1

        for idx, item in enumerate(self.active_inventory_rows):
            if not item.letter:
                y += 1
                continue
            selected = idx == self.SELECTED_INVENTORY_INDEX
            fg = self.PALETTE.white if selected else self.PALETTE.mid_light
            name_fg = (
                self.PALETTE.white
                if selected
                else render_functions.get_item_inventory_color(item.item)
            )
            bg = self.PALETTE.mid_dark if selected else None
            letter_starter = f"{item.letter}"
            item_name = f"{item.name}"
            console.print(x=x, y=y, text=letter_starter, fg=fg, bg=bg)
            console.print(
                x=x + len(letter_starter), y=y, text=item_name, fg=name_fg, bg=bg
            )
            y += 2

    def on_render(self, console):
        super().on_render(console)
        match self.SELECTED_SUBTAB:
            case 0:
                self.render_inventory(console)
        self.item_info_handler.on_render(console)

    def _handle_key(self, event):
        key = event.sym
        modifier = event.mod

        # character information screens traversal
        if key == tcod.event.KeySym.LEFT and modifier & (
            tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT
        ):
            # stats screen
            return CharacterStatsHandler(self.engine)
        if key == tcod.event.KeySym.RIGHT and modifier & (
            tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT
        ):
            # skills screen
            pass

        # cursor movement
        elif key == tcod.event.KeySym.UP:
            self.move_selection_cursor(-1)
        elif key == tcod.event.KeySym.DOWN:
            self.move_selection_cursor(1)

        return super()._handle_key(event)


class LevelUpEventHandler(AskUserEventHandler):

    def __init__(self, engine):
        TITLE = "LEVEL UP"
        QUESTION = "You have leveled up! Select an attribute to increase."
        frame_height = 25

        super().__init__(
            engine,
            frame_width=None,
            frame_height=frame_height,
            title=TITLE,
            question=QUESTION,
        )

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        console.draw_frame(
            x=self.x,
            y=self.y,
            width=self.frame_width,
            height=self.frame_height,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )
        console.print(self.title_x, self.y, self.TITLE)

        console.print(x=self.text_x, y=self.text_y, text=self.QUESTION)

        console.print(
            x=self.text_x,
            y=self.text_y + 1,
            text=f"1) Strength ({round_for_display(self.engine.player.fighter.stats.strength.value)} -> {round_for_display(self.engine.player.fighter.stats.strength.preview_value)})",
        )
        console.print(
            x=self.text_x,
            y=self.text_y + 2,
            text=f"2) Dexterity ({round_for_display(self.engine.player.fighter.stats.dexterity.value)} -> {round_for_display(self.engine.player.fighter.stats.dexterity.preview_value)})",
        )
        console.print(
            x=self.text_x,
            y=self.text_y + 3,
            text=f"3) Constitution ({round_for_display(self.engine.player.fighter.stats.constitution.value)} -> {round_for_display(self.engine.player.fighter.stats.constitution.preview_value)})",
        )
        console.print(
            x=self.text_x,
            y=self.text_y + 4,
            text=f"4) Intelligence ({round_for_display(self.engine.player.fighter.stats.intelligence.value)} -> {round_for_display(self.engine.player.fighter.stats.intelligence.preview_value)})",
        )
        console.print(
            x=self.text_x,
            y=self.text_y + 5,
            text=f"5) Cunning ({round_for_display(self.engine.player.fighter.stats.cunning.value)} -> {round_for_display(self.engine.player.fighter.stats.cunning.preview_value)})",
        )
        console.print(
            x=self.text_x,
            y=self.text_y + 6,
            text=f"6) Willpower ({round_for_display(self.engine.player.fighter.stats.willpower.value)} -> {round_for_display(self.engine.player.fighter.stats.willpower.preview_value)})",
        )

    def _handle_key(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym

        if key == tcod.event.KeySym.N1:
            player.level.increase_stat(StatTypes.STRENGTH)
        elif key == tcod.event.KeySym.N2:
            player.level.increase_stat(StatTypes.DEXTERITY)
        elif key == tcod.event.KeySym.N3:
            player.level.increase_stat(StatTypes.CONSTITUTION)
        elif key == tcod.event.KeySym.N4:
            player.level.increase_stat(StatTypes.INTELLIGENCE)
        elif key == tcod.event.KeySym.N5:
            player.level.increase_stat(StatTypes.CUNNING)
        elif key == tcod.event.KeySym.N6:
            player.level.increase_stat(StatTypes.WILLPOWER)
        else:
            return None
        return MainGameEventHandler(self.engine)


class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item.

    What happens then depends on the subclass.
    """

    def __init__(self, engine: Engine, question: str):
        TITLE = "INVENTORY"
        if len(engine.player.inventory.items) == 0:
            longest_item_name = 0
        else:
            longest_item_name = (
                max(len(item.name) for item in engine.player.inventory.items) + 10
            )
        frame_width = max(len(TITLE) + 4, longest_item_name)
        self.number_of_items_in_inventory = len(engine.player.inventory.items)
        frame_height = max(5, self.number_of_items_in_inventory + 4)
        super().__init__(
            engine,
            frame_width=frame_width,
            frame_height=frame_height,
            title=TITLE,
            question=question,
        )

    def on_render(self, console: tcod.console.Console) -> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        Will move to a different position based on where the player is located, so the player can always see where
        they are.
        """
        super().on_render(console)

        console.draw_frame(
            x=self.x,
            y=self.y,
            width=self.frame_width,
            height=self.frame_height,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )
        console.print(self.title_x, self.y, self.TITLE)

        if self.number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                is_equipped = self.engine.player.equipment.item_is_equipped(item)

                item_string = f"({item_key}) {item.name}"

                if is_equipped:
                    item_string = f"{item_string} (E)"

                console.print(self.text_x, self.text_y + i, item_string)
        else:
            console.print(self.text_x, self.text_y, "(Empty)")

    def _handle_key(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.A

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super()._handle_key(event)

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Called when the user selects a valid item."""
        raise NotImplementedError()


class InventoryActivateHandler(InventoryEventHandler):
    """Handle using an inventory item."""

    def __init__(self, engine):
        QUESTION = "Select an item to use"
        super().__init__(engine, question=QUESTION)

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Return the action for the selected item."""
        if item.consumable:
            # Return the action for the selected item.
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            if item.equippable.is_essence:
                return actions.EquipEssenceAction(self.engine.player, item)
            return actions.EquipAction(self.engine.player, item)
        else:
            return None


class InventoryDropHandler(InventoryEventHandler):
    """Handle dropping an inventory item."""

    def __init__(self, engine):
        QUESTION = "Select an item to drop"
        super().__init__(engine, question=QUESTION)

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Drop this item."""
        return actions.DropItem(self.engine.player, item)


class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine, frame_width=None, frame_height=None)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.rgb["bg"][x, y] = color.white
        console.rgb["fg"][x, y] = color.black

    def _handle_key(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1  # Holding modifier keys will speed up key movement.
            if event.mod & (tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.Modifier.LCTRL | tcod.event.Modifier.RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.Modifier.LALT | tcod.event.Modifier.RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            # Clamp the cursor index to the map size.
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        if key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super()._handle_key(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """Called when an index is selected."""
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""

    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler."""
        return MainGameEventHandler(self.engine)


class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""

    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""

    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        x, y = self.engine.mouse_location

        # Draw a rectangle around the targeted area, so the player can see the affected tiles.
        console.draw_frame(
            x=x - self.radius - 1,
            y=y - self.radius - 1,
            width=self.radius**2,
            height=self.radius**2,
            fg=color.red,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))


class MainGameEventHandler(EventHandler):

    def _handle_key(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None

        key = event.sym
        modifier = event.mod

        player = self.engine.player

        if key == tcod.event.KeySym.COMMA and modifier & (
            tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT
        ):
            return actions.TakeStairsAction(player)
        if key == tcod.event.KeySym.S and modifier & (
            tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT
        ):
            return QueryRestLoopHandler(self.engine)

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.KeySym.ESCAPE:
            return EscapeMenuEventHandler(self.engine)
        elif key == tcod.event.KeySym.V:
            return HistoryViewer(self.engine)
        elif key == tcod.event.KeySym.G:
            action = PickupAction(player)
        elif key == tcod.event.KeySym.I:
            return CharacterInventoryHandler(self.engine)
        elif key == tcod.event.KeySym.L:
            return LookHandler(self.engine)
        elif key == tcod.event.KeySym.TAB:
            return CharacterScreenEventHandler(self.engine)
        elif key == tcod.event.KeySym.O:
            return CharacterStatsHandler(self.engine)
        elif key == tcod.event.KeySym.K:
            return CharacterEssenceHandler(self.engine)
        return action


class GameOverEventHandler(EventHandler):

    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        save_path = Path("savegame.sav")
        if save_path.exists():
            save_path.unlink()  # Deletes the active save file.
        raise exceptions.QuitWithoutSaving()  # Avoid saving a finished game.

    def _handle_quit(self) -> None:
        self.on_quit()

    def _handle_key(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        if key == tcod.event.KeySym.ESCAPE:
            self.on_quit()

        # No valid key was pressed
        return action


class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.

        log_console = tcod.console.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print(
            x=0,
            y=0,
            width=log_console.width,
            height=1,
            text="┤Message history├",
            alignment=tcod.libtcodpy.CENTER,
        )

        # Render the message log using the cursor parameter.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def _handle_key(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        elif event.sym == tcod.event.KeySym.ESCAPE:
            return MainGameEventHandler(self.engine)
        return None
