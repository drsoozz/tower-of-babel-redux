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
menu_essence_tab_fg = (57, 237, 237)
menu_essence_tab_bg = (20, 40, 40)
menu_inventory_tab_fg = (237, 87, 57)
menu_inventory_tab_bg = (40, 20, 40)

# stats menu stuff
menu_stats_palette = Palette(
    pitch=(4, 0, 5),
    dark=(13, 0, 16),
    mid_dark=(59, 14, 67),
    mid=(101, 46, 111),
    mid_light=(156, 111, 164),
    light=(236, 208, 240),
)

menu_stats_tab_fg = (210, 57, 237)
menu_stats_tab_bg = (40, 40, 20)
menu_stats_subtab_fg = (156, 43, 178)
menu_stats_subtab_bg = (30, 30, 15)

menu_skills_tab_fg = (237, 201, 57)
menu_skills_tab_bg = (30, 30, 30)

menu_unselected_fg = (160, 160, 160)
menu_selected_text = (237, 57, 57)
