from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import logging
import json
import os

# Intentar importar el cliente Bitunix
try:
    from bitunix_client import place_order
except Exception as e:
    logging.warning(f"⚠️ Error importando bitunix_client: {e}")
    place_order = None

# Inicializar FastAPI
app = FastAPI()

# Configurar logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Token de seguridad
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "abc123token")


@app.get("/")
async def root():
    """
    Verificación de estado (Render health check)
    """
    logging.info("🟢 Solicitud recibida en '/'")
    return PlainTextResponse("Service is online 🚀")


@app.post("/webhook")
async def webhook_listener(request: Request):
    """
    Recibe alertas de TradingView y ejecuta órdenes en Bitunix.
    """
    try:
        body = await request.json()
        logging.info(f"📩 Señal recibida: {body}")

        # Validar token
        token = body.get("token")
        if token != WEBHOOK_TOKEN:
            return JSONResponse(status_code=403, content={"error": "Token inválido"})

        # Extraer parámetros
        symbol = body.get("symbol")
        side = body.get("side")
        quantity = body.get("quantity", "1")
        trade_side = body.get("tradeSide", "OPEN")
        order_type = body.get("orderType", "MARKET")

        if not symbol or not side:
            return JSONResponse(status_code=400, content={"error": "Faltan parámetros obligatorios"})

        # Verificar si el cliente está disponible
        if not place_order:
            logging.error("❌ Cliente Bitunix no disponible.")
            return JSONResponse(status_code=500, content={"error": "Cliente Bitunix no disponible"})

        # Ejecutar la orden
        result = place_order(symbol, side, quantity, order_type, trade_side)
        logging.info(f"✅ Resultado Bitunix: {result}")

        return JSONResponse(status_code=200, content={"status": "ok", "bitunix_response": result})

    except Exception as e:
        logging.exception("❌ Error interno al procesar el webhook")
        return JSONResponse(status_code=500, content={"error": str(e)})
