from logging import getLogger

class BaseException(Exception):
    """Base exception for all custom exceptions."""

    _title = "Exception"
    _logger = getLogger("System")

    def __init__(self, message: str):
        super().__init__(message)
        self.message = f"{self._title} - {message}"
        self._logger.error(self.message)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.message}')"