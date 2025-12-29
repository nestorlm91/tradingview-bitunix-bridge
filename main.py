from flask import Flask, request, jsonify
import logging
from bitunix_client import place_order

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] ✅ %(message)s")

SECURITY_TOKEN = "abc123token"  # Debe coincidir con el que usas en TradingView

@app.route("/", methods=["GET"])
def home():
    return "🚀 Bitunix TradingView Bridge activo y funcionando."

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        logging.info(f"📩 Webhook recibido: {data}")

        if data.get("token") != SECURITY_TOKEN:
            return jsonify({"error": "Token inválido"}), 403

        symbol = data.get("symbol")
        side = data.get("side")
        quantity = float(data.get("quantity", 0))
        trade_side = data.get("tradeSide", "OPEN")  # valor por defecto

        if not all([symbol, side, quantity]):
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        result = place_order(symbol, side, trade_side, quantity)
        return jsonify(result)

    except Exception as e:
        logging.error(f"❌ Error en webhook: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
