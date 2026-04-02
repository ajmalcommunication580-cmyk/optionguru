from flask import Flask, jsonify, render_template
import random
import time

app = Flask(__name__)

# 📊 BASE PRICES (REALISTIC)
base_prices = {
    "nifty": 22500,
    "banknifty": 51000,
    "sensex": 73000,
    "finnifty": 21000,
    "midcap": 15000
}

# 📊 FAKE LIVE PRICE (REAL FEEL)
def get_price(name):
    move = random.uniform(-50, 50)
    base_prices[name] += move
    return round(base_prices[name], 2)

# 🧠 SIGNAL LOGIC (SMART)
def generate_signal(price):
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

# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")

# 📊 ROUTES
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

# 🚀 RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
