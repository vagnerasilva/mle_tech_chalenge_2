"""
Utilitários para limpeza e normalização de dados.
"""

import re
import logging

logger = logging.getLogger(__name__)

def clean_number(value: str) -> int:
    """Limpa e converte valores numéricos com pontos de milhar."""
    if not value:
        return 0
    # Remove pontos de milhar e espaços
    cleaned = re.sub(r'[.\s]', '', value.strip())
    try:
        return int(cleaned)
    except ValueError:
        logger.warning(f"Não foi possível converter número: '{value}'")
        return 0

def clean_percentage(value: str) -> float:
    """Limpa e converte valores percentuais."""
    if not value:
        return 0.0
    # Substitui vírgula por ponto e remove espaços
    cleaned = value.strip().replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        logger.warning(f"Não foi possível converter percentual: '{value}'")
        return 0.0

def clean_text(value: str) -> str:
    """Normaliza espaços em texto."""
    if not value:
        return ""
    # Remove espaços extras e normaliza
    return ' '.join(value.strip().split())
