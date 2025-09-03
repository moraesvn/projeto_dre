# app/ai/config.py
from __future__ import annotations
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env para o ambiente
load_dotenv()

# Configurações padrão do agente CFO
MODEL_NAME = "gpt-5-mini"   # modelo padrão
TEMPERATURE = 0.4           # respostas objetivas


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
