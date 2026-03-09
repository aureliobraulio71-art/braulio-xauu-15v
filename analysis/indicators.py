# ============================================================
#  XAU/USD SUPER AI — INDICADORES TÉCNICOS
# ============================================================

import pandas as pd
import numpy as np

def add_all_indicators(df):
    """Adiciona todos os indicadores técnicos ao DataFrame"""
    if df is None or len(df) < 30:
        return df

    c = df["close"]
    h = df["high"]
    l = df["low"]

    # ── RSI ──────────────────────────────────────────────
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))

    # ── MACD ─────────────────────────────────────────────
    ema12 = c.ewm(span=12).mean()
    ema26 = c.ewm(span=26).mean()
    df["macd"]        = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    # ── EMAs ─────────────────────────────────────────────
    df["ema20"]  = c.ewm(span=20).mean()
    df["ema50"]  = c.ewm(span=50).mean()
    df["ema200"] = c.ewm(span=200).mean()

    # ── Bollinger Bands ──────────────────────────────────
    sma20        = c.rolling(20).mean()
    std20        = c.rolling(20).std()
    df["bb_mid"] = sma20
    df["bb_up"]  = sma20 + (2 * std20)
    df["bb_low"] = sma20 - (2 * std20)
    df["bb_pct"] = (c - df["bb_low"]) / (df["bb_up"] - df["bb_low"])

    # ── ATR ──────────────────────────────────────────────
    tr = pd.concat([
        h - l,
        (h - c.shift()).abs(),
        (l - c.shift()).abs()
    ], axis=1).max(axis=1)
    df["atr"] = tr.rolling(14).mean()

    # ── Stochastic ───────────────────────────────────────
    low14  = l.rolling(14).min()
    high14 = h.rolling(14).max()
    df["stoch_k"] = 100 * (c - low14) / (high14 - low14 + 1e-9)
    df["stoch_d"] = df["stoch_k"].rolling(3).mean()

    # ── ADX ──────────────────────────────────────────────
    tr_s   = tr.rolling(14).sum()
    dm_pos = (h.diff()).clip(lower=0)
    dm_neg = (-l.diff()).clip(lower=0)
    dm_pos = dm_pos.where(dm_pos > dm_neg, 0)
    dm_neg = dm_neg.where(dm_neg > dm_pos, 0)
    di_pos = 100 * dm_pos.rolling(14).sum() / tr_s.replace(0, np.nan)
    di_neg = 100 * dm_neg.rolling(14).sum() / tr_s.replace(0, np.nan)
    dx     = 100 * (di_pos - di_neg).abs() / (di_pos + di_neg + 1e-9)
    df["adx"]    = dx.rolling(14).mean()
    df["di_pos"] = di_pos
    df["di_neg"] = di_neg

    # ── CCI ──────────────────────────────────────────────
    tp = (h + l + c) / 3
    df["cci"] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())

    # ── Williams %R ──────────────────────────────────────
    df["williams_r"] = -100 * (h.rolling(14).max() - c) / (
        h.rolling(14).max() - l.rolling(14).min() + 1e-9)

    # ── VWAP ─────────────────────────────────────────────
    if "volume" in df.columns:
        tp_v = (h + l + c) / 3
        df["vwap"] = (tp_v * df["volume"]).cumsum() / df["volume"].cumsum()

    # ── Suporte & Resistência ────────────────────────────
    df["support"]    = l.rolling(20).min()
    df["resistance"] = h.rolling(20).max()

    # ── Padrões de velas ─────────────────────────────────
    body    = (c - df["open"]).abs()
    candle  = h - l
    df["doji"]     = (body / candle.replace(0, np.nan) < 0.1).astype(int)
    df["bullish"]  = (c > df["open"]).astype(int)
    df["bearish"]  = (c < df["open"]).astype(int)

    # ── Momentum ─────────────────────────────────────────
    df["momentum"] = c - c.shift(10)
    df["roc"]      = c.pct_change(10) * 100

    return df

def get_signal_summary(df):
    """Extrai resumo dos indicadores para análise da IA"""
    if df is None or len(df) < 2:
        return {}

    last = df.iloc[-1]
    prev = df.iloc[-2]

    return {
        "price":       round(float(last["close"]), 2),
        "rsi":         round(float(last.get("rsi", 50)), 1),
        "macd":        round(float(last.get("macd", 0)), 4),
        "macd_signal": round(float(last.get("macd_signal", 0)), 4),
        "macd_hist":   round(float(last.get("macd_hist", 0)), 4),
        "ema20":       round(float(last.get("ema20", 0)), 2),
        "ema50":       round(float(last.get("ema50", 0)), 2),
        "ema200":      round(float(last.get("ema200", 0)), 2),
        "bb_up":       round(float(last.get("bb_up", 0)), 2),
        "bb_low":      round(float(last.get("bb_low", 0)), 2),
        "bb_pct":      round(float(last.get("bb_pct", 0.5)), 3),
        "atr":         round(float(last.get("atr", 0)), 2),
        "stoch_k":     round(float(last.get("stoch_k", 50)), 1),
        "stoch_d":     round(float(last.get("stoch_d", 50)), 1),
        "adx":         round(float(last.get("adx", 0)), 1),
        "di_pos":      round(float(last.get("di_pos", 0)), 1),
        "di_neg":      round(float(last.get("di_neg", 0)), 1),
        "cci":         round(float(last.get("cci", 0)), 1),
        "williams_r":  round(float(last.get("williams_r", -50)), 1),
        "support":     round(float(last.get("support", 0)), 2),
        "resistance":  round(float(last.get("resistance", 0)), 2),
        "momentum":    round(float(last.get("momentum", 0)), 2),
        "roc":         round(float(last.get("roc", 0)), 2),
        "above_ema20": bool(last["close"] > last.get("ema20", 0)),
        "above_ema50": bool(last["close"] > last.get("ema50", 0)),
        "above_ema200":bool(last["close"] > last.get("ema200", 0)),
        "price_change":round(float(last["close"] - prev["close"]), 2),
    }
