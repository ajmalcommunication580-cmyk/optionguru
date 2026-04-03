from flask import Flask, jsonify, render_template
import random
import datetime

app = Flask(__name__)

# 📊 Base prices
base_prices = {
    "nifty": 22500,
    "banknifty": 51000,
    "sensex": 73000,
    "finnifty": 21000,
    "midcap": 15000
}

# 🕒 Market time check
def is_market_open():
    now = datetime.datetime.now()

    if now.weekday() >= 5:
        return False

    if now.hour < 9 or (now.hour == 9 and now.minute < 15):
        return False

    if now.hour > 15 or (now.hour == 15 and now.minute > 30):
        return False

    return True

# 📊 Fake live price
def get_price(name):
    move = random.uniform(-50, 50)
    base_prices[name] += move
    return round(base_prices[name], 2)

# 🧠 Signal logic
def generate_signal(price):

    # ❌ Market closed
    if not is_market_open():
        return {
            "signal": "CLOSED",
            "prediction": "MARKET CLOSED",
            "entry": 0,
            "sl": 0,
            "target": 0,
            "support": 0,
            "resistance": 0
        }

    support = round(price - 80, 2)
    resistance = round(price + 80, 2)

    if int(price) % 2 == 0:
        signal = "BUY"
        sl = support
        target = resistance
    else:
        signal = "SELL"
        sl = resistance
        target = support

    return {
        "signal": signal,
        "prediction": "LIVE",
        "entry": price,
        "sl": sl,
        "target": target,
        "support": support,
        "resistance": resistance
    }

# 🏠 Home
@app.route("/")
def home():
    return render_template("index.html")

# 📊 Routes
@app.route("/nifty")
def nifty():
    return jsonify(generate_signal(get_price("nifty")))

@app.route("/banknifty")
def banknifty():
    return jsonify(generate_signal(get_price("banknifty")))

@app.route("/sensex")
def sensex():
    return jsonify(generate_signal(get_price("sensex")))

@app.route("/finnifty")
def finnifty():
    return jsonify(generate_signal(get_price("finnifty")))

@app.route("/midcap")
def midcap():
    return jsonify(generate_signal(get_price("midcap")))

# 🚀 Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
