from __future__ import annotations

from typing import Optional, TYPE_CHECKING, List, Tuple, Dict
import random

import consts
from components.base_component import BaseComponent
from components.equipment_types import EquipmentTypes
from components.items.equippable import EssenceEquippable

from components.wallet.currencies import Currency

from exceptions import NotEnoughMoney

if TYPE_CHECKING:
    from entity import Actor, Item


class Wallet(BaseComponent):
    parent: Actor

    def __init__(
        self,
        starting_balance: Optional[Dict[Currency, int]] = None,
    ):
        self._balances: Dict[Currency, int] = (
            dict(starting_balance)
            if starting_balance
            else {
                Currency.SOUL_COIN: 0,
                Currency.SPIRIT_ASH: 0,
            }
        )

    # ---------- Queries ----------

    def balance(self, currency: Currency) -> int:
        return self._balances.get(currency, 0)

    def can_afford(self, amount: Dict[Currency, int]) -> bool:
        return all(
            self.balance(currency) >= amount for currency, amount in amount.items()
        )

    # ---------- Mutation ----------

    def spend(self, amount: Dict[Currency, int], add_message: bool = True) -> None:
        for ctype, cval in amount.items():
            if cval < 0:
                raise ValueError("Cannot spend a negative amount")

        if not self.can_afford(amount):
            raise NotEnoughMoney(f"Not enough money to cover {amount}")

        for ctype, cval in amount.items():
            self._balances[ctype] -= cval

        if add_message:
            self.spend_message(amount=amount)

    def add(self, amount: Dict[Currency, int], add_message: bool = True) -> None:

        for ctype, cval in amount.items():
            if cval < 0:
                raise ValueError("Cannot add a negative amount")

        for ctype, cval in amount.items():
            self._balances[ctype] += cval

        if add_message:
            self.add_message(amount=amount)

    # ---------- Messages ----------
    def add_message(self, amount: Dict[Currency, int]) -> None:
        for ctype, cval in amount.items():
            self.parent.gamemap.engine.message_log.add_message(
                f"You have received {cval} {ctype.value.upper()}."
            )

    def spend_message(self, amount: Dict[Currency, int]) -> None:
        for ctype, cval in amount.items():
            self.parent.gamemap.engine.message_log.add_message(
                f"You have spent {cval} {ctype.value.upper()}."
            )
