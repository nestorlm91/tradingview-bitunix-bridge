from flask import Flask, request, jsonify
import logging
from bitunix_client import place_order  # ✅ Importa la nueva función, no la clase

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        logging.info(f"📩 Webhook recibido: {data}")

        symbol = data.get("symbol")
        side = data.get("side")
        quantity = data.get("quantity", 0.1)
        trade_side = data.get("tradeSide", "OPEN")

        if not symbol or not side:
            return jsonify({"error": "symbol y side son requeridos"}), 400

        result = place_order(symbol, side, quantity, "MARKET", trade_side)
        logging.info(f"✅ Respuesta de Bitunix: {result}")

        return jsonify(result), 200

    except Exception as e:
        logging.error(f"❌ Error en webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return "✅ Bridge entre TradingView y Bitunix funcionando correctamente"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
