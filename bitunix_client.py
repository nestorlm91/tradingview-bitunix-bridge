import time
import hmac
import hashlib
import requests
import logging


class BitunixAPI:
    BASE_URL = "https://api.bitunix.com/openapi"

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key

    def _sign(self, params: dict):
        """Genera la firma HMAC SHA256 requerida por la API."""
        query = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.secret_key.encode(),
            query.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def place_order(self, symbol: str, side: str, quantity: float):
        """Crea una orden en Bitunix con manejo de errores y logs claros."""
        endpoint = f"{self.BASE_URL}/spot/v1/trade/order"

        # Parámetros de la orden
        timestamp = int(time.time() * 1000)
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity,
            "timestamp": timestamp
        }

        # Firma
        params["signature"] = self._sign(params)

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            logging.info(f"🚀 Enviando orden a Bitunix: {params}")
            response = requests.post(endpoint, headers=headers, json=params, timeout=8)

            if response.status_code != 200:
                logging.error(f"❌ Error HTTP {response.status_code}: {response.text}")
                return {"error": f"HTTP {response.status_code}", "details": response.text}

            data = response.json()

            # Confirmar si la API respondió correctamente
            if data.get("code") != 0:
                logging.error(f"⚠️ Error de Bitunix: {data}")
                return {"error": "Bitunix API", "details": data}

            logging.info(f"✅ Orden ejecutada correctamente: {data}")
            return data

        except requests.Timeout:
            logging.error("⚠️ Timeout al conectar con Bitunix (tardó más de 8s)")
            return {"error": "timeout"}

        except requests.RequestException as e:
            logging.error(f"❌ Error de conexión: {e}")
            return {"error": str(e)}

        except Exception as e:
            logging.error(f"💥 Excepción inesperada: {e}")
            return {"error": str(e)}
