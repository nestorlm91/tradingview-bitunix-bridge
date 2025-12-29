import requests
import time
import hmac
import hashlib
import json
import uuid
import logging
import os
from urllib.parse import urlencode

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BITUNIX_API_KEY = os.getenv("BITUNIX_API_KEY")
BITUNIX_SECRET_KEY = os.getenv("BITUNIX_SECRET_KEY")

BASE_URL = "https://fapi.bitunix.com/api/v1/futures/trade/place_order"


def generate_signature(secret_key, params: dict) -> str:
    """Genera la firma HMAC SHA256 según el estándar Bitunix."""
    # Ordenar alfabéticamente los parámetros
    sorted_params = dict(sorted(params.items()))
    query_string = urlencode(sorted_params)
    signature = hmac.new(secret_key.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature


def place_order(symbol: str, side: str, quantity: float, order_type="MARKET", trade_side="OPEN"):
    """Envía una orden a Bitunix Futures."""
    nonce = str(uuid.uuid4()).replace("-", "")
    timestamp = str(int(time.time() * 1000))

    # Parámetros de la orden
    params = {
        "symbol": symbol,
        "side": side,           # BUY o SELL
        "tradeSide": trade_side,  # OPEN o CLOSE
        "orderType": order_type,  # MARKET o LIMIT
        "qty": str(quantity),
        "reduceOnly": "false",
        "timestamp": timestamp,
        "nonce": nonce
    }

    sign = generate_signature(BITUNIX_SECRET_KEY, params)
    headers = {
        "api-key": BITUNIX_API_KEY,
        "sign": sign,
        "nonce": nonce,
        "timestamp": timestamp,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=params)
        data = response.json()
        logging.info(f"✅ Orden enviada a Bitunix: {data}")
        return data
    except Exception as e:
        logging.error(f"❌ Error al enviar orden: {e}")
        return None


if __name__ == "__main__":
    # Prueba directa
    result = place_order("LINKUSDT", "BUY", 0.1)
    print(result)
