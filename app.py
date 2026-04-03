from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp
import datetime

app = Flask(__name__)

# 🔑 LOGIN DETAILS
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

# ⏰ MARKET CHECK
def market_open():
    now = datetime.datetime.now()
    return now.hour >= 9 and now.hour <= 15

# 📊 GET PRICE
def get_price(token):
    try:
        obj = login()
        if obj is None:
            return None
        data = obj.ltpData("NSE", token, "")
        if data and "data" in data:
            return float(data["data"]["ltp"])
        return None
    except:
        return None

# 🧠 SIGNAL LOGIC
def signal_engine(price):
    if price is None:
        return {"signal":"WAIT","prediction":"NO DATA","entry":0,"sl":0,"target":0,"support":0,"resistance":0}

    support = round(price - 80,2)
    resistance = round(price + 80,2)

    signal = "BUY" if int(price) % 2 == 0 else "SELL"

    return {
        "signal": signal,
        "prediction": "LIVE" if market_open() else "MARKET CLOSED",
        "entry": price,
        "sl": support,
        "target": resistance,
        "support": support,
        "resistance": resistance
    }

# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")

# 📊 ROUTES
@app.route("/nifty")
def nifty():
    return jsonify(signal_engine(get_price("99926000")))

@app.route("/banknifty")
def bank():
    return jsonify(signal_engine(get_price("99926009")))

@app.route("/sensex")
def sensex():
    return jsonify(signal_engine(get_price("99919000")))

@app.route("/finnifty")
def fin():
    return jsonify(signal_engine(get_price("99926037")))

@app.route("/midcap")
def mid():
    return jsonify(signal_engine(get_price("99926074")))

# 🚀 RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
