from components.ai import HostileEnemy
from components import consumable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.items import equippable
from components.level import Level
from components.essence.essence import Essence
from components.wallet.wallet import Wallet
from components.loot.loot import Loot

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
    essence=Essence(),
    wallet=Wallet(starting_balance=None),
    loot=Loot(is_player=True),
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
    consumable=consumable.HealingPotion(amount=4),
)

lightning_scroll = Item(
    char="!",
    color=(255, 255, 0),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)
