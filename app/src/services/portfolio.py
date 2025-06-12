import asyncio
from dependency_injector.wiring import inject, Provide
from services.exchange_clients.exchange_client import ExchangeClient

class Portfolio:
    """
    Service for managing portfolio-related operations.
    This service can be extended to include methods for adding, removing, or updating portfolio items.
    """
    __legal_currency_amount: float
    __crypto_currency_amount: float
    __collateral_amount: float

    @inject
    async def sync(self, 
                   exchange_client: ExchangeClient = Provide['exchange_client'],
                   config: dict = Provide['config']):
        """
        Synchronize the portfolio data.
        This method can be extended to fetch and update portfolio data from an external source.
        :param exchange_client: The Bitflyer client for fetching balance and collateral.
        :param config: Configuration dictionary containing currency codes.
        """
        async with self.lock:
            balance = exchange_client.get_balance()
            collateral = exchange_client.get_collateral()

            self.__legal_currency_amount = next(filter(lambda x: x['currency_code'] == config.get('legal_currency_code'), balance), {}).get('amount', 0.0)
            self.__crypto_currency_amount = next(filter(lambda x: x['currency_code'] == config.get('crypto_currency_code'), balance), {}).get('amount', 0.0)
            self.__collateral_amount = collateral.get('collateral', 0.0)

    async def get_legal_currency_amount(self) -> float:
        async with self.lock:
            return self.__legal_currency_amount

    async def get_crypto_currency_amount(self) -> float:
        async with self.lock:
            return self.__crypto_currency_amount

    async def get_collateral_amount(self) -> float:
        async with self.lock:
            return self.__collateral_amount

    def __init__(self):
        """
        Initialize the PortfolioService with amounts and Bitflyer client.
        """
        self.lock = asyncio.Lock()