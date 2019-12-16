import csv
from pprint import pprint
from typing import List
from craps.player import Player
from craps.strategy import PassBet, PassComeBet, PassComeOdds
from craps.game import Craps
from craps.coin_control import coin_control
from craps.constants import ROLL_ODDS

# https://en.wikipedia.org/wiki/Glossary_of_craps_terms
if __name__ == "__main__":
    MIN_BET = 10
    WALLET = 1000
    ITERATIONS = 100

    histories: List[List[int]] = [coin_control(WALLET, ITERATIONS, MIN_BET)]

    strategies = [PassBet(), PassComeBet(), PassComeOdds()]

    for strat in strategies:
        print(f"\n\nPlaying: {type(strat).__name__}")
        game = Craps(10)
        player = Player(name="Evan", wallet=1000, strategy=strat)
        game.join(player)
        game.start(max_iterations=ITERATIONS)
        histories.append(game.game_history)
        for field_name, stats in game.field_win_lose.items():
            stats['percent'] = round(stats['win'] / stats['lose'] * 100.0, 2)
            print(field_name)
            pprint(dict(stats))
        for val in range(2, 13):
            amount = game.rolls[val]
            percent = amount / ITERATIONS * 100
            diff = percent - (ROLL_ODDS[val] * 100)
            s = f"{round(percent, 2)}% [{amount}] | {round(diff, 2)}% off"
            print(f"Roll {val}: {s}")
        pwin = game.player_win_lose['win']
        ploss = game.player_win_lose['lose']
        print(f"Player won: {pwin}")
        print(f"Player lost: {ploss}")
        print(f"Player net: {pwin - ploss}")

    with open('out.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Trial Num", "Coin Control"] +
                        [type(s).__name__ for s in strategies])
        for i in range(ITERATIONS):
            row = [i] + [history[i] for history in histories]
            writer.writerow(row)
