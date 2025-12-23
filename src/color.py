from dataclasses import dataclass


# currently unused
@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

    @property
    def rgb(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)


@dataclass(frozen=True)
class Palette:
    pitch: tuple[int, int, int]  # dark divided by 3
    dark: tuple[int, int, int]
    mid_dark: tuple[int, int, int]
    mid: tuple[int, int, int]
    mid_light: tuple[int, int, int]
    light: tuple[int, int, int]
    unselected: tuple[int, int, int] = (160, 160, 160)
    white: tuple[int, int, int] = (0xFF, 0xFF, 0xFF)


white = (0xFF, 0xFF, 0xFF)
black = (0x00, 0x00, 0x00)
red = (0xFF, 0x00, 0x00)

player_atk = (0xE0, 0xE0, 0xE0)
enemy_atk = (0xFF, 0xC0, 0xC0)
needs_target = (0x3F, 0xFF, 0xFF)
status_effect_applied = (0x3F, 0xFF, 0x3F)
ascend = (0x9F, 0x3F, 0xFF)

player_die = (0xFF, 0x30, 0x30)
enemy_die = (0xFF, 0xA0, 0x30)

invalid = (0xFF, 0xFF, 0x00)
impossible = (0x80, 0x80, 0x80)
error = (0xFF, 0x40, 0x40)

welcome_text = (0x20, 0xA0, 0xFF)
health_recovered = (0x00, 0xFF, 0x00)

bar_text = white
bar_filled = (0x00, 0x60, 0x00)
bar_empty = (0x40, 0x10, 0x10)

bar_hp = (0xC9, 0x00, 0x00)
bar_hp_text = (0xFF, 0xCE, 0xCE)
bar_hp_empty = (0x22, 0x00, 0x00)

bar_shield = (0x00, 0x5A, 0x7D)
bar_shield_text = (0xCE, 0xF1, 0xFF)

bar_overlap_hp_shield = (0x62, 0x00, 0x85)
bar_overlap_hp_shield_text = (0xF2, 0xCE, 0xFF)

bar_mana = (0x21, 0x00, 0x8A)
bar_mana_text = (0xDD, 0xD3, 0xFF)
bar_mana_empty = (0x05, 0x00, 0x17)

bar_energy = (0xC9, 0xA7, 0x00)
bar_energy_text = (0xFF, 0xF7, 0xCE)
bar_energy_empty = (0x22, 0x1C, 0x00)

bar_initiative = (0x00, 0xA0, 0x00)
bar_initiative_text = (0xCD, 0xFF, 0xCD)
bar_initiative_empty = (0x00, 0x1B, 0x00)


menu_title = (255, 255, 63)
menu_text = white

# stats menu stuff
menu_inventory_palette = Palette(
    pitch=(4, 0, 5),
    dark=(13, 0, 16),
    mid_dark=(59, 14, 67),
    mid=(101, 46, 111),
    mid_light=(156, 111, 164),
    light=(236, 208, 240),
)

menu_stats_palette = Palette(
    pitch=(8, 0, 1),
    dark=(23, 0, 1),
    mid_dark=(101, 19, 21),
    mid=(167, 67, 70),
    mid_light=(247, 165, 167),
    light=(255, 220, 221),
)

menu_essence_palette = Palette(
    pitch=(1, 0, 15),
    dark=(3, 2, 16),
    mid_dark=(27, 21, 71),
    mid=(64, 56, 117),
    mid_light=(129, 123, 173),
    light=(217, 213, 242),
)

menu_skill_palette = Palette(
    pitch=(6, 8, 0),
    dark=(20, 23, 0),
    mid_dark=(90, 100, 19),
    mid=(153, 164, 66),
    mid_light=(234, 243, 163),
    light=(250, 254, 219),
)

menu_unselected_fg = (160, 160, 160)
