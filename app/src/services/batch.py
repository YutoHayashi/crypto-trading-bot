from typing import List, Callable, Awaitable
import asyncio
from dependency_injector.wiring import inject, Provide
from services.logger import Logger
from services.exchanges.exchange import Exchange

class Batch:
    tasks: List[Callable[[], Awaitable[None]]]
    interval: int

    @inject
    async def run(self,
                  exchange: Exchange = Provide['exchange']):
        """
        Start the batch service.
        This method starts the event loop and runs the tasks at the specified interval.
        """
        self.logger.system.info("The batch service is started.")
        while True:
            if not self.paused:
                await asyncio.gather(exchange.sync(), asyncio.sleep(self.interval))
            else:
                await asyncio.sleep(1)

    def pause(self):
        """
        Pause all tasks in the batch service.
        This method pauses all tasks that are currently running in the batch service.
        """
        self.paused = True
        self.logger.system.info("The batch service is paused.")

    def resume(self):
        """
        Resume all tasks in the batch service.
        This method resumes all tasks that have been paused.
        """
        self.paused = False
        self.logger.system.info("The batch service is resumed.")

    @inject
    def __init__(self,
                 interval: int,
                 logger: Logger = Provide['logger']):
        """
        Initialize the Batch service with a list of tasks.
        :param interval: The interval in seconds at which to run the tasks.
        :param tasks: A list of asynchronous tasks to run at the specified interval.
        :param logger: The logger service to log messages.
        """
        self.interval = interval
        self.logger = logger
        self.paused = False