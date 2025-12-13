from pathlib import Path

BASE_PATH = Path("src")
TILESET_PATH = Path(BASE_PATH, "tilesets", "Dullard_Exponent_12x12.png")
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 72
MAP_WIDTH = SCREEN_WIDTH
MAP_HEIGHT = int(SCREEN_HEIGHT * 0.9)

# to convert from how initiative is stored to how it is used everywhere else
# it is stored in a weird way to attempt to prevent floating point errors
TRUE_INIT_FACTOR = int(1e4)
# factor to divide by when going from initiative to multiplier to regen value
MAX_INIT = int(1e6)

UPPER_RESIST_CAP = 0.75
