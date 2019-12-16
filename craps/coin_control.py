from typing import List
import random


def coin_control(wallet: int, iterations: int,
                 min_bet: int) -> List[int]:
    results: List[int] = []
    for i in range(iterations):
        val = random.randint(0, 1)
        if val == 1:
            wallet += min_bet
        else:
            wallet -= min_bet
        results.append(wallet)
    return results
