from abc import ABC, abstractmethod

class Agent(ABC):
    """
    Abstract base class for agents.
    Agents are responsible for executing tasks and managing their own state.
    """

    @abstractmethod
    def get_action(self, state: list) -> int:
        """
        Get the action to be taken based on the current state.
        :param state: The current state of the agent.
        :return: The action to be taken.
        """
        pass

    @abstractmethod
    def action(self, action: int) -> None:
        """
        Execute the given action.
        :param action: The action to be executed.
        """
        pass

    @abstractmethod
    def extract_features(self, data: list) -> list:
        """
        Extract features from the given data.
        :param data: The data from which to extract features.
        :return: A list of features extracted from the data.
        """
        pass