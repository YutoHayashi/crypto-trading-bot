from typing import List
import os
import time
import json
import hmac
import hashlib
import asyncio
import websockets
from websockets.asyncio.client import connect
from dependency_injector.wiring import inject, Provide
from services import handler_dispatcher_service
from services.streams.stream import Stream

class BitflyerLightningWsclientService(Stream):
    async def send_public_subscriptions(self, websocket):
        for channel in self.public_channels:
            await websocket.send(json.dumps({
                "method": "subscribe",
                "params": {
                    "channel": channel,
                },
            }))

    async def send_private_subscriptions(self, websocket):
        timestamp = int(time.time())
        nonce = os.urandom(16).hex()
        mix = f"{timestamp}{nonce}"
        signature = hmac.new(self.__api_secret.encode('utf-8'), mix.encode('utf-8'), hashlib.sha256).hexdigest()

        await websocket.send(json.dumps({
            "method": "auth",
            "params": {
                "api_key": self.__api_key,
                "timestamp": timestamp,
                "nonce": nonce,
                "signature": signature,
            },
        }))

        for channel in self.private_channels:
            await websocket.send(json.dumps({
                "method": "subscribe",
                "params": {
                    "channel": channel,
                },
            }))

    async def receive_message(self, websocket):
        while True:
            if not self.paused:
                message = await websocket.recv()
                message = json.loads(message)

                if 'params' in message and 'message' in message['params'] and 'channel' in message['params']:
                    data = message['params']['message']
                    channel = message['params']['channel']
                    await self.handler_dispatcher.dispatch(data, channel)
            else:
                await asyncio.sleep(1)

    async def run(self) -> None:
        """
        Start the WebSocket client.
        This method initializes the WebSocket connection and starts listening for messages.
        """
        self.logger.system.info("Starting WebSocket client...")
        async for websocket in connect(self.url):
            try:
                await asyncio.gather(self.send_public_subscriptions(websocket),
                                    self.send_private_subscriptions(websocket),
                                    self.receive_message(websocket))
            except websockets.exceptions.ConnectionClosed:
                self.logger.system.info("WebSocket connection closed.")

    @inject
    def __init__(self,
                 url: str,
                 api_key: str,
                 api_secret: str,
                 public_channels: List[str],
                 private_channels: List[str],
                 handler_dispatcher: handler_dispatcher_service.HandlerDispatcherService = Provide['handler_dispatcher']):
        """
        Initialize the WebSocket client.
        :param url: The WebSocket URL to connect to.
        :param api_key: The API key for authentication.
        :param api_secret: The API secret for authentication.
        :param public_channels: A list of public channels to subscribe to.
        :param private_channels: A list of private channels to subscribe to.
        :param handler_dispatcher: The handler dispatcher service to handle incoming messages.
        """
        super().__init__()

        self.url = url
        self.__api_key = api_key
        self.__api_secret = api_secret
        self.public_channels = public_channels
        self.private_channels = private_channels
        self.handler_dispatcher = handler_dispatcher