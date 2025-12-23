from __future__ import annotations

from typing import TYPE_CHECKING
import math

import color

if TYPE_CHECKING:
    from tcod.console import Console
    from engine import Engine
    from game_map import GameMap


def render_gui_frame(console: Console, y: int) -> None:
    console.draw_frame(-1, y, console.width + 2, console.height + 1)


def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )
    return names.capitalize()


def render_bar(
    console: Console,
    current_value: float,
    maximum_value: float,
    bar_empty: color.Color,
    bar_filled: color.Color,
    bar_text: color.Color,
    bar_title: str,
    x: int = 0,
    y: int = 0,
    total_width: int = 15,
) -> None:

    bar_x = x + 5
    bar_y = y
    bar_text_x = bar_x + 1
    bar_text_y = bar_y

    console.print(x=x, y=y, text=bar_title)

    bar_width = int(current_value / maximum_value * total_width)

    console.draw_rect(x=bar_x, y=bar_y, width=total_width, height=1, ch=1, bg=bar_empty)

    if bar_width > 0:
        console.draw_rect(
            x=bar_x, y=bar_y, width=bar_width, height=1, ch=1, bg=bar_filled
        )

    console.print(
        x=bar_text_x,
        y=bar_text_y,
        text=f"{round_for_display(current_value)}/{round_for_display(maximum_value)}",
        fg=bar_text,
    )


def render_dungeon_level(console: Console, dungeon_level: int, x: int, y: int) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    shift = len(str(dungeon_level))
    console.print(x=x - shift, y=y, text=f"Floor {dungeon_level}")


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )

    console.print(x=x, y=y, text=names_at_mouse_location)


def render_tabs(
    *,
    console,
    x: int,
    y: int,
    tabs: list[str],
    selected_index: int,
    selected_fg,
    selected_bg,
    unselected_fg,
    spacer: str = "  ",
    marker: bool = True,
) -> None:
    cursor_x = x

    for i, tab in enumerate(tabs):
        if i == selected_index:
            text = f"► {tab} ◄" if marker else tab
            fg = selected_fg
            bg = selected_bg
        else:
            text = tab
            fg = unselected_fg
            bg = None

        console.print(cursor_x, y, text, fg=fg, bg=bg)
        cursor_x += len(text) + len(spacer)


def round_for_display(x: float, sig: int = 3) -> float:
    if x == 0:
        return 0
    return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)


def render_character_information_screens(
    console: Console,
    palette: color.Palette,
    x: int,
    y: int,
    frame_width: int,
    frame_height: int,
    title: str,
    title_x: int,
    tabs_x: int,
    tabs_y: int,
    selected_tab: int,
    subtabs_x: int,
    subtabs_y: int,
    subtabs: list[str],
    selected_subtab: int,
    text_y: int,
    vertical_split: bool = True,  # if false, make a horizontal split line in the middle of the screen, not a vertical one!
    horizontal_split_y: int = None,  # only used if vertical_split is False
) -> None:
    TABS_NAMES = ["INVENTORY [I]", "STATS [O]", "ESSENCES [J]", "SKILLS [K]"]
    console.draw_frame(
        x=x,
        y=y,
        width=frame_width,
        height=frame_height,
        clear=True,
        fg=palette.light,
        bg=palette.dark,
    )

    console.print(title_x, y, title)

    # top-level tabs
    render_tabs(
        console=console,
        x=tabs_x,
        y=tabs_y,
        tabs=TABS_NAMES,
        selected_index=selected_tab,
        selected_fg=palette.white,
        selected_bg=palette.mid,
        unselected_fg=palette.unselected,
    )

    console.print(
        x=x + 2,
        y=tabs_y + 2,
        text="─" * (frame_width - 4),
        fg=palette.mid_light,
    )

    # subtabs
    render_tabs(
        console=console,
        x=subtabs_x,
        y=subtabs_y,
        tabs=subtabs,
        selected_index=selected_subtab,
        selected_fg=palette.white,
        selected_bg=palette.mid,
        unselected_fg=palette.unselected,
    )

    console.print(
        x=x + 3,
        y=subtabs_y + 2,
        text="─" * (frame_width - 6),
        fg=palette.mid,
    )

    console.print(
        x=x + 3,
        y=frame_height - 1,
        text="─" * (frame_width - 6),
        fg=palette.mid,
    )

    if vertical_split:
        for i in range(frame_height - 13):
            console.print(
                x=(frame_width + x) // 2,
                y=text_y + i,
                text="║",
                fg=palette.mid_dark,
            )
    else:
        console.print(
            x=(x + 3),
            y=horizontal_split_y,
            text="─" * (frame_width - 6),
            fg=palette.mid_dark,
        )
