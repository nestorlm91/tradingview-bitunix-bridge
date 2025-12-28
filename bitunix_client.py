import time
import hmac
import hashlib
import requests
import logging


class BitunixAPI:
    # 🔹 Endpoint para CopyTrading (válido para cuentas Leader Trader)
    BASE_URL = "https://copytradeapi.bitunix.com/api/v1/private"

    def __init__(self, api_key: str, secret_key: str):
        """Inicializa la conexión con la API de CopyTrading de Bitunix"""
        self.api_key = api_key
        self.secret_key = secret_key

    def _sign(self, params: dict) -> str:
        """Genera la firma HMAC SHA256 requerida por la API."""
        query = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.secret_key.encode(),
            query.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def place_order(self, symbol: str, side: str, quantity: float, order_type: str = "MARKET", leverage: int = 1):
        """
        Envía una orden a Bitunix CopyTrading.
        Requiere:
            symbol    -> Par de trading, ejemplo "LINKUSDT"
            side      -> "BUY" o "SELL"
            quantity  -> Cantidad de la orden
            order_type-> Tipo de orden, por defecto "MARKET"
            leverage  -> Apalancamiento (por defecto 1x)
        """
        endpoint = f"{self.BASE_URL}/order"

        timestamp = int(time.time() * 1000)
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "leverage": leverage,
            "quantity": quantity,
            "timestamp": timestamp
        }

        # Firma HMAC
        params["signature"] = self._sign(params)

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            logging.info(f"🚀 Enviando orden CopyTrading: {params}")
            response = requests.post(endpoint, headers=headers, json=params, timeout=10)

            logging.info(f"📩 Respuesta completa de Bitunix CopyTrading: {response.text}")

            if response.status_code != 200:
                logging.error(f"❌ Error HTTP {response.status_code}: {response.text}")
                return {"error": f"HTTP {response.status_code}", "details": response.text}

            data = response.json()
            logging.info(f"✅ Orden CopyTrading procesada correctamente: {data}")
            return data

        except requests.Timeout:
            logging.error("⚠️ Timeout al conectar con Bitunix CopyTrading")
            return {"error": "timeout"}

        except requests.RequestException as e:
            logging.error(f"❌ Error de conexión: {e}")
            return {"error": str(e)}

        except Exception as e:
            logging.error(f"💥 Error inesperado: {e}")
            return {"error": str(e)}
