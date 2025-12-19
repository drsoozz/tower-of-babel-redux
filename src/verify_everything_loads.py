from pathlib import Path

import consts
from load_entity import load_entity

BASE_DATA_PATH = consts.BASE_PATH / Path("entity_data")


def test_load_all_entities():
    failed = []
    for entity_file in BASE_DATA_PATH.glob("*.json"):
        entity_name = entity_file.stem  # removes extension
        try:
            load_entity(entity_name)
        except Exception as e:
            failed.append((entity_name, str(e)))

    if failed:
        print("Failed to load the following entities:")
        for name, error in failed:
            print(f"{name}: {error}")
    else:
        print("All entities loaded successfully!")


if __name__ == "__main__":
    test_load_all_entities()
