import random


def generate_player_portal_locations(
    floor_dimensions: tuple[int, int],
) -> tuple[tuple[int, int], tuple[int, int]]:
    floor_width, floor_height = floor_dimensions
    px, py = random.randint(0, floor_width - 1), random.randint(0, floor_height - 1)
    player_location = (px, py)

    satisfied = False
    portal_location = (None, None)
    while not satisfied:
        px, py = random.randint(0, floor_width - 1), random.randint(0, floor_height - 1)
        if (px, py) != player_location:
            portal_location = (px, py)
            satisfied = True

    return (player_location, portal_location)
