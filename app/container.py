from dependency_injector import containers, providers
import exceptions
import services
from services import batch, data_buffer, handler_dispatcher, health_check, logger, notification, s3client, portfolio, order_book, position_book
from services.exchange_clients import bitflyer_lightning_client
from services.streams import bitflyer_lightning_wsclient
from services.exchanges import bitflyer
import message_handlers
from message_handlers import board_event_handler, child_order_event_handler
import agents
from agents import sample

class ApplicationContainer(containers.DeclarativeContainer):
    """Dependency Injection Container for the application."""
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(
        packages=[exceptions, services, message_handlers, agents],
        modules=['__main__']
    )

    # Services
    logger = providers.Singleton(logger.Logger)
    stream = providers.Singleton(
        bitflyer_lightning_wsclient.BitflyerLightningWsclient,
        url=config.bitflyer_websocket_url,
        api_key=config.bitflyer_api_key,
        api_secret=config.bitflyer_api_secret,
        public_channels=config.public_channels,
        private_channels=config.private_channels
    )
    batch = providers.Singleton(
        batch.Batch,
        interval=config.batch_interval
    )
    health_check = providers.Singleton(
        health_check.HealthCheck,
        interval=config.health_check_interval,
    )
    notification = providers.Singleton(
        notification.Notification,
        line_messaging_api_base_url=config.line_messaging_api_base_url,
        line_messaging_api_channel_token=config.line_messaging_api_channel_token,
        line_messaging_api_destination_user_id=config.line_messaging_api_destination_user_id
    )
    s3client = providers.Singleton(
        s3client.S3Client,
        bucket=config.s3_bucket
    )
    exchange_client = providers.Factory(
        bitflyer_lightning_client.BitflyerLightningClient,
        base_url=config.bitflyer_api_base_url,
        api_key=config.bitflyer_api_key,
        api_secret=config.bitflyer_api_secret
    )
    exchange = providers.Singleton(bitflyer.Bitflyer)
    portfolio = providers.Singleton(portfolio.Portfolio)
    order_book = providers.Singleton(order_book.OrderBook)
    position_book = providers.Singleton(position_book.PositionBook)
    data_buffer = providers.Singleton(
        data_buffer.DataBuffer,
        max_size=config.data_buffer_size
    )

    # Message Handlers
    handler_dispatcher = providers.Singleton(
        handler_dispatcher.HandlerDispatcher,
        handlers=providers.List(
            providers.Factory(board_event_handler.BoardEventHandler),
            providers.Factory(child_order_event_handler.ChildOrderEventHandler)
        )
    )

    # Agent to select action
    agent = providers.Singleton(
        sample.Random,
    )