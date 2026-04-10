from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp
import yfinance as yf

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

# 🔁 Backup (Yahoo Finance)
def get_price_backup(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1m")

        if not data.empty:
            return float(data['Close'].iloc[-1])
        return None

    except Exception as e:
        print("Backup Error:", e)
        return None

# 🧠 Final price
def get_price(token, symbol, backup_symbol):
    price = get_price_smartapi(token, symbol)

    if price is None:
        price = get_price_backup(backup_symbol)

    return price

# 🏠 Homepage
@app.route("/")
def home():
    return render_template("index.html")

# 📈 Signal Logic
def generate_signal(price):
    if price is None:
        return {
            "price": 0,
            "signal": "WAIT",
            "trend": "NO DATA",
            "confidence": 0,
            "risk": "HIGH",
            "sl": 0,
            "target": 0
        }

    support = round(price - 100, 2)
    resistance = round(price + 100, 2)

    signal = "BUY" if price > support else "SELL"
    trend = "BULLISH" if signal == "BUY" else "BEARISH"
    confidence = 70 if signal == "BUY" else 60
    risk = "LOW" if confidence > 65 else "HIGH"

    return {
        "price": round(price,2),
        "signal": signal,
        "trend": trend,
        "confidence": confidence,
        "risk": risk,
        "sl": support,
        "target": resistance
    }

# 🚀 APIs
@app.route("/nifty")
def nifty():
    return jsonify(generate_signal(get_price("99926000","NIFTY","^NSEI")))

@app.route("/banknifty")
def banknifty():
    return jsonify(generate_signal(get_price("99926009","BANKNIFTY","^NSEBANK")))

@app.route("/sensex")
def sensex():
    return jsonify(generate_signal(get_price(None,None,"^BSESN")))

@app.route("/finnifty")
def finnifty():
    return jsonify(generate_signal(get_price(None,None,"^NSEFIN")))

@app.route("/midcap")
def midcap():
    return jsonify(generate_signal(get_price(None,None,"^NSEMDCP50")))

# 🔥 NEW: OPTION AI (FIX)
@app.route("/option")
def option_ai():
    price = get_price("99926000","NIFTY","^NSEI")

    if price is None:
        return jsonify({
            "price": 0,
            "ce": "N/A",
            "pe": "N/A",
            "direction": "NO DATA",
            "entry": 0
        })

    ce = round(price * 0.98,2)
    pe = round(price * 1.02,2)

    direction = "BUY CE 🟢" if price % 2 == 0 else "BUY PE 🔴"

    return jsonify({
        "price": round(price,2),
        "ce": ce,
        "pe": pe,
        "direction": direction,
        "entry": round(price,2)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
