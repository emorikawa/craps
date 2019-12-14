import random
from typing import Optional, Dict, List
from collections import defaultdict

# https://en.wikipedia.org/wiki/Glossary_of_craps_terms


class OutOfMoney(Exception):
    pass


class IllegalAction(Exception):
    pass


class Dice():
    def __init__(self) -> None:
        self.roll()

    def roll(self) -> int:
        self.value = random.randint(1, 6)
        return self.value


POINT = True
COME_OUT = False
NUM_TO_FIELD = {
    4: "FOUR",
    5: "FIVE",
    6: "SIX",
    8: "EIGHT",
    9: "NINE",
    10: "TEN",
}


class Action():
    pass


class Bet(Action):
    def __init__(self, field_name: str, amount: int):
        self.field_name = field_name
        self.amount = amount

    def __str__(self) -> str:
        return f"Betting {self.amount} on {self.field_name}"


class Move(Action):
    def __init__(self, from_field_name: str, to_field_name):
        self.from_field_name = from_field_name
        self.to_field_name = to_field_name

    def __str__(self) -> str:
        return f"Moving from {self.from_field_name} to {self.to_field_name}"


class DoNothing(Action):
    pass

    def __str__(self) -> str:
        return f"Doing nothing"


class Strategy():
    def next_action(self, game, player) -> Action:
        pass

    def __str__(self) -> str:
        return f"{type(self).__name__}"


class Player():
    def __init__(self, name: str, wallet: int, strategy: Strategy):
        self.name = name
        self.wallet = wallet
        self.strategy = strategy

    def __str__(self) -> str:
        return f"{self.name} [{self.wallet}] playing {self.strategy}"

    def next_action(self, game) -> Action:
        return self.strategy.next_action(game, self)

    def add(self, amount: int) -> None:
        self.wallet += amount

    def deduct(self, amount) -> int:
        self.wallet -= amount
        if self.wallet < 0:
            raise OutOfMoney()
        return self.wallet


class Field():
    def __init__(self, name: str):
        self.name = name
        self.values: Dict[Player, int] = defaultdict(int)

    def __str__(self) -> str:
        disp = ""
        for player, amount in self.values.items():
            disp += f"{player.name}: {amount}"
        return f"{self.name}: {disp}"

    def get(self, player: Player) -> int:
        return self.values.get(player, 0)

    def add(self, player: Player, amount: int = 0):
        self.values[player] += amount

    def deduct(self, player: Player):
        amount = self.values.get(player, 0)
        self.values[player] = 0
        return amount


