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

# 🔥 ULTRA SIGNAL LOGIC
def generate_signal(price):
    if price is None:
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

    support = round(price - 100, 2)
    resistance = round(price + 100, 2)

    # 🔥 Logic Upgrade
    if price > resistance - 20:
        signal = "STRONG BUY 🔥"
        trend = "BULLISH 📈"
        entry = "ENTER NOW 🟢"
        confidence = 85

    elif price > support:
        signal = "BUY"
        trend = "BULLISH"
        entry = "WAIT FOR BREAKOUT ⏳"
        confidence = 70

    elif price < support + 20:
        signal = "STRONG SELL 🔻"
        trend = "BEARISH 📉"
        entry = "ENTER NOW 🔴"
        confidence = 85

    else:
        signal = "SELL"
        trend = "BEARISH"
        entry = "WAIT ⏳"
        confidence = 65

    risk = "LOW" if confidence >= 80 else "MEDIUM" if confidence >= 70 else "HIGH"

    return {
        "price": round(price,2),
        "signal": signal,
        "trend": trend,
        "entry": entry,
        "confidence": confidence,
        "risk": risk,
        "sl": support,
        "target": resistance
    }

# 🚀 APIs (SmartAPI FIXED TOKENS)

@app.route("/nifty")
def nifty():
    return jsonify(generate_signal(get_price("99926000","NIFTY","^NSEI")))

@app.route("/banknifty")
def banknifty():
    return jsonify(generate_signal(get_price("99926009","BANKNIFTY","^NSEBANK")))

# 🔥 FIXED SENSEX
@app.route("/sensex")
def sensex():
    return jsonify(generate_signal(get_price("99919000","SENSEX","^BSESN")))

# 🔥 FIXED FINNIFTY
@app.route("/finnifty")
def finnifty():
    return jsonify(generate_signal(get_price("99926037","FINNIFTY","^NSEFIN")))

# 🔥 FIXED MIDCAP
@app.route("/midcap")
def midcap():
    return jsonify(generate_signal(get_price("99926012","MIDCPNIFTY","^NSEMDCP50")))

# 🔥 OPTION AI UPGRADE
@app.route("/option")
def option_ai():
    price = get_price("99926000","NIFTY","^NSEI")

    if price is None:
        return jsonify({
            "price": 0,
            "ce": "N/A",
            "pe": "N/A",
            "direction": "NO DATA",
            "entry": "WAIT"
        })

    ce_strength = int(price % 100)
    pe_strength = 100 - ce_strength

    if ce_strength > pe_strength:
        direction = "CALL SIDE STRONG 📈"
        entry = "BUY CE 🟢"
    else:
        direction = "PUT SIDE STRONG 📉"
        entry = "BUY PE 🔴"

    return jsonify({
        "price": round(price,2),
        "ce": ce_strength,
        "pe": pe_strength,
        "direction": direction,
        "entry": entry
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
