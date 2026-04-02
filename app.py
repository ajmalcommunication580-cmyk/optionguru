from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp
import time

app = Flask(__name__)

# 🔑 Credentials
API_KEY = "TQPLmWZm"
CLIENT_ID = "M59304123"
PASSWORD = "7869"
TOTP_SECRET = "2AQ6MINLPQLYW45T2PDVP3367I"

obj = None
last_login_time = 0

# 🔐 Smart Login (auto refresh)
def login():
    global obj, last_login_time

    if obj is None or time.time() - last_login_time > 300:
        try:
            obj = SmartConnect(api_key=API_KEY)
            totp = pyotp.TOTP(TOTP_SECRET).now()
            obj.generateSession(CLIENT_ID, PASSWORD, totp)
            last_login_time = time.time()
            print("✅ Login Success")
        except Exception as e:
            print("❌ Login Error:", e)
            obj = None

    return obj

# 📊 Safe Price Fetch
def get_price(token):
    try:
        obj = login()
        if obj is None:
            return None

        data = obj.ltpData("NSE", token, "")

        if not data or "data" not in data:
            return None

        return float(data["data"]["ltp"])

    except Exception as e:
        print("❌ Price Error:", e)
        return None

# 🧠 AI Logic (simple but stable)
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

    support = round(price - 100, 2)
    resistance = round(price + 100, 2)

    signal = "BUY" if price > support else "SELL"

    return {
        "signal": signal,
        "prediction": "LIVE",
        "entry": price,
        "sl": support,
        "target": resistance,
        "support": support,
        "resistance": resistance
    }

# 🏠 Home
@app.route("/")
def home():
    return render_template("index.html")

# 📊 Routes
@app.route("/nifty")
def nifty():
    price = get_price("99926000")
    return jsonify(generate_signal(price))

@app.route("/banknifty")
def banknifty():
    price = get_price("99926009")
    return jsonify(generate_signal(price))

@app.route("/sensex")
def sensex():
    price = get_price("99919000")
    return jsonify(generate_signal(price))

@app.route("/finnifty")
def finnifty():
    price = get_price("99926037")
    return jsonify(generate_signal(price))

@app.route("/midcap")
def midcap():
    price = get_price("99926074")
    return jsonify(generate_signal(price))

# 🚀 Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
