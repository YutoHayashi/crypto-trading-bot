import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import asyncio
from dotenv import load_dotenv
from container import ApplicationContainer
import exceptions

load_dotenv()

legal_currency_code = 'JPY'
crypto_currency_code = 'FX_BTC_JPY'

def main(container: ApplicationContainer) -> None:
    """
    Main function to run the application.
    This function initializes the portfolio and starts the WebSocket client.
    :param container: The application container containing all services and configurations.
    """
    try:
        asyncio.run(container.portfolio().sync())
        container.stream().run()
    except exceptions.LogicException as e:
        container.stream().stop()
    except exceptions.RuntimeException as e:
        container.stream().stop()

if __name__ == '__main__':
    container = ApplicationContainer()

    container.config.from_dict({
        'legal_currency_code': legal_currency_code,
        'crypto_currency_code': crypto_currency_code,
        'data_buffer_size': 100,
        'public_channels': [f"lightning_board_snapshot_{crypto_currency_code}"],
        'private_channels': ["child_order_events"],
    })

    container.config.bitflyer_websocket_url.from_env('BITFLYER_WEBSOCKET_URL')
    container.config.bitflyer_api_base_url.from_env('BITFLYER_API_BASE_URL')
    container.config.bitflyer_api_key.from_env('BITFLYER_API_KEY')
    container.config.bitflyer_api_secret.from_env('BITFLYER_API_SECRET')
    container.config.s3_bucket.from_env('S3_BUCKET')

    container.wire()

    main(container)