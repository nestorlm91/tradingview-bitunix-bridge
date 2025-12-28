from fastapi import FastAPI, Request, HTTPException
from bitunix_client import BitunixAPI
from config import settings
import logging
from datetime import datetime
import traceback

# Configuración de logs
logging.basicConfig(
    filename=f"logs/trades_{datetime.now().date()}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Inicialización de FastAPI
app = FastAPI(title="TradingView → Bitunix Bridge")

# Inicialización del cliente Bitunix
bitunix = BitunixAPI(settings.BITUNIX_API_KEY, settings.BITUNIX_SECRET_KEY)

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    """
    Endpoint que recibe señales de TradingView y ejecuta órdenes en Bitunix.
    """
    try:
        data = await request.json()

        token = data.get("token")
        symbol = data.get("symbol")
        side = data.get("side", "").upper()
        quantity = float(data.get("quantity", 0))

        # Validar token
        if token != settings.SECURITY_TOKEN:
            logging.warning("🚫 Token inválido recibido")
            raise HTTPException(status_code=403, detail="Token inválido")

        # Validar campos requeridos
        if not all([symbol, side, quantity]):
            logging.warning("⚠️ Datos incompletos en la señal")
            raise HTTPException(status_code=400, detail="Datos incompletos")

        logging.info(f"📩 Señal recibida: {symbol} {side} {quantity}")

        # Ejecutar orden en Bitunix
        result = bitunix.place_order(symbol=symbol, side=side, quantity=quantity)

        logging.info(f"✅ Orden enviada a Bitunix: {result}")
        return {"status": "success", "details": result}

    except HTTPException as e:
        logging.error(f"❌ Error HTTP: {e.detail}")
        raise e

    except Exception as e:
        error_info = traceback.format_exc()
        logging.error(f"💥 Error inesperado procesando webhook:\n{error_info}")
        return {"status": "error", "message": str(e), "trace": error_info}
