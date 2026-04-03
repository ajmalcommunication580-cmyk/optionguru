from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp
import datetime
import time

app = Flask(__name__)

# 🔑 Credentials
API_KEY = "TQPLmWZm"
CLIENT_ID = "M59304123"
PASSWORD = "7869"
TOTP_SECRET = "2AQ6MINLPQLYW45T2PDVP3367I"

obj = None

# 🔐 LOGIN (AUTO RETRY)
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
        return login()

# ⏰ MARKET STATUS
def market_open():
    now = datetime.datetime.now().time()
    return now >= datetime.time(9,15) and now <= datetime.time(15,30)

# 📊 PRICE FETCH SAFE
def get_price(token):
    try:
        obj = login()
        data = obj.ltpData("NSE", token, "")
        if data and data.get("data"):
            return float(data['data']['ltp'])
    except:
        return None

# 📈 SIGNAL LOGIC (REAL)
def generate_signal(price):
    if price is None:
        return None

    # simple trend logic
    last = price
    support = round(price - 80, 2)
    resistance = round(price + 80, 2)

    signal = "BUY" if price > (support + 40) else "SELL"

    return {
        "signal": signal,
        "prediction": "LIVE",
        "entry": round(price,2),
        "sl": support,
        "target": resistance,
        "support": support,
        "resistance": resistance
    }

# 🔁 MASTER FUNCTION
def get_data(token):
    if not market_open():
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

    return generate_signal(price)

# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")

# 📊 ROUTES
@app.route("/nifty")
def nifty():
    return jsonify(get_data("99926000"))

@app.route("/banknifty")
def banknifty():
    return jsonify(get_data("99926009"))

@app.route("/sensex")
def sensex():
    return jsonify(get_data("99919000"))

@app.route("/finnifty")
def finnifty():
    return jsonify(get_data("99926037"))

@app.route("/midcap")
def midcap():
    return jsonify(get_data("99926074"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
