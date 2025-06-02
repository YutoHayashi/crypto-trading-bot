from enum import Enum
import torch

class Actions(Enum):
    """
    Enum for possible actions in the environment.
    """
    DO_NOTHING = 0
    BUY_AT_BEST_ASK = 1
    SELL_AT_BEST_BID = 2
    BUY_AT_BEST_BID = 3
    SELL_AT_BEST_ASK = 4
    CANCEL_BUY_ORDER = 5
    CANCEL_SELL_ORDER = 6

class Agent:
    def __init__(self, qnet, model_path: str, observation_size: int, action_size: int):
        self.q_model = qnet(input_size=observation_size, output_size=action_size)
        self.q_model.load_state_dict(torch.load(model_path))
        self.q_model.eval()

    def get_action(self, state):
        with torch.no_grad():
            state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            action = self.q_model(state_tensor).argmax().item()
        return action