import asyncio
from dependency_injector.wiring import inject, Provide
from services.logger_service import LoggerService
from services.streams.stream import Stream
from services.exchanges.exchange import Exchange, Health, State

class HealthCheckService:
    """
    A service that performs health checks at regular intervals.
    This service runs in a separate thread and can be paused or resumed.
    """

    @inject
    async def check_health(self,
                           exchange: Exchange = Provide['exchange'],
                           stream: Stream = Provide['stream']) -> None:
        """
        Check the health and state of the exchange and stream.
        This method checks if the exchange is healthy and if the stream is paused or resumed.
        :param exchange: The exchange to check health and state.
        :param stream: The stream to check if it should be paused or resumed based on the exchange health and state.
        """
        health = await exchange.get_health()
        state = await exchange.get_state()

        if stream.paused and health == Health.NORMAL and state == State.RUNNING:
            stream.resume()
        elif not stream.paused and (health != Health.NORMAL or state != State.RUNNING):
            stream.pause()

    async def run(self):
        """
        Start the health check service.
        This method starts the event loop and runs the health checks at the specified interval.
        """
        self.logger.system.info("The health check service is started.")
        while True:
            if not self.paused:
                await asyncio.gather(self.check_health(), asyncio.sleep(self.interval))
            else:
                await asyncio.sleep(1)

    def pause(self):
        """
        Pause the health check service.
        This method pauses the health checks that are currently running.
        """
        self.pause = True
        self.logger.system.info("The health check service is paused.")

    def resume(self):
        """
        Resume the health check service.
        This method resumes the health checks that have been paused.
        """
        self.paused = False
        self.logger.system.info("The health check service is resumed.")

    @inject
    def __init__(self,
                 interval: int,
                 logger: LoggerService = Provide['logger']):
        """
        Initialize the HealthCheckService with an interval for health checks.
        :param interval: The interval in seconds at which to perform health checks.
        :param logger: The logger service for logging health check events.
        """
        self.interval = interval
        self.logger = logger
        self.paused = False