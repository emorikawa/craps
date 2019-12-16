# import csv
# from pprint import pprint
from craps.player import Player
# from craps.strategy import PassBet, PassComeBet, PassComeOdds
from craps.strategy import PassComeOdds
from craps.game import Craps

# https://en.wikipedia.org/wiki/Glossary_of_craps_terms
if __name__ == "__main__":
    MIN_BET = 10
    histories = []
    # for strat in [PassBet(), PassComeBet()]:
    for strat in [PassComeOdds()]:
        print(f"\n\nPlaying: {type(strat).__name__}")
        game = Craps(10)
        player = Player(name="Evan", wallet=1000, strategy=strat)
        game.join(player)
        game.start(max_iterations=20)
        histories.append(game.game_history)
        # for field_name, stats in game.win_lose.items():
        #     stats['percent'] = round(stats['win'] / stats['lose'] * 100.0, 2)
        #     print(field_name)
        #     pprint(dict(stats))

    # with open('out.csv', 'w') as csvfile:
    #     writer = csv.writer(csvfile)
    #     for i in range(len(histories[0])):
    #         writer.writerow([i, histories[0][i][1], histories[1][i][1]])
