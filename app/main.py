import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import asyncio
from dotenv import load_dotenv
from container import ApplicationContainer

load_dotenv()

legal_currency_code = 'JPY'
crypto_currency_code = 'FX_BTC_JPY'

async def main(container: ApplicationContainer) -> None:
    """
    Main entry point for the application.
    This function initializes the application container, synchronizes the portfolio,
    and starts the stream and batch services.
    :param container: The application container that holds all services and configurations.
    """
    await container.portfolio().sync()
    await container.order_book().sync()
    await container.position_book().sync()
    await asyncio.gather(
        container.stream().run(),
        container.batch().run(),
        container.health_check().run()
    )

if __name__ == '__main__':
    container = ApplicationContainer()

    container.config.from_dict({
        'batch_interval': 10,
        'health_check_interval': 10,
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
    container.config.line_messaging_api_base_url.from_env('LINE_MESSAGING_API_BASE_URL')
    container.config.line_messaging_api_channel_token.from_env('LINE_MESSAGING_API_CHANNEL_TOKEN')
    container.config.line_messaging_api_destination_user_id.from_env('LINE_MESSAGING_API_DESTINATION_USER_ID')

    container.wire()

    asyncio.run(main(container))