# ============================================================
#  XAU/USD SUPER AI — DADOS DE MERCADO (yfinance)
#  100% gratuito, sem limites, sem chave API
# ============================================================

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

INTERVAL_MAP = {
    "1min": "1m", "5min": "5m", "15min": "15m",
    "1h": "1h", "4h": "4h", "1d": "1d"
}

PERIOD_MAP = {
    "1m": "1d", "5m": "5d", "15m": "5d",
    "1h": "30d", "4h": "60d", "1d": "1y"
}

def get_price_data(interval="15min", bars=100):
    """Busca dados OHLCV do XAU/USD via yfinance"""
    try:
        yf_interval = INTERVAL_MAP.get(interval, "15m")
        period = PERIOD_MAP.get(yf_interval, "5d")

        ticker = yf.Ticker("GC=F")
        df = ticker.history(period=period, interval=yf_interval)

        if df is None or df.empty:
            ticker = yf.Ticker("XAUUSD=X")
            df = ticker.history(period=period, interval=yf_interval)

        if df is None or df.empty:
            print(f"⚠️ Sem dados para {interval}")
            return None

        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]

        if "date" in df.columns and "datetime" not in df.columns:
            df = df.rename(columns={"date": "datetime"})
        if "datetime" not in df.columns:
            df["datetime"] = pd.to_datetime(df.index)

        for col in ["open", "high", "low", "close", "volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["close"])
        df = df.sort_values("datetime").reset_index(drop=True)

        if len(df) > bars:
            df = df.tail(bars).reset_index(drop=True)

        print(f"✅ {len(df)} barras {interval} | Último: ${df.iloc[-1]['close']:.2f}")
        return df

    except Exception as e:
        print(f"❌ yfinance erro ({interval}): {e}")
        return None

def get_current_price():
    """Busca preço atual do XAU/USD"""
    try:
        ticker = yf.Ticker("GC=F")
        data = ticker.history(period="1d", interval="1m")
        if data is not None and not data.empty:
            price = float(data["Close"].iloc[-1])
            print(f"💰 XAU/USD: ${price:,.2f}")
            return price
        ticker = yf.Ticker("XAUUSD=X")
        data = ticker.history(period="1d", interval="1m")
        if data is not None and not data.empty:
            return float(data["Close"].iloc[-1])
        return None
    except Exception as e:
        print(f"❌ Erro preço: {e}")
        return None

def get_multi_timeframe():
    """Busca dados em múltiplos timeframes"""
    result = {}
    for tf, bars in {"5min": 50, "15min": 100, "1h": 60, "4h": 30}.items():
        df = get_price_data(interval=tf, bars=bars)
        if df is not None:
            result[tf] = df
    return result

def is_market_open():
    """Verifica se o mercado está aberto"""
    now = datetime.utcnow()
    weekday = now.weekday()
    hour = now.hour
    if weekday == 5: return False
    if weekday == 6 and hour < 22: return False
    if weekday == 4 and hour >= 22: return False
    return True
