from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp
import yfinance as yf   # ✅ FIXED

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

# 📊 SmartAPI price (FIXED)
def get_price_smartapi(token, symbol):
    try:
        obj = login()
        if obj is None or token is None:
            return None

        data = obj.ltpData("NSE", symbol, token)
        print("SMARTAPI:", data)

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

# 🧠 Final price fetch
def get_price(token, symbol, backup_symbol):
    price = get_price_smartapi(token, symbol)

    if price is None:
        print("⚠️ Using BACKUP DATA")
        price = get_price_backup(backup_symbol)

    return price

# 🏠 Homepage
@app.route("/")
def home():
    return render_template("index.html")

# 📈 Signal Logic (UPGRADED)
def generate_signal(price):
    if price is None:
        return {
            "signal": "WAIT",
            "prediction": "NO DATA",
            "entry": 0,
            "sl": 0,
            "target": 0,
            "support": 0,
            "resistance": 0,
            "confidence": 0,
            "risk": "HIGH"
        }

    support = round(price - 100, 2)
    resistance = round(price + 100, 2)

    signal = "BUY" if price > support else "SELL"

    confidence = 70 if signal == "BUY" else 60
    risk = "LOW" if confidence > 65 else "HIGH"

    return {
        "signal": signal,
        "prediction": "LIVE",
        "entry": round(price,2),
        "sl": support,
        "target": resistance,
        "support": support,
        "resistance": resistance,
        "confidence": confidence,
        "risk": risk
    }

# 🚀 NIFTY
@app.route("/nifty")
def nifty():
    price = get_price("99926000", "NIFTY", "^NSEI")
    return jsonify(generate_signal(price))

# 🚀 BANKNIFTY
@app.route("/banknifty")
def banknifty():
    price = get_price("99926009", "BANKNIFTY", "^NSEBANK")
    return jsonify(generate_signal(price))

# 🚀 SENSEX (backup only)
@app.route("/sensex")
def sensex():
    price = get_price(None, None, "^BSESN")
    return jsonify(generate_signal(price))

# 🚀 FINNIFTY
@app.route("/finnifty")
def finnifty():
    price = get_price(None, None, "^NSEFIN")
    return jsonify(generate_signal(price))

# 🚀 MIDCAP
@app.route("/midcap")
def midcap():
    price = get_price(None, None, "^NSEMDCP50")
    return jsonify(generate_signal(price))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
