from fastapi import FastAPI, Request, HTTPException
from bitunix_client import BitunixAPI
from config import settings
import logging
from datetime import datetime

logging.basicConfig(
    filename=f"logs/trades_{datetime.now().date()}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="TradingView → Bitunix Bridge")

bitunix = BitunixAPI(settings.BITUNIX_API_KEY, settings.BITUNIX_SECRET_KEY)

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

        if not all([symbol, side, quantity]):
            raise HTTPException(status_code=400, detail="Datos incompletos")

        logging.info(f"📩 Señal recibida: {symbol} {side} {quantity}")

        result = bitunix.place_order(symbol=symbol, side=side, quantity=quantity)

        logging.info(f"✅ Orden enviada a Bitunix: {result}")
        return {"status": "success", "details": result}

      except Exception as e:
        import traceback
        error_info = traceback.format_exc()
        logging.error(f"❌ Error procesando webhook:\n{error_info}")
        return {"status": "error", "message": str(e), "trace": error_info}
