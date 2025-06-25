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
import yfinance as yf
import pandas as pd

def get_signal(symbol):
    # Download recent price data
    data = yf.download(symbol, period="5d", interval="1h")

    # Calculate RSI
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]

    # Calculate MACD
    ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    latest_macd = macd.iloc[-1]
    latest_signal_line = signal.iloc[-1]

    # Calculate EMA 50 and EMA 200
    ema_50 = data['Close'].ewm(span=50, adjust=False).mean()
    ema_200 = data['Close'].ewm(span=200, adjust=False).mean()
    latest_ema_50 = ema_50.iloc[-1]
    latest_ema_200 = ema_200.iloc[-1]

    # Combine logic from all indicators
   if latest_rsi.iloc[-1] < 30 and latest_macd.iloc[-1] > latest_signal_line.iloc[-1] and latest_ema_50.iloc[-1] > latest_ema_200.iloc[-1]:

        return "STRONG BUY"
    elif latest_rsi > 70 and latest_macd < latest_signal_line and latest_ema_50 < latest_ema_200:
        return "STRONG SELL"
    elif latest_rsi < 30:
        return "BUY"
    elif latest_rsi > 70:
        return "SELL"
    else:
        return "HOLD"


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
