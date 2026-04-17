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

# 📊 SmartAPI price (LIVE)
def get_price_smartapi(token, symbol):
    try:
        obj = login()
        if obj is None:
            return None

        data = obj.ltpData("NSE", symbol, token)
        if data and 'data' in data:
            return float(data['data']['ltp'])
        return None

    except Exception as e:
        print("SmartAPI Error:", e)
        return None

# 📊 Yahoo history
def get_price_with_history(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="5m")

        if not data.empty:
            closes = list(data['Close'].tail(20))
            return closes

        return []

    except Exception as e:
        print("Yahoo Error:", e)
        return []

# 🧠 RSI
def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return 50

    series = pd.Series(prices)
    delta = series.diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return round(rsi.iloc[-1], 2)

# 🔥 HYBRID PRICE (LIVE + HISTORY)
def get_price_full(token, symbol, yahoo_symbol):
    price = get_price_smartapi(token, symbol)
    history = get_price_with_history(yahoo_symbol)

    return price, history

# 🔥 PRO AI SIGNAL
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

    high = max(history)
    low = min(history)
    range_val = high - low

    support = round(low, 2)
    resistance = round(high, 2)

    zone = range_val * 0.15

    # 🚀 BREAKOUT
    if price > resistance + zone:
        signal = "STRONG BREAKOUT BUY 🚀"
        trend = "STRONG BULLISH"
        entry = "ENTER NOW 🟢"
        confidence = 90

    elif price < support - zone:
        signal = "STRONG BREAKDOWN SELL 🔻"
        trend = "STRONG BEARISH"
        entry = "ENTER NOW 🔴"
        confidence = 90

    # 🔄 REVERSAL
    elif rsi < 30:
        signal = "BUY (OVERSOLD)"
        trend = "REVERSAL UP"
        entry = "BUY ON DIP 🟢"
        confidence = 80

    elif rsi > 70:
        signal = "SELL (OVERBOUGHT)"
        trend = "REVERSAL DOWN"
        entry = "SELL ON RISE 🔴"
        confidence = 80

    # 📊 SIDEWAYS
    elif support + zone < price < resistance - zone:
        signal = "NO TRADE"
        trend = "SIDEWAYS"
        entry = "AVOID ⚠️"
        confidence = 60

    else:
        signal = "WAIT"
        trend = "NEUTRAL"
        entry = "WAIT"
        confidence = 65

    # 🎯 Risk
    if confidence >= 85:
        risk = "LOW"
    elif confidence >= 70:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

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

# 🚀 APIs

@app.route("/nifty")
def nifty():
    price, history = get_price_full("99926000","NIFTY","^NSEI")
    return jsonify(generate_signal(price, history))

@app.route("/banknifty")
def banknifty():
    price, history = get_price_full("99926009","BANKNIFTY","^NSEBANK")
    return jsonify(generate_signal(price, history))

@app.route("/sensex")
def sensex():
    price, history = get_price_full("99919000","SENSEX","^BSESN")
    return jsonify(generate_signal(price, history))

@app.route("/finnifty")
def finnifty():
    price, history = get_price_full("99926037","FINNIFTY","^NSEFIN")
    return jsonify(generate_signal(price, history))

@app.route("/midcap")
def midcap():
    price, history = get_price_full("99926012","MIDCPNIFTY","^NSEMDCP50")
    return jsonify(generate_signal(price, history))

# 🔥 OPTION AI
@app.route("/option")
def option_ai():
    price, history = get_price_full("99926000","NIFTY","^NSEI")

    if price is None or len(history) < 10:
        return jsonify({
            "price": 0,
            "ce": "N/A",
            "pe": "N/A",
            "direction": "NO DATA",
            "entry": "WAIT"
        })

    rsi = calculate_rsi(history)
    avg = sum(history)/len(history)

    ce = round(price * 0.99, 2)
    pe = round(price * 1.01, 2)

    if rsi < 30 and price < avg:
        direction = "BUY CE 🟢 (REVERSAL)"
        entry = "ENTER NOW"

    elif rsi > 70 and price > avg:
        direction = "BUY PE 🔴 (REVERSAL)"
        entry = "ENTER NOW"

    else:
        direction = "NO CLEAR SIGNAL ⚠️"
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
