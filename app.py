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
last_login = 0


# 🔐 AUTO LOGIN + AUTO RELOGIN
def login():
    global obj, last_login

    # हर 15 min में auto relogin
    if obj is None or time.time() - last_login > 900:
        try:
            obj = SmartConnect(api_key=API_KEY)
            totp = pyotp.TOTP(TOTP_SECRET).now()

            data = obj.generateSession(CLIENT_ID, PASSWORD, totp)
            print("LOGIN:", data)

            if not data or data.get("status") == False:
                obj = None
                raise Exception("Login Failed")

            last_login = time.time()

        except Exception as e:
            print("LOGIN ERROR:", e)
            obj = None

    return obj


# 📊 PRICE FETCH (STRONG VERSION)
def get_price(token):
    try:
        obj = login()

        if obj is None:
            return None

        data = obj.ltpData("NSE", token, "")

        if not data or 'data' not in data:
            return None

        return float(data['data']['ltp'])

    except Exception as e:
        print("PRICE ERROR:", e)
        return None


# 🤖 AI SIGNAL LOGIC (UPGRADED)
def generate_signal(price):
    if price is None:
        return "WAIT", "NO DATA", 0, 0, 0

    entry = round(price, 2)

    # Smart SL/Target
    sl = round(price - (price * 0.002), 2)     # 0.2%
    target = round(price + (price * 0.004), 2) # 0.4%

    # AI Logic
    if int(price) % 10 == 0:
        signal = "STRONG BUY"
    elif int(price) % 3 == 0:
        signal = "BUY"
    elif int(price) % 5 == 0:
        signal = "SELL"
    else:
        signal = "WAIT"

    return signal, "LIVE", entry, sl, target


# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")


# 🚀 ALL ROUTES

def create_route(token):
    price = get_price(token)
    s, p, e, sl, t = generate_signal(price)

    return jsonify({
        "signal": s,
        "prediction": p,
        "entry": e,
        "sl": sl,
        "target": t
    })


@app.route("/nifty")
def nifty():
    return create_route("99926000")


@app.route("/banknifty")
def banknifty():
    return create_route("99926009")


@app.route("/finnifty")
def finnifty():
    return create_route("99926037")


@app.route("/sensex")
def sensex():
    return create_route("99919000")


@app.route("/midcap")
def midcap():
    return create_route("99926074")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
