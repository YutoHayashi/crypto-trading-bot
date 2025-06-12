from typing import List, Literal
import dataclasses
import asyncio
from dependency_injector.wiring import inject, Provide
from services.exchange_clients.exchange_client import ExchangeClient

@dataclasses.dataclass
class Order:
    product_code: str
    side: Literal['BUY', 'SELL']
    child_order_type: Literal['LIMIT', 'MARKET']
    price: float
    size: float
    child_order_acceptance_id: str
    id: int = None
    child_order_id: str = None
    average_price: float = None
    child_order_state: Literal['ACTIVE', 'COMPLETED', 'CANCELED', 'EXPIRED', 'REJECTED'] = None
    expire_date: str = None
    child_order_date: str = None
    outstanding_size: float = None
    cancel_size: float = None
    executed_size: float = None
    total_commission: float = None
    time_in_force: Literal['GTC', 'IOC', 'FOK'] = None

class OrderBook:
    """
    Service for managing order book operations.
    This service can be extended to include methods for adding, removing, or updating orders.
    """
    _orders: List[Order] = []

    @inject
    async def sync(self,
                   exchange_client: ExchangeClient = Provide['exchange_client'],
                   config: dict = Provide['config']):
        """
        Synchronize the order book data.
        This method can be extended to fetch and update order book data from an external source.
        :param exchange_client: The Bitflyer client for fetching order book data.
        """
        async with self.lock:
            orders = exchange_client.get_orders(symbol=config.get('crypto_currency_code'))

            self._orders = [Order(**order) for order in orders]

    async def get_orders(self) -> List[Order]:
        async with self.lock:
            return self._orders.copy()

    def __init__(self):
        """
        Initialize the OrderBook service.
        This service can be extended to include methods for managing order book data.
        """
        self.lock = asyncio.Lock()