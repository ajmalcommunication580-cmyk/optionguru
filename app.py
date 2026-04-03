from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp
import datetime

app = Flask(__name__)

API_KEY = "TQPLmWZm"
CLIENT_ID = "M59304123"
PASSWORD = "7869"
TOTP_SECRET = "2AQ6MINLPQLYW45T2PDVP3367I"

obj = None

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

def market_open():
    now = datetime.datetime.now()
    return now.hour >= 9 and now.hour <= 15

def get_price(token):
    try:
        obj = login()
        if obj is None:
            return None

        data = obj.ltpData("NSE", token, "")
        if data is None or 'data' not in data:
            return None

        return float(data['data']['ltp'])
    except:
        return None


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

    signal = "BUY" if int(price) % 2 == 0 else "SELL"

    return {
        "signal": signal,
        "prediction": "LIVE" if market_open() else "MARKET CLOSED",
        "entry": round(price, 2),
        "sl": round(price - 80, 2),
        "target": round(price + 80, 2),
        "support": round(price - 80, 2),
        "resistance": round(price + 80, 2)
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/nifty")
def nifty():
    price = get_price("99926000")
    return jsonify(generate_signal(price))


@app.route("/banknifty")
def banknifty():
    price = get_price("99926009")
    return jsonify(generate_signal(price))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
