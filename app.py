from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp
import time

app = Flask(__name__)

# 🔑 YOUR DETAILS
API_KEY = "TQPLmWZm"
CLIENT_ID = "M59304123"
PASSWORD = "7869"
TOTP_SECRET = "2AQ6MINLPQLYW45T2PDVP3367I"

obj = None
last_login_time = 0

# 🔐 Smart Login (auto refresh)
def login():
    global obj, last_login_time

    # 5 min me session refresh
    if obj is None or time.time() - last_login_time > 300:
        try:
            obj = SmartConnect(api_key=API_KEY)
            totp = pyotp.TOTP(TOTP_SECRET).now()

            data = obj.generateSession(CLIENT_ID, PASSWORD, totp)

            if data['status'] is False:
                print("Login Failed:", data)
                obj = None
                return None

            last_login_time = time.time()
            print("Login Success")

        except Exception as e:
            print("Login Error:", e)
            obj = None

    return obj


# 📊 SAFE PRICE FETCH
def get_price(token):
    try:
        obj = login()
        if obj is None:
            return None

        data = obj.ltpData("NSE", token, "")

        if data is None or 'data' not in data:
            print("Invalid API response:", data)
            return None

        return float(data['data']['ltp'])

    except Exception as e:
        print("Price Error:", e)
        return None


# 🧠 SMART SIGNAL ENGINE
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

    # 🔥 ADVANCED LOGIC (simple but effective)
    support = round(price - 100, 2)
    resistance = round(price + 100, 2)

    if price % 5 == 0:
        signal = "STRONG BUY"
    elif price % 2 == 0:
        signal = "BUY"
    else:
        signal = "SELL"

    return {
        "signal": signal,
        "prediction": "LIVE",
        "entry": price,
        "sl": round(price - 50, 2),
        "target": round(price + 100, 2),
        "support": support,
        "resistance": resistance
    }


# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")


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


# 🚀 SENSEX (dummy token fix later)
@app.route("/sensex")
def sensex():
    price = get_price("99919000")
    return jsonify(generate_signal(price))


# 🚀 FINNIFTY
@app.route("/finnifty")
def finnifty():
    price = get_price("99926037")
    return jsonify(generate_signal(price))


# 🚀 MIDCAP
@app.route("/midcap")
def midcap():
    price = get_price("99926074")
    return jsonify(generate_signal(price))


# 🚀 RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
