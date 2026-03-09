# ============================================================
#  XAU/USD SUPER AI — SISTEMA TELEGRAM
# ============================================================

import requests
from datetime import datetime
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_message(text, parse_mode="HTML"):
    """Envia mensagem para o Telegram"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json().get("ok", False)
    except Exception as e:
        print(f"❌ Telegram erro: {e}")
        return False

def send_signal(analysis, current_price):
    """Envia sinal de trading formatado"""
    signal = analysis.get("signal", "NO_SIGNAL")
    if signal == "NO_SIGNAL":
        return False

    confidence = analysis.get("confidence", 0)
    entry      = analysis.get("entry", current_price)
    sl         = analysis.get("sl", 0)
    tp1        = analysis.get("tp1", 0)
    tp2        = analysis.get("tp2", 0)
    tp3        = analysis.get("tp3", 0)
    reasoning  = analysis.get("reasoning", "")
    trend      = analysis.get("trend", "")
    key_levels = analysis.get("key_levels", "")
    rr         = analysis.get("risk_reward", 0)
    news_impact= analysis.get("news_impact", "NEUTRAL")
    tf         = analysis.get("timeframe", "15M")
    now        = datetime.utcnow().strftime("%H:%M UTC")

    emoji = "🟢" if signal == "BUY" else "🔴"
    arrow = "📈" if signal == "BUY" else "📉"
    news_emoji = "📰✅" if news_impact == "POSITIVE" else "📰❌" if news_impact == "NEGATIVE" else "📰➡️"
    stars = "⭐" * (5 if confidence >= 85 else 4 if confidence >= 75 else 3)

    msg = f"""
{emoji}{emoji} <b>SINAL XAU/USD — {signal}</b> {emoji}{emoji}

{arrow} <b>Direção:</b> {signal}
💰 <b>Entrada:</b> <code>${entry:,.2f}</code>
⏱ <b>Timeframe:</b> {tf}
🎯 <b>Confiança:</b> {confidence}% {stars}
📊 <b>Tendência:</b> {trend}

🛡 <b>Stop Loss:</b> <code>${sl:,.2f}</code>
✅ <b>TP1:</b> <code>${tp1:,.2f}</code>
✅ <b>TP2:</b> <code>${tp2:,.2f}</code>
✅ <b>TP3:</b> <code>${tp3:,.2f}</code>
⚖️ <b>Risco/Retorno:</b> 1:{rr}

{news_emoji} <b>Impacto Notícias:</b> {news_impact}

📍 <b>Níveis Chave:</b>
<code>{key_levels}</code>

🧠 <b>Análise:</b>
<i>{reasoning}</i>

🕐 {now} | XAU/USD Super AI
⚠️ <i>Trading envolve risco. Gestão de risco obrigatória.</i>
"""
    return send_message(msg.strip())

def send_daily_report(stats):
    """Envia relatório diário"""
    date    = datetime.utcnow().strftime("%d/%m/%Y")
    signals = stats.get("signals", 0)
    wins    = stats.get("wins", 0)
    losses  = stats.get("losses", 0)
    pending = stats.get("pending", 0)
    wr      = round(wins / signals * 100, 1) if signals > 0 else 0
    pl      = stats.get("pl_est", 0.0)

    bar_len = 10
    filled  = int(wr / 100 * bar_len)
    bar     = "█" * filled + "░" * (bar_len - filled)

    msg = f"""
📊 <b>RELATÓRIO DIÁRIO — {date}</b>

📡 <b>Sinais:</b> {signals} | ✅{wins} ❌{losses} ⏳{pending}
📈 <b>Win Rate:</b> {wr}% [{bar}]
💵 <b>P&L Est.:</b> €{pl:+.2f}

🔥 <b>Desempenho:</b> {"Excelente" if wr >= 70 else "Bom" if wr >= 55 else "A melhorar"}

⚠️ <i>Resultados baseados nos sinais enviados.</i>
"""
    return send_message(msg.strip())

def send_startup():
    """Mensagem de arranque do sistema"""
    now = datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")
    msg = f"""
🚀 <b>XAU/USD SUPER AI — ONLINE</b>

✅ Sistema iniciado com sucesso
🧠 Claude AI: Ativo
📊 Indicadores: 12 ativos
📰 Monitor de notícias: Ativo
⚡ Análise multi-timeframe: 15M | 1H | 4H

🕐 {now}
🔄 A monitorizar XAU/USD 24/7...
"""
    return send_message(msg.strip())

def send_market_update(price, change, trend, rsi, adx):
    """Envia update de mercado periódico"""
    now    = datetime.utcnow().strftime("%H:%M UTC")
    arrow  = "📈" if change > 0 else "📉" if change < 0 else "➡️"
    change_str = f"+{change:.2f}" if change > 0 else f"{change:.2f}"

    msg = f"""
{arrow} <b>XAU/USD UPDATE</b>

💰 Preço: <code>${price:,.2f}</code> ({change_str})
📊 Tendência: {trend}
📉 RSI: {rsi:.1f}
💪 ADX: {adx:.1f}
🕐 {now}
"""
    return send_message(msg.strip())

def send_error_alert(error_msg):
    """Alerta de erro"""
    msg = f"⚠️ <b>ALERTA SISTEMA</b>\n\n{error_msg}\n\n🔄 A tentar reconectar..."
    return send_message(msg)
