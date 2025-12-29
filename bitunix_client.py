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


# ==========================
# Función de firma oficial Bitunix
# ==========================
def generate_signature(api_key, secret_key, body):
    """
    Genera la firma de acuerdo con el formato oficial de Bitunix:
    nonce + timestamp + api_key + body_json (minificado)
    Luego aplica doble SHA256: primero al mensaje y luego al resultado + secret_key
    """
    # Nonce aleatorio de 32 caracteres
    nonce = str(uuid.uuid4()).replace("-", "")

    # Timestamp en milisegundos (UTC)
    timestamp = str(int(time.time() * 1000))

    # Convertir body a JSON minificado
    if isinstance(body, dict):
        body_str = json.dumps(body, separators=(',', ':'))
    else:
        body_str = body.strip()

    # Concatenación exacta según documentación
    message = f"{nonce}{timestamp}{api_key}{body_str}"

    # Primer hash SHA256
    first_hash = hashlib.sha256(message.encode('utf-8')).hexdigest()

    # Segundo hash con secret key
    final_sign = hashlib.sha256((first_hash + secret_key).encode('utf-8')).hexdigest()

    return final_sign, nonce, timestamp


# ==========================
# Función para enviar una orden
# ==========================
def place_order(symbol, side, quantity, order_type="MARKET", trade_side="OPEN"):
    """
    Envía una orden al endpoint de Bitunix Futures
    """
    body_dict = {
        "symbol": symbol,
        "side": side,              # BUY o SELL
        "tradeSide": trade_side,   # OPEN o CLOSE
        "orderType": order_type,   # MARKET o LIMIT
        "qty": str(quantity),      # En formato string (Bitunix lo requiere)
        "reduceOnly": False
    }

    # Convertir body a JSON
    body = json.dumps(body_dict, separators=(',', ':'))

    # Generar firma
    sign, nonce, timestamp = generate_signature(BITUNIX_API_KEY, BITUNIX_SECRET_KEY, body)

    headers = {
        "api-key": BITUNIX_API_KEY,
        "sign": sign,
        "nonce": nonce,
        "timestamp": timestamp,
        "Content-Type": "application/json"
    }

    # ==========================
    # Logs de depuración (clave para diagnosticar)
    # ==========================
    logging.info("🚀 Enviando orden a Bitunix...")
    logging.info(f"URL: {BASE_URL}")
    logging.info(f"Headers enviados: {headers}")
    logging.info(f"Body enviado: {body}")

    # ==========================
    # Envío de la solicitud
    # ==========================
    try:
        response = requests.post(BASE_URL, headers=headers, data=body)
        data = response.json()
        logging.info(f"✅ Respuesta de Bitunix: {data}")
        return data
    except Exception as e:
        logging.error(f"❌ Error al enviar orden: {e}")
        return None


# ==========================
# Ejecución directa de prueba
# ==========================
if __name__ == "__main__":
    logging.info("🧪 Prueba local de orden de mercado...")
    result = place_order("LINKUSDT", "BUY", "0.1")
    print(result)
