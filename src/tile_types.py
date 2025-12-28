from typing import Tuple

import numpy as np

from base_enum import BaseEnum

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),  # Graphics for when the tile is in FOV.
    ]
)


class TileTypes(str, BaseEnum):
    FLOOR = "floor"  # walkable, transparent
    WALL = "wall"  # not walkable, not transparent
    CHASM = "chasm"  # not walkable BUT transparent
    TRICK = "trick"  # walkable but NOT transparent


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    ttype: TileTypes,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types"""
    match ttype:
        case TileTypes.FLOOR:
            return np.array((True, True, dark, light), dtype=tile_dt)
        case TileTypes.WALL:
            return np.array((False, False, dark, light), dtype=tile_dt)
        case TileTypes.CHASM:
            return np.array((False, True, dark, light), dtype=tile_dt)
        case TileTypes.TRICK:
            return np.array((True, False, dark, light), dtype=tile_dt)
        case _:
            raise ValueError("what the fuck")


# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

"""
floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (50, 50, 150)),
    light=(ord(" "), (255, 255, 255), (200, 180, 50)),
)
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord(" "), (255, 255, 255), (0, 0, 100)),
    light=(ord(" "), (255, 255, 255), (130, 110, 50)),
)

up_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("<"), (0, 0, 100), (50, 50, 150)),
    light=(ord("<"), (255, 255, 255), (200, 180, 50)),
)
"""
