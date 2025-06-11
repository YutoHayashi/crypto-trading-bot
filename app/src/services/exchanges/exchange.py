from enum import Enum
from abc import ABC, abstractmethod

class Health(Enum):
    NORMAL = 'NORMAL'
    BUSY = 'BUSY'
    VERY_BUSY = 'VERY_BUSY'
    SUPER_BUSY = 'SUPER_BUSY'
    NO_ORDER = 'NO_ORDER'
    STOP = 'STOP'

class State(Enum):
    RUNNING = 'RUNNING'
    CLOSED = 'CLOSED'
    STARTING = 'STARTING'
    PREOPEN = 'PREOPEN'
    CIRCUITE_BREAK = 'CIRCUIT_BREAK'

class Exchange(ABC):
    """
    Abstract base class for exchanges.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the exchange.
        """
        pass

    @abstractmethod
    async def sync(self) -> None:
        """
        Synchronizes the exchange data.
        This method can be extended to fetch and update exchange data from an external source.
        """
        pass

    @abstractmethod
    async def get_health(self) -> str:
        """
        Returns the unique identifier of the exchange.
        """
        pass

    @abstractmethod
    async def get_state(self) -> str:
        """
        Returns the current state of the exchange.
        """
        pass