from __future__ import annotations

import heapq
from typing import TYPE_CHECKING, Iterable, Iterator, Optional, List, Tuple, Dict, 
import threading
import queue


import numpy as np
import numpy.typing as npt
from tcod.console import Console

import consts
from entity import Actor, Item
import tile_types
from procgen.load_floor_data import load_floor_data
from procgen.generate_floor import generate_floor
from procgen.direction_types import DirectionTypes

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:

    def __init__(
        self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player can currently see
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player has seen before

        self.upstairs_location = (0, 0)

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def sorted_actors_by_initiative(self) -> List[Actor]:
        return sorted(
            self.actors,
            key=lambda actor: consts.MAX_INIT
            - actor.fighter.stats.initiative.initiative.value,
            reverse=False,
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(
        self,
        location_x: int,
        location_y: int,
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(x=entity.x, y=entity.y, text=entity.char, fg=entity.color)


class GameFloor:

    def __init__(
        self,
        parent: GameWorld,
        floor_dimensions: Tuple[int, int],
        biome_grid: npt.NDArray,
        connectivity_grid: npt.NDArray,
        player_location: Tuple[int, int],
        portal_location: Tuple[int, int],
    ):
        # parent stuff
        self.parent = parent
        self.engine = self.parent.engine
        self.map_width = self.parent.map_width
        self.map_height = self.parent.map_height
        self.current_floor = self.parent.current_floor

        self.floor_dimensions = floor_dimensions
        self.floor_width, self.floor_height = self.floor_dimensions
        self.biome_grid = biome_grid
        self.connectivity_grid = connectivity_grid
        self.player_location = player_location
        self.portal_location = portal_location

        self.floor = np.full(floor_dimensions, None)

        self.x, self.y = self.player_location  # current position

        self.generate_game_map(self.x, self.y)
        initially_loaded = self.get_neighboring_maps
        initially_loaded.append((self.x, self.y))
        for x, y in initially_loaded:
            self.generate_game_map(x, y)

        # generation order
        self._gen_queue: list[tuple[int, tuple[int, int]]] = []

        # threading stuff
        self._request_lock = threading.Lock()
        self._ready_queue = queue.Queue()
        self._stop_event = threading.Event()

        self._worker = threading.Thread(target=self._generation_worker, daemon=True)
        self._worker.start()

    def request_nearby_maps(self, radius: int = 99) -> None:
        px, py = self.player_location

        with self._request_lock:
            for x in range(self.floor_width):
                for y in range(self.floor_height):
                    if self.floor[x, y] is not None:
                        continue

                    d = abs(x - px) + abs(y - py)
                    if d <= radius:
                        heapq.heappush(self._gen_queue, (d, (x, y)))

    def _generation_worker(self) -> None:
        while not self._stop_event.is_set():
            with self._request_lock:
                if not self._gen_queue:
                    continue
                _, (x, y) = heapq.heappop(self._gen_queue)

            # Double-check after popping
            if self.floor[x, y] is not None:
                continue

            gamemap = self._build_game_map_data(x, y)

            self._ready_queue.put((x, y, gamemap))

    def process_ready_maps(self) -> None:
        while not self._ready_queue.empty():
            x, y, gamemap = self._ready_queue.get()
            self.floor[x, y] = gamemap

    @property
    def get_neighboring_maps(self) -> list[tuple[int, int]]:
        north = self.x, self.y - 1
        east = self.x + 1, self.y
        south = self.x, self.y + 1
        west = self.x - 1, self.y
        directions = [north, east, south, west]
        neighbors = []
        for d in directions:
            x, y = d
            if 0 <= x < self.floor_width - 1 and 0 <= y < self.floor_height:
                neighbors.append(d)
        return neighbors

    def _build_game_map_data(self, x: int, y: int) -> GameMap:
        # heavy procgen, NO engine side effects
        biome = self.biome_grid[x, y]
        connectivity: Dict[DirectionTypes, tuple[int, int]] = self.connectivity_grid[x, y]

    def generate_game_map(self, x: int, y: int) -> None:
        # synchronous, main-thread safe
        gamemap = self._build_game_map_data(x, y)
        self.floor[x, y] = gamemap


class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        current_floor: int = 1,
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor
        self.game_floor: GameFloor = None

    def generate_floor(self) -> None:
        floor_args = generate_floor(self.current_floor)
        floor_args["parent"] = self
        self.game_floor = GameFloor(**floor_args)
