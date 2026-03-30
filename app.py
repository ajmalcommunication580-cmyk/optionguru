from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp

app = Flask(__name__)

# 🔑 YOUR DETAILS
API_KEY = "TQPLmWZm"
CLIENT_ID = "M59304123"
PASSWORD = "7869"
TOTP_SECRET = "2AQ6MINLPQLYW45T2PDVP3367I"

obj = None

# 🔐 Login once
def login():
    global obj
    if obj is None:
        try:
            obj = SmartConnect(api_key=API_KEY)
            totp = pyotp.TOTP(TOTP_SECRET).now()
            print("TOTP:", totp)

            session = obj.generateSession(CLIENT_ID, PASSWORD, totp)
            print("SESSION:", session)

        except Exception as e:
            print("LOGIN ERROR:", e)
            raise e
    return obj

# 📊 Price fetch
def get_price(token):
    obj = login()
    data = obj.ltpData("NSE", token, "")
    print("LTP DATA:", data)

    if 'data' not in data:
        raise Exception(data)

    return float(data['data']['ltp'])

# 🏠 Homepage
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
        return jsonify({
            "error": str(e)
        })

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
        return jsonify({
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
