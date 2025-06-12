from dependency_injector.wiring import inject, Provide
from services import data_buffer, portfolio
from message_handlers.message_handler import MessageHandler

class BoardEventHandler(MessageHandler):
    """
    Handles board events for a specific cryptocurrency.
    This handler processes messages related to the lightning board snapshot for the specified cryptocurrency.
    """
    channel_names = []

    @inject
    async def handle_message(self,
                             data: list|dict,
                             channel: str,
                             data_buffer: data_buffer.DataBuffer = Provide['data_buffer'],
                             portfolio: portfolio.Portfolio = Provide['portfolio']) -> None:
        """
        Handles the incoming message by checking the channel and appending data to the buffer if it matches.
        :param data: The data received from the WebSocket message.
        :param channel: The channel from which the message was received.
        :param data_buffer: The data buffer service to append data to.
        :param portfolio: The portfolio service (not used in this handler but can be extended).
        """
        data_buffer.append(data)

        if (len(data_buffer) > data_buffer.max_size):
            pass

    def __init__(self):
        """
        Initializes the BoardEventHandler with the cryptocurrency code.
        """
        super().__init__()
        self.channel_names.append(f'lightning_board_snapshot_{self.crypto_currency_code}')