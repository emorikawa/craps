from typing import List, Optional
import random


def coin_control(wallet: int,
                 iterations: Optional[int],
                 min_bet: int,
                 bias: int = 1) -> List[int]:
    results: List[int] = []
    cond = True
    i = 0
    while cond:
        if iterations is None:
            assert bias < 1, "This will never end if bias >= 1"
            cond = wallet > 0
        else:
            cond = i < iterations
        val = random.randint(0, 1)
        if val == 1:
            wallet += min_bet * bias
        else:
            wallet -= min_bet
        results.append(wallet)
        i += 1
    return results
