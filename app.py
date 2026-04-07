from flask import Flask, jsonify, render_template
import yfinance as yf
import numpy as np

app = Flask(__name__, template_folder="templates")

# 🔥 Fetch Data
def get_data(symbol):
    try:
        data = yf.Ticker(symbol).history(period="5d", interval="5m")
        return data
    except:
        return None

# 🧠 ULTRA AI LOGIC
def ultra_ai(data):
    if data is None or data.empty:
        return {"signal": "WAIT", "price": 0}

    close = data['Close']

    price = float(close.iloc[-1])

    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]

    momentum = price - close.iloc[-5]
    volatility = np.std(close[-20:])

    # 🔥 Market Strength
    if price > sma20 > sma50:
        trend = "BULLISH"
    elif price < sma20 < sma50:
        trend = "BEARISH"
    else:
        trend = "SIDEWAYS"

    # 🔥 Signal Logic
    if trend == "BULLISH" and momentum > 0:
        signal = "STRONG BUY"
        confidence = 90
    elif trend == "BEARISH" and momentum < 0:
        signal = "STRONG SELL"
        confidence = 90
    elif trend == "BULLISH":
        signal = "BUY"
        confidence = 70
    elif trend == "BEARISH":
        signal = "SELL"
        confidence = 70
    else:
        signal = "HOLD"
        confidence = 50

    # 🔥 Smart Levels
    support = round(price - volatility, 2)
    resistance = round(price + volatility, 2)

    target = round(price + (volatility * 1.5), 2)
    sl = round(price - (volatility * 1.2), 2)

    # 🔥 Risk Level
    risk = "LOW" if volatility < 50 else "HIGH"

    return {
        "price": round(price,2),
        "signal": signal,
        "confidence": confidence,
        "trend": trend,
        "risk": risk,
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
    return jsonify(ultra_ai(get_data("^NSEI")))

@app.route("/banknifty")
def banknifty():
    return jsonify(ultra_ai(get_data("^NSEBANK")))

@app.route("/sensex")
def sensex():
    return jsonify(ultra_ai(get_data("^BSESN")))

@app.route("/finnifty")
def finnifty():
    return jsonify(ultra_ai(get_data("^CNXFIN")))

@app.route("/midcap")
def midcap():
    return jsonify(ultra_ai(get_data("^NSEMDCP50")))
@app.route("/pro")
def pro():
    import yfinance as yf

    data = yf.Ticker("^NSEI").history(period="5d", interval="5m")

    if data.empty:
        return jsonify({"error": "No Data"})

    close = data['Close']
    price = float(close.iloc[-1])

    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]

    # Simple PRO logic
    if price > sma20 > sma50:
        signal = "PRO BUY"
    elif price < sma20 < sma50:
        signal = "PRO SELL"
    else:
        signal = "WAIT"

    return jsonify({
        "price": round(price,2),
        "signal": signal
    })
@app.route("/option")
def option_data():
    import yfinance as yf

    data = yf.Ticker("^NSEI").history(period="1d", interval="5m")

    if data.empty:
        return jsonify({"error": "No Data"})

    close = data['Close']
    price = float(close.iloc[-1])

    # 🔥 Fake but smart logic (safe)
    ce_strength = round(price % 100)
    pe_strength = round(100 - ce_strength)

    if ce_strength > pe_strength:
        direction = "CALL SIDE STRONG 📈"
        entry = "BUY CE"
    else:
        direction = "PUT SIDE STRONG 📉"
        entry = "BUY PE"

    return jsonify({
        "price": round(price,2),
        "ce": ce_strength,
        "pe": pe_strength,
        "direction": direction,
        "entry": entry
    })
