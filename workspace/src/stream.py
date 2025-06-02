import os
import time
import json
import hmac
import hashlib
import websocket
import rel
import traceback

class Stream:
    ws: websocket.WebSocketApp = None
    app = None
    
    @classmethod
    def on_open(cls, ws):
        print("### websocket opened ###")

        for channel in [f"lightning_board_snapshot_{cls.app.symbol}"]:
            ws.send(json.dumps({
                "method": "subscribe",
                "params": {
                    "channel": channel,
                },
            }))
        
        # Authenticate the WebSocket connection
        api_secret = os.environ.get("BITFLYER_API_SECRET")
        timestamp = int(time.time())
        nonce = os.urandom(16).hex()
        mix = f"{timestamp}{nonce}"
        signature = hmac.new(api_secret.encode('utf-8'), mix.encode('utf-8'), hashlib.sha256).hexdigest()
        ws.send(json.dumps({
            "method": "auth",
            "params": {
                "api_key": os.environ.get("BITFLYER_API_KEY"),
                "timestamp": timestamp,
                "nonce": nonce,
                "signature": signature,
            },
        }))

        # Subscribe to private channels from here
        for channel in ["child_order_events"]:
            ws.send(json.dumps({
                "method": "subscribe",
                "params": {
                    "channel": channel,
                },
            }))

    @classmethod
    def on_message(cls, ws, msg):
        message = json.loads(msg)
        if 'params' in message and 'message' in message['params'] and 'channel' in message['params']:
            data = message['params']['message']
            channel = message['params']['channel']
            cls.app.call(data, channel=channel)

    @classmethod
    def on_error(cls, ws, err):
        print("### websocket error ###")
        print(traceback.format_exc())

    @classmethod
    def on_close(cls, ws):
        print("### websocket closed ###")

    @classmethod
    def start(cls, App):
        cls.app = App()
        cls.ws = websocket.WebSocketApp(
            os.environ.get("BITFLYER_WEBSOCKET_URL"),
            on_open=cls.on_open,
            on_message=cls.on_message,
            on_error=cls.on_error,
            on_close=cls.on_close
        )
        cls.ws.run_forever(dispatcher=rel, reconnect=5)
        rel.signal(2, rel.abort)  # Keyboard Interrupt
        rel.dispatch()