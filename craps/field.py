from typing import Dict
from collections import defaultdict
from craps.player import Player


class Field():
    def __init__(self, name: str):
        self.name = name
        self.values: Dict[Player, int] = defaultdict(int)

    def __str__(self) -> str:
        disp = ""
        for player, amount in self.values.items():
            disp += f"{player.name}: {amount}"
        return f"{self.name}: {disp}"

    def get(self, player: Player) -> int:
        return self.values.get(player, 0)

    def add(self, player: Player, amount: int = 0):
        self.values[player] += amount

    def deduct(self, player: Player):
        amount = self.values.get(player, 0)
        self.values[player] = 0
        return amount


class OddsField(Field):
    def __init__(self, name: str, max_odds: int):
        super().__init__(name)
        self.max_odds = max_odds
