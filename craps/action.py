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
