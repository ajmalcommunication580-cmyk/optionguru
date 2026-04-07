from flask import Flask, jsonify, render_template
import yfinance as yf

app = Flask(__name__, template_folder="templates")

# 🔥 Fetch Data
def get_data(symbol):
    try:
        data = yf.Ticker(symbol).history(period="5d", interval="5m")
        return data
    except:
        return None

# 🤖 AI LOGIC
def ai_signal(data):
    if data is None or data.empty:
        return {"signal": "WAIT", "price": 0}

    close = data['Close']

    price = float(close.iloc[-1])
    sma_20 = close.rolling(20).mean().iloc[-1]
    sma_50 = close.rolling(50).mean().iloc[-1]

    momentum = price - close.iloc[-5]

    # 🤖 Decision Logic
    if price > sma_20 and sma_20 > sma_50 and momentum > 0:
        signal = "STRONG BUY"
        confidence = 90
    elif price > sma_20:
        signal = "BUY"
        confidence = 70
    elif price < sma_20 and sma_20 < sma_50:
        signal = "STRONG SELL"
        confidence = 90
    elif price < sma_20:
        signal = "SELL"
        confidence = 70
    else:
        signal = "HOLD"
        confidence = 50

    support = round(price - 100, 2)
    resistance = round(price + 100, 2)
    target = round(price + 150, 2)
    sl = round(price - 80, 2)

    return {
        "price": round(price,2),
        "signal": signal,
        "confidence": confidence,
        "support": support,
        "resistance": resistance,
        "target": target,
        "sl": sl
    }

# 🏠 UI
@app.route("/")
def home():
    return render_template("index.html")

# 📊 APIs
@app.route("/nifty")
def nifty():
    return jsonify(ai_signal(get_data("^NSEI")))

@app.route("/banknifty")
def banknifty():
    return jsonify(ai_signal(get_data("^NSEBANK")))

@app.route("/sensex")
def sensex():
    return jsonify(ai_signal(get_data("^BSESN")))

@app.route("/finnifty")
def finnifty():
    return jsonify(ai_signal(get_data("^CNXFIN")))

@app.route("/midcap")
def midcap():
    return jsonify(ai_signal(get_data("^NSEMDCP50")))
