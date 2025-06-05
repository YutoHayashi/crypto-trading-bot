from dependency_injector.wiring import inject, Provide
from services import bitflyer_client_service

class PortfolioService:
    """
    Service for managing portfolio-related operations.
    This service can be extended to include methods for adding, removing, or updating portfolio items.
    """
    legal_currency_amount: float
    crypto_currency_amount: float
    collateral_amount: float

    @inject
    def __init__(self,
                 config: dict = Provide['config'],
                 bitflyer_client: bitflyer_client_service.BitflyerClientService = Provide['bitflyer_client']):
        """
        Initialize the PortfolioService with amounts and Bitflyer client.
        :param legal_currency_code: The code for the legal currency (e.g., 'JPY').
        :param crypto_currency_code: The code for the crypto currency (e.g., 'FX_BTC_JPY').
        :param bitflyer_client: Bitflyer client for fetching balance and collateral.
        """
        balance = bitflyer_client.get_balance()
        collateral = bitflyer_client.get_collateral()

        self.legal_currency_amount = next(filter(lambda x: x['currency_code'] == config.get('legal_currency_code'), balance), {}).get('amount', 0.0)
        self.crypto_currency_amount = next(filter(lambda x: x['currency_code'] == config.get('crypto_currency_code'), balance), {}).get('amount', 0.0)
        self.collateral_amount = collateral.get('collateral', 0.0)