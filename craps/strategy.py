from typing import List
from craps.action import Action, Bet, DoNothing
from craps.constants import POINT, COME_OUT, NUM_TO_FIELD


class Strategy():
    def next_actions(self, game, player) -> List[Action]:
        pass

    def init_strategy(self, game, player) -> None:
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


class ThreePointMolly(Strategy):
    def _num_come_bets(self, game, player) -> int:
        return sum([f.get(player) > 0 for f in game.point_num_fields()])

    def _come_bet_fields(self, game, player) -> List["Field"]:  # type: ignore
        return [f for f in game.point_num_fields() if f.get(player) > 0]

    def _come_odds_fields(self, game, player) -> List["Field"]:  # type: ignore
        return [f for f in game.point_odds_fields() if f.get(player) > 0]

    def _bet_come_odds(self, game, player) -> List[Action]:
        actions: List[Action] = []
        for odds_field in self._come_odds_fields(game, player):
            if not odds_field.get(player) > 0:
                bet_amt = game.MIN_BET * odds_field.max_odds
                actions.append(Bet(odds_field.name, bet_amt))
        return actions

    def _bet_pass_odds(self, game, player) -> List[Action]:
        actions: List[Action] = []
        if game.fields["PASS_ODDS"].get(player) > 0:
            return actions
        point_field_name = NUM_TO_FIELD[game.point]
        multiplier = game.fields[f"{point_field_name}_ODDS"].max_odds
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


class PlaceNumbers(Strategy):
    def next_actions(self, game, player) -> List[Action]:
        if game.phase is COME_OUT and game.is_empty("PASS_LINE", player):
            return [Bet("PASS_LINE", game.MIN_BET)]
        elif game.phase is POINT:
            bets: List[Action] = []
            for field in game.place_num_fields():
                no_bet = f"{NUM_TO_FIELD[game.point]}_PLACE"
                if game.is_empty(field.name, player) and field.name != no_bet:
                    bets.append(Bet(field.name, game.place_bets(field)))
                else:
                    continue
            if game.is_empty("FIELD", player):
                bets.append(Bet("FIELD", game.MIN_BET))
            return bets
        return [DoNothing()]


class FieldBetOnly(Strategy):
    def next_actions(self, game, player) -> List[Action]:
        if game.is_empty("FIELD", player):
            return [Bet("FIELD", game.MIN_BET)]
        return [DoNothing()]


class IronCross(Strategy):
    def init_strategy(self, game, player):
        self.player = player
        self.game = game

    def _bet(self, field_num: int) -> Action:
        field_name = f"{NUM_TO_FIELD[field_num]}_PLACE"
        point_field_name = f"{NUM_TO_FIELD[self.game.point]}_PLACE"
        if self.game.is_empty(field_name,
                              self.player) and point_field_name != field_name:
            return Bet(field_name, self.game.place_bets(field_name))
        return DoNothing()

    def next_actions(self, game, player) -> List[Action]:
        bets: List[Action] = []
        if game.phase is COME_OUT and game.is_empty("PASS_LINE", player):
            player.strategy_state['bet_field'] = False
            if game.is_empty("FIELD", player):
                bets.append(Bet("FIELD", game.MIN_BET))
            bets.append(Bet("PASS_LINE", game.MIN_BET))
            return bets
        elif game.phase is POINT:
            bets.append(self._bet(6))
            bets.append(self._bet(8))
            if game.is_empty("FIELD", player):
                bets.append(Bet("FIELD", game.MIN_BET))
            return bets
        return [DoNothing()]


class ColorUp(Strategy):
    def init_strategy(self, game, player):
        self.player = player
        self.game = game
        self.player.strategy_state['bet_field'] = False

    def _bet(self, field_num: int) -> Action:
        field_name = f"{NUM_TO_FIELD[field_num]}_PLACE"
        point_field_name = f"{NUM_TO_FIELD[self.game.point]}_PLACE"
        if self.game.is_empty(field_name,
                              self.player) and point_field_name != field_name:
            return Bet(field_name, self.game.place_bets(field_name))
        return DoNothing()

    def _is_empty(self, field_nums: List[int]) -> bool:
        point_field_name = f"{NUM_TO_FIELD[self.game.point]}_PLACE"
        return all([
            (self.game.is_empty(f"{NUM_TO_FIELD[n]}_PLACE", self.player)
             or f"{NUM_TO_FIELD[n]}_PLACE" == point_field_name)
            for n in field_nums
        ])

    def next_actions(self, game, player) -> List[Action]:
        if game.phase is COME_OUT and game.is_empty("PASS_LINE", player):
            player.strategy_state['bet_field'] = False
            return [Bet("PASS_LINE", game.MIN_BET)]
        elif game.phase is POINT:
            bets: List[Action] = []
            bets.append(self._bet(6))
            bets.append(self._bet(8))
            if self._is_empty([4, 5, 9, 10]):
                if game.is_empty("FIELD", player):
                    if player.strategy_state['bet_field'] is False:
                        player.strategy_state['bet_field'] = True
                        bets.append(Bet("FIELD", game.MIN_BET))
                    else:
                        bets.append(self._bet(5))
            elif self._is_empty([4, 9, 10]):
                bets.append(self._bet(5))
            elif self._is_empty([4, 10]):
                bets.append(self._bet(8))
            elif self._is_empty([4]):
                bets.append(self._bet(10))
            else:
                bets.append(self._bet(4))
            return bets
        return [DoNothing()]
