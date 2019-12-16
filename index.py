import csv
import math
import numpy  # type: ignore
from pprint import pprint
from typing import List, Dict
from collections import defaultdict
from craps.player import Player
from craps.strategy import PassBet, PassComeBet, PassComeOdds
from craps.game import Craps
from craps.coin_control import coin_control
from craps.constants import ROLL_ODDS


def run_strageies_and_save():
    MIN_BET = 10
    WALLET = 1000
    ITERATIONS = 100

    histories: List[List[int]] = [coin_control(WALLET, ITERATIONS, MIN_BET)]

    strategies = [PassBet(), PassComeBet(), PassComeOdds()]

    for strat in strategies:
        print(f"\n\nPlaying: {type(strat).__name__}")
        game = Craps(MIN_BET)
        player = Player(name="Evan", wallet=WALLET, strategy=strat)
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


def _print_histogram(stats):
    stats.sort()
    NUM_BINS = 10
    min_w = int(min(stats))
    max_w = int(max(stats))
    buckets: Dict[int, int] = defaultdict(int)
    for i in range(NUM_BINS):
        buckets[i] = 0
    bucket_size = (max_w - min_w) / NUM_BINS
    for val in stats:
        bin_num = math.floor((val - min_w) / bucket_size)
        buckets[bin_num] += 1

    print(f"Min: {min_w}")
    print(f"P10: {int(round(numpy.percentile(stats, 10)))}")
    print(f"P50: {int(round(numpy.percentile(stats, 50)))}")
    print(f"P90: {int(round(numpy.percentile(stats, 90)))}")
    print(f"Max: {max_w}")
    print(f"Range: {max_w-min_w}")
    print(f"Variance: {numpy.var(stats)}")
    print(f"Stdev: {numpy.std(stats)}")
    bin_nums = list(buckets.keys())
    bin_nums.sort()
    for bin_num in bin_nums:
        num = buckets[bin_num]
        f = int(bin_num * bucket_size + min_w)
        t = int((bin_num + 1) * bucket_size + min_w)
        s = round(num / len(stats) * 30) * "*"
        print(f"{s}\t\t{f}->{t}: {num}")


def histogram_of_endings():
    MIN_BET = 10
    WALLET = 2000
    ITERATIONS = 100

    NUM_TRIALS = 1000
    end_wallets: List[int] = []
    for trial in range(NUM_TRIALS):
        game = Craps(MIN_BET)
        player = Player(name="Evan", wallet=WALLET, strategy=PassComeOdds())
        game.join(player)
        game.start(max_iterations=ITERATIONS)
        end_wallets.append(game.total_player_money())
    _print_histogram(end_wallets)


def how_long_to_live():
    MIN_BET = 10
    WALLET = 1000

    NUM_TRIALS = 100
    num_rolls: List[int] = []
    for trial in range(NUM_TRIALS):
        game = Craps(MIN_BET)
        player = Player(name="Evan", wallet=WALLET, strategy=PassComeOdds())
        game.join(player)
        game.start(max_iterations=None)
        num_rolls.append(game.iteration)
    _print_histogram(num_rolls)


def how_long_to_live_control():
    MIN_BET = 10
    WALLET = 1000

    NUM_TRIALS = 10
    result_histories: List[List[int]] = []
    num_flips: List[int] = []
    for trial in range(NUM_TRIALS):
        results = coin_control(WALLET, None, MIN_BET, bias=0.9)
        result_histories.append(results)
        num_flips.append(len(results))
    _print_histogram(num_flips)

    with open('out_how_long_to_live_control.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        headers = [f"Trial {n+1}" for n in range(NUM_TRIALS)]
        writer.writerow(["Trial Num"] + headers)
        max_result_size = max([len(l) for l in result_histories])
        for i in range(max_result_size):
            row = [i]
            for results in result_histories:
                if i >= len(results):
                    val = 0
                else:
                    val = results[i]
                row.append(val)
            writer.writerow(row)


# https://en.wikipedia.org/wiki/Glossary_of_craps_terms
if __name__ == "__main__":
    # run_strageies_and_save()
    # histogram_of_endings()
    # how_long_to_live()
    how_long_to_live_control()
