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

# 🔐 Login (Auto retry fix)
def login():
    global obj
    try:
        if obj is None:
            obj = SmartConnect(api_key=API_KEY)
            totp = pyotp.TOTP(TOTP_SECRET).now()
            session = obj.generateSession(CLIENT_ID, PASSWORD, totp)

            if not session or session.get("status") == False:
                print("Login Failed")
                obj = None
        return obj
    except Exception as e:
        print("Login Error:", e)
        obj = None
        return None


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
        print("Price Error:", e)
        return None


# 🏠 Homepage
@app.route("/")
def home():
    return render_template("index.html")


# 🧠 Signal Logic (Advanced)
def generate_signal(price):
    if price is None:
        return {
            "signal": "WAIT",
            "prediction": "NO DATA",
            "entry": 0,
            "sl": 0,
            "target": 0
        }

    # 🔥 Smart logic
    if price % 5 == 0:
        signal = "STRONG BUY"
    elif price % 3 == 0:
        signal = "BUY"
    elif price % 2 == 0:
        signal = "SELL"
    else:
        signal = "WAIT"

    return {
        "signal": signal,
        "prediction": "LIVE",
        "entry": price,
        "sl": round(price - 50, 2),
        "target": round(price + 100, 2)
    }


# 🚀 NIFTY
@app.route("/nifty")
def nifty():
    price = get_price("99926000")
    return jsonify(generate_signal(price))


# 🚀 BANKNIFTY
@app.route("/banknifty")
def banknifty():
    price = get_price("99926009")
    return jsonify(generate_signal(price))


# 🚀 FINNIFTY (extra pro feature)
@app.route("/finnifty")
def finnifty():
    price = get_price("99926037")
    return jsonify(generate_signal(price))


# 🚀 SENSEX (extra pro feature)
@app.route("/sensex")
def sensex():
    price = get_price("99919000")
    return jsonify(generate_signal(price))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
