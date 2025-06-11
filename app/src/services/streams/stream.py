from abc import ABC, abstractmethod
from dependency_injector.wiring import inject, Provide
from services.logger_service import LoggerService

class Stream(ABC):
    """
    Abstract base class for WebSocket streams.
    """
    logger: LoggerService = None

    @abstractmethod
    async def run(self):
        """
        Run the WebSocket stream.
        """
        pass

    def pause(self):
        """
        Stop the stream.
        """
        self.paused = True
        self.logger.system.info("The stream is paused.")

    def resume(self):
        """
        Resume the stream.
        """
        self.paused = False
        self.logger.system.info("The stream is resumed.")

    @inject
    def __init__(self,
                 logger: LoggerService = Provide['logger']):
        """
        Initialize the WebSocket stream.
        """
        self.logger = logger
        self.paused = False