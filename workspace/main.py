import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
load_dotenv()

from dependency_injector.wiring import inject, Provide
from container import ApplicationContainer
from services import wsclient_service

legal_currency_code = 'JPY'
crypto_currency_code = 'FX_BTC_JPY'

@inject
def main(wsclient: wsclient_service.WsClientService = Provide['wsclient']):
    """
    Main function to start the WebSocket client service.
    """
    wsclient.run()

if __name__ == '__main__':
    container = ApplicationContainer()

    container.config.from_dict({
        'legal_currency_code': legal_currency_code,
        'crypto_currency_code': crypto_currency_code,
        'data_buffer_size': 100,
        'public_channels': [f"lightning_board_snapshot_{crypto_currency_code}"],
        'private_channels': ["child_order_events"],
    })

    container.config.bitflyer_api_key.from_env('BITFLYER_API_KEY')
    container.config.bitflyer_api_secret.from_env('BITFLYER_API_SECRET')
    container.config.bitflyer_api_base_url.from_env('BITFLYER_API_BASE_URL')
    container.config.s3_bucket.from_env('S3_BUCKET')

    container.wire()

    main()