from typing import Dict
from pathlib import Path
import json

import consts

BASE_FLOOR_DATA_PATH = consts.BASE_PATH / Path("procgen") / Path("biomes")


def load_biome_data(biome: str) -> Dict:
    if not isinstance(biome, str):
        raise ValueError(f"given biome is unacceptable: {biome}")
    path = BASE_FLOOR_DATA_PATH / Path(f"{biome}.json")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data
