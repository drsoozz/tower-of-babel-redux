from load_entity import load_entity

from entity import Item, Actor

a = load_entity("goblin_shiv")
a: Item

b = load_entity("leather_chestplate")
b: Item

c = load_entity("troll_blood_pendant")
c: Item

d = load_entity("goblin_warrior")
d: Actor
print(d.fighter.stats.attack)
