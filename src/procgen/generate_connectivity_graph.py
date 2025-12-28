import random
import numpy as np
import copy
from procgen.direction_types import DirectionTypes


def generate_connectivity_graph(
    floor_dimensions: tuple[int, int],
    starting_pos: tuple[int, int],
):
    width, height = floor_dimensions

    # each cell gets its own dict (no shared references)
    default = {d: False for d in DirectionTypes}
    grid = np.empty((width, height), dtype=object)
    for x, y in np.ndindex(width, height):
        grid[x, y] = default.copy()

    visited: set[tuple[int, int]] = set()
    stack: list[tuple[int, int]] = [starting_pos]

    while stack:
        x, y = stack[-1]  # ← DO NOT pop yet
        visited.add((x, y))

        # find unvisited neighbors
        neighbors = []
        for direction in DirectionTypes:
            dx, dy = direction.value
            nx, ny = x + dx, y + dy

            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                neighbors.append((direction, nx, ny))

        if neighbors:
            # choose exactly ONE neighbor
            direction, nx, ny = random.choice(neighbors)

            # carve passage
            grid[x, y][direction] = True
            grid[nx, ny][direction.opposite] = True

            # move forward
            stack.append((nx, ny))
        else:
            # dead end → backtrack
            stack.pop()

    return grid


def visualize_connectivity_grid(connectivity_grid: np.typing.NDArray) -> str:
    char_map = {
        (False, False, False, False): " ",
        (True, False, True, False): "│",
        (True, False, False, False): "│",
        (False, False, True, False): "│",
        (False, True, False, True): "─",
        (False, True, False, False): "─",
        (False, False, False, True): "─",
        (False, True, True, False): "┌",
        (False, False, True, True): "┐",
        (True, True, False, False): "└",
        (True, False, False, True): "┘",
        (True, True, True, False): "├",
        (True, False, True, True): "┤",
        (False, True, True, True): "┬",
        (True, True, False, True): "┴",
        (True, True, True, True): "┼",
    }

    width, height = connectivity_grid.shape
    lines = []

    for y in range(height):
        row = []
        for x in range(width):
            cell = connectivity_grid[x, y]
            key = (
                cell[DirectionTypes.NORTH],
                cell[DirectionTypes.EAST],
                cell[DirectionTypes.SOUTH],
                cell[DirectionTypes.WEST],
            )
            row.append(char_map.get(key, "?"))
            if char_map.get(key, "?") == "?":
                print(key)
        lines.append("".join(row))

    return "\n".join(lines)
