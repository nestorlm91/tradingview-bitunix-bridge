from fastapi import FastAPI, Request, HTTPException
import logging
import os
import traceback
from bitunix_client import BitunixAPI
from config import settings

# Configurar logs
logging.basicConfig(
    filename=f"logs/webhook_{os.path.basename(__file__)}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI(title="TradingView → Bitunix Bridge")

# Inicializar cliente Bitunix
bitunix = BitunixAPI(
    api_key=settings.BITUNIX_API_KEY,
    secret_key=settings.BITUNIX_SECRET_KEY
)


@app.post("/webhook")
async def tradingview_webhook(request: Request):
    """
    Endpoint que recibe alertas de TradingView y ejecuta órdenes en Bitunix.
    """
    try:
        data = await request.json()
        logging.info(f"📩 Webhook recibido: {data}")

        # Extraer datos del mensaje
        token = data.get("token", "").strip()
        symbol = data.get("symbol", "").strip()
        side = data.get("side", "").upper().strip()
        quantity = float(data.get("quantity", 0))

        # Validar token directamente desde variables de entorno
        expected_token = os.getenv("SECURITY_TOKEN")
        logging.info(f"🧩 Token recibido: {token}, Token esperado: {expected_token}")

        if not expected_token:
            logging.error("⚠️ SECURITY_TOKEN no configurado en Render")
            raise HTTPException(status_code=500, detail="Token no configurado en el servidor")

        if token != expected_token:
            logging.warning("🚫 Token inválido o no coincide con el configurado en Render")
            raise HTTPException(status_code=403, detail="Token inválido")

        # Validar campos requeridos
        if not all([symbol, side, quantity]):
            logging.warning("⚠️ Datos incompletos en el webhook")
            raise HTTPException(status_code=400, detail="Datos incompletos")

        # Enviar orden a Bitunix
        logging.info(f"🚀 Enviando orden a Bitunix: {side} {quantity} {symbol}")
        result = bitunix.place_order(symbol, side, quantity)

        logging.info(f"✅ Orden enviada a Bitunix: {result}")
        return {"status": "success", "details": result}

    except HTTPException as e:
        logging.error(f"❌ Error HTTP: {e.detail}")
        raise e

    except Exception as e:
        error_info = traceback.format_exc()
        logging.error(f"💥 Error inesperado procesando webhook:\n{error_info}")
        return {"status": "error", "message": str(e), "trace": error_info}


@app.get("/")
def root():
    return {"message": "🚀 TradingView → Bitunix Bridge activo y listo."}
