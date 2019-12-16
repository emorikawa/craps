from craps.action import Action, Bet, DoNothing
from craps.constants import POINT, COME_OUT


class Strategy():
    def next_action(self, game, player) -> Action:
        pass

    def __str__(self) -> str:
        return f"{type(self).__name__}"


class PassBet(Strategy):
    def _num_points(self, game, player) -> int:
        return sum([f.get(player) > 0 for f in game.point_num_fields()])

    def next_action(self, game, player) -> Action:
        if game.phase is COME_OUT and game.is_empty("PASS_LINE", player):
            return Bet("PASS_LINE", game.MIN_BET)
        elif game.phase is POINT:
            return DoNothing()
        return DoNothing()


class PassComeBet(Strategy):
    def _num_points(self, game, player) -> int:
        return sum([f.get(player) > 0 for f in game.point_num_fields()])

    def next_action(self, game, player) -> Action:
        if game.phase is COME_OUT and game.is_empty("PASS_LINE", player):
            return Bet("PASS_LINE", game.MIN_BET)
        elif game.phase is POINT:
            if game.is_empty("COME",
                             player) and self._num_points(game, player) < 2:
                return Bet("COME", game.MIN_BET)
        return DoNothing()
