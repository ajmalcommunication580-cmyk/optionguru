from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# 🔑 YOUR DETAILS
API_KEY = "TQPLmWZm"
CLIENT_ID = "M59304123"
PASSWORD = "7869"
TOTP_SECRET = "2AQ6MINLPQLYW45T2PDVP3367I"

obj = None

# 🔐 Login
def login():
    global obj
    try:
        if obj is None:
            obj = SmartConnect(api_key=API_KEY)
            totp = pyotp.TOTP(TOTP_SECRET).now()
            obj.generateSession(CLIENT_ID, PASSWORD, totp)
        return obj
    except Exception as e:
        print("Login Error:", e)
        return None

# 📊 SmartAPI price
def get_price_smartapi(token, symbol):
    try:
        obj = login()
        if obj is None or token is None:
            return None

        data = obj.ltpData("NSE", symbol, token)

        if data and 'data' in data:
            return float(data['data']['ltp'])
        return None

    except Exception as e:
        print("SmartAPI Error:", e)
        return None

# 📊 Yahoo with history
def get_price_with_history(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="5m")

        if not data.empty:
            closes = list(data['Close'].tail(15))
            return closes[-1], closes

        return None, []

    except Exception as e:
        print("Backup Error:", e)
        return None, []

# 🧠 RSI
def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return 50

    series = pd.Series(prices)
    delta = series.diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return round(rsi.iloc[-1], 2)

# 🔥 PRO SIGNAL
def generate_signal(price, history):

    if price is None or len(history) < 10:
        return {
            "price": 0,
            "signal": "WAIT",
            "trend": "NO DATA",
            "entry": "NO TRADE",
            "confidence": 0,
            "risk": "HIGH",
            "sl": 0,
            "target": 0
        }

    rsi = calculate_rsi(history)
    avg = sum(history)/len(history)
    momentum = price - avg

    support = round(min(history), 2)
    resistance = round(max(history), 2)

    # 🚀 BREAKOUT
    if price > resistance:
        signal = "BREAKOUT BUY 🚀"
        trend = "STRONG BULLISH"
        entry = "ENTER NOW"
        confidence = 90

    elif price < support:
        signal = "BREAKDOWN SELL 🔻"
        trend = "STRONG BEARISH"
        entry = "ENTER NOW"
        confidence = 90

    # 🔥 RSI
    elif rsi < 30:
        signal = "BUY (OVERSOLD)"
        trend = "REVERSAL UP"
        entry = "SAFE ENTRY"
        confidence = 80

    elif rsi > 70:
        signal = "SELL (OVERBOUGHT)"
        trend = "REVERSAL DOWN"
        entry = "SAFE ENTRY"
        confidence = 80

    # 📊 MOMENTUM
    elif momentum > 20:
        signal = "BUY"
        trend = "BULLISH"
        entry = "WAIT FOR DIP"
        confidence = 70

    elif momentum < -20:
        signal = "SELL"
        trend = "BEARISH"
        entry = "WAIT FOR RISE"
        confidence = 70

    else:
        signal = "NO TRADE"
        trend = "SIDEWAYS"
        entry = "AVOID ⚠️"
        confidence = 60

    risk = "LOW" if confidence >= 80 else "MEDIUM"

    return {
        "price": round(price,2),
        "signal": signal,
        "trend": trend,
        "entry": entry,
        "confidence": confidence,
        "risk": risk,
        "rsi": rsi,
        "sl": support,
        "target": resistance
    }

# 🏠 Home
@app.route("/")
def home():
    return render_template("index.html")

# 🚀 APIs (अब history use होगी)

@app.route("/nifty")
def nifty():
    price, history = get_price_with_history("^NSEI")
    return jsonify(generate_signal(price, history))

@app.route("/banknifty")
def banknifty():
    price, history = get_price_with_history("^NSEBANK")
    return jsonify(generate_signal(price, history))

@app.route("/sensex")
def sensex():
    price, history = get_price_with_history("^BSESN")
    return jsonify(generate_signal(price, history))

@app.route("/finnifty")
def finnifty():
    price, history = get_price_with_history("^CNXFIN")  # ✅ FIX
    return jsonify(generate_signal(price, history))

@app.route("/midcap")
def midcap():
    price, history = get_price_with_history("^NSEMDCP50")
    return jsonify(generate_signal(price, history))

# 🔥 OPTION AI
@app.route("/option")
def option_ai():
    price, history = get_price_with_history("^NSEI")

    if price is None:
        return jsonify({
            "price": 0,
            "ce": "N/A",
            "pe": "N/A",
            "direction": "NO DATA",
            "entry": "WAIT"
        })

    rsi = calculate_rsi(history)

    ce = round(price * 0.99, 2)
    pe = round(price * 1.01, 2)

    if rsi < 35:
        direction = "BUY CE 🟢 (REVERSAL)"
        entry = "ENTER NOW"

    elif rsi > 65:
        direction = "BUY PE 🔴 (REVERSAL)"
        entry = "ENTER NOW"

    else:
        direction = "SIDEWAYS ⚠️"
        entry = "WAIT"

    return jsonify({
        "price": round(price,2),
        "ce": ce,
        "pe": pe,
        "direction": direction,
        "entry": entry
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
