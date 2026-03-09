# ============================================================
#  XAU/USD SUPER AI — ANALISADOR DE NOTÍCIAS
# ============================================================

import requests
from datetime import datetime, timedelta
from config.settings import NEWSAPI_KEY

GOLD_KEYWORDS = [
    "gold", "XAU", "federal reserve", "fed", "inflation", "CPI",
    "interest rate", "dollar", "USD", "geopolitical", "war",
    "safe haven", "central bank", "treasury", "yield", "recession",
    "ouro", "reserva federal", "inflação", "taxa de juro"
]

def get_latest_news(hours_back=4, max_articles=10):
    """Busca notícias recentes relevantes para XAU/USD"""
    from_time = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "gold XAU/USD OR 'federal reserve' OR inflation OR 'interest rate'",
        "from": from_time,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": max_articles,
        "apiKey": NEWSAPI_KEY
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        articles = data.get("articles", [])

        news_list = []
        for a in articles:
            title = a.get("title", "")
            desc  = a.get("description", "") or ""
            src   = a.get("source", {}).get("name", "")
            pub   = a.get("publishedAt", "")

            # Filtra relevantes
            text = (title + " " + desc).lower()
            relevance = sum(1 for kw in GOLD_KEYWORDS if kw.lower() in text)
            if relevance >= 1:
                news_list.append({
                    "title":   title,
                    "desc":    desc[:200],
                    "source":  src,
                    "time":    pub,
                    "score":   relevance
                })

        # Ordena por relevância
        news_list.sort(key=lambda x: x["score"], reverse=True)
        return news_list[:max_articles]

    except Exception as e:
        print(f"❌ Erro notícias: {e}")
        return []

def format_news_for_ai(news_list):
    """Formata notícias para análise da IA"""
    if not news_list:
        return "Sem notícias relevantes nas últimas horas."

    lines = []
    for i, n in enumerate(news_list[:6], 1):
        lines.append(f"{i}. [{n['source']}] {n['title']}")
        if n["desc"]:
            lines.append(f"   {n['desc'][:150]}")

    return "\n".join(lines)

def get_economic_calendar():
    """Retorna eventos económicos importantes do dia"""
    # Lista de eventos de alto impacto para XAU/USD
    high_impact = [
        "Non-Farm Payrolls", "CPI", "PPI", "FOMC", "Fed Rate Decision",
        "GDP", "Unemployment", "PCE", "ISM", "Retail Sales",
        "Core CPI", "Jackson Hole", "Fed Chair Speech"
    ]
    return high_impact
