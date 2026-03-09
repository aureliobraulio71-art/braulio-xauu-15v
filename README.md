# 🚀 XAU/USD SUPER AI — GROQ EDITION

Sistema de análise e sinais de trading para XAU/USD com **Groq AI (Llama 3.3 70B)** — 100% gratuito.

## 📁 Estrutura
```
xauusd-super-ai/
├── main.py                    ← Ponto de entrada
├── requirements.txt           ← Dependências
├── render.yaml                ← Deploy no Render
├── .env                       ← As tuas chaves (não partilhes!)
├── config/settings.py         ← Configurações
├── core/bot_engine.py         ← Motor principal 24/7
├── data/market_data.py        ← Dados TwelveData
├── analysis/
│   ├── indicators.py          ← 12 indicadores técnicos
│   ├── news_analyzer.py       ← Monitor de notícias
│   └── claude_brain.py        ← Cérebro Groq AI
├── notifications/
│   └── telegram_bot.py        ← Sinais Telegram
└── logs/                      ← Logs automáticos
```

## ⚡ Instalação Local (VS Code)

```bash
# 1. Instala dependências
pip install -r requirements.txt

# 2. Corre o bot
python main.py
```

## 🌐 Deploy no Render (24/7 gratuito)

1. Cria conta em **render.com**
2. New → Background Worker
3. Liga ao teu repositório GitHub
4. Em **Environment Variables** adiciona todas as chaves do .env
5. **Start Command:** `python main.py`
6. Clica **Deploy**

## 🧠 Como Funciona

| Componente | Função |
|---|---|
| TwelveData API | Preços XAU/USD em tempo real |
| NewsAPI | Notícias económicas relevantes |
| Groq AI (Llama 3.3 70B) | Análise inteligente e decisão |
| Telegram | Envio de sinais formatados |

## 📊 Indicadores (12 total)
RSI · MACD · EMA 20/50/200 · Bollinger Bands · ATR · Stochastic · ADX · CCI · Williams %R · VWAP · Suporte/Resistência · Padrões de Velas

## ⚙️ Configurações Principais
- `MIN_CONFIDENCE = 70` — Confiança mínima para sinal
- `MAX_SIGNALS_DAY = 6` — Máximo sinais por dia  
- `COOLDOWN_MINUTES = 30` — Espera entre sinais
- `ANALYSIS_INTERVAL = 300` — Análise a cada 5 minutos
