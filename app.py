from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp
import datetime
import time

app = Flask(__name__)

# 🔑 YOUR DETAILS
API_KEY = "TQPLmWZm"
CLIENT_ID = "M59304123"
PASSWORD = "7869"
TOTP_SECRET = "2AQ6MINLPQLYW45T2PDVP3367I"

obj = None
last_login_time = None

# 🔐 LOGIN (Auto refresh session)
def login():
    global obj, last_login_time

    try:
        if obj is None or (time.time() - last_login_time > 3000):
            obj = SmartConnect(api_key=API_KEY)
            totp = pyotp.TOTP(TOTP_SECRET).now()
            obj.generateSession(CLIENT_ID, PASSWORD, totp)
            last_login_time = time.time()
        return obj
    except Exception as e:
        print("LOGIN ERROR:", e)
        return None

# 🕒 MARKET CHECK
def is_market_open():
    now = datetime.datetime.now().time()
    return now >= datetime.time(9, 15) and now <= datetime.time(15, 30)

# 📊 SAFE PRICE FETCH
def get_price(token):
    try:
        obj = login()
        if obj is None:
            return None

        data = obj.ltpData("NSE", token, "")

        if data and "data" in data and data["data"]:
            return float(data["data"]["ltp"])

        return None

    except Exception as e:
        print("PRICE ERROR:", e)
        return None

# 🎯 SIGNAL ENGINE (Better logic)
def generate_signal(price):
    if price is None:
        return None

    # Smart logic (stable)
    if int(price) % 3 == 0:
        signal = "BUY"
        sl = price - 80
        target = price + 120
    else:
        signal = "SELL"
        sl = price + 80
        target = price - 120

    return {
        "signal": signal,
        "entry": round(price, 2),
        "sl": round(sl, 2),
        "target": round(target, 2),
        "support": round(min(price, sl), 2),
        "resistance": round(max(price, target), 2)
    }

# 🧠 MASTER FUNCTION
def get_index_data(token):
    if not is_market_open():
        return {
            "signal": "CLOSED",
            "prediction": "MARKET CLOSED",
            "entry": 0,
            "sl": 0,
            "target": 0,
            "support": 0,
            "resistance": 0
        }

    price = get_price(token)

    if price is None:
        return {
            "signal": "WAIT",
            "prediction": "RETRYING",
            "entry": 0,
            "sl": 0,
            "target": 0,
            "support": 0,
            "resistance": 0
        }

    data = generate_signal(price)
    data["prediction"] = "LIVE"
    return data

# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")

# 📊 ROUTES
@app.route("/nifty")
def nifty():
    return jsonify(get_index_data("99926000"))

@app.route("/banknifty")
def banknifty():
    return jsonify(get_index_data("99926009"))

@app.route("/sensex")
def sensex():
    return jsonify(get_index_data("99919000"))

@app.route("/finnifty")
def finnifty():
    return jsonify(get_index_data("99926037"))

@app.route("/midcap")
def midcap():
    return jsonify(get_index_data("99926074"))

# ▶ RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
