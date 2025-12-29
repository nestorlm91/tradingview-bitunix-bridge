import os
import time
import hmac
import hashlib
import json
import requests
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] ✅ %(message)s")

BITUNIX_API_KEY = os.getenv("BITUNIX_API_KEY")
BITUNIX_SECRET_KEY = os.getenv("BITUNIX_SECRET_KEY")

BASE_URL = "https://fapi.bitunix.com"

def generate_signature(secret, method, path, body, timestamp, nonce):
    """Genera la firma HMAC-SHA256 según la documentación oficial de Bitunix."""
    payload = f"{method}{path}{timestamp}{nonce}{body}"
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

def place_order(symbol, side, trade_side, quantity):
    """Envía una orden a Bitunix con firma y headers correctos."""
    try:
        timestamp = str(int(time.time() * 1000))
        nonce = hashlib.md5(timestamp.encode()).hexdigest()

        endpoint = "/api/v1/private/order/create"
        url = BASE_URL + endpoint

        body_dict = {
            "symbol": symbol,
            "side": side,
            "tradeSide": trade_side,
            "type": "MARKET",
            "quantity": quantity
        }
        body = json.dumps(body_dict, separators=(",", ":"))

        signature = generate_signature(
            BITUNIX_SECRET_KEY, "POST", endpoint, body, timestamp, nonce
        )

        headers = {
            "api-key": BITUNIX_API_KEY,
            "timestamp": timestamp,
            "nonce": nonce,
            "sign": signature,
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, data=body)
        result = response.json()
        logging.info(f"✅ Respuesta de Bitunix: {result}")

        return result

    except Exception as e:
        logging.error(f"❌ Error al enviar la orden a Bitunix: {e}")
        return {"error": str(e)}
