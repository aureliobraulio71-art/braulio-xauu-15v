#!/usr/bin/env python3
# ============================================================
#  XAU/USD SUPER AI — PONTO DE ENTRADA
#  Execute: python main.py
# ============================================================

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.bot_engine import run

if __name__ == "__main__":
    run()
