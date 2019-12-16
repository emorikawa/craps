from typing import List
from craps.action import Action
from craps.strategy import Strategy


class OutOfMoney(Exception):
    pass


class Player():
    def __init__(self, name: str, wallet: int, strategy: Strategy):
        self.name = name
        self.wallet = wallet
        self.strategy = strategy

    def __str__(self) -> str:
        return f"{self.name} [{self.wallet}] playing {self.strategy}"

    def next_actions(self, game) -> List[Action]:
        return self.strategy.next_actions(game, self)

    def add(self, amount: int) -> None:
        self.wallet += amount

    def deduct(self, amount) -> int:
        self.wallet -= amount
        # if self.wallet < 0:
        #     raise OutOfMoney()
        return self.wallet
