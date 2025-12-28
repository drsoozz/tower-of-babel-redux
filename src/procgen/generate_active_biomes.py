from typing import Dict
import random

from chance_picker import chance_picker


def generate_active_biomes(num_biomes: int, biomes: Dict[str, Dict]) -> Dict:
    current_biomes = 0

    chances = {}
    for name, bdata in biomes.items():
        chances[name] = bdata.get("rarity", 1)

    final_biomes = {}
    while current_biomes < num_biomes:
        # roll from chances dict to find biome to add
        biome_to_be_added = chance_picker(chances)
        biome_data_to_be_added = biomes[biome_to_be_added]

        # add biome
        final_biomes[biome_to_be_added] = biome_data_to_be_added

        # remove biome from chances dict
        del chances[biome_to_be_added]
        current_biomes += 1

    return final_biomes
