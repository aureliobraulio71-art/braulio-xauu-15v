# ============================================================
#  XAU/USD SUPER AI — CÉREBRO GROQ (Llama 3.3 70B)
#  IA gratuita e poderosa para análise de XAU/USD
# ============================================================

import requests
import json
from config.settings import GROQ_KEY

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL    = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an elite XAU/USD (Gold) trading specialist with 20 years of experience.
You analyze markets with surgical precision combining technical, fundamental and market sentiment analysis.
Your goal is to generate HIGH QUALITY trading signals only when you have VERY HIGH CONVICTION.
You prefer NO signal over a weak signal.
RULES: Only BUY, SELL or NO_SIGNAL. Minimum confidence 70%. Require confluence of 4+ indicators.
Respond ONLY with valid JSON, no markdown, no extra text."""

def analyze_market(indicators_15m, indicators_1h, indicators_4h, news_text, current_price):
    if not GROQ_KEY:
        return _fallback_analysis(indicators_15m, current_price)

    prompt = f"""Analyze XAU/USD and decide: BUY, SELL or NO_SIGNAL.

CURRENT PRICE: ${current_price}

15 MINUTES INDICATORS:
{json.dumps(indicators_15m, indent=2)}

1 HOUR INDICATORS:
{json.dumps(indicators_1h, indent=2)}

4 HOUR INDICATORS:
{json.dumps(indicators_4h, indent=2)}

RECENT NEWS:
{news_text}

Only signal if 4+ indicators agree. Check RSI, MACD, EMA alignment, Bollinger, ADX, Stochastic.

Respond ONLY with this JSON (no markdown):
{{"signal":"BUY" or "SELL" or "NO_SIGNAL","confidence":number 0-100,"entry":price,"sl":price,"tp1":price,"tp2":price,"tp3":price,"timeframe":"15M","trend":"BULLISH" or "BEARISH" or "SIDEWAYS","reasoning":"3-4 sentences why","key_levels":"support and resistance","news_impact":"POSITIVE" or "NEGATIVE" or "NEUTRAL","risk_reward":number}}"""

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens":  600
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["message"]["content"].strip()
        text = text.replace("```json","").replace("```","").strip()
        result = json.loads(text)
        print(f"🧠 Groq: {result.get('signal')} | {result.get('confidence')}%")
        return result
    except Exception as e:
        print(f"❌ Groq erro: {e}")
        return _fallback_analysis(indicators_15m, current_price)


def _fallback_analysis(ind, price):
    if not ind or not price:
        return {"signal": "NO_SIGNAL", "confidence": 0}

    score = 0; direction = 0
    rsi        = ind.get("rsi", 50)
    macd_hist  = ind.get("macd_hist", 0)
    macd       = ind.get("macd", 0)
    macd_sig   = ind.get("macd_signal", 0)
    adx        = ind.get("adx", 0)
    di_pos     = ind.get("di_pos", 0)
    di_neg     = ind.get("di_neg", 0)
    bb_pct     = ind.get("bb_pct", 0.5)
    stoch_k    = ind.get("stoch_k", 50)
    stoch_d    = ind.get("stoch_d", 50)
    cci        = ind.get("cci", 0)
    w_r        = ind.get("williams_r", -50)
    ema20_up   = ind.get("above_ema20", False)
    ema50_up   = ind.get("above_ema50", False)
    ema200_up  = ind.get("above_ema200", False)
    atr        = ind.get("atr", 5)

    if rsi < 25:    score+=3; direction+=2
    elif rsi < 35:  score+=2; direction+=1
    elif rsi > 75:  score+=3; direction-=2
    elif rsi > 65:  score+=2; direction-=1

    if macd > macd_sig and macd_hist > 0: direction+=2; score+=2
    elif macd < macd_sig and macd_hist < 0: direction-=2; score+=2

    if adx > 25:
        score+=1
        if di_pos > di_neg: direction+=1
        else: direction-=1

    if bb_pct < 0.1: score+=2; direction+=2
    elif bb_pct > 0.9: score+=2; direction-=2

    if ema20_up and ema50_up and ema200_up: direction+=2; score+=2
    elif ema20_up and ema50_up: direction+=1; score+=1
    elif not ema20_up and not ema50_up and not ema200_up: direction-=2; score+=2
    elif not ema20_up and not ema50_up: direction-=1; score+=1

    if stoch_k < 20 and stoch_k > stoch_d: direction+=1; score+=1
    elif stoch_k > 80 and stoch_k < stoch_d: direction-=1; score+=1

    if cci < -100: direction+=1; score+=1
    elif cci > 100: direction-=1; score+=1

    if w_r < -80: direction+=1; score+=1
    elif w_r > -20: direction-=1; score+=1

    confidence = min(int(score * 8), 88)
    if confidence < 60 or score < 4:
        return {"signal": "NO_SIGNAL", "confidence": confidence}

    support    = ind.get("support",    round(price - atr*3, 2))
    resistance = ind.get("resistance", round(price + atr*3, 2))

    if direction > 0:
        return {
            "signal": "BUY", "confidence": confidence,
            "entry": round(price,2), "sl": round(price-atr*1.5,2),
            "tp1": round(price+atr*2,2), "tp2": round(price+atr*3.5,2), "tp3": round(price+atr*5.5,2),
            "timeframe": "15M", "trend": "BULLISH",
            "reasoning": f"RSI={rsi:.0f} zona oversold, MACD bullish crossover, ADX={adx:.0f} confirma tendência. Confluência bullish em {score} indicadores.",
            "key_levels": f"Suporte: ${support:.2f} | Resistência: ${resistance:.2f}",
            "news_impact": "NEUTRAL", "risk_reward": 2.0
        }
    else:
        return {
            "signal": "SELL", "confidence": confidence,
            "entry": round(price,2), "sl": round(price+atr*1.5,2),
            "tp1": round(price-atr*2,2), "tp2": round(price-atr*3.5,2), "tp3": round(price-atr*5.5,2),
            "timeframe": "15M", "trend": "BEARISH",
            "reasoning": f"RSI={rsi:.0f} zona overbought, MACD bearish crossover, ADX={adx:.0f} confirma tendência. Confluência bearish em {score} indicadores.",
            "key_levels": f"Suporte: ${support:.2f} | Resistência: ${resistance:.2f}",
            "news_impact": "NEUTRAL", "risk_reward": 2.0
        }
