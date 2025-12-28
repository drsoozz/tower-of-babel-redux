from typing import Dict
from pathlib import Path
import json

import consts

BASE_FLOOR_DATA_PATH = consts.BASE_PATH / Path("procgen") / Path("floors")


def load_floor_data(current_floor: int) -> Dict:
    if not isinstance(current_floor, int):
        raise ValueError(f"given current_floor is unacceptable: {current_floor}")
    current_floor = str(current_floor) if current_floor >= 0 else f"n{-current_floor}"
    path = BASE_FLOOR_DATA_PATH / Path(f"{current_floor}.json")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data
