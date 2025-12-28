from typing import TYPE_CHECKING, Dict
import random

import numpy as np
import numpy.typing as npt

from chance_picker import chance_picker


def generate_biome_grid(
    biomes: Dict[str, Dict], floor_dimensions: tuple[int, int]
) -> None:

    biome_grid: npt.NDArray = np.full(floor_dimensions, None)

    chances = {}
    for name, bdata in biomes.items():
        chances[name] = {int(k): v for k, v in bdata.get("starting_points").items()}

    # get number of starting points for each biome
    num_starting_points = {}
    for name, chance in chances.items():
        num_starting_points[name] = chance_picker(chance)

    # get floor dimensions
    floor_width, floor_height = biome_grid.shape

    # create biome spawnpoints
    for biome, num_points in num_starting_points.items():
        for _ in range(num_points):
            satisfied = False
            while not satisfied:
                x = random.randint(0, floor_width - 1)
                y = random.randint(0, floor_height - 1)
                if biome_grid[x, y] is None:
                    satisfied = True

            biome_grid[x, y] = biomes[biome]

    # propagate from spawn points until map is full
    satisfied = False
    num_iterations = 0
    while not satisfied:
        num_iterations += 1
        satisfied = True
        for x, y in np.ndindex(floor_width, floor_height):
            if biome_grid[x, y] is not None:
                current_biome = biome_grid[x, y]
                name = current_biome.get("name", "N/A")
                spread = current_biome.get("spread", 0.5)
                north = (x % floor_width, (y - 1) % floor_height)
                east = ((x + 1) % floor_width, y % floor_height)
                south = ((x) % floor_width, (y + 1) % floor_height)
                west = ((x - 1) % floor_width, y % floor_height)
                neighbors = (north, east, south, west)
                for neighbor in neighbors:
                    nx, ny = neighbor
                    if random.random() < spread and biome_grid[nx, ny] is None:
                        biome_grid[nx, ny] = (name, current_biome)
            else:
                satisfied = False

    return biome_grid
