from dependency_injector.wiring import inject, Provide
import exceptions
from services import portfolio_service
from message_handlers.message_handler import MessageHandler

class ChildOrderEventHandler(MessageHandler):
    """
    Handles child order events.
    This handler processes messages related to child orders.
    """
    channel_names = ['child_order_events']

    @inject
    async def handle_message(self,
                             data: list|dict,
                             channel: str,
                             portfolio: portfolio_service.PortfolioService = Provide['portfolio']) -> None:
        """
        Handles the incoming message by checking the channel and processing child order data.
        :param data: The data received from the WebSocket message.
        :param channel: The channel from which the message was received.
        :param portfolio: The portfolio service to synchronize the portfolio.
        """
        if 'event_type' in data and data['event_type'] == 'order'.upper():
            """Handles order events for child orders.
            This method processes order events and updates the portfolio accordingly."""
            child_order_acceptance_id = data['child_order_acceptance_id'] if 'child_order_acceptance_id' in data else None
            side = data['side'] if 'side' in data else None
            price = data['price'] if 'price' in data else None
            size = data['size'] if 'size' in data else None

            if child_order_acceptance_id is None or side is None or price is None or size is None:
                raise exceptions.TransactionException('Invalid order event data received. Missing required fields: child_order_acceptance_id, side, price, or size.')

            self.logger.transaction.info(f'Order event received, Order ID: {child_order_acceptance_id}, Side: {size}, Price: {price}, Size: {size}')

        elif 'event_type' in data and data['event_type'] == 'execution'.upper():
            """Handles execution events for child orders.
            This method processes execution events and updates the portfolio accordingly."""
            child_order_acceptance_id = data['child_order_acceptance_id'] if 'child_order_acceptance_id' in data else None

            if child_order_acceptance_id is None:
                raise exceptions.TransactionException('Invalid execution event data received. Missing required field: child_order_acceptance_id.')

            await portfolio.sync()

            self.logger.transaction.info(f'Execution event received, Order ID: {child_order_acceptance_id}')

        elif 'event_type' in data and data['event_type'] == 'cancel'.upper():
            """Handles cancel events for child orders.
            This method processes cancel events and logs the cancellation."""
            child_order_acceptance_id = data['child_order_acceptance_id'] if 'child_order_acceptance_id' in data else None

            if child_order_acceptance_id is None:
                raise exceptions.TransactionException('Invalid cancel event data received. Missing required field: child_order_acceptance_id.')

            self.logger.transaction.info(f'Cancel event received, Order ID: {child_order_acceptance_id}')

        elif 'event_type' in data and data['event_type'] == 'order_failed'.upper():
            """Handles order failed events for child orders.
            This method processes order failed events and logs the failure."""
            self.logger.transaction.info('Order failed event received.')

        elif 'event_type' in data and data['event_type'] == 'cancel_failed'.upper():
            """Handles cancel failed events for child orders.
            This method processes cancel failed events and logs the failure."""
            child_order_acceptance_id = data.get('child_order_acceptance_id', None)

            if child_order_acceptance_id is None:
                raise exceptions.TransactionException('Invalid cancel failed event data received. Missing required field: child_order_acceptance_id.')

            self.logger.transaction.info(f'Cancel failed event received, Order ID: {child_order_acceptance_id}')