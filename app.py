from flask import Flask, jsonify
import yfinance as yf

app = Flask(__name__)

def get_data(symbol):
    try:
        data = yf.download(symbol, period="1d", interval="5m")

        if data.empty:
            return {"signal": "WAIT", "prediction": "Fallback Mode", "entry": 0, "sl": 0, "target": 0}

        last_close = float(data["Close"].iloc[-1])
        prev_close = float(data["Close"].iloc[-2])

        if last_close > prev_close:
            signal = "BUY"
            prediction = "UP"
        else:
            signal = "SELL"
            prediction = "DOWN"

        return {
            "signal": signal,
            "prediction": prediction,
            "entry": round(last_close, 2),
            "sl": round(last_close - 50, 2),
            "target": round(last_close + 100, 2)
        }

    except Exception as e:
        print("ERROR:", e)
        return {"signal": "WAIT", "prediction": "Fallback Mode", "entry": 0, "sl": 0, "target": 0}


@app.route("/")
def home():
    return "OptionGuru Backend Running ✅"


@app.route("/nifty")
def nifty():
    return jsonify(get_data("^NSEI"))


@app.route("/banknifty")
def banknifty():
    return jsonify(get_data("^NSEBANK"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
