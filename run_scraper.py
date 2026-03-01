#!/usr/bin/env python3
"""
Script principal para executar o scraper do IBOV.
"""

import sys
import os

# Adiciona o diretório raiz ao path para permitir imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.scraper_ibov_day import main

if __name__ == "__main__":
    main()
