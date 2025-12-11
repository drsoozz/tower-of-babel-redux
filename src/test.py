from components.stats.stats import Stats
from components.stats.stat_types import StatTypes
from components.stats.stat_mod_types import StatModType
from components.stats.stat_modifier import StatModifier
from components.stats.character_stat import CharacterStat

"""
constitution = CharacterStat(base_value=5, name="CON")
hp_max = CharacterStat(base_value=50, name="HP_MAX")

print(hp_max.check_if_dirty())
print(hp_max.value)

# hp_max depends on 50% of constitution
hp_max.add_modifier(
    StatModifier(value=constitution, mod_type=StatModType.FLAT, source="TEST")
)

# mark constitution dirty
constitution.add_modifier(
    StatModifier(value=0.5, mod_type=StatModType.PERCENT_ADD, source="ITEM")
)

# hp_max should now see it's dirty via the modifier
print(hp_max.check_if_dirty())  # True
print(hp_max.value)  # recalculates using current constitution.value
print(hp_max.check_if_dirty())  # False

"""
base_stats = {
    StatTypes.STRENGTH: 5,
    StatTypes.DEXTERITY: 5,
    StatTypes.CONSTITUTION: 5,
    StatTypes.INTELLIGENCE: 5,
    StatTypes.CUNNING: 5,
    StatTypes.WILLPOWER: 5,
}

test_stats = Stats(base_stats=base_stats)

random_object = Stats(base_stats=base_stats)  # doesnt matter what it is

print(test_stats.constitution.value)
print(test_stats.hp.max_value)

test_stats.constitution.add_modifier(
    StatModifier(value=0.5, mod_type=StatModType.PERCENT_ADD, source=random_object)
)
print(test_stats.constitution.check_if_dirty())
print(test_stats.hp.max.check_if_dirty())
print(test_stats.constitution.value)
print(test_stats.hp.max.check_if_dirty())

print(test_stats.hp.max_value)
print(test_stats.hp.max.check_if_dirty())

test_stats.constitution.remove_all_from_source(random_object)

print(test_stats.constitution.value)
print(test_stats.hp.max_value)
