import time
import hmac
import hashlib
import requests
import json
import logging
import uuid

class BitunixAPI:
    BASE_URL = "https://fapi.bitunix.com/api/v1/private"

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key

    def _generate_signature(self, params: dict, nonce: str, timestamp: str) -> str:
        """
        Genera la firma HMAC SHA256 con los parámetros, nonce y timestamp.
        """
        query_string = json.dumps(params, separators=(',', ':'), sort_keys=True)
        message = f"{nonce}{timestamp}{query_string}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def place_order(self, symbol: str, side: str, quantity: float, order_type: str = "MARKET"):
        """
        Crea una orden en Bitunix (CopyTrading o Futuros) con firma autenticada.
        """
        endpoint = f"{self.BASE_URL}/order"
        timestamp = str(int(time.time() * 1000))
        nonce = uuid.uuid4().hex  # genera cadena aleatoria de 32 caracteres

        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),  # BUY o SELL
            "type": order_type,    # MARKET, LIMIT, etc.
            "quantity": quantity
        }

        sign = self._generate_signature(params, nonce, timestamp)

        headers = {
            "api-key": self.api_key,
            "nonce": nonce,
            "timestamp": timestamp,
            "sign": sign,
            "Content-Type": "application/json"
        }

        try:
            logging.info(f"🚀 Enviando orden a Bitunix: {params}")
            response = requests.post(endpoint, headers=headers, json=params, timeout=10)

            if response.status_code != 200:
                logging.error(f"❌ Error HTTP {response.status_code}: {response.text}")
                return {"error": f"HTTP {response.status_code}", "details": response.text}

            data = response.json()
            logging.info(f"✅ Respuesta de Bitunix: {data}")
            return data

        except requests.Timeout:
            logging.error("⚠️ Timeout al conectar con Bitunix.")
            return {"error": "timeout"}

        except Exception as e:
            logging.error(f"❌ Error inesperado: {e}")
            return {"error": str(e)}
