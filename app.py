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

# 🔐 LOGIN
def login():
    global obj
    if obj is None:
        obj = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        data = obj.generateSession(CLIENT_ID, PASSWORD, totp)

        print("LOGIN:", data)

        if not data or data.get("status") == False:
            obj = None
            raise Exception("Login Failed")

    return obj


# 📊 PRICE FETCH
def get_price(token):
    try:
        obj = login()
        data = obj.ltpData("NSE", token, "")

        print("DATA:", data)

        if not data or 'data' not in data:
            return None

        return float(data['data']['ltp'])

    except Exception as e:
        print("ERROR:", e)
        return None


# 🎯 SIGNAL LOGIC
def generate_signal(price):
    if price is None:
        return "WAIT", "NO DATA", 0, 0, 0

    entry = price
    sl = round(price - 50, 2)
    target = round(price + 100, 2)

    if price % 5 == 0:
        signal = "STRONG BUY"
    elif price % 2 == 0:
        signal = "BUY"
    else:
        signal = "SELL"

    return signal, "LIVE", entry, sl, target


# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")


# 📊 ROUTES

@app.route("/nifty")
def nifty():
    price = get_price("99926000")
    s, p, e, sl, t = generate_signal(price)
    return jsonify({"signal": s, "prediction": p, "entry": e, "sl": sl, "target": t})


@app.route("/banknifty")
def banknifty():
    price = get_price("99926009")
    s, p, e, sl, t = generate_signal(price)
    return jsonify({"signal": s, "prediction": p, "entry": e, "sl": sl, "target": t})


@app.route("/finnifty")
def finnifty():
    price = get_price("99926037")
    s, p, e, sl, t = generate_signal(price)
    return jsonify({"signal": s, "prediction": p, "entry": e, "sl": sl, "target": t})


@app.route("/sensex")
def sensex():
    price = get_price("99919000")
    s, p, e, sl, t = generate_signal(price)
    return jsonify({"signal": s, "prediction": p, "entry": e, "sl": sl, "target": t})


@app.route("/midcap")
def midcap():
    price = get_price("99926074")
    s, p, e, sl, t = generate_signal(price)
    return jsonify({"signal": s, "prediction": p, "entry": e, "sl": sl, "target": t})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
