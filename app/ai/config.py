# app/ai/config.py
from __future__ import annotations
import os
from pathlib import Path

from dotenv import load_dotenv

# Raiz do repositório (…/projeto_dre) — Streamlit costuma rodar com cwd em app/, então .env na raiz não seria lido só com load_dotenv()
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")
load_dotenv()  # fallback: .env no cwd atual

# Configurações padrão do agente CFO
MODEL_NAME = "gpt-5-mini"   # modelo padrão
TEMPERATURE = 1           # respostas objetivas


def get_api_key() -> str:
    """Retorna a chave da API do OpenAI (vem do .env ou do ambiente)."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY não encontrada no ambiente. Defina no .env ou variável de ambiente.")
    return key


def get_model_name() -> str:
    """Modelo LLM a ser usado pelo agente CFO."""
    return os.getenv("MODEL_NAME", MODEL_NAME)


def get_temperature() -> float:
    """Temperatura para geração de texto (0.0 = determinístico, 1.0 = criativo)."""
    try:
        return float(os.getenv("MODEL_TEMPERATURE", TEMPERATURE))
    except ValueError:
        return TEMPERATURE
