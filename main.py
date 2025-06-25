import yfinance as yf
import pandas as pd
import telegram
import time
from flask import Flask

# Telegram bot setup
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = telegram.Bot(token=BOT_TOKEN)

# Flask app to keep the bot alive (needed for Render and UptimeRobot)
app = Flask(__name__)

@app.route("/")
def home():
    return "Forex Signal Bot is running."

# Signal generation
def get_signal(symbol):
    data = yf.download(symbol, period="5d", interval="1h")

    if data.empty or len(data) < 21:
        return None

    data["EMA9"] = data["Close"].ewm(span=9, adjust=False).mean()
    data["EMA21"] = data["Close"].ewm(span=21, adjust=False).mean()

    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

    last = data.iloc[-1]

    rsi_value = last["RSI"]
    rsi_neutral = 30 < rsi_value < 70

    if last["EMA9"] > last["EMA21"] and rsi_neutral:
        return "BUY"
    elif last["EMA9"] < last["EMA21"] and rsi_neutral:
        return "SELL"
    else:
        return None

# Bot loop (runs once per hour)
def run_bot():
    symbol = "EURUSD=X"
    signal = get_signal(symbol)
    if signal:
        message = f"{signal} signal for {symbol}"
        bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        print(f"No signal for {symbol}")

if __name__ == "__main__":
    run_bot()
    app.run(host="0.0.0.0", port=10000)
