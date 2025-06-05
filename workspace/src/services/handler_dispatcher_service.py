from typing import List
import dataclasses
from exceptions import runtime_exception
from message_handlers.message_handler import MessageHandler

@dataclasses.dataclass
class HandlerDispatcherService:
    handlers: List[MessageHandler]

    def dispatch(self, data: list|dict, channel: str) -> None:
        """
        Dispatch the message to the appropriate handler based on the channel.
        """
        for handler in self.handlers:
            if hasattr(handler, 'handle_message') and channel in handler.channel_names:
                handler.handle_message(data, channel)
            else:
                raise runtime_exception.RuntimeException(f"Handler {handler.__class__.__name__} does not implement handle_message method.")