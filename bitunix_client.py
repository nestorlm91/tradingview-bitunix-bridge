import requests
import time
import hmac
import hashlib
import json
import uuid
import logging
import os

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BITUNIX_API_KEY = os.getenv("BITUNIX_API_KEY")
BITUNIX_SECRET_KEY = os.getenv("BITUNIX_SECRET_KEY")

BASE_URL = "https://fapi.bitunix.com/api/v1/futures/trade/place_order"


def generate_signature(secret_key, params: dict, body: str):
    """
    Genera la firma HMAC SHA256 según el formato más reciente de Bitunix.
    La cadena a firmar debe incluir: timestamp + nonce + api-key + body
    """
    parts = [
        params.get("timestamp", ""),
        params.get("nonce", ""),
        params.get("api-key", ""),
        body
    ]
    message = "".join(parts)
    signature = hmac.new(secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature


def place_order(symbol, side, quantity, order_type="MARKET", trade_side="OPEN"):
    """Envía una orden a Bitunix (futuros)."""
    body_dict = {
        "symbol": symbol,
        "side": side,           # BUY o SELL
        "tradeSide": trade_side,  # OPEN o CLOSE
        "orderType": order_type,  # MARKET o LIMIT
        "qty": str(quantity),
        "reduceOnly": False
    }

    body = json.dumps(body_dict)
    nonce = str(uuid.uuid4()).replace("-", "")
    timestamp = str(int(time.time() * 1000))

    params = {
        "api-key": BITUNIX_API_KEY,
        "timestamp": timestamp,
        "nonce": nonce
    }

    sign = generate_signature(BITUNIX_SECRET_KEY, params, body)

    headers = {
        "api-key": BITUNIX_API_KEY,
        "sign": sign,
        "nonce": nonce,
        "timestamp": timestamp,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(BASE_URL, headers=headers, data=body)
        data = response.json()
        logging.info(f"✅ Respuesta de Bitunix: {data}")
        return data
    except Exception as e:
        logging.error(f"❌ Error al enviar orden: {e}")
        return None


if __name__ == "__main__":
    # Prueba directa (ajusta a un par válido)
    result = place_order("BTCUSDT", "BUY", 0.01)
    print(result)
