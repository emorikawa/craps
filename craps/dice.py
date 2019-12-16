import random


class Dice():
    def __init__(self) -> None:
        self.roll()

    def roll(self) -> int:
        self.value = random.randint(1, 6)
        return self.value
