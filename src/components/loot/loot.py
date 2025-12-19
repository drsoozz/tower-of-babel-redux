from __future__ import annotations

from typing import TYPE_CHECKING
import random

import consts

from components.base_component import BaseComponent

from components.wallet.currencies import Currency
from components.loot.rarity_types import RarityTypes

if TYPE_CHECKING:
    from entity import Actor, Item


class Loot(BaseComponent):
    parent: Actor

    def __init__(
        self,
        is_player: bool = False,
        monster_rarity: RarityTypes = None,
        monster_tier: int = None,
        monster_essence: Item = None,
        monster_item: Item = None,
    ):
        if not is_player:
            if monster_rarity is None:
                raise ValueError("No given monster rarity!")
            if monster_tier is None:
                raise ValueError("No given monster tier!")
            if monster_essence is None:
                raise ValueError("No given monster essence!")
            if monster_item is None:
                raise ValueError("No given monster item!")

        self.monster_tier = monster_tier
        self.monster_rarity = monster_rarity
        self.essence = monster_essence
        self.item = monster_item

        self._reward_money = 0
        self._reward_money = (
            (
                consts.SOUL_COIN_REWARD_BASE
                + consts.SOUL_COIN_REWARD_LEVEL_FACTOR
                * pow(self.monster_tier, consts.SOUL_COIN_REWARD_LEVEL_EXPONENT)
            )
            if self.monster_tier is not None
            else 0
        )

    @property
    def essence_drop_chance(self) -> float:
        return (
            consts.ESSENCE_RARITY_TABLE[self.monster_rarity]
            if self.monster_rarity is not None
            else 0
        )

    @property
    def item_drop_chance(self) -> float:
        return (
            consts.ITEM_RARITY_TABLE[self.monster_rarity]
            if self.monster_rarity is not None
            else 0
        )

    def _randomize_reward_money(self) -> None:
        # generate number between +-V, where V is the variance of the reward payout
        random_factor = consts.SOUL_COIN_REWARD_VARIANCE * (2 * random.random() - 1)
        self._reward_money = int(self._reward_money * (1 + random_factor))

    @property
    def reward_money(self) -> int:
        return self._reward_money

    def grant_reward_money_to_killer(self, killer: Actor) -> None:
        # dont do this during initialization because world-gen is already going to be painful...
        self._randomize_reward_money()

        wallet = killer.wallet
        wallet.add({Currency.SOUL_COIN: self.reward_money})

    def disperse_loot(self, killer: Actor) -> None:
        # 1. give reward money (guaranteed)
        self.grant_reward_money_to_killer(killer=killer)

        x, y = self.parent.x, self.parent.y

        # 2. check if item dropped
        if random.random() < self.item_drop_chance:
            # 2.a. drop item
            self.item.place(x, y, self.gamemap)

        # 3. check if essence dropped
        if random.random() < self.essence_drop_chance:
            # 3.a. drop essence
            self.essence.place(x, y, self.gamemap)
