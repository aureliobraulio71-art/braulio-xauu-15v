# ============================================================
#  XAU/USD SUPER AI — CONFIGURAÇÕES
# ============================================================

import os

# ── TELEGRAM ──────────────────────────────────────────────
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "8420334127:AAG2vNI0UlqJRdIe7678CPN-oV7f5lfP_mA")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003808354844")

# ── APIs ──────────────────────────────────────────────────
TWELVEDATA_KEY   = os.getenv("TWELVEDATA_KEY", "d65b5b0667034e8f9753823ec90e1c7e")
NEWSAPI_KEY      = os.getenv("NEWSAPI_KEY", "87ecaa3416314888b5bdbf3c68e3627e")
GROQ_KEY         = os.getenv("GROQ_KEY", "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")

# ── MERCADO ───────────────────────────────────────────────
SYMBOL           = "XAU/USD"
TIMEFRAMES       = ["1min", "5min", "15min", "1h", "4h"]
PRIMARY_TF       = "15min"

# ── ANÁLISE ───────────────────────────────────────────────
MIN_CONFIDENCE   = 70          # Confiança mínima para enviar sinal (%)
MAX_SIGNALS_DAY  = 6           # Máximo de sinais por dia
COOLDOWN_MINUTES = 30          # Espera entre sinais

# ── GESTÃO DE RISCO ───────────────────────────────────────
SL_PIPS          = 150         # Stop Loss em pips
TP1_PIPS         = 200         # Take Profit 1
TP2_PIPS         = 400         # Take Profit 2
TP3_PIPS         = 700         # Take Profit 3

# ── CICLOS ────────────────────────────────────────────────
ANALYSIS_INTERVAL = 300        # Análise a cada 5 minutos
NEWS_INTERVAL     = 600        # Notícias a cada 10 minutos
DAILY_REPORT_HOUR = 22         # Hora do relatório diário (UTC)
