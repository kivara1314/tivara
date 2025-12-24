import requests
import pandas as pd
import numpy as np
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

BINANCE_URL = "https://api.binance.com/api/v3/klines"

TIMEFRAMES = ["15m","1h","4h"]

def get_data(symbol, interval="1h", limit=200):
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
    r = requests.get(BINANCE_URL, params=params, timeout=10)
    df = pd.DataFrame(r.json(), columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","trades","taker_base",
        "taker_quote","ignore"
    ])
    for col in ["open","high","low","close","volume"]:
        df[col] = df[col].astype(float)
    return df

def market_structure(df):
    highs = df["high"]
    lows = df["low"]
    HH = highs.iloc[-1] > highs.iloc[-2] and highs.iloc[-2] > highs.iloc[-3]
    LL = lows.iloc[-1] < lows.iloc[-2] and lows.iloc[-2] < lows.iloc[-3]
    return "Uptrend" if HH else "Downtrend" if LL else "Sideways"

def analyze_timeframe(df):
    ema_fast = EMAIndicator(df["close"], 21).ema_indicator().iloc[-1]
    ema_slow = EMAIndicator(df["close"], 55).ema_indicator().iloc[-1]
    trend = "Bullish 🟢" if ema_fast > ema_slow else "Bearish 🔴"

    rsi = RSIIndicator(df["close"], 14).rsi().iloc[-1]
    momentum = "Oversold ⚡" if rsi < 30 else "Overbought 🔥" if rsi > 70 else "Neutral"

    atr = AverageTrueRange(df["high"], df["low"], df["close"]).average_true_range().iloc[-1]

    vol_avg = df["volume"].rolling(20).mean().iloc[-1]
    vol_last = df["volume"].iloc[-1]
    volume_signal = "High 🔥" if vol_last > vol_avg else "Normal"

    return {"trend": trend, "rsi": round(rsi,2), "momentum": momentum,
            "atr": round(atr,4), "volume": volume_signal}

def generate_signals(symbol):
    tf_results = {}
    for tf in TIMEFRAMES:
        df = get_data(symbol, tf)
        analysis = analyze_timeframe(df)
        ms = market_structure(df)
        tf_results[tf] = {"analysis": analysis, "market_structure": ms}

    # Decision Engine (Bias + Entry/SL/TP)
    bias_score = 0
    for tf, v in tf_results.items():
        bias_score += 1 if v["analysis"]["trend"]=="Bullish 🟢" else -1
    bias = "LONG ✅" if bias_score > 0 else "SHORT ❌" if bias_score < 0 else "NO TRADE ⚠️"

    entry_price = round(get_data(symbol)["close"].iloc[-1],4)
    sl = round(entry_price*0.98 if bias=="LONG ✅" else entry_price*1.02,4)
    tp = round(entry_price*1.03 if bias=="LONG ✅" else entry_price*0.97,4)

    confidence = min(abs(bias_score)*20 + 50, 95)

    return {"symbol": symbol, "bias": bias, "entry": entry_price, "SL": sl, "TP": tp,
            "confidence": f"{confidence}%", "timeframes": tf_results}
