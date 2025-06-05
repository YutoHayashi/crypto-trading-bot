from exceptions.base_exception import BaseException

class WebsocketException(BaseException):
    """Base exception for Websocket client errors."""
    _title = "Websocket Client Exception"