from typing import List
import os
import time
import json
import hmac
import hashlib
import websocket
import rel
from dependency_injector.wiring import inject, Provide
from exceptions import runtime_exception, websocket_exception
from services import logger_service, handler_dispatcher_service

class WsClientService:
    ws: websocket.WebSocketApp = None

    def on_open(self, ws):
        for channel in self.public_channels:
            ws.send(json.dumps({
                "method": "subscribe",
                "params": {
                    "channel": channel,
                },
            }))
        
        # Authenticate the WebSocket connection
        timestamp = int(time.time())
        nonce = os.urandom(16).hex()
        mix = f"{timestamp}{nonce}"
        signature = hmac.new(self.__api_secret.encode('utf-8'), mix.encode('utf-8'), hashlib.sha256).hexdigest()
        ws.send(json.dumps({
            "method": "auth",
            "params": {
                "api_key": self.__api_key,
                "timestamp": timestamp,
                "nonce": nonce,
                "signature": signature,
            },
        }))

        # Subscribe to private channels from here
        for channel in self.private_channels:
            ws.send(json.dumps({
                "method": "subscribe",
                "params": {
                    "channel": channel,
                },
            }))

        self.logger.system.info("WebSocket connection opened. Subscribing to channels.")

    def on_reconnect(self, ws):
        self.logger.system.info("WebSocket connection reestablished. Resubscribing to channels.")

    def on_message(self, ws, msg):
        message = json.loads(msg)
        if 'params' in message and 'message' in message['params'] and 'channel' in message['params']:
            data = message['params']['message']
            channel = message['params']['channel']
            self.handler_dispatcher.dispatch(data, channel)

    def on_close(self, ws, status_code, msg):
        self.logger.system.info(f"WebSocket connection closed with status code {status_code}: {msg}")

    def on_error(self, ws, err):
        raise websocket_exception.WebsocketException(f"WebSocket connection error: {str(err)}")

    def run(self):
        if self.ws is None:
            raise runtime_exception.RuntimeException("WebSocketApp is not initialized. Call Stream.start() first.")
        self.ws.run_forever(dispatcher=rel, reconnect=5)
        rel.signal(2, rel.abort)
        rel.dispatch()

    def stop(self):
        if self.ws is None:
            raise runtime_exception.RuntimeException("WebSocketApp is not running. Call Stream.start() first.")
        rel.abort()

    @inject
    def __init__(self,
                 api_key: str,
                 api_secret: str,
                 public_channels: List[str],
                 private_channels: List[str],
                 handler_dispatcher: handler_dispatcher_service.HandlerDispatcherService = Provide['handler_dispatcher'],
                 logger: logger_service.LoggerService = Provide['logger']):
        """
        Initialize the WebSocket client.
        :param message_handler: The message handler to process incoming messages.
        :param logger: An instance of Logger to log messages.
        """
        self.__api_key = api_key
        self.__api_secret = api_secret
        self.public_channels = public_channels
        self.private_channels = private_channels
        self.handler_dispatcher = handler_dispatcher
        self.logger = logger

        self.ws = websocket.WebSocketApp(
            os.environ.get("BITFLYER_WEBSOCKET_URL"),
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_reconnect=self.on_reconnect
        )