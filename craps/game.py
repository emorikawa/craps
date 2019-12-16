from typing import Optional, Dict, List
from collections import defaultdict
from craps.dice import Dice
from craps.field import Field, OddsField, NUM_TO_FIELD
from craps.player import Player
from craps.action import Action, Bet, Move
from craps.constants import POINT, COME_OUT

ODDS_PAYOUT = {
    "FOUR_ODDS": 2,
    "FIVE_ODDS": 3/2,
    "SIX_ODDS": 6/5,
    "EIGHT_ODDS": 6/5,
    "NINE_ODDS": 3/2,
    "TEN_ODDS": 2,
}


class IllegalAction(Exception):
    pass


class Craps():
    def __init__(self, min_bet: int) -> None:
        self.phase: bool = COME_OUT
        self.MIN_BET = min_bet
        self.point: Optional[int] = None
        self.d1 = Dice()
        self.d2 = Dice()
        self.house_wins = 0
        self.house_losses = 0
        self.iteration = 0
        self.players: List[Player] = []
        self.fields: Dict[str, Field] = {
            "PASS_LINE": Field("PASS_LINE"),
            "PASS_ODDS": Field("PASS_ODDS"),
            "COME": Field("COME"),
            "FOUR": Field("FOUR"),
            "FIVE": Field("FIVE"),
            "SIX": Field("SIX"),
            "EIGHT": Field("EIGHT"),
            "NINE": Field("NINE"),
            "TEN": Field("TEN"),
            "FOUR_ODDS": OddsField("FOUR_ODDS", max_odds=3),
            "FIVE_ODDS": OddsField("FIVE_ODDS", max_odds=4),
            "SIX_ODDS": OddsField("SIX_ODDS", max_odds=5),
            "EIGHT_ODDS": OddsField("EIGHT_ODDS", max_odds=5),
            "NINE_ODDS": OddsField("NINE_ODDS", max_odds=4),
            "TEN_ODDS": OddsField("TEN_ODDS", max_odds=3),
        }
        self.game_history: List[int] = []
        self.player_win_lose: Dict[str, int] = defaultdict(int)
        self.field_win_lose: Dict[str, Dict[str, float]] = defaultdict(
            lambda: defaultdict(float))
        self.rolls: Dict[int, int] = defaultdict(int)

    def join(self, player: Player) -> None:
        self.players.append(player)

    def dice(self) -> int:
        return self.d1.value + self.d2.value

    def start(self, max_iterations: int) -> None:
        while self.iteration < max_iterations:
            if self.phase:
                print(f"---> ON: {self.point}")
            else:
                print(f"---> OFF: COMING OUT")
            self._performPlayerActions()
            self._shoot()
            print(f"---> Rolled {self.dice()}")
            self._reconcile()
            self._print_game_status()
            self._record_game_history()
            self.iteration += 1

    def point_num_fields(self) -> List[Field]:
        return [self.fields[f] for f in ["FOUR", "FIVE", "SIX", "EIGHT", "NINE", "TEN"]]  # noqa

    def point_odds_fields(self) -> List[Field]:
        return [self.fields[f"{f}_ODDS"] for f in ["FOUR", "FIVE", "SIX", "EIGHT", "NINE", "TEN"]]  # noqa

    def current_point_field(self) -> Field:
        if self.point is None:
            raise IllegalAction()
        return self.fields[NUM_TO_FIELD[self.point]]

    def is_empty(self, field_name: str, player: Player) -> bool:
        return self.fields[field_name].get(player) == 0

    def _print_game_status(self) -> None:
        for player in self.players:
            print(f"================================")
            come_nums = [str(f.get(player)) for f in self.point_num_fields()]
            come_odds = [str(f.get(player)) for f in self.point_odds_fields()]
            print(f"= {' - '.join(come_nums)}")
            print(f"= {' - '.join(come_odds)}")
            print(f"= ----------------------------")
            print(f"= COME: {self.fields['COME'].get(player)}")
            print(f"= ---------------------------- =")
            pline = self.fields['PASS_LINE'].get(player)
            podds = self.fields['PASS_ODDS'].get(player)
            print(f"= PASS: {pline} | {podds}")
            print(f"= ---------------------------- =")
            print(f"= {player}")
            print(f"= iteration {self.iteration}")
            print(f"================================\n\n")

    def _record_game_history(self) -> None:
        hist = sum([p.wallet for p in self.players])
        self.game_history.append(hist)

    def _shoot(self) -> None:
        self.d1.roll()
        self.d2.roll()
        self.rolls[self.dice()] += 1

    def _performPlayerActions(self) -> None:
        for player in self.players:
            actions = player.next_actions(self)
            for action in actions:
                print(f"---> {player.name} -> {action}")
            for action in actions:
                self._performAction(action, player)

    def _performAction(self, action: Action, player: Player) -> None:
        if isinstance(action, Bet):
            if self.phase is POINT and action.field_name == "PASS_LINE":
                raise IllegalAction()
            player.deduct(action.amount)
            self.fields[action.field_name].add(player, action.amount)
        if isinstance(action, Move):
            amount = self.fields[action.from_field_name].deduct(player)
            self.fields[action.to_field_name].add(player, amount)

    def _assert_before_coming_out(self) -> None:
        m1 = "No bets on COME when coming out"
        assert sum(self.fields["COME"].values.values()) == 0, m1

        m2 = "No bets on PASS_ODDS when coming out"
        assert sum(self.fields["PASS_ODDS"].values.values()) == 0, m2

    def _reconcile(self) -> None:
        dice = self.dice()
        if self.phase is COME_OUT:
            self._assert_before_coming_out()
            if dice in [2, 3, 12]:
                self._crap_out()
            elif dice in [4, 5, 6, 8, 9, 10]:
                self._establish_point(dice)
                self._come_number_win(dice)
                self._come_odds_win(dice)
            elif dice == 11:
                self._natural()
            elif dice == 7:
                self._natural()
                self._come_number_lose()
                self._come_odds_lose()
        elif self.phase is POINT:
            if dice == 7:
                self._come_win()
                self._seven_out()
            elif dice == 11:
                self._come_win()
            elif dice in [2, 3, 12]:
                self._come_lose()
            elif dice in [4, 5, 6, 8, 9, 10]:
                if dice == self.point:
                    self._pass_win()
                    self._pass_odds_win()
                    self._end_turn()
                self._come_number_win(dice)
                self._come_odds_win(dice)
                self._come_point_win(dice)
                self._come_point_move(dice)
            else:
                pass

    def _player_win(self, field_name: str, multiplier: float) -> None:
        self.field_win_lose[field_name]['win'] += 1.0
        for player in self.fields[field_name].values:
            bet = self.fields[field_name].deduct(player)
            if bet == 0:
                break
            win = bet * multiplier
            self.house_losses += win
            print(f"!!!! Player WIN on {field_name}: {bet} bet + {win} win = {bet + win}")  # noqa
            self.player_win_lose['win'] += win
            player.add(bet + win)

    def _player_lose(self, field_name: str) -> None:
        self.field_win_lose[field_name]['lose'] += 1.0
        for player in self.fields[field_name].values:
            amount = self.fields[field_name].get(player)
            if amount > 0:
                print(f"XXXX Player LOSE: {amount} ON {field_name}")
                self.player_win_lose['lose'] += amount
            self.house_wins += self.fields[field_name].deduct(player)

    def _establish_point(self, dice: int) -> None:
        print(f"---> ESTABLISH POINT: {dice}")
        self.phase = POINT
        self.point = dice

    def _seven_out(self) -> None:
        # print("---> SEVEN OUT")
        self.phase = COME_OUT
        self.point = None
        self._player_lose("PASS_LINE")
        self._player_lose("PASS_ODDS")
        self._player_lose("FOUR")
        self._player_lose("FIVE")
        self._player_lose("SIX")
        self._player_lose("EIGHT")
        self._player_lose("NINE")
        self._player_lose("TEN")
        self._player_lose("FOUR_ODDS")
        self._player_lose("FIVE_ODDS")
        self._player_lose("SIX_ODDS")
        self._player_lose("EIGHT_ODDS")
        self._player_lose("NINE_ODDS")
        self._player_lose("TEN_ODDS")

    def _pass_win(self) -> None:
        # print("---> PASS WIN")
        self._player_win("PASS_LINE", 1)

    def _pass_odds_win(self) -> None:
        # print("---> PASS WIN")
        if self.point is None:
            raise IllegalAction()
        odds_field_name = f"{NUM_TO_FIELD[self.point]}_ODDS"
        self._player_win("PASS_ODDS", ODDS_PAYOUT[odds_field_name])

    def _end_turn(self) -> None:
        self.phase = COME_OUT
        self.point = None

    def _come_win(self) -> None:
        # print("---> COME CHECK WINNERS")
        self._player_win("COME", 1)

    def _come_lose(self) -> None:
        # print("---> COME CHECK LOSERS")
        self._player_lose("COME")

    def _come_number_win(self, dice: int) -> None:
        self._player_win(NUM_TO_FIELD[dice], 1)

    def _come_odds_win(self, dice: int) -> None:
        field_name = f"{NUM_TO_FIELD[dice]}_ODDS"
        self._player_win(field_name, ODDS_PAYOUT[field_name])

    def _come_number_lose(self) -> None:
        for f in self.point_num_fields():
            self._player_lose(f.name)

    def _come_odds_lose(self) -> None:
        for f in self.point_odds_fields():
            self._player_lose(f.name)

    def _move_all(self, from_field: str, to_field: str) -> None:
        values = self.fields[from_field].values
        self.fields[from_field].values = defaultdict(int)
        for player, value in values.items():
            if value > 0:
                print(
                    f"==== PLAYER MOVE {value} from {from_field} to {to_field}"
                )
            self.fields[to_field].add(player, value)

    def _come_point_move(self, point: int) -> None:
        # print(f"---> COME POINT MOVE TO {point}")
        self._move_all("COME", NUM_TO_FIELD[point])

    def _come_point_win(self, point: int) -> None:
        # print(f"---> COME POINT {point} CHECK WINNERS")
        self._player_win(NUM_TO_FIELD[point], 1)

    def _natural(self) -> None:
        # print("---> NATURAL!")
        self._player_win("PASS_LINE", 1)

    def _crap_out(self) -> None:
        # print("---> CRAPPED OUT")
        self._player_lose("PASS_LINE")
