from enum import Enum
import os
import io
import torch
from s3client import S3Client

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
    def __init__(self, qnet, model_key: str, observation_size: int, action_size: int):
        """
        Initializes the Agent with a Q-network and loads a pre-trained model from S3.
        :param qnet: The Q-network class to be used.
        :param model_key: The S3 key for the pre-trained model.
        :param observation_size: The size of the observation space.
        :param action_size: The size of the action space.
        """
        self.q_model = qnet(input_size=observation_size, output_size=action_size)

        s3client = S3Client(bucket=os.environ.get('S3_TRAINED_MODEL_BUCKET'))
        model_bytes = s3client.get_object(key=model_key)['Body'].read()
        buffer = io.BytesIO(model_bytes)

        self.q_model.load_state_dict(torch.load(buffer))
        self.q_model.eval()

    def get_action(self, state):
        """
        Determines the action to take based on the current state using the Q-network.
        :param state: The current state of the environment.
        :return: The action to take, represented as an integer.
        """
        with torch.no_grad():
            state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            action = self.q_model(state_tensor).argmax().item()
        return action