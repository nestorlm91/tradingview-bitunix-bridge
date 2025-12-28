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


def generate_signature(secret_key, body, nonce, timestamp):
    """
    Genera la firma HMAC SHA256 según la documentación oficial de Bitunix.
    La firma se calcula sobre la cadena: timestamp + nonce + body
    """
    message = timestamp + nonce + body
    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature


def place_order(symbol, side, quantity, order_type="MARKET", trade_side="OPEN"):
    """Envía una orden a Bitunix (futuros)."""
    body_dict = {
        "symbol": symbol,
        "side": side,  # BUY o SELL
        "tradeSide": trade_side,  # OPEN o CLOSE
        "orderType": order_type,  # MARKET o LIMIT
        "qty": str(quantity),
        "reduceOnly": False
    }

    body = json.dumps(body_dict)
    nonce = str(uuid.uuid4()).replace("-", "")
    timestamp = str(int(time.time() * 1000))
    sign = generate_signature(BITUNIX_SECRET_KEY, body, nonce, timestamp)

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
        logging.info(f"✅ Orden enviada a Bitunix: {data}")
        return data
    except Exception as e:
        logging.error(f"❌ Error al enviar orden: {e}")
        return None


if __name__ == "__main__":
    # Ejemplo de prueba directa
    result = place_order("BTCUSDT", "BUY", 0.01)
    print(result)
