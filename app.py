from flask import Flask, jsonify, render_template
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

def calculate_signal(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="5m")

        # ❌ agar data nahi mila toh fallback
        if data is None or data.empty:
            return "BUY ⚡", 0, 0, 0, "No Data (Default Buy)"

        data["EMA20"] = data["Close"].ewm(span=20).mean()
        data["EMA50"] = data["Close"].ewm(span=50).mean()

        last = data.iloc[-1]

        # ❌ safety check
        if pd.isna(last["Close"]) or pd.isna(last["EMA20"]) or pd.isna(last["EMA50"]):
            return "BUY ⚡", 0, 0, 0, "Data Issue (Default Buy)"

        price = round(float(last["Close"]), 2)

        # 🔥 STRONG SIGNAL
        if last["EMA20"] > last["EMA50"] and price > last["EMA20"]:
            signal = "🔥 STRONG BUY"
            prediction = "📈 UP TREND"
            entry = price
            sl = round(price - 50, 2)
            target = round(price + 100, 2)

        elif last["EMA20"] < last["EMA50"] and price < last["EMA20"]:
            signal = "🔥 STRONG SELL"
            prediction = "📉 DOWN TREND"
            entry = price
            sl = round(price + 50, 2)
            target = round(price - 100, 2)

        else:
            # ⚡ fallback (NO HOLD)
            if last["EMA20"] > last["EMA50"]:
                signal = "BUY ⚡"
                prediction = "📈 Weak Uptrend"
                entry = price
                sl = round(price - 40, 2)
                target = round(price + 80, 2)
            else:
                signal = "SELL ⚡"
                prediction = "📉 Weak Downtrend"
                entry = price
                sl = round(price + 40, 2)
                target = round(price - 80, 2)

        return signal, entry, sl, target, prediction

    except Exception as e:
        print("ERROR:", e)
        # ❌ ERROR aane pe bhi BUY return karega
        return "BUY ⚡", 0, 0, 0, "Fallback Mode"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/nifty")
def nifty():
    s, entry, sl, target, pred = calculate_signal("^NSEI")
    return jsonify({
        "signal": s,
        "entry": entry,
        "sl": sl,
        "target": target,
        "prediction": pred
    })


@app.route("/banknifty")
def banknifty():
    s, entry, sl, target, pred = calculate_signal("^NSEBANK")
    return jsonify({
        "signal": s,
        "entry": entry,
        "sl": sl,
        "target": target,
        "prediction": pred
    })


if __name__ == "__main__":
    print("Starting Flask Server...")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
