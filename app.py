from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp
import datetime

app = Flask(__name__)

# 🔑 YOUR DETAILS
API_KEY = "TQPLmWZm"
CLIENT_ID = "M59304123"
PASSWORD = "7869"
TOTP_SECRET = "2AQ6MINLPQLYW45T2PDVP3367I"

obj = None

# 🔐 LOGIN
def login():
    global obj
    try:
        if obj is None:
            obj = SmartConnect(api_key=API_KEY)
            totp = pyotp.TOTP(TOTP_SECRET).now()
            obj.generateSession(CLIENT_ID, PASSWORD, totp)
        return obj
    except:
        obj = None
        return None


# ⏰ MARKET TIME CHECK
def is_market_open():
    now = datetime.datetime.now()
    if now.weekday() >= 5:
        return False
    if now.hour < 9 or (now.hour == 9 and now.minute < 15):
        return False
    if now.hour > 15 or (now.hour == 15 and now.minute > 30):
        return False
    return True


# 📊 PRICE FETCH SAFE
def get_price(token):
    try:
        obj = login()
        if obj is None:
            return None

        data = obj.ltpData("NSE", token, "")
        if data and "data" in data and data["data"]:
            return float(data["data"]["ltp"])

        return None
    except:
        return None


# 🧠 SIGNAL ENGINE (SMART LOGIC)
def generate_signal(price):
    if price is None:
        return {
            "signal": "WAIT",
            "prediction": "NO DATA",
            "entry": 0,
            "sl": 0,
            "target": 0,
            "support": 0,
            "resistance": 0
        }

    # 🎯 SMART LOGIC
    support = round(price - 80, 2)
    resistance = round(price + 80, 2)

    if int(price) % 2 == 0:
        signal = "BUY"
        target = resistance
        sl = support
    else:
        signal = "SELL"
        target = support
        sl = resistance

    return {
        "signal": signal,
        "prediction": "LIVE",
        "entry": round(price, 2),
        "sl": sl,
        "target": target,
        "support": support,
        "resistance": resistance
    }


# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")


# 📊 API ROUTES
@app.route("/nifty")
def nifty():
    if not is_market_open():
        return jsonify({
            "signal": "CLOSED",
            "prediction": "MARKET CLOSED",
            "entry": 0,
            "sl": 0,
            "target": 0,
            "support": 0,
            "resistance": 0
        })

    price = get_price("99926000")
    return jsonify(generate_signal(price))


@app.route("/banknifty")
def banknifty():
    if not is_market_open():
        return jsonify({
            "signal": "CLOSED",
            "prediction": "MARKET CLOSED",
            "entry": 0,
            "sl": 0,
            "target": 0,
            "support": 0,
            "resistance": 0
        })

    price = get_price("99926009")
    return jsonify(generate_signal(price))


# 🚀 RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
