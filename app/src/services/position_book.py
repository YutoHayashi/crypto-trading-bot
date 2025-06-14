from typing import List, Literal
import dataclasses
import asyncio
from dependency_injector.wiring import inject, Provide
from services.exchange_clients.exchange_client import ExchangeClient

@dataclasses.dataclass
class Position:
    product_code: str
    side: Literal['BUY', 'SELL']
    price: float
    size: float
    commission: float = None
    swap_point_accumulate: float = None
    required_collateral: float = None
    open_date: str = None
    levarage: float = None
    pnl: float = None
    sfd: float = None

class PositionBook:
    """
    Service for managing position book operations.
    This service can be extended to include methods for adding, removing, or updating positions.
    """
    _positions: List[Position] = []

    @inject
    async def sync(self,
                   exchange_client: ExchangeClient = Provide['exchange_client'],
                   config: dict = Provide['config']):
        """
        Synchronize the position book data.
        This method can be extended to fetch and update position book data from an external source.
        :param exchange_client: The Bitflyer client for fetching position book data.
        """
        async with self.lock:
            positions = exchange_client.get_positions(symbol=config.get('crypto_currency_code'))

            self._positions = [Position(**position) for position in positions]

    async def add_and_settle(self, position: Position) -> float:
        """
        Add a new position to the position book.
        If an opposite position exists, offset (close) it as needed.
        :param position: The position to be added.
        :return: The realized PnL from offsetting, if any.
        """
        async with self.lock:
            pnl = 0.0
            for existing in self._positions:
                if existing.side != position.side and existing.size >= position.size:
                    # Offset the existing position with the new position
                    # Calculate PnL based on the offset size
                    offset_size = min(existing.size, position.size)
                    pnl += (position.price - existing.price) * offset_size if position.side == 'SELL' else (existing.price - position.price) * offset_size
                    existing.size -= offset_size
                    position.size -= offset_size
                    if existing.size == 0.0:
                        self._positions.remove(existing)
                    if position.size == 0.0:
                        break
            if position.size > 0:
                self._positions.append(position)
            return pnl

    async def get_positions(self) -> List[Position]:
        async with self.lock:
            return self._positions.copy()

    def __init__(self):
        """
        Initialize the PositionBook service.
        This service can be extended to include methods for managing position book data.
        """
        self.lock = asyncio.Lock()