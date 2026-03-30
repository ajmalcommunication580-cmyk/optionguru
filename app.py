from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp

app = Flask(__name__)

# 🔑 YOUR DETAILS
API_KEY = "TQPLmWZm"
CLIENT_ID = "M59304123"
PASSWORD = "7869"
TOTP_SECRET = "2AQ6MINLPQLYW45T2PDVP3367I"   # ⚠️ Google Authenticator wala secret

obj = None

# 🔐 Login once (important)
def login():
    global obj
    if obj is None:
        obj = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        obj.generateSession(CLIENT_ID, PASSWORD, totp)
    return obj

# 📊 Price fetch
def get_price(token):
    obj = login()
    data = obj.ltpData("NSE", token, "")
    return float(data['data']['ltp'])

# 🏠 Homepage (IMPORTANT)
@app.route("/")
def home():
    return render_template("index.html")

# 🚀 NIFTY
@app.route("/nifty")
def nifty():
    try:
        price = get_price("99926000")

        return jsonify({
            "signal": "BUY" if price % 2 == 0 else "SELL",
            "prediction": "LIVE",
            "entry": price,
            "sl": round(price - 50, 2),
            "target": round(price + 100, 2)
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"signal": "WAIT", "prediction": "ERROR", "entry": 0, "sl": 0, "target": 0})

# 🚀 BANKNIFTY
@app.route("/banknifty")
def banknifty():
    try:
        price = get_price("99926009")

        return jsonify({
            "signal": "BUY" if price % 2 == 0 else "SELL",
            "prediction": "LIVE",
            "entry": price,
            "sl": round(price - 50, 2),
            "target": round(price + 100, 2)
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"signal": "WAIT", "prediction": "ERROR", "entry": 0, "sl": 0, "target": 0})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
