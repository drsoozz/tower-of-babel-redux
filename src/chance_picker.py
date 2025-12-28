from typing import TypeVar, Mapping

import random

T = TypeVar("T")


def chance_picker(chance_dict: Mapping[T, int]) -> T | None:
    if not chance_dict:
        raise ValueError("chance_dict must not be empty")

    if any(weight < 0 for weight in chance_dict.values()):
        raise ValueError("Weights must be non-negative")

    total_weight = sum(chance_dict.values())
    roll = random.randint(1, total_weight)

    cumulative_weight = 0
    for item, weight in chance_dict.items():
        cumulative_weight += weight
        if roll <= cumulative_weight:
            if item == "none":
                return None
            return item

    print("please check chance_picker, it somehow did not produce a valid result...")
    return next(iter(chance_dict))
