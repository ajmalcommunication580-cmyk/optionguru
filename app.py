from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp

app = Flask(__name__)

API_KEY = "TQPLmWZm"
CLIENT_ID = "M59304123"
PASSWORD = "7869"
TOTP_SECRET = "2AQ6MINLPQLYW45T2PDVP3367I"

obj = None

def login():
    global obj
    if obj is None:
        obj = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        obj.generateSession(CLIENT_ID, PASSWORD, totp)
    return obj

def get_price(token):
    try:
        obj = login()
        data = obj.ltpData("NSE", token, "")
        
        if data and "data" in data and data["data"]:
            return float(data["data"]["ltp"])
        else:
            return None
    except:
        return None

def calculate_signal(price):
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

    return {
        "signal": "BUY" if price % 2 == 0 else "SELL",
        "prediction": "LIVE",
        "entry": price,
        "sl": round(price - 50, 2),
        "target": round(price + 100, 2),
        "support": round(price - 100, 2),
        "resistance": round(price + 100, 2)
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/nifty")
def nifty():
    return jsonify(calculate_signal(get_price("99926000")))

@app.route("/banknifty")
def banknifty():
    return jsonify(calculate_signal(get_price("99926009")))

@app.route("/sensex")
def sensex():
    return jsonify(calculate_signal(get_price("99919000")))

@app.route("/finnifty")
def finnifty():
    return jsonify(calculate_signal(get_price("99926037")))

@app.route("/midcap")
def midcap():
    return jsonify(calculate_signal(get_price("99926074")))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
