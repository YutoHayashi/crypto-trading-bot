from dependency_injector import containers, providers
import exceptions
import services
from services import logger_service, batch_service, health_check_service, notification_service, s3client_service, portfolio_service, data_buffer_service, handler_dispatcher_service
from services.exchange_clients import bitflyer_lightning_client_service
from services.streams import bitflyer_lightning_wsclient_service
from services.exchanges import bitflyer_service
import message_handlers
from message_handlers import board_event_handler, child_order_event_handler

class ApplicationContainer(containers.DeclarativeContainer):
    """Dependency Injection Container for the application."""
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(
        packages=[exceptions, services, message_handlers],
        modules=['__main__']
    )

    # Services
    logger = providers.Singleton(logger_service.LoggerService)
    stream = providers.Singleton(
        bitflyer_lightning_wsclient_service.BitflyerLightningWsclientService,
        url=config.bitflyer_websocket_url,
        api_key=config.bitflyer_api_key,
        api_secret=config.bitflyer_api_secret,
        public_channels=config.public_channels,
        private_channels=config.private_channels
    )
    batch = providers.Singleton(
        batch_service.BatchService,
        interval=config.batch_interval
    )
    health_check = providers.Singleton(
        health_check_service.HealthCheckService,
        interval=config.health_check_interval,
    )
    notifier = providers.Singleton(
        notification_service.NotificationService
    )
    exchange = providers.Singleton(bitflyer_service.BitflyerService)
    portfolio = providers.Singleton(portfolio_service.PortfolioService)
    data_buffer = providers.Singleton(
        data_buffer_service.DataBufferService,
        max_size=config.data_buffer_size
    )
    s3client = providers.Singleton(
        s3client_service.S3ClientService,
        bucket=config.s3_bucket
    )
    exchange_client = providers.Factory(
        bitflyer_lightning_client_service.BitflyerLightningClientService,
        base_url=config.bitflyer_api_base_url,
        api_key=config.bitflyer_api_key,
        api_secret=config.bitflyer_api_secret
    )

    # Message Handlers
    handler_dispatcher = providers.Singleton(
        handler_dispatcher_service.HandlerDispatcherService,
        handlers=providers.List(
            providers.Factory(board_event_handler.BoardEventHandler),
            providers.Factory(child_order_event_handler.ChildOrderEventHandler)
        )
    )