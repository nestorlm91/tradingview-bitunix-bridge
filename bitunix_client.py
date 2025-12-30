import requests
import time
import hmac
import hashlib
import json
import uuid
import logging
import os

# ==========================
# Configuración de logs
# ==========================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ==========================
# Claves desde variables de entorno
# ==========================
BITUNIX_API_KEY = os.getenv("BITUNIX_API_KEY")
BITUNIX_SECRET_KEY = os.getenv("BITUNIX_SECRET_KEY")

# Endpoint de Bitunix Futures
BASE_URL = "https://fapi.bitunix.com/api/v1/futures/trade/place_order"

# Endpoint para obtener balance
BALANCE_URL = "https://fapi.bitunix.com/api/v1/futures/account/balance"


# ==========================
# Firma según documentación oficial
# ==========================
def generate_signature(api_key, secret_key, body):
    nonce = str(uuid.uuid4()).replace("-", "")
    timestamp = str(int(time.time() * 1000))

    if isinstance(body, dict):
        body_str = json.dumps(body, separators=(',', ':'))
    else:
        body_str = body.strip()

    message = f"{nonce}{timestamp}{api_key}{body_str}"
    first_hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
    final_sign = hashlib.sha256((first_hash + secret_key).encode('utf-8')).hexdigest()

    return final_sign, nonce, timestamp


# ==========================
# Obtener balance disponible (en USDT)
# ==========================
def get_balance():
    """Obtiene el balance disponible en USDT"""
    body = "{}"
    sign, nonce, timestamp = generate_signature(BITUNIX_API_KEY, BITUNIX_SECRET_KEY, body)
    headers = {
        "api-key": BITUNIX_API_KEY,
        "sign": sign,
        "nonce": nonce,
        "timestamp": timestamp,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(BALANCE_URL, headers=headers, data=body)
        data = response.json()
        usdt_balance = 0.0
        for asset in data.get("data", []):
            if asset["currency"] == "USDT":
                usdt_balance = float(asset["availableBalance"])
        logging.info(f"💰 Balance disponible USDT: {usdt_balance}")
        return usdt_balance
    except Exception as e:
        logging.error(f"❌ Error al obtener balance: {e}")
        return 0.0


# ==========================
# Enviar orden MARKET
# ==========================
def place_order(symbol, side, trade_side="OPEN"):
    """Crea una orden MARKET con todo el balance disponible."""
    balance = get_balance()
    if balance <= 0:
        logging.error("❌ No hay balance disponible para operar.")
        return None

    # Definir tamaño aproximado
    qty = round(balance / 10, 3)  # puedes ajustar la fórmula si deseas más precisión

    body_dict = {
        "symbol": symbol,
        "side": side,              # BUY o SELL
        "tradeSide": trade_side,   # OPEN o CLOSE
        "orderType": "MARKET",
        "qty": str(qty),
        "reduceOnly": trade_side == "CLOSE"
    }

    body = json.dumps(body_dict, separators=(',', ':'))
    sign, nonce, timestamp = generate_signature(BITUNIX_API_KEY, BITUNIX_SECRET_KEY, body)

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
