from abc import ABC, abstractmethod

class Stream(ABC):
    """
    Abstract base class for WebSocket streams.
    """

    @abstractmethod
    def run(self) -> None:
        """
        Run the WebSocket stream.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stop the WebSocket stream.
        """
        pass