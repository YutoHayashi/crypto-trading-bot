from enum import Enum
import random
from .agent import Agent

class Action(Enum):
    DO_NOTHING = 0
    BUY = 1
    SELL = 2

class Random(Agent):
    def get_action(self, state: list) -> Action:
        return random.choice(list(Action))

    def action(self, action: Action) -> None:
        match action:
            case Action.DO_NOTHING:
                print("Doing nothing.")
            case Action.BUY:
                print("Executing buy action.")
            case Action.SELL:
                print("Executing sell action.")
            case _:
                print("Unknown action.")

    def extract_features(self, data: list) -> list:
        return []