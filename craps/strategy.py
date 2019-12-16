from typing import List
from craps.action import Action, Bet, DoNothing
from craps.constants import POINT, COME_OUT


class Strategy():
    def next_actions(self, game, player) -> List[Action]:
        pass

    def __str__(self) -> str:
        return f"{type(self).__name__}"


class PassBet(Strategy):
    def _num_come_bets(self, game, player) -> int:
        return sum([f.get(player) > 0 for f in game.point_num_fields()])

    def next_actions(self, game, player) -> List[Action]:
        if game.phase is COME_OUT and game.is_empty("PASS_LINE", player):
            return [Bet("PASS_LINE", game.MIN_BET)]
        elif game.phase is POINT:
            return [DoNothing()]
        return [DoNothing()]


class PassComeBet(Strategy):
    def _num_come_bets(self, game, player) -> int:
        return sum([f.get(player) > 0 for f in game.point_num_fields()])

    def next_actions(self, game, player) -> List[Action]:
        if game.phase is COME_OUT and game.is_empty("PASS_LINE", player):
            return [Bet("PASS_LINE", game.MIN_BET)]
        elif game.phase is POINT:
            if game.is_empty("COME",
                             player) and self._num_come_bets(game, player) < 2:
                return [Bet("COME", game.MIN_BET)]
        return [DoNothing()]


class PassComeOdds(Strategy):
    def _num_come_bets(self, game, player) -> int:
        return sum([f.get(player) > 0 for f in game.point_num_fields()])

    def _come_bet_fields(self, game, player) -> List["Field"]:
        return [f for f in game.point_num_fields() if f.get(player) > 0]

    def _bet_come_odds(self, game, player) -> List[Action]:
        actions: List[Action] = []
        for come_field in self._come_bet_fields(game, player):
            odds_field: "OddsField" = game.fields[f"{come_field.name}_ODDS"]
            if not odds_field.get(player) > 0:
                bet_amt = game.MIN_BET * odds_field.max_odds
                actions.append(Bet(odds_field.name, bet_amt))
        return actions

    def _bet_pass_odds(self, game, player) -> List[Action]:
        actions: List[Action] = []
        if game.fields["PASS_ODDS"].get(player) > 0:
            return actions
        point_field = game.current_point_field()
        multiplier = game.fields[f"{point_field.name}_ODDS"].max_odds
        return [Bet("PASS_ODDS", game.MIN_BET * multiplier)]

    def next_actions(self, game, player) -> List[Action]:
        actions: List[Action] = []
        if game.phase is COME_OUT:
            if game.is_empty("PASS_LINE", player):
                actions.append(Bet("PASS_LINE", game.MIN_BET))
            actions += self._bet_come_odds(game, player)
            return actions
        elif game.phase is POINT:
            actions += self._bet_pass_odds(game, player)
            actions += self._bet_come_odds(game, player)
            if game.is_empty("COME",
                             player) and self._num_come_bets(game, player) < 2:
                actions.append(Bet("COME", game.MIN_BET))
            return actions
        return [DoNothing()]
