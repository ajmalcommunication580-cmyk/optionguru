from flask import Flask, jsonify, render_template
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

import time

last_data = {}
last_fetch_time = {}

def calculate_signal(symbol):
    global cache, last_fetch_time

    import time
    import yfinance as yf
    import pandas as pd

    # 🔥 CACHE (20 sec)
    if time.time() - last_fetch_time < 20 and symbol in cache:
        return cache[symbol]

    try:
        data = yf.download(symbol, period="1d", interval="5m")

        if data.empty:
            return "NO SIGNAL", 0, 0, 0, "NO DATA"

        close = data['Close']
        volume = data['Volume']

        # 📊 Indicators
        ema20 = close.ewm(span=20).mean()
        ema50 = close.ewm(span=50).mean()

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Latest values
        last_price = round(close.iloc[-1], 2)
        last_rsi = rsi.iloc[-1]
        vol_avg = volume.rolling(20).mean().iloc[-1]
        last_vol = volume.iloc[-1]

        # 🔥 STRONG BUY
        if (
            ema20.iloc[-1] > ema50.iloc[-1] and
            last_rsi > 55 and
            last_vol > vol_avg
        ):
            signal = "STRONG BUY 🚀"
            entry = last_price
            sl = round(entry - 50, 2)
            target = round(entry + 120, 2)
            prediction = "📈 STRONG UPTREND"

        # 🔥 STRONG SELL
        elif (
            ema20.iloc[-1] < ema50.iloc[-1] and
            last_rsi < 45 and
            last_vol > vol_avg
        ):
            signal = "STRONG SELL 🔻"
            entry = last_price
            sl = round(entry + 50, 2)
            target = round(entry - 120, 2)
            prediction = "📉 STRONG DOWNTREND"

        else:
            # ❌ NO TRADE → fake BUY/SELL nahi
            return "NO TRADE ❌", 0, 0, 0, "Wait for strong signal"

        result = (signal, entry, sl, target, prediction)

        cache[symbol] = result
        last_fetch_time = time.time()

        return result

    except Exception as e:
        print("ERROR:", e)
        return "NO TRADE ❌", 0, 0, 0, "Error Mode"

        close = data['Close']

        # Indicators
        ema20 = close.ewm(span=20).mean()
        ema50 = close.ewm(span=50).mean()

        last_price = round(close.iloc[-1], 2)

        # 🔥 STRONG SIGNAL LOGIC
        if ema20.iloc[-1] > ema50.iloc[-1] * 1.001:
            signal = "BUY ⚡"
            entry = last_price
            sl = round(entry - 50, 2)
            target = round(entry + 120, 2)
            prediction = "📈 STRONG UP TREND"

        elif ema20.iloc[-1] < ema50.iloc[-1] * 0.999:
            signal = "SELL 🔻"
            entry = last_price
            sl = round(entry + 50, 2)
            target = round(entry - 120, 2)
            prediction = "📉 STRONG DOWN TREND"

        else:
            # ❌ HOLD hata diya → fallback SELL
            signal = "SELL 🔻"
            entry = last_price
            sl = round(entry + 30, 2)
            target = round(entry - 60, 2)
            prediction = "⚠️ WEAK TREND"

        return signal, entry, sl, target, prediction

    except Exception as e:
        print("ERROR:", e)
        return "NO SIGNAL", 0, 0, 0, "ERROR"


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
