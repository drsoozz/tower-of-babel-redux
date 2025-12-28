from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional

import numpy as np
import numpy.typing as npt

from procgen.load_floor_data import load_floor_data
from procgen.load_biome_data import load_biome_data
from procgen.generate_biome_grid import generate_biome_grid
from procgen.generate_active_biomes import generate_active_biomes
from procgen.generate_player_portal_locations import generate_player_portal_locations
from procgen.generate_connectivity_graph import (
    generate_connectivity_graph,
    visualize_connectivity_grid,
)

from procgen.direction_types import DirectionTypes

if TYPE_CHECKING:
    from game_map import GameWorld, GameFloor
    from engine import Engine


def generate_floor(current_floor: int) -> GameFloor:
    floor_data = load_floor_data(current_floor)

    # load floor data
    floor_width: Optional[int] = floor_data.get("floor_width", None)
    floor_height: Optional[int] = floor_data.get("floor_height", None)
    floor_dimensions = (floor_width, floor_height)

    # verify floor data
    for fd in floor_dimensions:
        if fd is None or not isinstance(fd, int) or fd < 1:
            fd_name = "floor_width" if fd == floor_dimensions[0] else "floor_height"
            raise ValueError(f"given {fd_name} is unacceptable: {fd}")

    num_biomes: Optional[int] = floor_data.get("num_biomes", None)
    if num_biomes is None or not isinstance(num_biomes, int) or num_biomes < 1:
        raise ValueError(f"given num_biomes is unacceptable: {num_biomes}")

    _biomes = floor_data.get("biomes", None)
    if _biomes is None:
        raise ValueError(f"given biomes list is unacceptable: {_biomes}")

    # create list of ALL biomes
    biomes = {}
    for biome in _biomes:
        biomes[biome] = load_biome_data(biome)

    # whittle down list to only "active" biomes (biomes that will be used)
    biomes: Dict[str, Dict] = generate_active_biomes(num_biomes, biomes)

    # create biome_grid, which is an n x m grid that contains the name and data for a biome at a spot
    biome_grid = generate_biome_grid(biomes, floor_dimensions)

    # player and portal locations never occupy the same place
    player_location, portal_location = generate_player_portal_locations(
        floor_dimensions
    )

    connectivity_grid = generate_connectivity_graph(floor_dimensions, player_location)

    floor_args = {
        "floor_dimensions": floor_dimensions,
        "biome_grid": biome_grid,
        "connectivity_grid": connectivity_grid,
        "player_location": player_location,
        "portal_location": portal_location,
    }

    return floor_args
