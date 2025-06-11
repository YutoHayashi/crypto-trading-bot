from typing import List
from abc import ABC, abstractmethod
from dependency_injector.wiring import inject, Provide
from services import logger_service

class MessageHandler(ABC):
    """
    Abstract base class for handling messages from a WebSocket.
    This class defines the interface for message handlers that process incoming messages from a WebSocket connection.
    Each handler must implement the `handle_message` method to process the data received.
    """
    legal_currency_code: str = None
    crypto_currency_code: str = None
    logger: logger_service.LoggerService = None

    @property
    @abstractmethod
    def channel_names(self) -> List[str]:
        pass

    @abstractmethod
    async def handle_message(self, data: list|dict, channel: str) -> None:
        """
        Handle incoming messages from the WebSocket.

        :param data: The data received from the WebSocket.
        :param channel: The channel from which the message was received.
        """
        pass

    @inject
    def __init__(self,
                 config: dict = Provide['config'],
                 logger: logger_service.LoggerService = Provide['logger']):
        """
        Initialize the message handler.
        """
        self.legal_currency_code = config.get('legal_currency_code')
        self.crypto_currency_code = config.get('crypto_currency_code')
        self.logger = logger