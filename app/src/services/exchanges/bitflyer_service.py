import asyncio
from dependency_injector.wiring import inject, Provide
from services.exchanges.exchange import Exchange, Health, State
from services.exchange_clients.exchange_client import ExchangeClient

class BitflyerService(Exchange):
    name = 'bitflyer Lightning'

    __health: Health = None
    __state: State = None

    @inject
    async def sync(self,
                   exchange_client: ExchangeClient = Provide['exchange_client'],
                   config: dict = Provide['config']) -> None:
        """
        Synchronize the exchange data.
        This method can be extended to fetch and update exchange data from an external source.
        """
        async with self.lock:
            boardstate = exchange_client.get_health(symbol=config.get('crypto_currency_code'))
            health = boardstate.get('health', Health.NORMAL.value)
            state = boardstate.get('state', State.RUNNING.value)

            self.__health = Health(health)
            self.__state = State(state)

    async def get_health(self) -> Health:
        async with self.lock:
            return self.__health

    async def get_state(self) -> State:
        async with self.lock:
            return self.__state

    def __init__(self):
        self.lock = asyncio.Lock()