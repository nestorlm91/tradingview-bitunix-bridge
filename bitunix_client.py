import time
import hmac
import hashlib
import requests

class BitunixAPI:
    BASE_URL = "https://api.bitunix.com/api/v1"

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key

    def _sign(self, params: dict):
        query = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.secret_key.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        return signature

    def place_order(self, symbol: str, side: str, quantity: float):
        endpoint = f"{self.BASE_URL}/order"
        timestamp = int(time.time() * 1000)

        data = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity,
            "timestamp": timestamp
        }

        signature = self._sign(data)
        data["signature"] = signature

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(endpoint, json=data, headers=headers)
        return response.json()
