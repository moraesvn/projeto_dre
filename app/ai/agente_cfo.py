from __future__ import annotations
from pathlib import Path
from typing import Any

from . import config

# Tenta usar Agno se disponível; caso contrário, retornamos None (o service faz fallback)
try:  # pragma: no cover
    # OBS: API do Agno pode variar por versão. Ajustaremos quando instalar.
    from agno import Agent  # type: ignore
except Exception:  # ImportError ou versões antigas
    Agent = None  # type: ignore

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "agente_cfo.md"


def load_system_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt não encontrado: {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8").strip()


def _create_cfo_agent() -> Any:
    """Instancia o agente Agno (sem cache). Retorna None se Agno indisponível ou falhar."""
    system_prompt = load_system_prompt()

    if Agent is None:
        return None

    try:
        return Agent(
            instructions=system_prompt,
            model=config.get_model_name(),
            temperature=config.get_temperature(),
        )
    except Exception:  # pragma: no cover
        return None


def make_cfo_agent() -> Any:
    """Cria o agente CFO (nova instância a cada chamada). Para o app Streamlit, prefira o cache em `service`."""
    return _create_cfo_agent()
