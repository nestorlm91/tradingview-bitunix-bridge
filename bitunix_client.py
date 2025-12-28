from fastapi import FastAPI, Request, HTTPException
from bitunix_client import BitunixAPI
from config import settings
import logging
from datetime import datetime
from collections import deque

logging.basicConfig(
    filename=f"logs/trades_{datetime.now().date()}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="TradingView → Bitunix Bridge")

bitunix = BitunixAPI(settings.BITUNIX_API_KEY, settings.BITUNIX_SECRET_KEY)

# 🧠 Memoria temporal para evitar duplicados
recent_alerts = deque(maxlen=20)

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    try:
        data = await request.json()
        token = data.get("token")

        if token != settings.SECURITY_TOKEN:
            raise HTTPException(status_code=403, detail="Token inválido")

        symbol = data.get("symbol")
        side = data.get("side").upper()
        quantity = float(data.get("quantity", 0))
        alert_id = data.get("alert_id") or f"{symbol}-{side}-{quantity}"

        # ⚠️ Evita procesar la misma alerta más de una vez
        if alert_id in recent_alerts:
            logging.warning(f"⚠️ Alerta duplicada ignorada: {alert_id}")
            return {"status": "ignored", "reason": "duplicate"}

        recent_alerts.append(alert_id)

        logging.info(f"📩 Señal recibida: {symbol} {side} {quantity} (ID: {alert_id})")

        result = bitunix.place_order(symbol=symbol, side=side, quantity=quantity)

        logging.info(f"✅ Orden enviada a Bitunix: {result}")
        return {"status": "success", "details": result}

    except Exception as e:
        logging.error(f"❌ Error procesando webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
