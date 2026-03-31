from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp, time

app = Flask(__name__)

API_KEY = "TQPLmWZm"
CLIENT_ID = "M59304123"
PASSWORD = "7869"
TOTP_SECRET = "2AQ6MINLPQLYW45T2PDVP3367I"

obj = None
last_login = 0
price_store = {}


# 🔐 LOGIN
def login():
    global obj, last_login

    if obj is None or time.time() - last_login > 900:
        try:
            obj = SmartConnect(api_key=API_KEY)
            totp = pyotp.TOTP(TOTP_SECRET).now()
            data = obj.generateSession(CLIENT_ID, PASSWORD, totp)

            if not data or data.get("status") == False:
                obj = None
                return None

            last_login = time.time()

        except:
            obj = None

    return obj


# 📊 PRICE STORE
def get_price(token):
    try:
        obj = login()
        if obj is None:
            return None

        data = obj.ltpData("NSE", token, "")
        if not data or 'data' not in data:
            return None

        price = float(data['data']['ltp'])

        if token not in price_store:
            price_store[token] = []

        price_store[token].append(price)

        if len(price_store[token]) > 50:
            price_store[token].pop(0)

        return price

    except:
        return None


# 🧠 TRADER AI ENGINE
def generate_signal(token):

    prices = price_store.get(token, [])

    if len(prices) < 15:
        return {"signal":"WAIT","prediction":"COLLECTING","entry":0,"sl":0,"target":0}

    price = prices[-1]

    # 📊 SUPPORT / RESISTANCE
    support = min(prices[-15:])
    resistance = max(prices[-15:])

    # 📈 MOVING AVERAGE
    ma5 = sum(prices[-5:]) / 5
    ma15 = sum(prices[-15:]) / 15

    # ⚡ MOMENTUM
    momentum = price - prices[-5]

    # 🔥 BREAKOUT
    breakout_up = price > resistance * 0.995
    breakout_down = price < support * 1.005

    # 💰 RISK MANAGEMENT
    sl = round(price - (price * 0.003),2)
    target = round(price + (price * 0.006),2)

    signal = "WAIT"
    reason = "NO CONFIRMATION"

    # 🚀 FINAL LOGIC
    if breakout_up and momentum > 0 and ma5 > ma15:
        signal = "STRONG BUY 🚀"
        reason = "BREAKOUT + TREND"
    elif breakout_down and momentum < 0 and ma5 < ma15:
        signal = "STRONG SELL 🔻"
        reason = "BREAKDOWN"
    elif ma5 > ma15 and momentum > 0:
        signal = "BUY 📈"
        reason = "UPTREND"
    elif ma5 < ma15 and momentum < 0:
        signal = "SELL 📉"
        reason = "DOWNTREND"

    return {
        "signal": signal,
        "prediction": reason,
        "entry": round(price,2),
        "sl": sl,
        "target": target,
        "support": round(support,2),
        "resistance": round(resistance,2)
    }


# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")


# 🚀 ROUTE
def route(token):
    get_price(token)
    return jsonify(generate_signal(token))


@app.route("/nifty")
def nifty():
    return route("99926000")

@app.route("/banknifty")
def banknifty():
    return route("99926009")

@app.route("/finnifty")
def finnifty():
    return route("99926037")

@app.route("/sensex")
def sensex():
    return route("99919000")

@app.route("/midcap")
def midcap():
    return route("99926074")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
