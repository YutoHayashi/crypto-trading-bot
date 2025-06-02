from typing import Literal
import os
import datetime
import json
import requests
import hashlib
import hmac

class BitflyerClient:
    def __init__(self):
        self.api_key = os.environ.get("BITFLYER_API_KEY")
        self.api_secret = os.environ.get("BITFLYER_API_SECRET")
        self.base_url = os.environ.get("BITFLYER_BASE_URL")

    def get_ticker(self, symbol: str) -> dict:
        path = "/v1/getticker"
        params = {"product_code": symbol}
        response = requests.get(self.base_url + path, params=params)
        return response.json()

    def get_balance(self) -> dict:
        path = "/v1/me/getbalance"
        headers = self._get_auth_headers('get', path)
        response = requests.get(self.base_url + path, headers=headers)
        return response.json()

    def create_order(self, symbol: str, side: Literal["buy", "sell"], size: float, price: float = None, order_type: str = Literal["limit", "market"]) -> dict:
        path = "/v1/me/sendchildorder"
        data = json.dumps({
            "product_code": symbol,
            "child_order_type": order_type.upper(),
            "side": side.upper(),
            "price": price,
            "size": size,
        })
        headers = self._get_auth_headers('post', path, data)
        response = requests.post(self.base_url + path, data=data, headers=headers)
        return response.json()

    def cancel_order(self, order_id: str, symbol: str = None) -> dict:
        path = '/v1/me/cancelchildorder'
        data = json.dumps({
            "product_code": symbol,
            "child_order_id": order_id,
        })
        headers = self._get_auth_headers('post', path, data)
        response = requests.post(self.base_url + path, data=data, headers=headers)
        return response.json()
    
    def _get_auth_headers(self, method: Literal["post", "get"], path: str, data: str = '') -> dict:
        timestamp = str(datetime.datetime.today())
        mix = f"{timestamp}{method.upper()}{path}{data}"
        signature = hmac.new(self.api_secret.encode('utf-8'), mix.encode('utf-8'), hashlib.sha256).hexdigest()
        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-SIGN": signature,
            "Content-Type": 'application/json',
        }