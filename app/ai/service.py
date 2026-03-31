from __future__ import annotations
from typing import Any, Iterator

import streamlit as st

from .agente_cfo import _create_cfo_agent


def _run_output_to_text(out: Any) -> str:
    """Extrai texto de RunOutput (Agno 2.x) ou converte fallback."""
    if out is None:
        return ""
    content = getattr(out, "content", None)
    if content is not None:
        return content if isinstance(content, str) else str(content)
    return str(out)


@st.cache_resource(show_spinner=False)
def _get_cached_cfo_agent() -> Any:
    """Uma instância do agente Agno por sessão de app (evita recriar a cada mensagem)."""
    return _create_cfo_agent()


def _default_context(filtros: Any) -> str:
    """Contexto padrão (não restritivo) para orientar respostas quando a pergunta não especificar escopo.
    Apenas para dar um default amigável; o agente pode ignorar se o usuário pedir outro recorte.
    """
    emp = getattr(filtros, "empresas", []) or []
    anos = getattr(filtros, "anos", []) or []
    mes_ini = getattr(filtros, "mes_ini", 1)
    mes_fim = getattr(filtros, "mes_fim", 12)
    return (
        f"Contexto default do app (pode ser ignorado se o usuário pedir outro recorte):\n"
        f"Empresas: {', '.join(emp) if emp else 'todas'} | "
        f"Anos: {', '.join(map(str, anos)) if anos else 'todos'} | "
        f"Meses: {mes_ini}–{mes_fim}."
    )


def ask_cfo(pergunta: str, filtros: Any) -> Iterator[str]:
    """Interface única para o chat: apenas o agente Agno (em cache). Retorna chunks para streaming."""
    agent = _get_cached_cfo_agent()

    if agent is None:
        yield (
            "⚠️ IA indisponível: o agente Agno não pôde ser criado. "
            "Confira `agno` e `openai` instalados, `OPENAI_API_KEY` no `.env` e se o modelo em MODEL_NAME "
            "é suportado pela API Responses da OpenAI."
        )
        return

    try:
        prompt = f"{_default_context(filtros)}\n\n{pergunta}"
        run_out = agent.run(prompt, stream=False)  # type: ignore[attr-defined]
        yield _run_output_to_text(run_out)
    except Exception as e:  # noqa: BLE001
        yield f"⚠️ Erro ao executar o agente: {e}"
