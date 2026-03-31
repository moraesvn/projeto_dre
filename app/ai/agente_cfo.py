from __future__ import annotations
from pathlib import Path
from typing import Any

from . import config

try:  # pragma: no cover
    from agno.agent import Agent
    from agno.models.openai import OpenAIResponses
except ImportError:  # agno ou openai ausentes
    Agent = None  # type: ignore[misc, assignment]
    OpenAIResponses = None  # type: ignore[misc, assignment]

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "agente_cfo.md"

# Último erro ao criar o agente (para mensagem no chat; esvaziado a cada tentativa)
_last_agent_error: str | None = None


def load_system_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt não encontrado: {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8").strip()


def _create_cfo_agent() -> Any:
    """Instancia o agente Agno 2.x (OpenAI via Responses API). Retorna None se indisponível ou falhar."""
    global _last_agent_error
    _last_agent_error = None

    system_prompt = load_system_prompt()

    if Agent is None or OpenAIResponses is None:
        _last_agent_error = "Pacotes `agno` ou `openai` não importaram (instale com pip)."
        return None

    try:
        model = OpenAIResponses(
            id=config.get_model_name(),
            temperature=config.get_temperature(),
            api_key=config.get_api_key(),
        )
        return Agent(
            model=model,
            instructions=system_prompt,
            markdown=True,
        )
    except Exception as e:  # pragma: no cover
        _last_agent_error = f"{type(e).__name__}: {e}"
        return None


def make_cfo_agent() -> Any:
    """Nova instância a cada chamada. No app Streamlit use o cache em `service`."""
    return _create_cfo_agent()
