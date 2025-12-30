from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import json
from bitunix_client import place_order

# Crear app FastAPI
app = FastAPI()

# Configurar logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Token de seguridad del webhook
WEBHOOK_TOKEN = "abc123token"

@app.post("/webhook")
async def webhook_listener(request: Request):
    """
    Endpoint principal para recibir alertas desde TradingView
    """
    try:
        body = await request.json()
        logging.info(f"📩 Señal recibida: {body}")

        # Validar token
        token = body.get("token")
        if token != WEBHOOK_TOKEN:
            logging.warning("🚫 Token inválido recibido.")
            return JSONResponse(status_code=403, content={"error": "Token inválido"})

        # Obtener parámetros
        symbol = body.get("symbol")
        side = body.get("side")
        quantity = body.get("quantity", "1")
        trade_side = body.get("tradeSide", "OPEN")
        order_type = body.get("orderType", "MARKET")

        if not symbol or not side:
            return JSONResponse(status_code=400, content={"error": "Faltan parámetros obligatorios"})

        # Enviar orden a Bitunix
        logging.info(f"🚀 Enviando orden: {symbol} | {side} | {trade_side} | {order_type} | qty={quantity}")
        result = place_order(symbol, side, quantity, order_type, trade_side)

        logging.info(f"✅ Resultado Bitunix: {result}")
        return JSONResponse(status_code=200, content={"status": "ok", "bitunix_response": result})

    except Exception as e:
        logging.exception("❌ Error al procesar el webhook")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def root():
    """
    Endpoint base para confirmar que el servidor está activo
    """
    return {"status": "online", "message": "🚀 Webhook Bitunix Bridge operativo y listo para recibir señales"}
