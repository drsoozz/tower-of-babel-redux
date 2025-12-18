from __future__ import annotations

from pathlib import Path

from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union

import tcod

import actions
from actions import Action, BumpAction, PickupAction, WaitAction
import color
import consts
import exceptions
from components.stats.stat_types import StatTypes
from render_functions import round_for_display

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item
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
            fg=color.white.rgb,
            bg=color.black.rgb,
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
            fg=color.white.rgb,
            bg=color.black.rgb,
            alignment=tcod.libtcodpy.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(["[Y] Yes", "[N] No"]):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text.rgb,
                bg=color.black.rgb,
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
        self, action: Optional[Action], console: tcod.console.Console
    ) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn.
        """
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible.rgb)
            return False  # Skip enemy turn on exceptions.
        for _ in self.engine.handle_enemy_turns():
            self.engine.update_fov()
            self.on_render(console)
        self.engine.update_fov()
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
        if event.sym in {  # Ignore modifier keys.
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,
        }:
            return None
        return self.on_exit()

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
                fg=color.menu_text.rgb,
                bg=color.black.rgb,
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
        return super()._handle_key(event)


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
                self.engine.message_log.add_message("Invalid entry.", color.invalid.rgb)
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
        console.rgb["bg"][x, y] = color.white.rgb
        console.rgb["fg"][x, y] = color.black.rgb

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
            fg=color.red.rgb,
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

        if key == tcod.event.KeySym.I and modifier & (
            tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT
        ):
            return InventoryDropHandler(self.engine)

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
            return InventoryActivateHandler(self.engine)
        elif key == tcod.event.KeySym.L:
            return LookHandler(self.engine)
        elif key == tcod.event.KeySym.TAB:
            return CharacterScreenEventHandler(self.engine)
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
