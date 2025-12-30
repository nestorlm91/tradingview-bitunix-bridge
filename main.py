from fastapi import FastAPI, Request, HTTPException
from bitunix_client import place_order
import logging
from datetime import datetime

# Configuración de logs
logging.basicConfig(
    filename=f"logs/trades_{datetime.now().date()}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="TradingView → Bitunix Bridge")

SECURITY_TOKEN = "secreto123"

# Mantener estado actual
current_position = None  # Puede ser "LONG", "SHORT" o None


@app.post("/webhook")
async def tradingview_webhook(request: Request):
    global current_position
    try:
        data = await request.json()
        token = data.get("token")

        if token != SECURITY_TOKEN:
            raise HTTPException(status_code=403, detail="Token inválido")

        symbol = data.get("symbol", "LINKUSDT")
        side = data.get("side", "").upper()

        if side not in ["BUY", "SELL", "CLOSE"]:
            raise HTTPException(status_code=400, detail="Dirección no válida")

        logging.info(f"📩 Señal recibida: {symbol} → {side}")

        # Lógica para abrir o cerrar operaciones
        if side == "BUY":
            if current_position == "SHORT":
                place_order(symbol, "BUY", "CLOSE")
            place_order(symbol, "BUY", "OPEN")
            current_position = "LONG"

        elif side == "SELL":
            if current_position == "LONG":
                place_order(symbol, "SELL", "CLOSE")
            place_order(symbol, "SELL", "OPEN")
            current_position = "SHORT"

        elif side == "CLOSE":
            if current_position == "LONG":
                place_order(symbol, "SELL", "CLOSE")
            elif current_position == "SHORT":
                place_order(symbol, "BUY", "CLOSE")
            current_position = None

        logging.info(f"✅ Nueva posición: {current_position}")
        return {"status": "success", "position": current_position}

    except Exception as e:
        logging.error(f"❌ Error procesando webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
