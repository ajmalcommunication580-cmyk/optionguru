from flask import Flask, jsonify, render_template
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

def calculate_signal(symbol):
    import yfinance as yf
    import pandas as pd

    data = yf.download(symbol, period="1d", interval="5m")

    if data.empty:
        return "NO SIGNAL", 0, 0, 0, "NO DATA"

    close = data['Close']

    # Indicators
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()

    last_price = round(close.iloc[-1], 2)

    # BUY / SELL logic (NO HOLD)
    if ema20.iloc[-1] > ema50.iloc[-1]:
        signal = "BUY ⚡"
        entry = last_price
        sl = round(entry - 50, 2)
        target = round(entry + 100, 2)
        prediction = "📈 UP TREND"

    else:
        signal = "SELL 🔻"
        entry = last_price
        sl = round(entry + 50, 2)
        target = round(entry - 100, 2)
        prediction = "📉 DOWN TREND"

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
