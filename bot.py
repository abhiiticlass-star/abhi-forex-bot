import os
import time
import requests
import threading
import pandas as pd
import yfinance as yf
from datetime import datetime
from flask import Flask

# ==========================================
# 🌐 RENDER KE LIYE DUMMY WEB SERVER (FLASK)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Abhi Forex Algo Pro Engine is running 24/7!"

def run_flask():
    # Render automatic 'PORT' environment variable deta hai
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# ⚙️ CORE TRADING ALGORITHM (1-MIN EUR/USD)
# ==========================================
BOT_TOKEN = "8863018421:AAHtmeQHhDBfzz-f6eDqHEFajol2qNipab8"
CHAT_ID = "-1003808226013"  
PAIR = "EURUSD=X"           
TIMEFRAME = "1m"            

def send_telegram_signal(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Delivery Error: {e}")

def calculate_price_action():
    print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Scanning 1-Min Market Candles...")
    try:
        ticker = yf.Ticker(PAIR)
        df = ticker.history(period="1d", interval=TIMEFRAME)
        
        if len(df) < 50:
            return

        df['EMA_Fast'] = df['Close'].ewm(span=50, adjust=False).mean()
        recent_window = df.tail(15)
        highest_resistance = recent_window['High'].max()
        lowest_support = recent_window['Low'].min()

        c_candle = df.iloc[-2]   
        p_candle = df.iloc[-3]   
        running_price = df.iloc[-1]['Close'] 

        c_open, c_close = c_candle['Open'], c_candle['Close']
        c_high, c_low = c_candle['High'], c_candle['Low']
        
        body_size = abs(c_close - c_open)
        total_range = c_high - c_low if (c_high - c_low) > 0 else 0.00001
        upper_shadow = c_high - max(c_open, c_close)
        lower_shadow = min(c_open, c_close) - c_low
        
        is_bullish_candle = c_close > c_open
        is_bearish_candle = c_close < c_open
        is_uptrend = c_close > c_candle['EMA_Fast']
        is_downtrend = c_close < c_candle['EMA_Fast']

        is_hammer = (lower_shadow >= (2 * body_size)) and (upper_shadow <= (0.2 * total_range))
        is_shooting_star = (upper_shadow >= (2 * body_size)) and (lower_shadow <= (0.2 * total_range))
        is_bullish_engulfing = (is_bullish_candle and p_candle['Close'] < p_candle['Open'] and c_close > p_candle['Open'] and c_open < p_candle['Close'])
        is_bearish_engulfing = (is_bearish_candle and p_candle['Close'] > p_candle['Open'] and c_close < p_candle['Open'] and c_open > p_candle['Close'])

        is_bullish_breakout = (c_close > highest_resistance) and (p_candle['Close'] <= highest_resistance)
        is_bearish_breakout = (c_close < lowest_support) and (p_candle['Close'] >= lowest_support)

        near_support = abs(c_close - lowest_support) < (total_range * 2)
        near_resistance = abs(c_close - highest_resistance) < (total_range * 2)

        if (is_uptrend and is_hammer and near_support) or (is_uptrend and is_bullish_engulfing and near_support) or is_bullish_breakout:
            msg = (
                f"🚨 *ABHI FOREX ALGO V2.0*\n"
                f"📊 *Asset:* EUR/USD\n"
                f"🟢 *Direction:* CALL\n"
                f"🎯 *Accuracy:* High Confluence\n"
                f"⏳ *Trade time:* 1 minute"
            )
            send_telegram_signal(msg)
            time.sleep(45) 

        elif (is_downtrend and is_shooting_star and near_resistance) or (is_downtrend and is_bearish_engulfing and near_resistance) or is_bearish_breakout:
            msg = (
                f"🚨 *ABHI FOREX ALGO V2.0*\n"
                f"📊 *Asset:* EUR/USD\n"
                f"🔴 *Direction:* PUT\n"
                f"🎯 *Accuracy:* High Confluence\n"
                f"⏳ *Trade time:* 1 minute"
            )
            send_telegram_signal(msg)
            time.sleep(45) 

    except Exception as e:
        print(f"❌ Error: {e}")

def main_trading_loop():
    while True:
        calculate_price_action()
        time.sleep(20)

if __name__ == "__main__":
    send_telegram_signal("✅ *Abhi Forex Bot Connection Test:* Server is successfully running!")
    # 1. Flask Server ko alag thread mein chalu karna Render ko khush rakhne ke liye
    server_thread = threading.Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()
    
    # 2. Main Trading Engine ko chalu karna
    main_trading_loop()
