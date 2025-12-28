import logging
import traceback
from fastapi import FastAPI, Request, HTTPException
from bitunix_client import BitunixAPI
import os

# ===============================
# CONFIGURACIÓN BÁSICA DEL LOG
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ===============================
# CONFIGURACIÓN GLOBAL
# ===============================
BITUNIX_API_KEY = os.getenv("BITUNIX_API_KEY")
BITUNIX_SECRET_KEY = os.getenv("BITUNIX_SECRET_KEY")
SECURITY_TOKEN = os.getenv("WEBHOOK_TOKEN", "abc123token")  # Token de seguridad para TradingView

bitunix = BitunixAPI(BITUNIX_API_KEY, BITUNIX_SECRET_KEY)
app = FastAPI(title="TradingView ↔ Bitunix Bridge")

# ===============================
# RUTA PRINCIPAL PARA TRADINGVIEW
# ===============================
@app.post("/webhook")
async def tradingview_webhook(request: Request):
    try:
        data = await request.json()
        logging.info(f"📩 Webhook recibido: {data}")

        # === Validar token ===
        token = data.get("token")
        if token != SECURITY_TOKEN:
            logging.warning("🚫 Token inválido recibido")
            raise HTTPException(status_code=403, detail="Token inválido")

        # === Extraer datos de la alerta ===
        symbol = data.get("symbol")
        side = data.get("side", "").upper()
        quantity = float(data.get("quantity", 0))

        # Validar datos
        if not all([symbol, side, quantity]):
            raise HTTPException(status_code=400, detail="Datos incompletos en la alerta")

        # === Enviar orden a Bitunix ===
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


# ===============================
# RUTA DE PRUEBA
# ===============================
@app.get("/")
async def root():
    return {"message": "🚀 Bitunix Bridge funcionando correctamente"}