class PassBet(Strategy):
    def _num_points(self, game, player: Player) -> int:
        return sum([f.get(player) > 0 for f in game.point_num_fields()])

    def next_action(self, game, player) -> Action:
        if game.phase is COME_OUT and game.is_empty("PASS_LINE", player):
            return Bet("PASS_LINE", game.MIN_BET)
        elif game.phase is POINT:
            if game.is_empty("COME",
                             player) and self._num_points(game, player) < 2:
                return Bet("COME", game.MIN_BET)
        return DoNothing()


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
            "COME": Field("COME"),
            "FOUR": Field("FOUR"),
            "FIVE": Field("FIVE"),
            "SIX": Field("SIX"),
            "EIGHT": Field("EIGHT"),
            "NINE": Field("NINE"),
            "TEN": Field("TEN"),
        }

    def join(self, player: Player) -> None:
        self.players.append(player)

    def dice(self) -> int:
        return self.d1.value + self.d2.value

    def start(self, max_iterations: int) -> None:
        while self.iteration < max_iterations:
            self._performPlayerActions()
            self._shoot()
            print(f"---> Rolled {self.dice()}")
            self._reconcile()
            self._print_game_status()
            self.iteration += 1

    def point_num_fields(self) -> List[Field]:
        return [self.fields[f] for f in ["FOUR", "FIVE", "SIX", "EIGHT", "NINE", "TEN"]]  # noqa

    def current_point_field(self) -> str:
        if self.point is None:
            raise IllegalAction()
        return NUM_TO_FIELD[self.point]

    def is_empty(self, field_name: str, player: Player) -> bool:
        return game.fields[field_name].get(player) == 0

    def _print_game_status(self) -> None:
        print(f"--- Game State ---")
        for name, field in self.fields.items():
            print(field)
        print(f"--- Player State ---")
        for player in self.players:
            print(player)
        print(f"=== iteration {self.iteration} ===\n\n")

    def _shoot(self) -> None:
        self.d1.roll()
        self.d2.roll()

    def _performPlayerActions(self) -> None:
        for player in self.players:
            action = player.next_action(self)
            print(f"---> {player.name} -> {action}")
            if isinstance(action, Bet):
                if self.phase is POINT and action.field_name == "PASS_LINE":
                    raise IllegalAction()
                player.deduct(action.amount)
                self.fields[action.field_name].add(player, action.amount)
            if isinstance(action, Move):
                amount = self.fields[action.from_field_name].deduct(player)
                self.fields[action.to_field_name].add(player, amount)

    def _reconcile(self) -> None:
        dice = self.dice()
        if self.phase is COME_OUT:
            if dice in [2, 3, 12]:
                self._crap_out()
            elif dice in [4, 5, 6, 8, 9, 10]:
                self._establish_point(dice)
            elif dice in [7, 11]:
                self._natural()
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
                self._come_point_win(dice)
                self._come_point_move(dice)
            else:
                pass

    def _player_win(self, field_name: str, multiplier: int) -> None:
        for player in self.fields[field_name].values:
            bet = self.fields[field_name].deduct(player)
            if bet == 0:
                break
            win = bet * 1
            self.house_losses += win
            print(f"!!!! Player WIN on {field_name}: {bet} bet + {win} win = {bet + win}")  # noqa
            player.add(bet + win)

    def _player_lose(self, field_name: str) -> None:
        for player in self.fields[field_name].values:
            amount = self.fields[field_name].get(player)
            if amount > 0:
                print(f"XXXX Player LOSE: {amount}")
            self.house_wins += self.fields[field_name].deduct(player)

    def _establish_point(self, dice: int) -> None:
        print("---> ESTABLISH POINT")
        self.phase = POINT
        self.point = dice

    def _seven_out(self) -> None:
        print("---> SEVEN OUT")
        self.phase = COME_OUT
        self.point = None
        self._player_lose("PASS_LINE")
        self._player_lose("FOUR")
        self._player_lose("FIVE")
        self._player_lose("SIX")
        self._player_lose("EIGHT")
        self._player_lose("NINE")
        self._player_lose("TEN")

    def _pass_win(self) -> None:
        print("---> PASS WIN")
        self.phase = COME_OUT
        self.point = None
        self._player_win("PASS_LINE", 1)

    def _come_win(self) -> None:
        print("---> COME CHECK WINNERS")
        self._player_win("COME", 1)

    def _come_lose(self) -> None:
        print("---> COME CHECK LOSERS")
        self._player_lose("COME")

    def _move_all(self, from_field: str, to_field: str) -> None:
        values = self.fields[from_field].values
        self.fields[from_field].values = defaultdict(int)
        for player, value in values.items():
            self.fields[to_field].add(player, value)

    def _come_point_move(self, point: int) -> None:
        print(f"---> COME POINT MOVE TO {point}")
        self._move_all("COME", NUM_TO_FIELD[point])

    def _come_point_win(self, point: int) -> None:
        print(f"---> COME POINT {point} CHECK WINNERS")
        self._player_win(NUM_TO_FIELD[point], 1)

    def _natural(self) -> None:
        print("---> NATURAL!")
        self._player_win("PASS_LINE", 1)

    def _crap_out(self) -> None:
        print("---> CRAPPED OUT")
        self._player_lose("PASS_LINE")


if __name__ == "__main__":
    MIN_BET = 10
    game = Craps(10)
    player = Player(name="Evan", wallet=1000, strategy=PassBet())
    game.join(player)
    game.start(max_iterations=100)
