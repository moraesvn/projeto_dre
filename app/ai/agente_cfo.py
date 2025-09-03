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


def make_cfo_agent() -> Any:
    """Cria o agente CFO.
    - Se Agno estiver instalado, retorna uma instância do agente Agno.
    - Se não estiver, retorna None; o service fará fallback para chamada direta ao LLM.
    """
    system_prompt = load_system_prompt()

    if Agent is None:
        return None

    # ⚠️ Place-holder: a assinatura real do Agent pode mudar conforme a versão do Agno.
    # Vamos manter os parâmetros essenciais aqui e ajustar quando instalar.
    try:
        agent = Agent(
            instructions=system_prompt,
            model=config.get_model_name(),
            temperature=config.get_temperature(),
            # tools=[]  # adicionaremos na próxima etapa (SQL read-only, KPIs canônicos)
        )
        return agent
    except Exception as e:  # pragma: no cover
        # Se a criação falhar (ex.: diferença de API), o service vai usar fallback direto no LLM
        return None
