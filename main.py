import os
import requests
import schedule
import time
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('7789994937:AAFqQvwgqU160P5_ffHL-2tbX7xdie6KSsY')
TELEGRAM_CHANNEL_ID = os.getenv('SK RESULT INSIGHTS')
ALPHA_VANTAGE_KEY = os.getenv('bcdbbd93ff8e19ef7d57e497df41e2b6')

# Your specific stock list (example)
SMALL_CAP_STOCKS = ["RADICO.NS", "RADHIKAJWE.NS", "MINDTECK.NS"]


def get_stock_data(symbol):
    """Fetch stock data from Alpha Vantage"""
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
        response = requests.get(url)
        data = response.json()

        latest_day = data['Time Series (Daily)']
        latest_data = latest_day[list(latest_day.keys())[0]]

        return {
            'symbol': symbol,
            'price': float(latest_data['4. close']),
            'volume': int(latest_data['5. volume']),
            'ema20': None  # Will calculate later
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def calculate_ema(data_points, period=20):
    """Calculate EMA for given data points"""
    if len(data_points) < period:
        return None
    multiplier = 2 / (period + 1)
    ema = sum(data_points[:period]) / period
    for value in data_points[period:]:
        ema = (value - ema) * multiplier + ema
    return ema


def check_stocks():
    print(f"{datetime.now()} - Checking stocks...")
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    for symbol in SMALL_CAP_STOCKS:
        stock = get_stock_data(symbol)
        if stock and stock['volume'] > 50000:
            # Create alert message
            message = f"""
🚀 *{symbol.replace('.NS', '')}* 🚀

📈 Volume Alert: {stock['volume']:,} (50K+)
💰 Price: ₹{stock['price']:.2f}

#StockAlert #SmallCap #HighVolume
"""
            try:
                bot.send_message(
                    chat_id='SK RESULT INSIGHTS',                text=message,
                    parse_mode='Markdown'
                )
                print(f"Alert sent for {symbol}")
            except TelegramError as e:
                print(f"Telegram error: {e}")


# Schedule checks every 30 minutes
schedule.every(30).minutes.do(check_stocks)

if name == "main":
    print("Starting SK RESULT INSIGHTS bot...")
    while True:
        schedule.run_pending()
        time.sleep(1)