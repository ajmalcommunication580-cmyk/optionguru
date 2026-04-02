from flask import Flask, jsonify, render_template
from SmartApi import SmartConnect
import pyotp
import yfinance as yf
import pandas as pd
import requests

app = Flask(__name__)

# 🔑 Credentials
API_KEY = "TQPLmWZm"
CLIENT_ID = "M59304123"
PASSWORD = "7869"
TOTP_SECRET = "2AQ6MINLPQLYW45T2PDVP3367I"

obj = None

# 🔐 Login
def login():
    global obj
    if obj is None:
        obj = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        obj.generateSession(CLIENT_ID, PASSWORD, totp)
    return obj

# 📊 Data fetch
def get_data(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="5m")
        return data
    except:
        return None

# 🧠 RSI
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 🚀 AI SIGNAL ENGINE
def generate_ai_signal(symbol):

    df = get_data(symbol)
    if df is None or df.empty:
        return {"signal":"WAIT","prediction":"NO DATA","entry":0,"sl":0,"target":0,"support":0,"resistance":0,"confidence":0}

    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['RSI'] = calculate_rsi(df)

    latest = df.iloc[-1]

    price = float(latest['Close'])
    ema20 = float(latest['EMA20'])
    ema50 = float(latest['EMA50'])
    rsi = float(latest['RSI'])

    support = round(df['Low'].tail(20).min(),2)
    resistance = round(df['High'].tail(20).max(),2)

    confidence = 50

    if price > ema20 and ema20 > ema50:
        confidence += 20
    if rsi < 60:
        confidence += 15
    if price > resistance * 0.98:
        confidence += 15

    if price > ema20 and ema20 > ema50 and rsi < 70:
        signal = "STRONG BUY 🔥"
        target = price + 200
        sl = price - 80

    elif price < ema20 and ema20 < ema50 and rsi > 30:
        signal = "STRONG SELL 🔥"
        target = price - 200
        sl = price + 80

    else:
        signal = "WAIT ⚠️"
        target = price + 50
        sl = price - 50
        confidence = 40

    return {
        "signal": signal,
        "prediction": "AI PRO",
        "entry": round(price,2),
        "sl": round(sl,2),
        "target": round(target,2),
        "support": support,
        "resistance": resistance,
        "rsi": round(rsi,2),
        "confidence": confidence
    }

# 📊 OPTION CHAIN
def option_chain_ai(symbol="NIFTY"):
    try:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        headers = {"User-Agent":"Mozilla/5.0"}
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        data = session.get(url, headers=headers).json()

        records = data['records']['data']

        ce = sum(i['CE']['openInterest'] for i in records if 'CE' in i)
        pe = sum(i['PE']['openInterest'] for i in records if 'PE' in i)

        if pe > ce:
            signal = "BULLISH 🔥"
        elif ce > pe:
            signal = "BEARISH 🔥"
        else:
            signal = "SIDEWAYS"

        return {"signal":signal,"ce":ce,"pe":pe}

    except:
        return {"signal":"ERROR"}

# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")

# 📈 ROUTES
@app.route("/nifty")
def nifty():
    return jsonify(generate_ai_signal("^NSEI"))

@app.route("/banknifty")
def banknifty():
    return jsonify(generate_ai_signal("^NSEBANK"))

@app.route("/sensex")
def sensex():
    return jsonify(generate_ai_signal("^BSESN"))

@app.route("/finnifty")
def finnifty():
    return jsonify(generate_ai_signal("^CNXFIN"))

@app.route("/midcap")
def midcap():
    return jsonify(generate_ai_signal("^NSEMDCP"))

@app.route("/option/nifty")
def opt_nifty():
    return jsonify(option_chain_ai("NIFTY"))

@app.route("/option/banknifty")
def opt_bank():
    return jsonify(option_chain_ai("BANKNIFTY"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
