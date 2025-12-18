from components.ai import HostileEnemy
from components import consumable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.items import equippable
from components.level import Level
from entity import Actor, Item

from components.stats.stat_types import StatTypes

player_stats = {
    StatTypes.STRENGTH: 10,
    StatTypes.DEXTERITY: 10,
    StatTypes.CONSTITUTION: 10,
    StatTypes.INTELLIGENCE: 10,
    StatTypes.CUNNING: 10,
    StatTypes.WILLPOWER: 10,
}

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(
        base_stats=player_stats,
        damage_resists=None,
        damage_amps=None,
        damage_masteries=None,
    ),
    inventory=Inventory(capacity=26),
    level=Level(),
)

orc_stats = {
    StatTypes.STRENGTH: 3,
    StatTypes.DEXTERITY: 2,
    StatTypes.CONSTITUTION: 4,
    StatTypes.INTELLIGENCE: 1,
    StatTypes.CUNNING: 1,
    StatTypes.WILLPOWER: 1,
}

orc = Actor(
    char="o",
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(
        base_stats=orc_stats,
        damage_resists=None,
        damage_amps=None,
        damage_masteries=None,
    ),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
)

troll_stats = {
    StatTypes.STRENGTH: 15,
    StatTypes.DEXTERITY: 3,
    StatTypes.CONSTITUTION: 25,
    StatTypes.INTELLIGENCE: 1,
    StatTypes.CUNNING: 1,
    StatTypes.WILLPOWER: 1,
}


troll = Actor(
    char="T",
    color=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(
        base_stats=troll_stats,
        damage_resists=None,
        damage_amps=None,
        damage_masteries=None,
    ),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
)


confusion_scroll = Item(
    char="!",
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)


fireball_scroll = Item(
    char="!",
    color=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
)

health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4),
)

lightning_scroll = Item(
    char="!",
    color=(255, 255, 0),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)

great_hammer = Item(
    char="!",
    color=(255, 255, 255),
    name="Greathammer",
    equippable=equippable.GreatHammer(),
)

"""

dagger = Item(
    char="/", color=(0, 191, 255), name="Dagger", equippable=equippable.Dagger()
)

sword = Item(char="/", color=(0, 191, 255), name="Sword", equippable=equippable.Sword())

leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    char="[", color=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail()
)

"""
