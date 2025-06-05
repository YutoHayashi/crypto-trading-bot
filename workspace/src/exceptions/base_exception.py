from dependency_injector.wiring import inject, Provide
from services import logger_service

class BaseException(Exception):
    """Base exception for all custom exceptions."""
    _title = "Exception"

    @inject
    def __init__(self,
                 message: str = 'An error occurred',
                 logger: logger_service.LoggerService = Provide['logger']):
        super().__init__(message)
        self.message = f"{self._title} - {message}"
        logger.system.error(self.message)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.message}')"