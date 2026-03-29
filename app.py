from flask import Flask, jsonify, render_template
import pandas as pd
import yfinance as yf

app = Flask(__name__)

def calculate_signal(symbol):
    try:
        df = yf.Ticker(symbol).history(interval="5m", period="5d")

        if df.empty:
            return "NO DATA ❌", 0, 0, 0, "NO DATA"

        df['ema9'] = df['Close'].ewm(span=9).mean()
        df['ema21'] = df['Close'].ewm(span=21).mean()

        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        last = df.iloc[-1]
        entry = round(last['Close'], 2)

        # 🔥 STRONG SIGNAL
        if last['rsi'] < 30 and last['ema9'] > last['ema21']:
            signal = "STRONG BUY CALL 🚀"
        elif last['rsi'] > 70 and last['ema9'] < last['ema21']:
            signal = "STRONG BUY PUT 🔻"
        else:
            signal = "HOLD ⏳"

        # 🔥 SL & TARGET
        if "CALL" in signal:
            sl = entry - 50
            target = entry + 100
        elif "PUT" in signal:
            sl = entry + 50
            target = entry - 100
        else:
            sl = 0
            target = 0

        # 🤖 AI PREDICTION
        if last['ema9'] > last['ema21'] and last['rsi'] > 50:
            prediction = "📈 UP TREND"
        elif last['ema9'] < last['ema21'] and last['rsi'] < 50:
            prediction = "📉 DOWN TREND"
        else:
            prediction = "➡️ SIDEWAYS"

        return signal, entry, sl, target, prediction

    except Exception as e:
        print("Error:", e)
        return "ERROR ❌", 0, 0, 0, "ERROR"


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


import os

if __name__ == "__main__":
    print("Starting Flask Server...")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
