from flask import Flask, jsonify, render_template
import yfinance as yf

app = Flask(__name__, template_folder="templates")

# 🔥 Fetch Price (STABLE)
def get_price(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1d", interval="5m")
        if not data.empty:
            return float(data['Close'].iloc[-1])
        return None
    except:
        return None

# 🔥 Signal Logic
def signal_logic(price):
    if price is None:
        return {"signal": "WAIT", "price": 0}

    support = round(price - 100, 2)
    resistance = round(price + 100, 2)

    signal = "BUY" if price > support else "SELL"

    return {
        "price": price,
        "signal": signal,
        "support": support,
        "resistance": resistance
    }

# 🏠 UI
@app.route("/")
def home():
    return render_template("index.html")

# 📊 APIs
@app.route("/nifty")
def nifty():
    return jsonify(signal_logic(get_price("^NSEI")))

@app.route("/banknifty")
def banknifty():
    return jsonify(signal_logic(get_price("^NSEBANK")))

@app.route("/sensex")
def sensex():
    return jsonify(signal_logic(get_price("^BSESN")))

@app.route("/finnifty")
def finnifty():
    return jsonify(signal_logic(get_price("^CNXFIN")))

@app.route("/midcap")
def midcap():
    return jsonify(signal_logic(get_price("^NSEMDCP50")))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
