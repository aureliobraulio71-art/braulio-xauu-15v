# ============================================================
#  XAU/USD SUPER AI — MOTOR PRINCIPAL
#  Loop 24/7 de análise e envio de sinais
# ============================================================

import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from config.settings import (
    MIN_CONFIDENCE, MAX_SIGNALS_DAY,
    COOLDOWN_MINUTES, ANALYSIS_INTERVAL,
    NEWS_INTERVAL, DAILY_REPORT_HOUR
)
from data.market_data import get_price_data, get_current_price
from analysis.indicators import add_all_indicators, get_signal_summary
from analysis.news_analyzer import get_latest_news, format_news_for_ai
from analysis.claude_brain import analyze_market
from notifications.telegram_bot import (
    send_signal, send_daily_report,
    send_startup, send_error_alert, send_market_update
)

# ── LOGGING ──────────────────────────────────────────────
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── ESTADO DO BOT ─────────────────────────────────────────
class BotState:
    def __init__(self):
        self.signals_today    = 0
        self.last_signal_time = None
        self.last_news_fetch  = None
        self.cached_news      = ""
        self.last_report_day  = None
        self.stats = {
            "signals": 0, "wins": 0,
            "losses": 0, "pending": 0, "pl_est": 0.0
        }
        self.load()

    def save(self):
        try:
            with open("logs/state.json", "w") as f:
                json.dump({
                    "signals_today":    self.signals_today,
                    "last_signal_time": str(self.last_signal_time),
                    "stats":            self.stats
                }, f, indent=2)
        except:
            pass

    def load(self):
        try:
            with open("logs/state.json") as f:
                data = json.load(f)
                self.signals_today = data.get("signals_today", 0)
                self.stats         = data.get("stats", self.stats)
        except:
            pass

    def can_send_signal(self):
        if self.signals_today >= MAX_SIGNALS_DAY:
            log.info(f"⏸ Limite diário atingido ({MAX_SIGNALS_DAY} sinais)")
            return False
        if self.last_signal_time:
            elapsed = (datetime.utcnow() - self.last_signal_time).total_seconds() / 60
            if elapsed < COOLDOWN_MINUTES:
                log.info(f"⏸ Cooldown: {COOLDOWN_MINUTES - elapsed:.0f}min restantes")
                return False
        return True

    def register_signal(self):
        self.signals_today   += 1
        self.last_signal_time = datetime.utcnow()
        self.stats["signals"] += 1
        self.stats["pending"] += 1
        self.save()

    def reset_daily(self):
        self.signals_today = 0
        self.stats = {"signals": 0, "wins": 0, "losses": 0, "pending": 0, "pl_est": 0.0}
        self.save()

# ── CICLO PRINCIPAL ───────────────────────────────────────
def run():
    log.info("🚀 XAU/USD Super AI a iniciar...")
    state = BotState()
    send_startup()

    news_refresh_interval = NEWS_INTERVAL
    last_analysis = 0
    last_update   = 0
    update_interval = 3600  # Update de mercado a cada hora

    while True:
        try:
            now = datetime.utcnow()

            # ── Reset diário à meia-noite UTC ────────────
            if now.hour == 0 and now.minute < 5:
                if state.last_report_day != now.date():
                    log.info("🔄 Reset diário")
                    state.reset_daily()
                    state.last_report_day = now.date()

            # ── Relatório diário ─────────────────────────
            if now.hour == DAILY_REPORT_HOUR and now.minute < 5:
                if state.last_report_day != now.date():
                    send_daily_report(state.stats)
                    state.last_report_day = now.date()

            current_time = time.time()

            # ── Refresh de notícias ──────────────────────
            if (state.last_news_fetch is None or
                    (now - state.last_news_fetch).total_seconds() > news_refresh_interval):
                log.info("📰 A buscar notícias...")
                news = get_latest_news(hours_back=3)
                state.cached_news = format_news_for_ai(news)
                state.last_news_fetch = now
                log.info(f"📰 {len(news)} notícias encontradas")

            # ── Análise de mercado ───────────────────────
            if current_time - last_analysis >= ANALYSIS_INTERVAL:
                last_analysis = current_time
                log.info("🔍 A analisar mercado...")

                price = get_current_price()
                if not price:
                    log.warning("⚠️ Sem preço atual")
                    time.sleep(60)
                    continue

                log.info(f"💰 XAU/USD: ${price:,.2f}")

                # Busca dados multi-timeframe
                df_15m = get_price_data("15min", 100)
                df_1h  = get_price_data("1h", 60)
                df_4h  = get_price_data("4h", 30)

                if df_15m is None:
                    log.warning("⚠️ Sem dados 15M")
                    time.sleep(60)
                    continue

                # Calcula indicadores
                df_15m = add_all_indicators(df_15m)
                ind_15m = get_signal_summary(df_15m)

                ind_1h = {}
                if df_1h is not None:
                    df_1h  = add_all_indicators(df_1h)
                    ind_1h = get_signal_summary(df_1h)

                ind_4h = {}
                if df_4h is not None:
                    df_4h  = add_all_indicators(df_4h)
                    ind_4h = get_signal_summary(df_4h)

                # ── Análise com Claude AI ─────────────────
                analysis = analyze_market(
                    ind_15m, ind_1h, ind_4h,
                    state.cached_news, price
                )

                signal     = analysis.get("signal", "NO_SIGNAL")
                confidence = analysis.get("confidence", 0)

                log.info(f"🧠 Análise: {signal} | Confiança: {confidence}%")

                # ── Envia sinal se válido ─────────────────
                if (signal != "NO_SIGNAL" and
                        confidence >= MIN_CONFIDENCE and
                        state.can_send_signal()):

                    log.info(f"📡 A enviar sinal {signal} ({confidence}%)")
                    success = send_signal(analysis, price)

                    if success:
                        state.register_signal()
                        log.info("✅ Sinal enviado com sucesso!")
                    else:
                        log.error("❌ Falha ao enviar sinal")

                elif signal != "NO_SIGNAL":
                    log.info(f"⏸ Sinal {signal} ignorado: confiança={confidence}% < {MIN_CONFIDENCE}% ou cooldown")

            # ── Update periódico de mercado ───────────────
            if current_time - last_update >= update_interval:
                last_update = current_time
                price = get_current_price()
                if price and df_15m is not None and ind_15m:
                    df_tmp = get_price_data("15min", 20)
                    if df_tmp is not None and len(df_tmp) >= 2:
                        chg = float(df_tmp.iloc[-1]["close"]) - float(df_tmp.iloc[-2]["close"])
                        trend = "BULLISH" if ind_15m.get("above_ema50") else "BEARISH"
                        send_market_update(
                            price, chg, trend,
                            ind_15m.get("rsi", 50),
                            ind_15m.get("adx", 0)
                        )

            time.sleep(30)  # Verifica a cada 30 segundos

        except KeyboardInterrupt:
            log.info("🛑 Bot parado pelo utilizador")
            break
        except Exception as e:
            log.error(f"❌ Erro inesperado: {e}")
            send_error_alert(str(e))
            time.sleep(120)

if __name__ == "__main__":
    run()
