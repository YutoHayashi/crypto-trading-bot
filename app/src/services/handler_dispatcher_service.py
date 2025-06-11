from typing import List
import dataclasses
import asyncio
import exceptions
from message_handlers.message_handler import MessageHandler

@dataclasses.dataclass
class HandlerDispatcherService:
    """
    HandlerDispatcherService is responsible for dispatching messages to the appropriate handlers.
    It checks the channel of the incoming message and calls the corresponding handler's method.
    """
    handlers: List[MessageHandler]

    async def dispatch(self, data: list|dict, channel: str) -> None:
        """
        Dispatch the message to the appropriate handler based on the channel.
        """
        tasks = []
        for handler in self.handlers:
            if hasattr(handler, 'handle_message'):
                if channel in handler.channel_names:
                    tasks.append(handler.handle_message(data, channel))
            else:
                raise exceptions.LogicException(f"Handler {handler.__class__.__name__} does not implement handle_message method.")
        if tasks:
            await asyncio.gather(*tasks)